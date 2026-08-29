"""Is entry depth a different property from social transit?  (ticket 43)

proposer.md 6.1 term 3 is social transit: sleeping Rooms reachable ONLY through
a social Space, real 11.1%.  If the entry-depth inversion (private nearer the
door than social, 17.4%) is the same dwellings, a fifth term buys nothing.

zoning.json (pass 1, has `dist`) and zoning2.json (pass 2, has `priv_via_social`)
are the same 2500 keys, joined on `k`.
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent / "out"
p1 = {r["k"]: r for r in json.load(open(OUT / "zoning.json"))["recs"]}
p2 = {r["k"]: r for r in json.load(open(OUT / "zoning2.json"))["recs"]}
keys = sorted(set(p1) & set(p2))
print("joined dwellings: {} (pass1 {}, pass2 {})".format(len(keys), len(p1), len(p2)))


def md(rec, ks):
    ds = [d for d, k in zip(rec["dist"], rec["classes"]) if k in ks]
    return min(ds) if ds else None


cells = {(a, b): 0 for a in (0, 1) for b in (0, 1)}
n = 0
for k in keys:
    a, b = p1[k], p2[k]
    pr, so = md(a, {"private"}), md(a, {"social"})
    if pr is None or so is None:
        continue
    n += 1
    inv = 1 if pr < so else 0                      # entry-depth inversion
    tr = 1 if any(b["priv_via_social"]) else 0     # social transit, dwelling level
    cells[(inv, tr)] += 1

print()
print("                       transit=0  transit=1    total")
for inv in (0, 1):
    r0, r1 = cells[(inv, 0)], cells[(inv, 1)]
    print("  inversion={}          {:>7}    {:>7}  {:>7}".format(inv, r0, r1, r0 + r1))
c0 = cells[(0, 0)] + cells[(1, 0)]
c1 = cells[(0, 1)] + cells[(1, 1)]
print("  total               {:>7}    {:>7}  {:>7}".format(c0, c1, n))
print()
inv_t = cells[(1, 0)] + cells[(1, 1)]
print("inversion rate            {:>5}/{} = {:.1f}%".format(inv_t, n, 100.0 * inv_t / n))
print("transit rate              {:>5}/{} = {:.1f}%".format(c1, n, 100.0 * c1 / n))
print("both                      {:>5}/{} = {:.1f}%".format(cells[(1, 1)], n, 100.0 * cells[(1, 1)] / n))
exp = inv_t * c1 / n
print("expected under independence: {:.1f}".format(exp))
print()
print("inversion dwellings NOT caught by transit: {} = {:.1f}% of all dwellings".format(
    cells[(1, 0)], 100.0 * cells[(1, 0)] / n))
print("transit dwellings NOT caught by inversion: {} = {:.1f}% of all dwellings".format(
    cells[(0, 1)], 100.0 * cells[(0, 1)] / n))
try:
    from scipy.stats import fisher_exact
    odds, p = fisher_exact([[cells[(0, 0)], cells[(0, 1)]],
                            [cells[(1, 0)], cells[(1, 1)]]])
    print("Fisher exact: odds {:.3f}, p = {:.4f}".format(odds, p))
except Exception as e:
    print("(scipy unavailable: {})".format(e))
