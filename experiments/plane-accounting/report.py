"""Ticket 77's four measurements, read off a finished `arms.py` run.

Separated from the run for `acceptance-thresholds/`'s standing reason: the
solves are ~30 minutes and a new statistic off them should cost seconds.

    python experiments/plane-accounting/report.py [--tag=main] [--seeds=seeds]
"""

from __future__ import annotations

import io
import json
import math
import statistics as st
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
ARMS = ("A", "B", "Bc", "Acap", "Bcap")
CORNER_MM2 = 5_625


def q(v, p):
    if not v:
        return None
    v = sorted(v)
    i = min(len(v) - 1, max(0, int(round(p * (len(v) - 1)))))
    return v[i]


def dist(v, nd=4):
    if not v:
        return None
    return {"n": len(v), "p10": round(q(v, .10), nd), "p50": round(q(v, .50), nd),
            "p90": round(q(v, .90), nd), "p99": round(q(v, .99), nd),
            "max": round(max(v), nd), "min": round(min(v), nd),
            "mean": round(sum(v) / len(v), nd)}


def sign_test(diffs, tol=0.0):
    """Two-sided exact sign test on the non-zero differences."""
    pos = sum(1 for d in diffs if d > tol)
    neg = sum(1 for d in diffs if d < -tol)
    n = pos + neg
    if n == 0:
        return {"pos": 0, "neg": 0, "p": 1.0}
    k = min(pos, neg)
    p = 2 * sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n)
    return {"pos": pos, "neg": neg, "p": round(min(1.0, p), 6)}


# ---------------------------------------------------------------------------
def item1_cost(rows, seeds_rows):
    solved = [r for r in rows if "A" in r]
    out = {"candidates_reaching_the_solve": len(solved)}
    for arm in ARMS:
        a = [r[arm] for r in solved if arm in r]
        if not a:
            continue
        out[arm] = {
            "build_s": dist([x["build"] for x in a]),
            "wall_s": dist([x["wall"] for x in a]),
            "at_cap": sum(1 for x in a if x["wall"] >= 14.5),
            "vars": dist([x["vars"] for x in a], 0),
            "cons": dist([x["cons"] for x in a], 0),
            "contact_lits": dist([x["clits"] for x in a], 0),
            "contact_ints": dist([x["cints"] for x in a], 0),
            "status": dict(Counter(x["status"] for x in a)),
        }
    # paired, on the candidates every arm reached
    both = [r for r in solved if all(k in r for k in ("A", "B", "Bc"))]
    out["paired"] = {}
    for arm in ("B", "Bc", "Acap", "Bcap"):
        p = [r for r in both if arm in r]
        dw = [r[arm]["wall"] - r["A"]["wall"] for r in p]
        db = [r[arm]["build"] - r["A"]["build"] for r in p]
        rv = [r[arm]["vars"] / r["A"]["vars"] for r in p]
        rc = [r[arm]["cons"] / r["A"]["cons"] for r in p]
        out["paired"][f"{arm}_minus_A"] = {
            "wall_s": dist(dw), "build_s": dist(db),
            "wall_sign_test": sign_test(dw),
            "vars_ratio": dist(rv, 3), "cons_ratio": dist(rc, 3),
            "total_wall_s": {"A": round(sum(r["A"]["wall"] for r in p), 1),
                             arm: round(sum(r[arm]["wall"] for r in p), 1)},
        }
    # the bar: seed-to-seed spread on the same model
    if seeds_rows:
        sp = {}
        for arm in ("A", "B", "Bc"):
            got = [r[arm] for r in seeds_rows if arm in r]
            sp[arm] = {
                "wall_med": dist([x["wall_med"] for x in got]),
                "wall_spread": dist([x["wall_spread"] for x in got]),
                "first_med": dist([x["first_med"] for x in got
                                   if x["first_med"] is not None]),
                "first_spread": dist([x["first_spread"] for x in got
                                      if x["first_spread"] is not None]),
            }
        # is the arm difference inside one candidate's own seed spread?
        inside = []
        for r in seeds_rows:
            if "A" not in r or "B" not in r:
                continue
            d = abs(r["B"]["wall_med"] - r["A"]["wall_med"])
            inside.append(d <= max(r["A"]["wall_spread"], r["B"]["wall_spread"]))
        sp["B_minus_A_inside_own_seed_spread"] = {
            "n": len(inside), "inside": sum(inside),
            "share": round(sum(inside) / len(inside), 4) if inside else None}
        dm = [r["B"]["wall_med"] - r["A"]["wall_med"]
              for r in seeds_rows if "A" in r and "B" in r]
        sp["B_minus_A_median_wall"] = dist(dm)
        sp["B_minus_A_sign_test"] = sign_test(dm)
        out["seed_spread"] = sp
    return out


