"""Two properties the first pass judged on proxies too weak to decide on.

(a) FACADE.  Pass 1 measured each room's *share* of the outer boundary and found
    social rooms hold less of it per square metre than private rooms.  Share is
    the wrong quantity: an architect allocates *aspect* -- a corner, two
    elevations, one long unbroken window wall -- not boundary length.  Both are
    topological and neither needs the site, so both are measurable here.

(b) LIVING-ROOM TRANSIT.  `circ.no_private_transit` blocks routing *through* a
    private room.  Nothing blocks routing through the living room, which is the
    classic amateur-plan signature.  Measured as a cut-set: does every path from
    the entrance to this bedroom pass through a social room?
"""
import sys, json, hashlib
from collections import defaultdict, Counter, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "rectangularise"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from shapely import wkt as shwkt
from shapely.ops import unary_union
import measure_swiss as MS
import measure_zoning as Z

OUT = Path(__file__).resolve().parent / "out"
RUN_MIN = 1.0          # an exterior run shorter than this holds no window
ANGLE_TOL = 20.0       # degrees: two runs closer than this are one elevation


def _runs(geom, boundary):
    """Exterior runs this room holds: [(length, orientation_deg)]."""
    import math
    f = MS._poly(geom.buffer(MS.TAU, join_style=2, mitre_limit=2.0))
    if f is None:
        return []
    seg = boundary.intersection(f)
    if seg.is_empty:
        return []
    parts = [seg] if seg.geom_type == "LineString" else list(
        getattr(seg, "geoms", []))
    out = []
    for p in parts:
        if p.geom_type != "LineString" or p.length < RUN_MIN:
            continue
        c = list(p.coords)
        dx, dy = c[-1][0] - c[0][0], c[-1][1] - c[0][1]
        out.append((p.length, math.degrees(math.atan2(dy, dx)) % 180.0))
    return out


def _aspects(runs):
    """Distinct elevations: runs whose orientations differ by > ANGLE_TOL."""
    ors = []
    for _, a in sorted(runs, key=lambda r: -r[0]):
        if all(min(abs(a - b), 180 - abs(a - b)) > ANGLE_TOL for b in ors):
            ors.append(a)
    return len(ors)


def _cut(adj, n, entry, target, blocked):
    """Is `target` reachable from `entry` avoiding every node in `blocked`?"""
    if entry in blocked or target in blocked:
        return True                      # question does not arise
    seen, q = {entry}, deque([entry])
    while q:
        u = q.popleft()
        if u == target:
            return True
        for v in adj[u]:
            if v not in seen and v not in blocked:
                seen.add(v)
                q.append(v)
    return False


def measure_one(items, door_wkts):
    geoms, types = [], []
    for st, w in items:
        p = MS._poly(shwkt.loads(w))
        if p is None:
            return None
        geoms.append(p)
        types.append(st)
    n = len(geoms)
    if not (3 <= n <= 12):
        return "n_out_of_band"

    best, best_a = None, 0.0
    for w in door_wkts:
        d = MS._poly(shwkt.loads(w))
        if d is None:
            continue
        for i, g in enumerate(geoms):
            f = MS._poly(g.buffer(MS.TAU / 2, join_style=2, mitre_limit=2.0))
            if f is None or not f.intersects(d):
                continue
            a = MS._area(MS._op(lambda x, y: x.intersection(y), f, d))
            if a > best_a:
                best, best_a = i, a
    if best is None:
        return "entry_not_located"

    adj = defaultdict(set)
    for i, j in MS.contact_graph(geoms):
        adj[i].add(j)
        adj[j].add(i)
    seen, q = {best}, deque([best])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                q.append(v)
    if len(seen) < n:
        return "disconnected"

    K = [Z.cls(t) for t in types]
    priv = [i for i in range(n) if K[i] == "private"]
    if not priv:
        return "no_private_room"

    env = MS._op(unary_union, [MS._poly(g.buffer(MS.TAU / 2, join_style=2,
                                                 mitre_limit=2.0)) for g in geoms])
    if env is None or not hasattr(env, "exterior"):
        return "no_envelope"
    b = env.exterior

    runs = [_runs(g, b) for g in geoms]
    aspects = [_aspects(r) for r in runs]
    longest = [max([x[0] for x in r], default=0.0) for r in runs]

    social = {i for i in range(n) if K[i] == "social"}
    circ = {i for i in range(n) if K[i] == "circ"}
    via_social = [not _cut(adj, n, best, i, social) for i in priv]
    via_circ = [not _cut(adj, n, best, i, circ) for i in priv]

    return {
        "n": n, "classes": K, "entry": best, "entry_class": K[best],
        "area": [g.area for g in geoms],
        "aspects": aspects, "longest_run": longest,
        "priv": priv,
        "priv_via_social": via_social,
        "priv_via_circ": via_circ,
    }


def main():
    n_target = int(sys.argv[1]) if len(sys.argv) > 1 else 2500
    rooms, doors = Z.load()
    keys = sorted(rooms.keys())
    keys.sort(key=lambda k: hashlib.md5("|".join(k).encode()).hexdigest())
    recs, skipped = [], Counter()
    for k in keys:
        if len(recs) >= n_target:
            break
        if not doors.get(k):
            skipped["no_entrance"] += 1
            continue
        try:
            r = measure_one(rooms[k], doors[k])
        except Exception as e:
            skipped["err:" + type(e).__name__] += 1
            continue
        if r is None or isinstance(r, str):
            skipped[r or "unmeasurable"] += 1
            continue
        r["k"] = "|".join(k)
        recs.append(r)
        if len(recs) % 500 == 0:
            print("  {}".format(len(recs)), flush=True)
    json.dump({"recs": recs, "skipped": dict(skipped)},
              open(OUT / "zoning2.json", "w"))
    print("measured {}; skipped {}".format(len(recs), dict(skipped)), flush=True)


if __name__ == "__main__":
    main()
