"""How deep a pool can this rig actually draw, and how deep is production?

Ticket 57. `absolute_area.py`'s pool arms are measured at `--pool=8` because
`proposer.md` 2.2.7's second limit says the sample is the 2,317 converted
dwellings of the ADR 0016 sample, not the full index, so *"a pool of 87 in
production is a pool of 8 here"*. That sentence is the premise the whole
best-of-m question rests on, and it states a **ratio** while never measuring the
**distribution**. A best-of-m curve cannot be run past the depth the sample
holds, so this is the cheap prerequisite: no warp, no solve.

Three pool definitions, because they are not the same and the difference is the
whole answer:

  `rig`    -- what `absolute_area.gate_pool` actually returns. Its primary branch
              returns the WHOLE multiset bucket and applies the area and aspect
              terms only in the by-room-count fallback.
  `gated`  -- the shipped three-term gate of 2.2.1 -- *"the gate's first term is
              an exact match, so the bucket is the pool and the other two terms
              are a scan of it"* -- over the same converted sample.
  `prod`   -- `coverage_restated.py`'s published depth over the full
              46,794-dwelling index, gated the same way and thinned by the
              per-multiset conversion rate. 86.6 at 4-6 rooms, 58.7 at 7-10.

Run: python experiments/warp/pool_depth.py [n]
"""

from __future__ import annotations

import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fit_warp import COLLAPSE, SEED, AREA_TOL, ASPECT_TOL   # noqa: E402
from absolute_area import FIT, ROOMS, OUT, gate_pool, pct   # noqa: E402

BANDS = {"4-6": range(4, 7), "7-10": range(7, 11)}
PROD_MEDIAN = {"4-6": 86.6, "7-10": 58.7}   # coverage_restated.py, full index


def load():
    recs = {r["k"]: r for r in json.load(open(ROOMS))}
    fits = [r for r in json.load(open(FIT)) if r["status"] in ("OPTIMAL", "FEASIBLE")]
    cands = []
    for f in fits:
        r = recs.get(f["k"])
        if not r or f["n"] != r["n"]:
            continue
        c = dict(f)
        c.update(area=r["area"], aspect=r["aspect"], rooms=r["rooms"], k=f["k"])
        c["ms"] = tuple(sorted(Counter(COLLAPSE.get(t, t)
                                       for t, _ in r["rooms"]).items()))
        cands.append(c)
    by_ms, by_n = defaultdict(list), defaultdict(list)
    for c in cands:
        by_ms[c["ms"]].append(c)
        by_n[c["n"]].append(c)
    return recs, cands, by_ms, by_n


def gated_pool(brief, by_ms):
    """2.2.1 as written: the bucket, scanned by the other two terms."""
    return [p for p in by_ms.get(brief["ms"], [])
            if p["k"] != brief["k"]
            and abs(brief["area"] - p["area"]) <= AREA_TOL * p["area"]
            and abs(brief["aspect"] - p["aspect"]) <= ASPECT_TOL * p["aspect"]]


def report(name, per_band, out):
    print(f"\n--- pool definition: {name} ---")
    print(f"{'band':<7}{'briefs':>8}{'p10':>7}{'p25':>7}{'p50':>7}{'p75':>7}"
          f"{'p90':>7}{'max':>7}{'empty':>8}{'>=8':>7}{'>=16':>7}{'>=32':>7}"
          f"{'>=64':>7}{'prod p50':>10}")
    for band in ("all", "4-6", "7-10"):
        ds = per_band.get(band)
        if not ds:
            continue
        m = len(ds)
        p = {q: pct(ds, q / 100) for q in (10, 25, 50, 75, 90)}
        ge = {t: sum(1 for d in ds if d >= t) / m for t in (8, 16, 32, 64)}
        empty = sum(1 for d in ds if d == 0) / m
        prod = PROD_MEDIAN.get(band)
        print(f"{band:<7}{m:>8,}{p[10]:>7.0f}{p[25]:>7.0f}{p[50]:>7.0f}"
              f"{p[75]:>7.0f}{p[90]:>7.0f}{max(ds):>7,}{100*empty:>7.0f}%"
              f"{100*ge[8]:>6.0f}%{100*ge[16]:>6.0f}%{100*ge[32]:>6.0f}%"
              f"{100*ge[64]:>6.0f}%"
              + (f"{prod:>10.1f}" if prod else f"{'-':>10}"))
        out[f"{name}:{band}"] = {
            "briefs": m, "p25": p[25], "p50": p[50], "p75": p[75], "p90": p[90],
            "max": max(ds), "empty_share": round(empty, 4),
            "share_ge_8": round(ge[8], 4), "share_ge_16": round(ge[16], 4),
            "share_ge_32": round(ge[32], 4), "share_ge_64": round(ge[64], 4),
            "prod_median": prod}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    n_arg = int(args[0]) if args else 200
    recs, cands, by_ms, by_n = load()
    print(f"full room cache: {len(recs):,} dwellings")
    print(f"converted dwellings joined to the room cache: {len(cands):,}")

    rng = random.Random(SEED)
    sample = rng.sample(cands, min(n_arg, len(cands)))
    print(f"sample: {len(sample)} Briefs, seed {SEED} "
          f"(the same draw absolute_area.py makes)")

    out = {}
    for name, fn in (("rig", lambda b: gate_pool(b, by_ms, by_n)),
                     ("gated", lambda b: gated_pool(b, by_ms))):
        per_band = defaultdict(list)
        for b in sample:
            d = len(fn(b))
            per_band["all"].append(d)
            for band, rr in BANDS.items():
                if b["n"] in rr:
                    per_band[band].append(d)
        report(name, per_band, out)

    print("\n'>=m' is the share of Briefs whose pool holds at least m candidates")
    print("-- the share for which a best-of-m point is measured on a full pool")
    print("rather than on a truncated one. 'empty' is a Brief retrieval cannot")
    print("serve at all, which falls to source B and is not a starvation.")
    OUT.mkdir(exist_ok=True)
    json.dump(out, open(OUT / "pool_depth.json", "w"), indent=1)
    print(f"\nwrote {OUT/'pool_depth.json'}")


if __name__ == "__main__":
    main()
