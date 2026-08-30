"""docs/spec/annotation.md section 6 -- the three drawn schedules on sheet 2.

Our columns diverge from the published form and the divergence is chosen:
`AZS ГОСТ 21.501-2010` cl. 2.3.6(2) defers to `ГОСТ 21.101` Annex 7, whose
columns carry the opening size in a NOTES column and add a mass column we cannot
populate. We put the size in its own column and carry no mass. Column headings
are Azerbaijani and use Elave D's published abbreviations.

EVERY PRINTED TOTAL IS COMPUTED FROM THE PRINTED CELLS. Areas render to 2 dp and
a sum of rounded values is not the rounded sum -- section 14's five rooms are
exactly 43,575 m2, which renders as 43,58 while the five printed cells add to
43,59. A Practitioner adds that column, and a totals row that disagrees with the
column above it by 0,01 is the same failure class as a chain that does not close.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from . import fmt, openings as op_mod, profile
from .model import Opening, Plan

EMDASH = "—"


@dataclass
class Table:
    title: str
    headers: List[str]
    rows: List[List[str]]
    notes: List[str] = field(default_factory=list)


def _handing(op: Opening) -> str:
    """Handing is READ OFF the position, never chosen -- which is what keeps the
    schedule's Handing column and the plan's swing arc from being two
    independent decisions that can disagree (openings.md section 4.1)."""
    if op.kind == "cased_opening":
        return EMDASH
    return "sol" if op.hinge_end == "lo" else "sağ"


def _swing(plan: Plan, op: Opening) -> str:
    if op.kind == "cased_opening":
        return EMDASH
    if op.swing_side is None:
        return EMDASH
    try:
        into = op.receiving if op.swing_side == op_mod._side_of_space(
            plan, op, op.receiving) else op.other
    except Exception:
        into = op.receiving
    return plan.by_ref(into).name_az if into else EMDASH


def door_schedule(plan: Plan) -> Table:
    rows = []
    for op in plan.openings:
        if not op.is_door:
            continue
        cat = profile.catalogue(op.catalogue) if op.catalogue else None
        typ = cat["v"] if cat else EMDASH
        leaf = (EMDASH if op.leaf_w is None
                else fmt.mm_dims(op.leaf_w, cat["leaf_h"] if cat else 2000))
        note = "giriş qapısı" if op.kind == "entrance_door" else (
            "şüşəli" if op.glazed else "")
        rows.append([op.mark, typ, fmt.mm_dims(op.width, op.height_mm), leaf,
                     _handing(op), _swing(plan, op), note])
    return Table("QAPI CƏDVƏLİ",
                 ["Marka", "Tip", "Tikinti açırımı En × Hün.",
                  "Qapı taxtası En × Hün.", "Yönü", "Açılır", "Qeyd"],
                 rows)


def window_schedule(plan: Plan) -> Table:
    rows = []
    for op in plan.openings:
        if op.kind != "window":
            continue
        rows.append([op.mark, op.catalogue,
                     fmt.mm_dims(op.width, op.height_mm),
                     str(op_mod.sill_mm(op)),
                     EMDASH,                      # fall barrier: see below
                     plan.by_ref(op.host_space).name_az])
    return Table("PƏNCƏRƏ CƏDVƏLİ",
                 ["Marka", "Tip", "Tikinti açırımı En × Hün.",
                  "Pəncərəaltı hün.", "Mühafizə", "Otaq"],
                 rows,
                 notes=["Mühafizə hündürlüyü verilmir: layihədə bir mərtəbə "
                        "var və sahə modelləşdirilmir."])


def room_schedule(plan: Plan) -> Table:
    """`Clear dimensions` carries EVERY leg in descending area order; `Area` is
    the Room's over the union. The two columns are not multiplicands of each
    other for an L and are not meant to be."""
    rows = []
    printed = []
    for s in plan.spaces:
        cell = fmt.area_cell(s.area_m2)
        printed.append(fmt.parse_back(cell))
        rows.append([s.ref, s.name_az, fmt.legs([(p.w, p.h) for p in s.parts]),
                     cell])
    total_spaces = fmt.area_cell(sum(printed))
    total_inner = fmt.area_cell(plan.interior_m2)
    diff = fmt.area_cell(fmt.parse_back(total_inner) - fmt.parse_back(total_spaces))
    rows.append(["", "CƏMİ (ümumi sahə)", "", total_spaces])
    rows.append(["", "Mərtəbənin daxili sahəsi", "", total_inner])
    rows.append(["", "Daxili arakəsmələrin sahəsi", "", diff])
    return Table("OTAQ CƏDVƏLİ", ["İşarə", "Otaq", "Təmiz ölçülər", "Sahə, m²"],
                 rows,
                 notes=["Sahələr ümumi sahə qaydasına görə ölçülüb "
                        "(Qaydalar, b. 3.8 və 3.2)."])


def totals_close(plan: Plan) -> bool:
    """`draw.schedule_totals_close` -- the area analogue of `chain_closes`, and
    the only Drawing predicate whose failure is invisible in the geometry and
    visible only to a person adding a column."""
    t = room_schedule(plan)
    body = t.rows[:-3]
    printed_sum = sum(fmt.parse_back(r[3]) for r in body)
    stated = fmt.parse_back(t.rows[-3][3])
    inner = fmt.parse_back(t.rows[-2][3])
    diff = fmt.parse_back(t.rows[-1][3])
    return (abs(printed_sum - stated) < 5e-3
            and abs((inner - stated) - diff) < 5e-3)
