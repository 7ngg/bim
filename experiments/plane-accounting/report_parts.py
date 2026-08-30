"""Ticket 78's measurements, read off a finished `arms_parts.py` run.

Separated from the run for the same reason `report.py` is: the solves are hours
and a new statistic off them should cost seconds.

    python experiments/plane-accounting/report_parts.py [--tag=parts]
"""

from __future__ import annotations

import io
import json
import math
import statistics as st
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
ARMS = ("A", "Ar", "Bn", "B", "Bcap")
CORNER_MM2 = 5_625
JOIN_MM2_PER_UNIT = 37_500


def q(v, p):
    if not v:
        return None
    v = sorted(v)
    return v[min(len(v) - 1, max(0, int(round(p * (len(v) - 1)))))]


def dist(v, nd=4):
    if not v:
        return None
    return {"n": len(v), "p10": round(q(v, .10), nd), "p50": round(q(v, .50), nd),
            "p90": round(q(v, .90), nd), "p99": round(q(v, .99), nd),
            "max": round(max(v), nd), "min": round(min(v), nd),
            "mean": round(sum(v) / len(v), nd)}


def sign_test(diffs, tol=0.0):
    pos = sum(1 for d in diffs if d > tol)
    neg = sum(1 for d in diffs if d < -tol)
    n = pos + neg
    if n == 0:
        return {"pos": 0, "neg": 0, "p": 1.0}
    k = min(pos, neg)
    return {"pos": pos, "neg": neg,
            "p": round(min(1.0, 2 * sum(math.comb(n, i)
                                        for i in range(k + 1)) / (2 ** n)), 6)}


def _solved(rows):
    return [r for r in rows if "A" in r]


# ---------------------------------------------------------------------------
def item0_population(rows):
    """What a two-part Room actually looks like in this corpus."""
    out = {"pairs": len(rows)}
    solved = _solved(rows)
    out["reached_the_solve"] = len(solved)
    shapes = Counter()
    per_cand = []
    joins = []
    rooms = 0
    for r in solved:
        rd = r.get("prop_resid") or []
        per_cand.append(sum(1 for d in rd if d["parts"] > 1))
        for d in rd:
            rooms += 1
            shapes[d["shape"]] += 1
            if d["parts"] > 1:
                joins.append(d["join"])
    out["rooms"] = rooms
    out["shapes_on_the_warped_proposal"] = dict(shapes.most_common())
    two = sum(v for k, v in shapes.items() if k != "single")
    out["two_part_rooms"] = two
    out["two_part_share_of_rooms"] = round(two / rooms, 4) if rooms else None
    out["two_part_rooms_per_candidate"] = dist(per_cand, 2)
    out["join_units"] = dist(joins, 2)
    out["join_mm2_if_omitted"] = dist([JOIN_MM2_PER_UNIT * j for j in joins], 0)
    out["join_m2_if_omitted"] = dist([JOIN_MM2_PER_UNIT * j / 1e6
                                      for j in joins], 4)
    return out


# ---------------------------------------------------------------------------
def item1_encoding_cost(rows):
    """What the encoding costs, and how much of it is the join term.

    `Bn -> B` is the join term alone: same plane, same binding site, same
    everything else.
    """
    solved = _solved(rows)
    out = {"candidates": len(solved)}
    for arm in ARMS:
        a = [r[arm] for r in solved if arm in r]
        if not a:
            continue
        out[arm] = {
            "build_s": dist([x["build"] for x in a]),
            "wall_s": dist([x["wall"] for x in a]),
            "at_cap": sum(1 for x in a if x["wall"] >= 14.5),
            "total_wall_s": round(sum(x["wall"] for x in a), 1),
            "first_plan_s": dist([x["first"] for x in a
                                  if x.get("first") is not None]),
            "vars": dist([x["vars"] for x in a], 0),
            "cons": dist([x["cons"] for x in a], 0),
            "parts": dist([x["parts"] for x in a], 0),
            "contact_lits": dist([x["clits"] for x in a], 0),
            "contact_ints": dist([x["cints"] for x in a], 0),
            "join_ints": dist([x["jints"] for x in a], 0),
            "status": dict(Counter(x["status"] for x in a)),
        }
    both = [r for r in solved if all(k in r for k in ARMS)]
    out["paired"] = {"n": len(both)}
    for arm, base in (("Ar", "A"), ("Bn", "Ar"), ("B", "Bn"), ("B", "A"),
                      ("Bcap", "B")):
        dw = [r[arm]["wall"] - r[base]["wall"] for r in both]
        out["paired"][f"{arm}_minus_{base}"] = {
            "wall_s": dist(dw), "wall_sign_test": sign_test(dw),
            "build_s": dist([r[arm]["build"] - r[base]["build"] for r in both]),
            "vars_ratio": dist([r[arm]["vars"] / r[base]["vars"]
                                for r in both], 3),
            "cons_ratio": dist([r[arm]["cons"] / r[base]["cons"]
                                for r in both], 3),
            "vars_delta": dist([r[arm]["vars"] - r[base]["vars"]
                                for r in both], 0),
            "cons_delta": dist([r[arm]["cons"] - r[base]["cons"]
                                for r in both], 0),
            "total_wall_s": {base: round(sum(r[base]["wall"] for r in both), 1),
                             arm: round(sum(r[arm]["wall"] for r in both), 1)},
        }
    # the join term's own price, per two-part Room present
    per_room = []
    for r in both:
        k2 = r.get("n_two_part") or 0
        if k2:
            per_room.append((r["B"]["vars"] - r["Bn"]["vars"]) / k2)
    out["join_vars_per_two_part_room"] = dist(per_room, 2)
    return out