# ---------------------------------------------------------------------------
def item2_infeasible(rows):
    out = {}
    out["pairs"] = len(rows)
    warp = Counter(r["status"] for r in rows if r["status"].startswith("warp_"))
    out["refused_before_the_solve"] = {
        "warp_INFEASIBLE": warp.get("warp_INFEASIBLE", 0),
        "other": {k: v for k, v in warp.items() if k != "warp_INFEASIBLE"},
        "total": sum(warp.values()),
        "share": round(sum(warp.values()) / len(rows), 4),
    }
    solved = [r for r in rows if "A" in r]
    out["reached_the_solve"] = len(solved)
    for arm in ARMS:
        a = [(r, r[arm]) for r in solved if arm in r]
        inf = [(r, x) for (r, x) in a if x["status"] == "INFEASIBLE"]
        byfloor = [1 for (_r, x) in inf if x.get("refused_by_floor")]
        rec = {"INFEASIBLE": len(inf), "share": round(len(inf) / len(a), 4),
               "by_floor": sum(byfloor),
               "ablate_status": dict(Counter(x.get("ablate_status")
                                             for (_r, x) in inf))}
        if arm in ("Acap", "Bcap"):
            rec["by_cap"] = sum(1 for (_r, x) in inf if x.get("refused_by_cap"))
            rec["ablate_cap_status"] = dict(Counter(x.get("ablate_cap_status")
                                                    for (_r, x) in inf))
        # plan-level starvation on the BAR plane, whatever plane was posted
        ok = [(r, x) for (r, x) in a if "plan_starved" in x]
        rec["plan_starved"] = sum(1 for (_r, x) in ok if x["plan_starved"])
        rec["plan_starved_rooms"] = sum(x["plan_starved_rooms"] for (_r, x) in ok)
        rec["returned_a_plan"] = len(ok)
        out[arm] = rec
    # the delta, paired
    both = [r for r in solved if "A" in r and "B" in r]
    a_inf = {i for i, r in enumerate(both) if r["A"]["status"] == "INFEASIBLE"}
    b_inf = {i for i, r in enumerate(both) if r["B"]["status"] == "INFEASIBLE"}
    out["paired_A_vs_B"] = {
        "n": len(both), "A_only": len(a_inf - b_inf), "B_only": len(b_inf - a_inf),
        "both": len(a_inf & b_inf),
        "rescued_by_the_bar_plane": len(a_inf - b_inf),
        "rescued_share_of_A": (round(len(a_inf - b_inf) / len(a_inf), 4)
                               if a_inf else None),
    }
    return out


