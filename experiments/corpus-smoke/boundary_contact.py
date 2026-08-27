"""The donor property retrieval actually inherits: can a needs_window Room reach a wall?

Ticket 51. `window_rule_overlap.py` measures where the *corpus's own builder* put
windows. That is a layer the engine overwrites -- `proposer.md` §1 emits boxes and
no openings, and `openings.md` §6.1 glazes every Space after the solve. So the
43.3 %/38.55 % is not a donor property at all.

What the warp does inherit is the arrangement, and through it one thing that binds:
whether a `needs_window` Room reaches the dwelling's own boundary, and with how much
run. Ticket 26 §4 posted that as a HARD SOLVER constraint -- each such Room holds an
`exterior`-condition run of at least its window's structural width plus 2 x 100 mm
jamb. A donor whose kitchen is landlocked cannot satisfy it under any Envelope.

Measured here at index scale, because the only figure carrying that argument today
is h8-frontage's 9.7 %, from 561 dwellings.

⚠️ **This is a LOWER bound on the loss, deliberately.** `proposer.md` §2.2.6 is
explicit that the conversion knows boundary *contact* and not exterior-versus-party,
so a run measured here may be party edge in the target Envelope and host no window.
Contact is necessary, never sufficient. Reporting the optimistic direction is the
honest way round: a gate argued on this number is argued on the smallest defensible
version of it.

Reads `rectangularise/out/swiss_dw.pkl` only -- no corpus stream, no CSV.

Run: ./venv/Scripts/python.exe experiments/corpus-smoke/boundary_contact.py
"""

from __future__ import annotations

import json
import pickle
import statistics as st
import sys
from collections import Counter, defaultdict
from pathlib import Path

from shapely import wkt
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[2]
FITS = ROOT / "experiments/rectangularise/out"
OUT = Path(__file__).resolve().parent / "out"

NEEDS_WINDOW = {"ROOM", "LIVING_DINING", "BEDROOM", "LIVING_ROOM", "DINING",
                "KITCHEN_DINING", "STUDIO", "KITCHEN"}
BRIDGE = 0.12
TOUCH = 0.15            # a room edge lying on the assembled envelope
DECIDED_OK = ("OPTIMAL", "FEASIBLE")

# ticket 26 §4 -- the frontage the SOLVER posts hard, per Room:
# catalogue window structural width + 2 x 100 mm jamb return, in metres.
BUDGET_M = {"KITCHEN": 1.10, "KITCHEN_DINING": 1.10,
            "BEDROOM": 1.40, "ROOM": 1.40, "STUDIO": 1.40,
            "LIVING_ROOM": 1.70, "LIVING_DINING": 1.70, "DINING": 1.70}


def pct(a, b):
    return f"{100 * a / b:5.2f}%" if b else "    - "


def rule(t):
    print("\n" + "=" * 78)
    print(t)
    print("=" * 78)


