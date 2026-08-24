"""PROTOTYPE — pull the shipped fixture footprints and ergonomic minima into a
small JSON blob the prototype HTML can embed. No values are invented here.
"""
from __future__ import annotations
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "..", "data", "standards", "room-constraints.json")

d = json.load(open(SRC, encoding="utf-8"))
erg = d["ergonomic"]
az = d["profiles"]["AZ"]

def val(x):
    return x["v"] if isinstance(x, dict) and "v" in x else x

rooms = {}
for k, v in erg["rooms"].items():
    if not isinstance(v, dict):
        continue
    rooms[k] = {
        "min_short": val(v.get("min_clear_short")),
        "min_long": val(v.get("min_clear_long")),
        "min_area": val(v.get("min_area_mm2")),
        "note": (v.get("min_clear_short") or {}).get("note", ""),
    }

out = {
    "fixtures_mm": erg["fixtures_mm"]["values"],
    "fixtures_src": f'{erg["fixtures_mm"]["src"]} {erg["fixtures_mm"]["ref"]} ({erg["fixtures_mm"]["conf"]})',
    "body_zone": val(erg["body_zone"]),
    "rooms": rooms,
    "az_areas": az["rooms"].get("areas_m2"),
    "decimal_separator": val(az["drawing"]["decimal_separator"]),
    "drawing_language": val(az["drawing"]["language"]),
    "t_int": val(az["construction"].get("t_int_mm")) if "t_int_mm" in az.get("construction", {}) else None,
    "construction_keys": list(az.get("construction", {}).keys()),
}
json.dump(out, open(os.path.join(HERE, "standards.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(json.dumps({k: (v if not isinstance(v, dict) else list(v)[:8]) for k, v in out.items()},
                 ensure_ascii=False)[:1400])
