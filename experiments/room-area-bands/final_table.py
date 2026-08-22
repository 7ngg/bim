"""The recommended band, in one table, with everything it rests on.

Columns, and where each comes from:

  target      corpus median -- brief.md 9.2's ladder rung 2 for the silent types
  cap         corpus p99.5 -- the hard maximum, absolute, CH-provenanced
  k           cap / target -- the multiplier when the Brief states its own target
  +40 m2      per-room slope x 40: what 40 m2 more dwelling buys THIS room
  CV          dispersion, which fixes the soft weight
  soft_w      1 / CV, normalised to the tightest class: the resistance to growth

wc and bathroom come from fixture ground truth (wc_fixture_truth.py), never from
the 2.4 m2 threshold split, which is circular for exactly these two.

Run: python experiments/room-area-bands/final_table.py
"""
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
RECT_OUT = ROOT / "experiments" / "rectangularise" / "out"
OUT = Path(__file__).resolve().parent / "out"

BATH_SPLIT_M2 = 2.4
COLLAPSE = {"ROOM": "room*", "BEDROOM": "room*", "STUDIO": "room*",
            "bedroom": "room*"}


def classify(t, area):
    if t in ("BATHROOM", "bathroom"):
        return "wc" if area < BATH_SPLIT_M2 else "bathroom"
    return COLLAPSE.get(t, t.lower())


def load(p):
    d = json.load(open(p))
    out = []
    for r in d["recs"]:
        rooms = [(classify(t, a), a) for t, a in zip(r["types"], r["area"])]
        out.append({"rooms": rooms, "total": sum(a for _, a in rooms)})
    return out


def build(tag, dwellings, fixture):
    by_type = defaultdict(list)
    pts = defaultdict(list)
    for d in dwellings:
        for c, a in d["rooms"]:
            by_type[c].append(a)
            pts[c].append((d["total"], a))
    rows = {}
    for c in sorted(by_type, key=lambda k: -len(by_type[k])):
        a = np.asarray(by_type[c])
        if len(a) < 500:
            continue
        if fixture and c in ("wc", "bathroom"):
            src = fixture["wc_pan_only"] if c == "wc" else fixture["bathroom_fixture"]
            med, cap, n = src["p50"], src["p99.5"], (fixture["n_wc"] if c == "wc"
                                                     else fixture["n_bathroom"])
            prov = "fixture"
            # dispersion must come from the same population as the median
            cv = None
        else:
            med, cap, n, prov, cv = (float(np.median(a)),
                                     float(np.percentile(a, 99.5)), len(a),
                                     "polygon", float(a.std(ddof=1) / a.mean()))
        x = np.array([p for p, _ in pts[c]]); y = np.array([q for _, q in pts[c]])
        b, _ = np.polyfit(x, y, 1)
        r2 = 1 - ((y - (b * x + np.polyfit(x, y, 1)[1])) ** 2).sum() / \
             ((y - y.mean()) ** 2).sum()
        if cv is None:                      # robust CV for the fixture classes
            cv = float((np.percentile(a, 75) - np.percentile(a, 25)) /
                       (1.349 * np.median(a)))
        rows[c] = dict(n=n, target=med, cap=cap, k=cap / med, d40=40 * b,
                       r2=r2, cv=cv, prov=prov)
    tightest = min(r["cv"] for r in rows.values())
    for r in rows.values():
        r["soft_w"] = tightest / r["cv"] and (1 / r["cv"]) / (1 / tightest)
        r["soft_w"] = (1 / r["cv"]) / (1 / tightest)
    return rows


def main():
    fixture = json.load(open(OUT / "wc_fixture_truth.json"))
    lines = []

    def w(s=""):
        print(s)
        lines.append(s)

    for tag, p, fx in [("SWISS DWELLINGS", RECT_OUT / "swiss_rects.json", fixture),
                       ("RESPLAN", RECT_OUT / "resplan_rects.json", None)]:
        rows = build(tag, load(p), fx)
        w()
        w("=" * 98)
        w(f"{tag}    RECOMMENDED BAND")
        w("=" * 98)
        w("  %-12s %7s %8s %8s %6s | %9s %6s | %5s %7s %8s"
          % ("class", "n", "target", "cap99.5", "k", "+40 m2", "r2", "CV",
             "soft_w", "source"))
        for c, r in rows.items():
            w("  %-12s %7d %8.2f %8.2f %6.2f | %8.2f  %6.3f | %5.2f %7.2f %8s"
              % (c, r["n"], r["target"], r["cap"], r["k"], r["d40"], r["r2"],
                 r["cv"], r["soft_w"], r["prov"]))
        w()
        grow = [c for c, r in rows.items() if r["d40"] >= 2.0]
        fixed = [c for c, r in rows.items() if r["d40"] < 1.0]
        w("     GROWS with the dwelling (>= 2 m2 per 40 m2): " + ", ".join(grow))
        w("     FIXED  (< 1 m2 per 40 m2)                  : " + ", ".join(fixed))
        json.dump(rows, open(OUT / f"band_{tag.split()[0].lower()}.json", "w"), indent=1)

    (OUT / "final_table.txt").write_text("\n".join(lines), encoding="utf-8")
    print(f"\nwrote {OUT/'final_table.txt'}")


if __name__ == "__main__":
    main()
