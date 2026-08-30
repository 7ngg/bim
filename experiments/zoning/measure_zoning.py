"""Is there a zoning signal in the corpus at all?  (ticket 30, item 3)

The Proposal transmits pairwise separation directions.  Zoning is a property of
a *set* against a set, so the question this answers is whether real dwellings
show a consistent one -- something a model could learn or a rule could assert.

Measured on Swiss Dwellings, in the corpus's own coordinates, over the contact
graph `measure_swiss.contact_graph` already defines (tau 0.30 m, door run
1.00 m).  Contact, not doors: that is *potential* circulation -- the layer the
solver actually constrains (CONTEXT.md).

Reads geometries.csv directly rather than swiss_fit.json, because the latter's
type labels are known off-by-one on 1.23 % of dwellings (ticket 40).
"""
import sys, json, hashlib
from collections import defaultdict, Counter, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "rectangularise"))
from shapely import wkt as shwkt
from shapely.ops import unary_union
import measure_swiss as MS

GEOM = MS.GEOM
OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(parents=True, exist_ok=True)

# Swiss subtype -> the class this system reasons in.  DERIVED, and this rig
# holds no table (ticket 80, ADR 0044).
#
# It used to hold one, and it was the FIFTH sleeping copy of the corpus-label
# projection ADR 0037 published -- the sweep that retired the other four never
# reached here, because ticket 69's write scope was `experiments/warp/`.  What
# the copy got wrong, measured against the full corpus:
#
#   * it named a {ROOM, BEDROOM, STUDIO} collapse in its own comment and mapped
#     only two of the three, so STUDIO fell to "other".  7 RESIDENTIAL rooms in
#     7 apartments -- none of which reached the measured 2 500, so the defect
#     was latent rather than benign;
#   * it did not map KITCHEN_DINING at all: 41 RESIDENTIAL rooms, of which 3
#     are in the measured set and were scored "other" instead of social;
#   * three of its entries CANNOT OCCUR.  OFFICE, LOBBY and CORRIDORS_AND_HALLS
#     have zero RESIDENTIAL rooms between them -- 376 / 118 / 42 rooms, all
#     COMMERCIAL, PUBLIC or JANITOR -- and load() filters RESIDENTIAL.  So the
#     ticket's "decide what OFFICE maps to" was a question about a label the
#     residential pipeline cannot see.
#
# The class is now `profile_read.zone_class_for_label`, which reads the
# published bridge (`ergonomic.corpus_label_map`) and the flags.  The bridge
# carries the three-way collapse, so STUDIO is handled by the data.
sys.path.insert(0, str(ROOT / "experiments" / "region-profile"))
import profile_read as PR


def cls(t):
    """Corpus label -> zoning class.  Unknown labels are "other", as before --
    but the KNOWN ones now come from the bridge rather than from a dict here."""
    try:
        return PR.zone_class_for_label(t)
    except KeyError:
        return "other"


def load():
    """(site, floor, apartment) -> rooms [(subtype, wkt)], entrance door wkts."""
    import pandas as pd
    rooms, doors = defaultdict(list), defaultdict(list)
    for chunk in pd.read_csv(GEOM, usecols=MS.COLS, chunksize=500_000, dtype=str):
        chunk = chunk[(chunk["unit_usage"] == "RESIDENTIAL") &
                      (chunk["apartment_id"] != MS.MD5_EMPTY)]
        a = chunk[chunk["entity_type"] == "area"]
        a = a[~a["entity_subtype"].isin(MS.NOT_A_ROOM)]
        for s, f, ap, st, g in zip(a["site_id"], a["floor_id"], a["apartment_id"],
                                   a["entity_subtype"].fillna("<NA>"), a["geometry"]):
            rooms[(s, f, ap)].append((st, g))
        d = chunk[chunk["entity_subtype"] == "ENTRANCE_DOOR"]
        for s, f, ap, g in zip(d["site_id"], d["floor_id"], d["apartment_id"],
                               d["geometry"]):
            doors[(s, f, ap)].append(g)
    return rooms, doors


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

    # entry room: the room whose fattened polygon overlaps an entrance door most
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

    edges = MS.contact_graph(geoms)
    adj = defaultdict(set)
    for i, j in edges:
        adj[i].add(j)
        adj[j].add(i)

    # hop distance from the entry room over the contact graph
    dist = {best: 0}
    q = deque([best])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    if len(dist) < n:
        return "disconnected"            # a conversion artefact

    K = [cls(t) for t in types]
    sleep_idx = [i for i in range(n) if K[i] == "sleeping"]
    if not sleep_idx:
        return "no_sleeping_room"
    circ_nodes = {v for v in range(n) if K[v] == "circ"}

    # 1. does each sleeping room touch circulation?  touch a social room?
    touch_circ = [any(K[v] == "circ" for v in adj[i]) for i in sleep_idx]
    touch_soc = [any(K[v] == "social" for v in adj[i]) for i in sleep_idx]
    # entered ONLY through social space: no circ neighbour, but a social one
    social_only = [(not c) and s for c, s in zip(touch_circ, touch_soc)]

    # 2. are the sleeping rooms grouped?  components of the sleeping set in a
    #    graph where two sleeping rooms are joined by touching, or by sharing a
    #    circulation node -- "off the same hall" is grouped; touching is not
    #    required, and real bedrooms rarely touch.
    link = defaultdict(set)
    for i in sleep_idx:
        for j in sleep_idx:
            if i >= j:
                continue
            if j in adj[i] or (adj[i] & adj[j] & circ_nodes):
                link[i].add(j)
                link[j].add(i)
    seen, comps = set(), 0
    for i in sleep_idx:
        if i in seen:
            continue
        comps += 1
        stack = [i]
        seen.add(i)
        while stack:
            u = stack.pop()
            for v in link[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)

    # 3. facade share: fraction of the dwelling's outer boundary each room holds
    env = MS._op(unary_union, [MS._poly(g.buffer(MS.TAU / 2, join_style=2,
                                                 mitre_limit=2.0)) for g in geoms])
    facade = {}
    if env is not None and hasattr(env, "exterior"):
        b = env.exterior
        tot = b.length
        for i, g in enumerate(geoms):
            f = MS._poly(g.buffer(MS.TAU, join_style=2, mitre_limit=2.0))
            facade[i] = (b.intersection(f).length / tot) if (f is not None and tot > 0) else 0.0

    return {
        "n": n, "types": types, "classes": K, "entry": best,
        "entry_class": K[best],
        "dist": [dist[i] for i in range(n)],
        "area": [g.area for g in geoms],
        "facade": [facade.get(i) for i in range(n)],
        "sleeping_rooms": sleep_idx,
        "touch_circ": touch_circ, "touch_social": touch_soc,
        "social_only": social_only,
        "sleeping_groups": comps,
        "deg": [len(adj[i]) for i in range(n)],
    }


def main():
    n_target = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    rooms, doors = load()
    keys = sorted(rooms.keys())
    keys.sort(key=lambda k: hashlib.md5("|".join(k).encode()).hexdigest())
    print("dwellings loaded: {}; with entrance door: {}".format(
        len(keys), sum(1 for k in keys if doors.get(k))), flush=True)

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
        if len(recs) % 250 == 0:
            print("  {}".format(len(recs)), flush=True)
    json.dump({"recs": recs, "skipped": dict(skipped)},
              open(OUT / "zoning.json", "w"))
    print("measured {}; skipped {}".format(len(recs), dict(skipped)), flush=True)


if __name__ == "__main__":
    main()
