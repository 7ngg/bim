"""Aggregate `results/*.jsonl` into the tables ticket 15 asks for.

    python report.py                 # every suite present
    python report.py S2 S4

Percentiles are nearest-rank on the sorted sample, so every number printed is a
value that was actually measured rather than an interpolation between two.
"""

from __future__ import annotations

import json
import pathlib
import sys
from collections import Counter, defaultdict
from typing import Dict, Iterable, List, Optional, Sequence

RESULTS = pathlib.Path(__file__).parent / "results"


def load(suite: str, tag: str = "") -> List[dict]:
    f = RESULTS / f"{suite}{tag}.jsonl"
    if not f.exists():
        return []
    out = []
    for line in f.read_text(encoding="utf-8").splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def pct(xs: Sequence[float], q: float) -> Optional[float]:
    """Nearest-rank percentile: always a value that was measured."""
    v = sorted(x for x in xs if x is not None)
    if not v:
        return None
    k = max(1, min(len(v), int(-(-q * len(v) // 100))))
    return v[k - 1]


def dist(rows: Sequence[dict], field: str = "first") -> dict:
    xs = [r.get(field) for r in rows if r.get(field) is not None]
    return {
        "n": len(rows),
        "got": len(xs),
        "p50": pct(xs, 50), "p90": pct(xs, 90), "p95": pct(xs, 95),
        "max": max(xs) if xs else None,
        "min": min(xs) if xs else None,
    }


def fmt(x, w=6, p=2) -> str:
    return " " * w if x is None else f"{x:{w}.{p}f}"


def statuses(rows: Sequence[dict]) -> str:
    c = Counter(r["status"] for r in rows)
    return " ".join(f"{k}={v}" for k, v in sorted(c.items()))


def solved(rows: Sequence[dict]) -> List[dict]:
    return [r for r in rows if r["status"] in ("FEASIBLE", "OPTIMAL")]


def group(rows: Iterable[dict], *keys) -> Dict[tuple, List[dict]]:
    g: Dict[tuple, List[dict]] = defaultdict(list)
    for r in rows:
        g[tuple(r.get(k) for k in keys)].append(r)
    return dict(g)


def hdr(t: str) -> None:
    print(f"\n{'=' * 78}\n{t}\n{'=' * 78}")


def valid_rate(rows: Sequence[dict]) -> str:
    s = solved(rows)
    if not s:
        return "  -  "
    ok = sum(1 for r in s if r.get("valid"))
    return f"{100*ok/len(s):3.0f}%"


# ---------------------------------------------------------------------------


def report_S1(tag: str = "") -> None:
    rows = load("S1", tag)
    if not rows:
        return
    hdr("S1 — formulation cost: grid units vs ADR 0001's eroded millimetres")
    print("erode=True is the real feasible set (minima bind on clear dims);")
    print("erode=False relaxes them by t_int so only the numeric cost differs.\n")
    print(f"{'n':>3} {'rig':>10} {'ero':>5} {'seeds':>5} "
          f"{'first p50':>9} {'p90':>7} {'max':>7} "
          f"{'w5 p50':>7} {'p90':>7} {'obj p50':>8} {'vars':>6} {'cons':>6} "
          f"{'mult':>5} {'valid':>6}  status")
    for (n, rig, ero), rs in sorted(group(rows, "n", "rig", "erode").items(),
                                    key=lambda kv: (kv[0][0], kv[0][1], not kv[0][2])):
        s = solved(rs)
        d = dist(s, "first")
        w = dist(s, "within5")
        objs = [r["objective"] for r in s if r.get("objective") is not None]
        m = s[0] if s else rs[0]
        print(f"{n:>3} {rig:>10} {str(ero):>5} {len(rs):>5} "
              f"{fmt(d['p50'],9,3)} {fmt(d['p90'],7,3)} {fmt(d['max'],7,3)} "
              f"{fmt(w['p50'],7,2)} {fmt(w['p90'],7,2)} "
              f"{fmt(pct(objs,50),8,0)} {str(m.get('vars') or ''):>6} "
              f"{str(m.get('cons') or ''):>6} {str(m.get('mults') or ''):>5} "
              f"{valid_rate(rs):>6}  {statuses(rs)}")


def report_S2(tag: str = "") -> None:
    rows = load("S2", tag)
    if not rows:
        return
    hdr("S2 — room count x dwelling-type exposure (the main grid)")
    order = ["detached", "terrace_mid", "flat_corner", "corpus_median",
             "flat_single_aspect"]
    print(f"{'n':>3} {'exposure':>19} {'seeds':>5} {'solved':>6} "
          f"{'first p50':>9} {'p90':>7} {'p95':>7} {'max':>7} "
          f"{'w5 p50':>7} {'w5 p90':>7} {'valid':>6}  status")
    for n in sorted({r["n"] for r in rows}):
        for e in order:
            rs = [r for r in rows if r["n"] == n and r["exposure"] == e]
            if not rs:
                continue
            s = solved(rs)
            d, w = dist(s, "first"), dist(s, "within5")
            print(f"{n:>3} {e:>19} {len(rs):>5} {len(s):>6} "
                  f"{fmt(d['p50'],9,3)} {fmt(d['p90'],7,3)} {fmt(d['p95'],7,3)} "
                  f"{fmt(d['max'],7,3)} {fmt(w['p50'],7,2)} {fmt(w['p90'],7,2)} "
                  f"{valid_rate(rs):>6}  {statuses(rs)}")
        print()

    hdr("S2 — the shipped time limit: what a budget buys, pooled over the grid")
    s = solved(rows)
    for label, field in (("time to first Plan", "first"),
                         ("time to a VALID Plan", "valid_at"),
                         ("time to within 5% of best", "within5")):
        d = dist(s, field)
        print(f"{label:28s} p50={fmt(d['p50'],6,2)} p90={fmt(d['p90'],6,2)} "
              f"p95={fmt(d['p95'],6,2)} max={fmt(d['max'],6,2)}  (n={d['got']})")
    print()
    print("  Derived from the solution traces, so every row below is what a")
    print("  shipped time limit of that size would actually have delivered.\n")
    print(f"  {'budget':>7} {'any Plan':>9} {'VALID Plan':>11} {'within 5%':>10}")
    for budget in (0.5, 1, 2, 3, 5, 7.5, 10, 15, 20, 30):
        a = sum(1 for r in s if r["first"] is not None and r["first"] <= budget)
        v = sum(1 for r in s if r.get("valid_at") is not None
                and r["valid_at"] <= budget)
        g = sum(1 for r in s if r["within5"] is not None and r["within5"] <= budget)
        print(f"  {budget:6.1f}s {100*a/len(s):8.1f}% {100*v/len(s):10.1f}% "
              f"{100*g/len(s):9.1f}%")


def report_drawing(tag: str = "") -> None:
    rows = [r for r in load("S2", tag) if r.get("drawing")
            and "error" not in r["drawing"]]
    if not rows:
        return
    hdr("S2 — drawing measurements (annotation.md), taken off the same solves")
    print(f"{'n':>3} {'plans':>5} {'walls':>6} {'2b':>5} "
          f"{'witn/side p50':>13} {'max':>5} {'narrow p50':>10} {'max':>5} "
          f"{'collide':>7} {'closes':>6}  sheets")
    for n in sorted({r["n"] for r in rows}):
        rs = [r for r in rows if r["n"] == n]
        d = [r["drawing"] for r in rs]
        wit = [x["witnesses_max"] for x in d]
        walls = [x["walls_total"] for x in d]
        orph = [x["orphan_partitions"] for x in d]
        nar = [x["narrow_fires"] for x in d]
        col = sum(x["narrow_collisions"] for x in d)
        closes = sum(1 for x in d if x["chains_close"])
        sheets = Counter(f"{x['sheet']}/1:{x['scale']}"
                         + ("!" if not x["sheet_fits"] else "") for x in d)
        print(f"{n:>3} {len(rs):>5} {fmt(pct(walls,50),6,1)} "
              f"{fmt(pct(orph,50),5,1)} {fmt(pct(wit,50),13,1)} "
              f"{max(wit):>5} {fmt(pct(nar,50),10,1)} {max(nar):>5} "
              f"{col:>7} {closes:>3}/{len(d):<3} "
              + " ".join(f"{k}x{v}" for k, v in sheets.most_common()))
    print("\n`!` marks a plan that fell off the end of the sheet ladder.")


def report_S3(tag: str = "") -> None:
    rows = load("S3", tag)
    if not rows:
        return
    hdr("S3 — Proposal quality: solve time against corner noise sigma")
    print(f"{'n':>3} {'sigma_m':>8} {'seeds':>5} {'solved':>6} "
          f"{'first p50':>9} {'p90':>7} {'max':>7} {'obj p50':>9} "
          f"{'fixed rel':>9} {'valid':>6}  status")
    for n in sorted({r["n"] for r in rows}):
        for sig in sorted({r["sigma"] for r in rows}):
            rs = [r for r in rows if r["n"] == n and r["sigma"] == sig]
            if not rs:
                continue
            s = solved(rs)
            d = dist(s, "first")
            objs = [r["objective"] for r in s if r.get("objective") is not None]
            fr = [r["fixed_relations"] for r in rs
                  if r.get("fixed_relations") is not None]
            print(f"{n:>3} {sig:>8.2f} {len(rs):>5} {len(s):>6} "
                  f"{fmt(d['p50'],9,3)} {fmt(d['p90'],7,3)} {fmt(d['max'],7,3)} "
                  f"{fmt(pct(objs,50),9,0)} {fmt(pct(fr,50),9,1)} "
                  f"{valid_rate(rs):>6}  {statuses(rs)}")
        print()


def report_S4(tag: str = "") -> None:
    rows = load("S4", tag)
    if not rows:
        return
    hdr("S4 — tau: the confidence margin above which a relation is fixed hard")
    print("High tau fixes few relations (slower, more arrangements survive);")
    print("low tau fixes many (faster, and a wrong one is INFEASIBLE at once).\n")
    print(f"{'n':>3} {'exposure':>15} {'tau':>4} {'seeds':>5} "
          f"{'INFEAS':>6} {'solved':>6} {'fixed/cand':>11} "
          f"{'first p50':>9} {'p90':>7} {'obj p50':>9} {'valid':>6}")
    for n in sorted({r["n"] for r in rows}):
        for e in sorted({r["exposure"] for r in rows}):
            for tau in sorted({r["tau"] for r in rows}):
                rs = [r for r in rows if r["n"] == n and r["exposure"] == e
                      and r["tau"] == tau]
                if not rs:
                    continue
                s = solved(rs)
                inf = sum(1 for r in rs if r["status"] == "INFEASIBLE")
                d = dist(s, "first")
                objs = [r["objective"] for r in s if r.get("objective") is not None]
                fr = [r["fixed_relations"] for r in rs
                      if r.get("fixed_relations") is not None]
                cand = next((r["candidate_relations"] for r in rs
                             if r.get("candidate_relations")), None)
                ratio = (f"{pct(fr,50):.0f}/{cand}" if fr and cand else "-")
                print(f"{n:>3} {e:>15} {tau:>4} {len(rs):>5} "
                      f"{inf:>6} {len(s):>6} {ratio:>11} "
                      f"{fmt(d['p50'],9,3)} {fmt(d['p90'],7,3)} "
                      f"{fmt(pct(objs,50),9,0)} {valid_rate(rs):>6}")
            print()


def report_S5(tag: str = "") -> None:
    rows = load("S5", tag)
    if not rows:
        return
    hdr("S5 — the two known failure modes, and how fast detection fires")
    print(f"{'n':>3} {'proposal':>12} {'seeds':>5} "
          f"{'first p50':>9} {'p90':>7} {'detect p50':>10} {'max':>7} "
          f"{'valid':>6}  status")
    for n in sorted({r["n"] for r in rows}):
        for k in ("degenerate", "shuffled"):
            rs = [r for r in rows if r["n"] == n and r["proposal"] == k]
            if not rs:
                continue
            s = solved(rs)
            d = dist(s, "first")
            det = [r["wall"] for r in rs if r["status"] == "INFEASIBLE"]
            print(f"{n:>3} {k:>12} {len(rs):>5} "
                  f"{fmt(d['p50'],9,3)} {fmt(d['p90'],7,3)} "
                  f"{fmt(pct(det,50),10,3)} {fmt(max(det) if det else None,7,3)} "
                  f"{valid_rate(rs):>6}  {statuses(rs)}")
    cores = {tuple(r["core"]) for r in rows if r.get("core")}
    print("\ninfeasibility cores seen:", *cores, sep="\n  ")


def report_S6(tag: str = "") -> None:
    rows = load("S6", tag)
    if not rows:
        return
    hdr("S6 — worker scaling. The honest half of the hardware axis.")
    print("No modern CPU was available; this is the same 4-core Ivy Bridge.")
    print("What can be measured is how the portfolio uses cores.\n")
    print(f"{'n':>3} {'workers':>7} {'seeds':>5} {'first p50':>9} {'p90':>7} "
          f"{'w5 p50':>7} {'obj p50':>9} {'valid':>6}  status")
    for n in sorted({r["n"] for r in rows}):
        for w in sorted({r["workers"] for r in rows}):
            rs = [r for r in rows if r["n"] == n and r["workers"] == w]
            if not rs:
                continue
            s = solved(rs)
            d, ww = dist(s, "first"), dist(s, "within5")
            objs = [r["objective"] for r in s if r.get("objective") is not None]
            print(f"{n:>3} {w:>7} {len(rs):>5} {fmt(d['p50'],9,3)} "
                  f"{fmt(d['p90'],7,3)} {fmt(ww['p50'],7,2)} "
                  f"{fmt(pct(objs,50),9,0)} {valid_rate(rs):>6}  {statuses(rs)}")
        print()


def report_S7(tag: str = "") -> None:
    rows = load("S7", tag)
    if not rows:
        return
    hdr("S7 — distinct valid Plans off ONE Proposal, against tau")
    print("Proposal held fixed; only CP-SAT's random seed moves. `distinct` is")
    print("how many different rectangle sets the runs produced.\n")
    print(f"{'n':>3} {'tau':>4} {'runs':>5} {'fixed/cand':>11} {'INFEAS':>6} "
          f"{'valid':>6} {'distinct':>8} {'first p50':>9} {'obj p50':>9}")
    for n in sorted({r["n"] for r in rows}):
        for tau in sorted({r["tau"] for r in rows}):
            rs = [r for r in rows if r["n"] == n and r["tau"] == tau]
            if not rs:
                continue
            s_ = solved(rs)
            ok = [r for r in s_ if r.get("valid")]
            d = dist(s_, "first")
            objs = [r["objective"] for r in ok if r.get("objective") is not None]
            fr = [r["fixed_relations"] for r in rs
                  if r.get("fixed_relations") is not None]
            cand = next((r["candidate_relations"] for r in rs
                         if r.get("candidate_relations")), None)
            ratio = f"{pct(fr,50):.0f}/{cand}" if fr and cand else "-"
            distinct = len({r["plan"] for r in ok if r.get("plan")})
            print(f"{n:>3} {tau:>4} {len(rs):>5} {ratio:>11} "
                  f"{sum(1 for r in rs if r['status']=='INFEASIBLE'):>6} "
                  f"{len(ok):>6} {distinct:>8} {fmt(d['p50'],9,3)} "
                  f"{fmt(pct(objs,50),9,0)}")
        print()


def report_S8(tag: str = "") -> None:
    rows = load("S8", tag)
    if not rows:
        return
    hdr("S8 - does tau buy back tolerance to a noisy Proposal?")
    print("Cells are INFEASIBLE count / runs. sigma 0.5 m is what every")
    print("published run used, so the 0.5 row is where v1 sits today.")
    taus = sorted({r["tau"] for r in rows})
    for n in sorted({r["n"] for r in rows}):
        print()
        print(f"  n={n}")
        print(f"  {'sigma':>6} | " + " | ".join(f"tau={t:<3}" for t in taus))
        for sig in sorted({r["sigma"] for r in rows}):
            cells = []
            for t in taus:
                rs = [r for r in rows if r["n"] == n and r["sigma"] == sig
                      and r["tau"] == t]
                inf = sum(1 for r in rs if r["status"] == "INFEASIBLE")
                cells.append(f"{inf}/{len(rs)}".rjust(7))
            print(f"  {sig:6.2f} | " + " | ".join(cells))
        print(f"  {'':6} | " + " | ".join("-------" for _ in taus))
        vs, fs, ws = [], [], []
        for t in taus:
            rs = [r for r in rows if r["n"] == n and r["tau"] == t]
            vs.append(f"{sum(1 for r in rs if r.get('valid'))}/{len(rs)}".rjust(7))
            fs.append(fmt(pct([r["first"] for r in rs if r.get("first")], 50), 7, 2))
            ws.append(fmt(pct([r["valid_at"] for r in rs if r.get("valid_at")], 50), 7, 2))
        print(f"  {'valid':>6} | " + " | ".join(vs))
        print(f"  {'first':>6} | " + " | ".join(fs))
        print(f"  {'vld@':>6} | " + " | ".join(ws))
    print()
    print("  valid / first / vld@ rows pool every sigma at that tau.")


def report_invalid() -> None:
    """Any Plan the solver returned and the independent validator rejected."""
    bad = []
    for suite in ("S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"):
        for r in load(suite):
            if r.get("valid") is False:
                bad.append(r)
    if not bad:
        return
    hdr(f"Plans the solver returned and validate.check rejected — {len(bad)}")
    c = Counter(f[:60] for r in bad for f in (r.get("failures") or []))
    for k, v in c.most_common(12):
        print(f"  {v:>4}  {k}")
    by = Counter((r["suite"], r["n"], r["proposal"]) for r in bad)
    print("\n  by (suite, n, proposal):")
    for k, v in by.most_common(12):
        print(f"  {v:>4}  {k}")


HOSTS = {}


def report_host() -> None:
    for suite in ("S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"):
        for r in load(suite):
            if r.get("host"):
                HOSTS[json.dumps(r["host"], sort_keys=True)] = r["host"]
    if HOSTS:
        hdr("Measurement host(s)")
        for h in HOSTS.values():
            print(" ", h)


if __name__ == "__main__":
    want = sys.argv[1:] or ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"]
    report_host()
    fns = {"S1": report_S1, "S2": report_S2, "S3": report_S3,
           "S4": report_S4, "S5": report_S5, "S6": report_S6,
           "S7": report_S7, "S8": report_S8}
    for w in want:
        fns[w]()
        if w == "S2":
            report_drawing()
    report_invalid()
