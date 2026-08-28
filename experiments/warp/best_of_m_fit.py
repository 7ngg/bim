"""The best-of-m curve, fitted and extrapolated to production pool depth.

Ticket 57. `best_of_m.py` measures the curve as far as the converted sample can
hold it. Production pool depth is **86.6** at 4-6 rooms and **58.7** at 7-10
(`coverage_restated.py`, full 46,794-dwelling index) and the sample cannot reach
either under the shipped gate. The ticket names two routes and this is the second
one: **fit the curve and publish it as an extrapolation, labelled as such.**

## The model, and the one it replaces

Independence is already known to be wrong here by a factor of 780 -- ADR 0018
consequence 3, and `absolute_area.py` §5a reproducing it -- because every
candidate for one Brief is sized from one Envelope, so the decline probability is
a property of the **Brief**. That says: mixture, not `q^m`.

⚠️ **A plain Beta mixture is ALSO wrong, and it fails in the dangerous
direction.** `E[p^m] = B(a+m, b)/B(a,b)` tends to zero for every Beta, so it
predicts that enough pool depth serves every Brief. The measured curve says
otherwise: on the gated pool it is **flat at 8,2 % from m = 6 to m = 64**, and
fitting a plain Beta to that data returns 0,45 % at m = 8 against a measured 8,2 %
-- an answer contradicted by the column next to it. Published, it would have said
*deepen the pool* is free.

The fix is a **point mass at p = 1**: a share of Briefs retrieval does not serve
at any depth, because the pool is a corpus and the corpus may simply not hold an
arrangement that clears their floors.

    starvation(m)  =  pi  +  (1 - pi) * B(a + m, b) / B(a, b)

`pi` is the asymptote -- *the share no pool depth reaches* -- and it is the number
`acceptance-bar.md` §11.1 step 1 actually needs, because step 1 spends search and
`pi` is what search cannot buy.

## Why the likelihood is the right one

Each Brief contributes what was observed, and censoring is the point:

  * served at position `f` (0-based) -- `f` declines then a serve:
        L = (1 - pi) * B(a+f, b+1) / B(a, b)
  * no serve in the `n` candidates its pool could offer -- **censored**, `n` being
    the pool's own depth when that is below `max_m`:
        L = pi + (1 - pi) * B(a+n, b) / B(a, b)

A Brief whose gated pool holds 3 members is not a Brief that survived best-of-32.
Dropping those would bias the curve optimistic; the censored term uses them at
their true depth, which is the whole reason a shallow sample can say anything
about a deep pool.

⚠️ **`pi` is identified by the DEPTH of the censored observations, so a pool that
truncates early identifies it weakly.** That is not hidden -- it is what the
bootstrap interval reports, and it is why the deep `rig` pool is fitted alongside
the shipped-gate `gated` one. Where the interval is wide, the honest reading is
that the sample cannot answer, not that the point estimate is small.

Run: python experiments/warp/best_of_m_fit.py [--pool=rig] [--boot=300]
"""

from __future__ import annotations

import json
import math
import random
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fit_warp import SEED                                        # noqa: E402
from absolute_area import OUT                                    # noqa: E402

BANDS = {"4-6": range(4, 7), "7-10": range(7, 11)}
PROD_MEDIAN = {"4-6": 86.6, "7-10": 58.7}
REPORT_M = (1, 2, 4, 8, 12, 16, 24, 32, 48, 59, 64, 87, 96, 128)


def logB(a, b):
    return math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)


def observations(briefs, max_m):
    """(kind, k) per Brief with a pool. 's' = served at position k, 'c' =
    censored after k candidates, k being the depth actually available."""
    obs = []
    for b in briefs:
        if b["empty_pool"]:
            continue
        if b["first_serve"] is not None:
            obs.append(("s", b["first_serve"]))
        else:
            obs.append(("c", min(len(b["outcomes"]), b["depth"], max_m)))
    return obs


def nll(pi, a, b, groups):
    """Grouped over distinct (kind, k): at most ~130 terms whatever the sample."""
    if a <= 0 or b <= 0 or pi < 0 or pi >= 1:
        return float("inf")
    base = logB(a, b)
    tot = 0.0
    for (kind, k), n in groups.items():
        if kind == "s":
            p = (1.0 - pi) * math.exp(logB(a + k, b + 1.0) - base)
        else:
            p = pi + (1.0 - pi) * math.exp(logB(a + k, b) - base)
        if p <= 0.0:
            return float("inf")
        tot -= n * math.log(p)
    return tot


def fit(obs, rounds=7, steps=13):
    """Coarse-to-fine over (pi, log a, log b). No scipy: the environment is
    pinned and a measurement is not a reason to move a pin."""
    groups = Counter(obs)
    plo, phi = 0.0, 0.9
    lo, hi = -5.0, 5.0
    best = (0.0, 1.0, 1.0, float("inf"))
    for _ in range(rounds):
        for ip in range(steps + 1):
            pi = plo + (phi - plo) * ip / steps
            for i in range(steps + 1):
                a = math.exp(lo + (hi - lo) * i / steps)
                for j in range(steps + 1):
                    b = math.exp(lo + (hi - lo) * j / steps)
                    v = nll(pi, a, b, groups)
                    if v < best[3]:
                        best = (pi, a, b, v)
        pspan = (phi - plo) / 4.0
        span = (hi - lo) / 4.0
        plo, phi = max(0.0, best[0] - pspan), min(0.9999, best[0] + pspan)
        ca, cb = math.log(best[1]), math.log(best[2])
        lo, hi = min(ca, cb) - span, max(ca, cb) + span
    return best


