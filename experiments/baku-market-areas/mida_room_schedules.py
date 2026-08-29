"""Independent recomputation of the MIDA per-room statistics from the crawl of
api.mida.gov.az/api/front/getApartment/{id}.

Input: out/mida_types.json -- one record per MIDA apartment TYPE, each carrying
`internal` (net internal area), `external` (external-perimeter area), `nrooms`
(MIDA's otaq count) and `rooms` (the published eksplikasiya: name + m2 + order).

The input is a harvest of MIDA's public JSON API and lives under out/, which is
gitignored: it is DATA, not a document, and the repo does not redistribute
third-party material. Regenerate it by walking

    GET https://api.mida.gov.az/api/front/getProjectPlans      -> project ids
    GET https://api.mida.gov.az/api/front/getProjectPlan/{id}  -> project detail
    ... -> sectors -> sector floors -> sector floor apartments -> apartment ids
    GET https://api.mida.gov.az/api/front/getApartment/{id}    -> the schedule

The last endpoint is the one that matters and is the one verified first-hand:
its `internal_size` equals the sum of its own room schedule, which is what fixes
the measurement plane as net internal. The five populated Baku projects at the
time of the harvest were 300001 Hovsan, 300004 Yasamal, 100001 Yasamal 2,
300005 Hovsan 2, 300019 Binaqadi (see out/mida_crawl_stats.json). Four further
announced projects returned zero sectors.

Unit of analysis is the DISTINCT PLAN GEOMETRY, keyed on the exact multiset of
(room name, area). MIDA repeats one plan across floors and entrances, so counting
type rows would weight a repeated plan up to 60x -- the same replication defect
that destroys the Swiss KITCHEN_DINING median (findings note SS4.2).
"""
import json, os, sys, statistics as st
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("MIDA_TYPES", os.path.join(HERE, "out", "mida_types.json"))
sys.stdout.reconfigure(encoding="utf-8")

recs = list(json.load(open(SRC, encoding="utf-8")).values())
print(f"type records: {len(recs)}")

# --- sanity filter -------------------------------------------------------
def sane(r):
    if not r.get("rooms") or not r.get("internal"):
        return False
    if r["internal"] <= 0 or r["internal"] > 400:
        return False
    HAB = {"Qonaq otağı", "Yataq otağı", "Mətbəx-studio", "Studio"}
    for x in r["rooms"]:
        if not (0 < x["sq"] <= 200):
            return False
        if "test" in x["n"].lower():
            return False
        # placeholder rows: a habitable room or kitchen recorded at a token area.
        # The ergonomic layer floors the smallest of these at 1,8 m2, so a
        # sub-4 m2 living room or bedroom is data entry, not a room.
        if x["n"] in HAB | {"Mətbəx"} and x["sq"] < 4.0:
            return False
        if x["n"] == "Dəhliz" and x["sq"] < 1.5:
            return False
    # must contain at least one habitable room
    return any(x["n"] in HAB for x in r["rooms"])

ok = [r for r in recs if sane(r)]
print(f"after sanity filter: {len(ok)}")

# --- collapse to distinct plan geometries --------------------------------
plans = {}
for r in ok:
    key = tuple(sorted((x["n"], round(x["sq"], 2)) for x in r["rooms"]))
    plans.setdefault(key, r)
plans = list(plans.values())
print(f"distinct plan geometries: {len(plans)}\n")

def q(v):
    v = sorted(v)
    p = lambda f: v[min(len(v) - 1, int(f * (len(v) - 1)))]
    return (round(v[0], 2), round(p(.25), 2), round(st.median(v), 2),
            round(p(.75), 2), round(v[-1], 2))

# --- per-room-type distributions, over distinct plans --------------------
per = defaultdict(list)
nplans = Counter()
for r in plans:
    seen = Counter()
    for x in r["rooms"]:
        per[x["n"]].append(x["sq"])
        seen[x["n"]] += 1
    for k in seen:
        nplans[k] += 1

print("room type                     plans  rooms |    min    p25    MED    p75    max")
for name, vals in sorted(per.items(), key=lambda kv: -len(kv[1])):
    if len(vals) < 5:
        continue
    a, b, c, d, e = q(vals)
    print(f"{name:28s} {nplans[name]:6d} {len(vals):6d} | {a:6.2f} {b:6.2f} {c:6.2f} {d:6.2f} {e:6.2f}")

