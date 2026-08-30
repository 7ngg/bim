"""The Plan as the drawing layer sees it: integer millimetres, clear plane.

ONE COORDINATE SYSTEM, and every module in this package uses it.

    Origin at the Envelope's inner-face bbox minimum. +X east, +Y north.
    Every coordinate is an integer millimetre on the CLEAR plane — ADR 0010's
    finished face, which is the plane `ümumi sahə` is measured on and the plane
    every published dimension measures to (ADR 0004, annotation.md §3).

The solver works in grid units on a domain DILATED by `t_int/2` (ADR 0001), so
the conversion in is exactly one erosion:

    clear_lo(u) = GRID * u          clear_hi(u) = GRID * u - t_int

which is annotation.md §14's arithmetic verbatim: a solved `[-75, 4425]` at
grid 250 / t_int 150 becomes a clear `[0, 4350]`, and an Envelope of 32 cells
becomes an inner 7850. `build.from_solved` is the only place that conversion
happens.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from . import profile


@dataclass(frozen=True)
class RectMM:
    """Half-open in the same sense the solver's `Rect` is, in millimetres."""
    x1: int
    y1: int
    x2: int
    y2: int

    @property
    def w(self) -> int:
        return self.x2 - self.x1

    @property
    def h(self) -> int:
        return self.y2 - self.y1

    @property
    def area_mm2(self) -> int:
        return self.w * self.h

    @property
    def area_m2(self) -> float:
        return self.area_mm2 / 1_000_000.0

    @property
    def centroid(self) -> Tuple[float, float]:
        return ((self.x1 + self.x2) / 2.0, (self.y1 + self.y2) / 2.0)

    def as_poly(self):
        from shapely.geometry import box
        return box(self.x1, self.y1, self.x2, self.y2)


@dataclass
class Space:
    """One Room's floor, as one or two rectangles — ADR 0014.

    `parts` is ordered largest-first, which is what §7 places the tag on and
    what §6's `Clear dimensions` column prints.
    """
    ref: str                      # R01, R02 … the room-schedule join key
    key: str                      # ergonomic key: living, bedroom_double, wc …
    corpus_label: str             # the donor's own label, kept for provenance
    parts: List[RectMM]

    def __post_init__(self):
        self.parts = sorted(self.parts, key=lambda r: -r.area_mm2)

    @property
    def primary(self) -> RectMM:
        return self.parts[0]

    @property
    def area_m2(self) -> float:
        return sum(p.area_m2 for p in self.parts)

    @property
    def name_az(self) -> str:
        return profile.name_az(self.key)

    @property
    def is_private(self) -> bool:
        return profile.is_private(self.key)

    @property
    def is_wet(self) -> bool:
        return profile.is_wet(self.key)

    @property
    def is_habitable(self) -> bool:
        return profile.is_habitable(self.key)

    @property
    def is_circulation(self) -> bool:
        return self.key in ("hall", "corridor", "entrance_lobby")

    @property
    def needs_window(self) -> bool:
        return profile.needs_window(self.key)

    def as_poly(self):
        from shapely.ops import unary_union
        return unary_union([p.as_poly() for p in self.parts])


@dataclass(frozen=True)
class Face:
    """One Envelope boundary face, on the clear plane. ADR 0003's typed edge ring.

    `axis` 'v' means a vertical face at x == `coord` spanning y in [lo, hi).
    `outward` is +1 when the wall body lies at greater coordinate than the face
    and -1 when it lies at less. `side` is the bbox edge it belongs to, or None
    for a notch face that is not on a bbox line.
    """
    axis: str
    coord: int
    lo: int
    hi: int
    outward: int
    is_exterior: bool
    side: Optional[str] = None

    @property
    def length(self) -> int:
        return self.hi - self.lo

    @property
    def thickness(self) -> int:
        return profile.T_EXT_MM if self.is_exterior else profile.T_PARTY_MM


@dataclass
class Opening:
    """A hosted Opening. `openings.py` is the only thing that constructs one.

    Geometry is stated on the wall it is hosted in: `axis` is the WALL's axis
    ('v' = a vertical wall, so the opening runs in y), `across` is the wall
    body's extent perpendicular to itself, and `p1..p2` is the STRUCTURAL
    opening along the wall.
    """
    kind: str                       # door | entrance_door | cased_opening | window
    catalogue: str                  # profile catalogue key, or "" for a series window
    mark: str                       # plan mark: a bare number, or ОК<n>
    axis: str                       # 'v' | 'h'  — the wall's axis
    across: Tuple[int, int]         # wall body extent across itself
    p1: int                         # structural opening, along the wall
    p2: int
    height_mm: int                  # structural opening height
    receiving: Optional[str] = None  # Space ref the door belongs to (§3.3)
    other: Optional[str] = None      # the Space on the far side, or None (exterior)
    hinge_end: Optional[str] = None  # 'lo' | 'hi' along the wall, or None
    swing_side: Optional[str] = None  # 'lo' | 'hi' across the wall, or None
    host_space: Optional[str] = None  # for a window: the Space it lights
    datum: Optional[int] = None      # §4.5's setting-out datum face, along the wall
    glazed: bool = False

    @property
    def width(self) -> int:
        return self.p2 - self.p1

    @property
    def leaf_w(self) -> Optional[int]:
        """openings.md §2.3 — `leaf = opening − 100`, derived, and it reproduces
        GOST 6629-88's published leaf series exactly."""
        if self.kind in ("cased_opening", "window"):
            return None
        return self.width - 100

    @property
    def is_door(self) -> bool:
        return self.kind in ("door", "entrance_door", "cased_opening")

    def rect(self) -> RectMM:
        a, b = self.across
        if self.axis == "v":
            return RectMM(a, self.p1, b, self.p2)
        return RectMM(self.p1, a, self.p2, b)


@dataclass
class Plan:
    """Everything the Drawing is derived from, and nothing else."""
    name: str
    spaces: List[Space]
    faces: List[Face]
    inner: RectMM                       # the Envelope's inner-face bounding box
    entrance_side: str                  # 'N' | 'S' | 'E' | 'W'
    notches: List[RectMM] = field(default_factory=list)
    openings: List[Opening] = field(default_factory=list)
    grid_mm: int = profile.GRID_MM
    t_int: int = profile.T_INT_MM
    provenance: dict = field(default_factory=dict)

    def by_ref(self, ref: str) -> Space:
        for s in self.spaces:
            if s.ref == ref:
                return s
        raise KeyError(ref)

    @property
    def sum_space_m2(self) -> float:
        """`faydalı sahə` — and numerically `ümumi sahə` in v1, which models no
        balcony. annotation.md §7.2 says why those are not the same quantity."""
        return sum(s.area_m2 for s in self.spaces)

    @property
    def habitable_m2(self) -> float:
        """`yaşayış sahəsi` — the numerator of §7.2's fraction."""
        return sum(s.area_m2 for s in self.spaces if s.is_habitable)

    @property
    def interior_m2(self) -> float:
        """The Envelope inner area, notches removed. The schedule's second total."""
        return (self.inner.area_mm2 - sum(n.area_mm2 for n in self.notches)) / 1e6

    def interior_poly(self):
        from shapely.ops import unary_union
        p = self.inner.as_poly()
        if self.notches:
            p = p.difference(unary_union([n.as_poly() for n in self.notches]))
        return p
