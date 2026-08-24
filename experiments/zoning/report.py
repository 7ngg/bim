"""Read out/zoning.json and answer ticket 30 item 3."""
import json, statistics as st
from collections import Counter, defaultdict
from pathlib import Path

OUT = Path(__file__).resolve().parent / "out"
d = json.load(open(OUT / "zoning.json"))
R = d["recs"]
print("dwellings measured: {}".format(len(R)))
print("skipped: {}\n".format(d["skipped"]))

# ---------------------------------------------------------------- 1. gradient
print("=" * 68)
print("1. HOP DISTANCE FROM THE ENTRANCE, BY CLASS")
print("   is there a day/night gradient a set-shaped rule could assert?")
print("=" * 68)
byc = defaultdict(list)
for r in R:
    for i, k in enumerate(r["classes"]):
        byc[k].append(r["dist"][i])
print("{:<10}{:>7}{:>8}{:>8}{:>8}{:>8}".format(
    "class", "n", "mean", "median", "p10", "p90"))
for k in ("circ", "kitchen", "social", "wet", "private", "other"):
    v = sorted(byc[k])
    if not v:
        continue
    print("{:<10}{:>7}{:>8.2f}{:>8}{:>8}{:>8}".format(
        k, len(v), st.mean(v), v[len(v) // 2], v[len(v) // 10], v[9 * len(v) // 10]))

# within-dwelling: is private further than social in the SAME dwelling?
gt = lt = eq = 0
for r in R:
    p = [r["dist"][i] for i, k in enumerate(r["classes"]) if k == "private"]
    s = [r["dist"][i] for i, k in enumerate(r["classes"]) if k == "social"]
    if not p or not s:
        continue
    a, b = st.mean(p), st.mean(s)
    gt += a > b
    lt += a < b
    eq += a == b
tot = gt + lt + eq
print("\nwithin one dwelling, mean private hop vs mean social hop:")
print("  private FURTHER : {:5d}  {:5.1f}%".format(gt, 100 * gt / tot))
print("  equal           : {:5d}  {:5.1f}%".format(eq, 100 * eq / tot))
print("  private NEARER  : {:5d}  {:5.1f}%".format(lt, 100 * lt / tot))

# ------------------------------------------------------- 2. the candidate rule
print()
print("=" * 68)
print("2. IS A PRIVATE ROOM ENTERED FROM CIRCULATION?")
print("   the candidate hard rule, at the potential-circulation layer")
print("=" * 68)
rooms_tc = sum(sum(r["touch_circ"]) for r in R)
rooms_p = sum(len(r["priv"]) for r in R)
rooms_so = sum(sum(r["social_only"]) for r in R)
print("private rooms                      : {}".format(rooms_p))
print("  touching circulation             : {:6d}  {:5.1f}%".format(
    rooms_tc, 100 * rooms_tc / rooms_p))
print("  touching a social room           : {:6d}  {:5.1f}%".format(
    sum(sum(r["touch_social"]) for r in R), rooms_p) if False else
    "  touching a social room           : {:6d}  {:5.1f}%".format(
        sum(sum(r["touch_social"]) for r in R),
        100 * sum(sum(r["touch_social"]) for r in R) / rooms_p))
print("  NO circ, only social             : {:6d}  {:5.1f}%".format(
    rooms_so, 100 * rooms_so / rooms_p))

alltc = sum(1 for r in R if all(r["touch_circ"]))
anyso = sum(1 for r in R if any(r["social_only"]))
print("\ndwellings where EVERY private room touches circulation:"
      " {:5d}  {:5.1f}%".format(alltc, 100 * alltc / len(R)))
print("dwellings with at least one social-only private room  :"
      " {:5d}  {:5.1f}%".format(anyso, 100 * anyso / len(R)))

# by room count, because C13's band is 3-10
print("\nby engine room count:")
print("{:>4}{:>8}{:>12}{:>14}".format("n", "dwell", "all-circ %", "social-only %"))
bn = defaultdict(list)
for r in R:
    bn[r["n"]].append(r)
for n in sorted(bn):
    v = bn[n]
    a = 100 * sum(1 for r in v if all(r["touch_circ"])) / len(v)
    b = 100 * sum(1 for r in v if any(r["social_only"])) / len(v)
    print("{:>4}{:>8}{:>12.1f}{:>14.1f}".format(n, len(v), a, b))

# --------------------------------------------------------------- 3. grouping
print()
print("=" * 68)
print("3. ARE THE PRIVATE ROOMS GROUPED?")
print("   components of the private set: touching, or off a shared circ node")
print("=" * 68)
c = Counter(r["priv_components"] for r in R)
cn = Counter(len(r["priv"]) for r in R)
print("private rooms per dwelling: {}".format(dict(sorted(cn.items()))))
tot = len(R)
for k in sorted(c):
    print("  {} component(s): {:5d}  {:5.1f}%".format(k, c[k], 100 * c[k] / tot))
multi = [r for r in R if len(r["priv"]) >= 2]
one = sum(1 for r in multi if r["priv_components"] == 1)
print("\nof the {} dwellings with 2+ private rooms, {} ({:.1f}%) hold them in ONE"
      " group".format(len(multi), one, 100 * one / len(multi)))
c2 = Counter(r["priv_components"] for r in multi)
for k in sorted(c2):
    print("  {} component(s): {:5d}  {:5.1f}%".format(k, c2[k], 100 * c2[k] / len(multi)))

# ---------------------------------------------------------------- 4. facade
print()
print("=" * 68)
print("4. FACADE ALLOCATION: share of the outer boundary, by class")
print("=" * 68)
fb, ab = defaultdict(list), defaultdict(list)
for r in R:
    tot_a = sum(r["area"])
    for i, k in enumerate(r["classes"]):
        if r["facade"][i] is None:
            continue
        fb[k].append(r["facade"][i])
        ab[k].append(r["area"][i] / tot_a if tot_a else 0)
print("{:<10}{:>7}{:>12}{:>12}{:>10}".format(
    "class", "n", "facade share", "area share", "ratio"))
for k in ("social", "private", "kitchen", "wet", "circ", "other"):
    if not fb[k]:
        continue
    f, a = st.mean(fb[k]), st.mean(ab[k])
    print("{:<10}{:>7}{:>12.3f}{:>12.3f}{:>10.2f}".format(k, len(fb[k]), f, a, f / a if a else 0))

# does the living room get MORE facade than a bedroom, per dwelling?
gt = lt = 0
for r in R:
    s = [r["facade"][i] for i, k in enumerate(r["classes"])
         if k == "social" and r["facade"][i] is not None]
    p = [r["facade"][i] for i, k in enumerate(r["classes"])
         if k == "private" and r["facade"][i] is not None]
    if not s or not p:
        continue
    gt += max(s) > max(p)
    lt += max(s) <= max(p)
print("\nper dwelling, does the best-facade social room beat the best-facade"
      " private room?")
print("  yes: {:5d}  {:5.1f}%".format(gt, 100 * gt / (gt + lt)))
print("  no : {:5d}  {:5.1f}%".format(lt, 100 * lt / (gt + lt)))

# ------------------------------------------------------------- 5. entry class
print()
print("=" * 68)
print("5. WHAT THE FRONT DOOR OPENS ONTO")
print("=" * 68)
c = Counter(r["entry_class"] for r in R)
for k, v in c.most_common():
    print("  {:<10}{:5d}  {:5.1f}%".format(k, v, 100 * v / len(R)))
