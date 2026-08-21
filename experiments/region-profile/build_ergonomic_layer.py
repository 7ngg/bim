"""Author the `ergonomic` layer of data/standards/room-constraints.json.

The layer is GENERATED, not typed, so the published numbers and the arithmetic
that produced them cannot drift apart. Every value is a sum of published fixture
footprints plus `u`, the one calibrated body-zone constant. Re-run to regenerate.

Ticket: docs/wayfinder/tickets/19-ergonomic-minima-and-the-tables-missing-half.md
Findings: docs/research/ergonomic-minima.md

Run: python experiments/region-profile/build_ergonomic_layer.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "data" / "standards" / "room-constraints.json"

U = 300  # the calibrated body zone; see `body_zone` below.

# --- published fixture footprints, mm -------------------------------------
# AD M Volume 1 Appendix D (OGL, verified) unless the note says otherwise.
F = {
    "bath":            (700, 1700),
    "wc_pan":          (500, 700),
    "basin":           (450, 600),
    "shower_tray":     (900, 900),
    "bed_single":      (900, 1900),
    "bed_double":      (1350, 1900),
    "bed_principal":   (1500, 2000),
    "settee_3":        (850, 1850),
    "armchair":        (850, 850),
    "desk":            (500, 1050),
    "table_4p":        (1000, 1200),
    "unit_depth":      (600, 600),
    "sink_drainer":    (600, 900),
    "appliance":       (600, 600),
}

# --- room programmes -------------------------------------------------------
# (short_mm, long_mm, human-readable arithmetic). `u` is added once per body
# zone that CANNOT be shared with another fixture's zone.
def programmes(u: int) -> dict[str, tuple[int, int, str]]:
    return {
        "living": (
            F["settee_3"][0] + u + F["armchair"][0], F["settee_3"][1],
            f"3-seat settee 850 deep + body {u} + armchair 850 deep = "
            f"{850+u+850} across; settee 1850 long"),
        "dining": (
            F["table_4p"][0] + u, F["table_4p"][1] + u,
            f"4-person table 1000 x 1200 (Neufert 600 x 400 per place + 200 "
            f"serving strip) + body {u} on the served side of each axis"),
        "living_dining": (None, None, "packed from living and dining"),
        "kitchen": (
            F["unit_depth"][0] + u,
            F["sink_drainer"][1] + F["appliance"][0] + F["appliance"][0],
            f"base-unit run 600 deep + body {u} across the aisle; Neufert's work "
            f"sequence store-wash-prepare-cook = fridge 600 + sink/drainer 900 "
            f"+ hob 600 along the run"),
        "kitchen_dining": (None, None, "packed from kitchen and dining"),
        "living_dining_kitchen": (None, None, "packed from living, dining and kitchen"),
        "bedroom_principal": (
            F["bed_principal"][0] + 2 * u, F["bed_principal"][1] + u,
            f"principal double 1500 x 2000 + body {u} to BOTH sides and the foot "
            f"(AD M M4(2) 2.25 gives the principal double both sides)"),
        "bedroom_double": (
            F["bed_double"][0] + u, F["bed_double"][1],
            f"double bed 1350 x 1900 + body {u} to one side (AD M M4(2) 2.25)"),
        "bedroom_single": (
            F["bed_single"][0] + u, F["bed_single"][1],
            f"single bed 900 x 1900 + body {u} to one side (AD M M4(2) 2.25)"),
        "study": (
            F["desk"][0] + u, F["desk"][1],
            f"desk 500 x 1050 (AD M Appendix D 'table and chair') + body {u}"),
        "bathroom": (
            F["bath"][0] + u, F["bath"][1],
            f"bath 700 deep + body {u} alongside; bath 1700 long. Pan and basin "
            f"occupy the same strip as the body zone, which is shared"),
        "shower_room": (
            max(F["shower_tray"][0], F["wc_pan"][1] + u),
            F["shower_tray"][1] + F["wc_pan"][0],
            f"tray 900 beside pan 500 = 1400 along the wall; across, the deeper "
            f"of the 900 tray and pan 700 + body {u}"),
        "wc": (
            F["wc_pan"][0] + u, F["wc_pan"][1] + u,
            f"pan and cistern 500 x 700 + body {u} to one side and in front"),
        "utility": (
            F["unit_depth"][0] + u, F["sink_drainer"][1] + F["appliance"][0],
            f"unit run 600 deep + body {u}; sink/drainer 900 + washing machine 600"),
        "hall": (
            900, 838 + u,
            f"AD M M4(2) 2.22a clear width 900; entrance leaf 838 + body {u} for "
            f"the swing"),
        "entrance_lobby": (
            900, 838 + u,
            "as hall; the two differ in programme, not in geometry"),
        "corridor": (
            900, 900,
            "AD M M4(2) 2.22a clear width 900, both axes. A corridor has no "
            "second dimension of its own"),
        "storage": (
            F["unit_depth"][0], F["unit_depth"][0] + u,
            f"shelf depth 600; shelf 600 + body {u} to reach it"),
    }


# (is_habitable, is_wet, is_private, needs_window). Definitions, not
# measurements -- see flag_semantics. needs_window follows is_habitable except
# for kitchen, where BayBO Art. 46(1) expressly permits a windowless kitchen with
# effective ventilation and win.kitchen_windowless surfaces the fact instead.
FLAGS = {
    "living":                (True,  False, False, True),
    "dining":                (True,  False, False, True),
    "living_dining":         (True,  False, False, True),
    "kitchen":               (False, True,  False, False),
    "kitchen_dining":        (True,  True,  False, True),
    "living_dining_kitchen": (True,  True,  False, True),
    "bedroom_principal":     (True,  False, True,  True),
    "bedroom_double":        (True,  False, True,  True),
    "bedroom_single":        (True,  False, True,  True),
    "study":                 (True,  False, True,  True),
    "bathroom":              (False, True,  True,  False),
    "shower_room":           (False, True,  True,  False),
    "wc":                    (False, True,  True,  False),
    "utility":               (False, True,  False, False),
    "hall":                  (False, False, False, False),
    "entrance_lobby":        (False, False, False, False),
    "corridor":              (False, False, False, False),
    "storage":               (False, False, False, False),
}

# Composite rooms hold two or three programmes disjointly. A (short, long) pair
# cannot say "contains A or B", so we publish the PERMISSIVE envelope: the
# smallest short, the smallest long and the smallest area over all packings.
COMPOSITES = {
    "living_dining": ("living", "dining"),
    "kitchen_dining": ("kitchen", "dining"),
    "living_dining_kitchen": ("living", "dining", "kitchen"),
}


def pack(parts: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Stack parts in a common-width band, once per candidate width."""
    out = []
    for w in sorted({d for p in parts for d in p}):
        if any(min(p) > w for p in parts):
            continue
        depth = 0
        for s, lg in parts:
            depth += lg if s <= w < lg else s if lg <= w else lg
        out.append((w, depth) if w <= depth else (depth, w))
    return out


