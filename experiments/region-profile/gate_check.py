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

Ticket 31 adds a third, non-arithmetic family: the ergonomic -> AZ room
vocabulary mapping is total, closed, and its two flags do not drift.

Run:  python experiments/region-profile/gate_check.py
"""
import json
import pathlib
import re
import sys

GRID = 250
PROFILE = "AZ"

# THE RATCHET.  `all N gates pass` is true of a file with every gate deleted, so
# the count is asserted rather than printed.  It lives HERE, next to the runner,
# because the number was previously carried in prose -- map C15, three ADRs and
# two tickets -- and went 146 behind (238 against 384) across four tickets that
# each moved it and none of which updated C15.  A count four documents have to
# remember is a count that goes stale; a count the runner asserts cannot.
#
# RAISE IT when you add gates.  Lowering it is a deliberate act and needs a line
# saying which gates went and why -- ADR 0036 removed three guard entries and
# took the total 238 -> 235 without losing a named gate, which is the shape of a
# legitimate decrease.
# LOWERED 446 -> 445 by *A regulator states an aspect rule and the engine says none
# does* (ticket 72), and NO GATE WENT MISSING.  446 was never satisfiable: at commit
# 8e2dd86, the commit that SET this floor, the runner already emitted 445, and this
# file is byte-identical from that commit to now.  The floor was set one too high, so
# the ratchet has printed a phantom `1 gate(s) have gone missing` on every run since,
# through five ticket closures, and nobody looked -- which is the exact failure mode a
# ratchet exists to prevent, arriving as a false positive instead of a false negative.
# Verified by re-running this file against the room-constraints.json and rules.json of
# 8e2dd86, a910412, 77fc942, e69472a, 006b230 and 4da406f: 445 at every one.
# A check that can never pass is a lie about coverage, the same argument rules.json
# makes for retiring a rule that can never fire.
GATE_FLOOR = 445
DATA = pathlib.Path(__file__).resolve().parents[2] / "data/standards/room-constraints.json"

fails, notes = [], []


def check(ok, label, detail=""):
    (notes if ok else fails).append(f"{'PASS' if ok else 'FAIL'}  {label}" + (f"  -- {detail}" if detail else ""))



def vocabulary_gates(doc, check):
    """Ticket 31 -- the ergonomic -> AZ mapping is total, closed and non-drifting.

    The ticket's closing check reads: "for every room type the Brief can name, both a
    hard floor and a soft target are resolvable". RESOLVABLE MEANS THE LOOKUP IS TOTAL,
    NOT THAT A NUMBER COMES BACK. Ten of eighteen ergonomic keys have no AZ area at all,
    and the other reading -- a non-null soft target for every Brief-nameable type --
    could only be satisfied by inventing ten Azerbaijani numbers, which is precisely the
    C8 failure this profile exists to avoid. So the gate asserts that every lookup is
    defined and every null is explicit, and mapping.null_means carries the semantics.
    """
    inv = doc["ergonomic"]["rooms"]
    az = doc["profiles"]["AZ"]["rooms"]
    mapping = az["mapping"]["rooms"]
    areas, widths = az["areas_m2"], az["clear_widths_mm"]

    # -- V1  totality, both directions ------------------------------------
    check(set(mapping) == set(inv),
          "T31 mapping is total over the ergonomic key set",
          f"{len(mapping)} rows vs {len(inv)} keys; "
          f"missing={sorted(set(inv) - set(mapping))} extra={sorted(set(mapping) - set(inv))}")

    # -- V2  every guard list is well formed and lands on a real cell ------
    for k, r in mapping.items():
        guards = r["az_area"]
        if guards is None:
            continue
        for g in guards:
            check(g["key"] in areas,
                  f"T31 {k}.az_area -> areas_m2.{g['key']} exists")
        unguarded = [i for i, g in enumerate(guards) if g["when_otaq_count"] is None]
        check(unguarded == [len(guards) - 1],
              f"T31 {k}.az_area has exactly one unguarded fallthrough, and it is last",
              f"unguarded at {unguarded} of {len(guards)}")

    # -- V3  the second mapping, into a differently-keyed table ------------
    for k, r in mapping.items():
        w = r["az_clear_width"]
        check(w is None or w in widths,
              f"T31 {k}.az_clear_width -> clear_widths_mm.{w} exists or is null")

    # -- V4  THE TICKET'S CLOSING CHECK ------------------------------------
    for k, node in inv.items():
        if not node["brief_nameable"]:
            continue
        hard = all(isinstance(node[f], dict) and node[f].get("v") is not None
                   for f in ("min_area", "min_clear_short", "min_clear_long"))
        check(hard, f"T31 Brief-nameable {k} resolves a hard floor")
        check("az_area" in mapping[k] and "az_clear_width" in mapping[k],
              f"T31 Brief-nameable {k} resolves a soft target or an explicit null")

    # -- V5  no orphaned profile cell --------------------------------------
    reached = {g["key"] for r in mapping.values() if r["az_area"]
               for g in r["az_area"]}
    for k, cell in areas.items():
        if k == "comment":
            continue
        check(k in reached or cell.get("reachable_in_v1", {}).get("v") is False,
              f"T31 areas_m2.{k} is reachable from the mapping or declares it is not")

    # -- V6  the is_habitable / counts_as_otaq divergence cannot grow silently
    diverge = {k for k, n in inv.items()
               if bool(n["is_habitable"]) != bool(n["counts_as_otaq"])}
    check(diverge == {"kitchen_dining"},
          "T31 is_habitable and counts_as_otaq diverge on exactly the documented type",
          f"diverging: {sorted(diverge)}")

    # -- V7  both new flags present on every key ---------------------------
    for k, node in inv.items():
        check(isinstance(node.get("counts_as_otaq"), bool),
              f"T31 {k}.counts_as_otaq present and boolean")
        check(isinstance(node.get("brief_nameable"), bool),
              f"T31 {k}.brief_nameable present and boolean")

    # -- V8  every printed name is sourced or declares that it is not ------
    for k, r in mapping.items():
        n = r["name_az"]
        check(bool(n["v"]), f"T31 {k}.name_az is non-empty")
        check(n["conf"] != "engine_choice" or bool(n.get("note")),
              f"T31 {k}.name_az is sourced, or engine_choice WITH a note")


def bridge_gates(doc, check):
    """Ticket 69 -- `ergonomic.corpus_label_map`, the THIRD vocabulary.

    Ticket 31 published ergonomic -> AZ on the finding that no object stated the
    bridge between two independently-authored vocabularies. The same defect sat
    one step upstream: every rig in `experiments/warp/` speaks the CORPUS label
    set, every number it needs is keyed by ERGONOMIC key, and the map between
    them lived only in end-of-line comments inside four Python dicts. These gates
    are `vocabulary_gates` V1-V3 in the new direction.
    """
    inv = doc["ergonomic"]["rooms"]
    br = doc["ergonomic"]["corpus_label_map"]
    labels = br["labels"]
    collapse = {k: v for k, v in br["collapse"].items() if k != "comment"}

    # -- B1  every label lands on a real ergonomic key ----------------------
    for lab, row in labels.items():
        check(row["erg"] in inv,
              f"T69 corpus_label_map.{lab}.erg -> ergonomic.rooms.{row['erg']} exists")
        check(row["erg_lenient"] is None or row["erg_lenient"] in inv,
              f"T69 corpus_label_map.{lab}.erg_lenient is null or a real key",
              str(row["erg_lenient"]))

    # -- B2  the collapse resolves before the lookup, and lands inside it ---
    for src, dst in collapse.items():
        check(dst in labels,
              f"T69 corpus_label_map.collapse {src} -> {dst} is itself a mapped label")
        check(src not in labels,
              f"T69 corpus_label_map.collapse source {src} is not ALSO a label",
              "a label that is both collapsed and mapped resolves twice")

    # -- B3  exactly one label carries a single/double split ---------------
    split = {lab for lab, row in labels.items() if row["erg_lenient"]}
    check(split == {"PRIVATE"},
          "T69 exactly one corpus label carries a lenient split, and it is PRIVATE",
          f"split on {sorted(split)}")

    # -- B4  every mapped label is documented ------------------------------
    for lab, row in labels.items():
        check(bool(row.get("note")), f"T69 corpus_label_map.{lab} carries a note")

    # -- B5  the bridge covers what the conversion actually emits ----------
    # Conditional: the gate runs against the profile alone, and gains this check
    # when the converted corpus is on disk.
    rooms = DATA.parents[2] / "experiments/warp/out/dwelling_rooms.json"
    if rooms.exists():
        seen = set()
        for rec in json.loads(rooms.read_text(encoding="utf-8")):
            for t, _a in rec["rooms"]:
                seen.add(t)
        unmapped = sorted(l for l in seen if collapse.get(l, l) not in labels)
        check(not unmapped,
              f"T69 corpus_label_map covers every label the conversion emits "
              f"({len(seen)} distinct)", f"unmapped: {unmapped}")


def referent_gates(doc, check):
    """ADR 0034's four owed gates, plus ADR 0036's fifth. Ticket 69.

    `mapping.referent_model.gate_owed` names (a)-(d); ticket 74 added (e) after
    finding that all four passed an UNLICENSED `part` read -- the open-plan floor
    that sat above all five real Baku rooms of its kind. (d) and (e) are the two
    that matter: (d) because ADR 0034 leaves the norm's own ordering to be
    carried by the target, so a `part` row with no target has nothing carrying
    it; (e) because a licence stated as prose in an ADR is a licence no gate can
    read, which is the defect ADR 0034 was itself written to close.
    """
    az = doc["profiles"]["AZ"]["rooms"]
    mapping, areas = az["mapping"]["rooms"], az["areas_m2"]
    rm = az["mapping"]["referent_model"]
    medians = doc["ergonomic"]["corpus_medians"]
    published = set(rm["values"])

    # `hall`/`entrance_lobby`/`corridor` share a merged median ticket 31's split
    # made unusable; corpus_medians records it as an explicit null.
    median_key = {"hall": "hall_entrance_lobby_corridor",
                  "entrance_lobby": "hall_entrance_lobby_corridor",
                  "corridor": "hall_entrance_lobby_corridor"}

    def cell(key, tier):
        c = (areas.get(key) or {}).get(tier)
        return c["v"] if isinstance(c, dict) else None

    def rung2(erg_key):
        c = medians.get(median_key.get(erg_key, erg_key))
        return c["v"] if isinstance(c, dict) else None

    seen = {"room": 0, "part": 0, "undetermined": 0}
    rows_with_area = 0

    for key, row in mapping.items():
        guards = row["az_area"]
        if guards is None:
            continue
        rows_with_area += 1
        for g in guards:
            ref = g.get("referent")
            tag = f"{key}.az_area[when_otaq_count={g['when_otaq_count']}]"

            # -- R1 (a) every guard entry declares what its cell measures -----
            check(ref in published,
                  f"ADR 0034 (a) {tag} carries a published referent", str(ref))
            if ref in seen:
                seen[ref] += 1

            # -- R2 (b) an entailed sum only ever adds VERIFIED law -----------
            for extra in g.get("compose_with") or []:
                c = (areas.get(extra) or {}).get("statutory_floor")
                check(isinstance(c, dict) and c.get("v") is not None
                      and c.get("conf") == "verified",
                      f"ADR 0034 (b) {tag} compose_with {extra} is a verified, "
                      f"non-null statutory_floor",
                      "an entailed bound may never sum a derived or fitted cell")

            # -- R5 (e) the licence is a FIELD, and it governs the read -------
            lic = g.get("licence")
            if ref == "part":
                check(isinstance(lic, dict) and bool(lic.get("clause"))
                      and bool(lic.get("type_defined_as")),
                      f"ADR 0036 (e) {tag} names the clause whose type definition "
                      f"licenses the entailed read",
                      "a `part` read asserts the norm entails a bound on a room it "
                      "has a word for; where it has none, nothing is entailed")
            else:
                check(lic is None,
                      f"ADR 0036 (e) {tag} carries licence: null -- a {ref} read's "
                      f"authority is its own cell `ref`")

            if ref != "part":
                continue

            # -- R3 (c) a `part` read may floor and may NEVER target ----------
            # The cell keeps its market_default: it is a first-hand transcription
            # and real provenance. What is forbidden is READING it as the room's
            # target, so the gate binds the resolution rather than the datum.
            soft = cell(g["key"], "market_default")
            target = rung2(key)
            check(target is not None and (soft is None or target != soft),
                  f"ADR 0034 (c) {tag} resolves its target from the ladder, not "
                  f"from the `part` cell",
                  f"cell market_default {soft}, ladder rung 2 {target}")

            # -- R4 (d) EVERY `part` READ HAS A TARGET ------------------------
            # The load-bearing one. ADR 0034 leaves kitchen_dining's hard floor
            # at 6,0 -- BELOW the 8,0 a plain kitchen gets -- and has the target
            # carry the norm's ordering. With no target, nothing carries it.
            check(target is not None,
                  f"ADR 0034 (d) {tag} has a target from some rung of "
                  f"brief.md 9.2's ladder", f"resolved {target}")
            plain = cell(g["key"], "statutory_floor")
            check(plain is None or target > plain,
                  f"ADR 0034 (d) {tag} target {target} sits above its own "
                  f"entailed floor {plain}")

    # -- R6  the ADR's own published counts cannot go stale -----------------
    at = rm["counts_at_authoring"]
    check(sum(seen.values()) == at["guard_entries"] and rows_with_area == at["rows_with_az_area"]
          and seen["room"] == at["room"] and seen["part"] == at["part"]
          and seen["undetermined"] == at["undetermined"],
          "ADR 0034 referent_model.counts_at_authoring matches the file",
          f"file: {sum(seen.values())} entries over {rows_with_area} rows, "
          f"{seen}; recorded: {at['guard_entries']}/{at['rows_with_az_area']}, "
          f"room {at['room']} part {at['part']} undetermined {at['undetermined']}")


def resolver_gates(doc, check):
    """`profile_read` is the only reader of this file that sizes a room, so it is
    the one place a bug reaches geometry. Ticket 69.

    These do NOT import `experiments/warp/`: coupling a PROFILE gate to the
    solver toolchain would make this file fail when ortools moves. The rigs are
    bound by construction instead -- they hold no literals to check, because
    `MIN_SIDE`, `MARKET` and `ERG_AREA` are now this module's tables.
    """
    import profile_read as p

    inv = doc["ergonomic"]["rooms"]
    cat = doc["profiles"]["AZ"]["construction"]["catalogue"]

    # -- P1  the grid and t_int are READ, and agree with the catalogue ------
    check(p.T_INT_MM == cat["brick"]["t_int"]["v"],
          f"T69 profile_read.T_INT_MM {p.T_INT_MM} is the catalogue's t_int",
          "ADR 0007: the profile offers exactly one")
    check(p.GRID_MM == GRID, f"T69 profile_read.GRID_MM {p.GRID_MM} == {GRID}")

    # -- P2  every table is TOTAL over the bridge, so no default can fire ---
    ms, erg = p.min_side_table(), p.ergonomic_area_table()
    for lab in p.labels():
        check(lab in ms and lab in erg,
              f"T69 profile_read tables are total at corpus label {lab}")

    # -- P3  the derived table is the FORMULA, recomputed from the file -----
    for lab in p.labels():
        k = p.erg_key(lab)
        want = -(-(inv[k]["min_clear_short"]["v"] + p.T_INT_MM) // GRID)   # ceil
        check(ms[lab] == want,
              f"T69 MIN_SIDE[{lab}] = ceil((min_clear_short + t_int) / grid)",
              f"{ms[lab]} vs {want} from {inv[k]['min_clear_short']['v']} mm")

    # -- P4  the transcribed table is the cell, unmodified ------------------
    for lab in p.labels():
        check(erg[lab] == inv[p.erg_key(lab)]["min_area"]["v"],
              f"T69 ERG_AREA[{lab}] is ergonomic.rooms.{p.erg_key(lab)}.min_area")

    # -- P5  the otaq guard is RESOLVED, and the otaq set is the file's -----
    # `absolute_area.HABITABLE` omitted DINING, whose counts_as_otaq is true, so
    # a living+dining dwelling counted one otaq and took the 15,0 floor where the
    # profile says 16,0. The set is now read; this holds it read.
    for k, node in inv.items():
        check(p.counts_as_otaq(k) == bool(node["counts_as_otaq"]),
              f"T69 profile_read.counts_as_otaq({k}) is the file's flag")
    check(p.statutory_floor_m2("living", 1) != p.statutory_floor_m2("living", 2),
          "T69 the when_otaq_count guard actually resolves",
          f"1 otaq {p.statutory_floor_m2('living', 1)}, "
          f"2+ {p.statutory_floor_m2('living', 2)}")

    # -- P6  ADR 0034 (c), enforced at the read rather than trusted ---------
    for k, row in doc["profiles"]["AZ"]["rooms"]["mapping"]["rooms"].items():
        for g in row["az_area"] or []:
            if g["referent"] != "part":
                continue
            soft = (doc["profiles"]["AZ"]["rooms"]["areas_m2"][g["key"]]
                    .get("market_default") or {}).get("v")
            for otaq in (None, 1, 2, 3):
                got = p.market_default_m2(k, otaq)
                check(got != soft or soft is None,
                      f"T69 market_default_m2({k}, otaq={otaq}) does not return the "
                      f"`part` cell {g['key']}", f"got {got}, part cell {soft}")

    # -- P7  a label the bridge does not define RAISES, never defaults ------
    try:
        p.erg_key("NOT_A_LABEL")
        check(False, "T69 an unmapped corpus label raises rather than defaulting")
    except KeyError:
        check(True, "T69 an unmapped corpus label raises rather than defaulting")

    # -- C1  no consumer re-introduces a copy -------------------------------
    # The one check that binds the RIGS without importing them. It gates the
    # SHAPE of the defect rather than its values: a table of profile numbers
    # written as a literal beside the file that publishes them. That shape is
    # how MARKET drifted four cells behind ADR 0035 in a day, how MIN_SIDE lost
    # KITCHEN_DINING, and how HABITABLE came to omit DINING. Cheap, exact on
    # these names, and it fails the moment the pattern comes back.
    COPY = re.compile(r"^\s*(MIN_SIDE|MARKET|ERG_AREA|STAT_FLOOR|STAT_FLOOR_LENIENT"
                      r"|HABITABLE|LIVING_FAMILY)\s*=\s*[\{\(]", re.M)
    warp = DATA.parents[2] / "experiments/warp"
    for f in sorted(warp.glob("*.py")):
        hits = COPY.findall(f.read_text(encoding="utf-8"))
        check(not hits,
              f"T69 {f.name} holds no profile table as a literal",
              f"re-copied: {sorted(set(hits))} -- read it from profile_read instead")


# Ticket 80 -- the sleeping flag lands, and the one bit the others cannot supply.
#
# SLEEPING is zoning.md D2's node set and CONTEXT.md's Sleeping room; four of
# proposer.md section 6.1's five plan-quality terms and four of the five owed
# zone.* rules read it.  CIRCULATION exists because MEASUREMENT said it had to:
# `hall` and `storage` carry identical vectors over the six older flags and must
# land in different classes, so no precedence over those six separates them.
# That collision is why experiments/zoning/measure_zoning.py held a private
# corpus-label table, and Z9 below is the gate that stops the bit being
# "simplified" back out.
SLEEPING = {"bedroom_principal", "bedroom_double", "bedroom_single", "study"}
CIRCULATION = {"hall", "entrance_lobby", "corridor"}
# zoning.md section 5b says three.  It predates ADR 0022's nineteenth type.
PRIVATE_NOT_SLEEPING = {"bathroom", "bathroom_combined", "shower_room", "wc"}
OLD_FLAGS = ("is_habitable", "is_wet", "is_private", "needs_window",
             "counts_as_otaq", "brief_nameable")


def zoning_gates(doc, check):
    """Ticket 80 -- is_sleeping and is_circulation, and the identity that is NOT
    a derivation.

    Z5 is the load-bearing one and it is an AGREEMENT gate, the mirror of V6's
    divergence gate.  is_sleeping is exactly `is_habitable AND is_private` over
    the nineteen types that ship, and the flag is published anyway because
    flag_semantics calls these DEFINITIONS: the conjunction is a property of
    today's type set, not the meaning of the word.  A habitable private room
    that is not for sleeping -- a library, a home office that is not a study --
    breaks it, and this gate is where that gets decided rather than silently
    rezoning every plan.
    """
    rooms = doc["ergonomic"]["rooms"]

    # -- Z1/Z2  both flags present and boolean on every type ------------------
    for k, node in rooms.items():
        check(isinstance(node.get("is_sleeping"), bool),
              f"T80 {k}.is_sleeping present and boolean")
        check(isinstance(node.get("is_circulation"), bool),
              f"T80 {k}.is_circulation present and boolean")

    sleep = {k for k, n in rooms.items() if n.get("is_sleeping") is True}
    circ = {k for k, n in rooms.items() if n.get("is_circulation") is True}

    def flag(k, f):
        v = rooms[k][f]
        return bool(v["v"] if isinstance(v, dict) else v)

    # -- Z3/Z4  the two sets are exactly what CONTEXT.md and zoning.md name ---
    check(sleep == SLEEPING, "T80 is_sleeping is exactly the four sleeping types",
          f"got {sorted(sleep)}")
    check(circ == CIRCULATION,
          "T80 is_circulation is exactly hall, entrance_lobby, corridor",
          f"got {sorted(circ)}")

    # -- Z5  AGREEMENT, not derivation ---------------------------------------
    conj = {k for k in rooms if flag(k, "is_habitable") and flag(k, "is_private")}
    check(sleep == conj,
          "T80 is_sleeping AGREES with is_habitable AND is_private -- break this "
          "deliberately, never silently",
          f"sleeping-not-conjunction {sorted(sleep - conj)}, "
          f"conjunction-not-sleeping {sorted(conj - sleep)}")

    # -- Z6  the divergence from is_private is FOUR types, not section 5b's 3 -
    priv = {k for k in rooms if flag(k, "is_private")}
    check(priv - sleep == PRIVATE_NOT_SLEEPING,
          "T80 is_private diverges from is_sleeping on exactly the four wet "
          "private types (zoning.md 5b says three; it predates ADR 0022)",
          f"diverging: {sorted(priv - sleep)}")

    # -- Z7  a room is not both, and no sleeping room is wet (zoning.md D2) ---
    check(not (sleep & circ), "T80 no type is both sleeping and circulation",
          f"both: {sorted(sleep & circ)}")
    wet_sleep = {k for k in sleep if flag(k, "is_wet")}
    check(not wet_sleep,
          "T80 no sleeping type is wet -- the whole of zoning.md D2",
          f"wet and sleeping: {sorted(wet_sleep)}")

    # -- Z8  invariants a rule may rely on ------------------------------------
    for k in sorted(sleep):
        check(flag(k, "counts_as_otaq") and flag(k, "needs_window"),
              f"T80 {k} counts as otaq and needs a window")
    for k in sorted(circ):
        check(not flag(k, "is_habitable") and not flag(k, "counts_as_otaq"),
              f"T80 {k} is neither habitable nor an otaq")

    # -- Z9  is_circulation is LOAD-BEARING, and this is the proof ------------
    # If a later ticket "simplifies" the flag away, hall and storage merge and
    # the private table comes back.  Assert the collision exists and that only
    # the new bit resolves it.
    def vec(k):
        return tuple(flag(k, f) for f in OLD_FLAGS)
    check(vec("hall") == vec("storage"),
          "T80 hall and storage are IDENTICAL over the six older flags -- the "
          "measurement that made is_circulation necessary")
    check(flag("hall", "is_circulation") is not flag("storage", "is_circulation"),
          "T80 is_circulation is the only bit separating hall from storage")

    # -- Z10  no two types sharing an old-flag vector disagree on the new bits -
    # (i.e. the derived class partition is well defined on every collision set)
    groups = {}
    for k in rooms:
        groups.setdefault(vec(k), []).append(k)
    for v, ks in sorted(groups.items()):
        if len(ks) < 2:
            continue
        new = {(k in sleep, k in circ) for k in ks}
        check(len(new) == 1 or sorted(ks) == sorted(["hall", "storage"]),
              f"T80 collision set {sorted(ks)} is resolved by the new flags or "
              f"is the documented hall/storage split")


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
    # A LIST since *A statutory floor, posted soft, in the one region v1 ships*:
    # the hard floor is max(ergonomic, statutory_floor) and a profile may raise
    # it. Read as a scalar this crashes, which is how the amendment was noticed
    # here. Every named tier is checked, because ADR 0007's congruence binds each
    # hard number, not their maximum.
    hard_tiers = rules["tier_binding"]["hard_reject_below"]
    if isinstance(hard_tiers, str):
        hard_tiers = [hard_tiers]

    hard_in_profile = []
    for room, cells in az["rooms"]["clear_widths_mm"].items():
        if room == "comment":
            continue
        for tier in hard_tiers:
            cell = cells.get(tier)
            if cell and cell.get("v") is not None:
                hard_in_profile.append((f"{room}/{tier}", cell["v"]))
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
    print(f"hard tiers are {hard_tiers!r}")
    print(f"hard linear minima published by profile {PROFILE}: {len(hard_in_profile)}")

    # ---- where they really live ------------------------------------------
    # Only one member of hard_tiers is a top-level layer in this document; the
    # rest are per-profile cells, counted above. ADR 0009 exempts this one from
    # the congruence, which is why it is reported and not gated.
    invariant_tier = next((t for t in hard_tiers if t in doc), None)
    inv = doc.get(invariant_tier) if invariant_tier else None
    if not inv:
        print(f"  (none of {hard_tiers!r} is a layer in the file yet)")
        return 1 if fails else 0
    hard_tier = invariant_tier

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

    vocabulary_gates(doc, check)
    bridge_gates(doc, check)
    referent_gates(doc, check)
    resolver_gates(doc, check)
    zoning_gates(doc, check)

    if fails:
        print("\n".join(fails))
        print(f"\n{len(fails)} gate failure(s)")
        return 1
    if len(notes) < GATE_FLOOR:
        print(f"all {len(notes)} gates pass -- but GATE_FLOOR is {GATE_FLOOR}.")
        print(f"  {GATE_FLOOR - len(notes)} gate(s) have gone missing since the "
              f"floor was last set. `all N pass` is true of an empty file; that "
              f"is what this ratchet exists to catch.")
        print("  If the removal was deliberate, lower GATE_FLOOR and say which "
              "gates went and why.")
        return 1
    print(f"all {len(notes)} gates pass  (floor {GATE_FLOOR})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
