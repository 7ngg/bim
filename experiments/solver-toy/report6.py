"""Ticket 24 -- read `results/P6.jsonl` and print the tables the answer is made of.

    python report6.py                 # everything
    python report6.py A C             # a subset
"""

from __future__ import annotations

import json
import pathlib
import statistics
import sys
from collections import defaultdict
from typing import Dict, List

RESULTS = pathlib.Path(__file__).parent / "results"


def load(name: str = "P6.jsonl") -> List[dict]:
    p = RESULTS / name
    if not p.exists():
        sys.exit(f"no {p} -- run probe6.py first")
    return [json.loads(l) for l in p.open(encoding="utf-8") if l.strip()]


def pct(x: float) -> str:
    return f"{100*x:5.1f}%"


def med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def fmt(x, w=6, d=2):
    return " " * w + "-" if x is None else f"{x:>{w}.{d}f}"


def rule(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


# ---------------------------------------------------------------------------


def table_A(rows, suite="A", label="A -- dose-response, guarded"):
    rs = [r for r in rows if r["suite"] == suite]
    if not rs:
        return
    rule(f"{label}   (Proposal = ground truth; only the relation set is corrupted)")
    print(f"{'n':>3} {'k':>3} {'base':>5} {'posted':>6} {'cycdrop':>7} "
          f"{'violated':>8} {'INFEAS':>7} {'survivor':>8} {'valid_at p50':>12} "
          f"{'wall p50':>9}")
    by = defaultdict(list)
    for r in rs:
        by[(r["n"], r["k"])].append(r)
    for (n, k) in sorted(by):
        g = by[(n, k)]
        inf = sum(1 for r in g if r["status"] == "INFEASIBLE") / len(g)
        sur = sum(1 for r in g if r.get("survivor")) / len(g)
        print(f"{n:>3} {k:>3} {g[0].get('base', 0):>5} "
              f"{sum(r['posted'] for r in g)/len(g):>6.1f} "
              f"{sum(r.get('cycle_drops', 0) for r in g)/len(g):>7.2f} "
              f"{sum(r['violated_posted'] for r in g)/len(g):>8.2f} "
              f"{pct(inf):>7} {pct(sur):>8} "
              f"{fmt(med([r['valid_at'] for r in g]), 12, 3)} "
              f"{fmt(med([r['wall'] for r in g]), 9, 3)}")


def table_dose(rows):
    """The headline: survival against the dose that actually reached the model."""
    rs = [r for r in rows if r["suite"] in ("A", "A3")]
    if not rs:
        return
    rule("THE HEADLINE -- survival against violated relations actually posted")
    print("A relation flipped to a direction the truth still happens to satisfy "
          "is not\na violated relation. `violated` counts only the ones the "
          "truth contradicts.")
    print()
    print(f"{'n':>3} {'violated':>8} {'runs':>5} {'INFEAS':>7} {'survivor':>8} "
          f"{'valid_at p50':>12}")
    by = defaultdict(list)
    for r in rs:
        by[(r["n"], r["violated_posted"])].append(r)
    for (n, v) in sorted(by):
        g = by[(n, v)]
        inf = sum(1 for r in g if r["status"] == "INFEASIBLE") / len(g)
        sur = sum(1 for r in g if r.get("survivor")) / len(g)
        print(f"{n:>3} {v:>8} {len(g):>5} {pct(inf):>7} {pct(sur):>8} "
              f"{fmt(med([r['valid_at'] for r in g]), 12, 3)}")

    rule("The same, pooled over sizes -- is one violated relation already fatal?")
    by2 = defaultdict(list)
    for r in rs:
        by2[min(r["violated_posted"], 6)].append(r)
    print(f"{'violated':>8} {'runs':>5} {'INFEAS':>7} {'survivor':>8}")
    for v in sorted(by2):
        g = by2[v]
        lbl = f"{v}" if v < 6 else ">=6"
        inf = sum(1 for r in g if r["status"] == "INFEASIBLE") / len(g)
        sur = sum(1 for r in g if r.get("survivor")) / len(g)
        print(f"{lbl:>8} {len(g):>5} {pct(inf):>7} {pct(sur):>8}")


def table_B(rows):
    rs = [r for r in rows if r["suite"] == "B"]
    if not rs:
        return
    rule("B -- abstain. Dropping relations, not flipping them")
    print("f = 1.0 is every relation dropped: the unamended C10 form ticket 4 "
          "refuted.")
    print()
    print(f"{'n':>3} {'drop f':>7} {'posted':>6} {'INFEAS':>7} {'survivor':>8} "
          f"{'valid_at p50':>12} {'first p50':>10} {'wall p50':>9}")
    by = defaultdict(list)
    for r in rs:
        by[(r["n"], r["mode"])].append(r)
    for (n, mode) in sorted(by, key=lambda t: (t[0], float(t[1][4:]))):
        g = by[(n, mode)]
        inf = sum(1 for r in g if r["status"] == "INFEASIBLE") / len(g)
        sur = sum(1 for r in g if r.get("survivor")) / len(g)
        print(f"{n:>3} {mode[4:]:>7} {sum(r['posted'] for r in g)/len(g):>6.1f} "
              f"{pct(inf):>7} {pct(sur):>8} "
              f"{fmt(med([r['valid_at'] for r in g]), 12, 3)} "
              f"{fmt(med([r['first'] for r in g]), 10, 3)} "
              f"{fmt(med([r['wall'] for r in g]), 9, 3)}")


def table_C(rows):
    rs = [r for r in rows if r["suite"] == "C"]
    if not rs:
        return
    rule("C -- realistic noise, shipped configuration, no injection")
    print(f"{'n':>3} {'sigma':>6} {'asserted':>8} {'abstain%':>8} {'cyclic':>6} "
          f"{'argwrong%':>9} {'viol%':>6} {'violN':>6} {'INFEAS':>7} "
          f"{'survivor':>8} {'valid_at p50':>12}")
    by = defaultdict(list)
    for r in rs:
        by[(r["n"], r["sigma"])].append(r)
    for (n, s) in sorted(by):
        g = by[(n, s)]
        inf = sum(1 for r in g if r["status"] == "INFEASIBLE") / len(g)
        sur = sum(1 for r in g if r.get("survivor")) / len(g)
        print(f"{n:>3} {s:>6} {sum(r['asserted'] for r in g)/len(g):>8.1f} "
              f"{100*sum(r['abstain_rate'] for r in g)/len(g):>8.2f} "
              f"{sum(r['cyclic'] for r in g)/len(g):>6.2f} "
              f"{100*sum(r['argmin_wrong_rate'] for r in g)/len(g):>9.2f} "
              f"{100*sum(r['violated_rate'] for r in g)/len(g):>6.2f} "
              f"{sum(r['violated'] for r in g)/len(g):>6.2f} "
              f"{pct(inf):>7} {pct(sur):>8} "
              f"{fmt(med([r['valid_at'] for r in g]), 12, 3)}")

    rule("C -- which number separates a survivor from a failure?")
    print("Group means over every C run, split by outcome. A metric that "
          "predicts\nshows a gap here; one that does not, does not.")
    print()
    surv = [r for r in rs if r.get("survivor")]
    fail = [r for r in rs if not r.get("survivor")]
    print(f"{'metric':>22} {'survivors':>10} {'failures':>10} {'ratio':>8}")
    for key, name in (("agreement", "agreement"),
                      ("abstain_rate", "abstain rate"),
                      ("argmin_wrong_rate", "argmin-wrong rate"),
                      ("violated_rate", "violated rate"),
                      ("violated", "violated (count)"),
                      ("cyclic", "cyclic (count)")):
        a = sum(r[key] for r in surv) / len(surv) if surv else 0
        b = sum(r[key] for r in fail) / len(fail) if fail else 0
        ratio = (b / a) if a else float("inf") if b else 0.0
        print(f"{name:>22} {a:>10.4f} {b:>10.4f} "
              f"{'inf' if ratio == float('inf') else f'{ratio:>8.2f}'}")

    rule("C -- separation, run by run: does violated == 0 ever fail, and does "
         "violated > 0 ever survive?")
    print(f"{'n':>3} {'violated':>8} {'runs':>5} {'survivor':>8}")
    by = defaultdict(list)
    for r in rs:
        by[(r["n"], min(r["violated"], 8))].append(r)
    for (n, v) in sorted(by):
        g = by[(n, v)]
        sur = sum(1 for r in g if r.get("survivor")) / len(g)
        print(f"{n:>3} {v:>8} {len(g):>5} {pct(sur):>8}")


def table_E(rows):
    rs = [r for r in rows if r["suite"] == "E"]
    if not rs:
        return
    rule("E -- cause, not correlation")
    print("sufficient : post ONLY the flipped relations. INFEASIBLE means they "
          "alone explain it.\n"
          "necessary  : post everything EXCEPT the flipped ones, which is what "
          "abstaining\n"
          "             on those pairs would have done. A survivor means the "
          "flips are what\n"
          "             killed it.\n"
          "Sufficiency is only readable at 8 and 12 rooms: with almost no "
          "relations posted\n"
          "the 24-room model is the unamended C10 form, which ticket 4 showed "
          "finds nothing.")
    print()
    print(f"{'n':>3} {'k':>3} {'viol':>5} {'full':>11} {'suff':>11} "
          f"{'nec':>11} {'nec survivor':>12} {'core=posted':>11}")
    for r in sorted(rs, key=lambda r: (r["n"], r["k"], r["seed"])):
        print(f"{r['n']:>3} {r['k']:>3} {r['violated_posted']:>5} "
              f"{r['status']:>11} {r['suff_status']:>11} {r['nec_status']:>11} "
              f"{str(r['nec_valid_at'] is not None):>12} "
              f"{str(r['core_size'] == r['posted']):>11}")

    rule("E -- summary")
    tot = [r for r in rs if r["violated_posted"] > 0]
    if tot:
        infe = [r for r in tot if r["status"] == "INFEASIBLE"]
        print(f"runs with >=1 violated relation posted : {len(tot)}")
        print(f"  of which the full set is INFEASIBLE  : {len(infe)} "
              f"({100*len(infe)/len(tot):.0f}%)")
        if infe:
            nec = sum(1 for r in infe if r["nec_valid_at"] is not None)
            print(f"  deleting just the flips restores a survivor : {nec}/{len(infe)}"
                  f" ({100*nec/len(infe):.0f}%)")
            s12 = [r for r in infe if r["n"] in (8, 12)]
            if s12:
                suf = sum(1 for r in s12 if r["suff_status"] == "INFEASIBLE")
                print(f"  flips alone are INFEASIBLE (8 and 12 rooms) : "
                      f"{suf}/{len(s12)} ({100*suf/len(s12):.0f}%)")
        core_all = sum(1 for r in rs if r["core_size"] == r["posted"])
        print(f"CP-SAT's assumption core is the ENTIRE posted set in "
              f"{core_all}/{len(rs)} runs -- it discriminates nothing.")


def table_A3(rows):
    rs = [r for r in rows if r["suite"] == "A3"]
    if not rs:
        return
    rule("A3 -- does the kind of wrongness matter?")
    print(f"{'n':>3} {'mode':>8} {'k':>3} {'violated':>8} {'INFEAS':>7} "
          f"{'survivor':>8}")
    by = defaultdict(list)
    for r in rs:
        by[(r["n"], r["mode"], r["k"])].append(r)
    for key in sorted(by):
        g = by[key]
        n, mode, k = key
        inf = sum(1 for r in g if r["status"] == "INFEASIBLE") / len(g)
        sur = sum(1 for r in g if r.get("survivor")) / len(g)
        print(f"{n:>3} {mode:>8} {k:>3} "
              f"{sum(r['violated_posted'] for r in g)/len(g):>8.2f} "
              f"{pct(inf):>7} {pct(sur):>8}")


def table_A2(rows):
    a = {(r["n"], r["seed"], r["k"]): r for r in rows if r["suite"] == "A"}
    rs = [r for r in rows if r["suite"] == "A2"]
    if not rs:
        return
    rule("A2 -- what the acyclicity guard is worth")
    print("Same flips, guard off, so the posted set may contain a directed "
          "cycle.\nThe shipping extractor cannot produce one; this is the "
          "counterfactual.")
    print()
    print(f"{'n':>3} {'k':>3} {'guarded INFEAS':>15} {'unguarded INFEAS':>17} "
          f"{'guarded surv':>13} {'unguarded surv':>15}")
    by = defaultdict(list)
    for r in rs:
        by[(r["n"], r["k"])].append(r)
    for (n, k) in sorted(by):
        u = by[(n, k)]
        g = [a[(n, r["seed"], k)] for r in u if (n, r["seed"], k) in a]
        if not g:
            continue
        f = lambda xs, p: pct(sum(1 for r in xs if p(r)) / len(xs))
        print(f"{n:>3} {k:>3} "
              f"{f(g, lambda r: r['status'] == 'INFEASIBLE'):>15} "
              f"{f(u, lambda r: r['status'] == 'INFEASIBLE'):>17} "
              f"{f(g, lambda r: r.get('survivor')):>13} "
              f"{f(u, lambda r: r.get('survivor')):>15}")


def table_D(rows):
    rs = [r for r in rows if r["suite"] == "D" and r["status"] != "SKIP"]
    if not rs:
        return
    rule("D -- a directed cycle, posted unguarded")
    print(f"{'n':>3} {'cycle len':>9} {'runs':>5} {'INFEAS':>7} {'wall p50':>9}")
    by = defaultdict(list)
    for r in rs:
        by[(r["n"], r["cyclen"])].append(r)
    for key in sorted(by):
        g = by[key]
        inf = sum(1 for r in g if r["status"] == "INFEASIBLE") / len(g)
        print(f"{key[0]:>3} {key[1]:>9} {len(g):>5} {pct(inf):>7} "
              f"{fmt(med([r['wall'] for r in g]), 9, 3)}")


def table_predict(rows):
    """The whole ticket in one table.

    If confident-wrong predicts, then a Proposal with zero violated relations
    survives and one with any fails. That is a 2x2, and its off-diagonal is the
    metric's error rate. Run for both readings of 5.1, because they disagree and
    only one of them can be the published definition.
    """
    rs = [r for r in rows if r["suite"] in ("C", "C2")]
    if not rs:
        return
    rule("PREDICTION -- does the metric call the outcome, run by run?")
    for key, name in (("violated", "violated (asserted and FALSE of the truth)"),
                      ("argmin_wrong", "argmin-wrong (5.1 read literally)"),
                      ("abstained", "abstained")):
        for scope, label in ((None, "all sizes"), (24, "24 rooms only")):
            g = rs if scope is None else [r for r in rs if r["n"] == scope]
            tp = sum(1 for r in g if r[key] == 0 and r.get("survivor"))
            fn = sum(1 for r in g if r[key] == 0 and not r.get("survivor"))
            fp = sum(1 for r in g if r[key] > 0 and r.get("survivor"))
            tn = sum(1 for r in g if r[key] > 0 and not r.get("survivor"))
            acc = (tp + tn) / len(g) if g else 0
            print()
            print(f"  {name}  [{label}, n={len(g)}]")
            print(f"    {'':>14} {'survivor':>10} {'no survivor':>12}")
            print(f"    {key+' == 0':>14} {tp:>10} {fn:>12}")
            print(f"    {key+' >  0':>14} {fp:>10} {tn:>12}")
            print(f"    accuracy {pct(acc)}   "
                  f"false-alarm {fp}/{fp+tn if fp+tn else 1}  "
                  f"missed {fn}/{tp+fn if tp+fn else 1}")

    rule("PREDICTION -- a rate compounds. What a 'small' rate costs at 24 rooms")
    print("A per-pair rate p over m asserted pairs leaves a Proposal clean with")
    print("probability (1-p)^m. m is quadratic in rooms, so the same rate is a")
    print("different product at 8 rooms and at 24.")
    print()
    print(f"{'per-pair rate':>14} " + " ".join(f"{n:>10}" for n in (8, 12, 24)))
    ms = {}
    for n in (8, 12, 24):
        g = [r for r in rs if r["n"] == n]
        ms[n] = sum(r["asserted"] for r in g) / len(g) if g else 0
    print(f"{'asserted m':>14} " + " ".join(f"{ms[n]:>10.0f}" for n in (8, 12, 24)))
    for p_ in (0.001, 0.002, 0.005, 0.01, 0.02, 0.05):
        cells = " ".join(f"{pct((1-p_)**ms[n]):>10}" for n in (8, 12, 24))
        print(f"{p_:>14.3f} {cells}   <- P(clean Proposal)")


def table_F(rows):
    rs = [r for r in rows if r["suite"] == "F"]
    a = [r for r in rows if r["suite"] == "A"]
    if not rs:
        return
    rule("F -- the interaction: does abstaining more buy a wrong relation back?")
    print("Suite E showed a flipped relation is rarely infeasible alone. If it")
    print("is only fatal in company, loosening the company should rescue it.")
    print()
    print(f"{'n':>3} {'drop f':>7} {'k':>3} {'posted':>6} {'violated':>8} "
          f"{'INFEAS':>7} {'survivor':>8} {'A survivor at same k':>21}")
    by = defaultdict(list)
    for r in rs:
        by[(r["n"], r["mode"], r["k"])].append(r)
    for key in sorted(by, key=lambda t: (t[0], t[1], t[2])):
        g = by[key]
        n, mode, k = key
        ag = [r for r in a if r["n"] == n and r["k"] == k]
        inf = sum(1 for r in g if r["status"] == "INFEASIBLE") / len(g)
        sur = sum(1 for r in g if r.get("survivor")) / len(g)
        asur = (pct(sum(1 for r in ag if r.get("survivor")) / len(ag))
                if ag else "-")
        print(f"{n:>3} {mode[4:]:>7} {k:>3} "
              f"{sum(r['posted'] for r in g)/len(g):>6.1f} "
              f"{sum(r['violated_posted'] for r in g)/len(g):>8.2f} "
              f"{pct(inf):>7} {pct(sur):>8} {asur:>21}")


TABLES = {"A": table_A, "dose": table_dose, "predict": table_predict,
          "B": table_B, "C": table_C, "E": table_E, "F": table_F,
          "A2": table_A2, "A3": table_A3, "D": table_D}


def main() -> None:
    rows = load()
    want = sys.argv[1:] or list(TABLES)
    print(f"{len(rows)} rows from results/P6.jsonl")
    for name in want:
        if name == "A":
            table_A(rows)
            table_A(rows, "A2", "A2 -- dose-response, UNGUARDED")
        elif name in TABLES:
            TABLES[name](rows)


if __name__ == "__main__":
    main()
