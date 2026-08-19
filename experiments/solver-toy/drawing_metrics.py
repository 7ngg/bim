"""Drawing measurements taken off a solved Plan — ticket 15's third axis.

`docs/spec/annotation.md` fixes the tiers, the narrow-tick rule and the sheet
ladder, and works one five-room example by hand. Nothing above five rooms has
ever been measured, so the sheet ladder's top rungs are untested and nobody
knows how crowded a tier-2 chain gets at 24 rooms.

These are pure post-processing over the rects the solver already returned. No
extra solving, and no drawing is produced: the point is the counts.

Coordinates
-----------
The toy solves in grid units and its rooms tile exactly, which under ADR 0001
is precisely the **solve domain** — the interior clear region dilated outward by
`t_int/2`. So the mapping to the spec's coordinates is direct:

    solve domain  = [0, 250*W] x [0, 250*H]  mm
    Envelope inner= that eroded by t_int/2, so 250*W - t_int wide
    clear rect    = erode(solved rect, t_int/2)

which reproduces the worked example exactly: 8000 x 6000 solve domain at
`t_int = 100` gives the stated 7900 x 5900 inner region.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from geometry import Envelope, Rect

GRID_MM = 250

# annotation.md 9: ISO 3098 only. Dimension text is 2.5 mm paper.
TEXT_H = 2.5
# Fitted to the spec's own worked example, which calls a three-digit dimension
# at 2.5 mm "~7 mm of text": 3 * 2.5 * 0.9 = 6.75.
CHAR_W = 0.9
DIMGAP = 0.625                       # annotation.md 11, s.dxf.dimgap

# annotation.md 4: rung offsets in paper mm, allocated outward.
RUNG_TIER3 = 10.0
RUNG_TIER2 = 18.0
RUNG_TIER2B = 26.0
RUNG_TIER1_NO_2B = 26.0
RUNG_TIER1_WITH_2B = 34.0
# The worked example grows the footprint by `rung + 4` per side.
EXTENT_TEXT_PAD = 4.0

# annotation.md 14 inputs.
T_EXT = 300
T_PARTY = 200

# annotation.md 9: landscape, 10 mm margins, 40 mm title strip on the right.
SHEETS = {"A3": (420, 297), "A2": (594, 420), "A1": (841, 594)}
LADDER = (("A3", 50), ("A2", 50), ("A1", 50), ("A1", 100))


def printable(sheet: str) -> Tuple[float, float]:
    w, h = SHEETS[sheet]
    return w - 20 - 40, h - 20


def text_width(value_mm: int) -> float:
    return len(str(int(value_mm))) * TEXT_H * CHAR_W


# ---------------------------------------------------------------------------
# Walls
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WallRun:
    """A maximal straight internal wall run, in grid units (ADR 0001)."""

    axis: str          # 'v' = constant x, 'h' = constant y
    coord: int
    lo: int
    hi: int


def _merge(spans: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    spans = sorted(spans)
    out: List[Tuple[int, int]] = []
    for lo, hi in spans:
        if out and lo <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], hi))
        else:
            out.append((lo, hi))
    return out


def wall_runs(rooms: Sequence[Rect]) -> List[WallRun]:
    """Every internal wall, as a maximal straight run.

    A wall separates a room pair; runs collinear and touching are one Wall, per
    the geometry model. Envelope boundary faces are excluded — they are the
    external wall, not a partition, and tier 2 dimensions partitions.
    """
    vert: Dict[int, List[Tuple[int, int]]] = {}
    horz: Dict[int, List[Tuple[int, int]]] = {}
    n = len(rooms)
    for i in range(n):
        for j in range(i + 1, n):
            a, b = rooms[i], rooms[j]
            if a.x2 == b.x1 or b.x2 == a.x1:
                x = a.x2 if a.x2 == b.x1 else b.x2
                lo, hi = max(a.y1, b.y1), min(a.y2, b.y2)
                if hi > lo:
                    vert.setdefault(x, []).append((lo, hi))
            if a.y2 == b.y1 or b.y2 == a.y1:
                y = a.y2 if a.y2 == b.y1 else b.y2
                lo, hi = max(a.x1, b.x1), min(a.x2, b.x2)
                if hi > lo:
                    horz.setdefault(y, []).append((lo, hi))
    runs: List[WallRun] = []
    for x, sp in vert.items():
        runs += [WallRun("v", x, lo, hi) for lo, hi in _merge(sp)]
    for y, sp in horz.items():
        runs += [WallRun("h", y, lo, hi) for lo, hi in _merge(sp)]
    return runs


# ---------------------------------------------------------------------------
# Tier 2 chains
# ---------------------------------------------------------------------------

SIDES = ("S", "N", "W", "E")


def chains(rooms: Sequence[Rect], env: Envelope, t_int: int = 100) -> Dict[str, dict]:
    """One tier-2 chain per bbox side, per annotation.md 4.2.

    A side's chain dimensions only the partition faces on walls that *reach*
    that side, so every tick is a real clear dimension of a real room. Each
    chain closes on the Envelope inner dimension for its axis.
    """
    runs = wall_runs(rooms)
    half = t_int // 2
    inner_x = env.W * GRID_MM - t_int
    inner_y = env.H * GRID_MM - t_int
    out: Dict[str, dict] = {}
    reaching: Dict[str, List[WallRun]] = {s: [] for s in SIDES}

    for r in runs:
        if r.axis == "v":
            if r.lo == 0:
                reaching["S"].append(r)
            if r.hi == env.H:
                reaching["N"].append(r)
        else:
            if r.lo == 0:
                reaching["W"].append(r)
            if r.hi == env.W:
                reaching["E"].append(r)

    for side in SIDES:
        span = inner_x if side in ("S", "N") else inner_y
        faces: List[int] = []
        for r in reaching[side]:
            c = r.coord * GRID_MM - half   # solve-domain mm -> clear datum
            faces += [c - half, c + half]
        faces = sorted(set(faces))
        ticks = []
        prev = 0
        for f in faces:
            ticks.append(f - prev)
            prev = f
        ticks.append(span - prev)
        out[side] = {
            "walls": len(reaching[side]),
            "witnesses": len(faces),
            "segments": len(ticks),
            "ticks": ticks,
            "closes": sum(ticks) == span,
            "span": span,
        }
    return out


def orphan_partitions(rooms: Sequence[Rect], env: Envelope) -> int:
    """Tier 2b: partition runs reaching no Envelope bbox edge.

    Each such face needs a running dimension from the nearest side, on its own
    rung — which is what pushes tier 1 outward from 26 to 34 mm paper.
    """
    k = 0
    for r in wall_runs(rooms):
        if r.axis == "v":
            if r.lo != 0 and r.hi != env.H:
                k += 1
        else:
            if r.lo != 0 and r.hi != env.W:
                k += 1
    return k


def orphan_sides(rooms: Sequence[Rect], env: Envelope) -> Dict[str, bool]:
    """Which sides carry a tier-2b rung. A 2b face goes to its nearest side."""
    out = {s: False for s in SIDES}
    for r in wall_runs(rooms):
        if r.axis == "v" and r.lo != 0 and r.hi != env.H:
            out["S" if r.lo <= env.H - r.hi else "N"] = True
        elif r.axis == "h" and r.lo != 0 and r.hi != env.W:
            out["W" if r.lo <= env.W - r.hi else "E"] = True
    return out


# ---------------------------------------------------------------------------
# Narrow-tick rule (annotation.md 5a)
# ---------------------------------------------------------------------------


def narrow_ticks(chain: dict, scale: int) -> dict:
    """How often a segment is narrower than its own text, and what collides.

    > If a segment's span in `paper` mm is less than the rendered text width
    > plus 2 x DIMGAP, place the text outside the extension lines with a
    > leader. When two consecutive outside texts would themselves overlap,
    > alternate them above and below the dimension line.
    """
    ticks = chain["ticks"]
    fires: List[int] = []
    for idx, t in enumerate(ticks):
        paper = t / scale
        if paper < text_width(t) + 2 * DIMGAP:
            fires.append(idx)

    # Midpoints of the outside-text segments, in paper mm along the chain.
    mids: List[Tuple[int, float, float]] = []
    run = 0.0
    for idx, t in enumerate(ticks):
        if idx in fires:
            mids.append((idx, (run + t / 2) / scale, text_width(t)))
        run += t
    collisions = 0
    for a, b in zip(mids, mids[1:]):
        if b[1] - a[1] < (a[2] + b[2]) / 2:
            collisions += 1
    return {"fires": len(fires), "outside_collisions": collisions,
            "segments": len(ticks)}


# ---------------------------------------------------------------------------
# Sheet and scale (annotation.md 9)
# ---------------------------------------------------------------------------


def sheet_and_scale(rooms: Sequence[Rect], env: Envelope,
                    t_int: int = 100) -> dict:
    """Take the first ladder entry whose annotated extent fits the printable area.

    Annotated extent = footprint grown on each side by that side's outermost
    occupied rung plus one text height. Tier 1 sits at 26 mm paper, or 34 where
    that side also carries a tier-2b rung.
    """
    inner_x = env.W * GRID_MM - t_int
    inner_y = env.H * GRID_MM - t_int
    # Footprint: an exterior edge adds its full thickness, a party edge half of
    # it, matching tier 1 and GIA/IPMS (annotation.md 3).
    ext = {s: False for s in SIDES}
    frac = env.exterior_sides
    for s, key in (("S", "S"), ("N", "N"), ("W", "W"), ("E", "E")):
        ext[s] = frac.get(key, 0.0) > 0.0
    add = {s: (T_EXT if ext[s] else T_PARTY // 2) for s in SIDES}
    foot_x = inner_x + add["W"] + add["E"]
    foot_y = inner_y + add["S"] + add["N"]

    has2b = orphan_sides(rooms, env)
    rung = {s: (RUNG_TIER1_WITH_2B if has2b[s] else RUNG_TIER1_NO_2B)
            for s in SIDES}

    for sheet, scale in LADDER:
        px, py = printable(sheet)
        ex = (foot_x + (rung["W"] + EXTENT_TEXT_PAD) * scale
              + (rung["E"] + EXTENT_TEXT_PAD) * scale) / scale
        ey = (foot_y + (rung["S"] + EXTENT_TEXT_PAD) * scale
              + (rung["N"] + EXTENT_TEXT_PAD) * scale) / scale
        if ex <= px and ey <= py:
            return {"sheet": sheet, "scale": scale, "extent_x": round(ex, 1),
                    "extent_y": round(ey, 1), "fits": True,
                    "footprint_x": foot_x, "footprint_y": foot_y}
    sheet, scale = LADDER[-1]
    px, py = printable(sheet)
    ex = (foot_x + (rung["W"] + EXTENT_TEXT_PAD) * scale
          + (rung["E"] + EXTENT_TEXT_PAD) * scale) / scale
    ey = (foot_y + (rung["S"] + EXTENT_TEXT_PAD) * scale
          + (rung["N"] + EXTENT_TEXT_PAD) * scale) / scale
    return {"sheet": sheet, "scale": scale, "extent_x": round(ex, 1),
            "extent_y": round(ey, 1), "fits": False,
            "footprint_x": foot_x, "footprint_y": foot_y}


def measure(rooms: Sequence[Rect], env: Envelope, t_int: int = 100) -> dict:
    """Every drawing measurement ticket 15 asks for, off one solved Plan."""
    sh = sheet_and_scale(rooms, env, t_int)
    ch = chains(rooms, env, t_int)
    nt = {s: narrow_ticks(ch[s], sh["scale"]) for s in SIDES}
    return {
        "sheet": sh["sheet"],
        "scale": sh["scale"],
        "sheet_fits": sh["fits"],
        "extent_x": sh["extent_x"],
        "extent_y": sh["extent_y"],
        "walls_total": len(wall_runs(rooms)),
        "orphan_partitions": orphan_partitions(rooms, env),
        "witnesses": {s: ch[s]["witnesses"] for s in SIDES},
        "witnesses_max": max(ch[s]["witnesses"] for s in SIDES),
        "witnesses_total": sum(ch[s]["witnesses"] for s in SIDES),
        "segments_max": max(ch[s]["segments"] for s in SIDES),
        "chains_close": all(ch[s]["closes"] for s in SIDES),
        "narrow_fires": sum(nt[s]["fires"] for s in SIDES),
        "narrow_collisions": sum(nt[s]["outside_collisions"] for s in SIDES),
    }
