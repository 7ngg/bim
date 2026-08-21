"""Is the corpus's low tail real, and what does the 250 mm grid cost the floor?

Two questions this answers, both from the cache `ergonomic_floor_probe.py` wrote.

**1. Self-consistency.** A room the corpus labels a bathroom contains a BATHTUB
feature, and a bathtub is 1700 mm long (AD M Appendix D). So a bathroom whose
minimum rotated rectangle is shorter than 1700 mm on its LONG side cannot hold the
fixture the corpus says is in it. Those rooms are annotation fragments, not small
homes -- the same finding *Solver timing variance sweep* reached about the three
sub-0.02-exposure units. This gives an evidence-based floor for the falsification
line, instead of taking p1 on trust.

**2. Grid cost.** ADR 0007 requires every published minimum to satisfy
`minimum + t_int = 0 (mod grid)`. At grid 250 / t_int 100 the admissible values
are 650, 900, 1150, 1400, 1650, 1900 ... A derived minimum must round UP onto that
lattice -- rounding DOWN, which is what ADR 0007's own worked example does, is
sound for a CONVENTION-derived number (the source quoted a nominal or centreline
figure, so subtracting t_int recovers the clear one) and unsound for a
DERIVATION-derived one, which is already clear and has nothing to subtract. So the
ergonomic layer rounds up, and this measures what that costs against the corpus at
three candidate grids.

Run: python experiments/region-profile/floor_calibration.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "experiments" / "region-profile" / "out" / "room_dims.npz"

T_INT = 100
GRIDS = (250, 125, 50)

# Fixture footprints, mm. AD M Volume 1 Appendix D unless noted; OGL, VERIFIED.
BATH_L, BATH_D = 1700, 700
PAN_W, PAN_D = 500, 700
BASIN_W, BASIN_D = 600, 450
TRAY = 900                     # Neufert shower tray width
BED_S_L, BED_S_W = 1900, 900
BED_D_L, BED_D_W = 1900, 1350
UNIT_D = 600                   # kitchen base unit / appliance module depth
SINK_W, HOB_W, FRIDGE_W = 900, 600, 600
SETTEE_L, SETTEE_D = 1850, 850
CHAIR_D = 850

# The fixture each corpus label must be able to hold, on the room's LONG side.
# If the room cannot hold it, the polygon is a fragment, not a small home.
MUST_HOLD_LONG = {
    "bathroom": BATH_L,
    "shower_room": TRAY,
    "wc": PAN_D,
    "private": BED_S_L,
    "kitchen": SINK_W + HOB_W,
}


def programme(u: int) -> dict[str, tuple[int, int]]:
    """(short, long) raw derived floor, in mm, as a function of body depth `u`.

    `u` is the one free parameter: the depth of the body zone in front of a
    fixture that cannot be shared with another fixture's zone. Everything else is
    a published footprint. Structure is derived; `u` is calibrated below.
    """
    return {
        "wc":            (PAN_W + u,               PAN_D + u),
        "shower_room":   (max(TRAY, PAN_D + u),    TRAY + PAN_W),
        "bathroom":      (BATH_D + u,              BATH_L),
        "kitchen":       (UNIT_D + u,              SINK_W + HOB_W + FRIDGE_W),
        "private":       (BED_D_W + u,             BED_D_L),
        "living":        (SETTEE_D + u + CHAIR_D,  SETTEE_L),
        "dining":        (1000 + u,                1200 + u),
        "storage":       (UNIT_D,                  UNIT_D + u),
    }


def snap(v: int, grid: int) -> int:
    """Smallest x >= v with x + T_INT = 0 (mod grid). ADR 0007, rounding UP."""
    x = -T_INT % grid
    if x < v:
        x += ((v - x + grid - 1) // grid) * grid
    return x


def main() -> None:
    data = {k: np.load(CACHE)[k] for k in np.load(CACHE).files}

    print("1. SELF-CONSISTENCY -- can the room hold the fixture the corpus says")
    print("   is in it? Rooms that cannot are annotation fragments.")
    print()
    print(f"{'room type':14s} {'n':>7} {'must hold':>10} {'cannot':>9} {'share':>8} "
          f"{'p1 all':>8} {'p1 real':>8}")
    real: dict[str, np.ndarray] = {}
    for kind, need in MUST_HOLD_LONG.items():
        a = data[kind]
        ok = a[a[:, 1] >= need]
        real[kind] = ok
        bad = len(a) - len(ok)
        print(f"{kind:14s} {len(a):7d} {need:10d} {bad:9d} {100*bad/len(a):7.1f}% "
              f"{np.percentile(a[:, 0], 1):8.0f} {np.percentile(ok[:, 0], 1):8.0f}")
    for kind in data:
        real.setdefault(kind, data[kind])
    print()

    print("2. CALIBRATION -- the body depth `u` at which the derived floor rejects")
    print("   at most 1% of fixture-consistent rooms, per type, at grid 250.")
    print()
    print(f"{'u (mm)':>7} " + " ".join(f"{k[:9]:>10}" for k in sorted(programme(0))))
    for u in (200, 250, 300, 350, 400, 450, 500, 550, 600):
        cells = []
        for kind in sorted(programme(u)):
            s, lg = programme(u)[kind]
            s, lg = snap(s, 250), snap(lg, 250)
            a = real.get(kind)
            if a is None:
                cells.append(f"{'-':>10}")
                continue
            bad = np.mean((a[:, 0] < s) | (a[:, 1] < lg))
            cells.append(f"{100*bad:9.1f}%")
        print(f"{u:7d} " + " ".join(cells))
    print()

    print("3. GRID -- reject rate of the same derivation snapped onto three grids.")
    print("   `raw` is the derivation before any snapping: the arithmetic floor.")
    print()
    U = 450
    print(f"{'room type':14s} {'raw s x l':>14} " +
          " ".join(f"{f'grid {g}':>18}" for g in ("raw",) + GRIDS))
    for kind in sorted(programme(U)):
        s0, l0 = programme(U)[kind]
        a = real.get(kind)
        row = f"{kind:14s} {f'{s0} x {l0}':>14} "
        cells = []
        for g in (None,) + GRIDS:
            s, lg = (s0, l0) if g is None else (snap(s0, g), snap(l0, g))
            if a is None:
                cells.append(f"{f'{s}x{lg}':>12} {'-':>5}")
            else:
                bad = np.mean((a[:, 0] < s) | (a[:, 1] < lg))
                cells.append(f"{f'{s}x{lg}':>12} {100*bad:4.1f}%")
        print(row + " ".join(cells))


if __name__ == "__main__":
    main()
