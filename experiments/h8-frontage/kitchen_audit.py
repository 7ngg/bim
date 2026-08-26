"""Is the 31% windowless kitchen real, or is it window-to-room attribution?

Three checks:
  1. how many WINDOW openings on the dwelling boundary get attributed to NO room
  2. for kitchens with facade but no window: their area, run, and nearest window
  3. does the open-plan route explain it -- is the kitchen adjacent to a windowed
     habitable room (a kitchen zone off a living room), which AzDTN's taxca-metbex
     names and profiles.AZ.windows.kitchen_niche_windowless holds false
"""
import random, statistics
from collections import Counter, defaultdict
from pathlib import Path
import pandas as pd
from shapely import wkt
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[2]
GEOM = ROOT / "data/corpora/swiss-dwellings/swiss-dwellings-v3.0.0/geometries.csv"
NULL_APT = "d41d8cd98f00b204e9800998ecf8427e"
NOT_A_ROOM = {"SHAFT","VOID","OUTDOOR_VOID","LIGHTWELL","ELEVATOR","STAIRCASE",
              "TECHNICAL_AREA","BALCONY","LOGGIA","TERRACE","GARDEN","PATIO","WINTERGARTEN"}
NEEDS_WINDOW = {"ROOM","LIVING_DINING","BEDROOM","LIVING_ROOM","DINING","KITCHEN_DINING","STUDIO","KITCHEN"}
PARTY_GAP_M, NEAR_M, BRIDGE = 0.45, 0.60, 0.12
N_FLOORS = 150
cols = ["apartment_id","site_id","floor_id","unit_usage","entity_type","entity_subtype","geometry"]

counts = defaultdict(set)
for ch in pd.read_csv(GEOM, usecols=[c for c in cols if c!="geometry"], chunksize=1_000_000, dtype=str):
    a = ch[(ch.entity_type=="area")&(ch.unit_usage=="RESIDENTIAL")&(ch.apartment_id!=NULL_APT)]
    for s,f,ap in zip(a.site_id,a.floor_id,a.apartment_id): counts[(s,f)].add(ap)
multi = sorted(k for k,v in counts.items() if len(v)>=2)
random.seed(20260819); pick = set(random.sample(multi, N_FLOORS))

dwell=defaultdict(list); occupied=defaultdict(list); openings=defaultdict(list)
for ch in pd.read_csv(GEOM, usecols=cols, chunksize=500_000, dtype=str):
    ch = ch[ch.entity_type.isin(("area","opening"))]
    ch = ch[[k in pick for k in zip(ch.site_id,ch.floor_id)]]
    if ch.empty: continue
    for s,f,ap,usage,et,sub,g in zip(ch.site_id,ch.floor_id,ch.apartment_id,ch.unit_usage,
                                     ch.entity_type,ch.entity_subtype,ch.geometry):
        try: poly=wkt.loads(g)
        except Exception: continue
        if poly.is_empty: continue
        if et=="opening": openings[(s,f)].append((str(sub),poly)); continue
        if sub in NOT_A_ROOM: continue
        occupied[(s,f)].append(poly)
        if usage=="RESIDENTIAL" and ap!=NULL_APT: dwell[(s,f,ap)].append((str(sub),poly))

orphan=0; attributed=0; multi_attr=0
kit_rows=[]; openplan=Counter(); nowin_by_adj=Counter()
for (s,f,ap),items in dwell.items():
    env=unary_union([p.buffer(BRIDGE) for _,p in items]).buffer(-BRIDGE)
    if env.is_empty: continue
    if env.geom_type=="MultiPolygon": env=max(env.geoms,key=lambda p:p.area)
    if env.geom_type!="Polygon": continue
    others=[p for p in occupied[(s,f)] if not p.intersects(env.buffer(-0.05))]
    if not others: continue
    near=unary_union([p.buffer(PARTY_GAP_M) for p in others])
    ext_line=env.exterior.difference(near)
    wins=[op for sub,op in openings[(s,f)] if sub.upper().startswith("WINDOW")
          and op.intersects(env.exterior.buffer(NEAR_M))]
    # attribution audit
    for w in wins:
        hits=[sub for sub,poly in items if w.intersects(poly.exterior.buffer(NEAR_M))]
        if not hits: orphan+=1
        else:
            attributed+=1
            if len(hits)>1: multi_attr+=1
    # kitchens
    for sub,poly in items:
        if sub!="KITCHEN": continue
        rb=poly.exterior
        has=any(w.intersects(rb.buffer(NEAR_M)) for w in wins)
        run=rb.buffer(0.15).intersection(ext_line).length
        if has: continue
        # adjacency: does it touch a habitable room that HAS a window?
        adj_windowed=False
        for sub2,poly2 in items:
            if sub2==sub and poly2.equals(poly): continue
            if sub2 not in NEEDS_WINDOW or sub2=="KITCHEN": continue
            if poly.buffer(0.25).intersects(poly2):
                if any(w.intersects(poly2.exterior.buffer(NEAR_M)) for w in wins):
                    adj_windowed=True; break
        d=min((w.distance(poly) for w in wins), default=float("inf"))
        kit_rows.append({"area":poly.area,"run":run,"adj":adj_windowed,"nearest":d,
                         "n_wins":len(wins)})
        nowin_by_adj[adj_windowed]+=1

print(f"window openings on dwelling boundary: attributed {attributed}, orphan {orphan} "
      f"({100*orphan/max(1,attributed+orphan):.1f}%), attributed to >1 room {multi_attr}")
print(f"\nwindowless kitchens: {len(kit_rows)}")
if kit_rows:
    a=sorted(r["area"] for r in kit_rows)
    print(f"  area m2: p25 {a[len(a)//4]:.1f}  median {statistics.median(a):.1f}  p75 {a[3*len(a)//4]:.1f}")
    print(f"  with exterior run >= 1.0 m : {sum(1 for r in kit_rows if r['run']>=1.0)} "
          f"({100*sum(1 for r in kit_rows if r['run']>=1.0)/len(kit_rows):.1f}%)")
    print(f"  adjacent to a WINDOWED habitable room: {nowin_by_adj[True]} "
          f"({100*nowin_by_adj[True]/len(kit_rows):.1f}%)  not adjacent: {nowin_by_adj[False]}")
    fin=[r['nearest'] for r in kit_rows if r['nearest']<float('inf')]
    if fin: print(f"  distance to nearest dwelling window m: median {statistics.median(fin):.2f}, "
                  f"under 1.0 m {100*sum(1 for x in fin if x<1.0)/len(fin):.1f}%")
    print(f"  in dwellings with zero windows at all: {sum(1 for r in kit_rows if r['n_wins']==0)}")
