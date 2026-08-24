"""Per room *type*, how often does a free solver reach for a second rectangle?

`sweep_k2.py` records which kinds became gratuitous Ls, and a raw count is not a
rate: `scenarios.composition(n)` is NOT the Brief's actual kind multiset, because
`assign_kinds` draws from a filler list within `comp_bounds`, so kinds appear that
`composition` never names. An earlier reading of these results used it as the
denominator and got the rates wrong.

This regenerates each (n, seed) Brief the sweep actually solved — same seeds, same
envelope, same `clear_t` — takes its real kind multiset, and joins it to the
sweep's L counts. That gives the number the qualitative question needs: does a
solver left to choose put Ls on the room types real dwellings keep RECTANGULAR?

Corpus rectangularity for comparison comes from `k_tolerance.py`, so both sides
are measured rather than assumed.

Run: python experiments/room-rectangles/kind_rates.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

TOY = Path(__file__).resolve().parents[1] / "solver-toy"
sys.path.insert(0, str(TOY))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import scenarios  # noqa: E402
from scenarios import envelope_for, make_brief, mm  # noqa: E402

scenarios.ASSIGN_WORKERS = 4
OUT = Path(__file__).resolve().parent / "out"
T_INT = 150
DOOR_MIN = mm(1.0)

# k_tol = 1 share, from k_tolerance.py, mapped onto the toy's kind vocabulary.
# `wc` has no corpus row of its own -- the corpus label is `BATHROOM` and the
# split is an area threshold, so it inherits BATHROOM and is marked.
CORPUS_K1 = {
    "bedroom": ("BEDROOM", 0.7206), "study": ("ROOM", 0.6942),
    "storage": ("STOREROOM", 0.7203), "utility": ("STOREROOM", 0.7203),
    "bathroom": ("BATHROOM", 0.6181), "wc": ("BATHROOM*", 0.6181),
    "kitchen": ("KITCHEN", 0.4402), "living": ("LIVING_ROOM", 0.4980),
    "dining": ("LIVING_DINING", 0.2633), "corridor": ("CORRIDOR", 0.3034),
    "hall": ("CORRIDOR", 0.3034),
}


def main() -> None:
    rows = [r for r in json.loads((OUT / "sweep_k2.json").read_text())
            if r["status"] != "NO_SCENARIO"]
    pairs = sorted({(r["n"], r["seed"]) for r in rows})
    kinds_of = {}
    for n, seed in pairs:
        try:
            env = envelope_for(n, "corpus_median")
            _b, _t, kinds = make_brief(f"{n}-room", env, n, seed, DOOR_MIN,
                                       scenarios.WINDOW_MIN, clear_t=T_INT)
            kinds_of[(n, seed)] = list(kinds)
        except Exception as e:                       # noqa: BLE001 - a result
            print(f"  (n={n} seed={seed} could not regenerate: {str(e)[:60]})")
    print(f"regenerated {len(kinds_of)} of {len(pairs)} Briefs\n")

    for arm in ("free_all", "free_scoped", "forced2"):
        num, den = Counter(), Counter()
        runs = 0
        for r in rows:
            if r["arm"] != arm or not r.get("valid"):
                continue
            ks = kinds_of.get((r["n"], r["seed"]))
            if ks is None:
                continue
            runs += 1
            elig = ks if arm != "free_scoped" else [
                k for k in ks if k in
                __import__("solver_parts").CIRCULATION_AND_OPEN]
            den.update(elig)
            num.update(r.get("l_kinds", []))
        if not runs:
            continue
        print("=" * 78)
        print(f"{arm}  ({runs} valid runs) -- share of that kind's Rooms made an L")
        print("=" * 78)
        print(f"{'kind':<12}{'Ls':>5}{'chances':>9}{'rate':>8}   "
              f"{'corpus type':<15}{'corpus k_tol=1':>15}")
        for k in sorted(den, key=lambda x: -(num[x] / den[x])):
            ct, cv = CORPUS_K1.get(k, ("-", float("nan")))
            print(f"{k:<12}{num[k]:>5}{den[k]:>9}{num[k] / den[k]:>8.3f}   "
                  f"{ct:<15}{cv:>15.4f}")
        # Is the ordering inverted? Rank correlation between the solver's rate
        # and the corpus's rectangularity, over kinds with a corpus row.
        xs = [(num[k] / den[k], CORPUS_K1[k][1]) for k in den if k in CORPUS_K1]
        if len(xs) >= 4:
            print(f"\n   Spearman(solver L-rate, corpus k=1 share) = "
                  f"{spearman([a for a, _ in xs], [b for _, b in xs]):+.3f}")
            print("   negative = the solver prefers the types real dwellings keep "
                  "rectangular")
        print()


def spearman(a, b):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    ra, rb = rank(a), rank(b)
    n = len(a)
    ma, mb = sum(ra) / n, sum(rb) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    va = sum((x - ma) ** 2 for x in ra) ** 0.5
    vb = sum((y - mb) ** 2 for y in rb) ** 0.5
    return cov / (va * vb) if va and vb else float("nan")


if __name__ == "__main__":
    main()
