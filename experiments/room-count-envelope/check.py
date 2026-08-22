"""Assert the numbers ADR 0013 quotes are the numbers the scripts produce.

The band itself lives in no data file yet -- `room-constraints.json` has three
open claimants, so this ticket could not write the `habitable` flag or the bounds
(they went to *Two room vocabularies in one file* and *What the engine says when
the Envelope is bigger than the programme*). Until they land, this is the only
thing standing between ADR 0013's table and quiet drift.
"""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
cov = {int(k): v for k, v in json.load(open(HERE / "coverage_per_n.json")).items()}

# ADR 0013, "Where the edges sit, and why not at round numbers"
QUOTED = {1: 10.8, 2: 42.6, 3: 24.2, 4: 17.2, 5: 8.3, 6: 7.9,
          7: 9.3, 8: 9.1, 9: 15.7, 10: 28.5, 11: 58.0}
GATE_LO, GATE_HI = 3, 10

fails = []
def check(ok, msg):
    print(("[PASS] " if ok else "[FAIL] ") + msg)
    if not ok:
        fails.append(msg)

for n, pct in QUOTED.items():
    check(abs(cov[n]["zero_pct"] - pct) < 0.05,
          f"n={n:<2} retrieval blank {cov[n]['zero_pct']}% == ADR 0013's {pct}%")

# The two claims the edges rest on, stated as relations rather than constants --
# these are what a re-measure on different data would have to preserve.
check(cov[2]["zero_pct"] > max(cov[n]["zero_pct"] for n in range(3, 11)),
      "n=2 is the worst regime below 11 -- why the floor is not 2")
check(cov[1]["zero_pct"] < cov[4]["zero_pct"],
      "n=1 retrieves better than n=4 -- why excluding studios was never a coverage argument")
check(cov[GATE_HI + 1]["zero_pct"] > 2 * cov[GATE_HI]["zero_pct"],
      f"retrieval collapses between n={GATE_HI} and n={GATE_HI+1} -- why the ceiling is {GATE_HI}")
check(cov[GATE_LO]["zero_pct"] < cov[GATE_HI]["zero_pct"],
      f"n={GATE_LO} retrieves BETTER than n={GATE_HI}, which the old 4-10 band included "
      f"and this excluded -- why the floor moved to {GATE_LO}")
check(all(cov[n]["median"] == 0 for n in (11, 12)),
      "median pool is 0 at n=11 and n=12 -- above the ceiling only source B answers")

print(f"\n{len(QUOTED) + 5 - len(fails)}/{len(QUOTED) + 5} gates pass")
sys.exit(1 if fails else 0)