# --- by otaq count --------------------------------------------------------
print("\notaq  plans |  internal net (min/p25/MED/p75/max)      | MED excl. balcony | MED external | ext/int")
by = defaultdict(list)
for r in plans:
    by[r["nrooms"]].append(r)
for n in sorted(by):
    g = by[n]
    if len(g) < 3:
        continue
    ints = [r["internal"] for r in g]
    nob = [r["internal"] - sum(x["sq"] for x in r["rooms"] if x["n"] == "Eyvan") for r in g]
    ext = [r["external"] for r in g if r.get("external")]
    ratio = [r["external"] / r["internal"] for r in g if r.get("external")]
    a, b, c, d, e = q(ints)
    print(f"{n:4d} {len(g):6d} | {a:6.2f} {b:6.2f} {c:6.2f} {d:6.2f} {e:6.2f} |"
          f" {st.median(nob):17.2f} | {st.median(ext):12.2f} | {st.median(ratio):.3f}")

# --- the open-plan room ---------------------------------------------------
print("\n-- Metbex-studio (MIDA's open-plan kitchen-living-dining) --")
studio_plans = [r for r in plans if any(x["n"] == "Mətbəx-studio" for x in r["rooms"])]
print(f"plan geometries containing it: {len(studio_plans)} of {len(plans)}"
      f"  ({100*len(studio_plans)/len(plans):.2f} %)")
multi = [r for r in studio_plans if r["nrooms"] >= 2]
print(f"of which multi-room (nrooms >= 2): {len(multi)}")
sv = [x["sq"] for r in studio_plans for x in r["rooms"] if x["n"] == "Mətbəx-studio"]
if sv:
    print(f"area  min/p25/MED/p75/max: {q(sv)}   n={len(sv)}")
print(f"total distinct MIDA room names: {len(per)}")
kd = [n for n in per if "yemək" in n.lower()]
print(f"room names containing 'yemək' (dining): {kd if kd else 'NONE'}")

# --- compliance against the norm the profile ships -----------------------
print("\n-- MIDA plans against AzDTN 2.7-2 cl. 5.7, over distinct plans --")
def share(pred, sel):
    g = [r for r in plans if sel(r)]
    return (sum(1 for r in g if pred(r)), len(g))
k = share(lambda r: all(x["sq"] >= 8 for x in r["rooms"] if x["n"] == "Mətbəx"),
          lambda r: any(x["n"] == "Mətbəx" for x in r["rooms"]))
print(f"kitchen >= 8,0 m2      : {k[0]}/{k[1]} = {100*k[0]/k[1]:.1f} %")
lv = share(lambda r: all(x["sq"] >= 16 for x in r["rooms"] if x["n"] == "Qonaq otağı"),
           lambda r: r["nrooms"] >= 2 and any(x["n"] == "Qonaq otağı" for x in r["rooms"]))
print(f"living >= 16,0 m2 (2+) : {lv[0]}/{lv[1]} = {100*lv[0]/lv[1]:.1f} %")
bd = share(lambda r: all(x["sq"] >= 8 for x in r["rooms"] if x["n"] == "Yataq otağı"),
           lambda r: any(x["n"] == "Yataq otağı" for x in r["rooms"]))
print(f"bedroom >= 8,0 m2      : {bd[0]}/{bd[1]} = {100*bd[0]/bd[1]:.1f} %")

# --- the comparison the research question asks for ------------------------
print("\n-- AZ market_default against the MIDA published schedules --")
print("cell                      target | MIDA class          plans rooms   p25    MED    p75 | below | MED/target")
CMP = [("living_room_2plus", 16.0, "Qonaq otağı"),
       ("bedroom_single", 9.0, "Yataq otağı"),
       ("bedroom_double", 12.0, "Yataq otağı"),
       ("kitchen", 9.0, "Mətbəx"),
       ("bathroom", 3.2, "Sanitar qovşağı"),
       ("bathroom_combined", 3.8, "Sanitar qovşağı"),
       ("kitchen_zone_in_diner", 6.0, "Mətbəx-studio")]
for cell, t, cls in CMP:
    v = per.get(cls, [])
    if not v:
        continue
    a, b, c, d, e = q(v)
    below = 100 * sum(1 for x in v if x < t) / len(v)
    print(f"{cell:24s} {t:6.1f} | {cls:18s} {nplans[cls]:5d} {len(v):5d} "
          f"{b:6.2f} {c:6.2f} {d:6.2f} | {below:5.1f}% | {c/t:.2f}")
