"""The ergonomic layer, asserted against its consumer.

*Ergonomic minima and the constraint table's missing half* was told to "cross-check
every value against `data/acceptance/rules.json`: the registry is the consumer, and
any minimum it cannot read is a rule that silently does not fire." This is that
check, kept as an assertion rather than a claim -- the same move `gate_check.py`
makes for the region-profile ship gates.

Run:  python experiments/region-profile/ergonomic_check.py
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
STANDARDS = ROOT / "data/standards/room-constraints.json"
RULES = ROOT / "data/acceptance/rules.json"

fails, passes = [], []


def check(ok, label, detail=""):
    (passes if ok else fails).append(
        f"{'PASS' if ok else 'FAIL'}  {label}" + (f"  -- {detail}" if detail else ""))


def resolve(doc, pointer):
    """Resolve a JSON pointer, treating a {placeholder} segment as a wildcard."""
    node = doc
    for seg in pointer.split("/")[1:]:
        if seg.startswith("{") and seg.endswith("}"):
            if not isinstance(node, dict) or not node:
                return None
            node = next(iter(node.values()))
            continue
        if not isinstance(node, dict) or seg not in node:
            return None
        node = node[seg]
    return node


def main():
    std = json.loads(STANDARDS.read_text(encoding="utf-8"))
    rules = json.loads(RULES.read_text(encoding="utf-8"))
    erg = std["ergonomic"]
    rooms = erg["rooms"]
    by_id = {r["id"]: r for r in rules["rules"]}

    # ---- the layer is internally consistent ------------------------------
    for name, r in rooms.items():
        s, lg = r["min_clear_short"]["v"], r["min_clear_long"]["v"]
        area = r["min_area"]["v"]
        check(s <= lg, f"{name}: short <= long", f"{s} > {lg}")
        packings = r.get("packings_mm")
        if packings:
            # A composite minimises the three fields over its packings
            # independently, so min_area may exceed short x long -- that is what
            # excludes the corner of the box no packing occupies. The property
            # that must hold is that every packing clears all three rules.
            for ps, pl in packings:
                ps, pl = min(ps, pl), max(ps, pl)
                check(ps >= s and pl >= lg and ps * pl / 1e6 >= area - 1e-9,
                      f"{name}: packing {ps}x{pl} clears its own envelope",
                      f"vs short {s}, long {lg}, area {area}")
        else:
            check(area <= s * lg / 1e6 + 1e-9,
                  f"{name}: min_area does not reject its own rectangle",
                  f"{area} m2 > {s}x{lg}")
        check(round(area, 1) == area, f"{name}: area is one decimal", str(area))
        for field in ("min_clear_short", "min_clear_long", "min_area"):
            cell = r[field]
            check(all(k in cell for k in ("v", "src", "ref", "conf")),
                  f"{name}.{field} carries provenance per value_format")
        for flag in ("is_habitable", "is_wet", "is_private", "needs_window"):
            check(isinstance(r.get(flag), bool), f"{name}.{flag} is present")
        check(not r["is_habitable"] or r["needs_window"] or name == "kitchen",
              f"{name}: needs_window follows is_habitable (kitchen excepted)")

    # ---- every consumer can read what it consumes ------------------------
    for rid in ("dim.min_area", "dim.min_clear_width", "dim.min_clear_depth"):
        rule = by_id[rid]
        check(rule.get("conf") != "pending", f"{rid} is no longer pending")
        ptr = rule.get("value_source", "")
        check(ptr.startswith("data/standards/room-constraints.json#"),
              f"{rid} names its value source")
        check(resolve(std, ptr.split("#", 1)[1]) is not None,
              f"{rid} value_source resolves", ptr)

    for rid, flag in (("circ.no_private_transit", "is_private"),
                      ("win.habitable_has_window", "needs_window"),
                      ("win.habitable_touches_exterior", "is_habitable"),
                      ("wet.plumbing_group_count", "is_wet")):
        ptr = by_id[rid].get("flag_source", "")
        check(resolve(std, ptr.split("#", 1)[1]) is not None if "#" in ptr else False,
              f"{rid} flag_source resolves", ptr or "(absent)")

    check(not [r for r in rules["rules"] if r.get("conf") == "pending"],
          "rules.json carries no pending rules")
    check(rules["tier_binding"]["hard_reject_below"]
          == std["tier_model"]["validator_binding"]["hard_reject_below"],
          "both files name the same hard tier",
          f'{rules["tier_binding"]["hard_reject_below"]!r} vs '
          f'{std["tier_model"]["validator_binding"]["hard_reject_below"]!r}')

    # ---- sources with no machine-readable citation -----------------------
    # INFORMATIONAL, never a failure. This ticket owned exactly one orphan --
    # `de_baybo`, which *The Azerbaijani region profile* closed by re-sourcing its
    # consumers, so the block was withdrawn rather than added. A general audit is
    # not this check's business and could not be trusted anyway: a source may be
    # cited from prose or from a findings document, neither of which is scanned
    # here, so "no citation found" is not evidence of an orphan.
    cited = {r.get("src") for r in rules["rules"]} | {
        c.get("src") for prof in std.get("profiles", {}).values()
        if isinstance(prof, dict) for c in _cells(prof)}
    uncited = sorted(k for k in std["sources"] if k not in cited)
    check("de_baybo" not in std["sources"],
          "de_baybo is not carried as an uncited source")

    # ---- the corridor rule and the hall floor agree ----------------------
    check(by_id["dim.corridor_min_width"]["value"]
          <= rooms["hall"]["min_clear_short"]["v"],
          "dim.corridor_min_width does not exceed the hall ergonomic floor")

    for line in passes:
        print(" ", line)
    for line in fails:
        print(" ", line)
    print(f"\n{len(passes)} checks pass, {len(fails)} fail")
    return 1 if fails else 0


def _cells(node):
    """Every dict in the tree that looks like a provenance-carrying value."""
    if isinstance(node, dict):
        if "src" in node and "v" in node:
            yield node
        for v in node.values():
            yield from _cells(v)
    elif isinstance(node, list):
        for v in node:
            yield from _cells(v)


if __name__ == "__main__":
    sys.exit(main())
