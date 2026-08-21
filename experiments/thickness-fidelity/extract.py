"""Ticket 33 — pull the Swiss Dwellings rows this study needs into a cache.

One streaming pass over the 1.09 GB `geometries.csv`. Keeps, for a sampled set
of FLOORS:

  * every RESIDENTIAL `area` row with a non-null `apartment_id` (the Space
    polygons — the corpus records rooms as CLEAR polygons, inner faces, and no
    two of them ever touch: `experiments/rectangularise/probe_swiss.py`), and
  * every `separator/WALL` row on the same floor, regardless of `apartment_id`
    (20.9 % of walls carry none, and a party wall is exactly the kind that
    would not).

Floors are sampled two ways and unioned:

  * every floor that `experiments/rectangularise/out/swiss_fit.json` fitted, so
    item 4 can join thickness against ADR 0008 convert/drop status on the same
    dwellings; plus
  * a deterministic 1-in-`STRIDE` hash sample of all other floors, so the main
    census is not conditioned on having been fitted.

Writes `out/cache.pkl.gz`. Read-only on everything else.

Run:  python experiments/thickness-fidelity/extract.py [stride]
"""
from __future__ import annotations

import gzip
import hashlib
import json
import pickle
import sys
import time
from collections import defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
GEOM = ROOT / "data" / "corpora" / "swiss-dwellings" / "swiss-dwellings-v3.0.0" / "geometries.csv"
FIT = ROOT / "experiments" / "rectangularise" / "out" / "swiss_fit.json"
OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(parents=True, exist_ok=True)

STRIDE = int(sys.argv[1]) if len(sys.argv) > 1 else 10

# Same exclusion list as experiments/rectangularise/measure_swiss.py, so the two
# studies count the same things as rooms.
NOT_A_ROOM = {
    "SHAFT", "VOID", "OUTDOOR_VOID", "LIGHTWELL", "ELEVATOR", "STAIRCASE",
    "TECHNICAL_AREA", "BALCONY", "LOGGIA", "TERRACE", "GARDEN", "PATIO",
    "WINTERGARTEN",
}
COLS = ["apartment_id", "site_id", "floor_id", "unit_usage",
        "entity_type", "entity_subtype", "geometry"]


def sampled(floor_id: int) -> bool:
    h = hashlib.md5(str(int(floor_id)).encode()).digest()
    return h[0] % STRIDE == 0


def main() -> None:
    fit_floors: set[int] = set()
    if FIT.exists():
        for rec in json.loads(FIT.read_text(encoding="utf-8")):
            fit_floors.add(int(rec["k"].split("|")[1]))
    print(f"floors already fitted by ADR 0008 conversion: {len(fit_floors):,}")

    rooms: dict[tuple[int, str], list[tuple[str, str]]] = defaultdict(list)
    other: dict[tuple[int, str], list[tuple[str, str]]] = defaultdict(list)
    walls: dict[int, list[str]] = defaultdict(list)
    floors_seen: set[int] = set()
    kept_floors: set[int] = set()

    t0 = time.time()
    n_rows = 0
    for chunk in pd.read_csv(GEOM, usecols=COLS, chunksize=400_000):
        n_rows += len(chunk)
        fl = chunk.floor_id.astype("int64")
        floors_seen.update(fl.unique().tolist())
        keep_mask = fl.map(lambda f: f in fit_floors or sampled(f))
        ch = chunk[keep_mask]
        if ch.empty:
            continue
        kept_floors.update(ch.floor_id.astype("int64").unique().tolist())

        w = ch[(ch.entity_type == "separator") & (ch.entity_subtype == "WALL")]
        for f, g in zip(w.floor_id.astype("int64"), w.geometry):
            walls[f].append(g)

        a = ch[(ch.entity_type == "area")
               & (ch.unit_usage == "RESIDENTIAL")
               & ch.apartment_id.notna()]
        for f, ap, st, g in zip(a.floor_id.astype("int64"), a.apartment_id,
                                a.entity_subtype, a.geometry):
            (other if st in NOT_A_ROOM else rooms)[(f, ap)].append((st, g))

        print(f"  {n_rows:>10,} rows  {time.time() - t0:6.0f}s  "
              f"kept {len(kept_floors):,} floors", flush=True)

    print(f"\nrows: {n_rows:,}   floors in corpus: {len(floors_seen):,}   "
          f"floors kept: {len(kept_floors):,}")
    print(f"dwellings kept: {len(rooms):,}   floors with walls: {len(walls):,}")

    payload = {
        "stride": STRIDE,
        "fit_floors": sorted(fit_floors),
        "n_rows": n_rows,
        "n_floors_corpus": len(floors_seen),
        "rooms": {f"{f}|{ap}": v for (f, ap), v in rooms.items()},
        "other": {f"{f}|{ap}": v for (f, ap), v in other.items()},
        "walls": {str(f): v for f, v in walls.items()},
    }
    dest = OUT / "cache.pkl.gz"
    with gzip.open(dest, "wb", compresslevel=4) as fh:
        pickle.dump(payload, fh, protocol=5)
    print(f"wrote {dest}  ({dest.stat().st_size / 1e6:.0f} MB)  "
          f"in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
