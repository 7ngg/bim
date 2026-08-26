"""Run the hard registry against real dwellings and price every rule.

Ticket 20's second instruction: *"Every hard `engine_choice` threshold is a
candidate 99 %-rejection bug. Run the full registry against the corpora as
plans and report the per-rule rejection rate."*

Reported per rule and then jointly, because a bar is a conjunction: the number
that matters to C6's generate-many-reject-most is how many real, built Swiss
dwellings survive ALL of it.

Two rules are evaluated on the CONVERTED arm and say so, because the quantity
they bind is a rectangle's and a polygon has no rectangles: dim.min_clear_short
and dim.min_clear_long (ADR 0014 binds them per part). Every other rule here is
evaluated on the raw clear polygons.

Provenance: every number is Swiss and the shipping profile is AZ (C14). The
ergonomic floor is region-free by construction -- a body is a body -- so a
rejection against it is a real rejection, not a regional mismatch. The area caps
are Swiss market facts and are marked as such.

Run: python experiments/acceptance-thresholds/reject.py
"""
import io
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "out"
CENSUS = OUT / __import__("os").environ.get("CENSUS_FILE", "swiss_census.json")
FIT = ROOT / "experiments" / "rectangularise" / "out" / "swiss_fit_k2.json"
STD = ROOT / "data" / "standards" / "room-constraints.json"

GRID_MM, T_INT_MM = 250, 150
BATH_SPLIT_M2 = 2.4
EXEMPT_ASPECT = {"corridor", "hall", "storage"}
CIRC = {"corridor"}
WET = {"kitchen", "bathroom", "wc", "kitchen_dining"}

# Reporting class -> the ergonomic row whose floor a Space of that class must
# clear. `room*` is the collapsed {ROOM, BEDROOM, STUDIO} class: the corpus does
# not say which bedroom a room is, so the headline uses bedroom_double (the AZ
# market default) and bedroom_single is reported as the loosest sensitivity.
ERG = {
    "room*": "bedroom_double", "living": "living",
    "living_dining": "living_dining", "dining": "dining", "kitchen": "kitchen",
    "kitchen_dining": "kitchen_dining", "bathroom": "bathroom", "wc": "wc",
    "corridor": "corridor", "storage": "storage",
}
ERG_LOOSE = dict(ERG, **{"room*": "bedroom_single"})

# room-area-bands.md 6.1, absolute_cap[type] -- the p99.5 fallback used where a
# Room carries no target_area. A corpus dwelling carries none, so this is the
# branch under test.
ABS_CAP = {
    "room*": 31.09, "bathroom": 9.15, "wc": 6.20, "kitchen": 20.59,
    "living_dining": 57.12, "living": 48.12, "corridor": 24.84,
    "dining": 35.91, "storage": 18.23,
}

# Rooms whose Room type carries needs_window, read from the shipped standards.
STDDOC = json.load(io.open(STD, encoding="utf-8"))
ERG_ROOMS = STDDOC["ergonomic"]["rooms"]


def needs_window(c):
    row = ERG_ROOMS.get(ERG.get(c, ""), {})
    return bool(row.get("needs_window"))


LINES = []


def emit(s=""):
    print(s)
    LINES.append(s)


def classify_parts(t, a_m2):
    C = {"ROOM": "room*", "BEDROOM": "room*", "STUDIO": "room*",
         "LIVING_ROOM": "living", "LIVING_DINING": "living_dining",
         "DINING": "dining", "KITCHEN": "kitchen",
         "KITCHEN_DINING": "kitchen_dining", "CORRIDOR": "corridor",
         "STOREROOM": "storage"}
    if t == "BATHROOM":
        return "wc" if a_m2 < BATH_SPLIT_M2 else "bathroom"
    return C.get(t, t.lower())


