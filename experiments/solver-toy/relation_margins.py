"""Is a pinwheel's relation graph really denser — and are its margins tighter?

Ticket 29 asserts that "a pinwheel has a denser relation graph than a slicing
layout, so there is a specific reason to expect movement" in τ. That is a
measurable claim about a quantity the solver already computes, so it should be
measured rather than reasoned about.

τ (`SolveConfig.relation_confidence`) gates on the **margin**: per room pair,
the second-cheapest separation minus the cheapest, in grid units, computed by
`solver.rank_relations` over the **Proposal** — not the truth, because the
Proposal is what the solver sees. A pair whose margin is below τ abstains and is
never posted as a hard constraint. So "does τ = 4 still filter the right things"
is answered by where the margin distribution sits relative to 4.

No solve. Regenerates the sweep's own scenarios — deterministic in
(n, seed, exposure, truth arm) — and runs the solver's own extractor on them.

Run: python experiments/solver-toy/relation_margins.py
"""

from __future__ import annotations

import sys

from typing import Dict, List, Optional, Sequence

import scenarios
import sweep_ng
from solver import extract_relations, rank_relations

# The console here is cp1252 and these tables are read back as UTF-8; without
# this a single non-ASCII character lands in the saved output as a mojibake.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:                                      # noqa: BLE001
    pass

COUNTS = sweep_ng.COUNTS
EXPOSURES = ("detached", "corpus_median")
SEEDS = [sweep_ng.BASE_SEED + s for s in range(5)]
TAUS = (0, 1, 2, 4, 6, 10)


def q(xs: Sequence[float], p: float) -> Optional[float]:
    if not xs:
        return None
    s = sorted(xs)
    return s[min(len(s) - 1, max(0, int(round(p * (len(s) - 1)))))]


def collect(arm: str) -> Dict[str, list]:
    margins: List[int] = []
    costs: List[int] = []
    fixed_at: Dict[int, List[float]] = {t: [] for t in TAUS}
    scen = 0
    for n in COUNTS:
        for exposure in EXPOSURES:
            for seed in SEEDS:
                sc = sweep_ng.get_scenario(n, seed, exposure, arm,
                                           sweep_ng.DOOR_MIN_ADR, 0.5,
                                           sweep_ng.T_INT_PUBLISHED)
                if sc[0] != "ok":
                    continue
                scen += 1
                _, _brief, _truth, proposal, _, _ = sc
                ranked = rank_relations(proposal.boxes)
                margins += [m for _c, m, _a, _i, _j in ranked]
                costs += [c for c, _m, _a, _i, _j in ranked]
                pairs = len(ranked)
                for t in TAUS:
                    chosen, _ab, _cy = extract_relations(proposal.boxes, t)
                    fixed_at[t].append(len(chosen) / pairs if pairs else 0.0)
    return {"margins": margins, "costs": costs, "fixed_at": fixed_at,
            "scenarios": scen}


def main() -> None:
    data = {arm: collect(arm) for arm in ("guillotine", "pinwheel")}

    print("Separation margins over the Proposal, the quantity tau gates on.")
    print("Margin is second-cheapest minus cheapest separation, in grid units")
    print("(250 mm). A pair below tau abstains and is never posted hard.\n")
    print(f"{'arm':>12} {'scenarios':>10} {'pairs':>8} " +
          " ".join(f"{('p' + str(int(p * 100))):>7}"
                   for p in (0.10, 0.25, 0.50, 0.75, 0.90)) +
          f" {'mean':>7} {'share < 4':>10}")
    for arm, d in data.items():
        m = d["margins"]
        below = sum(1 for x in m if x < 4)
        print(f"{arm:>12} {d['scenarios']:>10} {len(m):>8} " +
              " ".join(f"{(q(m, p) or 0):>7.1f}"
                       for p in (0.10, 0.25, 0.50, 0.75, 0.90)) +
              f" {(sum(m) / len(m) if m else 0):>7.2f} "
              f"{(100 * below / len(m) if m else 0):>9.1f}%")

    print("\nSeparation cost - how far a pair must move to be pulled apart.")
    print(f"{'arm':>12} " + " ".join(f"{('p' + str(int(p * 100))):>7}"
                                     for p in (0.50, 0.90, 0.99)) + f" {'max':>7}")
    for arm, d in data.items():
        c = d["costs"]
        print(f"{arm:>12} " + " ".join(f"{(q(c, p) or 0):>7.1f}"
                                       for p in (0.50, 0.90, 0.99)) +
              f" {(max(c) if c else 0):>7.0f}")

    print("\nWhat share of pairs tau actually fixes, per arm.")
    print("If a pinwheel's margins were tighter, its curve would fall away")
    print("faster and tau = 4 would be doing a different job in the two arms.\n")
    print(f"{'tau':>5} " + " ".join(f"{a:>14}" for a in data) + f" {'ratio':>8}")
    for t in TAUS:
        vals = []
        for arm in data:
            f = data[arm]["fixed_at"][t]
            vals.append(sum(f) / len(f) if f else 0.0)
        ratio = (vals[1] / vals[0]) if vals[0] else float("nan")
        star = "   <- shipped" if t == 4 else ""
        print(f"{t:>5} " + " ".join(f"{v:>14.4f}" for v in vals) +
              f" {ratio:>8.3f}{star}")


if __name__ == "__main__":
    main()
