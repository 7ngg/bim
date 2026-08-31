"""Read `repeat_seeds.py`'s grid and answer ticket 83 items 3 and 4.

Three questions, in the order they have to be answered:

  Q1  THE SEED SPREAD THE NOTE OWES. Arm `base`, one instance per room count,
      12 CP-SAT seeds. What moves and what does not -- reported separately for
      status, objective and seconds, because ADR 0043 decision 5 permits a gate
      to assert the first two and forbids it the third.

  Q2  DOES A RUN REPEAT ITSELF? Every cell was solved twice. Two runs agree iff
      status, objective AND the Plan fingerprint are identical. Reported per
      arm, which is what prices determinism rather than asserting it.

  Q3  WHAT `interleave_search` COSTS. `base` against `il` paired on
      (n, seed, replicate) at the same 15 s wall cap: objective, status,
      validity and time to first Plan. Then `det` -- ADR 0043 decision 5's
      whole prescription -- against both.

    python experiments/solver-toy/repeat_seeds_report.py [--tag=main]
"""

from __future__ import annotations

import argparse
import json
import pathlib
import statistics as st
from collections import defaultdict

HERE = pathlib.Path(__file__).resolve().parent
RESULTS = HERE / "results"


def load(tag):
    rows = [json.loads(l) for l in
            open(RESULTS / f"repeat_seeds_{tag}.jsonl", encoding="utf-8")]
    meta_p = RESULTS / f"repeat_seeds_meta_{tag}.json"
    meta = json.load(open(meta_p, encoding="utf-8")) if meta_p.exists() else {}
    return rows, meta


