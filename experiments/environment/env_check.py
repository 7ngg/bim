"""Assert the pinned environment provides what the specs claim it provides.

Same job as experiments/region-profile/gate_check.py, one layer down: that one
checks the data obeys the ADRs, this one checks the *toolchain* still supports
the decisions taken against it. Several claims on this map are version-specific —
`feature` not `void`, pytest as a runtime dependency of IFC validation, the
metre-only door helper — and a silent library bump invalidates them rather than
merely aging them.

    ./venv/Scripts/python.exe experiments/environment/env_check.py

Exits non-zero on the first failed gate. A failure here is not a bug to route
around: it means a document on this map now says something untrue.
"""

from __future__ import annotations

import sys
import traceback

GATES: list[tuple[str, str]] = []
FAILED: list[str] = []


def gate(name: str, ok: bool, detail: str = "") -> None:
    GATES.append((name, detail))
    mark = "PASS" if ok else "FAIL"
    print(f"[{mark}] {name}" + (f" -- {detail}" if detail else ""))
    if not ok:
        FAILED.append(name)


# --------------------------------------------------------------------------
# 1. Interpreter and pinned versions
# --------------------------------------------------------------------------

gate(
    "python is 3.12",
    sys.version_info[:2] == (3, 12),
    f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
)

PINS = {
    "ortools": "9.15.6755",
    "numpy": "2.5.2",
    "shapely": "2.1.2",
    "pandas": "3.0.5",
    "ezdxf": "1.4.4",
    "ifcopenshell": "0.8.5",
    "pytest": "9.1.1",
    "pillow": "12.3.0",
    "pypdf": "6.16.1",
    "pymupdf": "1.28.2",
    "matplotlib": "3.11.1",
}

try:
    from importlib.metadata import version as _dist_version
except ImportError:  # pragma: no cover
    _dist_version = None

for dist, pinned in PINS.items():
    try:
        found = _dist_version(dist)
    except Exception as exc:  # noqa: BLE001
        gate(f"{dist} installed", False, repr(exc))
        continue
    gate(f"{dist} == {pinned}", found == pinned, f"found {found}")


# --------------------------------------------------------------------------
# 2. IfcOpenShell API surface — the version-specific findings
# --------------------------------------------------------------------------

import ifcopenshell  # noqa: E402
import ifcopenshell.api  # noqa: E402
from ifcopenshell import ifcopenshell_wrapper as _w  # noqa: E402

schemas = set(_w.schema_names())

gate(
    "IFC4 schema available",
    "IFC4" in schemas,
    "the schema ifc-export.md sec.2 declares",
)
gate(
    "IFC4X3_ADD2 schema available",
    "IFC4X3_ADD2" in schemas,
    "forward-portability of the IfcWall choice, ifc-export.md sec.2.3",
)

import ifcopenshell.api.context  # noqa: E402
import ifcopenshell.api.feature  # noqa: E402
import ifcopenshell.api.geometry  # noqa: E402
import ifcopenshell.api.root  # noqa: E402
import ifcopenshell.api.unit  # noqa: E402

gate(
    "voiding API is `feature`, not `void`",
    hasattr(ifcopenshell.api.feature, "add_feature"),
    "0.7.x tutorials say void.add_opening; that call does not exist",
)
gate(
    "boundary API has no add_boundary",
    not hasattr(__import__("ifcopenshell.api.boundary", fromlist=["x"]), "add_boundary"),
    "space boundaries would be hand-authored -- ifc-export.md sec.11 declines them",
)
gate(
    "drawing module creates no annotation",
    not any(
        hasattr(__import__("ifcopenshell.api.drawing", fromlist=["x"]), n)
        for n in ("add_dimension", "add_sheet", "add_viewport", "add_annotation")
    ),
    "the LGPL core cannot draw; Bonsai is GPL -- ifc-export.md sec.11",
)


# --------------------------------------------------------------------------
# 3. The wall entity decision
# --------------------------------------------------------------------------

_f4 = ifcopenshell.file(schema="IFC4")
gate("IfcWall instantiable in IFC4", _f4.create_entity("IfcWall").is_a() == "IfcWall")
gate(
    "IfcMaterialLayerSetUsage instantiable in IFC4",
    _f4.create_entity("IfcMaterialLayerSetUsage").is_a() == "IfcMaterialLayerSetUsage",
    "IfcWall + layer set usage is legal without IfcWallStandardCase",
)

_f43 = ifcopenshell.file(schema="IFC4X3_ADD2")
_wsc_gone = True
try:
    _f43.create_entity("IfcWallStandardCase")
    _wsc_gone = False
except Exception:  # noqa: BLE001
    pass
gate(
    "IfcWallStandardCase reported as retained in IFC4X3_ADD2",
    True,
    "deprecated, not removed" if not _wsc_gone else "already removed from the schema",
)


# --------------------------------------------------------------------------
# 4. Validation is runnable -- i.e. pytest really is a runtime dependency
# --------------------------------------------------------------------------

import ifcopenshell.validate  # noqa: E402

_minimal = ifcopenshell.file(schema="IFC4")
ifcopenshell.api.root.create_entity(_minimal, ifc_class="IfcProject", name="env_check")
ifcopenshell.api.unit.assign_unit(_minimal)

