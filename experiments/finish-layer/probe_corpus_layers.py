"""Ticket 35 item 4 — does either corpus record a FINISH layer separately
from a structural one?

Swiss Dwellings v3.0.0: stream geometries.csv, tally (entity_type,
entity_subtype) and, for wall-ish entities, the distribution of wall
thickness derived from the polygon. We are looking for evidence that a
single physical wall is stored as MORE THAN ONE stacked entity (a core
plus a finish skin), or that any subtype names a finish/render/plaster.

ResPlan: inspect the pickle's record schema for any layer/finish field.

Read-only. Writes nothing outside experiments/finish-layer/out/.
"""
import csv, sys, os, collections, json

SD = os.path.join("data", "corpora", "swiss-dwellings",
                  "swiss-dwellings-v3.0.0", "geometries.csv")
OUT = os.path.join("experiments", "finish-layer", "out")
os.makedirs(OUT, exist_ok=True)
csv.field_size_limit(10**9)

def main():
    pairs = collections.Counter()
    n = 0
    with open(SD, newline="", encoding="utf-8") as fh:
        r = csv.DictReader(fh)
        for row in r:
            n += 1
            pairs[(row["entity_type"], row["entity_subtype"])] += 1
    print(f"rows: {n}")
    print(f"distinct (entity_type, entity_subtype): {len(pairs)}")
    for (t, s), c in sorted(pairs.items(), key=lambda kv: -kv[1]):
        print(f"  {c:>10}  {t:<20} {s}")
    with open(os.path.join(OUT, "sd_entity_pairs.json"), "w", encoding="utf-8") as fh:
        json.dump({f"{t}|{s}": c for (t, s), c in pairs.items()}, fh,
                  indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
