"""The H8 frontage budget — is a low-exposure Brief hard, or arithmetically dead?

H8 says every habitable room touches an exterior wall over a window's width.
Rooms do not overlap, so the stretches of exterior wall they occupy are
disjoint, and each habitable room consumes at least its own shorter minimum
dimension of exterior run. That gives a **necessary condition** with no search
in it at all:

    sum over habitable rooms of min(min_w, min_h)  <=  total exterior run

When it fails, no tiling of that Envelope can satisfy H8 — the Brief is dead
before the solver sees it, and no amount of solve time or Proposal quality can
help. When it holds, the Brief may still be infeasible for other reasons; the
condition is necessary, not sufficient.

This is the difference between "the solver is slow at low exposure" and
"single-aspect flats cannot have this many habitable rooms", and it is the
difference between a tuning problem and a product finding.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from geometry import EXPOSURE_PRESETS
from scenarios import GRID_MM, HABITABLE, STANDARDS, composition, envelope_for


def budget(n: int, exposure: str) -> dict:
    env = envelope_for(n, exposure)
    mix = composition(n)
    need = 0
    parts: List[Tuple[str, int]] = []
    for k in mix:
        if k in HABITABLE:
            mw, mh, _ = STANDARDS[k]
            c = min(mw, mh)
            need += c
            parts.append((k, c))
    have = sum(hi - lo for (_, _, lo, hi) in env.exterior_faces())
    return {
        "n": n,
        "exposure": exposure,
        "envelope": env.name,
        "exterior_fraction": round(env.exterior_fraction, 3),
        "habitable": len(parts),
        "need_mm": need * GRID_MM,
        "have_mm": have * GRID_MM,
        "slack_mm": (have - need) * GRID_MM,
        "possible": have >= need,
        "breakdown": parts,
    }


def table(counts=(4, 5, 6, 7, 8, 10, 12, 14, 16, 20, 24),
          presets=tuple(EXPOSURE_PRESETS)) -> List[dict]:
    return [budget(n, e) for e in presets for n in counts]


if __name__ == "__main__":
    counts = (4, 5, 6, 7, 8, 10, 12, 14, 16, 20, 24)
    presets = tuple(EXPOSURE_PRESETS)
    print("H8 frontage budget: habitable min-dimension sum vs exterior run\n")
    print(f"{'n':>3} {'hab':>4} {'need':>7} | " +
          " | ".join(f"{p[:13]:>13}" for p in presets))
    for n in counts:
        b0 = budget(n, presets[0])
        cells = []
        for p in presets:
            b = budget(n, p)
            mark = "ok " if b["possible"] else "DEAD"
            cells.append(f"{b['have_mm']:6d} {mark} {b['slack_mm']:+7d}".rjust(13))
        print(f"{n:>3} {b0['habitable']:>4} {b0['need_mm']:>7} | " + " | ".join(cells))
    print("\nnumbers are: exterior run available (mm), verdict, slack (mm)")
    print("`need` is the sum over habitable rooms of min(min_w, min_h).")