# ---------------------------------------------------------------------------
def item3_cap(rows):
    """`dim.max_area`, under both plane readings. `solver.py` posts no cap at
    all today, so every number here is new model."""
    solved = [r for r in rows if "A" in r]
    out = {}
    # (a) would the cap have bound, on the UNCAPPED solutions?
    for arm, key in (("A", "solver"), ("B", "bar")):
        rooms = over = 0
        cands_over = 0
        for r in solved:
            x = r.get(arm)
            if not x or "resid" not in x:
                continue
            hit = x[f"cap_binds_{key}"]
            rooms += len(x["resid"])
            over += len(hit)
            cands_over += bool(hit)
        out[f"uncapped_{arm}_over_cap_on_its_own_plane"] = {
            "rooms": rooms, "over": over,
            "share": round(over / rooms, 5) if rooms else None,
            "candidates": cands_over}
    # (b) the false pass: under the cap on the solver plane, over on the bar's
    fp_rooms = fp_cands = 0
    both_planes = []
    for r in solved:
        x = r.get("A")
        if not x or "resid" not in x:
            continue
        caps = r["caps_mm2"]
        hit = [i for i, (d, c) in enumerate(zip(x["resid"], caps))
               if d["solver"] <= c < d["true"]]
        fp_rooms += len(hit)
        fp_cands += bool(hit)
        both_planes.append((len(x["resid"]), len(hit)))
    out["false_pass_solver_plane_under_bar_plane_over"] = {
        "rooms": fp_rooms, "candidates": fp_cands,
        "of_rooms": sum(a for a, _ in both_planes),
        "share": (round(fp_rooms / sum(a for a, _ in both_planes), 5)
                  if both_planes else None)}
    # (c) headroom -- how far from binding, on the bar plane
    hd = []
    for r in solved:
        x = r.get("B") or r.get("A")
        if not x or "headroom_m2" not in x:
            continue
        hd += x["headroom_m2"]
    out["headroom_m2_bar_plane"] = dist(hd)
    out["rooms_within_1_m2_of_the_cap"] = sum(1 for h in hd if h < 1.0)
    # (d) what posting it costs
    for cap_arm, base in (("Acap", "A"), ("Bcap", "B")):
        p = [r for r in solved if cap_arm in r and base in r]
        if not p:
            continue
        ci = {i for i, r in enumerate(p) if r[cap_arm]["status"] == "INFEASIBLE"}
        bi = {i for i, r in enumerate(p) if r[base]["status"] == "INFEASIBLE"}
        dobj = [r[cap_arm]["objective"] - r[base]["objective"] for r in p
                if r[cap_arm].get("objective") is not None
                and r[base].get("objective") is not None]
        out[f"{cap_arm}_vs_{base}"] = {
            "n": len(p),
            "new_INFEASIBLE": len(ci - bi), "lost_INFEASIBLE": len(bi - ci),
            "objective_delta": dist(dobj, 1),
            "objective_moved": sum(1 for d in dobj if d != 0),
            "wall_delta_s": dist([r[cap_arm]["wall"] - r[base]["wall"]
                                  for r in p]),
            "cons_delta": dist([r[cap_arm]["cons"] - r[base]["cons"] for r in p], 0),
        }
    # (e) which Room types ever come near
    near = Counter()
    for r in solved:
        x = r.get("B") or r.get("A")
        if not x or "headroom_m2" not in x:
            continue
        for t, h in zip(r["types"], x["headroom_m2"]):
            if h < 1.0:
                near[t] += 1
    out["types_within_1_m2"] = dict(near.most_common())
    return out


