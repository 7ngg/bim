"""Ticket 53: the GENERAL absorption. Not "one part, one full edge" -- iterate.

A part may absorb a slab of the void spanning that part's full width or full
height and adjacent to it. Doing that changes the void, which may expose another
slab. Run to fixpoint. Aspect stays inside dim.aspect_ratio_hard = 3.02, and a
part may not swallow so much that its Room's total area drifts absurdly.

ADR 0014 says why the void may not simply BECOME a second part: any further part
carries 900 mm clear on both axes, realisable 1100 = 5 cells, so a legal leg is
>= 1.5625 m2. Void p50 is 0.5. Below that it is a NICHE and this system does not
model niches.
"""
import json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path("experiments/warp").resolve()))
from absolute_area import notch_share

ASPECT = 3.02
LEG_CELLS = 5           # ADR 0014 / dim.leg_join realisable 1100 mm

def comps(mask):
    ny, nx = mask.shape
    seen = np.zeros_like(mask); out = []
    for y in range(ny):
        for x in range(nx):
            if mask[y, x] and not seen[y, x]:
                st = [(y, x)]; seen[y, x] = True; cells = []
                while st:
                    a, b = st.pop(); cells.append((a, b))
                    for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
                        p, q = a+dy, b+dx
                        if 0 <= p < ny and 0 <= q < nx and mask[p, q] and not seen[p, q]:
                            seen[p, q] = True; st.append((p, q))
                out.append(cells)
    return out

def absorb(parts, free, ny, nx):
    """Greedy to fixpoint. `parts` is a flat list of [x1,y1,x2,y2] in LOCAL cells,
    each tagged with its Room. Returns (parts, free, moves)."""
    moves = 0
    changed = True
    while changed:
        changed = False
        for p in parts:
            a, b, c, d = p["r"]
            for side in ("E", "W", "N", "S"):
                # the maximal slab of free cells adjacent to this part's full edge
                if side == "E":
                    if c >= nx: continue
                    k = 0
                    while c + k < nx and free[b:d, c + k].all(): k += 1
                    if k == 0: continue
                    new = (a, b, c + k, d)
                elif side == "W":
                    if a <= 0: continue
                    k = 0
                    while a - k - 1 >= 0 and free[b:d, a - k - 1].all(): k += 1
                    if k == 0: continue
                    new = (a - k, b, c, d)
                elif side == "S":
                    if d >= ny: continue
                    k = 0
                    while d + k < ny and free[d + k, a:c].all(): k += 1
                    if k == 0: continue
                    new = (a, b, c, d + k)
                else:
                    if b <= 0: continue
                    k = 0
                    while b - k - 1 >= 0 and free[b - k - 1, a:c].all(): k += 1
                    if k == 0: continue
                    new = (a, b - k, c, d)
                w, h = new[2] - new[0], new[3] - new[1]
                if max(w, h) / min(w, h) > ASPECT: continue
                p["r"] = new
                free[new[1]:new[3], new[0]:new[2]] = False
                moves += 1; changed = True
                a, b, c, d = new
    return parts, free, moves

fits = [r for r in json.load(open("experiments/rectangularise/out/swiss_fit_k2.json"))
        if r["status"] in ("OPTIMAL", "FEASIBLE")]

tot_before = tot_after = 0
dw_before = dw_after = 0
resid_m2, before_m2 = [], []
legal_leg = 0
per_n_before, per_n_after = defaultdict(int), defaultdict(int)
n_by = defaultdict(int)
for rec in fits:
    parts = rec.get("parts") or [[r] for r in rec["rects"]]
    s, v = notch_share(parts)
    n_by[rec["n"]] += 1
    if v <= 0:
        continue
    x0 = min(p[0] for pl in parts for p in pl); y0 = min(p[1] for pl in parts for p in pl)
    x1 = max(p[2] for pl in parts for p in pl); y1 = max(p[3] for pl in parts for p in pl)
    ny, nx = y1 - y0, x1 - x0
    g = np.zeros((ny, nx), dtype=bool)
    flat = []
    for ri, pl in enumerate(parts):
        for a, b, c, d in pl:
            g[b-y0:d-y0, a-x0:c-x0] = True
            flat.append({"room": ri, "r": (a-x0, b-y0, c-x0, d-y0)})
    free = ~g
    # enclosed only
    enclosed = np.zeros_like(free)
    for cells in comps(free):
        ys = [c[0] for c in cells]; xs = [c[1] for c in cells]
        if min(ys) == 0 or max(ys) == ny-1 or min(xs) == 0 or max(xs) == nx-1:
            continue
        for (cy, cx) in cells: enclosed[cy, cx] = True
        if (max(ys)-min(ys)+1) >= LEG_CELLS and (max(xs)-min(xs)+1) >= LEG_CELLS:
            legal_leg += 1
    b0 = int(enclosed.sum())
    if b0 == 0:
        continue
    dw_before += 1
    tot_before += b0
    before_m2.append(b0 * 0.0625)
    per_n_before[rec["n"]] += 1
    work = enclosed.copy()
    _p, work, _m = absorb(flat, work, ny, nx)
    b1 = int(work.sum())
    tot_after += b1
    if b1 > 0:
        dw_after += 1
        resid_m2.append(b1 * 0.0625)
        per_n_after[rec["n"]] += 1

def q(v, p):
    if not v: return float("nan")
    s = sorted(v); return s[max(0, min(len(s)-1, int(round(p/100*(len(s)-1)))))]

N = len(fits)
print(f"index {N:,} converted dwellings")
print(f"voided before absorption : {dw_before} ({100*dw_before/N:.2f}%)  "
      f"area p50 {q(before_m2,50):.3f} p90 {q(before_m2,90):.3f} m2")
print(f"voided AFTER  absorption : {dw_after} ({100*dw_after/N:.2f}%)  "
      f"area p50 {q(resid_m2,50):.3f} p90 {q(resid_m2,90):.3f} max {q(resid_m2,100):.3f} m2")
print(f"void cells closed: {100*(tot_before-tot_after)/tot_before:.1f}%  "
      f"({tot_before*0.0625:.0f} m2 -> {tot_after*0.0625:.0f} m2 over the index)")
print(f"\nvoid components big enough to be a LEGAL second part "
      f"(>= {LEG_CELLS}x{LEG_CELLS} cells = 1.5625 m2, ADR 0014): {legal_leg}")
print("\nresidue by room count (what a gate would actually cost):")
for n in sorted(n_by):
    if n_by[n] < 30: continue
    print("  n=%2d  N=%5d   before %5.2f%%   after %5.2f%%"
          % (n, n_by[n], 100*per_n_before[n]/n_by[n], 100*per_n_after[n]/n_by[n]))
