"""Seeded, reproducible Briefs, Envelopes and Proposals for the toy.

Vocabulary follows CONTEXT.md:

* **Envelope** — the outer boundary a Plan is laid out inside. Always
  non-rectangular here.
* **Brief** — rooms, types, minimum dimensions, required *and forbidden*
  adjacencies, entry. The constraint side. Feasibility depends only on this.
* **Proposal** — what a learned model emits: axis-aligned boxes with room
  types. Never a constraint; only the objective.

Why the Brief is generated from a ground truth
----------------------------------------------
Every Brief here is derived from a **known-feasible tiling**, and room types
are assigned by a small CP-SAT model that is itself required to satisfy the
type-dependent rules (exterior access, wet clustering, circulation). The truth
is then re-checked by `validate.check`. That guarantees a failure to solve is a
fact about the *projection* problem, not about an accidentally impossible
Brief — otherwise the whole timing table would be uninterpretable.

The Proposal is that ground truth corrupted with seeded per-corner Gaussian
noise, which reproduces the two pathologies a learned generator actually
produces: **overlap** and **unassigned floor**.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from ortools.sat.python import cp_model

from geometry import (
    Envelope,
    Rect,
    adjacency_matrix,
    l_shape,
    touches_exterior,
    u_shape,
)

# ---------------------------------------------------------------------------
# Grid
# ---------------------------------------------------------------------------
GRID_MM = 250                 # one grid unit = 250 mm
CELLS_PER_M2 = 16             # (1000/250)^2


def m2(x: float) -> int:
    return round(x * CELLS_PER_M2)


def mm(x: float) -> int:
    """metres -> grid units"""
    return round(x * 1000 / GRID_MM)


# ---------------------------------------------------------------------------
# Room-type standards. Placeholders pending ticket 05 (dimensional standards
# corpus) — the point here is the *shape* of the constraint, not the number.
# ---------------------------------------------------------------------------

WET = {"bathroom", "wc", "kitchen", "utility"}
PRIVATE = {"bedroom", "bathroom", "wc"}
HABITABLE = {"bedroom", "living", "kitchen", "dining", "study"}
CIRCULATION = {"hall", "corridor"}

STANDARDS: Dict[str, Tuple[int, int, int]] = {
    # kind:      (min_w,   min_h,   min_area)
    "living":    (mm(2.75), mm(2.75), m2(12.0)),
    "bedroom":   (mm(2.00), mm(2.00), m2(7.0)),
    "kitchen":   (mm(1.75), mm(1.75), m2(5.0)),
    "dining":    (mm(2.25), mm(2.25), m2(7.0)),
    "study":     (mm(1.75), mm(1.75), m2(5.0)),
    "bathroom":  (mm(1.50), mm(1.50), m2(3.5)),
    "wc":        (mm(1.00), mm(1.00), m2(1.5)),
    "utility":   (mm(1.25), mm(1.25), m2(2.5)),
    "hall":      (mm(1.25), mm(1.25), m2(3.0)),
    "corridor":  (mm(1.00), mm(1.00), m2(2.5)),
}

ALL_KINDS = tuple(STANDARDS)

# Composition rules: (min count, max count) over the whole dwelling.
COMPOSITION: Dict[str, Tuple[int, Optional[int]]] = {
    "hall": (1, 1),
    "living": (1, 1),
    "kitchen": (1, 1),
    "bathroom": (1, None),
    "bedroom": (2, None),
    "wc": (0, None),
    "dining": (0, None),
    "study": (0, None),
    "utility": (0, None),
    "corridor": (0, None),
}

# Order in which extra rooms are added beyond the mandatory six.
FILLER = ("bedroom", "bathroom", "study", "wc", "dining", "corridor",
          "bedroom", "utility", "study", "bedroom", "corridor", "bathroom",
          "bedroom", "study", "wc", "dining", "bedroom", "utility")


def composition(n: int) -> List[str]:
    """A plausible room mix of size `n` satisfying COMPOSITION."""
    base = ["hall", "living", "kitchen", "bathroom", "bedroom", "bedroom"]
    if n < len(base):
        raise ValueError(f"{n} rooms cannot satisfy the composition rules")
    out = list(base)
    i = 0
    while len(out) < n:
        out.append(FILLER[i % len(FILLER)])
        i += 1
    return out


@dataclass
class RoomSpec:
    name: str
    kind: str
    min_w: int
    min_h: int
    min_area: int


@dataclass
class Brief:
    name: str
    env: Envelope
    grid_mm: int
    rooms: List[RoomSpec]
    entry: int
    required_adj: List[Tuple[int, int]] = field(default_factory=list)
    forbidden_adj: List[Tuple[int, int]] = field(default_factory=list)
    door_min: int = mm(0.75)
    max_aspect: int = 4

    @property
    def n(self) -> int:
        return len(self.rooms)

    def indices(self, kinds: Sequence[str]) -> List[int]:
        return [i for i, r in enumerate(self.rooms) if r.kind in kinds]


@dataclass
class Proposal:
    boxes: List[Rect]
    kinds: List[str]
    label: str = "noisy"


# ---------------------------------------------------------------------------
# Ground-truth tiling: backtracking guillotine dissection of each Envelope part
# ---------------------------------------------------------------------------

MIN_SIDE = mm(1.0)
MIN_PIECE_AREA = m2(3.0)
MAX_ASPECT = 4


def _leaf_ok(r: Rect) -> bool:
    return (
        r.w >= MIN_SIDE
        and r.h >= MIN_SIDE
        and r.area >= MIN_PIECE_AREA
        and r.w <= MAX_ASPECT * r.h
        and r.h <= MAX_ASPECT * r.w
    )


def _capacity_ok(r: Rect, k: int) -> bool:
    if k == 1:
        return _leaf_ok(r)
    return r.w >= MIN_SIDE and r.h >= MIN_SIDE and r.area >= k * MIN_PIECE_AREA


def _guillotine(
    rect: Rect, targets: List[int], rng: random.Random, budget: List[int]
) -> Optional[List[Rect]]:
    """Dissect `rect` into len(targets) rectangles of roughly the target areas.

    Cuts are placed in proportion to the summed target areas on each side, so
    a 12 m2 living room and a 1.5 m2 WC can coexist in the same plan. Backtracks
    when a branch cannot produce legal leaves.
    """
    if budget[0] <= 0:
        return None
    budget[0] -= 1
    k = len(targets)
    if k == 1:
        return [rect] if _leaf_ok(rect) else None

    order = list(range(k))
    rng.shuffle(order)
    tsum = sum(targets)
    splits = []
    for left in (k // 2, k // 3 or 1, (2 * k) // 3 or 1, 1, k - 1):
        if 1 <= left <= k - 1 and left not in [s for s, _ in splits]:
            splits.append((left, order[:left]))

    for left, sel in splits:
        sel_set = set(sel)
        ta = [targets[i] for i in range(k) if i in sel_set]
        tb = [targets[i] for i in range(k) if i not in sel_set]
        frac = sum(ta) / tsum
        axes = ["h", "v"] if rect.h > rect.w else ["v", "h"]
        for axis in axes:
            base = rect.y1 if axis == "h" else rect.x1
            span = rect.h if axis == "h" else rect.w
            ideal = base + max(1, round(span * frac))
            for delta in sorted(range(-span, span + 1), key=abs)[:48]:
                cut = ideal + delta
                if not (base < cut < base + span):
                    continue
                if axis == "h":
                    a = Rect(rect.x1, rect.y1, rect.x2, cut)
                    b = Rect(rect.x1, cut, rect.x2, rect.y2)
                else:
                    a = Rect(rect.x1, rect.y1, cut, rect.y2)
                    b = Rect(cut, rect.y1, rect.x2, rect.y2)
                if not (_capacity_ok(a, len(ta)) and _capacity_ok(b, len(tb))):
                    continue
                ra = _guillotine(a, ta, rng, budget)
                if ra is None:
                    continue
                rb = _guillotine(b, tb, rng, budget)
                if rb is None:
                    continue
                return ra + rb
    return None


def area_targets(kinds: Sequence[str], total: int) -> List[int]:
    """Target areas per room: the type minimum with headroom, then the surplus
    shared out in proportion. Sums to `total`."""
    base = [max(MIN_PIECE_AREA, round(STANDARDS[k][2] * 1.15)) for k in kinds]
    s = sum(base)
    if s > total:
        raise ValueError(f"room minima {s} exceed the Envelope interior {total}")
    surplus = total - s
    out = [b + round(surplus * b / s) for b in base]
    out[0] += total - sum(out)
    return out


def ground_truth(env: Envelope, kinds: Sequence[str], rng: random.Random) -> List[Rect]:
    """A valid exact tiling of the (non-rectangular) Envelope."""
    targets = area_targets(kinds, env.interior_area)
    order = sorted(range(len(targets)), key=lambda i: -targets[i])

    parts = sorted(env.parts, key=lambda p: -p.area)
    groups: List[List[int]] = [[] for _ in parts]
    remaining = [p.area for p in parts]
    for i in order:                       # largest room into the emptiest part
        j = max(range(len(parts)), key=lambda j: remaining[j])
        groups[j].append(i)
        remaining[j] -= targets[i]
    if any(not g for g in groups):
        raise ValueError("a part of the Envelope received no rooms")

    out: List[Rect] = []
    for part, g in zip(parts, groups):
        scale = part.area / sum(targets[i] for i in g)
        tg = [max(MIN_PIECE_AREA, round(targets[i] * scale)) for i in g]
        piece = _guillotine(part, tg, rng, [400_000])
        if piece is None:
            raise ValueError(f"cannot dissect {part} into {len(g)} rooms")
        out.extend(piece)
    assert len(out) == len(kinds)
    return out


# ---------------------------------------------------------------------------
# Room-type assignment: a small CP-SAT model over FIXED geometry.
#
# This exists so the ground truth provably satisfies the type-dependent rules
# (exterior access for habitable rooms, one wet cluster, circulation that never
# passes through a bedroom). Geometry is constant here, so it is a pure
# assignment problem and solves in milliseconds.
# ---------------------------------------------------------------------------


def assign_kinds(
    truth: Sequence[Rect], env: Envelope, door_min: int, window_min: int, seed: int
) -> Optional[List[str]]:
    n = len(truth)
    adj = adjacency_matrix(truth, door_min)
    adj_any = adjacency_matrix(truth, 1)
    ext = [touches_exterior(r, env, window_min) for r in truth]

    m = cp_model.CpModel()
    k_of = {k: idx for idx, k in enumerate(ALL_KINDS)}
    z = [[m.NewBoolVar(f"z_{i}_{k}") for k in ALL_KINDS] for i in range(n)]
    for i in range(n):
        m.AddExactlyOne(z[i])
        for k in ALL_KINDS:
            mw, mh, ma = STANDARDS[k]
            if truth[i].w < mw or truth[i].h < mh or truth[i].area < ma:
                m.Add(z[i][k_of[k]] == 0)          # room too small for this type
            if k in HABITABLE and not ext[i]:
                m.Add(z[i][k_of[k]] == 0)          # habitable needs a window

    for k, (lo, hi) in COMPOSITION.items():
        col = [z[i][k_of[k]] for i in range(n)]
        m.Add(sum(col) >= lo)
        if hi is not None:
            m.Add(sum(col) <= hi)

    is_wet = [m.NewBoolVar(f"wet_{i}") for i in range(n)]
    is_priv = [m.NewBoolVar(f"priv_{i}") for i in range(n)]
    for i in range(n):
        m.Add(is_wet[i] == sum(z[i][k_of[k]] for k in WET))
        m.Add(is_priv[i] == sum(z[i][k_of[k]] for k in PRIVATE))

    entry = [m.NewBoolVar(f"entry_{i}") for i in range(n)]
    for i in range(n):
        m.Add(entry[i] == z[i][k_of["hall"]])
    m.AddExactlyOne(entry)

    # -- circulation flow: entry serves everyone, private rooms never forward
    cap = n
    fout = {i: [] for i in range(n)}
    fin = {i: [] for i in range(n)}
    for i in range(n):
        for j in range(n):
            if i != j and adj[i][j]:
                f = m.NewIntVar(0, cap, f"cf_{i}_{j}")
                fout[i].append(f)
                fin[j].append(f)
    for i in range(n):
        bal = m.NewIntVar(-cap, cap, f"bal_{i}")
        m.Add(bal == sum(fin[i]) - sum(fout[i]))
        m.Add(bal == 1).OnlyEnforceIf(entry[i].Not())
        m.Add(bal == -(n - 1)).OnlyEnforceIf(entry[i])
        m.Add(sum(fout[i]) == 0).OnlyEnforceIf([is_priv[i], entry[i].Not()])

    # -- wet cluster flow over the selected wet nodes
    nwet = m.NewIntVar(0, n, "nwet")
    m.Add(nwet == sum(is_wet))
    wroot = [m.NewBoolVar(f"wroot_{i}") for i in range(n)]
    m.AddExactlyOne(wroot)
    wout = {i: [] for i in range(n)}
    win = {i: [] for i in range(n)}
    for i in range(n):
        m.AddImplication(wroot[i], is_wet[i])
        for j in range(n):
            if i != j and adj_any[i][j]:
                f = m.NewIntVar(0, cap, f"wf_{i}_{j}")
                m.Add(f == 0).OnlyEnforceIf(is_wet[i].Not())
                m.Add(f == 0).OnlyEnforceIf(is_wet[j].Not())
                wout[i].append(f)
                win[j].append(f)
    for i in range(n):
        wb = m.NewIntVar(-cap, cap, f"wb_{i}")
        m.Add(wb == sum(win[i]) - sum(wout[i]))
        m.Add(wb == 1).OnlyEnforceIf([is_wet[i], wroot[i].Not()])
        m.Add(wb == 0).OnlyEnforceIf(is_wet[i].Not())
        m.Add(wb + nwet == 1).OnlyEnforceIf(wroot[i])

    # Prefer bigger rooms for the big kinds; makes the plan read like a home.
    m.Maximize(sum(truth[i].area * z[i][k_of["living"]] for i in range(n)))

    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = 30.0
    s.parameters.num_workers = 8
    s.parameters.random_seed = seed
    st = s.Solve(m)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None
    return [next(k for k in ALL_KINDS if s.Value(z[i][k_of[k]])) for i in range(n)]


# ---------------------------------------------------------------------------
# Brief construction
# ---------------------------------------------------------------------------


def make_brief(
    name: str,
    env: Envelope,
    n_rooms: int,
    seed: int,
    door_min: int,
    window_min: int,
    required_frac: float = 0.30,
    forbidden_frac: float = 0.10,
) -> Tuple[Brief, List[Rect], List[str]]:
    mix = composition(n_rooms)
    last = None
    for attempt in range(40):
        rng = random.Random(seed + attempt)
        try:
            truth = ground_truth(env, mix, rng)
        except ValueError as e:
            last = e
            continue
        kinds = assign_kinds(truth, env, door_min, window_min, seed + attempt)
        if kinds is None:
            last = "no valid room-type assignment"
            continue

        rooms = [
            RoomSpec(f"{k}{i}", k, *STANDARDS[k]) for i, k in enumerate(kinds)
        ]
        adj_door = adjacency_matrix(truth, door_min)
        adj_any = adjacency_matrix(truth, 1)
        entry = kinds.index("hall")

        true_pairs = [(i, j) for i in range(n_rooms) for j in range(i + 1, n_rooms)
                      if adj_door[i][j]]
        non_pairs = [(i, j) for i in range(n_rooms) for j in range(i + 1, n_rooms)
                     if not adj_any[i][j]]
        rng.shuffle(true_pairs)
        rng.shuffle(non_pairs)
        required = sorted(true_pairs[: max(1, round(len(true_pairs) * required_frac))])
        forbidden = sorted(non_pairs[: max(1, round(len(non_pairs) * forbidden_frac))])

        return (
            Brief(
                name=name, env=env, grid_mm=GRID_MM, rooms=rooms, entry=entry,
                required_adj=required, forbidden_adj=forbidden, door_min=door_min,
                max_aspect=MAX_ASPECT,
            ),
            truth,
            kinds,
        )
    raise RuntimeError(f"{name}: no feasible Brief after 40 attempts ({last})")


# ---------------------------------------------------------------------------
# Proposal
# ---------------------------------------------------------------------------


def make_proposal(
    truth: Sequence[Rect], kinds: Sequence[str], seed: int, sigma: float, label: str = "noisy"
) -> Proposal:
    """Independent Gaussian jitter on each of the four corners of each box.

    Per-corner (not per-box) noise is the point: it is what produces overlap
    *and* unassigned floor simultaneously, which is what a learned generator
    actually emits and what the solver has to repair.
    """
    rng = random.Random(seed * 7919 + 13)
    boxes = []
    for r in truth:
        x1 = r.x1 + round(rng.gauss(0, sigma))
        x2 = r.x2 + round(rng.gauss(0, sigma))
        y1 = r.y1 + round(rng.gauss(0, sigma))
        y2 = r.y2 + round(rng.gauss(0, sigma))
        if x2 <= x1:
            x1, x2 = min(x1, x2), min(x1, x2) + 1
        if y2 <= y1:
            y1, y2 = min(y1, y2), min(y1, y2) + 1
        boxes.append(Rect(x1, y1, x2, y2))
    return Proposal(boxes=boxes, kinds=list(kinds), label=label)


def degenerate_proposal(truth: Sequence[Rect], kinds: Sequence[str]) -> Proposal:
    """A worthless Proposal: every room a unit box in one corner.

    Proves the structural claim that the Proposal cannot make the model
    infeasible, because it appears only in the objective.
    """
    return Proposal([Rect(0, 0, 1, 1) for _ in truth], list(kinds), "degenerate")


def shuffled_proposal(truth: Sequence[Rect], kinds: Sequence[str], seed: int) -> Proposal:
    """A Proposal whose rooms are correct boxes assigned to the wrong rooms.

    Topologically hostile rather than merely noisy: it asks for a layout whose
    adjacency graph contradicts the Brief.
    """
    rng = random.Random(seed)
    order = list(range(len(truth)))
    rng.shuffle(order)
    return Proposal([truth[order[i]] for i in range(len(truth))], list(kinds), "shuffled")


# ---------------------------------------------------------------------------
# The three scenarios the ticket asks for
# ---------------------------------------------------------------------------

DOOR_MIN = mm(0.75)     # a shared wall shorter than this is not a door
WINDOW_MIN = mm(1.00)   # exterior wall run a habitable room needs


def envelope_for(n_rooms: int) -> Envelope:
    if n_rooms == 8:
        notches, parts = l_shape(mm(10.0), mm(8.0), mm(2.5), mm(2.0))
        return Envelope("L 10.0x8.0 m less 2.5x2.0 m", mm(10.0), mm(8.0), notches, parts)
    if n_rooms == 12:
        notches, parts = u_shape(mm(13.0), mm(10.0), mm(3.0), mm(1.5), mm(5.0))
        return Envelope("U 13.0x10.0 m, two notches", mm(13.0), mm(10.0), notches, parts)
    if n_rooms == 24:
        notches, parts = u_shape(mm(18.0), mm(14.0), mm(4.0), mm(1.75), mm(7.0))
        return Envelope("U 18.0x14.0 m, two notches", mm(18.0), mm(14.0), notches, parts)
    raise ValueError(f"no Envelope defined for {n_rooms} rooms")


DEFAULT_SEED = 20260817


def scenario(n_rooms: int, seed: int = DEFAULT_SEED) -> Tuple[Brief, List[Rect], Proposal]:
    env = envelope_for(n_rooms)
    brief, truth, kinds = make_brief(
        f"{n_rooms}-room", env, n_rooms, seed, DOOR_MIN, WINDOW_MIN
    )
    proposal = make_proposal(truth, kinds, seed, sigma=mm(0.5))
    return brief, truth, proposal


ROOM_COUNTS = (8, 12, 24)
