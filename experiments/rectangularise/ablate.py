"""Which constraint actually rejects a dwelling?

The joint fit drops a dwelling when no rectangular tiling satisfies all of it at
once. That is the reject rule, and it is only a useful one if we can say what it
is rejecting FOR -- otherwise nobody tuning this later knows which knob moves it.

Relaxes one family at a time over the same dwellings.

The arms ARE ADR 0008's fidelity ladder, which is why re-running this is not
merely diagnosis: `as shipped` is tier A, `relations, neighbours only` is tier B,
`no hard relations` is tier C and `relations + adjacency off` is tier D. Ticket
40 item 3 asks whether the ladder still earns its complexity at k <= 2, and this
is the run that answers it.

Run: python experiments/rectangularise/ablate.py [n] [--k2]
"""
import hashlib
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fit_rects as F  # noqa: E402
from measure_swiss import COLS, GEOM, MD5_EMPTY, NOT_A_ROOM  # noqa: E402

# Arms are ordered cheapest first, and each carries its own sample size: the
# two arms that drop the hard relations run ~7x slower, because the relations
# are what prunes the search, so they are measured on fewer dwellings and their
# figures carry a wider band.
TIER = {"as shipped": "A", "relations, neighbours only": "B",
        "no hard relations": "C", "relations + adjacency off": "D"}

ARMS = [
    ("as shipped",                dict(), 250),
    ("area band +/-25%",          dict(area_tol=0.25), 250),
    ("area free",                 dict(area_tol=0.95), 250),
    ("up to 4 notches",           dict(max_notches=4), 250),
    ("relations, neighbours only", dict(rel_scope="adjacent"), 250),
    ("no hard adjacency",         dict(use_adj=False), 250),
    ("no hard relations",         dict(use_rel=False), 80),
    ("relations + adjacency off", dict(use_rel=False, use_adj=False), 80),
]


def main():
    n_target = int(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else 250
    k_max = 2 if "--k2" in sys.argv else 1
    dw = defaultdict(list)
    for chunk in pd.read_csv(GEOM, usecols=COLS, chunksize=500_000, dtype=str):
        a = chunk[(chunk["entity_type"] == "area") &
                  (chunk["unit_usage"] == "RESIDENTIAL") &
                  (chunk["apartment_id"] != MD5_EMPTY)]
        a = a[~a["entity_subtype"].isin(NOT_A_ROOM)]
        for s, f, ap, st, wkt in zip(a["site_id"], a["floor_id"], a["apartment_id"],
                                     a["entity_subtype"].fillna("<NA>"), a["geometry"]):
            dw[(s, f, ap)].append((st, wkt))
    keys = sorted(dw.keys())
    keys.sort(key=lambda k: hashlib.md5("|".join(k).encode()).hexdigest())

    geoms = []
    for k in keys:
        if len(geoms) >= n_target:
            break
        g = F.load_swiss_geoms(dw[k])
        if g is not None:
            geoms.append(g)
    print(f"dwellings: {len(geoms)}  k_max={k_max}\n", flush=True)

    print(f"{'arm':<28} {'n':>5} {'converted':>10} {'INFEASIBLE':>11} "
          f"{'UNKNOWN':>9} {'other':>7}")
    for label, kw, n in ARMS:
        sub = geoms[:n]
        st = Counter()
        for g in sub:
            st[F.run_dwelling(g, k_max=k_max, **kw)["status"]] += 1
        ok = st["OPTIMAL"] + st["FEASIBLE"]
        other = sum(v for k, v in st.items()
                    if k not in ("OPTIMAL", "FEASIBLE", "INFEASIBLE", "UNKNOWN"))
        print(f"{label:<28} {TIER.get(label, '-'):>4} {len(sub):>5} "
              f"{ok / len(sub):>10.4f} {st['INFEASIBLE']:>11} "
              f"{st['UNKNOWN']:>9} {other:>7}", flush=True)


if __name__ == "__main__":
    main()
