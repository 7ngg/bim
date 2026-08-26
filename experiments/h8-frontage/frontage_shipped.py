"""Re-run the H8 frontage budget against the SHIPPED ergonomic layer.

The published table in ticket 26 used experiments/solver-toy/scenarios.STANDARDS,
which is a placeholder ("the point here is the shape of the constraint, not the
number").  Ticket 19 has since landed the real one.
"""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "solver-toy"))
from geometry import EXPOSURE_PRESETS            # noqa: E402
from scenarios import composition, envelope_for, GRID_MM  # noqa: E402

RC = json.load(open(ROOT / "data" / "standards" / "room-constraints.json", encoding="utf-8"))
ROOMS = RC["ergonomic"]["rooms"]
CAT = RC["profiles"]["AZ"]["openings"]["catalogue"]
JAMB = 100          # open.fits_segment value, per side
LEG = 900           # acceptance-bar 9.1 leg floor
T_INT = 150

def v(room, key):
    x = ROOMS[room].get(key)
    return x["v"] if isinstance(x, dict) else x

# toy kind -> shipped room type (the toy has one generic 'bedroom')
MAP = {"living": "living", "bedroom": "bedroom_double", "kitchen": "kitchen",
       "dining": "dining", "study": "study", "bathroom": "bathroom",
       "wc": "wc", "utility": "utility", "hall": "hall", "corridor": "corridor"}

WIN = {"living": "window_living", "living_dining": "window_living",
       "living_dining_kitchen": "window_living", "dining": "window_living",
       "bedroom_double": "window_bedroom", "bedroom_principal": "window_bedroom",
       "bedroom_single": "window_bedroom", "study": "window_bedroom",
       "kitchen": "window_kitchen", "kitchen_dining": "window_kitchen"}

def win_w(rt):
    return CAT[WIN[rt]]["opening_w"]

def realisable(clear_mm):
    """ADR 0007/0009: clear = 250*w - t_int; smallest w meeting the floor."""
    w = 0
    while 250 * w - T_INT < clear_mm:
        w += 1
    return 250 * w - T_INT

def needs(n, rule):
    tot, parts = 0, []
    for k in composition(n):
        rt = MAP[k]
        hab = v(rt, "is_habitable")
        win = v(rt, "needs_window")
        if not (hab or win):
            continue
        if rule == "A_toy":
            continue
        if rule == "B_width":            # shipped min width, whole room at facade
            c = v(rt, "min_clear_short")
        elif rule == "C_window":         # window fit only (leg relief, option 1)
            c = (win_w(rt) + 2 * JAMB) if win else LEG
        elif rule == "D_leg":            # max(leg floor, window fit)
            c = max(LEG, (win_w(rt) + 2 * JAMB) if win else 0)
        elif rule == "E_option2":        # window-bearing part meets room min width
            c = max(v(rt, "min_clear_short"), (win_w(rt) + 2 * JAMB) if win else 0)
        c = realisable(c)
        tot += c
        parts.append((rt, c))
    return tot, parts

def run(rule):
    counts = (4, 5, 6, 7, 8, 10, 12, 14, 16, 20, 24)
    presets = tuple(EXPOSURE_PRESETS)
    print(f"\n=== rule {rule} ===")
    print(f"{'n':>3} {'rms':>4} {'need':>7} | " + " | ".join(f"{p[:13]:>13}" for p in presets))
    for n in counts:
        need, parts = needs(n, rule)
        cells = []
        for p in presets:
            env = envelope_for(n, p)
            have = sum(hi - lo for (_, _, lo, hi) in env.exterior_faces()) * GRID_MM
            mark = "ok  " if have >= need else "DEAD"
            cells.append(f"{have:6d} {mark} {have-need:+7d}".rjust(13))
        print(f"{n:>3} {len(parts):>4} {need:>7} | " + " | ".join(cells))

for r in ("B_width", "E_option2", "D_leg", "C_window"):
    run(r)
print("\nbreakdown at n=7:")
for r in ("B_width", "E_option2", "D_leg"):
    print(r, needs(7, r))