# ---------------------------------------------------------------------------
def item2_refusals(rows):
    """Who refuses what, and which of the three changes rescues it."""
    out = {"pairs": len(rows)}
    warp = Counter(r["status"] for r in rows if r["status"].startswith("warp_"))
    out["refused_before_the_solve"] = {
        "total": sum(warp.values()),
        "share": round(sum(warp.values()) / len(rows), 4) if rows else None,
        "by_status": dict(warp),
    }
    solved = _solved(rows)
    out["reached_the_solve"] = len(solved)
    for arm in ARMS:
        a = [r[arm] for r in solved if arm in r]
        inf = [x for x in a if x["status"] == "INFEASIBLE"]
        rec = {"INFEASIBLE": len(inf),
               "share": round(len(inf) / len(a), 4) if a else None,
               "by_floor": sum(1 for x in inf if x.get("refused_by_floor")),
               "ablate_status": dict(Counter(x.get("ablate_status")
                                             for x in inf))}
        if arm in ("Bcap",):
            rec["by_cap"] = sum(1 for x in inf if x.get("refused_by_cap"))
        ok = [x for x in a if "plan_starved" in x]
        rec["returned_a_plan"] = len(ok)
        rec["plan_starved"] = sum(1 for x in ok if x["plan_starved"])
        rec["plan_starved_rooms"] = sum(x["plan_starved_rooms"] for x in ok)
        out[arm] = rec

    both = [r for r in solved if all(k in r for k in ARMS)]
    idx = {arm: {i for i, r in enumerate(both)
                 if r[arm]["status"] == "INFEASIBLE"} for arm in ARMS}
    out["paired"] = {"n": len(both)}
    for arm, base in (("Ar", "A"), ("Bn", "Ar"), ("B", "Bn"), ("B", "A"),
                      ("Bcap", "B")):
        out["paired"][f"{arm}_vs_{base}"] = {
            "rescued": len(idx[base] - idx[arm]),
            "newly_refused": len(idx[arm] - idx[base]),
            "both": len(idx[arm] & idx[base]),
        }
    # objective: does the plane buy a better Plan where both are feasible?
    for arm, base in (("Bn", "Ar"), ("B", "Bn"), ("B", "A")):
        d = [r[arm]["objective"] - r[base]["objective"] for r in both
             if r[arm].get("objective") is not None
             and r[base].get("objective") is not None]
        out["paired"][f"objective_{arm}_minus_{base}"] = {
            "dist": dist(d, 1), "better": sum(1 for v in d if v < 0),
            "worse": sum(1 for v in d if v > 0),
            "same": sum(1 for v in d if v == 0)}
    # H3 slack, which the objective's soft coverage term dominates
    for arm in ARMS:
        sl = [r[arm]["cov_slack"] for r in both if "cov_slack" in r[arm]]
        out.setdefault("cov_slack_cells", {})[arm] = dist(sl, 1)
    return out


