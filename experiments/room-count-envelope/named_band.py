"""Ticket 21: expected retrieval blank rate PER HOMEOWNER-NAMED ROOM COUNT.

Joins two measurements:
  - circulation_split.py:  P(engine = e | named = m)   -- resolve invents k corridors
  - coverage_per_n.py:     blank(e)                    -- retrieval pool = 0 rate at e

The promise is made in named rooms; retrieval is measured in engine rooms.
This is the only table that speaks the unit the product copy is written in.
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

cov = {int(k): v for k, v in json.load(
    open(Path(__file__).resolve().parent / "coverage_per_n.json")).items()}

total, circ = Counter(), Counter()
for chunk in pd.read_csv(GEOM, usecols=["entity_type","entity_subtype","unit_usage",
                                        "site_id","floor_id","apartment_id"],
                         chunksize=1_000_000, dtype=str):
    a = chunk[(chunk.entity_type=="area") & (chunk.unit_usage=="RESIDENTIAL") &
              (chunk.apartment_id!=NULL_HASH)]
    a = a[~a.entity_subtype.isin(EXCLUDE)]
    total.update(zip(a.site_id, a.floor_id, a.apartment_id))
    c = a[a.entity_subtype.isin(CIRC)]
    circ.update(zip(c.site_id, c.floor_id, c.apartment_id))

joint = Counter()
for k, n in total.items():
    joint[(n - circ.get(k, 0), n)] += 1

print("named -> expected retrieval blank rate (weighted over engine counts)\n")
print(f"{'named':>6}{'n':>8}{'E[blank]':>10}{'median k':>10}   engine mix")
for m in range(1, 12):
    row = {e: v for (nm, e), v in joint.items() if nm == m}
    if not row:
        continue
    tot = sum(row.values())
    blank = sum(v * cov.get(e, {"zero_pct": 100.0})["zero_pct"] for e, v in row.items()) / tot
    ks = sorted(e - m for e in row for _ in range(row[e]))
    mix = " ".join(f"{e}:{100*v/tot:.0f}%" for e, v in sorted(row.items()) if v/tot >= 0.03)
    print(f"{m:>6}{tot:>8,}{blank:>9.1f}%{ks[len(ks)//2]:>10}   {mix}")

print("\nk (invented circulation rooms) per named count -- what `resolve` must guess")
for m in range(3, 11):
    row = {e - m: v for (nm, e), v in joint.items() if nm == m}
    if not row: continue
    tot = sum(row.values())
    print(f"  named {m:>2}: " + "  ".join(f"k={k}:{100*v/tot:4.1f}%"
          for k, v in sorted(row.items()) if v/tot >= 0.01))
