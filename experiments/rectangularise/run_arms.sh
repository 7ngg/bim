#!/usr/bin/env bash
# Ticket 85. The paired arms, SERIALLY.
#
# Serial is not a convenience. Two arms running at once contend for cores, and
# the wall-clock cap is the thing under test -- a contended arm reports the cap
# biting more often and attributes it to the arm. ADR 0043 made the opposite
# point about the warp (an idle machine exonerates the wall clock), and both
# follow from the same rule: the load must be the same in every arm you compare.
set -eu
cd "$(dirname "$0")"
PY=/c/Users/tng/g2p/bim-engine/venv/Scripts/python.exe
N=${N:-400}
K=out/det/keys.json

run () {                       # run <name> [extra flags...]
  local name=$1; shift
  if [ -f "out/det/$name.json" ]; then echo "### $name exists, skip"; return; fi
  echo "### $name $* @ $(date +%H:%M:%S)"
  "$PY" fit_rects.py "$N" --k2 --only=$K --out="det/$name.json" --every=100 "$@" \
    > "out/det/$name.log" 2>&1
  tail -2 "out/det/$name.log"
}

# REPEAT: nothing varied at all. Two runs of the shipped config. If these
# disagree, wall-clock racing is proved without implicating seed or cap.
run rep1
run rep2
# SEED: the mechanism the ticket named, at the shipped cap.
run seed7   --seed=7
# CAP: the other mechanism, at the shipped seed. Costs more per dwelling by
# construction -- only the capped records get longer.
run cap30   --time=30
# FIX: the candidate, twice. Determinism is a claim about repeat runs, so it is
# measured the way the defect was. One worker removes the race; the wall cap
# stays, because a deterministic budget has NO wall bound (ADR 0043 decision 4:
# `DeterministicLoop` takes no time limit) and the probe measured that costing
# 1,85x the wall time for a cover that still moves.
run w1a     --workers=1
run w1b     --workers=1
echo "### all arms done @ $(date +%H:%M:%S)"
