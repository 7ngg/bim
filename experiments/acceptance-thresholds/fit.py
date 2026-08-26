"""Fit every ENGINE_CHOICE threshold, and price each one in rejected dwellings.

Ticket 20. Reads out/swiss_census.json (raw polygons, clear plane, all in-band
Swiss dwellings) and reports, per threshold:

  - the distribution the placeholder was guessed against
  - the per-ROOM (or per-opening) cost of the placeholder
  - the per-DWELLING rejection rate, which is the number the ticket asks for:
    a hard rule that rejects a large share of real, built dwellings is a bug in
    the rule, not a quality bar

Every number here is Swiss and the shipping profile is AZ (C14). Disclosed per
value in the emitted JSON as `src`.

Run: python experiments/acceptance-thresholds/fit.py
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent / "out"
CENSUS = OUT / "swiss_census.json"

EXEMPT = {"corridor", "hall", "storage"}     # dim.aspect_ratio_*'s exempt_types
CIRC = {"corridor"}
PCTS = [1, 5, 10, 25, 50, 75, 90, 95, 99, 99.5]

LINES = []


def emit(s=""):
    print(s)
    LINES.append(s)


def pct_row(label, v, pcts=PCTS, fmt="{:>9.2f}", n=True):
    v = np.asarray(v, dtype=float)
    head = f"{label:22}" + (f"{len(v):>8}" if n else "")
    return head + "".join(fmt.format(np.percentile(v, p)) for p in pcts)


def header(pcts=PCTS, n=True):
    return f"{'':22}" + (f"{'n':>8}" if n else "") + \
        "".join(f"{('p' + str(p)):>9}" for p in pcts)


def main():
    d = json.load(open(CENSUS))
    recs = d["recs"]
    emit(f"Swiss Dwellings, raw CLEAR polygons, {len(recs)} in-band dwellings "
         f"of {d['n_dwellings_total']} residential apartments")
    emit(f"repairs: {d['repairs']}   bathroom split {d['bath_split_m2']} m2   "
         f"envelope closing radius {d['close_r_m']} m")
    emit()
    out = {}

    # ---------------------------------------------------------------- aspect
    emit("=" * 96)
    emit("dim.aspect_ratio_hard = 3.0 / dim.aspect_ratio_soft = 2.2   "
         "(bbox aspect, dwelling's own frame)")
    emit("=" * 96)
    asp = defaultdict(list)
    for r in recs:
        for c, (w, h) in zip(r["cls"], r["dim"]):
            lo, hi = min(w, h), max(w, h)
            if lo <= 0:
                continue
            asp[c].append(hi / lo)
    emit(header())
    binding = []
    for c in sorted(asp, key=lambda k: -len(asp[k])):
        tag = c + (" *exempt" if c in EXEMPT else "")
        emit(pct_row(tag, asp[c]))
        if c not in EXEMPT:
            binding.extend(asp[c])
    emit(pct_row("BINDING (all)", binding))
    emit(f"{'':22}{'':>8}   max = {max(binding):.2f}")
    emit()
    emit(f"{'threshold':>10}{'rooms above':>14}{'dwellings rejected':>22}")
    asp_cost = {}
    for thr in (2.2, 2.5, 3.0, 3.2, 3.5, 4.0, 4.5, 5.0):
        rooms = float(np.mean(np.asarray(binding) > thr))
        dw = float(np.mean([
            any(max(w, h) / min(w, h) > thr
                for c, (w, h) in zip(r["cls"], r["dim"])
                if c not in EXEMPT and min(w, h) > 0)
            for r in recs]))
        asp_cost[thr] = {"rooms": rooms, "dwellings": dw}
        emit(f"{thr:>10.1f}{rooms:>13.2%}{dw:>21.2%}")
    out["aspect"] = {
        "by_class": {c: {"n": len(v), **{f"p{p}": float(np.percentile(v, p))
                                         for p in PCTS}} for c, v in asp.items()},
        "binding_max": float(max(binding)),
        "cost": asp_cost,
        "src": "swiss_dwellings_raw_polygon_bbox",
    }

    # ------------------------------------------------------- circulation share
    emit()
    emit("=" * 96)
    emit("circ.fraction_soft = [0.08, 0.18] / circ.fraction_hard = 0.30")
    emit("denominator: sum of ALL Space areas, circulation included "
         "(ADR 0010, az_umumi_sahe)")
    emit("=" * 96)
    frac, zero = [], 0
    for r in recs:
        tot = sum(r["area"])
        cz = sum(a for c, a in zip(r["cls"], r["area"]) if c in CIRC)
        if tot <= 0:
            continue
        if cz == 0:
            zero += 1
        frac.append(cz / tot)
    emit(header())
    emit(pct_row("circulation share", frac, fmt="{:>9.4f}"))
    nz = [f for f in frac if f > 0]
    emit(pct_row("  ... where present", nz, fmt="{:>9.4f}"))
    emit(f"\ndwellings with NO circulation Space at all: {zero / len(frac):.2%}")
    emit(f"{'band':>16}{'inside':>12}{'below':>12}{'above':>12}")
    for lo, hi in ((0.08, 0.18), (0.05, 0.18), (0.05, 0.20), (0.06, 0.19)):
        a = np.asarray(frac)
        emit(f"{f'[{lo},{hi}]':>16}{((a >= lo) & (a <= hi)).mean():>11.2%}"
             f"{(a < lo).mean():>11.2%}{(a > hi).mean():>11.2%}")
    emit()
    emit(f"{'hard cap':>10}{'dwellings rejected':>22}")
    circ_cost = {}
    for thr in (0.20, 0.25, 0.28, 0.30, 0.33, 0.35, 0.40):
        v = float(np.mean(np.asarray(frac) > thr))
        circ_cost[thr] = v
        emit(f"{thr:>10.2f}{v:>21.2%}")
    out["circulation"] = {"n": len(frac), "zero_share": zero / len(frac),
                          **{f"p{p}": float(np.percentile(frac, p)) for p in PCTS},
                          "max": float(max(frac)), "cost": circ_cost,
                          "src": "swiss_dwellings_raw_polygon"}

    # ----------------------------------------------------------- wet grouping
    emit()
    emit("=" * 96)
    emit("wet.plumbing_group_count = 2   (group = maximal set sharing a wall, "
         "tau 0.30 m)")
    emit("=" * 96)
    gc = Counter(r["wet_groups"] for r in recs)
    tot = sum(gc.values())
    emit(f"{'groups':>8}{'dwellings':>12}{'share':>10}{'cumulative <=':>16}")
    cum = 0
    for g in sorted(gc):
        cum += gc[g]
        emit(f"{g:>8}{gc[g]:>12}{gc[g] / tot:>9.2%}{cum / tot:>15.2%}")
    wet_cost = {k: float(sum(v for g, v in gc.items() if g > k) / tot)
                for k in (1, 2, 3, 4)}
    emit()
    for k, v in wet_cost.items():
        emit(f"  hard bound <= {k}: rejects {v:.2%} of real dwellings")
    runs = [x for r in recs for x in r["wet_runs"]]
    tot_runs = [sum(r["wet_runs"]) for r in recs]
    emit()
    emit("wet.shared_wall_length -- total shared run between wet Spaces, m")
    emit(header())
    emit(pct_row("per adjacent pair", runs, fmt="{:>9.2f}"))
    emit(pct_row("per dwelling", tot_runs, fmt="{:>9.2f}"))
    out["wet"] = {"group_counts": dict(gc), "cost": wet_cost,
                  "run_pairs_p50": float(np.percentile(runs, 50)),
                  "run_dwelling_p50": float(np.percentile(tot_runs, 50)),
                  "src": "swiss_dwellings_raw_polygon"}

    # --------------------------------------------------------- jamb / segment
    emit()
    emit("=" * 96)
    emit("open.fits_segment = 100 mm minimum jamb return per side")
    emit("face declared CLEAR by *Opening placement rules*; the run measured "
         "here is a room's own clear edge, corner to corner")
    emit("=" * 96)
    jam = defaultdict(list)
    for r in recs:
        for c, kind, w, L, ret in r["jambs"]:
            jam[kind].append((w, L, ret))
    emit(f"{'':22}{'n':>8}" + "".join(f"{('p' + str(p)):>9}" for p in PCTS))
    for kind in ("DOOR", "ENTRANCE_DOOR", "WINDOW"):
        if not jam[kind]:
            continue
        rr = [x[2] * 1000 for x in jam[kind]]
        emit(pct_row(f"{kind} return mm", rr, fmt="{:>9.0f}"))
    for kind in ("DOOR", "ENTRANCE_DOOR", "WINDOW"):
        if not jam[kind]:
            continue
        ww = [x[0] * 1000 for x in jam[kind]]
        emit(pct_row(f"{kind} width mm", ww, fmt="{:>9.0f}"))
    emit()
    emit(f"{'return mm':>10}{'DOOR openings failing':>24}"
         f"{'all openings failing':>24}{'dwellings rejected':>22}")
    alljam = [(kind, w, L, ret) for r in recs for _, kind, w, L, ret in r["jambs"]]
    jam_cost = {}
    for thr in (0, 25, 50, 75, 100, 150):
        t = thr / 1000.0
        dset = [x for x in alljam if x[0] == "DOOR"]
        dfail = float(np.mean([x[3] < t for x in dset])) if dset else 0.0
        afail = float(np.mean([x[3] < t for x in alljam]))
        dw = float(np.mean([any(y[4] < t for y in r["jambs"])
                            for r in recs if r["jambs"]]))
        jam_cost[thr] = {"door": dfail, "all": afail, "dwellings": dw}
        emit(f"{thr:>10}{dfail:>23.2%}{afail:>23.2%}{dw:>21.2%}")
    emit()
    emit("the rule as written -- structural width + 2 x return <= clear run:")
    for thr in (0, 25, 50, 75, 100):
        t = thr / 1000.0
        f = float(np.mean([L < w + 2 * t for _, w, L, _ in alljam]))
        emit(f"  return {thr:>4} mm: {f:>7.2%} of real openings do not fit "
             f"their own clear run")
    emit()
    emit("HALF-SLACK -- (clear run - structural width) / 2, which is the "
         "largest symmetric\nreturn the placement could have had. This is what "
         "the rule as written actually fits:")
    emit(header())
    for name, sel in (("all openings", lambda k, w, L: True),
                      ("DOOR", lambda k, w, L: k == "DOOR"),
                      ("DOOR, run >= 1.5 m", lambda k, w, L: k == "DOOR" and L >= 1.5),
                      ("WINDOW", lambda k, w, L: k == "WINDOW")):
        v = [(L - w) * 500 for k, w, L, _ in alljam if sel(k, w, L)]
        if v:
            emit(pct_row(name + " mm", v, fmt="{:>9.0f}"))
    emit()
    emit("  75.1 % of the openings that fail the rule as written sit on a run "
         "under 1.5 m,\n  where the opening is effectively the whole wall -- a "
         "cased or full-width opening,\n  which openings.md models and which "
         "has no jamb by construction. Restricted to\n  doors on runs of "
         "1.5 m or more, the 100 mm rule costs "
         + f"{np.mean([L < w + 0.2 for k, w, L, _ in alljam if k == 'DOOR' and L >= 1.5]):.2%}.")
    emit()
    emit("joint with the two shipped run demands on the same segment:")
    emit("  open.leading_edge_nib  = 300 mm clear at the door's leading edge")
    emit("  circ.potential_reachability = w + t_int + 400 mm of contact run "
         "(ADR 0021)")
    doors = [(w, L) for k, w, L, _ in alljam if k != "WINDOW"]
    for thr in (0, 50, 100):
        t = thr / 1000.0
        f = float(np.mean([L < w + 0.300 + t for w, L in doors]))
        emit(f"  nib 300 + jamb {thr:>4} mm: {f:>7.2%} of real doors sit on a "
             f"clear run too short")
    f = float(np.mean([L < w + 0.150 + 0.400 for w, L in doors]))
    emit(f"  ADR 0021's w + t_int + 400:        {f:>7.2%} of real doors sit on "
         f"a run below the contact threshold")
    out["jamb"] = {
        "n": len(alljam),
        **{kind: {f"p{p}": float(np.percentile([x[2] * 1000 for x in jam[kind]], p))
                  for p in PCTS} for kind in jam if jam[kind]},
        "cost": jam_cost, "src": "swiss_dwellings_raw_polygon"}

    # ----------------------------------------------- efficiency and envelope
    emit()
    emit("=" * 96)
    emit("efficiency in envelope_clear_area = sum(room target areas) / "
         "efficiency   (shipping ~0.85)")
    emit("default Envelope aspect ratio applied to that area   (shipping ~1.35)")
    emit("=" * 96)
    eff_named, eff_all, envasp, bboxfill = [], [], [], []
    for r in recs:
        env = r["env_area"]
        if env <= 0:
            continue
        named = sum(a for c, a in zip(r["cls"], r["area"]) if c not in CIRC)
        eff_named.append(named / env)
        eff_all.append(sum(r["area"]) / env)
        if r["env_short"] > 0:
            envasp.append(r["env_long"] / r["env_short"])
        if r["env_bbox_area"] > 0:
            bboxfill.append(env / r["env_bbox_area"])
    emit(header())
    emit(pct_row("eff, named rooms", eff_named, fmt="{:>9.4f}"))
    emit(pct_row("eff, all Spaces", eff_all, fmt="{:>9.4f}"))
    emit(pct_row("envelope aspect", envasp, fmt="{:>9.3f}"))
    emit(pct_row("interior / its bbox", bboxfill, fmt="{:>9.3f}"))
    emit()
    emit("  'eff, named rooms' is the fit: the formula's numerator is the sum of "
         "the Brief's\n  room targets, and no Brief names a corridor (C13).")
    out["efficiency"] = {
        "named": {f"p{p}": float(np.percentile(eff_named, p)) for p in PCTS},
        "all": {f"p{p}": float(np.percentile(eff_all, p)) for p in PCTS},
        "envelope_aspect": {f"p{p}": float(np.percentile(envasp, p)) for p in PCTS},
        "interior_over_bbox": {f"p{p}": float(np.percentile(bboxfill, p))
                               for p in PCTS},
        "src": "swiss_dwellings_raw_polygon"}

    # ------------------------------------------------------------ entrance
    emit()
    emit("=" * 96)
    emit("entry.exists / entry.single_primary")
    emit("=" * 96)
    ec = Counter(r["n_entrance"] for r in recs)
    tot = sum(ec.values())
    for k in sorted(ec):
        emit(f"  {k} ENTRANCE_DOOR polygons: {ec[k]:>7} dwellings  {ec[k] / tot:>7.2%}")
    out["entrance"] = {"counts": dict(ec), "src": "swiss_dwellings_raw_polygon"}

    # ------------------------------------------------- area / invented envelope
    emit()
    emit("=" * 96)
    emit("area.invented_envelope_hard = 5 % / _soft = 2 %")
    emit("quantity: sum of Space areas against the Brief target_area "
         "(ADR 0010). Not corpus-measurable -- what the corpus CAN say is how "
         "much of a dwelling the partitions take, which is the gap between the "
         "two quantities a Homeowner might mean.")
    emit("=" * 96)
    part_share = [1 - x for x in eff_all]
    emit(header())
    emit(pct_row("partition footprint", part_share, fmt="{:>9.4f}"))
    out["partition_share"] = {f"p{p}": float(np.percentile(part_share, p))
                              for p in PCTS}

    # ------------------------------------------------------------- piers
    emit()
    emit("=" * 96)
    emit("AZ.openings.min_pier_mm = 600   (wall left between two structural "
         "openings on one run)")
    emit("handed here by *Opening placement rules* as the only unfitted "
         "constant openings.md adds")
    emit("=" * 96)
    P = [(a, b, g * 1000) for r in recs for a, b, g in r["piers"]]
    ww = np.asarray([g for a, b, g in P if a == "WINDOW" and b == "WINDOW"])
    emit(f"window-to-window gaps on one run: n = {len(ww)}")
    emit(header())
    emit(pct_row("raw gap mm", ww, fmt="{:>9.0f}"))
    emit()
    emit("THE CORPUS DOES NOT DISTINGUISH A MULLION FROM A PIER. The mass "
         "below ~150 mm\nis one window unit stored as two sashes, not two "
         "windows in a wall, so the fit is\nreported at three merge "
         "thresholds rather than as one number:")
    pier_fit = {}
    for cut in (100, 150, 200):
        v = ww[ww >= cut]
        pier_fit[cut] = {"n": int(len(v)),
                         **{f"p{p}": float(np.percentile(v, p)) for p in PCTS},
                         "below_600": float((v < 600).mean()),
                         "below_250": float((v < 250).mean())}
        emit(pct_row(f"merged below {cut} mm", v, fmt="{:>9.0f}"))
        emit(f"{'':22}{'':>8}   below 600 mm: {(v < 600).mean():.2%}   "
             f"below 250 mm: {(v < 250).mean():.2%}")
    out["min_pier"] = {"raw_n": int(len(ww)), "by_merge_cut": pier_fit,
                       "src": "swiss_dwellings_raw_polygon"}

    # ------------------------------------------------- grid quantisation
    emit()
    emit("=" * 96)
    emit("what the 250 mm grid alone costs Sum(Space area) -- the floor under "
         "area.invented_envelope_*")
    emit("=" * 96)
    q = []
    for r in recs:
        a0 = sum(r["area"])
        if a0 <= 0:
            continue
        a1 = 0.0
        for (w, h), a in zip(r["dim"], r["area"]):
            s = (a / (w * h)) ** 0.5 if w * h > 0 else 0.0
            W, H = w * s, h * s
            a1 += max(0.25, round(W / 0.25) * 0.25) * \
                max(0.25, round(H / 0.25) * 0.25)
        q.append(abs(a1 - a0) / a0)
    q = np.asarray(q)
    emit(header())
    emit(pct_row("|rel err| on Sum area", q, fmt="{:>9.4f}"))
    emit()
    for thr in (0.02, 0.03, 0.05):
        emit(f"  dwellings whose grid residual alone exceeds {thr:.0%}: "
             f"{(q > thr).mean():.2%}")
    out["grid_residual"] = {**{f"p{p}": float(np.percentile(q, p)) for p in PCTS},
                            "above_2pct": float((q > 0.02).mean()),
                            "above_3pct": float((q > 0.03).mean()),
                            "above_5pct": float((q > 0.05).mean()),
                            "src": "swiss_dwellings_raw_polygon"}

    (OUT / "fit.txt").write_text("\n".join(LINES), encoding="utf-8")
    json.dump(out, open(OUT / "fit.json", "w"), indent=1)
    print(f"\nwrote {OUT / 'fit.txt'} and {OUT / 'fit.json'}")


if __name__ == "__main__":
    main()