def main():
    d = json.load(open(CENSUS))
    recs = d["recs"]
    N = len(recs)
    emit(f"Swiss Dwellings, {N} in-band dwellings, raw CLEAR polygons")
    emit("a dwelling is REJECTED by a rule if any Space in it fails that rule")
    emit()

    fails = defaultdict(set)          # rule id -> set of dwelling indices
    obs = defaultdict(set)            # observations that are NOT rejection tests
    detail = {}

    for i, r in enumerate(recs):
        cls, area, dim = r["cls"], r["area"], r["dim"]
        tot = sum(area)
        wins = Counter()
        for c, kind, *_ in r["jambs"]:
            if kind == "WINDOW":
                wins[c] += 1

        for c, a, (w, h) in zip(cls, area, dim):
            lo, hi = min(w, h), max(w, h)
            erow = ERG_ROOMS.get(ERG.get(c, ""), {})
            ma = erow.get("min_area", {}).get("v")
            if ma is not None and a < ma:
                fails["dim.min_area"].add(i)
            # bbox short side is an UPPER bound on the clear width, so a failure
            # here is a certain failure and the rate is a LOWER bound
            ms = erow.get("min_clear_short", {}).get("v")
            if ms is not None and lo * 1000 < ms:
                fails["dim.min_clear_short (lower bound)"].add(i)
            if c == "corridor" and lo * 1000 < 900:
                fails["dim.corridor_min_width"].add(i)
            if c not in EXEMPT_ASPECT and lo > 0 and hi / lo > 3.0:
                fails["dim.aspect_ratio_hard"].add(i)
            cap = ABS_CAP.get(c)
            if cap is not None and a > cap:
                fails["dim.max_area (absolute_cap)"].add(i)

        if tot > 0:
            cz = sum(a for c, a in zip(cls, area) if c in CIRC)
            if cz / tot > 0.30:
                fails["circ.fraction_hard"].add(i)
        if r["wet_groups"] > 2:
            fails["wet.plumbing_group_count"].add(i)
        if r["n_entrance"] < 1:
            fails["entry.exists"].add(i)
        if r["n_entrance"] > 1:
            fails["entry.single_primary (>1 exterior door)"].add(i)
        for c in set(cls):
            if needs_window(c) and wins[c] == 0:
                fails["win.habitable_has_window"].add(i)
        for _, kind, w, L, ret in r["jambs"]:
            # THE RULE AS WRITTEN: a segment-LENGTH test. It does not constrain
            # where on the run the Opening sits, only that the run is long
            # enough for it plus a return each side.
            if L < w + 2 * 0.100:
                fails["open.fits_segment (as written, 100 mm)"].add(i)
            # WHAT THE RULE IS NAMED FOR, which it does not bind: the return
            # actually achieved. Reported, never counted in the union.
            if ret < 0.100:
                obs["return achieved < 100 mm"].add(i)
            if kind != "WINDOW" and L < w + 0.150 + 0.400:
                obs["door run < w + t_int + 400 (ADR 0021 contact)"].add(i)
        # programme rules, ADR 0022 cl. 5.2
        s = set(cls)
        if not (s & {"kitchen", "kitchen_dining"}):
            fails["prog.kitchen_exists"].add(i)
        if not (s & {"bathroom", "wc"}):
            fails["prog.wc_exists"].add(i)
        if "storage" not in s:
            fails["prog.storage_exists (warn)"].add(i)

    emit(f"{'rule':44}{'dwellings':>12}{'rejected':>12}")
    emit("-" * 68)
    order = sorted(fails, key=lambda k: -len(fails[k]))
    for k in order:
        emit(f"{k:44}{len(fails[k]):>12}{len(fails[k]) / N:>11.2%}")
    detail["per_rule"] = {k: len(fails[k]) / N for k in fails}

    emit()
    emit("NOT rejection tests -- quantities no shipped rule binds, reported "
         "because a ticket downstream needs them:")
    for k in sorted(obs, key=lambda k: -len(obs[k])):
        emit(f"  {k:52}{len(obs[k]) / N:>8.2%}")
    detail["observations"] = {k: len(obs[k]) / N for k in obs}

    emit()
    hard = [k for k in fails if "warn" not in k and "lower bound" not in k
            and not k.startswith("entry.single_primary")]
    union = set().union(*[fails[k] for k in hard])
    emit(f"union of the hard rules above: {len(union) / N:.2%} of real Swiss "
         f"dwellings rejected")
    emit(f"survivors: {1 - len(union) / N:.2%}")
    emit()
    emit("the same union under this ticket's FITTED values, and under a "
         "real-pier reading of\nopen.fits_segment (runs >= 1.5 m, where an "
         "opening is not the whole wall):")
    fitted = set()
    for k in hard:
        if k == "wet.plumbing_group_count":
            continue
        fitted |= fails[k]
    wet3 = {i for i, r in enumerate(recs) if r["wet_groups"] > 3}
    emit(f"  as shipped                        {len(union) / N:>7.2%}")
    emit(f"  with wet.plumbing_group_count = 3 {len(fitted | wet3) / N:>7.2%}")
    pier = {i for i, r in enumerate(recs)
            for _, kind, w, L, ret in r["jambs"] if L >= 1.5 and L < w + 0.2}
    rest = set()
    for k in hard:
        if k in ("wet.plumbing_group_count", "open.fits_segment (as written, 100 mm)"):
            continue
        rest |= fails[k]
    emit(f"  ... and fits_segment on real piers only "
         f"{len(rest | wet3 | pier) / N:>7.2%}   "
         f"(survivors {1 - len(rest | wet3 | pier) / N:.2%})")
    emit(f"  ... and without fits_segment at all    "
         f"{len(rest | wet3) / N:>7.2%}")
    detail["union_fitted"] = len(fitted | wet3) / N
    detail["union_fitted_real_piers"] = len(rest | wet3 | pier) / N

    emit()
    emit("leave-one-out -- what the bar rejects with each rule removed:")
    for k in order:
        if k not in hard:
            continue
        rest = set().union(*[fails[j] for j in hard if j != k]) if len(hard) > 1 else set()
        emit(f"  without {k:42} {len(rest) / N:>7.2%}  "
             f"(that rule alone adds {len(union - rest) / N:.2%})")
    detail["union_hard"] = len(union) / N

    # ------------------------------------------------------- converted arm
    emit()
    emit("=" * 68)
    emit("the two rules a polygon cannot answer -- CONVERTED arm, per part, "
         "centreline eroded by t_int")
    emit("=" * 68)
    frecs = [r for r in json.load(open(FIT))
             if r.get("status") in ("OPTIMAL", "FEASIBLE") and r.get("parts")
             and r.get("types") and len(r["parts"]) == len(r["types"])]
    M = len(frecs)
    f2 = defaultdict(set)
    for i, r in enumerate(frecs):
        for p, t in zip(r["parts"], r["types"]):
            a_m2 = sum((x1 - x0) * (y1 - y0) for x0, y0, x1, y1 in p) \
                * (GRID_MM / 1000.0) ** 2
            c = classify_parts(t, a_m2)
            erow = ERG_ROOMS.get(ERG.get(c, ""), {})
            ms = erow.get("min_clear_short", {}).get("v")
            ml = erow.get("min_clear_long", {}).get("v")
            for x0, y0, x1, y1 in p:
                w = (x1 - x0) * GRID_MM - T_INT_MM
                h = (y1 - y0) * GRID_MM - T_INT_MM
                lo, hi = min(w, h), max(w, h)
                if ms is not None and lo < ms:
                    f2["dim.min_clear_short"].add(i)
                if ml is not None and hi < ml:
                    f2["dim.min_clear_long"].add(i)
                if c not in EXEMPT_ASPECT and lo > 0 and hi / lo > 3.0:
                    f2["dim.aspect_ratio_hard (per part)"].add(i)
    emit(f"{'rule':44}{'dwellings':>12}{'rejected':>12}")
    emit("-" * 68)
    for k in sorted(f2, key=lambda k: -len(f2[k])):
        emit(f"{k:44}{len(f2[k]):>12}{len(f2[k]) / M:>11.2%}")
    emit(f"\n(converted population, {M} dwellings -- 9.74 % thinner than the raw "
         f"corpus\n and under-representing the store-heavy and bedroom-heavy "
         f"dwelling, ADR 0016)")
    detail["converted_arm"] = {k: len(f2[k]) / M for k in f2}

    # sensitivity: room* as bedroom_single
    emit()
    emit("sensitivity -- `room*` read as bedroom_single (the loosest bedroom "
         "floor) instead of bedroom_double:")
    for label, table in (("min_area", ERG_LOOSE),):
        cnt = set()
        for i, r in enumerate(recs):
            for c, a in zip(r["cls"], r["area"]):
                erow = ERG_ROOMS.get(table.get(c, ""), {})
                ma = erow.get("min_area", {}).get("v")
                if ma is not None and a < ma:
                    cnt.add(i)
        emit(f"  dim.{label}: {len(cnt) / N:.2%}  "
             f"(against {len(fails['dim.min_area']) / N:.2%} at bedroom_double)")
        detail["min_area_bedroom_single"] = len(cnt) / N

    (OUT / "reject.txt").write_text("\n".join(LINES), encoding="utf-8")
    json.dump(detail, open(OUT / "reject.json", "w"), indent=1)
    print(f"\nwrote {OUT / 'reject.txt'}")


if __name__ == "__main__":
    main()
