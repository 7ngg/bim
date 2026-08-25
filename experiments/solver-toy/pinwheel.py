"""Non-guillotine ground truth — the layout class this harness has never solved.

`scenarios.ground_truth` dissects every Envelope part with `_guillotine`, a
backtracking recursive dissection. Every one of the 965 solves behind
`docs/research/solver-formulation.md` Part II therefore had a **guillotine**
target: a tiling some sequence of full-width cuts can take apart.

The solver does not care — `AddNoOverlap2D` admits any rectangular tiling — but
nothing has ever checked, because nothing has ever handed it a target that is
not guillotine. A **pinwheel** (four rooms circling a central one, the canonical
real apartment plan) is the smallest such tiling and is unreachable by any cut
sequence.

This module builds those targets.

    R4 R4 | R3 R3 R3         Five cells, cuts a < b in x and c < d in y:
    R4 R4 | R3 R3 R3           R1 = (x1, y1,  b,  c)     R2 = ( b, y1, x2,  d)
    ------+---------           R3 = ( a,  d, x2, y2)     R4 = (x1,  c,  a, y2)
    R4 R4 | C  | R2            C  = ( a,  c,  b,  d)
    ------+----+----
    R1 R1 R1 | R2 R2         No full cut exists: x = a is spanned by R1, x = b
    R1 R1 R1 | R2 R2         by R3, y = c by R2 and y = d by R4.

Every tiling of a rectangle into four or fewer rectangles is guillotine, so five
is the floor and `n < 5` falls back to the guillotine generator. Each assembled
tiling is checked with `is_guillotine` and rejected if it comes out guillotine
anyway — a pinwheel cell subdivided further can accidentally open a cut line.

The guillotine predicate is `experiments/rectangularise/guillotine_share.py`'s,
copied rather than imported so this directory keeps its "no other dependencies"
promise. It admits cuts through an Envelope notch, because a notch is not a room
— which makes it *conservative here*: it can only call a tiling guillotine that
a stricter reading would not.
"""

from __future__ import annotations

import random
from typing import Dict, List, Optional, Sequence, Tuple

import scenarios
from geometry import Envelope, Rect
from scenarios import (
    MAX_ASPECT,
    MIN_PIECE_AREA,
    MIN_SIDE,
    _capacity_ok,
    _guillotine,
    _leaf_ok,
    area_targets,
)

# ---------------------------------------------------------------------------
# Is a tiling guillotine?
# ---------------------------------------------------------------------------


def is_guillotine(rects: Sequence[Rect]) -> bool:
    """Does some sequence of full-width cuts take this tiling apart?

    Recursive: a cut that splits the set without crossing any rectangle, then
    the same question on each side. `len <= 1` is trivially guillotine.
    """
    return _is_guillotine([(r.x1, r.y1, r.x2, r.y2) for r in rects])


def guillotine_residue(rects: Sequence[Rect]) -> int:
    """The largest block that survives every cut — the **dose**.

    Peel guillotine cuts recursively; whatever cannot be cut further is
    entangled. 1 means the tiling came apart completely and is guillotine; 5 is
    a bare pinwheel; larger means more of the plan is knotted together. This is
    the covariate a "nothing moved" result has to be read against, because a
    treatment that is barely non-guillotine proves nothing about one that is.
    """
    return _residue([(r.x1, r.y1, r.x2, r.y2) for r in rects])


def _residue(rects: List[Tuple[int, int, int, int]]) -> int:
    if len(rects) <= 1:
        return 1
    for a, b in _cuts(rects):
        return max(_residue(a), _residue(b))
    return len(rects)


def _cuts(rects: List[Tuple[int, int, int, int]]):
    x0 = min(r[0] for r in rects)
    x1 = max(r[2] for r in rects)
    y0 = min(r[1] for r in rects)
    y1 = max(r[3] for r in rects)
    for c in sorted({r[0] for r in rects} | {r[2] for r in rects}):
        if not (x0 < c < x1) or any(r[0] < c < r[2] for r in rects):
            continue
        a = [r for r in rects if r[2] <= c]
        b = [r for r in rects if r[0] >= c]
        if a and b and len(a) + len(b) == len(rects):
            yield a, b
    for c in sorted({r[1] for r in rects} | {r[3] for r in rects}):
        if not (y0 < c < y1) or any(r[1] < c < r[3] for r in rects):
            continue
        a = [r for r in rects if r[3] <= c]
        b = [r for r in rects if r[1] >= c]
        if a and b and len(a) + len(b) == len(rects):
            yield a, b


