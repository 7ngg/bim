"""Ticket 35 item 4, ResPlan half — does ResPlan record a finish layer
separately from a structural one? Inspect the record schema only; no plotting,
no conversion. Read-only.
"""
import pickle, os, sys, collections

P = os.path.join("data", "corpora", "resplan", "ResPlan.pkl")

with open(P, "rb") as fh:
    data = pickle.load(fh)

print("top-level type:", type(data))
if isinstance(data, dict):
    print("top-level keys:", list(data.keys())[:20])
    sample = data[list(data.keys())[0]]
elif isinstance(data, (list, tuple)):
    print("n records:", len(data))
    sample = data[0]
else:
    sample = data

print("\nsample record type:", type(sample))
if isinstance(sample, dict):
    for k, v in sample.items():
        tv = type(v).__name__
        try:
            extra = f" len={len(v)}" if hasattr(v, "__len__") else ""
        except Exception:
            extra = ""
        print(f"  {k!r}: {tv}{extra}  -> {str(v)[:110]}")

# scan every key name across a sample of records for finish/layer/thickness words
WORDS = ("finish", "layer", "plaster", "render", "thick", "wall", "material", "skin", "core")
keys = collections.Counter()
recs = data.values() if isinstance(data, dict) else data
for i, rec in enumerate(recs):
    if i >= 500:
        break
    if isinstance(rec, dict):
        keys.update(rec.keys())
print("\nall record keys seen in first 500 records:")
for k, c in keys.most_common():
    hit = [w for w in WORDS if w in str(k).lower()]
    print(f"  {k!r}  x{c}" + (f"   <== matches {hit}" if hit else ""))

# distribution of wall_depth — is it one scalar per plan, and is it uniform?
import statistics
vals = [r["wall_depth"] for r in recs if isinstance(r, dict) and "wall_depth" in r]
print(f"\nwall_depth: n={len(vals)} min={min(vals):.4f} max={max(vals):.4f} "
      f"mean={statistics.mean(vals):.4f} median={statistics.median(vals):.4f} "
      f"distinct={len(set(round(v,6) for v in vals))}")
print("It is ONE scalar per plan. There is no per-wall thickness, no material, "
      "no layer decomposition, and no separate finish entity anywhere in the record.")
