"""Does `win.habitable_has_window` cost the index anything ADR 0016 has not already spent?

Ticket 51. *H8 and the single-aspect flat* measured the rule at **43.3 %** of real
Swiss dwellings over a 561-dwelling sample and left the decision open. The ticket
says the overlap against ADR 0016's conversion drop must be **measured rather than
assumed** — nobody knows whether the two drops hit the same dwellings or compound.

Three populations, on purpose:

  FULL INDEX (46,800 dwellings, `rectangularise/out/swiss_dw.pkl`). The window rule
  alone, at index scale rather than at 561. This is the population every coverage
  number in `proposer.md` §2.2.7 is quoted over, so a filter decision has to be
  priced here and not on a sample.

  ADR 0016's OWN SAMPLE (2,600, `rectangularise/out/swiss_fit_k2.json`). The only
  dwellings whose conversion verdict is known, so the 2x2 is paired by construction:
  the same dwelling, both filters, no sampling gap to argue about.

  THE POOL. Blank rate and pool size per collapsed room multiset (§4.1's vocabulary),
  which is the unit retrieval actually gates in — `coverage_restated.py`'s warning
  against a corpus-wide thinning factor applies here identically.

Method is `experiments/h8-frontage/window_rules_corpus.py`'s, verbatim, so the
headline is comparable rather than merely similar: bridge 0.12 m to assemble the
dwelling envelope across its wall gaps, windows kept only where they meet that
envelope's own boundary band (0.60 m), a room has a window where one meets its own
boundary band. Double-attribution is left in — it biases toward *finding* a window,
which is the safe direction for a rule this study may argue against.

Run: ./venv/Scripts/python.exe experiments/corpus-smoke/window_rule_overlap.py
     (~8 min: one pass over geometries.csv, then 46,800 envelope assemblies)
"""

from __future__ import annotations

import json
import pickle
import statistics as st
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd
from shapely import wkt
from shapely.ops import unary_union
from shapely.strtree import STRtree

ROOT = Path(__file__).resolve().parents[2]
GEOM = ROOT / "data/corpora/swiss-dwellings/swiss-dwellings-v3.0.0/geometries.csv"
FITS = ROOT / "experiments/rectangularise/out"
OUT = Path(__file__).resolve().parent / "out"

# --- verbatim from window_rules_corpus.py, so the numbers join -----------------
NEEDS_WINDOW = {"ROOM", "LIVING_DINING", "BEDROOM", "LIVING_ROOM", "DINING",
                "KITCHEN_DINING", "STUDIO", "KITCHEN"}
HABITABLE = NEEDS_WINDOW - {"KITCHEN"}
BRIDGE = 0.12          # assemble the dwelling across its wall gaps
NEAR_M = 0.60          # an opening sits in the wall, not in the room polygon
ADJOIN_M = 0.30        # two rooms sharing a partition, for borrowed daylight

# --- proposer.md 4.1 -----------------------------------------------------------
COLLAPSE = {"ROOM": "PRIVATE", "BEDROOM": "PRIVATE", "STUDIO": "PRIVATE"}
BANDS = {"4-6": range(4, 7), "7-10": range(7, 11)}
DECIDED_OK = ("OPTIMAL", "FEASIBLE")


def pct(a, b):
    return f"{100 * a / b:5.2f}%" if b else "    - "


def rule(title):
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def load_windows(floors_wanted):
    """(site, floor) -> [window polygon].  One pass, opening rows only."""
    cols = ["site_id", "floor_id", "entity_type", "entity_subtype", "geometry"]
    wins = defaultdict(list)
    seen = 0
    for ch in pd.read_csv(GEOM, usecols=cols, chunksize=500_000, dtype=str):
        ch = ch[ch.entity_type == "opening"]
        if ch.empty:
            continue
        ch = ch[ch.entity_subtype.astype(str).str.upper().str.startswith("WINDOW")]
        if ch.empty:
            continue
        ch = ch[[k in floors_wanted for k in zip(ch.site_id, ch.floor_id)]]
        for s, f, g in zip(ch.site_id, ch.floor_id, ch.geometry):
            try:
                p = wkt.loads(g)
            except Exception:
                continue
            if not p.is_empty:
                wins[(s, f)].append(p)
                seen += 1
        print(f"  ... {seen:,} window openings", file=sys.stderr, flush=True)
    return wins


