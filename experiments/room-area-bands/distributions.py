"""Per-room-type area distributions over the converted corpus.

Ticket 37, *What a room's area is allowed to be*. Every area predicate in
`data/acceptance/rules.json` is a floor or a total, so a 40 m2 WC passes the bar
and `model.no_unassigned_area` makes the surplus compulsory. This measures what
real dwellings actually do, so the upper bound is fitted rather than invented.

Reads the committed conversions from *Rectangularising real rooms*:

  out/swiss_rects.json    42,986 in-band (4-10 room) Swiss dwellings
  out/resplan_rects.json  16,617 in-band ResPlan plans, scaled to metres

Both corpora are reported separately and never pooled (*Cross-dataset
unification*).

Two already-decided rules are applied and nothing else, because the corpus-to-
ergonomic vocabulary mapping is ticket 31's and must not be built here:

  - {ROOM, BEDROOM, STUDIO} collapse to one class (*What the model proposes*).
  - BATHROOM splits at 2.4 m2 into wc / bathroom, the fixture-fitted threshold
    in `ergonomic.corpus_label_split`.

Run: python experiments/room-area-bands/distributions.py
"""
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
RECT_OUT = ROOT / "experiments" / "rectangularise" / "out"
OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(parents=True, exist_ok=True)

# ergonomic.corpus_label_split, fitted over 66,386 fixture-labelled rooms.
BATH_SPLIT_M2 = 2.4

# *What the model proposes*: one class, so every coverage figure measured
# before the collapse was pessimistic.
COLLAPSE = {"ROOM": "room*", "BEDROOM": "room*", "STUDIO": "room*",
            "bedroom": "room*"}

PCTS = [5, 25, 50, 75, 90, 95, 99]


def classify(t, area):
    """Corpus label -> reporting class. Two decided rules, no new mapping."""
    if t in ("BATHROOM", "bathroom"):
        return "wc" if area < BATH_SPLIT_M2 else "bathroom"
    return COLLAPSE.get(t, t.lower())


def load(path):
    """-> list of dwellings, each a list of (class, area_m2), plus the total."""
    d = json.load(open(path))
    out = []
    for r in d["recs"]:
        rooms = [(classify(t, a), a) for t, a in zip(r["types"], r["area"])]
        out.append((rooms, sum(a for _, a in rooms)))
    return out


def summarise(xs):
    a = np.asarray(xs, dtype=float)
    q = np.percentile(a, PCTS)
    return dict(n=len(a), mean=a.mean(), sd=a.std(ddof=1) if len(a) > 1 else 0.0,
                cv=(a.std(ddof=1) / a.mean()) if len(a) > 1 and a.mean() else 0.0,
                **{f"p{p}": v for p, v in zip(PCTS, q)})


def row(name, s):
    return ("  %-12s %6d  %6.2f %6.2f %6.2f %6.2f %6.2f %6.2f %6.2f   %5.2f"
            % (name, s["n"], s["p5"], s["p25"], s["p50"], s["p75"],
               s["p90"], s["p95"], s["p99"], s["cv"]))


HEAD = ("  %-12s %6s  %6s %6s %6s %6s %6s %6s %6s   %5s"
        % ("class", "n", "p5", "p25", "p50", "p75", "p90", "p95", "p99", "CV"))


def report(tag, dwellings, fh):
    def w(s=""):
        print(s)
        fh.write(s + "\n")

    by_type = defaultdict(list)          # absolute m2
    by_frac = defaultdict(list)          # share of dwelling total
    by_dw = defaultdict(list)            # (dwelling_total, area) for slopes
    totals = []

    for rooms, tot in dwellings:
        totals.append(tot)
        agg = defaultdict(float)
        for c, a in rooms:
            by_type[c].append(a)
            by_frac[c].append(a / tot if tot else 0.0)
            agg[c] += a
        for c, a in agg.items():
            by_dw[c].append((tot, a))

    w()
    w("=" * 96)
    w(f"{tag}   {len(dwellings)} dwellings, {sum(len(r) for r, _ in dwellings)} rooms")
    w("=" * 96)
    w()
    w(f"dwelling total area m2: {summarise(totals)['p50']:.1f} median, "
      f"{summarise(totals)['p5']:.1f}-{summarise(totals)['p95']:.1f} p5-p95")
    w()
    w("(1) ABSOLUTE AREA, m2")
    w(HEAD)
    order = sorted(by_type, key=lambda c: -len(by_type[c]))
    for c in order:
        w(row(c, summarise(by_type[c])))
    w()
    w("(2) AREA AS FRACTION OF DWELLING TOTAL")
    w(HEAD)
    for c in order:
        w(row(c, summarise(by_frac[c])))
    w()
    w("(3) MARGINAL ALLOCATION -- where an extra m2 of dwelling goes")
    w("     slope = d(type total in dwelling) / d(dwelling total), OLS")
    w("     resid_cv = spread of the type's area that dwelling size does NOT explain")
    w("  %-12s %6s  %7s %8s %8s   %8s %8s"
      % ("class", "n_dw", "slope", "intercept", "r2", "resid_sd", "resid_cv"))
    slopes = {}
    for c in order:
        pts = by_dw[c]
        if len(pts) < 30:
            continue
        x = np.array([p for p, _ in pts]); y = np.array([q for _, q in pts])
        b, a0 = np.polyfit(x, y, 1)
        pred = b * x + a0
        resid = y - pred
        ss = 1 - (resid ** 2).sum() / ((y - y.mean()) ** 2).sum()
        slopes[c] = b
        w("  %-12s %6d  %7.3f %8.2f %8.3f   %8.2f %8.2f"
          % (c, len(pts), b, a0, ss, resid.std(ddof=1),
             resid.std(ddof=1) / y.mean()))
    w()
    w("     slopes sum to %.3f (should be ~1.00: every m2 lands somewhere)"
      % sum(slopes.values()))
    return by_type, by_frac, by_dw, totals


def main():
    with open(OUT / "distributions.txt", "w", encoding="utf-8") as fh:
        res = {}
        for tag, p in [("SWISS DWELLINGS", RECT_OUT / "swiss_rects.json"),
                       ("RESPLAN", RECT_OUT / "resplan_rects.json")]:
            res[tag] = report(tag, load(p), fh)
        # dump the raw per-class arrays for the band fit
        dump = {}
        for tag, (by_type, by_frac, _, totals) in res.items():
            dump[tag] = {"abs": {k: v for k, v in by_type.items()},
                         "frac": {k: v for k, v in by_frac.items()},
                         "totals": totals}
        json.dump(dump, open(OUT / "areas.json", "w"))
    print(f"\nwrote {OUT/'distributions.txt'} and {OUT/'areas.json'}")


if __name__ == "__main__":
    main()
