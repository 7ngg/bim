"""Ticket 24 — *why* does a confident-wrong relation kill a solve?

`probe6.py` shows that it does. This asks by what mechanism, and the candidate is
arithmetic rather than combinatorial.

A posted relation `x2[a] <= x1[b]` is an edge in a per-axis digraph. Along any
directed path the rooms sit strictly side by side, so the Envelope must be at
least the sum of their minimum widths. The longest such path is therefore a lower
bound on the Envelope, computable in O(pairs) with no solver at all:

    need_x = max over directed paths P in the x-digraph of sum(min_w[i] for i in P)

The truth's own relation set always satisfies `need_x <= W` and `need_y <= H` —
it describes a real tiling. Flipping one relation can add an edge that extends a
path, and if that pushes `need` past the Envelope the model is infeasible by
counting, not by search.

If that is the mechanism, two things follow, and both are worth more than the
correlation:

  * `docs/spec/proposer.md` 5.2 explains failure by a **directed cycle**. A cycle
    is not the only unrealisable relation set, and it is not the one that occurs:
    the extractor's guard makes cycles impossible, while over-long chains are
    left entirely unchecked.
  * a Proposer can run this check on its own output, before a solve and without a
    ground truth, which the metric itself cannot do.

    python mechanism6.py
"""

from __future__ import annotations

import json
import pathlib
import random
import zlib
from collections import defaultdict
from typing import Dict, List, Sequence, Tuple

import arrangement as A
import probe6
from solver import extract_relations

RESULTS = pathlib.Path(__file__).parent / "results"
Relation = Tuple[str, int, int]


def longest_chain(relations: Sequence[Relation], axis: str, n: int,
                  weight: Sequence[int]) -> int:
    """Heaviest directed path in the per-axis digraph, by node weight.

    The graph is acyclic whenever the guard ran, so a memoised DFS is enough. An
    unguarded set may contain a cycle; those are reported separately and never
    reach here.
    """
    succ: Dict[int, List[int]] = {i: [] for i in range(n)}
    for ax, a, b in relations:
        if ax == axis:
            succ[a].append(b)
    best: Dict[int, int] = {}

    def walk(u: int) -> int:
        if u in best:
            return best[u]
        best[u] = weight[u] + max((walk(v) for v in succ[u]), default=0)
        return best[u]

    return max((walk(i) for i in range(n)), default=0)


def has_cycle(relations: Sequence[Relation], axis: str, n: int) -> bool:
    succ: Dict[int, List[int]] = {i: [] for i in range(n)}
    for ax, a, b in relations:
        if ax == axis:
            succ[a].append(b)
    state = [0] * n

    def dfs(u: int) -> bool:
        state[u] = 1
        for v in succ[u]:
            if state[v] == 1 or (state[v] == 0 and dfs(v)):
                return True
        state[u] = 2
        return False

    return any(state[i] == 0 and dfs(i) for i in range(n))


def budget(brief, relations: Sequence[Relation]) -> dict:
    n = brief.n
    env = brief.env
    minw = [r.min_w for r in brief.rooms]
    minh = [r.min_h for r in brief.rooms]
    cx = has_cycle(relations, "x", n)
    cy = has_cycle(relations, "y", n)
    need_x = None if cx else longest_chain(relations, "x", n, minw)
    need_y = None if cy else longest_chain(relations, "y", n, minh)
    return {
        "cycle_x": cx, "cycle_y": cy,
        "need_x": need_x, "W": env.W,
        "need_y": need_y, "H": env.H,
        "over_x": None if cx else need_x > env.W,
        "over_y": None if cy else need_y > env.H,
        "dead": cx or cy or (need_x > env.W) or (need_y > env.H),
    }


def rng_for(row: dict) -> random.Random:
    return random.Random(zlib.crc32(
        "|".join(str(row.get(f)) for f in probe6.RNG_FIELDS).encode()))