def _is_guillotine(rects: List[Tuple[int, int, int, int]]) -> bool:
    if len(rects) <= 1:
        return True
    x0 = min(r[0] for r in rects)
    x1 = max(r[2] for r in rects)
    y0 = min(r[1] for r in rects)
    y1 = max(r[3] for r in rects)
    for c in sorted({r[0] for r in rects} | {r[2] for r in rects}):
        if not (x0 < c < x1):
            continue
        if any(r[0] < c < r[2] for r in rects):
            continue
        a = [r for r in rects if r[2] <= c]
        b = [r for r in rects if r[0] >= c]
        if a and b and len(a) + len(b) == len(rects):
            return _is_guillotine(a) and _is_guillotine(b)
    for c in sorted({r[1] for r in rects} | {r[3] for r in rects}):
        if not (y0 < c < y1):
            continue
        if any(r[1] < c < r[3] for r in rects):
            continue
        a = [r for r in rects if r[3] <= c]
        b = [r for r in rects if r[1] >= c]
        if a and b and len(a) + len(b) == len(rects):
            return _is_guillotine(a) and _is_guillotine(b)
    return False


# ---------------------------------------------------------------------------
# The pinwheel split
# ---------------------------------------------------------------------------

# Cut quadruples are sampled rather than enumerated: a 40 x 32 grid part has
# ~1.6 M (a, b, c, d) and only the area fit distinguishes them.
PINWHEEL_SAMPLES = 6000

# Sampling the four cuts uniformly produces slivers — a 1 m deep arm running the
# width of the plan — which are legal rectangles and useless rooms. Sampling the
# three *spans* on each axis as proportions instead bounds every piece away from
# zero by construction.
SPAN_LO, SPAN_HI = 0.10, 0.72

# A cell holding exactly one room has to be able to *be* that room. `_leaf_ok`'s
# 3 m2 and aspect 4 are the generator's floor, not a living room's: a 7.5 x 2.5 m
# strip passes both and fails `living`'s 2.75 m clear depth. Kept looser than
# that floor rather than tighter — an exhaustive enumeration of the 8-room part
# found 5 595 legal pinwheels carrying a living-capable cell, and a first cut of
# these bounds at 2.5 / 0.85 excluded every one of them.
LEAF_ASPECT = 3.0
LEAF_AREA_FRAC = 0.75


def pinwheel_cells(
    rect: Rect, targets: Sequence[int], rng: random.Random, sizes: Sequence[int]
) -> Optional[List[Tuple[Rect, int]]]:
    """Five pinwheel cells of `rect`, matched to `targets` by area.

    `sizes[i]` is how many rooms target i will eventually hold, so a cell about
    to be dissected further is held to `_capacity_ok` rather than `_leaf_ok`.

    Geometry is sampled, then **groups are matched to cells by sorted area**
    rather than assigned to fixed positions. The five pinwheel positions have
    very different shapes — a corner block, three interlocking arms and a small
    centre — and pinning the largest group to a fixed one starves it: the first
    version of this did that and produced Envelopes where no rectangle was big
    enough to be a living room at all.

    Returns [(cell, target_index)] or None if no sampled quadruple is legal.
    """
    if len(targets) != 5 or len(sizes) != 5:
        raise ValueError("a pinwheel is exactly five cells")
    W, H = rect.w, rect.h
    if W < 4 or H < 4:
        return None
    if sum(targets) <= 0:
        return None

    order = sorted(range(5), key=lambda i: targets[i])   # ascending target

    def spans(total: int) -> Optional[Tuple[int, int]]:
        """Two cuts splitting `total` into three spans, none degenerate."""
        p = [rng.uniform(SPAN_LO, SPAN_HI) for _ in range(3)]
        s = sum(p)
        first = round(total * p[0] / s)
        second = round(total * (p[0] + p[1]) / s)
        if not (1 <= first < second <= total - 1):
            return None
        return first, second

    best: Optional[List[Tuple[Rect, int]]] = None
    best_err = float("inf")
    for _ in range(PINWHEEL_SAMPLES):
        xs = spans(W)
        ys = spans(H)
        if xs is None or ys is None:
            continue
        a, b = xs
        c, d = ys
        ax, bx = rect.x1 + a, rect.x1 + b
        cy, dy = rect.y1 + c, rect.y1 + d
        cells = [
            Rect(rect.x1, rect.y1, bx, cy),        # R1  corner block
            Rect(bx, rect.y1, rect.x2, dy),        # R2  right arm
            Rect(ax, dy, rect.x2, rect.y2),        # R3  top arm
            Rect(rect.x1, cy, ax, rect.y2),        # R4  left arm
            Rect(ax, cy, bx, dy),                  # C   centre
        ]
        # Smallest cell to smallest target, and so on up.
        pairs = [(cells[j], order[rank]) for rank, j in
                 enumerate(sorted(range(5), key=lambda j: cells[j].area))]
        if not all(_capacity_ok(r, sizes[i]) for r, i in pairs):
            continue
        # A single-room cell must be able to *hold* its room, not merely be a
        # legal rectangle: `_leaf_ok`'s 3 m2 floor is far below a living room.
        if any(sizes[i] == 1 and
               (r.area < targets[i] * LEAF_AREA_FRAC
                or max(r.w, r.h) > LEAF_ASPECT * min(r.w, r.h))
               for r, i in pairs):
            continue
        err = sum(abs(r.area - targets[i]) / targets[i] for r, i in pairs)
        # Prefer compact cells: an arm that meets its area target as a strip is
        # a worse fixture than one that meets it as a room-shaped rectangle.
        err += 0.15 * sum(max(r.w, r.h) / min(r.w, r.h) for r, _ in pairs) / 5
        if err < best_err:
            best_err, best = err, pairs
    return best


