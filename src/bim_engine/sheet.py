"""docs/spec/annotation.md sections 9 and 10 -- sheet, scale, and sheet furniture.

SCALE IS HELD; THE SHEET GROWS. 1:50 is the residential GA scale, and dropping
to 1:100 to keep a plan on A3 is a printing decision masquerading as a drawing
decision. The ladder is three lines and the top two rungs are unreachable at v1
sizes -- an A1 selection is a signal that something upstream produced a dwelling
outside the promised envelope.

THE SET MARK IS `MH` AND THE SHEETS ARE NUMBERED WITHIN IT. SPDS carries the
designation on the SET and numbers sheets 1..N; NCS puts a discipline letter and
a series number on each sheet. So `A-101`/`A-102` do not become `MH-101`/`MH-102`
-- they become `<job>-MH`, *Vərəq 1* and *Vərəq 2*.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional, Tuple

from . import fmt, profile
from .dimensions import Dimensions
from .model import Plan

#: (name, width, height) in paper millimetres, landscape.
SHEETS = {"A3": (420.0, 297.0), "A2": (594.0, 420.0), "A1": (841.0, 594.0)}
LADDER = (("A3", 50), ("A2", 50), ("A1", 50), ("A1", 100))

MARGIN = 10.0
TITLE_STRIP = 40.0
TEXT_ALLOWANCE = 4.0        # one text height beyond the outermost rung


@dataclass
class Sheet:
    size: str
    scale: int
    width: float
    height: float
    printable: Tuple[float, float]
    extent_paper: Tuple[float, float]
    origin: Tuple[float, float] = (0.0, 0.0)   # paper position of model (0,0)


def printable(size: str) -> Tuple[float, float]:
    w, h = SHEETS[size]
    return (w - 2 * MARGIN - TITLE_STRIP, h - 2 * MARGIN)


def outermost_rung(dims: Dimensions) -> float:
    return max([c.rung for c in dims.chains] +
               [r.rung for r in dims.runnings] + [0.0])


def choose(plan: Plan, dims: Dimensions, footprint_mm: Tuple[int, int]) -> Sheet:
    """Take the first combination whose ANNOTATED extent fits the printable area.

    Annotated extent = footprint grown on each side by that side's outermost
    occupied rung plus one text height -- section 9, and section 14's own
    arithmetic: 8150 + 2 x (26 + 4) x 50 = 11 150 mm = 223 paper at 1:50.
    """
    rung = outermost_rung(dims) + TEXT_ALLOWANCE
    for size, scale in LADDER:
        ew = footprint_mm[0] / scale + 2 * rung
        eh = footprint_mm[1] / scale + 2 * rung
        pw, ph = printable(size)
        if ew <= pw and eh <= ph:
            w, h = SHEETS[size]
            return Sheet(size, scale, w, h, (pw, ph), (ew, eh))
    size, scale = LADDER[-1]
    w, h = SHEETS[size]
    ew = footprint_mm[0] / scale + 2 * rung
    eh = footprint_mm[1] / scale + 2 * rung
    return Sheet(size, scale, w, h, printable(size), (ew, eh))


# ---------------------------------------------------------------------------
# Title block -- section 10
# ---------------------------------------------------------------------------
def title_attribs(plan: Plan, sheet: Sheet, job: Dict[str, str],
                  n: int, of: int) -> Dict[str, str]:
    """`CHECKED` is deliberately present and deliberately empty. A generated
    drawing has not been checked by anyone, and a title block that omits the
    field implies a process that does not exist here."""
    return {
        "PROJECT": job.get("project", plan.name),
        "CLIENT": job.get("client", "—"),
        "DATE": job.get("date", date.today().isoformat()),
        "DRAWING": "%s-MH" % job.get("job", "BE"),
        "SHEET": "Vərəq %d / %d" % (n, of),
        "DRAWN": job.get("drawn", "bim-engine"),
        "CHECKED": "—",
        "SCALE": "M 1:%d" % sheet.scale,
        "SIZE": sheet.size,
        "REV": job.get("rev", "A"),
        "STATUS": "İLKİN — TİKİNTİ ÜÇÜN DEYİL",
        "UNITS": "Bütün ölçülər millimetrlədir",
        "DIM-CONV": ("Ölçülər təmiz divar üzlərinədir. Ümumi ölçü xarici "
                     "divarların xarici üzünə, qonşu divarların daxili üzünə."),
        "AREAS": ("ümumi sahə — Qaydalar b. 3.8, b. 3.2-yə görə təmiz üzlər "
                  "arasında, döşəmə səviyyəsində, plintuslar çıxılmaqla"),
    }


# ---------------------------------------------------------------------------
# General notes -- section 10, generated and not authored
# ---------------------------------------------------------------------------
def general_notes(plan: Plan) -> List[str]:
    t_ext = profile.T_EXT_MM
    notes = [
        "1. Bütün ölçülər millimetrlədir. Bu çertyojdan ölçü götürməyin.",
        "2. Ölçülər, əks göstərilməyibsə, təmiz divar üzlərinədir. Ümumi "
        "ölçülər xarici divarların xarici üzünə, qonşu divarların daxili "
        "üzünə verilir.",
        "3. Bütün arakəsmələr %d mm. Xarici divarlar %d mm. Qonşu divarlar "
        "%d mm." % (profile.T_INT_MM, t_ext, profile.T_PARTY_MM),
        "4. t.d.s. %s. Təmiz tavan hündürlüyü %d mm."
        % (fmt.level(0.0), profile.H_CLEAR_MM),
        "5. Sahələr ümumi sahə qaydasına görə, təmiz divar üzlərinə, döşəmə "
        "səviyyəsində, plintuslar çıxılmaqla ölçülüb (Qaydalar b. 3.8, b. 3.2).",
        "6. Bütün daxili açırımlar rəflə tərəfdəki perpendikulyar divarın "
        "təmiz üzündən 100 mm məsafədə yerləşdirilib, ölçüdə göstərildiyi kimi.",
        "7. Yanğın, istilik, akustika və konstruksiya göstəriciləri "
        "verilmir.",
        "8. Neufert səviyyəsində ölçü standartlarına uyğun hazırlanıb. "
        "HEÇ BİR TİKİNTİ NORMASINA UYĞUNLUQ YOXLANMAYIB. TİKİNTİ ÜÇÜN VƏ "
        "EKSPERTİZAYA TƏQDİM ÜÇÜN DEYİL.",
    ]
    if any(s.key == "living_dining_kitchen" for s in plan.spaces):
        notes.append(
            "9. Bu mətbəx qonaq otağına açıqdır; elektrik plitəsi nəzərdə "
            "tutulmalıdır.")
    return notes
