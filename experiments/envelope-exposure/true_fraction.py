"""The exterior share of an Envelope's perimeter, counted once per face.

`geometry.Envelope.exterior_fraction` is the quantity `EXPOSURE_PRESETS` is
fitted against, and it double-counts. `all_faces()` emits each bbox edge in full
*and* all four faces of every notch, so the stretch a corner notch removed is
counted twice -- once as part of the bbox edge that no longer runs there, once as
a phantom notch face on the same line. On `envelope_for(8)` the true perimeter is
144 grid units and `all_faces()` counts 180: a denominator 25 % too large.

The phantom faces are also returned by `exterior_faces()`, which the solver reads
for H8. That half is harmless -- `Envelope.contains` forbids a room inside a
notch, so no room can be flush with the removed stretch and claim its daylight --
but the fraction is not, because it is what every preset was tuned to hit.

This recomputes it from the real boundary, which is the same operation on the
same objects and so is comparable with the corpus scalar rather than merely
similar to it. It lives here rather than in `geometry.py` because
`experiments/solver-toy/` is claimed by *What an ordered entry sequence costs the
solver*; the defect is handed to that ticket, see this directory's README.
"""

import sys
from pathlib import Path

from shapely.geometry import box
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "solver-toy"))

TOL = 1e-9


def true_faces(env):
    """Every real boundary face of `env`, as ('v'|'h', coord, lo, hi, is_exterior).

    Built from the actual polygon rather than from bbox edges plus notch
    rectangles, so a stretch of bbox edge a notch removed is simply absent
    instead of being counted twice with a phantom face laid over it.
    """
    poly = box(0, 0, env.W, env.H)
    if env.notches:
        poly = poly.difference(unary_union(
            [box(n.x1, n.y1, n.x2, n.y2) for n in env.notches]))
    if poly.geom_type != "Polygon":
        poly = max(poly.geoms, key=lambda p: p.area)

    # The preset's typing, as intervals per bbox line. A face not on a bbox line
    # is an internal notch face and takes the notch's own typing. Every bbox line
    # gets an entry, exterior runs or not: keying only the exterior ones lets a
    # wholly-party edge fall through to the notch branch below and be typed by a
    # notch that merely touches it, which reported a mid-terrace U as fully
    # exterior.
    ext_runs = {}
    for (k, c, lo, hi, is_ext) in env._bbox_runs():
        ext_runs.setdefault((k, round(c)), [])
        if is_ext:
            ext_runs[(k, round(c))].append((lo, hi))
    notch_ext = {(n.x1, n.y1, n.x2, n.y2): env._notch_is_exterior(n)
                 for n in env.notches}

    out = []
    cs = list(poly.exterior.coords)
    for i in range(len(cs) - 1):
        (x1, y1), (x2, y2) = cs[i], cs[i + 1]
        if abs(x1 - x2) < TOL and abs(y1 - y2) < TOL:
            continue
        if abs(x1 - x2) < TOL:
            k, c, lo, hi = "v", x1, min(y1, y2), max(y1, y2)
        else:
            k, c, lo, hi = "h", y1, min(x1, x2), max(x1, x2)

        key = (k, round(c))
        if key in ext_runs:
            runs = ext_runs[key]
            # On a bbox line: split at the preset's exterior/party cut so a
            # partial edge contributes exactly its exterior head.
            covered = 0.0
            for (a, b) in runs:
                covered += max(0.0, min(hi, b) - max(lo, a))
            if covered > TOL:
                out.append((k, c, lo, lo + covered, True))
            if hi - lo - covered > TOL:
                out.append((k, c, lo + covered, hi, False))
            continue

        # Not on a bbox line: an internal face of whichever notch it bounds.
        e = False
        for (nx1, ny1, nx2, ny2), is_ext in notch_ext.items():
            on = (k == "v" and abs(c - nx1) < TOL or k == "v" and abs(c - nx2) < TOL
                  or k == "h" and abs(c - ny1) < TOL or k == "h" and abs(c - ny2) < TOL)
            if on and is_ext:
                e = True
                break
        out.append((k, c, lo, hi, e))
    return out


def true_exterior_fraction(env) -> float:
    faces = true_faces(env)
    total = sum(hi - lo for (_, _, lo, hi, _) in faces)
    ext = sum(hi - lo for (_, _, lo, hi, e) in faces if e)
    return ext / total if total else 0.0


if __name__ == "__main__":
    from geometry import EXPOSURE_PRESETS
    from scenarios import envelope_for

    print("true vs published exterior_fraction, by preset and room count\n")
    names = list(EXPOSURE_PRESETS)
    print(f"{'n':>3} " + " ".join(f"{e:>21}" for e in names))
    for n in range(4, 13):
        row = []
        for e in names:
            env = envelope_for(n, exposure=e)
            row.append(f"{true_exterior_fraction(env):.2f} ({env.exterior_fraction:.2f})")
        print(f"{n:>3} " + " ".join(f"{c:>21}" for c in row))