def starvation(pi, a, b, m):
    return pi + (1.0 - pi) * math.exp(logB(a + m, b) - logB(a, b))


def empirical(briefs, m):
    live = [b for b in briefs if not b["empty_pool"]]
    if not live:
        return None
    st = sum(1 for b in live
             if not (b["first_serve"] is not None and b["first_serve"] < m))
    return st / len(live)


def truncated(briefs, m, max_m):
    """Briefs that never served AND ran out of pool before m -- the ones whose
    empirical value at this m is a censoring artefact rather than a result."""
    live = [b for b in briefs if not b["empty_pool"]]
    return sum(1 for b in live
               if b["first_serve"] is None and min(b["depth"], max_m) < m)


def analyse(briefs, max_m, boot, label, rng):
    obs = observations(briefs, max_m)
    pi, a, b, v = fit(obs)
    live = [x for x in briefs if not x["empty_pool"]]
    meas_to = min((min(x["depth"], max_m) for x in live), default=0)

    boots = []
    for _ in range(boot):
        res = [obs[rng.randrange(len(obs))] for _ in obs]
        boots.append(fit(res, rounds=5, steps=11)[:3])
    pis = sorted(p for p, _, _ in boots)
    pi_lo = pis[int(0.025 * len(pis))] if pis else None
    pi_hi = pis[int(0.975 * len(pis)) - 1] if pis else None

    rows = []
    for m in REPORT_M:
        s = starvation(pi, a, b, m)
        vals = sorted(starvation(*bb, m) for bb in boots) if boots else []
        lo = vals[int(0.025 * len(vals))] if vals else None
        hi = vals[int(0.975 * len(vals)) - 1] if vals else None
        emp = empirical(briefs, m)
        rows.append({"m": m, "fitted": round(s, 5),
                     "ci95": [round(lo, 5), round(hi, 5)] if vals else None,
                     "empirical": round(emp, 5) if emp is not None else None,
                     "empirical_truncated": truncated(briefs, m, max_m),
                     "measured": m <= meas_to})

    print("\n=== %s ===" % label)
    print("pi %.4f  CI95 [%.4f, %.4f]   Beta(a=%.3f, b=%.3f)  mean p %.4f  "
          "nll %.2f  briefs %d" % (pi, pi_lo or 0, pi_hi or 0, a, b,
                                   a / (a + b), v, len(obs)))
    print("pi is the ASYMPTOTE: the share of Briefs no pool depth serves.")
    print("'trunc' counts Briefs whose empirical value at that m is a censoring")
    print("artefact -- they never served and ran out of pool before m.\n")
    print("   m   fitted    95%% CI              empirical  trunc  measured")
    for r in rows:
        ci = ("[%.4f, %.4f]" % tuple(r["ci95"])) if r["ci95"] else "-"
        print("%4d  %7.4f  %-20s %9s  %5d  %s"
              % (r["m"], r["fitted"], ci,
                 ("%.4f" % r["empirical"]) if r["empirical"] is not None else "-",
                 r["empirical_truncated"],
                 "yes" if r["measured"] else "EXTRAPOLATED"))
    return {"pi": round(pi, 5), "pi_ci95": [round(pi_lo, 5), round(pi_hi, 5)],
            "beta_a": round(a, 5), "beta_b": round(b, 5),
            "mean_decline_p": round(a / (a + b), 5),
            "nll": round(v, 3), "briefs": len(obs),
            "measured_to_m": meas_to, "bootstrap": boot, "curve": rows}


def main():
    pool, boot = "rig", 300
    for a in sys.argv[1:]:
        if a.startswith("--pool="):
            pool = a.split("=", 1)[1]
        if a.startswith("--boot="):
            boot = int(a.split("=", 1)[1])

    briefs = json.load(open(OUT / ("best_of_m_briefs_%s.json" % pool)))
    meta = json.load(open(OUT / "best_of_m.json")).get("_meta", {})
    max_m = meta.get("max_m", 32)
    print("pool definition: %s | %d Briefs | max_m %d" % (pool, len(briefs), max_m))

    rng = random.Random(SEED)
    out = {"all": analyse(briefs, max_m, boot, "%s, all Briefs" % pool, rng)}
    for name, rr in BANDS.items():
        sel = [b for b in briefs if b["n"] in rr]
        if len(sel) < 20:
            continue
        res = analyse(sel, max_m, boot, "%s, %s rooms (production pool %.1f)"
                      % (pool, name, PROD_MEDIAN[name]), rng)
        res["prod_median_pool"] = PROD_MEDIAN[name]
        pm = int(round(PROD_MEDIAN[name]))
        res["at_production_depth"] = {
            "m": pm,
            "fitted": round(starvation(res["pi"], res["beta_a"],
                                       res["beta_b"], pm), 5)}
        out[name] = res

    OUT.mkdir(exist_ok=True)
    json.dump({"pool": pool, **out},
              open(OUT / ("best_of_m_fit_%s.json" % pool), "w"), indent=1)
    print("\nwrote %s" % (OUT / ("best_of_m_fit_%s.json" % pool)))


if __name__ == "__main__":
    main()