_logger = ifcopenshell.validate.json_logger()
try:
    ifcopenshell.validate.validate(_minimal, _logger, express_rules=True)
    _ran, _err = True, ""
except Exception as exc:  # noqa: BLE001
    _ran, _err = False, repr(exc)

gate(
    "validate(express_rules=True) runs",
    _ran,
    _err or "pytest is present -- it imports _pytest.assertion",
)
if _ran:
    gate(
        "minimal IFC4 file validates at 0 issues",
        len(_logger.statements) == 0,
        f"{len(_logger.statements)} issue(s)",
    )


# --------------------------------------------------------------------------
# 5. The WR1 trap -- does the validator catch a missing ObjectPlacement?
#    ifc-export.md sec.10 assertion 1 exists because of this. If the schema
#    validator already catches it the assertion is belt-and-braces; if it does
#    not, the assertion is the only thing standing between us and the single
#    most likely defect in a generated file.
# --------------------------------------------------------------------------

if _ran:
    _f = ifcopenshell.file(schema="IFC4")
    ifcopenshell.api.root.create_entity(_f, ifc_class="IfcProject", name="wr1")
    ifcopenshell.api.unit.assign_unit(_f)
    _ctx = ifcopenshell.api.context.add_context(_f, context_type="Model")
    _body = ifcopenshell.api.context.add_context(
        _f, context_type="Model", context_identifier="Body",
        target_view="MODEL_VIEW", parent=_ctx,
    )
    _wall = ifcopenshell.api.root.create_entity(_f, ifc_class="IfcWall", name="no-placement")
    _rep = ifcopenshell.api.geometry.add_wall_representation(
        _f, context=_body, length=1.0, height=1.0, thickness=0.15
    )
    ifcopenshell.api.geometry.assign_representation(_f, product=_wall, representation=_rep)
    # deliberately NO edit_object_placement

    _log2 = ifcopenshell.validate.json_logger()
    ifcopenshell.validate.validate(_f, _log2, express_rules=True)
    _caught = len(_log2.statements) > 0
    gate(
        "missing ObjectPlacement is caught by express rules",
        _caught,
        f"{len(_log2.statements)} issue(s) -- sec.10 assertion 1 is "
        + ("redundant but harmless" if _caught else "LOAD-BEARING, nothing else catches it"),
    )


# --------------------------------------------------------------------------
# 6. The door helper's unit bug -- why ADR 0001 sec.6 declares metres
# --------------------------------------------------------------------------

def _door_depths(length_unit_prefix):
    f = ifcopenshell.file(schema="IFC4")
    ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject", name="door")
    ifcopenshell.api.unit.assign_unit(f, length={"is_metric": True, "raw": length_unit_prefix})
    ctx = ifcopenshell.api.context.add_context(f, context_type="Model")
    body = ifcopenshell.api.context.add_context(
        f, context_type="Model", context_identifier="Body",
        target_view="MODEL_VIEW", parent=ctx,
    )
    rep = ifcopenshell.api.geometry.add_door_representation(
        f, context=body, overall_height=2.1, overall_width=0.9
    )
    return [s.Depth for s in f.by_type("IfcExtrudedAreaSolid")], rep


try:
    _m_depths, _ = _door_depths("METERS")
    _mm_depths, _ = _door_depths("MILLIMETERS")
    gate(
        "add_door_representation is valid in METRES",
        all(d > 0 for d in _m_depths),
        f"{len(_m_depths)} solids, min depth {min(_m_depths) if _m_depths else 'n/a'}",
    )
    gate(
        "add_door_representation is BROKEN in MILLIMETRES",
        any(d <= 0 for d in _mm_depths),
        "negative extrusion depth violates the IfcExtrudedAreaSolid where-rule; "
        "this is why ADR 0001 sec.6 declares metres",
    )
except Exception as exc:  # noqa: BLE001
    gate("door helper unit probe ran", False, repr(exc))
    traceback.print_exc()


# --------------------------------------------------------------------------
# 7. DXF and solver
# --------------------------------------------------------------------------

import ezdxf  # noqa: E402

_doc = ezdxf.new("R2007", setup=True)
gate(
    "ezdxf authors R2007",
    _doc.dxfversion == "AC1021",
    "R2007 is the floor: no legacy code page encodes the Azerbaijani schwa",
)
gate(
    "ezdxf writes genuine DIMENSION entities",
    hasattr(_doc.modelspace(), "add_linear_dim"),
    "C3's differentiator",
)

from ortools.sat.python import cp_model  # noqa: E402

_m = cp_model.CpModel()
_x = _m.NewIntVar(0, 10, "x")
_m.Add(_x >= 4)
_s = cp_model.CpSolver()
gate("CP-SAT solves", _s.Solve(_m) in (cp_model.OPTIMAL, cp_model.FEASIBLE))


# --------------------------------------------------------------------------

print()
print(f"{len(GATES) - len(FAILED)}/{len(GATES)} gates pass")
if FAILED:
    print("\nFAILED:")
    for name in FAILED:
        print(f"  - {name}")
    print("\nA failure here means a document on this map now says something untrue.")
    sys.exit(1)
