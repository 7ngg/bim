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


# Ticket 15 axis 3 sweeps room counts across the whole range, and C13 fixes the
# v1 band at 4-10. The mandatory six below 6 rooms is not a fact about homes: a
# studio is 4 rooms and a one-bed 5, and both are ordinary in Swiss Dwellings.
# The *bounds* fall with the mix (see `comp_bounds`) so the constraint system
# stays the same shape rather than becoming infeasible by table lookup.
SMALL_BASE = {
    4: ["hall", "living", "kitchen", "bathroom"],                # studio
    5: ["hall", "living", "kitchen", "bathroom", "bedroom"],     # one-bed
}


def comp_bounds(mix: Sequence[str]) -> Dict[str, Tuple[int, Optional[int]]]:
    """COMPOSITION with every minimum clamped to what `mix` actually contains."""
    out = {}
    for k, (lo, hi) in COMPOSITION.items():
        out[k] = (min(lo, mix.count(k)), hi)
    return out


def composition(n: int) -> List[str]:
    """A plausible room mix of size `n` satisfying COMPOSITION."""
    base = ["hall", "living", "kitchen", "bathroom", "bedroom", "bedroom"]
    if n in SMALL_BASE:
        return list(SMALL_BASE[n])
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


# Tunable so a sweep over hundreds of scenarios cannot spend 40 x 30 s failing
# to type a single hostile one. Defaults reproduce the published behaviour.
ASSIGN_TIME_LIMIT_S = 30.0
ASSIGN_WORKERS = 8
BRIEF_ATTEMPTS = 40


def fits_kind(r: Rect, kind: str, clear_t: int = 0) -> bool:
    """Does a *solved* rect satisfy a kind's published minima?

    `clear_t` is the internal wall thickness in millimetres. At 0 the minima
    bind on the solved rect, which is the reading every published run used. At
    100 they bind on the clear rect — `erode(solved, t/2)` — which is what
    ADR 0001 means by a published minimum, and which costs one whole grid unit
    on every dimension because 250w - 100 >= 250*min_w forces w >= min_w + 1.

    Ticket 15: without this the ground truth stops being a witness under the
    clear reading, and the harness's central guarantee — that a failure to solve
    is a fact about the projection problem, not about an impossible Brief —
    silently stops holding.
    """
    mw, mh, ma = STANDARDS[kind]
    if clear_t <= 0:
        return r.w >= mw and r.h >= mh and r.area >= ma
    cw = r.w * GRID_MM - clear_t
    ch = r.h * GRID_MM - clear_t
    return (cw >= mw * GRID_MM and ch >= mh * GRID_MM
            and cw * ch >= ma * GRID_MM * GRID_MM)


def assign_kinds(
    truth: Sequence[Rect], env: Envelope, door_min: int, window_min: int, seed: int,
    comp: Optional[Dict[str, Tuple[int, Optional[int]]]] = None,
    clear_t: int = 0,
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
            if not fits_kind(truth[i], k, clear_t):
                m.Add(z[i][k_of[k]] == 0)          # room too small for this type
            if k in HABITABLE and not ext[i]:
                m.Add(z[i][k_of[k]] == 0)          # habitable needs a window

    for k, (lo, hi) in (comp or COMPOSITION).items():
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
    s.parameters.max_time_in_seconds = ASSIGN_TIME_LIMIT_S
    s.parameters.num_workers = ASSIGN_WORKERS
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
    clear_t: int = 0,
) -> Tuple[Brief, List[Rect], List[str]]:
    mix = composition(n_rooms)
    last = None
    for attempt in range(BRIEF_ATTEMPTS):
        rng = random.Random(seed + attempt)
        try:
            truth = ground_truth(env, mix, rng)
        except ValueError as e:
            last = e
            continue
        kinds = assign_kinds(truth, env, door_min, window_min, seed + attempt,
                             comp_bounds(mix), clear_t)
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
    raise RuntimeError(
        f"{name}: no feasible Brief after {BRIEF_ATTEMPTS} attempts ({last})")


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


