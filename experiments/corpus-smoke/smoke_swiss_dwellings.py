"""Swiss Dwellings loader smoke test + the blocking per-dwelling area histogram.



Answers ticket 12's inventory questions and ticket 18 §3.2's blocking query:

how many C5-surviving dwellings hold >=16 areas?



Run: python experiments/corpus-smoke/smoke_swiss_dwellings.py

"""



from collections import Counter

from pathlib import Path



import pandas as pd



ROOT = Path(__file__).resolve().parents[2]

GEOM = ROOT / "data" / "corpora" / "swiss-dwellings" / "swiss-dwellings-v3.0.0" / "geometries.csv"



IDS = ["apartment_id", "site_id", "building_id", "plan_id", "floor_id",

       "unit_usage", "entity_type", "entity_subtype"]



# Areas that are rooms of a dwelling. Everything else (shafts, voids, balconies

# that are not enclosed) is counted separately so the histogram can be re-keyed

# without re-reading a 1 GB file.

# Not rooms of a dwelling: vertical service voids, circulation cores, and

# anything outdoors. A Brief never asks for one and the proposer never emits one.

NOT_A_ROOM = {

    "SHAFT", "VOID", "OUTDOOR_VOID", "LIGHTWELL", "ELEVATOR", "STAIRCASE",

    "TECHNICAL_AREA", "BALCONY", "LOGGIA", "TERRACE", "GARDEN", "PATIO",

    "WINTERGARTEN",

}

# The subset a Homeowner would actually name in a Brief.

HABITABLE = {

    "ROOM", "BEDROOM", "LIVING_ROOM", "LIVING_DINING", "DINING", "KITCHEN",

    "KITCHEN_DINING", "BATHROOM", "STUDIO",

}





def main() -> None:

    rows = 0

    ent = Counter()

    sub_by_ent = {}

    usage = Counter()

    # (site, floor, apartment) -> n areas, and the same keyed the way ticket 18 wrote it

    per_sfa = Counter()

    per_sa = Counter()

    per_a = Counter()

    per_rooms = Counter()    # interior rooms only - no shafts, no outdoor, no cores

    per_hab = Counter()      # habitable only - the Brief's own room list

    apt_floors = {}          # apartment_id -> set of floor_id

    apt_sites = {}           # apartment_id -> set of site_id

    area_subtypes = Counter()



    reader = pd.read_csv(GEOM, usecols=IDS, chunksize=1_000_000, dtype=str)

    for chunk in reader:

        rows += len(chunk)

        ent.update(chunk["entity_type"].value_counts().to_dict())

        usage.update(chunk["unit_usage"].fillna("<NA>").value_counts().to_dict())

        for et, grp in chunk.groupby("entity_type", observed=True):

            d = sub_by_ent.setdefault(et, Counter())

            d.update(grp["entity_subtype"].fillna("<NA>").value_counts().to_dict())



        areas = chunk[(chunk["entity_type"] == "area") &

                      (chunk["unit_usage"] == "RESIDENTIAL")]

        area_subtypes.update(areas["entity_subtype"].fillna("<NA>").value_counts().to_dict())

        per_sfa.update(Counter(zip(areas["site_id"], areas["floor_id"], areas["apartment_id"])))

        per_sa.update(Counter(zip(areas["site_id"], areas["apartment_id"])))

        per_a.update(Counter(areas["apartment_id"]))

        interior = areas[~areas["entity_subtype"].isin(NOT_A_ROOM)]

        per_rooms.update(Counter(zip(interior["site_id"], interior["floor_id"],

                                     interior["apartment_id"])))

        hab = areas[areas["entity_subtype"].isin(HABITABLE)]

        per_hab.update(Counter(zip(hab["site_id"], hab["floor_id"], hab["apartment_id"])))

        for a, f, s in zip(areas["apartment_id"], areas["floor_id"], areas["site_id"]):

            apt_floors.setdefault(a, set()).add(f)

            apt_sites.setdefault(a, set()).add(s)



    print(f"geometries.csv rows: {rows:,}")

    print(f"entity_type: {dict(ent)}")

    print(f"unit_usage:  {dict(usage)}")

    for et in sorted(sub_by_ent):

        top = dict(sub_by_ent[et].most_common(12))

        print(f"  {et} subtypes ({len(sub_by_ent[et])}): {top}")



    print(f"\nresidential area rows: {sum(per_sfa.values()):,}")

    print(f"distinct apartment_id (residential):        {len(per_a):,}")

    print(f"distinct (site,apartment):                  {len(per_sa):,}")

    print(f"distinct (site,floor,apartment) = dwellings {len(per_sfa):,}")

    multi = sum(1 for a, fs in apt_floors.items() if len(fs) > 1)

    print(f"apartment_ids spanning >1 floor_id: {multi:,}")

    multis = sum(1 for a, ss in apt_sites.items() if len(ss) > 1)

    print(f"apartment_ids spanning >1 site_id:  {multis:,}")



    print(f"\narea subtypes (residential), {len(area_subtypes)} distinct:")

    for k, v in area_subtypes.most_common():

        print(f"    {k:<28} {v:>8,}")



    for name, counter in (("(site,floor,apartment), all residential areas", per_sfa),
                          ("(site,apartment) - ticket 18 key, all areas", per_sa),
                          ("(site,floor,apartment), interior rooms only", per_rooms),
                          ("(site,floor,apartment), habitable only", per_hab)):

        hist = Counter(counter.values())

        n = len(counter)

        tail16 = sum(v for k, v in hist.items() if k >= 16)

        tail20 = sum(v for k, v in hist.items() if k >= 20)

        tail24 = sum(v for k, v in hist.items() if k >= 24)

        mean = sum(k * v for k, v in hist.items()) / n

        print(f"\n=== per-dwelling area histogram, keyed {name} ===")

        print(f"dwellings: {n:,}   mean areas/dwelling: {mean:.2f}   max: {max(hist)}")

        for k in sorted(hist):

            if k <= 30 or hist[k] > 0:

                print(f"  {k:>3} areas : {hist[k]:>7,}")

        print(f"  >=16 areas: {tail16:,}   >=20: {tail20:,}   >=24: {tail24:,}")





if __name__ == "__main__":

    main()

