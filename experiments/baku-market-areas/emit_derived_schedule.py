# -*- coding: utf-8 -*-
"""Emit the COMMITTED derived MIDA schedule from the gitignored raw harvest.

Ticket 73 / ADR 0035 moved four shipped `market_default` constants onto this
population, so it stopped being research colour and became the source of values
the engine targets. Every measured number on this map is meant to be
reproducible from pinned inputs -- the posture `requirements.lock.txt` is held
to -- and the raw harvest is under `out/`, which is gitignored.

WHAT IS COMMITTED AND WHY THAT LINE. This writes `mida_plans_318.json`: the 318
DISTINCT PLAN GEOMETRIES, which is the unit of analysis every published
statistic is computed over. It is one derivation step from MIDA's own tables
rather than a mirror of them, which is what `minima.md` SS7.1's copyright posture
asks for -- the posture forbids reproducing published tables wholesale, and the
raw harvest (5 954 type records, one row per apartment) is exactly that.

WHAT THIS COSTS, STATED RATHER THAN HIDDEN. The deduplication is load-bearing --
MIDA repeats one plan across floors and entrances up to 60x, and counting type
rows reproduces the replication artefact that destroys the Swiss KITCHEN_DINING
median (findings SS4.2). Committing the deduplicated output means the dedup
itself CANNOT BE RE-AUDITED once the endpoint dies. The md5 of the raw harvest is
recorded here so a future re-crawl can be compared against the one the constants
were fitted on; if it differs, the population moved and the cells must be
re-read, not patched.

Run:  ./venv/Scripts/python.exe experiments/baku-market-areas/emit_derived_schedule.py
"""
import hashlib
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "out", "mida_types.json")
OUT = os.path.join(HERE, "mida_plans_318.json")
STATS = os.path.join(HERE, "out", "mida_crawl_stats.json")

HAB = {"Qonaq otağı", "Yataq otağı", "Mətbəx-studio", "Studio"}


def sane(r):
    """The filter mida_room_schedules.py applies, restated so this file stands alone."""
    if not r.get("rooms") or not r.get("internal"):
        return False
    if r["internal"] <= 0 or r["internal"] > 400:
        return False
    for x in r["rooms"]:
        if not (0 < x["sq"] <= 200):
            return False
        if "test" in x["n"].lower():
            return False
        if x["n"] in HAB | {"Mətbəx"} and x["sq"] < 4.0:
            return False
        if x["n"] == "Dəhliz" and x["sq"] < 1.5:
            return False
    return any(x["n"] in HAB for x in r["rooms"])


def main():
    if not os.path.exists(RAW):
        raise SystemExit(
            "out/mida_types.json is absent. It is gitignored by design; re-crawl it with the "
            "endpoint chain in mida_room_schedules.py's docstring, then compare the md5 below."
        )
    raw_bytes = open(RAW, "rb").read()
    md5 = hashlib.md5(raw_bytes).hexdigest()
    recs = list(json.loads(raw_bytes.decode("utf-8")).values())
    kept = [r for r in recs if sane(r)]

    seen = {}
    for r in kept:
        key = tuple(sorted((x["n"], round(x["sq"], 2)) for x in r["rooms"]))
        seen.setdefault(key, r)

    plans = []
    for r in seen.values():
        plans.append({
            "nrooms": r.get("nrooms"),
            "internal": round(r["internal"], 2),
            "external": round(r["external"], 2) if r.get("external") else None,
            "rooms": [{"n": x["n"], "sq": round(x["sq"], 2)} for x in sorted(
                r["rooms"], key=lambda x: x.get("order", 0))],
        })
    plans.sort(key=lambda p: (p["nrooms"] if p["nrooms"] is not None else -1, p["internal"]))

    doc = {
        "id": "mida_plans_318",
        "what": "Distinct Baku plan geometries published by MIDA, deduplicated. The unit of analysis for every "
                "az_mida_2026 statistic in data/standards/room-constraints.json.",
        "source": "az_mida_2026 (see data/standards/room-constraints.json #/sources)",
        "plane": "net internal; each plan's room areas sum to its own `internal` to the cent",
        "provenance": {
            "raw_harvest": "experiments/baku-market-areas/out/mida_types.json (gitignored, NOT redistributed)",
            "raw_md5": md5,
            "raw_type_records": len(recs),
            "after_sanity_filter": len(kept),
            "distinct_plan_geometries": len(plans),
            "dedup_key": "exact multiset of (room name, area rounded to 0,01 m2)",
            "dedup_is_not_re_auditable_without_the_raw": True,
            "crawl_stats": json.load(open(STATS, encoding="utf-8")) if os.path.exists(STATS) else None,
        },
        "plans": plans,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("raw md5           : %s" % md5)
    print("type records      : %d" % len(recs))
    print("after sanity      : %d" % len(kept))
    print("distinct plans    : %d" % len(plans))
    print("written           : %s (%.1f KB)" % (OUT, os.path.getsize(OUT) / 1024))


if __name__ == "__main__":
    main()