def main() -> None:
    prog = programmes(U)
    rooms: dict[str, dict] = {}

    for kind, (s, lg, why) in prog.items():
        if kind in COMPOSITES:
            continue
        s, lg = (s, lg) if s <= lg else (lg, s)
        rooms[kind] = {"short": s, "long": lg,
                       "area": int(s * lg / 1e5) / 10.0, "why": why}

    for kind, members in COMPOSITES.items():
        parts = [(rooms[m]["short"], rooms[m]["long"]) for m in members]
        packings = pack(parts)
        s = min(p[0] for p in packings)
        lg = min(p[1] for p in packings)
        area = min(int(p[0] * p[1] / 1e5) / 10.0 for p in packings)
        rooms[kind] = {
            "short": s, "long": lg, "area": area,
            "packings": [list(p) for p in packings],
            "why": ("permissive envelope over the packings of "
                    + " + ".join(members) + ": "
                    + "; ".join(f"{a} x {b}" for a, b in packings))}

    doc = json.loads(TARGET.read_text(encoding="utf-8"))
    doc.pop("PLACEHOLDER_NOTE", None)

    # NOTE: this generator used to add a `de_baybo` source block, to close a
    # key data/acceptance/rules.json cited and the sources block lacked. *The
    # Azerbaijani region profile* closed it better and concurrently, by
    # RE-SOURCING both consumers to AzDTN 2.7-2 -- which also caught that AZ
    # REQUIRES the kitchen window where Bayern permitted its absence, so the
    # BayBO reading was not merely redundant but inverted. Nothing cites
    # de_baybo now, so the block is not added.

    doc["tier_model"]["validator_binding"]["hard_reject_below"] = "ergonomic"
    doc["tier_model"]["validator_binding"]["hard_reject_below_note"] = (
        "Was null, then 'statutory_floor'. Ticket 7 found that binding unusable "
        "and named the ergonomic minimum instead; ticket 19 authored the layer "
        "and this now names it by the key it actually has. Region-invariant "
        "because bodies are. data/acceptance/rules.json tier_binding must hold "
        "the same string; a conformance test asserts it.")

    doc["ergonomic"] = {
        "comment": (
            "The region-invariant hard floor, and the whole hard dimensional "
            "reject set of the acceptance bar. Every value is DERIVED -- a sum of "
            "published fixture footprints plus the body zone below -- never "
            "transcribed from a table. Findings section 7.6 item 12 requires this; "
            "it is also the strongest copyright hygiene available, because the row "
            "set, the programmes and the arithmetic are ours."),
        "generated_by": "experiments/region-profile/build_ergonomic_layer.py",
        "findings": "docs/research/ergonomic-minima.md",
        "reading": {
            "dimensions_are_clear": "Every value is a CLEAR dimension, per ADR 0001 -- what an occupant can tape between finished faces. Nothing here is nominal or centreline, so nothing here has t_int to subtract.",
            "short_and_long_not_width_and_depth": "A room has no canonical orientation, so the pair is (shorter side, longer side), not (x, y). Findings section 8 set min_width = min_depth for orientation-free rooms and made bathroom and wc directional exceptions; that distinction DISSOLVES under this reading -- the acceptance rules are already stated over the shorter and longer clear dimension, so every room publishes a (short, long) pair and no room needs an axis binding. Most room types turn out non-square once fixtures drive the rectangle, not just the two.",
            "area_is_not_redundant": "area is short x long rounded DOWN to 0.1 m2. Rounded up it would reject the very rectangle it was derived from. It binds independently because a room may satisfy both sides and still be long and thin -- dim.aspect_ratio_hard catches that separately.",
            "adr_0007_does_not_apply_here": "ADR 0007 requires a published minimum to satisfy min + t_int = 0 (mod grid). That rule is sound for a CONVENTION-derived number, where the source quoted a nominal or centreline figure and subtracting t_int recovers the clear one, and UNSOUND for a derivation-derived one, which is already clear and has nothing to subtract. A derived 1700 mm IS the bath; rounding it down to 1650 deletes 50 mm of bathtub. Measured: snapping this layer onto the 250 mm lattice costs the wc floor about 10 points of real corpus. So the ergonomic layer publishes millimetre-precise minima and the solver's ceiling absorbs the remainder; ADR 0007 continues to bind on the region profile, whose numbers are quoted."
        },
        "body_zone": {
            "v": U,
            "src": "engine_choice",
            "ref": "calibrated; see note",
            "conf": "engine_choice",
            "note": ("The single free parameter: the depth of body in front of a "
                     "fixture that cannot be shared with another fixture's zone. "
                     "Fitted so that no room type's floor rejects more than about "
                     "5% of fixture-consistent real rooms in Swiss Dwellings "
                     "(experiments/region-profile/floor_calibration.py). It lands "
                     "on 300 mm, which is also Neufert's stated minimum clearance "
                     "from a WC pan's free side to a wall -- fitted and cited "
                     "agree. NOT 750 mm: AD M's 750 is a wheelchair transfer "
                     "space, and composing a private bathroom out of accessibility "
                     "figures produces a floor that rejects a third of real homes.")
        },
        "fixtures_mm": {
            "comment": "Footprints, (depth, length). AD M Volume 1 Appendix D is published under the Open Government Licence and may be reproduced with attribution (findings 7.6 item 3). shower_tray is Neufert's 900 mm; table_4p is composed from Neufert's per-place module, not copied.",
            "src": "uk_adm1_2015", "ref": "Appendix D", "conf": "verified",
            "values": {k: list(v) for k, v in F.items()}
        },
        "rooms": {
            k: {
                "min_clear_short": {"v": v["short"], "src": "derived", "ref": "ergonomic.fixtures_mm + ergonomic.body_zone", "conf": "derived", "note": v["why"]},
                "min_clear_long": {"v": v["long"], "src": "derived", "ref": "ergonomic.fixtures_mm + ergonomic.body_zone", "conf": "derived", "note": v["why"]},
                "min_area": {"v": v["area"], "src": "derived", "ref": "short x long, rounded down to 0.1 m2", "conf": "derived", "note": f"{v['short']} x {v['long']} mm"},
                **({"packings_mm": v["packings"],
                    "packings_note": (
                        "A composite room is the only case where min_area EXCEEDS "
                        "min_clear_short x min_clear_long, and that is deliberate. "
                        "The three fields are minimised over the packings "
                        "INDEPENDENTLY, so the box they describe has a corner no "
                        "packing occupies, and min_area is what rules that corner "
                        "out. Every listed packing satisfies all three rules; the "
                        "envelope stays permissive without being loose. For every "
                        "other room type the rectangle IS the packing and "
                        "min_area <= short x long holds.")}
                   if "packings" in v else {}),
                "is_habitable": FLAGS[k][0],
                "is_wet": FLAGS[k][1],
                "is_private": FLAGS[k][2],
                "needs_window": FLAGS[k][3],
            } for k, v in rooms.items()
        },
        "flags_note": (
            "The four booleans are DEFINITIONS, stated operationally in "
            "flag_semantics, and no reference work supplies them. They are "
            "published here per room type because data/acceptance/rules.json "
            "consumes them -- circ.no_private_transit, win.habitable_has_window, "
            "win.exterior_wall and wet.plumbing_group_count all read one -- and "
            "before this they existed only as prose in findings section 8. A flag "
            "the registry cannot read is a predicate that silently does not fire, "
            "which is the same failure as a missing minimum. ONE CORRECTION to "
            "findings section 8: it sets study is_private false, while CONTEXT.md "
            "defines the Private room class as 'a Brief's bedroom, study or "
            "nursery, as one class' and the Proposer spec collapses {ROOM, "
            "BEDROOM, STUDIO} to PRIVATE on the same reasoning. A study that is a "
            "thoroughfare to another room is not a study. Set true here; section 8 "
            "predates the glossary entry."),
        "corpus_label_split": {
            "comment": ("*What the model proposes* handed this ticket the "
                        "BATHROOM split, on the reasoning that the threshold is "
                        "the boundary between two rooms' minima and so falls out "
                        "of this table. MEASURED, THAT IS WRONG. Two floors are "
                        "both floors: wc is 0.8 m2 and shower_room 1.4 m2, and a "
                        "threshold there misclassifies 19% of the corpus. The "
                        "classes differ in their DISTRIBUTIONS, not their minima "
                        "-- real WCs sit at a median 1.85 m2 and real bathrooms at "
                        "4.17 -- so the splitter has to be fitted, and it is "
                        "fitted against fixture ground truth rather than invented: "
                        "Swiss Dwellings carries BATHTUB, SHOWER and TOILET "
                        "features, so which rooms really are bathrooms is known."),
            "label": "BATHROOM",
            "corpus": "swiss_dwellings",
            "threshold_m2": {
                "v": 2.4, "src": "engine_choice",
                "ref": "experiments/region-profile/bathroom_fixture_split.py",
                "conf": "engine_choice",
                "note": ("Fitted over 66,386 fixture-labelled rooms. Total "
                         "misclassification 5.9% at 2.4 m2 against a measured "
                         "optimum of 5.8% at 2.45; 2.4 is published because the "
                         "curve is flat there and the round number is honest about "
                         "the precision. The derived candidates the ticket "
                         "expected -- 3.6 and 4.0 -- score 23.3% and 36.9%. Adding "
                         "the long side as a second test buys nothing: the best "
                         "two-term rule collapses back onto the area term.")
            },
            "error_direction": {
                "below_threshold": "wc",
                "above_threshold": "bathroom",
                "measured": "At 2.4 m2, 1.5% of real bathrooms are called wc and 4.4% of real WCs are called bathroom. It prefers to over-assign to `bathroom`, by about three to one.",
                "why_that_direction_is_tolerable": "An over-large wc wastes floor and breaks nothing. A bathroom that is really a WC arrives with too little room for a bath -- but it is still a real, built Swiss room and still clears the bathroom floor of 1.7 m2, so it produces a small bathroom, not an invalid Plan. Neither error moves a published minimum, because no minimum here is fitted to the corpus."
            }
        },
        "validated_against_corpus": {
            "comment": ("*Rectangularising real rooms* set the principle: every "
                        "corpus dwelling is a real, built, QA'd home, so a hard "
                        "rule that rejects them measures what our model cannot "
                        "express. A derived floor is therefore not self-justifying "
                        "and every value above was checked against Swiss "
                        "Dwellings. The low tail is REAL, not annotation debris: "
                        "0% of wc rooms fail to hold a pan, 0.8% of bathroom rooms "
                        "fail to hold a 1700 mm bath."),
            "harness": "experiments/region-profile/ergonomic_floor_probe.py",
            "reject_rate_of_the_published_floor": {
                "bathroom": 0.000, "living": 0.000, "private": 0.000,
                "dining": 0.006, "kitchen": 0.012, "shower_room": 0.037,
                "wc": 0.046, "storage": 0.078
            },
            "weakest_cells": ["study", "utility", "hall", "entrance_lobby"],
            "weakest_cells_note": "Swiss Dwellings carries no label for these, so they are derived and UNFALSIFIED. study is the weakest number in the file: a one-desk programme with no corpus to check it against and no source that states a study minimum."
        }
    }

    TARGET.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
                      encoding="utf-8")

    print(f"{'room type':24s} {'short':>7} {'long':>7} {'area':>7}")
    for k, v in rooms.items():
        print(f"{k:24s} {v['short']:7d} {v['long']:7d} {v['area']:7.1f}")
    print(f"\nwrote {TARGET}")


if __name__ == "__main__":
    main()