def spread(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return None
    return {"n": len(xs), "min": min(xs), "p50": st.median(xs), "max": max(xs),
            "range": max(xs) - min(xs)}


def fmt(s, unit="", dp=3):
    if s is None:
        return "--"
    f = f"%.{dp}f"
    return (f"{f % s['min']}{unit} .. {f % s['max']}{unit}  "
            f"(p50 {f % s['p50']}{unit}, range {f % s['range']}{unit})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="main")
    a = ap.parse_args()
    rows, meta = load(a.tag)

    print("=" * 78)
    print("ticket 83 items 3 and 4 -- the owed seed repeat, and the price of "
          "interleave_search")
    print("=" * 78)
    if meta:
        print(f"ortools {meta.get('ortools')}  python {meta.get('python')}  "
              f"machine {meta.get('machine')}")
        print(f"workers {meta.get('workers')} | scenario seed "
              f"{meta.get('scenario_seed')} FIXED | solver seeds "
              f"{meta.get('solver_seeds', [])[:3]}.."
              f"{meta.get('solver_seeds', [])[-1:]} "
              f"x {meta.get('replicates')} replicates")
        print(f"exposure {meta.get('exposure')}  tau {meta.get('tau')}  "
              f"sigma {meta.get('sigma')}  rig {meta.get('rig')}  "
              f"erode {meta.get('erode')}  t_int {meta.get('t_int_mm')}")
        print(f"caps: base/il max_time_in_seconds = {meta.get('wall_cap_s')} s "
              f"(machine-local) | det max_deterministic_time = "
              f"{meta.get('det_budget')} (publishable)")
    print(f"{len(rows)} rows")

    arms = [x for x in ("base", "il", "det")
            if any(r["arm"] == x for r in rows)]
    ns = sorted({r["n"] for r in rows})

    # ---------------------------------------------------------------- Q1 ----
    print()
    print("-" * 78)
    print("Q1  THE SEED SPREAD  --  arm `base`, the configuration every "
          "published number used")
    print("-" * 78)
    print("    One instance per room count. Only CP-SAT's random_seed moves, "
          "which is what")
    print("    'CP-SAT's portfolio search is stochastic across workers' means "
          "and what the")
    print("    eight seeds already run could not isolate.")
    print()
    hdr = (f"{'n':>3}  {'runs':>4}  {'status':<22}  {'objective':<20}  "
           f"{'valid':>6}")
    print(hdr)
    print("-" * len(hdr))
    for n in ns:
        rs = [r for r in rows if r["n"] == n and r["arm"] == "base"]
        if not rs:
            continue
        sts = defaultdict(int)
        for r in rs:
            sts[r["status"]] += 1
        objs = sorted({r["objective"] for r in rs if r.get("objective") is not None})
        nv = sum(1 for r in rs if r.get("valid"))
        so = (f"{objs[0]}" if len(objs) == 1
              else f"{len(objs)} distinct {objs[0]}..{objs[-1]}")
        print(f"{n:>3}  {len(rs):>4}  "
              f"{','.join(f'{k} {v}' for k, v in sorted(sts.items())):<22}  "
              f"{so:<20}  {nv}/{len(rs)}")
    print()
    print("    seconds -- reported as a spread and asserted at nothing "
          "(ADR 0043 decision 5)")
    print()
    for n in ns:
        rs = [r for r in rows if r["n"] == n and r["arm"] == "base"]
        if not rs:
            continue
        print(f"    n={n:<3} wall     {fmt(spread([r.get('wall') for r in rs]), ' s')}")
        print(f"         first    {fmt(spread([r.get('first') for r in rs]), ' s')}")
        print(f"         valid_at {fmt(spread([r.get('valid_at') for r in rs]), ' s')}")
        print(f"         dtime    {fmt(spread([r.get('dtime') for r in rs]), '')}")
        plans = {r.get("plan") for r in rs}
        print(f"         distinct Plans off ONE Proposal: {len(plans)} "
              f"of {len(rs)} runs")
    print()

    # ---------------------------------------------------------------- Q2 ----
    print("-" * 78)
    print("Q2  DOES A RUN REPEAT ITSELF  --  every cell solved twice, same "
          "seed, same model")
    print("-" * 78)
    print("    Two runs AGREE iff status, objective and the Plan fingerprint "
          "are all identical.")
    print()
    hdr = (f"{'arm':<5}  {'n':>3}  {'cells':>5}  {'status =':>9}  "
           f"{'objective =':>12}  {'PLAN =':>8}")
    print(hdr)
    print("-" * len(hdr))
    det_summary = {}
    for arm in arms:
        for n in ns:
            byseed = defaultdict(dict)
            for r in rows:
                if r["arm"] == arm and r["n"] == n:
                    byseed[r["solver_seed"]][r["rep"]] = r
            pairs = [(v[0], v[1]) for v in byseed.values() if 0 in v and 1 in v]
            if not pairs:
                continue
            ss = sum(1 for x, y in pairs if x["status"] == y["status"])
            oo = sum(1 for x, y in pairs if x.get("objective") == y.get("objective"))
            pp = sum(1 for x, y in pairs if x.get("plan") == y.get("plan"))
            det_summary[(arm, n)] = (len(pairs), ss, oo, pp)
            print(f"{arm:<5}  {n:>3}  {len(pairs):>5}  {ss:>4}/{len(pairs):<4}  "
                  f"{oo:>6}/{len(pairs):<5}  {pp:>3}/{len(pairs):<4}")
    print()
    for arm in arms:
        tot = [v for k, v in det_summary.items() if k[0] == arm]
        if not tot:
            continue
        c = sum(x[0] for x in tot)
        print(f"    {arm:<5} {sum(x[1] for x in tot)}/{c} status, "
              f"{sum(x[2] for x in tot)}/{c} objective, "
              f"{sum(x[3] for x in tot)}/{c} PLAN identical across a repeat")
    print()

    # ---------------------------------------------------------------- Q3 ----
    print("-" * 78)
    print("Q3  THE PRICE OF `interleave_search`  --  paired on (n, seed, "
          "replicate)")
    print("-" * 78)
    idx = {(r["arm"], r["n"], r["solver_seed"], r["rep"]): r for r in rows}
    for other in [x for x in arms if x != "base"]:
        print(f"\n    base -> {other}")
        hdr = (f"    {'n':>3}  {'pairs':>5}  {'obj better':>10}  "
               f"{'obj worse':>9}  {'obj =':>6}  {'status changed':>14}  "
               f"{'valid':>11}")
        print(hdr)
        print("    " + "-" * (len(hdr) - 4))
        for n in ns:
            pairs = []
            for k, r in idx.items():
                if k[0] != "base" or k[1] != n:
                    continue
                o = idx.get((other,) + k[1:])
                if o is not None:
                    pairs.append((r, o))
            if not pairs:
                continue
            better = worse = same = stc = 0
            vb = vo = 0
            for b, o in pairs:
                ob, oo = b.get("objective"), o.get("objective")
                if ob is not None and oo is not None:
                    if oo < ob:
                        better += 1
                    elif oo > ob:
                        worse += 1
                    else:
                        same += 1
                if b["status"] != o["status"]:
                    stc += 1
                vb += bool(b.get("valid"))
                vo += bool(o.get("valid"))
            print(f"    {n:>3}  {len(pairs):>5}  {better:>10}  {worse:>9}  "
                  f"{same:>6}  {stc:>14}  {vb:>4} -> {vo:<4}")
        print()
        for n in ns:
            b = [r for r in rows if r["arm"] == "base" and r["n"] == n]
            o = [r for r in rows if r["arm"] == other and r["n"] == n]
            if not b or not o:
                continue
            sb, so = spread([x.get("first") for x in b]), spread([x.get("first") for x in o])
            wb, wo = spread([x.get("wall") for x in b]), spread([x.get("wall") for x in o])
            if sb and so:
                print(f"    n={n:<3} first Plan  base p50 {sb['p50']:.3f} s "
                      f"-> {other} p50 {so['p50']:.3f} s")
            if wb and wo:
                print(f"         wall        base p50 {wb['p50']:.3f} s "
                      f"-> {other} p50 {wo['p50']:.3f} s")
    print()
    print("=" * 78)


if __name__ == "__main__":
    main()
