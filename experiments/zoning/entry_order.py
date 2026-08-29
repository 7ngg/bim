"""Does an ordered entry sequence survive the corpus?  (ticket 43, item 3)

Ticket 43 item 1 lists three candidate readings of "entry -> hall -> living",
and only the third needs hop-count integers:

  R1  the entry Space's hop-1 neighbourhood contains no habitable Room
  R2  every habitable Room is at hop >= 2
  R3  a genuine total order over a named sequence

R1 and R2 are sets at hop <= 1, and hop <= 1 from a FIXED node is not a hop
count: "r is at hop >= 2" is exactly `door_{entry,r} == 0`, one literal the H6
machinery already reifies.  R3 is the only one that needs `d_r`.

Measured off `out/zoning.json` -- no new corpus pass.  `dist` there is BFS from
the located entry over `measure_swiss.contact_graph` (tau 0.30 m, door run
1.00 m), which is the SAME layer the solver reifies as `door_ij`
(solver-formulation.md line 400: "true exactly when the two rooms share a wall
segment at least a door's width long").  So a rule that fails here fails on the
plane it would actually be posted on.

Otaq per CONTEXT.md l.394: bedrooms and living rooms, never a kitchen.
Habitable is wider and includes the kitchen-diner, so both are reported.
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

OUT = Path(__file__).resolve().parent / "out"

OTAQ = {"private", "social"}
HABITABLE = {"private", "social", "kitchen"}


def load():
    return json.load(open(OUT / "zoning.json"))["recs"]


def _min_dist(rec, classes):
    ds = [d for d, k in zip(rec["dist"], rec["classes"]) if k in classes]
    return min(ds) if ds else None


def rules(rec):
    d, K = rec["dist"], rec["classes"]
    hop1 = {K[i] for i in range(rec["n"]) if d[i] == 1}
    hop01 = {K[i] for i in range(rec["n"]) if d[i] <= 1}
    ec = rec["entry_class"]

    md_soc = _min_dist(rec, {"social"})
    md_pri = _min_dist(rec, {"private"})
    md_cir = _min_dist(rec, {"circ"})

    r = {
        # already shipped: one predicate about one Space (ticket 30)
        "R0  entry Space is circulation": ec == "circ",

        # hop-1 sets -- one existing literal each, no new integers
        "R1  no otaq at hop 1": not (hop1 & OTAQ),
        "R1h no habitable at hop 1": not (hop1 & HABITABLE),
        "R2  every otaq at hop >= 2": not (hop01 & OTAQ),
        "R2h every habitable at hop >= 2": not (hop01 & HABITABLE),
        "R5  every private room at hop >= 2": not (hop01 & {"private"}),

        # genuine orders -- these are the ones that need d_r
        "R3  circulation strictly nearer than any social room":
            (md_cir is not None and md_soc is not None and md_cir < md_soc),
        "R4  nearest private no nearer than nearest social":
            (md_pri is not None and md_soc is not None and md_pri >= md_soc),
        "R6  strict entry < social < private":
            (md_cir is not None and md_soc is not None and md_pri is not None
             and md_cir < md_soc < md_pri),
    }
    return r


def main():
    recs = load()
    names = list(rules(recs[0]).keys())
    hits = Counter()
    by_n = defaultdict(Counter)
    n_by = Counter()
    # applicability: R3/R4/R6 need both sets present
    appl = Counter()

    for rec in recs:
        r = rules(rec)
        n = rec["n"]
        n_by[n] += 1
        for k, v in r.items():
            if v:
                hits[k] += 1
                by_n[n][k] += 1
        for k in ("R3  circulation strictly nearer than any social room",
                  "R4  nearest private no nearer than nearest social",
                  "R6  strict entry < social < private"):
            need = {"R3": ({"circ"}, {"social"}),
                    "R4": ({"private"}, {"social"}),
                    "R6": ({"circ"}, {"social"})}[k[:2]]
            ok = all(_min_dist(rec, s) is not None for s in need)
            if k.startswith("R6"):
                ok = ok and _min_dist(rec, {"private"}) is not None
            if ok:
                appl[k] += 1

    tot = len(recs)
    print("dwellings: {}".format(tot))
    print()
    print("{:<52} {:>7} {:>8}  {}".format("rule", "holds", "%", "breaks 1 in"))
    print("-" * 84)
    for k in names:
        h = hits[k]
        pct = 100.0 * h / tot
        brk = tot - h
        one_in = ("never" if brk == 0 else "{:.1f}".format(tot / brk))
        print("{:<52} {:>7} {:>7.1f}%  {}".format(k, h, pct, one_in))

    print()
    print("applicable population for the ordering rules (both sets present):")
    for k in sorted(appl):
        a = appl[k]
        print("  {:<50} {:>5} dwellings ({:.1f}%)".format(k, a, 100.0 * a / tot))
        # conditional rate, on the population where the question arises
    print()
    print("conditional rate on the applicable population:")
    for rec_name, key in (("R3", "R3  circulation strictly nearer than any social room"),
                          ("R4", "R4  nearest private no nearer than nearest social"),
                          ("R6", "R6  strict entry < social < private")):
        a = appl[key]
        if a:
            print("  {:<50} {:>7.1f}%".format(key, 100.0 * hits[key] / a))

    print()
    print("by engine room count (% of dwellings the rule holds on):")
    hdr = "{:>4} {:>6}".format("n", "dwell")
    keys_short = [k for k in names]
    for k in keys_short:
        hdr += " {:>7}".format(k[:2])
    print(hdr)
    for n in sorted(n_by):
        row = "{:>4} {:>6}".format(n, n_by[n])
        for k in keys_short:
            row += " {:>6.1f}%".format(100.0 * by_n[n][k] / n_by[n])
        print(row)


if __name__ == "__main__":
    main()
