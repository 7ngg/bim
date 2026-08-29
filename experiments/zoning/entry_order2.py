"""The slogan, stated positively -- and how soft R4's violation is.

entry_order.py refuted the ticket's own hop-1 candidates.  This asks the
question the other way round: what DOES the corpus put at hop 1, and is the
day/night order (R4) violated by a hop or by a mile?
"""
import json
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent / "out"
recs = json.load(open(OUT / "zoning.json"))["recs"]


def md(rec, ks):
    ds = [d for d, k in zip(rec["dist"], rec["classes"]) if k in ks]
    return min(ds) if ds else None


print("dwellings: {}".format(len(recs)))
print()
print("=" * 72)
print("A. THE SLOGAN, POSITIVELY: front door -> hall -> living")
print("=" * 72)
slogan = sum(1 for r in recs
             if r["entry_class"] == "circ" and md(r, {"social"}) == 1)
has_soc = sum(1 for r in recs if md(r, {"social"}) is not None)
print("entry is circulation AND a social room sits at hop exactly 1:")
print("  {} / {} dwellings with a social room = {:.1f}%".format(
    slogan, has_soc, 100.0 * slogan / has_soc))
print()
print("where the nearest social room sits (hop from the entry Space):")
c = Counter(md(r, {"social"}) for r in recs if md(r, {"social"}) is not None)
for k in sorted(c):
    print("  hop {}: {:>5}  {:>5.1f}%".format(k, c[k], 100.0 * c[k] / has_soc))
print()
print("  -> R1 ('no otaq at hop 1') FORBIDS the modal case.")
print()

print("=" * 72)
print("B. WHAT SITS AT HOP 1 AT ALL")
print("=" * 72)
at1 = Counter()
n1 = 0
for r in recs:
    for i in range(r["n"]):
        if r["dist"][i] == 1:
            at1[r["classes"][i]] += 1
            n1 += 1
for k, v in at1.most_common():
    print("  {:<10} {:>6}  {:>5.1f}%".format(k, v, 100.0 * v / n1))
print()

print("=" * 72)
print("C. R4 (nearest private >= nearest social) -- how soft is the breach?")
print("=" * 72)
gap = Counter()
appl = 0
for r in recs:
    p, s = md(r, {"private"}), md(r, {"social"})
    if p is None or s is None:
        continue
    appl += 1
    gap[p - s] += 1
print("applicable: {} dwellings".format(appl))
print("  d(nearest private) - d(nearest social):")
for k in sorted(gap):
    tag = "  <- VIOLATION" if k < 0 else ("  <- tie" if k == 0 else "")
    print("   {:>+3}: {:>5}  {:>5.1f}%{}".format(k, gap[k], 100.0 * gap[k] / appl, tag))
viol = sum(v for k, v in gap.items() if k < 0)
strict = sum(v for k, v in gap.items() if k > 0)
print()
print("  strict (private FURTHER):  {:>5}  {:.1f}%".format(strict, 100.0 * strict / appl))
print("  tie:                       {:>5}  {:.1f}%".format(gap[0], 100.0 * gap[0] / appl))
print("  violation (private NEARER): {:>4}  {:.1f}%  = 1 in {:.1f}".format(
    viol, 100.0 * viol / appl, appl / viol))
print()
print("  every violation is by exactly one hop: {}".format(
    all(k >= -1 for k in gap if k < 0)))