def main() -> None:
    rows = [json.loads(l) for l in (RESULTS / "P6.jsonl").open(encoding="utf-8")
            if l.strip()]
    rs = [r for r in rows if r["suite"] in ("A", "A2")]

    print("Control: the truth's own relation set, which describes a real tiling")
    print(f"{'n':>3} {'need_x':>7} {'W':>4} {'need_y':>7} {'H':>4} {'dead':>6}")
    for n in probe6.ROOM_COUNTS:
        brief, truth, _kinds = probe6.get(n, probe6.DEFAULT_SEED)
        base, _a, _c = extract_relations(truth, probe6.TAU)
        b = budget(brief, base)
        print(f"{n:>3} {b['need_x']:>7} {b['W']:>4} {b['need_y']:>7} "
              f"{b['H']:>4} {str(b['dead']):>6}")

    print()
    print("Injected sets: is the model dead by counting, before any search?")
    print("`dead` means one axis needs more Envelope than there is, or the set "
          "is cyclic.")
    print()
    print(f"{'suite':>5} {'n':>3} {'k':>3} {'runs':>5} {'INFEASIBLE':>10} "
          f"{'dead by chain':>13} {'cyclic':>7} {'chain explains':>14}")
    by = defaultdict(list)
    for r in rs:
        by[(r["suite"], r["n"], r["k"])].append(r)
    tot_inf = tot_expl = 0
    for key in sorted(by):
        suite, n, k = key
        g = by[key]
        infe = dead = cyc = expl = 0
        for r in g:
            brief, truth, _kinds = probe6.get(n, r["seed"])
            base, _a, _c = extract_relations(truth, probe6.TAU)
            posted, _d, _f = A.inject_wrong(base, k, rng_for(r), n,
                                            mode=r["mode"] or "any",
                                            guarded=bool(r["guarded"]))
            b = budget(brief, posted)
            if b["dead"]:
                dead += 1
            if b["cycle_x"] or b["cycle_y"]:
                cyc += 1
            if r["status"] == "INFEASIBLE":
                infe += 1
                if b["dead"]:
                    expl += 1
        tot_inf += infe
        tot_expl += expl
        pc = f"{100*expl/infe:.0f}%" if infe else "-"
        print(f"{suite:>5} {n:>3} {k:>3} {len(g):>5} {infe:>10} {dead:>13} "
              f"{cyc:>7} {pc:>14}")
    if tot_inf:
        print()
        print(f"Overall: {tot_expl}/{tot_inf} "
              f"({100*tot_expl/tot_inf:.0f}%) of INFEASIBLE runs are already "
              f"dead on the chain bound alone.")


def blame(limit_k=(1, 2, 3)) -> None:
    """The low doses the chain bound cannot explain. What breaks instead?

    Coverage is already soft in the shipped configuration, so an INFEASIBLE run
    is being killed by one of the four families that stay hard. Soften them one
    at a time, relations still hard, and see which one buys feasibility back.

    CP-SAT's own assumption core is not used: asked for a sufficient set it
    returns *all five* families at every size, which is the same non-minimality
    ticket 15 reported for `solver._core`. Softening one family at a time is
    slower and actually discriminates.
    """
    from copy import deepcopy

    rows = [json.loads(l) for l in (RESULTS / "P6.jsonl").open(encoding="utf-8")
            if l.strip()]
    rs = [r for r in rows if r["suite"] == "A" and r["k"] in limit_k
          and r["status"] == "INFEASIBLE"]
    if not rs:
        print("no INFEASIBLE low-dose rows yet")
        return
    fams = ("required_adj", "exterior", "wet_cluster", "circulation")
    print()
    print("Low-dose INFEASIBLE runs: which HARD family does the wrong relation")
    print("break? Coverage is soft already, so it cannot be the answer.")
    print("`geometry` means no single family rescued it -- the asserted")
    print("arrangement does not pack into the Envelope at all.")
    print()
    print(f"{'n':>3} {'k':>3} {'seed':>9} {'viol':>5} {'chain dead':>10} "
          f"{'rescued by':>14}")
    tally = defaultdict(int)
    for r in sorted(rs, key=lambda r: (r["n"], r["k"], r["seed"])):
        n = r["n"]
        brief, truth, kinds = probe6.get(n, r["seed"])
        base, _a, _c = extract_relations(truth, probe6.TAU)
        posted, _d, _f = A.inject_wrong(base, r["k"], rng_for(r), n,
                                        mode=r["mode"] or "any",
                                        guarded=bool(r["guarded"]))
        b = budget(brief, posted)
        prop = probe6.truth_proposal(truth, kinds, r["seed"])
        rescued = []
        for fam in fams:
            cfg = deepcopy(probe6.cfg_free())
            cfg.soft = ("coverage", fam)
            if A.project_with(brief, prop, posted, cfg).status != "INFEASIBLE":
                rescued.append(fam)
        key = "+".join(rescued) if rescued else "geometry"
        tally[key] += 1
        print(f"{n:>3} {r['k']:>3} {r['seed']:>9} {r['violated_posted']:>5} "
              f"{str(b['dead']):>10} {key:>14}")
    print()
    print("Tally:")
    for k, v in sorted(tally.items(), key=lambda kv: -kv[1]):
        print(f"  {v:>3}  {k}")


if __name__ == "__main__":
    main()
    blame()
