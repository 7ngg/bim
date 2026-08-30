"""Read out/zoning2.json: aspect allocation, and living-room transit."""
import json, statistics as st
from collections import Counter, defaultdict
from pathlib import Path

OUT = Path(__file__).resolve().parent / "out"
d = json.load(open(OUT / "zoning2.json"))
R = d["recs"]
print("dwellings measured: {}".format(len(R)))
print("skipped: {}\n".format(d["skipped"]))

print("=" * 70)
print("A. ASPECT, NOT BOUNDARY SHARE")
print("   pass 1 measured share and found social rooms hold LESS per m2.")
print("   an architect allocates elevations and a long window wall.")
print("=" * 70)
asp, lng, ar = defaultdict(list), defaultdict(list), defaultdict(list)
for r in R:
    for i, k in enumerate(r["classes"]):
        asp[k].append(r["aspects"][i])
        lng[k].append(r["longest_run"][i])
        ar[k].append(r["area"][i])
print("{:<10}{:>7}{:>10}{:>12}{:>14}{:>10}".format(
    "class", "n", "mean asp", "dual-aspect", "longest run m", "mean m2"))
for k in ("social", "sleeping", "kitchen", "wet", "circ", "other"):
    if not asp[k]:
        continue
    dual = 100 * sum(1 for a in asp[k] if a >= 2) / len(asp[k])
    print("{:<10}{:>7}{:>10.2f}{:>11.1f}%{:>14.2f}{:>10.1f}".format(
        k, len(asp[k]), st.mean(asp[k]), dual, st.mean(lng[k]), st.mean(ar[k])))

# per dwelling: does a social room take the best aspect / longest run?
for label, key in (("dual aspect (>=2 elevations)", "aspects"),
                   ("longest single exterior run", "longest_run")):
    win = tie = loss = 0
    for r in R:
        s = [r[key][i] for i, k in enumerate(r["classes"]) if k == "social"]
        p = [r[key][i] for i, k in enumerate(r["classes"]) if k == "sleeping"]
        if not s or not p:
            continue
        a, b = max(s), max(p)
        win += a > b
        tie += a == b
        loss += a < b
    t = win + tie + loss
    print("\nper dwelling, best social room vs best sleeping room on {}:".format(label))
    print("  social WINS  : {:5d}  {:5.1f}%".format(win, 100 * win / t))
    print("  tie          : {:5d}  {:5.1f}%".format(tie, 100 * tie / t))
    print("  sleeping wins : {:5d}  {:5.1f}%".format(loss, 100 * loss / t))

# area-normalised, the pass-1 confound
print("\narea-normalised longest run (m per m2), to kill the size confound:")
for k in ("social", "sleeping", "kitchen", "wet"):
    v = [l / a for l, a in zip(lng[k], ar[k]) if a > 0]
    print("  {:<10}{:.4f}".format(k, st.mean(v)))

print()
print("=" * 70)
print("B. LIVING-ROOM TRANSIT")
print("   circ.no_private_transit blocks routing THROUGH a bedroom.")
print("   nothing blocks routing through the living room.")
print("=" * 70)
np_ = sum(len(r["sleeping_rooms"]) for r in R)
vs = sum(sum(r["sleeping_via_social"]) for r in R)
vc = sum(sum(r["priv_via_circ"]) for r in R)
print("sleeping rooms                                   : {}".format(np_))
print("  reachable ONLY through a social room          : {:5d}  {:5.1f}%".format(
    vs, 100 * vs / np_))
print("  reachable ONLY through circulation            : {:5d}  {:5.1f}%".format(
    vc, 100 * vc / np_))
dws = sum(1 for r in R if any(r["sleeping_via_social"]))
print("\ndwellings with at least one such bedroom        : {:5d}  {:5.1f}%".format(
    dws, 100 * dws / len(R)))

print("\nby engine room count -- does it concentrate in small flats?")
print("{:>4}{:>8}{:>16}{:>18}".format("n", "dwell", "via-social %", "bedrooms via-soc %"))
bn = defaultdict(list)
for r in R:
    bn[r["n"]].append(r)
for n in sorted(bn):
    v = bn[n]
    a = 100 * sum(1 for r in v if any(r["sleeping_via_social"])) / len(v)
    tp = sum(len(r["sleeping_rooms"]) for r in v)
    b = 100 * sum(sum(r["sleeping_via_social"]) for r in v) / tp if tp else 0
    print("{:>4}{:>8}{:>16.1f}{:>18.1f}".format(n, len(v), a, b))

# does a corridor existing predict it?
has_c = [r for r in R if "circ" in r["classes"]]
no_c = [r for r in R if "circ" not in r["classes"]]
for lab, v in (("with circulation", has_c), ("without circulation", no_c)):
    if not v:
        continue
    a = 100 * sum(1 for r in v if any(r["sleeping_via_social"])) / len(v)
    print("\n{:<22}{:5d} dwellings, {:5.1f}% route a bedroom through a social room"
          .format(lab, len(v), a))