def evaluate(dw, wins):
    """One record per dwelling: which window-needing rooms have a window."""
    out = []
    for i, (key, rooms) in enumerate(dw.items()):
        if i % 5000 == 0:
            print(f"  ... {i:,}/{len(dw):,} dwellings", file=sys.stderr, flush=True)
        site, floor, _apt = key
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
        band_env = env.exterior.buffer(NEAR_M)
        floor_wins = [w for w in wins.get((site, floor), ()) if w.intersects(band_env)]
        tree = STRtree(floor_wins) if floor_wins else None

        rec = {"k": f"{site}|{floor}|{_apt}", "n": len(polys), "types": subs,
               "rooms": []}
        need = [(sub, p) for sub, p in zip(subs, polys) if sub in NEEDS_WINDOW]
        for sub, p in need:
            band = p.exterior.buffer(NEAR_M)
            has = False
            if tree is not None:
                has = any(floor_wins[j].intersects(band)
                          for j in tree.query(band))
            rec["rooms"].append({"sub": sub, "win": has, "area": p.area})
        if not rec["rooms"]:
            continue

        # borrowed daylight: does a windowless room touch a windowed habitable one?
        # Paired by position, never by subtype -- two BEDROOMs are two rooms.
        lit = [p for (sub, p), r in zip(need, rec["rooms"])
               if sub in HABITABLE and r["win"]]
        lit_union = unary_union(lit) if lit else None
        for r, (_sub, p) in zip(rec["rooms"], need):
            r["borrowed"] = bool(
                (not r["win"]) and lit_union is not None
                and p.buffer(ADJOIN_M).intersects(lit_union))
        rec["fail_rooms"] = [r["sub"] for r in rec["rooms"] if not r["win"]]
        rec["fails"] = bool(rec["fail_rooms"])
        rec["kitchen_only"] = (rec["fails"]
                               and set(rec["fail_rooms"]) <= {"KITCHEN"})
        rec["all_borrowed"] = (rec["fails"]
                               and all(r["borrowed"] for r in rec["rooms"]
                                       if not r["win"]))
        out.append(rec)
    return out


def ms_of(types):
    return tuple(sorted(Counter(COLLAPSE.get(t, t) for t in types).items()))


