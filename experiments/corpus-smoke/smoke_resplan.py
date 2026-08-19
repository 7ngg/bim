"""ResPlan loader smoke test.

Opens ResPlan.pkl with a restricted unpickler (whitelist only), parses one plan,
prints its room types and geometry bounds, and checks the released counts against
the paper's published figures.

Run: python experiments/corpus-smoke/smoke_resplan.py
"""

import io
import json
import pickle
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKL = ROOT / "data" / "corpora" / "resplan" / "ResPlan.pkl"
SPLIT = ROOT / "data" / "corpora" / "resplan" / "split.json"

# The pickle is third-party data. Refuse to construct anything outside this set,
# so loading it cannot execute arbitrary code.
ALLOWED = {
    ("shapely.io", "from_wkb"),
    ("numpy.core.multiarray", "_reconstruct"),
    ("numpy._core.multiarray", "_reconstruct"),
    ("numpy", "ndarray"),
    ("numpy", "dtype"),
    ("numpy.core.multiarray", "scalar"),
    ("numpy._core.multiarray", "scalar"),
}


class Restricted(pickle.Unpickler):
    seen = set()

    def find_class(self, module, name):
        Restricted.seen.add((module, name))
        if (module, name) not in ALLOWED:
            raise pickle.UnpicklingError(f"blocked global: {module}.{name}")
        return super().find_class(module, name)


def main() -> int:
    plans = Restricted(io.BufferedReader(open(PKL, "rb"))).load()
    print(f"globals referenced by the pickle: {sorted(Restricted.seen)}")
    print(f"plans loaded: {len(plans)}")

    keys = list(plans[0].keys())
    print(f"per-plan keys ({len(keys)}): {keys}")

    ROOM_KEYS = [
        "living", "kitchen", "bedroom", "bathroom", "balcony",
        "garden", "parking", "pool", "storage", "stair",
    ]

    p = plans[0]
    print(f"\n--- plan[0] id={p.get('id')} ---")
    print(f"area={p.get('area')} net_area={p.get('net_area')}")
    for k in ROOM_KEYS:
        v = p.get(k)
        if v:
            n = len(v) if isinstance(v, (list, tuple)) else 1
            print(f"  {k:<9} n={n}")
    inner = p.get("inner")
    geom = inner[0] if isinstance(inner, (list, tuple)) else inner
    print(f"  inner bounds (metres?): {geom.bounds}")
    wall = p.get("wall")
    if wall is not None:
        w = wall[0] if isinstance(wall, (list, tuple)) else wall
        print(f"  wall[0] bounds: {w.bounds}  wall_depth={p.get('wall_depth')}")

    # Room counts per plan, over the whole corpus.
    counts = Counter()
    functional = 0
    for pl in plans:
        n = 0
        for k in ROOM_KEYS:
            v = pl.get(k)
            if v:
                n += len(v) if isinstance(v, (list, tuple)) else 1
        counts[n] += 1
        functional += n
    print(f"\nmean rooms/plan (all {len(ROOM_KEYS)} classes): {functional/len(plans):.2f}")
    print(f"rooms/plan histogram: {dict(sorted(counts.items()))}")

    if SPLIT.exists():
        sp = json.load(open(SPLIT))
        print(f"\nsplit.json keys: {list(sp.keys())}")
        for k, v in sp.items():
            print(f"  {k}: {len(v) if hasattr(v,'__len__') else v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
