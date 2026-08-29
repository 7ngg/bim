# -*- coding: utf-8 -*-
"""Recompute the four MIDA-sourced `market_default` cells from the COMMITTED schedule.

ADR 0035 moved four shipped constants onto MIDA's published Baku schedules. This
file is the check that they still follow from the data, and it deliberately reads
`mida_plans_318.json` -- the committed derived file -- rather than the gitignored
raw harvest, so it runs in a clean clone.

It is NOT `gate_check.py`. That file is 67 gates of ARITHMETIC properties of the
profile and the ticket that owns adding a `the profile matches its own source`
gate to it is *The law is a hand copy and it now shapes rooms*. This is the
narrower thing: the four cells whose source is a measurement rather than a
document, checked against that measurement.

Run:  ./venv/Scripts/python.exe experiments/baku-market-areas/verify_shipped_cells.py
"""
import json
import math
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PLANS = os.path.join(HERE, "mida_plans_318.json")
PROFILE = os.path.join(ROOT, "data", "standards", "room-constraints.json")


def q(vals, p):
    v = sorted(vals)
    i = (len(v) - 1) * p
    lo, hi = math.floor(i), math.ceil(i)
    return v[lo] if lo == hi else v[lo] + (v[hi] - v[lo]) * (i - lo)


def rooms(plan, name):
    return sorted((x["sq"] for x in plan["rooms"] if x["n"] == name), reverse=True)


def main():
    doc = json.load(open(PLANS, encoding="utf-8"))
    plans = doc["plans"]
    areas = json.load(open(PROFILE, encoding="utf-8"))["profiles"]["AZ"]["rooms"]["areas_m2"]

    # (cell, selector, expected n, expected p50, shipped value, how it was rounded)
    CASES = [
        ("living_room_2plus",
         [rooms(p, "Qonaq otağı")[0] for p in plans if rooms(p, "Qonaq otağı")], 312, 17.60, 17.6),
        ("bedroom_double",
         [rooms(p, "Yataq otağı")[0] for p in plans if rooms(p, "Yataq otağı")], 287, 13.20, 13.2),
        ("bedroom_single",
         [rooms(p, "Yataq otağı")[-1] for p in plans if len(rooms(p, "Yataq otağı")) >= 2], 159, 11.45, 11.5),
        ("wc",
         [rooms(p, "Sanitar qovşağı")[1] for p in plans if len(rooms(p, "Sanitar qovşağı")) >= 2], 172, 2.06, 2.1),
    ]

    fails = []
    print("%-22s %6s %8s %8s %8s" % ("cell", "n", "p50", "shipped", "verdict"))
    for cell, vals, want_n, want_p50, shipped in CASES:
        got_n, got_p50 = len(vals), round(q(vals, 0.5), 2)
        live = areas[cell]["market_default"]
        ok = (got_n == want_n and abs(got_p50 - want_p50) < 0.005
              and live["v"] == shipped and live["src"] == "az_mida_2026"
              # the rounding rule, enforced: nearest 0,1 m2 off the measured p50, so a
              # shipped cell can never sit more than half a step from the data (ADR 0035)
              and abs(live["v"] - got_p50) <= 0.05 + 1e-9)
        if not ok:
            fails.append("%s: n=%d (want %d), p50=%.2f (want %.2f), shipped=%s src=%s"
                         % (cell, got_n, want_n, got_p50, want_p50, live["v"], live["src"]))
        print("%-22s %6d %8.2f %8s %8s" % (cell, got_n, got_p50, live["v"], "PASS" if ok else "FAIL"))

    # ADR 0035's rule itself: no MIDA-sourced cell may sit below the AzDTN value it replaced.
    for cell in ("living_room_2plus", "bedroom_double", "bedroom_single"):
        live = areas[cell]["market_default"]
        old = live.get("superseded_by_measurement", {}).get("v")
        if old is None or live["v"] < old:
            fails.append("%s: monotone-upward rule violated -- %s is not above the superseded %s"
                         % (cell, live["v"], old))
    print("\nmonotone-upward rule: every MIDA cell sits at or above the AzDTN value it replaced")

    if fails:
        print("\n%d FAIL" % len(fails))
        for f in fails:
            print("  " + f)
        raise SystemExit(1)
    print("all %d shipped MIDA cells reproduce from the committed schedule" % len(CASES))


if __name__ == "__main__":
    main()
