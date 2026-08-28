"""Which branch of the rig's gate actually fires, and what it admits.

Ticket 60. `pool_depth.py` prices the *depth* difference between
`absolute_area.gate_pool` (renamed `bucket_pool` by this ticket) and 2.2.1 as
written. This prices the two divergences that are not about depth:

  (a) the PRIMARY branch returns the whole multiset bucket, so it admits donors
      the area and aspect terms refuse -- how many, and how far outside;
  (b) the FALLBACK branch drops the multiset term entirely and scans by room
      COUNT, so it serves retrieval on Briefs where 2.2.1 says *"outside the
      gate, do not retrieve -- hand the Brief to source B"*.

(b) is the one that does not show up as depth: it converts a blank into a pool,
so every coverage figure measured through this rig counts a Brief as served that
the shipped system hands to source B.

No warp, no solve. Seconds.

Run: python experiments/warp/gate_sites.py [n]
"""

from __future__ import annotations

import json
import random
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fit_warp import SEED, AREA_TOL, ASPECT_TOL          # noqa: E402
from absolute_area import OUT, pct                       # noqa: E402
from best_of_m import load, gated_pool, BANDS            # noqa: E402


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    n_arg = int(args[0]) if args else 2000
    cands, by_ms, by_n = load()
    rng = random.Random(SEED)
    sample = rng.sample(cands, min(n_arg, len(cands)))
    print("converted dwellings joined to the room cache: %s"
          % format(len(cands), ","))
    print("sample %d Briefs, seed %d\n" % (len(sample), SEED))

    branch = defaultdict(int)
    excess, dist_a, dist_p = [], [], []
    fallback_depth, band_fallback = [], defaultdict(lambda: [0, 0])
    both_terms_refuse = one_term_refuses = 0
    for b in sample:
        bucket = [p for p in by_ms.get(b["ms"], []) if p["k"] != b["k"]]
        adm = gated_pool(b, by_ms)
        for band, rr in BANDS.items():
            if b["n"] in rr:
                band_fallback[band][1] += 1
        if bucket:
            branch["primary (bucket non-empty)"] += 1
            refused = len(bucket) - len(adm)
            excess.append(refused)
            for p in bucket:
                da = abs(b["area"] - p["area"]) / (AREA_TOL * p["area"])
                dp = abs(b["aspect"] - p["aspect"]) / (ASPECT_TOL * p["aspect"])
                if da > 1 or dp > 1:
                    dist_a.append(da)
                    dist_p.append(dp)
                    if da > 1 and dp > 1:
                        both_terms_refuse += 1
                    else:
                        one_term_refuses += 1
            if not adm:
                branch["  ...and the GATE would have been blank"] += 1
        else:
            fb = [p for p in by_n.get(b["n"], [])
                  if p["k"] != b["k"]
                  and abs(b["area"] - p["area"]) <= AREA_TOL * p["area"]
                  and abs(b["aspect"] - p["aspect"]) <= ASPECT_TOL * p["aspect"]]
            if fb:
                branch["fallback fired (by room count, off-multiset)"] += 1
                fallback_depth.append(len(fb))
                for band, rr in BANDS.items():
                    if b["n"] in rr:
                        band_fallback[band][0] += 1
            else:
                branch["blank in both"] += 1

    n = len(sample)
    print("--- which branch of the pre-60 gate_pool fires ---")
    for k, v in branch.items():
        print("  %-46s%6d%8.1f%%" % (k, v, 100 * v / n))

    print("\n--- (a) primary branch: donors admitted that the gate refuses ---")
    tot_refused = sum(excess)
    tot_bucket = sum(excess) + sum(len(gated_pool(b, by_ms)) for b in sample
                                   if by_ms.get(b["ms"]))
    print("  bucket members the two terms refuse: %s of %s = %.1f%%"
          % (format(tot_refused, ","), format(tot_bucket, ","),
             100 * tot_refused / max(1, tot_bucket)))
    print("  per Brief, refused members p50 %.0f  p90 %.0f  max %d"
          % (pct(excess, 0.5), pct(excess, 0.9), max(excess) if excess else 0))
    print("  of the refused, refused by BOTH terms %.1f%%, by one only %.1f%%"
          % (100 * both_terms_refuse / max(1, both_terms_refuse + one_term_refuses),
             100 * one_term_refuses / max(1, both_terms_refuse + one_term_refuses)))
    print("  how far outside, in units of the tolerance:")
    print("    area   p50 %.2f  p90 %.2f  max %.1f"
          % (pct(dist_a, 0.5), pct(dist_a, 0.9), max(dist_a) if dist_a else 0))
    print("    aspect p50 %.2f  p90 %.2f  max %.1f"
          % (pct(dist_p, 0.5), pct(dist_p, 0.9), max(dist_p) if dist_p else 0))

    print("\n--- (b) fallback branch: retrieval where 2.2.1 hands to source B ---")
    if fallback_depth:
        print("  Briefs served only by the fallback: %d = %.1f%% of the sample"
              % (len(fallback_depth), 100 * len(fallback_depth) / n))
        print("  pool it invents: p50 %.0f  p90 %.0f  max %d"
              % (pct(fallback_depth, 0.5), pct(fallback_depth, 0.9),
                 max(fallback_depth)))
        for band in ("4-6", "7-10"):
            f, t = band_fallback[band]
            if t:
                print("    %-6s %d of %d Briefs = %.1f%%" % (band, f, t, 100 * f / t))
    else:
        print("  never fires on this sample")

    out = {"sample": n, "branch": dict(branch),
           "refused_by_terms_share": round(tot_refused / max(1, tot_bucket), 4),
           "refused_per_brief_p50": pct(excess, 0.5) if excess else 0,
           "refused_per_brief_p90": pct(excess, 0.9) if excess else 0,
           "refused_by_both_terms_share": round(
               both_terms_refuse / max(1, both_terms_refuse + one_term_refuses), 4),
           "d_area_p50": round(pct(dist_a, 0.5), 3) if dist_a else None,
           "d_aspect_p50": round(pct(dist_p, 0.5), 3) if dist_p else None,
           "fallback_briefs": len(fallback_depth),
           "fallback_share": round(len(fallback_depth) / n, 4),
           "fallback_depth_p50": pct(fallback_depth, 0.5) if fallback_depth else 0,
           "blank_in_both": branch.get("blank in both", 0),
           "gate_blank_but_rig_served": branch.get(
               "  ...and the GATE would have been blank", 0)}
    OUT.mkdir(exist_ok=True)
    json.dump(out, open(OUT / "gate_sites.json", "w"), indent=1)
    print("\nwrote %s" % (OUT / "gate_sites.json"))


if __name__ == "__main__":
    main()
