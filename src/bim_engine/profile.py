"""The region profile, READ. Never transcribed.

`data/standards/room-constraints.json` is the only source of a dimensional
constant in this package. Ticket 69's finding applies with full force to a
drawing layer: a hand copy of `t_int` here would be the eleventh copy of a class
that had already drifted once.

`experiments/region-profile/profile_read.py` is the same idea one layer up and
this file deliberately does not import it — that directory is an experiment and
`src/` may not depend on one. The two read the same cells and
`selftest.py::test_profile_agrees` asserts they agree.
"""
from __future__ import annotations

import json
import pathlib
from functools import lru_cache

DATA = pathlib.Path(__file__).resolve().parents[2] / "data/standards/room-constraints.json"
PROFILE = "AZ"


@lru_cache(maxsize=1)
def _doc() -> dict:
    return json.loads(DATA.read_text(encoding="utf-8"))


def _v(cell):
    """A profile cell is `{v, src, ref, conf, note}` or a bare value."""
    return cell["v"] if isinstance(cell, dict) and "v" in cell else cell


def _az() -> dict:
    return _doc()["profiles"][PROFILE]


def _erg() -> dict:
    return _doc()["ergonomic"]["rooms"]


# ---------------------------------------------------------------------------
# Construction — ADR 0010's layer-set TOTALS. Nothing here consumes a component.
# ---------------------------------------------------------------------------
def _brick() -> dict:
    return _az()["construction"]["catalogue"]["brick"]


GRID_MM: int = _az()["construction"]["residue_class_mod_grid"]["grid_mm"]
T_INT_MM: int = _az()["construction"]["residue_class_mod_grid"]["t_int_mm"]
T_PARTY_MM: int = _v(_brick()["t_party"])
T_EXT_MM: int = _v(_brick()["t_ext_total"])
T_FINISH_MM: int = _v(_brick()["t_finish"])

#: ADR 0012's single vertical datum, `clear_heights_mm.habitable_room_and_kitchen`.
H_CLEAR_MM: int = _v(_az()["rooms"]["clear_heights_mm"]["habitable_room_and_kitchen"])

#: annotation.md §3.2 — every thickness TOTAL must be even, because ADR 0001
#: halves it. Asserted here rather than trusted, because this is the one module
#: that reads all three.
for _name, _t in (("t_int", T_INT_MM), ("t_party", T_PARTY_MM), ("t_ext", T_EXT_MM)):
    if _t % 2:
        raise ValueError(f"{_name} = {_t} is odd; annotation.md §3.2 forbids it")


# ---------------------------------------------------------------------------
# The ergonomic layer — region-free flags the placement rules key off.
# ---------------------------------------------------------------------------
def is_habitable(key: str) -> bool:
    return bool(_v(_erg()[key]["is_habitable"]))


def is_private(key: str) -> bool:
    return bool(_v(_erg()[key]["is_private"]))


def is_wet(key: str) -> bool:
    return bool(_v(_erg()[key]["is_wet"]))


def needs_window(key: str) -> bool:
    """openings.md §6.2 made `kitchen` true. Read, not assumed."""
    return bool(_v(_erg()[key]["needs_window"]))


def counts_as_otaq(key: str) -> bool:
    return bool(_v(_erg()[key]["counts_as_otaq"]))


def erg_keys() -> list:
    return list(_erg())


# ---------------------------------------------------------------------------
# The corpus bridge — swiss_dwellings label -> ergonomic key.
# ---------------------------------------------------------------------------
def _bridge() -> dict:
    return _doc()["ergonomic"]["corpus_label_map"]


def collapse() -> dict:
    return {k: v for k, v in _bridge()["collapse"].items() if k != "comment"}


def erg_key(label: str, lenient: bool = False) -> str:
    label = collapse().get(label, label)
    row = _bridge()["labels"].get(label)
    if row is None:
        raise KeyError(f"corpus label {label!r} is not in ergonomic.corpus_label_map")
    return row["erg_lenient"] if (lenient and row["erg_lenient"]) else row["erg"]


# ---------------------------------------------------------------------------
# Names — annotation.md §7. Eighteen sourced rows; never translated here.
# ---------------------------------------------------------------------------
def name_az(key: str) -> str:
    return _v(_az()["rooms"]["mapping"]["rooms"][key]["name_az"])


def name_az_conf(key: str) -> str:
    cell = _az()["rooms"]["mapping"]["rooms"][key]["name_az"]
    return cell.get("conf", "unknown") if isinstance(cell, dict) else "unknown"


# ---------------------------------------------------------------------------
# Openings — the catalogue, the door map, the window series.
# ---------------------------------------------------------------------------
def _openings() -> dict:
    return _az()["openings"]


def catalogue(entry: str) -> dict:
    return _openings()["catalogue"][entry]


def door_entry_for(key: str) -> str:
    """openings.md §2.1, keyed by the RECEIVING Room. Raises on a room type the
    map does not carry — §9's rule that a new type arrives with a mapping row."""
    m = _openings()["door_for_room"]["map"]
    if key not in m:
        raise KeyError(f"no door_for_room row for {key!r} (openings.md §2.1/§9)")
    return m[key]


def window_height_mm(key: str) -> int:
    return _openings()["window_for_room"]["height_by_family"][key]


def width_series_mm() -> list:
    return list(_openings()["width_series_mm"]["v"])


def width_series_published_through() -> int:
    return _openings()["width_series_mm"]["published_through"]


HEAD_DATUM_MM: int = _v(_openings()["head_datum_mm"])
MIN_PIER_MM: int = _v(_openings()["min_pier_mm"])

#: openings.md §3.2, both from the acceptance bar's own constants.
JAMB_RETURN_MM = 100
LEADING_EDGE_NIB_MM = 300
NIB_DEPTH_MM = 1200


def glazing_hard_floor() -> float:
    """`win.area_ratio`, AzDTN 2.7-2 cl. 9.13. HARD."""
    return float(_v(_az()["windows"]["area_ratio"]))


def glazing_soft_target() -> float:
    return float(_v(_az()["windows"]["area_ratio_soft_target"]))


# ---------------------------------------------------------------------------
# Drawing — §1.1's formatter reads its separators from here and nowhere else.
# ---------------------------------------------------------------------------
def decimal_separator() -> str:
    return _v(_az()["drawing"]["decimal_separator"])


def thousands_separator():
    """`null` for AZ and it must stay null: CLDR gives `.` as the az group
    separator, so a grouped 4.400 reads as a decimal. annotation.md §1.1."""
    return _v(_az()["drawing"]["thousands_separator"])


def language() -> str:
    return _v(_az()["drawing"]["language"])


def area_convention_id() -> str:
    return _az()["area_convention"]["id"]
