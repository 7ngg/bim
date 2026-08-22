"""Ticket 21: the three room-count units, and the map has been conflating them.

  engine    every Space, incl. `resolve`-invented circulation. The 4-10 band and
            every retrieval-coverage figure are measured HERE.
  named     what a Homeowner types = engine - invented circulation.
  otaq      habitable rooms only (bedroom + living), the AzDTN / post-Soviet
            convention. `AZ` ships living_room_1room_flat and wardrobe_1room_entry
            keyed on it (AzDTN 2.7-2 cl. 5.7), and it is how flats are SOLD in Baku.
"""
import json
from collections import Counter
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
GEOM = ROOT / "data/corpora/swiss-dwellings/swiss-dwellings-v3.0.0/geometries.csv"
NULL_HASH = "d41d8cd98f00b204e9800998ecf8427e"
EXCLUDE = {"SHAFT","VOID","OUTDOOR_VOID","LIGHTWELL","ELEVATOR","STAIRCASE",
           "TECHNICAL_AREA","BALCONY","LOGGIA","TERRACE","GARDEN","PATIO","WINTERGARTEN"}
CIRC = {"CORRIDOR"}
# AzDTN "otaq": habitable rooms. Bedrooms + living rooms. Not kitchen, not bath,
# not corridor, not storage. LIVING_DINING and DINING count as one habitable room.
HABITABLE = {"ROOM","BEDROOM","STUDIO","LIVING_ROOM","LIVING_DINING","DINING"}

cov = {int(k): v for k, v in json.load(
    open(Path(__file__).resolve().parent / "coverage_per_n.json")).items()}

tot, circ, hab = Counter(), Counter(), Counter()
for chunk in pd.read_csv(GEOM, usecols=["entity_type","entity_subtype","unit_usage",
                                        "site_id","floor_id","apartment_id"],
                         chunksize=1_000_000, dtype=str):
    a = chunk[(chunk.entity_type=="area") & (chunk.unit_usage=="RESIDENTIAL") &
              (chunk.apartment_id!=NULL_HASH)]
    a = a[~a.entity_subtype.isin(EXCLUDE)]
    tot.update(zip(a.site_id, a.floor_id, a.apartment_id))
    circ.update(zip(*[c for c in zip(*[(s,f,p) for s,f,p,st in zip(
        a.site_id,a.floor_id,a.apartment_id,a.entity_subtype) if st in CIRC])] or [(),(),()]))
    hab.update(zip(*[c for c in zip(*[(s,f,p) for s,f,p,st in zip(
        a.site_id,a.floor_id,a.apartment_id,a.entity_subtype) if st in HABITABLE])] or [(),(),()]))

rows = []
for k, n in tot.items():
    rows.append((n, n - circ.get(k,0), hab.get(k,0)))

N = len(rows)
print(f"dwellings: {N:,}\n")
print("otaq (AzDTN habitable-room count) distribution:")
oh = Counter(o for _,_,o in rows)
for o in sorted(oh):
    if oh[o] >= 20:
        print(f"  {o} otaq: {oh[o]:>6,}  ({100*oh[o]/N:5.2f}%)")

print("\notaq -> engine, and what the engine band 4-10 does to each")
print(f"{'otaq':>5}{'n':>8}{'med eng':>9}{'in 4-10':>9}{'E[blank]':>10}   engine mix")
for o in range(0, 8):
    sel = [(e, nm) for e, nm, oo in rows if oo == o]
    if len(sel) < 20: continue
    es = sorted(e for e, _ in sel)
    m = len(sel)
    inband = sum(1 for e,_ in sel if 4 <= e <= 10)
    blank = sum(cov.get(e, {"zero_pct":100.0})["zero_pct"] for e,_ in sel)/m
    mix = Counter(e for e,_ in sel)
    ms = " ".join(f"{e}:{100*v/m:.0f}%" for e,v in sorted(mix.items()) if v/m>=0.05)
    print(f"{o:>5}{m:>8,}{es[m//2]:>9}{100*inband/m:>8.1f}%{blank:>9.1f}%   {ms}")

print("\nthe same dwelling, three ways (median):")
import statistics as st
for o in range(1, 6):
    sel = [(e, nm) for e, nm, oo in rows if oo == o]
    if len(sel) < 20: continue
    print(f"  {o} otaq  ->  named {st.median(nm for _,nm in sel):.0f}"
          f"  ->  engine {st.median(e for e,_ in sel):.0f}")

# --- gate floor 3 vs 4, and the three zones ---
print("\n\ngate floor: 3 vs 4")
for lo in (3, 4):
    inb = sum(1 for e,_,_ in rows if lo <= e <= 10)
    print(f"  engine {lo}-10: {inb:,} of {N:,} = {100*inb/N:.2f}%")
    for o in (0,1,2):
        sel = [e for e,_,oo in rows if oo == o]
        if not sel: continue
        print(f"      {o} otaq in band: {100*sum(1 for e in sel if lo<=e<=10)/len(sel):5.1f}%")

print("\nthree zones (gate engine 3-10, promise 1-4 otaq):")
promised = sum(1 for e,_,o in rows if 3 <= e <= 10 and 1 <= o <= 4)
served   = sum(1 for e,_,o in rows if 3 <= e <= 10 and not (1 <= o <= 4))
refused  = sum(1 for e,_,_ in rows if not (3 <= e <= 10))
for lbl, v in (("promised", promised), ("served, not promised", served), ("refused", refused)):
    print(f"  {lbl:<22} {v:>7,}  {100*v/N:5.2f}%")
