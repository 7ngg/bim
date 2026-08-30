"""Does the contact threshold drive result 2?  Re-measure at a looser run."""
import sys, json, hashlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import measure_zoning as Z
import measure_swiss as MS

rooms, doors = Z.load()
keys = sorted(rooms.keys())
keys.sort(key=lambda k: hashlib.md5("|".join(k).encode()).hexdigest())

for run in (1.00, 0.80, 0.60):
    MS.DOOR_CONTACT = run
    orig = MS.contact_graph
    MS.contact_graph = lambda g, tau=MS.TAU, min_run=run: orig(g, tau, min_run)
    n, tc, p, allc, skip = 0, 0, 0, 0, 0
    for k in keys:
        if n >= 600:
            break
        if not doors.get(k):
            continue
        try:
            r = Z.measure_one(rooms[k], doors[k])
        except Exception:
            continue
        if r is None or isinstance(r, str):
            skip += 1
            continue
        n += 1
        tc += sum(r["touch_circ"])
        p += len(r["sleeping_rooms"])
        allc += all(r["touch_circ"])
    print("min_run {:.2f} m: dwellings {}, skipped {}, sleeping rooms touching "
          "circ {:.1f}%, dwellings all-circ {:.1f}%".format(
              run, n, skip, 100 * tc / p, 100 * allc / n), flush=True)
    MS.contact_graph = orig