# ---------------------------------------------------------------------------
def item3_residual(rows):
    """The residual `true - [B]`, with and without the join term, by shape."""
    out = {}
    for label, get in (("on_the_warped_proposal",
                        lambda r: r.get("prop_resid")),
                       ("on_the_solved_plan_B",
                        lambda r: r.get("B", {}).get("resid"))):
        vals, nj, by_shape, parts = [], [], {}, Counter()
        for r in rows:
            rd = get(r)
            if not rd:
                continue
            for d in rd:
                vals.append(d["resid"])
                nj.append(d["resid_nj"])
                parts[d["parts"]] += 1
                by_shape.setdefault(d["shape"], []).append(d["resid"])
        if not vals:
            continue
        out[label] = {
            "rooms": len(vals),
            "parts": dict(parts),
            "resid_m2": dist([v / 1e6 for v in vals], 5),
            "abs_resid_m2": dist([abs(v) / 1e6 for v in vals], 5),
            "negative": sum(1 for v in vals if v < 0),
            "negative_share": round(sum(1 for v in vals if v < 0) / len(vals), 5),
            "zero": sum(1 for v in vals if v == 0),
            "worst_abs_m2": round(max(abs(v) for v in vals) / 1e6, 5),
            "within_ADR_0039_bound_0_0225_m2":
                sum(1 for v in vals if abs(v) <= 4 * CORNER_MM2),
            "outside_it": sum(1 for v in vals if abs(v) > 4 * CORNER_MM2),
            "is_a_multiple_of_5625": all(v % CORNER_MM2 == 0 for v in vals),
            "by_shape": {k: dist([v / 1e6 for v in vv], 5)
                         for k, vv in sorted(by_shape.items())},
            # the naive arm's residual: the join band, omitted
            "no_join_resid_m2": dist([v / 1e6 for v in nj], 5),
            "no_join_negative": sum(1 for v in nj if v < 0),
        }
    # verdicts
    crossed_floor = crossed_cap = rooms = 0
    nj_floor = 0
    for r in rows:
        x = r.get("B")
        if not x or "resid" not in x:
            continue
        for d, f, c in zip(x["resid"], r["floors"], r["caps_mm2"]):
            rooms += 1
            fl = f * 1e6
            if (d["bar"] >= fl) != (d["true"] >= fl):
                crossed_floor += 1
            if (d["bar_nj"] >= fl) != (d["true"] >= fl):
                nj_floor += 1
            if (d["bar"] <= c) != (d["true"] <= c):
                crossed_cap += 1
    out["verdict_changed"] = {
        "rooms": rooms,
        "floor_by_the_residual": crossed_floor,
        "floor_if_the_join_term_is_omitted": nj_floor,
        "cap_by_the_residual": crossed_cap,
    }
    # the oracle against shapely, at corpus scale
    worst, n_chk = 0.0, 0
    for r in rows:
        seqs = [r.get("prop_resid", [])]
        seqs += [r[a]["resid"] for a in ARMS
                 if a in r and "resid" in r[a]]
        for seq in seqs:
            for d in seq:
                if "chk" in d:
                    worst = max(worst, abs(d["true"] - d["chk"]))
                    n_chk += 1
    out["true_vs_space_m2_on_the_corpus"] = {
        "rooms_checked": n_chk, "worst_abs_mm2": round(worst, 3),
        "agree": worst <= 1}
    # scale: the plane gap this ticket's parent exists to close
    gap = []
    for r in rows:
        x = r.get("B")
        if not x or "resid" not in x:
            continue
        for d in x["resid"]:
            if d["true"]:
                gap.append((d["true"] - d["solver"]) / d["true"])
    out["plane_gap_true_minus_solver_over_true"] = dist(gap, 5)
    # and the join term's share of that gap, on two-part Rooms
    share = []
    for r in rows:
        x = r.get("B")
        if not x or "resid" not in x:
            continue
        for d in x["resid"]:
            if d["parts"] > 1 and d["true"]:
                share.append((d["bar"] - d["bar_nj"]) / d["true"])
    out["join_term_over_true_area_two_part_rooms"] = dist(share, 5)
    return out


# ---------------------------------------------------------------------------
def item4_cap(rows):
    """`dim.max_area`, posted on the ROOM. Ticket 77 measured it per Room where
    every Room was one rectangle; here a Room can be two."""
    solved = _solved(rows)
    out = {}
    for arm, key in (("Ar", "solver"), ("B", "bar")):
        rooms = over = cands = 0
        for r in solved:
            x = r.get(arm)
            if not x or "resid" not in x:
                continue
            hit = x[f"cap_binds_{key}"]
            rooms += len(x["resid"])
            over += len(hit)
            cands += bool(hit)
        out[f"uncapped_{arm}_over_cap_on_its_own_plane"] = {
            "rooms": rooms, "over": over, "candidates": cands,
            "share": round(over / rooms, 5) if rooms else None}
    # over the TRUE plane, whatever was posted
    for arm in ("A", "Ar", "B", "Bcap"):
        over, rooms, types = 0, 0, Counter()
        worst = 0
        for r in solved:
            x = r.get(arm)
            if not x or "resid" not in x:
                continue
            for i, (d, c) in enumerate(zip(x["resid"], r["caps_mm2"])):
                rooms += 1
                if d["true"] > c:
                    over += 1
                    types[r["types"][i]] += 1
                    worst = max(worst, (d["true"] - c) / 1e6)
        out[f"{arm}_rooms_above_the_cap_on_the_bar_plane"] = {
            "rooms": rooms, "over": over,
            "share": round(over / rooms, 5) if rooms else None,
            "worst_over_m2": round(worst, 4), "types": dict(types.most_common())}
    p = [r for r in solved if "Bcap" in r and "B" in r]
    if p:
        ci = {i for i, r in enumerate(p) if r["Bcap"]["status"] == "INFEASIBLE"}
        bi = {i for i, r in enumerate(p) if r["B"]["status"] == "INFEASIBLE"}
        dobj = [r["Bcap"]["objective"] - r["B"]["objective"] for r in p
                if r["Bcap"].get("objective") is not None
                and r["B"].get("objective") is not None]
        out["Bcap_vs_B"] = {
            "n": len(p), "new_INFEASIBLE": len(ci - bi),
            "lost_INFEASIBLE": len(bi - ci),
            "objective_delta": dist(dobj, 1),
            "objective_moved": sum(1 for d in dobj if d != 0),
            "wall_delta_s": dist([r["Bcap"]["wall"] - r["B"]["wall"] for r in p]),
            "cons_delta": dist([r["Bcap"]["cons"] - r["B"]["cons"] for r in p], 0),
            "vars_delta": dist([r["Bcap"]["vars"] - r["B"]["vars"] for r in p], 0),
        }
    return out