def _partition(targets: Sequence[int], rng: random.Random
               ) -> Optional[List[List[int]]]:
    """Split room indices into the pinwheel's five groups.

    Three strategies, drawn at random, because no single one covers the range.
    Balancing the five loads (1) puts the living room in a cell one fifth the
    size of the plan and starves it; giving the biggest room a cell of its own
    (0) demands one compact cell of ~a third of the plan, which a pinwheel
    cannot always cut. `pinwheel_ground_truth` retries, so a strategy that fails
    on one Envelope costs an attempt rather than the run.
    """
    k = len(targets)
    if k < 5:
        return None
    order = sorted(range(k), key=lambda i: -targets[i])
    strategy = rng.randrange(3)

    if strategy == 0:                       # biggest room alone
        groups: List[List[int]] = [[order[0]], [], [], [], []]
        load = [targets[order[0]], 0, 0, 0, 0]
        for i in order[1:]:
            j = min(range(1, 5), key=lambda j: load[j])
            groups[j].append(i)
            load[j] += targets[i]
    elif strategy == 1:                     # balance the five loads
        groups = [[] for _ in range(5)]
        load = [0] * 5
        for i in order:
            j = min(range(5), key=lambda j: load[j])
            groups[j].append(i)
            load[j] += targets[i]
    else:                                   # random, seeded to stay non-empty
        idx = list(range(k))
        rng.shuffle(idx)
        groups = [[idx[j]] for j in range(5)]
        for i in idx[5:]:
            groups[rng.randrange(5)].append(i)

    return groups if all(groups) else None


def _dissect_pinwheel(
    rect: Rect, targets: List[int], rng: random.Random, budget: List[int],
    depth: int = 1, count: Optional[List[int]] = None,
) -> Optional[List[Rect]]:
    """Dissect `rect` into len(targets) rectangles, pinwheel at the top level.

    The five pinwheel cells take the rooms largest-first into the emptiest cell,
    the same rule `ground_truth` uses to spread rooms over Envelope parts.

    `depth` is the **dose**. At 1 the non-guillotine structure is exactly one
    level deep and everything below it reproduces the baseline generator's
    shapes — the mildest treatment that is still not guillotine. At higher
    values any cell still holding five rooms is pinwheeled again, so a large
    dwelling carries several. The dose axis exists so a null result cannot be
    dismissed as too small a perturbation.

    `count` accumulates how many pinwheels were actually placed.
    """
    k = len(targets)
    if k < 5 or depth < 1:
        return None
    if count is None:
        count = [0]

    groups = _partition(targets, rng)
    if groups is None:
        return None
    cell_targets = [sum(targets[i] for i in g) for g in groups]
    sizes = [len(g) for g in groups]

    pairs = pinwheel_cells(rect, cell_targets, rng, sizes)
    if pairs is None:
        return None
    count[0] += 1

    out: List[Optional[Rect]] = [None] * k
    for cell, gi in pairs:
        g = groups[gi]
        if len(g) == 1:
            out[g[0]] = cell
            continue
        scale = cell.area / sum(targets[i] for i in g)
        tg = [max(MIN_PIECE_AREA, round(targets[i] * scale)) for i in g]
        piece = None
        if depth > 1 and len(g) >= 5:
            piece = _dissect_pinwheel(cell, tg, rng, budget, depth - 1, count)
        if piece is None:
            piece = _guillotine(cell, tg, rng, budget)
        if piece is None:
            return None
        for i, r in zip(g, piece):
            out[i] = r
    if any(r is None for r in out):
        return None
    return [r for r in out if r is not None]