def main():
    OUT.mkdir(exist_ok=True)
    print("loading the converted-corpus room cache ...", file=sys.stderr)
    dw, _keys = pickle.load(open(FITS / "swiss_dw.pkl", "rb"))
    floors = {(s, f) for (s, f, _a) in dw}
    print(f"{len(dw):,} dwellings on {len(floors):,} floors", file=sys.stderr)

    wins = load_windows(floors)
    print(f"windows on {len(wins):,} floors", file=sys.stderr)

    recs = evaluate(dw, wins)
    json.dump(recs, open(OUT / "window_rule_index.json", "w"), separators=(",", ":"))

    # ---------------------------------------------------------------- 1. index
    rule("1. `win.habitable_has_window` over the full index")
    n = len(recs)
    fails = [r for r in recs if r["fails"]]
    konly = [r for r in fails if r["kitchen_only"]]
    print(f"dwellings evaluated                   {n:,}")
    print(f"  fail win.habitable_has_window       {len(fails):,}  {pct(len(fails), n)}")
    print(f"    ...on the KITCHEN alone           {len(konly):,}  {pct(len(konly), n)}")
    print(f"    ...on a non-kitchen room          {len(fails)-len(konly):,}  "
          f"{pct(len(fails)-len(konly), n)}")
    print(f"  h8-frontage measured 43.3 % / 23.0 pts / 20.3 pts on 561 dwellings")

    rule("1b. by room subtype — no window on its own boundary")
    per = defaultdict(lambda: [0, 0])
    for r in recs:
        for x in r["rooms"]:
            per[x["sub"]][1] += 1
            if not x["win"]:
                per[x["sub"]][0] += 1
    print(f"{'subtype':<16}{'no window':>11}{'total':>10}{'rate':>9}")
    for k, (a, b) in sorted(per.items(), key=lambda kv: -kv[1][1]):
        print(f"{k:<16}{a:>11,}{b:>10,}{pct(a, b):>9}")

    rule("1c. borrowed daylight — the taxca-metbex shape, at index scale")
    wl = [x for r in recs for x in r["rooms"] if not x["win"]]
    wlk = [x for x in wl if x["sub"] == "KITCHEN"]
    for lbl, pop in (("all windowless rooms", wl), ("windowless KITCHENs", wlk)):
        b = sum(1 for x in pop if x["borrowed"])
        med = st.median([x["area"] for x in pop]) if pop else 0
        print(f"{lbl:<24} n={len(pop):>7,}  adjoin a windowed habitable room "
              f"{pct(b, len(pop))}  median area {med:5.1f} m2")
    print("  h8-frontage measured 84.7 % adjoining, median 6.8 m2, on 549 kitchens")
    dw_all_borrowed = sum(1 for r in fails if r["all_borrowed"])
    print(f"\ndwellings whose EVERY failing room is borrowed-daylight: "
          f"{dw_all_borrowed:,} of {len(fails):,} failing  "
          f"{pct(dw_all_borrowed, len(fails))}  "
          f"= {pct(dw_all_borrowed, n)} of the index")

    # ------------------------------------------------------- 2. the paired 2x2
    rule("2. THE OVERLAP — ADR 0016's conversion drop x the window rule, paired")
    fit = {r["k"]: r["status"] for r in json.load(open(FITS / "swiss_fit_k2.json"))}
    byk = {r["k"]: r for r in recs}
    pairs = [(fit[k], byk[k]) for k in fit if k in byk]
    decided = [(s, r) for s, r in pairs if s != "UNKNOWN"]
    print(f"fit sample {len(fit):,}; joined to the window evaluation {len(pairs):,}; "
          f"decided {len(decided):,}")
    tab = Counter((s in DECIDED_OK, not r["fails"]) for s, r in decided)
    N = len(decided)
    cc, cf = tab[(True, True)], tab[(True, False)]
    rc, rf = tab[(False, True)], tab[(False, False)]
    print(f"\n{'':<22}{'window PASS':>14}{'window FAIL':>14}{'total':>10}")
    print(f"{'conversion CONVERTS':<22}{cc:>14,}{cf:>14,}{cc+cf:>10,}")
    print(f"{'conversion REFUSES':<22}{rc:>14,}{rf:>14,}{rc+rf:>10,}")
    print(f"{'total':<22}{cc+rc:>14,}{cf+rf:>14,}{N:>10,}")
    print(f"\nconversion refuses              {pct(rc+rf, N)}   (ADR 0016: 9.74 %)")
    print(f"window rule refuses             {pct(cf+rf, N)}   (h8: 43.3 %)")
    print(f"BOTH refuse (the overlap)       {pct(rf, N)}")
    print(f"either refuses (the joint drop) {pct(cf+rc+rf, N)}")
    print(f"survive both                    {pct(cc, N)}")
    exp = (rc + rf) / N * (cf + rf) / N
    print(f"\noverlap if the two were independent: {100*exp:5.2f}%   "
          f"observed {pct(rf, N).strip()}   lift {rf/N/exp:4.2f}x" if exp else "")
    print(f"window rule's MARGINAL cost, on dwellings the conversion keeps: "
          f"{pct(cf, cc+cf)}")

    # -------------------------------------------------------- 3. the slope in n
    rule("3. The slope — ADR 0016 flattened the conversion's; does this restore one?")
    print(f"{'n':>4}{'dwellings':>11}{'window fail':>13}{'conv refuse':>13}"
          f"{'either':>10}{'survive':>10}")
    byn = defaultdict(list)
    for s, r in decided:
        byn[r["n"]].append((s, r))
    for k in sorted(byn):
        if k < 3 or k > 12:
            continue
        g = byn[k]
        wf = sum(1 for s, r in g if r["fails"])
        cr = sum(1 for s, r in g if s not in DECIDED_OK)
        ei = sum(1 for s, r in g if r["fails"] or s not in DECIDED_OK)
        print(f"{k:>4}{len(g):>11,}{pct(wf, len(g)):>13}{pct(cr, len(g)):>13}"
              f"{pct(ei, len(g)):>10}{pct(len(g)-ei, len(g)):>10}")

    # ----------------------------------------------- 4. what it costs the pool
    rule("4. What filtering the index costs the POOL, per collapsed multiset")
    for r in recs:
        r["ms"] = ms_of(r["types"])
    by_ms = defaultdict(list)
    for r in recs:
        by_ms[r["ms"]].append(r)
    print(f"index {len(recs):,} dwellings, {len(by_ms):,} distinct multisets "
          f"(proposer.md 2.2.1 quotes 916 over 46,794)")
    print(f"\n{'band':<7}{'briefs':>9}{'blank now':>12}{'blank filtered':>16}"
          f"{'median pool':>13}{'median filtered':>17}")
    for b, rr in BANDS.items():
        sel = [r for r in recs if r["n"] in rr]
        bn = ba = 0
        pn, pa = [], []
        for r in sel:
            bucket = by_ms[r["ms"]]
            now = len(bucket) - 1
            after = sum(1 for x in bucket if not x["fails"]) - (0 if r["fails"] else 1)
            bn += now == 0
            ba += after == 0
            pn.append(now)
            pa.append(after)
        print(f"{b:<7}{len(sel):>9,}{pct(bn, len(sel)):>12}{pct(ba, len(sel)):>16}"
              f"{st.median(pn):>13.1f}{st.median(pa):>17.1f}")
    print("\nproposer.md 2.2.7, after the conversion: blank 9.7 % / 12.8 %, "
          "median pool 86.6 / 58.7")

    rule("5. And what a BORROWED-DAYLIGHT exception would buy back")
    keep = lambda r: (not r["fails"]) or r["all_borrowed"]
    for b, rr in BANDS.items():
        sel = [r for r in recs if r["n"] in rr]
        ba = sum(1 for r in sel
                 if sum(1 for x in by_ms[r["ms"]] if keep(x)) - (1 if keep(r) else 0) == 0)
        pa = st.median([sum(1 for x in by_ms[r["ms"]] if keep(x)) - (1 if keep(r) else 0)
                        for r in sel])
        print(f"{b:<7}{len(sel):>9,} briefs   blank {pct(ba, len(sel))}   "
              f"median pool {pa:6.1f}")
    kept = sum(1 for r in recs if keep(r))
    print(f"\nindex retained under the exception: {kept:,} of {len(recs):,}  "
          f"{pct(kept, len(recs))}   (hard rule as shipped: "
          f"{pct(len(recs)-len(fails), len(recs))})")


if __name__ == "__main__":
    main()
