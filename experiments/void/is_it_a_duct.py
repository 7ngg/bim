"""Ticket 53, bullet 4: is an enclosed void ever REAL?

The conversion drops SHAFT/VOID/LIGHTWELL/ELEVATOR/STAIRCASE/TECHNICAL_AREA as
NOT_A_ROOM *before* the watershed. But `watershed` labels any cell within
WALL_REACH = 350 mm of a kept room, so a dropped duct narrower than ~700 mm is
swallowed into `dom` and lands in the enclosed-void census as if it were fit
residue. Nobody has separated the two. This does, read-only, into scratchpad.
"""
import json, sys, pickle
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, str(Path("experiments/rectangularise").resolve()))
import pandas as pd, numpy as np
from shapely import from_wkt
from shapely.ops import unary_union
from measure_swiss import COLS, GEOM, MD5_EMPTY, NOT_A_ROOM, _poly, MIN_ROOM_AREA
from fit_rects import (watershed, keep_largest_component, envelope_approx,
                       components, GRID, GRID_MM)

VOID_SUB = {"SHAFT", "VOID", "OUTDOOR_VOID", "LIGHTWELL", "ELEVATOR",
            "STAIRCASE", "TECHNICAL_AREA"}
want = set()
fits = [r for r in json.load(open("experiments/rectangularise/out/swiss_fit_k2.json"))
        if r["status"] in ("OPTIMAL", "FEASIBLE")]
fitmap = {r["k"]: r for r in fits}

# Load the DROPPED entities only, keyed the same way swiss_keys() keys dwellings.
drop = defaultdict(list)
n = 0
for chunk in pd.read_csv(GEOM, usecols=COLS, chunksize=500_000, dtype=str):
    a = chunk[chunk["entity_type"] == "area"] if "entity_type" in chunk else chunk
    a = a[a["entity_subtype"].isin(VOID_SUB)]
    for r in a.itertuples(index=False):
        k = (str(r.site_id), str(r.floor_id), str(r.apartment_id))
        drop[k].append(r.geometry)
        n += 1
print(f"dropped NOT_A_ROOM void-like polygons: {n:,} over {len(drop):,} apartments", flush=True)

sys.path.insert(0, str(Path("experiments/warp").resolve()))
from absolute_area import notch_share

rows = []
cache = Path("experiments/rectangularise/out/swiss_dw.pkl")
dw, keys = pickle.load(open(cache, "rb"))
seen = 0
for k, rec in fitmap.items():
    key = tuple(k.split("|"))
    items = dw.get(key)
    if items is None:
        continue
    s, v = notch_share(rec["parts"])
    if v <= 0:
        continue
    seen += 1
    if seen > 400:
        break
    # rebuild the fit's own frame
    geoms = [_poly(from_wkt(w)) for _st, w in items]
    geoms = [g for g in geoms if g is not None and g.area >= MIN_ROOM_AREA]
    if not geoms:
        continue
    lab, x0, y0 = watershed(geoms)
    if lab is None:
        continue
    lab = keep_largest_component(lab)
    env, notches, info, (oy, ox) = envelope_approx(lab >= 0)
    # dropped polygons for this apartment, rasterised on the same frame
    dg = [from_wkt(w) for w in drop.get(key, [])]
    dg = [g for g in dg if g is not None and not g.is_empty]
    ny, nx = env.shape
    hit_any = False
    if dg:
        u = unary_union(dg)
        from shapely import contains_xy
        cy = y0 + (np.arange(lab.shape[0]) + 0.5) * GRID
        cx = x0 + (np.arange(lab.shape[1]) + 0.5) * GRID
        gx, gy = np.meshgrid(cx, cy)
        dropmask_full = contains_xy(u, gx.ravel(), gy.ravel()).reshape(lab.shape)
        dropmask = dropmask_full[oy:oy + ny, ox:ox + nx]
    else:
        dropmask = np.zeros(env.shape, dtype=bool)
    covered = np.zeros(env.shape, dtype=bool)
    for ps in (rec.get("parts") or [[r] for r in rec["rects"]]):
        for (a1, b1, a2, b2) in ps:
            covered[b1:b2, a1:a2] = True
    unc = env & ~covered
    edge = np.zeros(env.shape, dtype=bool)
    edge[0, :] = edge[-1, :] = True; edge[:, 0] = edge[:, -1] = True
    pad = np.pad((~env) | edge, 1, constant_values=True)
    touches_out = (pad[:-2, 1:-1] | pad[2:, 1:-1] | pad[1:-1, :-2] | pad[1:-1, 2:])
    for cells in components(unc):
        m = np.zeros(env.shape, dtype=bool)
        for (cyy, cxx) in cells:
            m[cyy, cxx] = True
        if (m & touches_out).any():
            continue
        overlap = (m & dropmask).sum() / len(cells)
        rows.append({"k": k, "cells": len(cells), "m2": len(cells) * 0.0625,
                     "drop_overlap": float(overlap)})
        hit_any = hit_any or overlap > 0

print(f"\n{len(rows)} enclosed void components over {seen} voided dwellings")
if rows:
    for lo in (0.5, 0.25, 0.05, 0.0001):
        n2 = sum(1 for r in rows if r["drop_overlap"] >= lo)
        print("  components with >= %.0f%% of their cells inside a dropped SHAFT/VOID/"
              "TECHNICAL_AREA: %d (%.1f%%)" % (100*lo, n2, 100*n2/len(rows)))
    big = [r for r in rows if r["m2"] >= 0.5]
    if big:
        n2 = sum(1 for r in big if r["drop_overlap"] >= 0.5)
        print("  of the %d components >= 0.5 m2, %d (%.1f%%) are majority dropped-entity"
              % (len(big), n2, 100*n2/len(big)))
    a = sum(r["m2"] for r in rows if r["drop_overlap"] >= 0.5)
    print("  area share: %.1f%% of all enclosed void m2 is majority dropped-entity"
          % (100*a/sum(r["m2"] for r in rows)))
