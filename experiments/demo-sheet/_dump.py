import json, pathlib, random, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import run as R
import briefs_az
from collections import defaultdict

cands = R.load()
by_ms = defaultdict(list)
for c in cands:
    by_ms[c["ms"]].append(c)
briefs = briefs_az.build(by_ms, otaq=[2, 3])
rng = random.Random(R.SEED)
rng.shuffle(briefs)
b = briefs[0]
rec, best = R.serve(b, by_ms, 4, 2.0, 8.0, False, rng)
plan = R.to_plan(b["k"], best, {})
from bim_engine import openings, dimensions
openings.place(plan)
d = dimensions.derive(plan)
print("inner", plan.inner)
for ch in d.chains:
    print("chain tier=%s side=%s axis=%s rung=%s pts=%s segs=%s"
          % (ch.tier, ch.side, ch.axis, ch.rung, ch.points, ch.segments))
for r in d.runnings:
    print("running side=%s axis=%s %s->%s = %s rung=%s" % (r.side, r.axis, r.frm, r.to, r.value, r.rung))
for so in d.setting_out:
    print("sod", so.opening.mark, so.axis, so.frm, so.to, so.value)
