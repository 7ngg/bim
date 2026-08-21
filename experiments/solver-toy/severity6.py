"""Ticket 24 — not all confident-wrong relations are equally wrong.

Suite A3 measured that a **same-axis reversal** is fatal at every dose tested,
while a **cross-axis swap** at the same dose often is not. If that holds on
realistic noise it is a redefinition, not a footnote: `docs/spec/proposer.md` 5.2
counts confident-wrong as one number, and one of its two kinds barely costs
anything.

For each asserted relation, against the truth's own argmin for that pair:

  agree     same axis, same direction
  reversal  same axis, opposite direction   -- the truth puts them the other way
  swap      the other axis                  -- the truth separates them on x, we
                                               asserted y (or the reverse)

Crossed with whether the truth actually *violates* the assertion, since a swap
on a diagonal pair is satisfied by the truth and costs nothing at all.

Also scores severity: a violated relation carries `sep_cost` against the truth,
the overlap the assertion demands be closed. A relation violated by one grid unit
and one violated by ten are the same number in 5.2 and are not the same defect.

    python severity6.py
"""

from __future__ import annotations

import json
import pathlib
from collections import defaultdict
from typing import Dict, List

import arrangement as A
import probe6
from scenarios import make_proposal, mm
from solver import extract_relations

RESULTS = pathlib.Path(__file__).parent / "results"


def classify(row: dict) -> dict:
    """Recompute one C/C2 row's relation set and break the errors down."""
    n, seed = row["n"], row["seed"]
    if row["suite"] == "C2":
        brief, truth, kinds = probe6.get(n, seed, probe6.SHIPPED["exposure"],
                                         probe6.SHIPPED["door_min"],
                                         probe6.T_INT)
        tau = row["tau"]
    else:
        brief, truth, kinds = probe6.get(n, seed)
        tau = probe6.TAU
    prop = make_proposal(truth, kinds, seed, sigma=mm(row["sigma"]))
    chosen, _abst, _cyc = extract_relations(prop.boxes, tau)
    truth_dir = A.argmin_directions(truth)

    out = {"agree": 0, "reversal": 0, "swap": 0,
           "reversal_violated": 0, "swap_violated": 0,
           "sev_sum": 0, "sev_max": 0}
    for rel in chosen:
        axis, a, b = rel
        t_axis, ta, tb = truth_dir[frozenset((a, b))]
        cost = A.sep_cost(truth, axis, a, b)
        if rel == (t_axis, ta, tb):
            out["agree"] += 1
            continue
        kind = "reversal" if axis == t_axis else "swap"
        out[kind] += 1
        if cost > 0:
            out[kind + "_violated"] += 1
            out["sev_sum"] += cost
            out["sev_max"] = max(out["sev_max"], cost)
    out["violated"] = out["reversal_violated"] + out["swap_violated"]
    return out


def confusion(rs: List[dict], key, name: str) -> None:
    tp = sum(1 for r in rs if key(r) == 0 and r.get("survivor"))
    fn = sum(1 for r in rs if key(r) == 0 and not r.get("survivor"))
    fp = sum(1 for r in rs if key(r) > 0 and r.get("survivor"))
    tn = sum(1 for r in rs if key(r) > 0 and not r.get("survivor"))
    acc = (tp + tn) / len(rs) if rs else 0
    print(f"  {name:<34} clean&survived {tp:>3}  clean&failed {fn:>3}  "
          f"dirty&survived {fp:>3}  dirty&failed {tn:>3}   acc {100*acc:5.1f}%")


def main() -> None:
    rows = [json.loads(l) for l in (RESULTS / "P6.jsonl").open(encoding="utf-8")
            if l.strip()]
    rs = [r for r in rows if r["suite"] in ("C", "C2")]
    for r in rs:
        r.update(classify(r))

    print("Realistic Proposals, broken down by KIND of disagreement")
    print("(mean per Proposal; `violated` = the truth contradicts the assertion)")
    print()
    print(f"{'rig':>4} {'n':>3} {'sigma':>6} {'tau':>4} {'runs':>5} {'asserted':>8} "
          f"{'reversal':>8} {'rev viol':>8} {'swap':>6} {'swap viol':>9} "
          f"{'sev sum':>8} {'survivor':>8}")
    by = defaultdict(list)
    for r in rs:
        by[(r["suite"], r["n"], r["sigma"], r.get("tau"))].append(r)
    for key in sorted(by, key=lambda t: (t[1], t[0], t[2],
                                         t[3] if t[3] is not None else -1)):
        g = by[key]
        m = lambda f: sum(f(r) for r in g) / len(g)
        sur = sum(1 for r in g if r.get("survivor")) / len(g)
        tau = key[3] if key[3] is not None else probe6.TAU
        print(f"{key[0]:>4} {key[1]:>3} {key[2]:>6} {tau:>4} {len(g):>5} "
              f"{m(lambda r: r['asserted']):>8.1f} "
              f"{m(lambda r: r['reversal']):>8.2f} "
              f"{m(lambda r: r['reversal_violated']):>8.2f} "
              f"{m(lambda r: r['swap']):>6.2f} "
              f"{m(lambda r: r['swap_violated']):>9.2f} "
              f"{m(lambda r: r['sev_sum']):>8.1f} "
              f"{100*sur:>7.1f}%")

    for scope, label in ((lambda r: True, "all sizes"),
                         (lambda r: r["n"] <= 12, "8 and 12 rooms (v1's band)"),
                         (lambda r: r["n"] == 24, "24 rooms (outside C13)")):
        g = [r for r in rs if scope(r)]
        print()
        print(f"Which definition calls the outcome?  [{label}, n={len(g)}]")
        confusion(g, lambda r: r["reversal"] + r["swap"],
                  "argmin-wrong (5.1 literal)")
        confusion(g, lambda r: r["violated"], "violated (either kind)")
        confusion(g, lambda r: r["reversal_violated"], "violated REVERSAL only")
        confusion(g, lambda r: r["reversal"], "reversal, violated or not")
        confusion(g, lambda r: r["swap_violated"], "violated SWAP only")
        confusion(g, lambda r: r["sev_sum"], "severity sum > 0")
        for thr in (2, 4, 8, 16):
            confusion(g, lambda r, t=thr: max(0, r["sev_sum"] - (t - 1)),
                      f"severity sum >= {thr} grid units")


if __name__ == "__main__":
    main()
