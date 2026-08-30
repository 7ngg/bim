"""annotation.md §1.1 — every number goes through one formatter.

`DIMDSEP` is inert at `dimdec = 0`, so the separator's real consumers are the
strings *we* format: the room tag's area, the level mark, the schedule cells and
the preview's metre dimensions. Three call sites, one function — or the
convention silently never fires.

Integer millimetres contain no separator and are unaffected, which is why
§1's chain invariant is independent of locale.
"""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from . import profile


def num(value: float, dp: int, signed: bool = False) -> str:
    """A decimal number in the region profile's own convention.

    NEVER grouped: `thousands_separator` is null for AZ and CLDR gives `.` as
    the az group separator, so a grouped `4.400` reads as a decimal to the
    person the sheet is for.
    """
    grp = profile.thousands_separator()
    if grp:
        raise NotImplementedError(
            "thousands grouping is not implemented and AZ must never use it")
    # HALF-UP, not Python's round-half-even and not binary truncation.
    # annotation.md section 14 prints 4,935 as 4,94 and 3,885 as 3,89; a
    # formatter that gave 4,93 would put the schedule 0,01 out on two rows and
    # `draw.schedule_totals_close` would then be asserting the wrong column.
    q = Decimal(1).scaleb(-dp)
    d = Decimal(repr(abs(value))).quantize(q, rounding=ROUND_HALF_UP)
    s = f"{d:f}".replace(".", profile.decimal_separator())
    if signed:
        return ("±" if value == 0 else ("-" if value < 0 else "+")) + s
    return ("-" if value < 0 else "") + s


def area_m2(value_m2: float) -> str:
    """`15,66 m²` — 2 dp, §1.1's first row."""
    return f"{num(value_m2, 2)} m²"


def area_cell(value_m2: float) -> str:
    """A schedule cell: the number alone, 2 dp. §6's totals are computed from
    these PRINTED values, never from the exact ones."""
    return num(value_m2, 2)


def level(value_m: float = 0.0) -> str:
    """`t.d.s. ±0,000` — 3 dp per `AZS ГОСТ 21.101-2010` cl. 3.3.7."""
    return num(value_m, 3, signed=True)


def metre_dims(w_mm: int, h_mm: int) -> str:
    """The PREVIEW's dimension string, `4,35 × 3,60 m`. Rounded, therefore barred
    from any chain — §1's invariant."""
    return f"{num(w_mm / 1000.0, 2)} × {num(h_mm / 1000.0, 2)} m"


def mm_dims(w_mm: int, h_mm: int) -> str:
    """The SHEET's dimension string, `4350 × 3600`. Integer millimetres, no unit
    suffix, no separator — sums exactly, so a chain closes by construction."""
    return f"{int(w_mm)} × {int(h_mm)}"


def legs(rects_wh) -> str:
    """annotation.md §6/§7 — every leg of a Room, `4400 × 3400 + 2100 × 1800`,
    in descending area order. Never the bounding box."""
    ordered = sorted(rects_wh, key=lambda wh: -(wh[0] * wh[1]))
    return " + ".join(mm_dims(w, h) for w, h in ordered)


def parse_back(s: str) -> float:
    """Read a formatted number back. Used only by `check.schedule_totals_close`,
    which must add the PRINTED column."""
    return float(s.replace("±", "").replace(profile.decimal_separator(), "."))