# The three published Envelopes, kept bit-exact so every number this sweep
# produces at 8 / 12 / 24 is comparable with the ones already in
# docs/research/solver-formulation.md.
PUBLISHED_ENVELOPES = {
    8:  ("L 10.0x8.0 m less 2.5x2.0 m", 10.0, 8.0, ("L", 2.5, 2.0, None)),
    12: ("U 13.0x10.0 m, two notches",  13.0, 10.0, ("U", 3.0, 1.5, 5.0)),
    24: ("U 18.0x14.0 m, two notches",  18.0, 14.0, ("U", 4.0, 1.75, 7.0)),
}

# Fitted from the three published Envelopes: 75.0 / 118.0 / 232.8 m2 of interior
# over 8 / 12 / 24 rooms is 9.38 / 9.83 / 9.70 m2 per room, and all three bboxes
# sit at an aspect of 1.25-1.30.
AREA_PER_ROOM_M2 = 9.65
BBOX_ASPECT = 1.28

# Set False to make 8 / 12 / 24 scale with AREA_PER_ROOM_M2 like every other
# count, which is what a sweep over Envelope size needs.
USE_PUBLISHED_ENVELOPES = True


def envelope_for(n_rooms: int, exposure: str = "detached") -> Envelope:
    """An Envelope sized for `n_rooms`, under a dwelling-type exposure preset.

    8, 12 and 24 return the published Envelopes unchanged. Every other count is
    generated by the same recipe: interior area scaled at a fixed area per room,
    a bbox at the published aspect, and one notch below 10 rooms or two above,
    cut to the published notch share of the bbox.
    """
    if USE_PUBLISHED_ENVELOPES and n_rooms in PUBLISHED_ENVELOPES:
        name, Wm, Hm, spec = PUBLISHED_ENVELOPES[n_rooms]
        kind, nw, nh, gap = spec
        if kind == "L":
            notches, parts = l_shape(mm(Wm), mm(Hm), mm(nw), mm(nh))
        else:
            notches, parts = u_shape(mm(Wm), mm(Hm), mm(nw), mm(nh), mm(gap))
        return Envelope(name, mm(Wm), mm(Hm), notches, parts, exposure)

    if n_rooms < 4:
        raise ValueError(f"no Envelope defined for {n_rooms} rooms")

    notch_share = 0.0625 if n_rooms < 10 else 0.085
    bbox_m2 = n_rooms * AREA_PER_ROOM_M2 / (1.0 - notch_share)
    Wm = round((bbox_m2 * BBOX_ASPECT) ** 0.5 * 4) / 4      # snap to 250 mm
    Hm = round(bbox_m2 / Wm * 4) / 4
    W, H = mm(Wm), mm(Hm)

    if n_rooms < 10:
        # One notch, in the published 2.5x2.0-of-10.0x8.0 proportion.
        nw = round(W * 0.25 / 2) * 2 or 2
        nh = round(H * 0.25 / 2) * 2 or 2
        notches, parts = l_shape(W, H, nw, nh)
        name = f"L {Wm}x{Hm} m less {nw*GRID_MM/1000}x{nh*GRID_MM/1000} m"
    else:
        nh = max(2, round(H * 0.145))
        nw = max(2, round(W * 0.23))
        gap = max(2, round(W * 0.39))
        if nw + gap >= W:
            gap = max(2, W - nw - 2)
        notches, parts = u_shape(W, H, nw, nh, gap)
        name = f"U {Wm}x{Hm} m, two notches"
    return Envelope(name, W, H, notches, parts, exposure)


DEFAULT_SEED = 20260817


def scenario(
    n_rooms: int,
    seed: int = DEFAULT_SEED,
    exposure: str = "detached",
    door_min: int = DOOR_MIN,
    sigma_m: float = 0.5,
    clear_t: int = 0,
) -> Tuple[Brief, List[Rect], Proposal]:
    env = envelope_for(n_rooms, exposure)
    brief, truth, kinds = make_brief(
        f"{n_rooms}-room", env, n_rooms, seed, door_min, WINDOW_MIN,
        clear_t=clear_t
    )
    proposal = make_proposal(truth, kinds, seed, sigma=mm(sigma_m))
    return brief, truth, proposal


ROOM_COUNTS = (8, 12, 24)