# ---------------------------------------------------------------------------
def item4_residual(rows):
    """The realised corner residual: `true - [B]`, in mm2, per Room."""
    out = {}
    for label, key in (("on_the_warped_proposal", "prop_resid"),
                       ("on_the_solved_plan_B", None)):
        vals, corners, reflex, neg = [], [], [], 0
        for r in rows:
            if key:
                rd = r.get(key)
            else:
                rd = r.get("B", {}).get("resid")
            if not rd:
                continue
            for d in rd:
                vals.append(d["resid"])
                corners.append(d["corners"])
                reflex.append(d["reflex"])
                neg += d["resid"] < 0
        if not vals:
            continue
        out[label] = {
            "rooms": len(vals),
            "resid_mm2": dist(vals, 0),
            "resid_m2": dist([v / 1e6 for v in vals], 5),
            "abs_resid_m2": dist([abs(v) / 1e6 for v in vals], 5),
            "negative": neg,
            "negative_share": round(neg / len(vals), 5),
            "zero": sum(1 for v in vals if v == 0),
            "corners": dict(Counter(corners)),
            "reflex": dict(Counter(reflex)),
            "reflex_gt_corners": sum(1 for c, x in zip(corners, reflex) if x > c),
            "bound_0_0225_m2_respected": all(abs(v) <= 4 * CORNER_MM2
                                             for v in vals),
            "worst_m2": round(max(abs(v) for v in vals) / 1e6, 5),
        }
    # does the residual ever change a verdict?
    crossed_floor = crossed_cap = 0
    rooms = 0
    for r in rows:
        x = r.get("B")
        if not x or "resid" not in x:
            continue
        floors = r["floors"]
        caps = r["caps_mm2"]
        for d, f, c in zip(x["resid"], floors, caps):
            rooms += 1
            fl = f * 1e6
            if (d["bar"] >= fl) != (d["true"] >= fl):
                crossed_floor += 1
            if (d["bar"] <= c) != (d["true"] <= c):
                crossed_cap += 1
    out["verdict_changed_by_the_residual"] = {
        "rooms": rooms, "floor": crossed_floor, "cap": crossed_cap,
        "floor_share": round(crossed_floor / rooms, 6) if rooms else None}
    # T2 at corpus scale: `arms.py` records `plan_space` from `space_m2`
    # (shapely, on the real solved geometry) and `resid[*]["true"]` from the
    # integer identity. They are computed by different code on different
    # representations and must agree.
    worst = 0.0
    n_chk = 0
    for r in rows:
        for key in ("prop_resid",):
            for d in r.get(key, []):
                if "chk" not in d:
                    continue
                worst = max(worst, abs(d["true"] - d["chk"]))
                n_chk += 1
        for arm in ("A", "B", "Bc", "Acap", "Bcap"):
            x = r.get(arm)
            if not x or "resid" not in x:
                continue
            for d in x["resid"]:
                if "chk" not in d:
                    continue
                worst = max(worst, abs(d["true"] - d["chk"]))
                n_chk += 1
    out["true_vs_space_m2_on_the_corpus"] = {
        "rooms_checked": n_chk, "worst_abs_mm2": round(worst, 3),
        "agree": worst <= 1}

    # The rig posts `coverage` SOFT, so a Plan may leave interior cells
    # unassigned and `outside_of(plan_rects)` then reads a boundary-touching
    # GAP as outside. Envelope-relative and Plan-relative Space differ exactly
    # there, and the solver could not have known: it is H3's slack, not the
    # encoding's. Reported rather than hidden, and it bites both arms equally.
    gap = {}
    for arm in ("A", "B", "Bc", "Acap", "Bcap"):
        sl, dif = [], []
        for r in rows:
            x = r.get(arm)
            if not x or "resid" not in x or "plan_space" not in x:
                continue
            if x.get("cov_slack") is not None:
                sl.append(x["cov_slack"])
            for d, ps in zip(x["resid"], x["plan_space"]):
                dif.append(abs(d["true"] / 1e6 - ps))
        if not dif:
            continue
        gap[arm] = {"cov_slack_cells": dist(sl, 0),
                    "plans_tiling_exactly": sum(1 for v in sl if v == 0),
                    "plans": len(sl),
                    "envelope_minus_plan_relative_m2": dist(dif, 5)}
    out["soft_H3_gap"] = gap

    # and the plane gap itself, for scale
    gap = []
    for r in rows:
        x = r.get("B")
        if not x or "resid" not in x:
            continue
        for d in x["resid"]:
            if d["true"]:
                gap.append((d["true"] - d["solver"]) / d["true"])
    out["plane_gap_true_minus_solver_over_true"] = dist(gap, 5)
    return out


def main():
    opt = {a.split("=")[0]: a.split("=")[1] for a in sys.argv[1:] if "=" in a}
    tag = opt.get("--tag", "main")
    rows = json.load(io.open(OUT / f"arms_rows_{tag}.json", encoding="utf-8"))
    sfile = OUT / f"seeds_rows_{opt.get('--seeds', 'seeds')}.json"
    seeds_rows = (json.load(io.open(sfile, encoding="utf-8"))
                  if sfile.exists() else [])
    rep = {
        "_meta": json.load(io.open(OUT / f"arms_meta_{tag}.json", encoding="utf-8"))
        if (OUT / f"arms_meta_{tag}.json").exists() else {"rows": len(rows)},
        "item1_cost": item1_cost(rows, seeds_rows),
        "item2_infeasible": item2_infeasible(rows),
        "item3_cap": item3_cap(rows),
        "item4_residual": item4_residual(rows),
    }
    json.dump(rep, io.open(OUT / f"report_{tag}.json", "w", encoding="utf-8"),
              indent=1)
    print(json.dumps(rep, indent=1))
    print(f"\nwrote out/report_{tag}.json")


if __name__ == "__main__":
    main()
