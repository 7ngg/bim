"""Ship gates on a region profile, asserted against the data file.

Two arithmetic constraints have to hold before a profile ships (map C15):

  ADR 0004  every wall thickness is an even number of millimetres, so that
            `erode(rect, t_int/2)` and the tier-1 `t_party/2` stay integral.
            ADR 0010 makes a thickness a LAYER SET, which sharpens this: the
            rule binds on the numbers that get HALVED -- the totals -- and not
            on a layer component, which only ever enters a total doubled. A
            15 mm finish is legal and a 15 mm wall is not.
  ADR 0007  every *hard linear* minimum satisfies `min + t_int == 0 (mod grid)`
            for every `t_int` the profile offers, so the clear reading does not
            cost a whole grid unit per room per axis.

Run:  python experiments/region-profile/gate_check.py
"""
import json
import pathlib
import re
import sys

GRID = 250
PROFILE = "AZ"
DATA = pathlib.Path(__file__).resolve().parents[2] / "data/standards/room-constraints.json"

fails, notes = [], []


def check(ok, label, detail=""):
    (notes if ok else fails).append(f"{'PASS' if ok else 'FAIL'}  {label}" + (f"  -- {detail}" if detail else ""))


def main():
    doc = json.loads(DATA.read_text(encoding="utf-8"))
    az = doc["profiles"][PROFILE]
    cat = az["construction"]["catalogue"]

    # ---- ADR 0004, thicknesses -------------------------------------------
    # ADR 0010: a thickness is a layer set. Evenness binds on what is halved.
    HALVED_NOWHERE = {"t_finish"}
    for ctype, fields in cat.items():
        for name, cell in fields.items():
            t = cell["v"]
            if name in HALVED_NOWHERE:
                check(isinstance(t, int),
                      f"ADR 0004 exempt (enters doubled) {ctype}.{name} = {t}")
                continue
            check(isinstance(t, int) and t % 2 == 0,
                  f"ADR 0004 even thickness {ctype}.{name} = {t}")

    # ---- ADR 0010, the layer arithmetic actually closes -------------------
    for ctype, fields in cat.items():
        if "t_finish" not in fields:
            continue
        f = fields["t_finish"]["v"]
        for total, leaf in (("t_int", "t_int_structural"),
                            ("t_party", "t_party_structural")):
            if total in fields and leaf in fields:
                check(fields[total]["v"] == fields[leaf]["v"] + 2 * f,
                      f"ADR 0010 {ctype}.{total} = {leaf} + 2 x t_finish",
                      f"{fields[total]['v']} vs "
                      f"{fields[leaf]['v']} + 2 x {f}")

    # ---- ADR 0004, openings ----------------------------------------------
    # The mark encodes decimetres; the opening itself is nominal + 10 mm both
    # axes, so evenness is a property of the nominal series.
    for key, cell in az["openings"]["catalogue"].items():
        dims = [int(round(float(p.replace(",", ".")) * 100))
                for p in cell["v"].split()[-1].split("-")]
        for d in dims:
            check(d % 2 == 0, f"ADR 0004 even opening {key} {cell['v']} -> {d} mm")

    # ---- ADR 0007 --------------------------------------------------------
    t_ints = sorted({f["t_int"]["v"] for f in cat.values()})
    check(len(t_ints) == 1,
          f"ADR 0007 profile offers exactly one t_int",
          f"offers {t_ints}; two thicknesses share a minima table only if they "
          f"differ by a multiple of {GRID}")
    t_int = t_ints[0]

    declared = az["construction"]["residue_class_mod_grid"]
    check(declared["residue"] == (-t_int) % GRID,
          f"ADR 0007 declared residue matches t_int",
          f"declared {declared['residue']}, computed {(-t_int) % GRID}")
    check(all(m % GRID == declared["residue"] for m in declared["admissible_linear_minima"]),
          "ADR 0007 declared admissible minima are all in the residue class")

    # The rule binds HARD linear minima. Find where they actually are.
    # rules.json's tier_binding supersedes room-constraints.json's, and says so.
    rules = json.loads((DATA.parents[1] / "acceptance/rules.json").read_text(encoding="utf-8"))
    hard_tier = rules["tier_binding"]["hard_reject_below"]

    hard_in_profile = []
    for room, cells in az["rooms"]["clear_widths_mm"].items():
        if room == "comment":
            continue
        cell = cells.get(hard_tier)
        if cell and cell.get("v") is not None:
            hard_in_profile.append((room, cell["v"]))
    for room, m in hard_in_profile:
        check((m + t_int) % GRID == 0, f"ADR 0007 hard linear minimum {room} = {m}")

    # ---- ADR 0012, the vertical datum -----------------------------------
    # v1 has ONE vertical datum, h_clear, and one derived head line. These
    # gates assert the datum actually holds the file up: with h_storey
    # deleted there is no floor-to-floor left to hide a bad opening in.
    ch = az["rooms"]["clear_heights_mm"]
    h_clear = ch["habitable_room_and_kitchen"]["v"]
    op = az["openings"]
    head = op["head_datum_mm"]["v"]
    guard = op["fall_barrier_mm"]["v"]

    check(ch["storey_height_mm"]["v"] is None,
          "ADR 0012 h_storey is NULL -- AzDTN 2.7-2 prescribes no storey height")
    check(ch["corridor_hall_antresol"]["v"] <= h_clear,
          f"ADR 0012 corridor allowance {ch['corridor_hall_antresol']['v']} <= h_clear {h_clear}")
    check("fall_barrier_trigger_mm" not in op,
          "ADR 0012 the guarding TRIGGER is refused, not chosen -- fall_barrier_when_required")
    check(op["fall_barrier_mm"]["conf"] == "verified",
          f"ADR 0012 guarding height {guard} is verified (cl. 8.3, mandatory register)")
    check(guard < h_clear, f"ADR 0012 fall barrier {guard} < h_clear {h_clear}")
    check(head <= h_clear, f"ADR 0012 head datum {head} <= h_clear {h_clear}")

    # A GOST opening mark is <type> <HEIGHT dm>-<width dm>. Height comes first.
    def mark_h(cell):
        m = re.search(r"([0-9]+)\s*-", cell["v"])
        return int(m.group(1)) * 100 if m else None

    sills = {}
    for key, cell in op["catalogue"].items():
        h = mark_h(cell)
        if h is None:
            check(False, f"ADR 0012 catalogue {key} mark parses a height", cell["v"])
            continue
        check(h <= h_clear, f"ADR 0012 {key} ({cell['v']}) head {h} <= h_clear {h_clear}")
        check(h % 2 == 0, f"ADR 0004 {key} opening height {h} is even")
        if key.startswith("window_"):
            check(h <= head, f"ADR 0012 {key} ({cell['v']}) H {h} <= head datum {head}")
            sill = head - h
            sills[key] = sill
            check(sill % 2 == 0, f"ADR 0004 {key} derived sill {sill} is even")

    check(sills["window_kitchen"] > sills["window_living"],
          f"ADR 0012 kitchen sill {sills['window_kitchen']} is above living "
          f"{sills['window_living']} -- the short window clears a counter")
    check(min(sills.values()) > 0 and max(sills.values()) < h_clear,
          f"ADR 0012 every derived sill is inside the room: {sorted(sills.values())}")


    print("\n".join(notes))
    print()
    print(f"hard tier is {hard_tier!r}")
    print(f"hard linear minima published by profile {PROFILE}: {len(hard_in_profile)}")

    # ---- where they really live ------------------------------------------
    inv = doc.get(hard_tier)
    if not inv:
        print(f"  (no {hard_tier!r} layer in the file yet)")
        return 1 if fails else 0

    linear = []
    for room, cells in inv["rooms"].items():
        if not isinstance(cells, dict):
            continue
        for field, cell in cells.items():
            if isinstance(cell, dict) and isinstance(cell.get("v"), int) and "clear" in field:
                linear.append((f"{room}.{field}", cell["v"]))
    misaligned = [(k, m) for k, m in linear if (m + t_int) % GRID != 0]

    print(f"hard linear minima published by the region-INVARIANT {hard_tier!r} layer: "
          f"{len(linear)}, of which {len(misaligned)} miss the residue class "
          f"{(-t_int) % GRID}:")
    for k, m in sorted(misaligned, key=lambda kv: -((-(kv[1] + t_int)) % GRID))[:12]:
        waste = (-(m + t_int)) % GRID
        print(f"    {k:34s} {m:5d}  ->  {m + waste:5d}   (+{waste} mm per room per axis)")
    if len(misaligned) > 12:
        print(f"    ... and {len(misaligned) - 12} more")
    print()
    print("  NOT A GATE FAILURE, and by ADR 0009 not a defect either. ADR 0007's congruence")
    print("  rule is a REGION-PROFILE ship gate only; the ergonomic layer is exempt because")
    print("  its numbers are derived from fixture footprints rather than quoted from a")
    print("  source, so there is no nominal-to-clear conversion to apply. The layer's own")
    print("  `reading` field states it: 'nothing here has t_int to subtract.' The solver's")
    print("  ceiling absorbs the remainder and the published number stays millimetre-exact.")
    print("  These 36 rows are printed to show the exemption is load-bearing, not cosmetic.")
    print()

    if fails:
        print("\n".join(fails))
        print(f"\n{len(fails)} gate failure(s)")
        return 1
    print(f"all {len(notes)} gates pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
