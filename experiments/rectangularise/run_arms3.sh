#!/usr/bin/env bash
# Ticket 85, third chain: the candidate shipped configuration, as a pair.
#
# `w1a`/`w1b` proved one worker reproducible at the SHIPPED 10 s cap, and `cap30`
# proved 30 s decides every dwelling (0 UNKNOWN) at 1,55x the wall cost. The
# recommendation is the combination, and the combination is not the sum of two
# arms: a longer cap gives the wall clock more room to cut in a different place,
# so the residual 1-in-366 disagreement could grow rather than shrink. Measured,
# not assumed -- and measured the way every other determinism claim here is, by
# repeat.
set -eu
cd "$(dirname "$0")"
PY=/c/Users/tng/g2p/bim-engine/venv/Scripts/python.exe
N=${N:-400}
K=out/det/keys.json

run () {
  local name=$1; shift
  if [ -f "out/det/$name.json" ]; then echo "### $name exists, skip"; return; fi
  echo "### $name $* @ $(date +%H:%M:%S)"
  "$PY" fit_rects.py "$N" --k2 --only=$K --out="det/$name.json" --every=200 "$@" \
    > "out/det/$name.log" 2>&1
  tail -2 "out/det/$name.log"
}

run w1c30a --workers=1 --time=30
run w1c30b --workers=1 --time=30
echo "### chain 3 done @ $(date +%H:%M:%S)"