# ---------------------------------------------------------------------------
def item5_seed_spread(seed_rows):
    """Is the difference between two arms bigger than one model's own spread?

    ADR 0040's bar. `B - Bn` is the join term alone and is the one that needs
    it; `B - A` is the whole encoding and is expected to clear it easily.
    """
    if not seed_rows:
        return None
    out = {"candidates": len(seed_rows), "seeds": len(seed_rows[0]["A"]["wall"])}
    for arm in ("A", "Bn", "B"):
        got = [r[arm] for r in seed_rows if arm in r]
        out[arm] = {
            "wall_med": dist([x["wall_med"] for x in got]),
            "wall_spread": dist([x["wall_spread"] for x in got]),
            "first_med": dist([x["first_med"] for x in got
                               if x["first_med"] is not None]),
            "first_spread": dist([x["first_spread"] for x in got
                                  if x["first_spread"] is not None]),
            "vars": dist([r[f"vars_{arm}"] for r in seed_rows], 0),
            "cons": dist([r[f"cons_{arm}"] for r in seed_rows], 0),
        }
    for arm, base in (("B", "A"), ("B", "Bn"), ("Bn", "A")):
        inside, diffs = [], []
        for r in seed_rows:
            if arm not in r or base not in r:
                continue
            d = r[arm]["wall_med"] - r[base]["wall_med"]
            diffs.append(d)
            inside.append(abs(d) <= max(r[base]["wall_spread"],
                                        r[arm]["wall_spread"]))
        out[f"{arm}_minus_{base}"] = {
            "median_wall": dist(diffs),
            "sign_test": sign_test(diffs),
            "n": len(inside), "inside_own_seed_spread": sum(inside),
            "share_inside": (round(sum(inside) / len(inside), 4)
                             if inside else None),
        }
    return out


def load_rows(tag):
    """`arms_parts.py` appends one JSON object per line, so a run killed
    mid-write costs at most the row being written. A trailing partial line is
    dropped with a warning rather than crashing the report."""
    jl = OUT / f"armsp_rows_{tag}.jsonl"
    if not jl.exists():
        return json.load(io.open(OUT / f"armsp_rows_{tag}.json",
                                 encoding="utf-8"))
    rows, bad = [], 0
    for line in io.open(jl, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except ValueError:
            bad += 1
    if bad:
        print(f"warning: dropped {bad} incomplete row(s)", file=sys.stderr)
    return rows


def main():
    opt = {a.split("=")[0]: a.split("=")[1] for a in sys.argv[1:] if "=" in a}
    tag = opt.get("--tag", "parts")
    rows = load_rows(tag)
    mfile = OUT / f"armsp_meta_{tag}.json"
    stag = opt.get("--seeds", "seedsp")
    sfile = OUT / f"seedsp_rows_{stag}.jsonl"
    seed_rows = ([json.loads(l) for l in io.open(sfile, encoding="utf-8")
                  if l.strip()] if sfile.exists() else [])
    rep = {
        "_meta": (json.load(io.open(mfile, encoding="utf-8"))
                  if mfile.exists() else {"rows": len(rows)}),
        "item0_population": item0_population(rows),
        "item1_encoding_cost": item1_encoding_cost(rows),
        "item2_refusals": item2_refusals(rows),
        "item3_residual": item3_residual(rows),
        "item4_cap": item4_cap(rows),
        "item5_seed_spread": item5_seed_spread(seed_rows),
    }
    json.dump(rep, io.open(OUT / f"report_{tag}.json", "w", encoding="utf-8"),
              indent=1)
    print(json.dumps(rep, indent=1))
    print(f"\nwrote out/report_{tag}.json")


if __name__ == "__main__":
    main()
