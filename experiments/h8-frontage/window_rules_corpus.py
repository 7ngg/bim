"""H8 against real dwellings, on a correctly assembled dwelling envelope.

Also sweeps the wall-bridging distance, since that is the one judgement the
corrected envelope rests on.
"""
import random, statistics, sys
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
HABITABLE = NEEDS_WINDOW - {"KITCHEN"}
PARTY_GAP_M = 0.45
NEAR_M = 0.60
N_FLOORS = 150

cols = ["apartment_id","site_id","floor_id","unit_usage","entity_type","entity_subtype","geometry"]
counts = defaultdict(set)
for ch in pd.read_csv(GEOM, usecols=[c for c in cols if c!="geometry"], chunksize=1_000_000, dtype=str):
    a = ch[(ch.entity_type=="area")&(ch.unit_usage=="RESIDENTIAL")&(ch.apartment_id!=NULL_APT)]
    for s,f,ap in zip(a.site_id,a.floor_id,a.apartment_id): counts[(s,f)].add(ap)
multi = sorted(k for k,v in counts.items() if len(v)>=2)
random.seed(20260819)
pick = set(random.sample(multi, min(N_FLOORS,len(multi))))

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
        if et=="opening":
            openings[(s,f)].append((str(sub),poly)); continue
        if sub in NOT_A_ROOM: continue
        occupied[(s,f)].append(poly)
        if usage=="RESIDENTIAL" and ap!=NULL_APT: dwell[(s,f,ap)].append((str(sub),poly))

def envelope(polys, bridge):
    b = unary_union([p.buffer(bridge) for p in polys]).buffer(-bridge)
    if b.is_empty: return None
    if b.geom_type=="MultiPolygon": b = max(b.geoms,key=lambda p:p.area)
    return b if b.geom_type=="Polygon" else None

print("bridge sweep (exterior fraction of the dwelling perimeter):")
for bridge in (0.06,0.10,0.12,0.15,0.20,0.30):
    fr=[]
    for (s,f,ap),items in dwell.items():
        env = envelope([p for _,p in items], bridge)
        if env is None: continue
        others=[p for p in occupied[(s,f)] if not p.intersects(env.buffer(-0.05))]
        if not others or env.exterior.length<=0: continue
        near=unary_union([p.buffer(PARTY_GAP_M) for p in others])
        fr.append(env.exterior.difference(near).length/env.exterior.length)
    q=statistics.quantiles(sorted(fr),n=20)
    print(f"  bridge {bridge:.2f} m  n={len(fr)}  p25 {q[4]:.2f}  median {statistics.median(fr):.2f}  p75 {q[14]:.2f}")

BRIDGE=0.12
rows=[]; per_room=[]
for (s,f,ap),items in dwell.items():
    env = envelope([p for _,p in items], BRIDGE)
    if env is None: continue
    others=[p for p in occupied[(s,f)] if not p.intersects(env.buffer(-0.05))]
    if not others: continue
    near=unary_union([p.buffer(PARTY_GAP_M) for p in others])
    ext_line=env.exterior.difference(near)
    if env.exterior.length<=0: continue
    ext_frac=ext_line.length/env.exterior.length
    wins=[op for sub,op in openings[(s,f)] if sub.upper().startswith("WINDOW")]
    # keep only windows on this dwelling's own boundary band
    band_env=env.exterior.buffer(NEAR_M)
    wins=[w for w in wins if w.intersects(band_env)]
    need=nowin=noext=0
    for sub,poly in items:
        if sub not in NEEDS_WINDOW: continue
        need+=1
        rb=poly.exterior
        has_win=any(w.intersects(rb.buffer(NEAR_M)) for w in wins)
        run=rb.buffer(0.15).intersection(ext_line).length
        if not has_win: nowin+=1
        if run<0.05: noext+=1
        per_room.append({"sub":sub,"win":has_win,"run":run,"area":poly.area,
                         "hab":sub in HABITABLE,"ext":ext_frac})
    if need==0: continue
    rows.append({"ext":ext_frac,"need":need,"nowin":nowin,"noext":noext,
                 "area":env.area,"run":ext_line.length,"rooms":len(items)})