# ---------------------------------------------------------------------------
# Ground truth
# ---------------------------------------------------------------------------

PINWHEEL_ATTEMPTS = 40


def pinwheel_ground_truth(
    env: Envelope, kinds: Sequence[str], rng: random.Random, depth: int = 1,
    stats: Optional[Dict[str, int]] = None,
) -> List[Rect]:
    """A valid exact tiling of the Envelope that is **not** guillotine.

    Mirrors `scenarios.ground_truth` exactly — same area targets, same
    largest-room-into-emptiest-part assignment — and differs only in dissecting
    the part that holds the most rooms with a pinwheel instead of a cut.

    `depth` is the dose (see `_dissect_pinwheel`); `stats` receives the number
    of pinwheels actually placed.

    Raises ValueError if no non-guillotine tiling was reachable, which is a
    result about the Envelope, not a bug: a part holding four rooms or fewer has
    no non-guillotine tiling to find.
    """
    targets = area_targets(kinds, env.interior_area)
    order = sorted(range(len(targets)), key=lambda i: -targets[i])

    parts = sorted(env.parts, key=lambda p: -p.area)
    groups: List[List[int]] = [[] for _ in parts]
    remaining = [p.area for p in parts]
    for i in order:
        j = max(range(len(parts)), key=lambda j: remaining[j])
        groups[j].append(i)
        remaining[j] -= targets[i]
    if any(not g for g in groups):
        raise ValueError("a part of the Envelope received no rooms")

    # Pinwheel the part holding the most rooms; anything with fewer than five
    # cannot carry one. Where the area-proportional split leaves it short, pull
    # rooms across — smallest first, so the big part's area budget absorbs them
    # — but never empty another part, which `ground_truth` treats as a failure.
    pin = max(range(len(parts)), key=lambda j: len(groups[j]))
    while len(groups[pin]) < 5:
        donors = [j for j in range(len(parts))
                  if j != pin and len(groups[j]) > 1]
        if not donors:
            raise ValueError(
                f"largest Envelope part holds {len(groups[pin])} rooms and no "
                "other part can spare one; a non-guillotine tiling needs five")
        j = max(donors, key=lambda j: len(groups[j]))
        i = min(groups[j], key=lambda i: targets[i])
        groups[j].remove(i)
        groups[pin].append(i)

    for _ in range(PINWHEEL_ATTEMPTS):
        out: List[Rect] = []
        placed = [0]
        ok = True
        for j, (part, g) in enumerate(zip(parts, groups)):
            scale = part.area / sum(targets[i] for i in g)
            tg = [max(MIN_PIECE_AREA, round(targets[i] * scale)) for i in g]
            if j == pin:
                piece = _dissect_pinwheel(part, tg, rng, [400_000],
                                          depth, placed)
            else:
                piece = _guillotine(part, tg, rng, [400_000])
            if piece is None:
                ok = False
                break
            out.extend(piece)
        if not ok or len(out) != len(kinds):
            continue
        if not is_guillotine(out):
            if stats is not None:
                stats["pinwheels"] = placed[0]
            return out
    raise ValueError("no non-guillotine tiling after "
                     f"{PINWHEEL_ATTEMPTS} attempts")


def make_brief_pinwheel(
    name: str,
    env: Envelope,
    n_rooms: int,
    seed: int,
    door_min: int,
    window_min: int,
    required_frac: float = 0.30,
    forbidden_frac: float = 0.10,
    clear_t: int = 0,
    depth: int = 1,
) -> Tuple[scenarios.Brief, List[Rect], List[str]]:
    """`scenarios.make_brief` over a non-guillotine ground truth.

    Deliberately a copy rather than a parameter on `make_brief`: the baseline
    path must stay bit-identical so the guillotine arm of the sweep reproduces
    the published numbers exactly.
    """
    from geometry import adjacency_matrix

    mix = scenarios.composition(n_rooms)
    last = None
    for attempt in range(scenarios.BRIEF_ATTEMPTS):
        rng = random.Random(seed + attempt)
        try:
            truth = pinwheel_ground_truth(env, mix, rng, depth)
        except ValueError as e:
            last = e
            continue
        kinds = scenarios.assign_kinds(
            truth, env, door_min, window_min, seed + attempt,
            scenarios.comp_bounds(mix), clear_t)
        if kinds is None:
            last = "no valid room-type assignment"
            continue

        rooms = [scenarios.RoomSpec(f"{k}{i}", k, *scenarios.STANDARDS[k])
                 for i, k in enumerate(kinds)]
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
            scenarios.Brief(
                name=name, env=env, grid_mm=scenarios.GRID_MM, rooms=rooms,
                entry=entry, required_adj=required, forbidden_adj=forbidden,
                door_min=door_min, max_aspect=MAX_ASPECT,
            ),
            truth,
            kinds,
        )
    raise RuntimeError(
        f"{name}: no feasible non-guillotine Brief after "
        f"{scenarios.BRIEF_ATTEMPTS} attempts ({last})")


