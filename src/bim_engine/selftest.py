"""The drawing layer against `annotation.md` section 14, number by number.

That worked example is the only fully computed Plan on this map -- envelope,
solved rectangles, clear rectangles, areas, tier 1, four tier-2 chains, two
tier-3 chains, four setting-out dimensions, two windows sized from the series,
and the totals row that deliberately does not add up. It was written by hand,
before any of this code existed, which makes it a genuine oracle rather than a
restatement of the implementation.

    ./venv/Scripts/python.exe -m bim_engine.selftest        (from src/)

Exits non-zero on the first disagreement. A failure here means either this
package is wrong or section 14 is, and both are worth stopping for.

ONE KNOWN DIVERGENCE, AND IT IS THE SPEC'S: section 14 states its exterior edges
at t = 300, where the shipped profile's `t_ext_total` is 500 (engine_choice,
provisional, blocked on Baku's degree-day figure). Tier 1 is therefore checked
against the profile's arithmetic, and the spec's own 8150 / 6150 is reported
beside it rather than asserted.
"""
from __future__ import annotations

import sys

from . import build, dimensions, fmt, openings, profile
from .model import Plan

FAILED = []


def check(name, got, want):
    ok = got == want
    print("[%s] %-46s got %s want %s" % ("PASS" if ok else "FAIL", name, got, want))
    if not ok:
        FAILED.append(name)
    return ok


def s14_plan() -> Plan:
    """section 14's inputs, in GRID units. Envelope 32 x 24 cells, no notches.
    S and W exterior, N and E party, entrance side N."""
    faces = [("v", 0, 0, 24, True),      # W exterior
             ("v", 32, 0, 24, False),    # E party
             ("h", 0, 0, 32, True),      # S exterior
             ("h", 24, 0, 32, False)]    # N party
    parts = [[(0, 0, 18, 15)],           # R01 living_dining_kitchen
             [(18, 0, 32, 15)],          # R02 bedroom_double
             [(0, 15, 10, 24)],          # R03 bathroom
             [(10, 15, 24, 24)],         # R04 hall
             [(24, 15, 32, 24)]]         # R05 storage
    keys = ["living_dining_kitchen", "bedroom_double", "bathroom", "hall", "storage"]
    labels = ["LIVING_DINING", "PRIVATE", "BATHROOM", "CORRIDOR", "STOREROOM"]
    return build.make_plan("annotation-s14", 32, 24, [], faces, parts,
                           labels, keys, entrance_side="N")


def main() -> int:
    plan = s14_plan()

    # ---- clear rectangles, section 14's own table -------------------------
    want = {"R01": (0, 0, 4350, 3600), "R02": (4500, 0, 7850, 3600),
            "R03": (0, 3750, 2350, 5850), "R04": (2500, 3750, 5850, 5850),
            "R05": (6000, 3750, 7850, 5850)}
    for ref, w in want.items():
        r = plan.by_ref(ref).primary
        check("clear rect %s" % ref, (r.x1, r.y1, r.x2, r.y2), w)

    check("Envelope inner", (plan.inner.w, plan.inner.h), (7850, 5850))

    # ---- areas ------------------------------------------------------------
    for ref, a in (("R01", "15,66"), ("R02", "12,06"), ("R03", "4,94"),
                   ("R04", "7,04"), ("R05", "3,89")):
        check("area %s" % ref, fmt.area_cell(plan.by_ref(ref).area_m2), a)
    check("sum Space printed",
          fmt.area_cell(sum(fmt.parse_back(fmt.area_cell(s.area_m2))
                            for s in plan.spaces)), "43,59")
    check("sum Space exact rounds to", fmt.area_cell(plan.sum_space_m2), "43,58")
    check("Envelope inner area", fmt.area_cell(plan.interior_m2), "45,92")
    check("yasayis sahesi", fmt.area_cell(plan.habitable_m2), "27,72")

    # ---- openings ---------------------------------------------------------
    openings.place(plan)
    doors = [o for o in plan.openings if o.is_door]
    wins = [o for o in plan.openings if o.kind == "window"]
    check("door count", len(doors), 5)
    check("window count", len(wins), 2)

    ent = doors[0]
    check("entrance is on the N party wall", (ent.axis, ent.across),
          ("h", (5850, 5850 + profile.T_PARTY_MM)))
    check("entrance structural opening", (ent.p1, ent.p2), (2600, 3500))
    check("entrance receives the hall", plan.by_ref(ent.receiving).key, "hall")
    check("entrance swings into circulation", ent.swing_side,
          openings._side_of_space(plan, ent, ent.receiving))

    by_recv = {plan.by_ref(d.receiving).ref: d for d in doors if d.other}
    for ref, w, datum in (("R01", 900, 2500), ("R02", 800, 4500),
                          ("R03", 700, 5850), ("R05", 700, 5850)):
        d = by_recv.get(ref)
        if d is None:
            check("door to %s exists" % ref, False, True)
            continue
        check("door %s structural width" % ref, d.width, w)
        check("door %s setting-out datum" % ref, d.datum, datum)
        check("door %s leaf" % ref, d.leaf_w, w - 100)

    w1 = [w for w in wins if w.host_space == "R01"][0]
    w2 = [w for w in wins if w.host_space == "R02"][0]
    check("OK1 width", w1.width, 1800)
    check("OK1 position", (w1.p1, w1.p2), (1275, 3075))
    check("OK1 designation", openings.window_designation(1800, 1500), "ОР 15-18")
    check("OK2 width", w2.width, 1350)
    check("OK2 position", (w2.p1, w2.p2), (5500, 6850))
    check("OK2 designation", openings.window_designation(1350, 1500), "ОР 15-13,5")
    check("OK1 sill", openings.sill_mm(w1), 700)

    # ---- dimensions -------------------------------------------------------
    dims = dimensions.derive(plan)
    got = {(c.tier, c.side): c.segments for c in dims.chains}
    check("tier 2 South", got[(2, "S")], [4350, 150, 3350])
    check("tier 2 North", got[(2, "N")], [2350, 150, 3350, 150, 1850])
    check("tier 2 West", got[(2, "W")], [3600, 150, 2100])
    check("tier 2 East", got[(2, "E")], [3600, 150, 2100])
    check("tier 2b is empty", len(dims.runnings), 0)
    check("tier 3 South", got[(3, "S")], [1275, 1800, 2425, 1350, 1000])
    check("tier 3 North", got[(3, "N")], [2600, 900, 4350])
    check("every chain closes",
          all(c.closes(c.span) for c in dims.chains), True)
    check("setting-out is 100 everywhere",
          sorted({s.value for s in dims.setting_out}), [100])
    check("setting-out count", len(dims.setting_out), 4)

    t1 = dimensions.tier1(plan)
    print("     tier 1 at the profile's t_ext=%d: x=%d y=%d  "
          "(section 14 states 8150 / 6150 at its own t=300)"
          % (profile.T_EXT_MM, t1["S"], t1["W"]))
    check("tier 1 x from the profile", t1["S"], 7850 + profile.T_EXT_MM)
    check("tier 1 y from the profile", t1["W"], 5850 + profile.T_EXT_MM)

    print()
    if FAILED:
        print("%d FAILED: %s" % (len(FAILED), ", ".join(FAILED)))
        return 1
    print("annotation.md section 14 reproduced.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
