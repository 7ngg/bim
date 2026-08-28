"""proposer.md 2.2's coverage table, restated on the converted corpus.

Ticket 23. The published table -- 9.5 % blank at 4-6 rooms, 12.4 % at 7-10,
median pool 92 and 66 -- was measured on the **unconverted** corpus by
`experiments/retrieval-coverage/`. Retrieval can only warp a dwelling the
conversion could represent, so every one of those pools thins.

`experiments/rectangularise/coverage_thinning.py` hands over the thinning
factor **per room multiset**, which is the unit retrieval gates in, and warns
against applying a single corpus-wide number. This does the join properly:

    blank_after(brief) = (1 - t[multiset]) ^ pool_size(brief)
    pool_after(brief)  = pool_size(brief) * t[multiset]

in expectation, over the full 46,794-dwelling index rather than the 2,600
sampled by the fit. A multiset the fit did not sample enough of falls back to
its band's rate, and how many Briefs that covers is reported rather than hidden.

⚠️ **This file gates against a random same-room-count donor `d`, not against the
Brief, and that is deliberate — do NOT "fix" it to match `absolute_area`'s
`admissible_pool`.** It predates ADR 0020. Back then a Brief's area and aspect
came from an Envelope donor, so drawing one is how a Brief is simulated here;
under ADR 0020 the Brief carries its own. `gate_curve.py`, `room_area_spread.py`
and `pool_fidelity.py` share the convention. Changing it re-bases **86.6 and
58.7** — the production pool depths quoted across the whole map — so it is a
decision with its own blast radius and not a tidy-up. Ticket 60 left it alone on
purpose and recorded it here.

Run: python experiments/warp/coverage_restated.py
"""

from __future__ import annotations

import json
import random
import statistics as st
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
ROOMS = OUT / "dwelling_rooms.json"
FITS = HERE.parent / "rectangularise" / "out"
AREA_TOL, ASPECT_TOL, SEED = 0.10, 0.15, 20260819
COLLAPSE = {"ROOM": "PRIVATE", "BEDROOM": "PRIVATE", "STUDIO": "PRIVATE"}
MIN_SAMPLE = 15          # below this a multiset's own rate is noise
BANDS = {"4-6": range(4, 7), "7-10": range(7, 11)}


def ms_of(rooms):
    return tuple(sorted(Counter(COLLAPSE.get(t, t) for t, _ in rooms).items()))


def main():
    recs = json.load(open(ROOMS))
    for r in recs:
        r["ms"] = ms_of(r["rooms"])
    by_ms, by_n = defaultdict(list), defaultdict(list)
    for r in recs:
        by_ms[r["ms"]].append(r)
        by_n[r["n"]].append(r)
    print(f"full index: {len(recs):,} dwellings, {len(by_ms):,} multisets")

    fit = {r["k"]: r["status"] in ("OPTIMAL", "FEASIBLE")
           for r in json.load(open(FITS / "swiss_fit_k2.json"))
           if r["status"] != "UNKNOWN"}
    key_ms = {r["k"]: r["ms"] for r in recs}
    hit, tot = defaultdict(int), defaultdict(int)
    bhit, btot = defaultdict(int), defaultdict(int)
    nrooms = {r["k"]: r["n"] for r in recs}
    for k, ok in fit.items():
        if k not in key_ms:
            continue
        tot[key_ms[k]] += 1
        hit[key_ms[k]] += ok
        for b, rr in BANDS.items():
            if nrooms[k] in rr:
                btot[b] += 1
                bhit[b] += ok
    band_rate = {b: bhit[b] / btot[b] for b in btot}
    print(f"fit sample: {len(fit):,} decided dwellings; band conversion "
          + ", ".join(f"{b} {band_rate[b]:.4f}" for b in sorted(band_rate)))

    def t_of(ms, n):
        if tot[ms] >= MIN_SAMPLE:
            return hit[ms] / tot[ms], True
        for b, rr in BANDS.items():
            if n in rr:
                return band_rate.get(b, 0.9), False
        return 0.9, False

    print()
    print(f"{'band':<7}{'briefs':>9}{'blank now':>11}{'blank after':>13}"
          f"{'median now':>12}{'median after':>14}{'own rate':>10}")
    out = {}
    for b, rr in BANDS.items():
        rng = random.Random(SEED)
        sel = [r for r in recs if r["n"] in rr]
        blanks_now = blanks_after = 0
        pools_now, pools_after, own = [], [], 0
        for r in sel:
            d = rng.choice(by_n[r["n"]])
            pool = sum(1 for p in by_ms[r["ms"]]
                       if p["k"] != r["k"]
                       and abs(p["area"] - d["area"]) <= AREA_TOL * d["area"]
                       and abs(p["aspect"] - d["aspect"]) <= ASPECT_TOL * d["aspect"])
            t, exact = t_of(r["ms"], r["n"])
            own += exact
            pools_now.append(pool)
            pools_after.append(pool * t)
            if pool == 0:
                blanks_now += 1
                blanks_after += 1
            else:
                blanks_after += (1 - t) ** pool
        m = len(sel)
        pools_now.sort()
        pools_after.sort()
        print(f"{b:<7}{m:>9,}{100*blanks_now/m:>10.1f}%{100*blanks_after/m:>12.1f}%"
              f"{pools_now[m//2]:>12,}{pools_after[m//2]:>14.1f}"
              f"{100*own/m:>9.1f}%")
        out[b] = {"briefs": m,
                  "blank_now_pct": round(100 * blanks_now / m, 2),
                  "blank_after_pct": round(100 * blanks_after / m, 2),
                  "median_pool_now": pools_now[m // 2],
                  "median_pool_after": round(pools_after[m // 2], 1),
                  "own_multiset_rate_pct": round(100 * own / m, 1)}

    print("\n'own rate' is the share of Briefs whose multiset the fit sampled at")
    print(f"least {MIN_SAMPLE} times; the rest fall back to their band's rate.")
    OUT.mkdir(exist_ok=True)
    json.dump(out, open(OUT / "coverage_restated.json", "w"), indent=1)
    print(f"\nwrote {OUT/'coverage_restated.json'}")


if __name__ == "__main__":
    main()
