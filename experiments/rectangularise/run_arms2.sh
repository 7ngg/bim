#!/usr/bin/env bash
# Ticket 85, second chain: more realisations of the SHIPPED config.
#
# One repeat pair gives one realisation of the drift, which is a delta and not a
# band. ADR 0043 decision 6 item 4 asks for "N runs x which seeds, as a
# distribution"; its own aggregate floor was six draws. With the baseline and
# rep1/rep2 already in hand these two take the shipped config to five runs over
# one key list, which is enough for a range and an sd per published figure.
set -eu
cd "$(dirname "$0")"
PY=/c/Users/tng/g2p/bim-engine/venv/Scripts/python.exe
N=${N:-400}
K=out/det/keys.json

# `run <name> [flags]` uses $N. `runn <count> <name> [flags]` overrides it for
# ONE call -- deliberately not `N=60 run ...`, because bash keeps a prefix
# assignment after a FUNCTION call and rep3/rep4 would silently run at 60.
runn () {
  local n=$1; shift
  local name=$1; shift
  if [ -f "out/det/$name.json" ]; then echo "### $name exists, skip"; return; fi
  echo "### $name $* n=$n @ $(date +%H:%M:%S)"
  "$PY" fit_rects.py "$n" --k2 --only=$K --out="det/$name.json" --every=200 "$@"     > "out/det/$name.log" 2>&1
  tail -2 "out/det/$name.log"
}

run () {
  local name=$1; shift
  if [ -f "out/det/$name.json" ]; then echo "### $name exists, skip"; return; fi
  echo "### $name $* @ $(date +%H:%M:%S)"
  "$PY" fit_rects.py "$N" --k2 --only=$K --out="det/$name.json" --every=200 "$@" \
    > "out/det/$name.log" 2>&1
  tail -2 "out/det/$name.log"
}

# FIRST, because it is the one config the arms do not cover and it decides the
# recommendation. ADR 0043 decision 3 adopted `num_workers = 1` +
# `max_deterministic_time` for the warp, measured at 0,00 % disagreement and no
# wall cost. One worker under a WALL cap still lets a marginal record flip
# decided/undecided -- 2 in 56 on the probe -- and a deterministic cap is what
# removes that. What it costs here is unknown: a deterministic budget carries NO
# wall bound (ADR 0043 decision 4), so this is a calibration before a pair, not a
# pair. 60 dwellings, two budgets.
runn 60 c_w1d10 --workers=1 --dettime=10
runn 60 c_w1d30 --workers=1 --dettime=30

run rep3
run rep4
echo "### chain 2 done @ $(date +%H:%M:%S)"