# ---------------------------------------------------------------------------
# Structure of a tiling — the covariates a timing difference has to be read
# against
# ---------------------------------------------------------------------------


def tiling_structure(rects: Sequence[Rect], door_min: int) -> Dict[str, float]:
    """Adjacency density and shape spread, so a solve-time difference between
    two tilings can be attributed rather than only observed.

    The ticket asserts a pinwheel "has a denser relation graph than a slicing
    layout". That is a measurable claim and this is what measures it.
    """
    from geometry import adjacency_matrix

    n = len(rects)
    pairs = n * (n - 1) / 2 if n > 1 else 1
    adj_door = adjacency_matrix(rects, door_min)
    adj_any = adjacency_matrix(rects, 1)
    n_door = sum(adj_door[i][j] for i in range(n) for j in range(i + 1, n))
    n_any = sum(adj_any[i][j] for i in range(n) for j in range(i + 1, n))

    # A separation is "unambiguous" when one axis strictly orders the pair --
    # the pairs `solver.fix_relations` can turn into a hard linear constraint.
    sep = 0
    for i in range(n):
        for j in range(i + 1, n):
            a, b = rects[i], rects[j]
            dx = a.x2 <= b.x1 or b.x2 <= a.x1
            dy = a.y2 <= b.y1 or b.y2 <= a.y1
            sep += (dx != dy)          # exactly one axis separates: unambiguous

    aspects = [max(r.w, r.h) / min(r.w, r.h) for r in rects]
    return {
        "n": n,
        "residue": guillotine_residue(rects),
        "adj_door": n_door,
        "adj_any": n_any,
        "adj_door_density": round(n_door / pairs, 4),
        "adj_any_density": round(n_any / pairs, 4),
        "unambiguous_sep": round(sep / pairs, 4),
        "aspect_mean": round(sum(aspects) / n, 3),
        "aspect_max": round(max(aspects), 3),
    }


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    from scenarios import DOOR_MIN, envelope_for

    ns = [int(x) for x in sys.argv[1:]] or [4, 5, 6, 7, 8, 10, 12, 16, 20, 24]
    print("Can this Envelope family carry a pinwheel, and how does the")
    print("relation graph move when it does? One seed, `detached`.\n")
    print(f"{'n':>4} {'baseline':>10} {'depth1':>8} {'wheels':>7} "
          f"{'depth3':>8} {'wheels':>7} {'adjG':>6} {'adjP1':>6} {'adjP3':>6} "
          f"{'sepG':>6} {'sepP3':>6}")
    for n in ns:
        env = envelope_for(n, "detached")
        mix = scenarios.composition(n)
        try:
            g = scenarios.ground_truth(env, mix, random.Random(20260817))
            gs = tiling_structure(g, DOOR_MIN)
            gtag = "guillo" if is_guillotine(g) else "NON-GUIL"
        except Exception:                                # noqa: BLE001
            gs, gtag = None, "err"
        cells = []
        for d in (1, 3):
            st: Dict[str, int] = {}
            try:
                p = pinwheel_ground_truth(env, mix, random.Random(20260817),
                                          d, st)
                cells.append((tiling_structure(p, DOOR_MIN),
                              "ok" if not is_guillotine(p) else "GUILL!",
                              st.get("pinwheels", 0)))
            except Exception:                            # noqa: BLE001
                cells.append((None, "none", 0))
        (p1, t1, w1), (p3, t3, w3) = cells

        def f(d, k):
            return f"{d[k]:>6.3f}" if d else f"{'-':>6}"
        print(f"{n:>4} {gtag:>10} {t1:>8} {w1:>7} {t3:>8} {w3:>7} "
              f"{f(gs,'adj_door_density')} {f(p1,'adj_door_density')} "
              f"{f(p3,'adj_door_density')} {f(gs,'unambiguous_sep')} "
              f"{f(p3,'unambiguous_sep')}")