def pct(a,b): return f"{100*a/b:.1f}%" if b else "-"
n=len(per_room)
print(f"\ndwellings {len(rows)}   window-needing rooms {n}")
print(f"rooms with no window on own boundary : {sum(1 for r in per_room if not r['win'])}/{n} ({pct(sum(1 for r in per_room if not r['win']),n)})")
print(f"rooms with no exterior run           : {sum(1 for r in per_room if r['run']<0.05)}/{n} ({pct(sum(1 for r in per_room if r['run']<0.05),n)})")
print(f"dwellings failing has_window         : {pct(sum(1 for r in rows if r['nowin']),len(rows))}")
print(f"dwellings failing touches_exterior   : {pct(sum(1 for r in rows if r['noext']),len(rows))}")

print("\nby subtype: no-window / no-exterior-run / total")
bysub=defaultdict(lambda:[0,0,0])
for r in per_room:
    bysub[r["sub"]][2]+=1
    if not r["win"]: bysub[r["sub"]][0]+=1
    if r["run"]<0.05: bysub[r["sub"]][1]+=1
for k,(a,b,c) in sorted(bysub.items(),key=lambda kv:-kv[1][2]):
    print(f"  {k:15s} {a:4d} ({pct(a,c):>5}) {b:4d} ({pct(b,c):>5}) / {c}")

runs=sorted(r["run"] for r in per_room if r["run"]>=0.05)
q=lambda p: runs[int(p*(len(runs)-1))]
print(f"\nfacade run per room that has any (m), n={len(runs)}: p5 {q(.05):.2f} p25 {q(.25):.2f} median {q(.50):.2f} p75 {q(.75):.2f} p95 {q(.95):.2f}")
for t,lbl in ((1.85,"realisable ergonomic floor"),(2.60,"AZ market kitchen width"),(3.00,"AZ market habitable width")):
    print(f"  below {t:.2f} m ({lbl}): {pct(sum(1 for x in runs if x<t),len(runs))}")

low=[r for r in rows if r["ext"]<=0.35]
print(f"\nlow-exposure dwellings (corrected ext <= 0.35): {len(low)}/{len(rows)} ({pct(len(low),len(rows))})")
if low:
    print(f"  median window-needing rooms {statistics.median(r['need'] for r in low):.1f}, median exterior run {statistics.median(r['run'] for r in low):.1f} m, median area {statistics.median(r['area'] for r in low):.1f} m2")
    print(f"  failing has_window {pct(sum(1 for r in low if r['nowin']),len(low))}")

# --- what the kitchen rule alone costs the corpus -------------------------
by = defaultdict(lambda: [0,0,0])
tot=konly=nonk=0
for (s,f,ap),items in dwell.items():
    env = envelope([p for _,p in items], BRIDGE)
    if env is None: continue
    others=[p for p in occupied[(s,f)] if not p.intersects(env.buffer(-0.05))]
    if not others: continue
    near=unary_union([p.buffer(PARTY_GAP_M) for p in others])
    ext_line=env.exterior.difference(near)
    wins=[op for sub,op in openings[(s,f)] if sub.upper().startswith("WINDOW")
          and op.intersects(env.exterior.buffer(NEAR_M))]
    fk=fo=need=0
    for sub,poly in items:
        if sub not in NEEDS_WINDOW: continue
        need+=1
        if any(w.intersects(poly.exterior.buffer(NEAR_M)) for w in wins): continue
        if sub=="KITCHEN": fk+=1
        else: fo+=1
    if need==0: continue
    tot+=1
    if fk and not fo: konly+=1
    if fo: nonk+=1
print(f"\ndwellings {tot}: fail on KITCHEN ALONE {konly} ({100*konly/tot:.1f}%), "
      f"fail on a non-kitchen room {nonk} ({100*nonk/tot:.1f}%)")