def main():
    OUT.mkdir(exist_ok=True)
    dw, _ = pickle.load(open(FITS / "swiss_dw.pkl", "rb"))
    print(f"{len(dw):,} dwellings", file=sys.stderr)

    recs = []
    for i, (key, rooms) in enumerate(dw.items()):
        if i % 5000 == 0:
            print(f"  ... {i:,}", file=sys.stderr, flush=True)
        polys, subs = [], []
        for sub, g in rooms:
            try:
                p = wkt.loads(g) if isinstance(g, str) else g
            except Exception:
                continue
            if p.is_empty or p.geom_type != "Polygon":
                continue
            polys.append(p)
            subs.append(sub)
        if not polys:
            continue
        env = unary_union([p.buffer(BRIDGE) for p in polys]).buffer(-BRIDGE)
        if env.is_empty:
            continue
        if env.geom_type == "MultiPolygon":
            env = max(env.geoms, key=lambda p: p.area)
        if env.geom_type != "Polygon":
            continue
        ring = env.exterior
        rr = []
        for sub, p in zip(subs, polys):
            if sub not in NEEDS_WINDOW:
                continue
            run = p.exterior.buffer(TOUCH).intersection(ring).length
            rr.append({"sub": sub, "run": run,
                       "ok": run >= BUDGET_M.get(sub, 1.40)})
        if not rr:
            continue
        recs.append({"k": f"{key[0]}|{key[1]}|{key[2]}", "n": len(polys),
                     "rooms": rr,
                     "landlocked": [r["sub"] for r in rr if r["run"] < 0.05],
                     "short": [r["sub"] for r in rr if not r["ok"]]})
    json.dump(recs, open(OUT / "boundary_contact.json", "w"), separators=(",", ":"))

    rule("1. Per room — can it reach the dwelling boundary, and with what run?")
    per = defaultdict(lambda: [0, 0, 0, []])
    for r in recs:
        for x in r["rooms"]:
            per[x["sub"]][2] += 1
            per[x["sub"]][3].append(x["run"])
            if x["run"] < 0.05:
                per[x["sub"]][0] += 1
            if not x["ok"]:
                per[x["sub"]][1] += 1
    print(f"{'subtype':<16}{'budget':>8}{'landlocked':>12}{'below budget':>14}"
          f"{'total':>9}{'median run':>12}")
    for k, (a, b, c, runs) in sorted(per.items(), key=lambda kv: -kv[1][2]):
        print(f"{k:<16}{BUDGET_M.get(k, 1.40):>8.2f}{pct(a, c):>12}{pct(b, c):>14}"
              f"{c:>9,}{st.median(runs):>12.2f}")

    rule("2. Per dwelling — the residue retrieval actually inherits")
    n = len(recs)
    ll = [r for r in recs if r["landlocked"]]
    sh = [r for r in recs if r["short"]]
    llk = [r for r in ll if set(r["landlocked"]) <= {"KITCHEN"}]
    print(f"dwellings                                    {n:,}")
    print(f"  >=1 needs_window Room landlocked           {len(ll):,}  {pct(len(ll), n)}")
    print(f"    ...the KITCHEN alone                     {len(llk):,}  {pct(len(llk), n)}")
    print(f"  >=1 below the solver's frontage budget     {len(sh):,}  {pct(len(sh), n)}")
    print("\nh8-frontage measured 11.9 % of dwellings with a room having no exterior")
    print("run, 9.7 % of KITCHENs, on 561 dwellings. Contact here is boundary, not")
    print("exterior, so this is the LOWER bound -- see the module docstring.")

    rule("3. Against the glazing measurement — is the donor's window a proxy at all?")
    try:
        win = {r["k"]: r for r in json.load(open(OUT / "window_rule_index.json"))}
    except FileNotFoundError:
        print("window_rule_index.json absent; run window_rule_overlap.py first")
        win = {}
    if win:
        both = [(r, win[r["k"]]) for r in recs if r["k"] in win]
        print(f"joined {len(both):,} dwellings\n")
        tab = Counter((bool(w["fails"]), bool(b["landlocked"])) for b, w in both)
        N = len(both)
        print(f"{'':<26}{'has boundary':>14}{'landlocked':>13}{'total':>9}")
        print(f"{'donor GLAZES all rooms':<26}{tab[(False,False)]:>14,}"
              f"{tab[(False,True)]:>13,}{tab[(False,False)]+tab[(False,True)]:>9,}")
        print(f"{'donor leaves one dark':<26}{tab[(True,False)]:>14,}"
              f"{tab[(True,True)]:>13,}{tab[(True,False)]+tab[(True,True)]:>9,}")
        rep = tab[(True, False)]
        print(f"\ndark BUT on the boundary -- the engine reglazes these for free:")
        print(f"  {rep:,} dwellings, {pct(rep, N)} of the index")
        print(f"  = {pct(rep, tab[(True,False)]+tab[(True,True)])} of every dwelling"
              f" the shipped rule rejects")
        # per-room version, kitchens only
        kr = 0
        kt = 0
        for b, w in both:
            runs = {id(x): x for x in b["rooms"]}
            bk = [x for x in b["rooms"] if x["sub"] == "KITCHEN"]
            wk = [x for x in w["rooms"] if x["sub"] == "KITCHEN"]
            for x, y in zip(bk, wk):
                if not y["win"]:
                    kt += 1
                    if x["run"] >= 0.05:
                        kr += 1
        print(f"\nwindowless KITCHENs that DO reach the boundary: {kr:,}/{kt:,}"
              f"  {pct(kr, kt)}")

    rule("4. What a landlocked gate would cost the index, by room count")
    byn = defaultdict(list)
    for r in recs:
        byn[r["n"]].append(r)
    print(f"{'n':>4}{'dwellings':>11}{'landlocked':>13}{'below budget':>15}")
    for k in sorted(byn):
        if k < 3 or k > 12:
            continue
        g = byn[k]
        print(f"{k:>4}{len(g):>11,}"
              f"{pct(sum(1 for r in g if r['landlocked']), len(g)):>13}"
              f"{pct(sum(1 for r in g if r['short']), len(g)):>15}")


if __name__ == "__main__":
    main()
