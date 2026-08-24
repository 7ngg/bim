"""Does AddNoOverlap2D ignore zero-area boxes in the pinned OR-Tools?

The whole k<=2 formulation rests on it: a Room's second rectangle is *absent*
by having zero size, rather than by being an optional interval. If a zero-area
box still conflicts, the model is wrong and every timing off it is worthless.

Pinned: ortools 9.15.6755.
"""
from ortools.sat.python import cp_model


def probe(zero_w: bool) -> str:
    m = cp_model.CpModel()
    # A 10x10 field. One 10x10 box fills it. A second box must coexist.
    xs, ys, xiv, yiv = [], [], [], []
    for i, (w, h) in enumerate(((10, 10), (0 if zero_w else 1, 0 if zero_w else 1))):
        x1 = m.NewIntVar(0, 10, f"x1_{i}")
        y1 = m.NewIntVar(0, 10, f"y1_{i}")
        x2 = m.NewIntVar(0, 10, f"x2_{i}")
        y2 = m.NewIntVar(0, 10, f"y2_{i}")
        wv = m.NewIntVar(0, 10, f"w_{i}")
        hv = m.NewIntVar(0, 10, f"h_{i}")
        m.Add(wv == w)
        m.Add(hv == h)
        m.Add(x2 == x1 + wv)
        m.Add(y2 == y1 + hv)
        xiv.append(m.NewIntervalVar(x1, wv, x2, f"xi_{i}"))
        yiv.append(m.NewIntervalVar(y1, hv, y2, f"yi_{i}"))
        xs.append((x1, x2))
        ys.append((y1, y2))
    m.AddNoOverlap2D(xiv, yiv)
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = 5
    return s.StatusName(s.Solve(m))


print("second box 0x0 :", probe(True))
print("second box 1x1 :", probe(False))
