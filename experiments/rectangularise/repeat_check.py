"""Assert that the conversion returns the same answer twice on the same input.

Ticket 85, the sibling of `experiments/warp/salt_check.py` and deliberately NOT
an extension of it.

**Why this is not a line in `salt_check.py`.** That check catches a defect that
is *static and unconditional*: `random.Random(SEED ^ hash(key))` is wrong in
every rig, in every context, and a regex can say so. `num_search_workers = 4` is
not that. It is **correct** in `solver.py` -- `solver-formulation.md` II.6
measured one worker failing to reach a valid Plan at all at 24 rooms, and ADR
0043 decision 4 accepts that the shipped projection is therefore not reproducible
and says why that is entailed rather than broken. A pattern that fires on both
the defect and the defended decision cannot separate them, and `salt_check.py`'s
own docstring names the failure it would become: *"a checker whose first two
findings are its own prose is a checker nobody will keep."* Its OWED table would
absorb the real finding and the check would go quiet.

What is checkable is not the *parameter* but the *behaviour*, and only on a rig
that claims reproducibility. So this asserts the claim directly, on the rig that
makes it: solve, solve again, compare.

**What it asserts, and what it deliberately does not.** Two runs at
`--workers=1` must agree on everything the map ever publishes -- status,
objective, the number of Parts per Room, and the shape class those Parts make.
They are NOT asserted to agree on the rectangles themselves: ADR 0046 measured
tied optima returning different covers between two runs of identical code, which
is google/or-tools issue #3948 and is not this repo's to fix. A check that
asserted the cover would be red on a defect nobody here can repair, so it
asserts the published plane and states the gap.

Dwellings are chosen to solve well inside the cap, because a record at the wall
clock's boundary can legitimately flip decided/undecided between runs -- measured
at 2 in 56 -- and a check that is red one run in thirty is a check that gets
switched off.

Run: ./venv/Scripts/python.exe experiments/rectangularise/repeat_check.py
Exit 0 when both runs agree on the published plane, 1 on any disagreement.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from determinism import shape_of                      # noqa: E402
from fit_rects import (SEED, TIME_LIMIT, WORKERS,                  # noqa: E402
                       load_swiss_geoms, run_dwelling, swiss_keys)

OUT = Path(__file__).resolve().parent / "out"
BASELINE = OUT / "swiss_fit_k2.json"
N_DWELLINGS = 3
FAST = 2.0          # seconds in the baseline: well inside any cap the rig uses
# Taken from `fit_rects`, never restated. A check that hard-codes the
# configuration it is asserting goes green on a config nobody ships the day
# someone edits one and not the other.
CAP = TIME_LIMIT


def published(r):
    """Every quantity a document is allowed to quote off one record."""
    parts = r.get("parts") or []
    return {
        "status": r["status"],
        "objective": r.get("objective"),
        "k_used": r.get("k_used"),
        "shapes": [shape_of(p) for p in parts if len(p) >= 2],
        "n_parts": r.get("n_parts"),
    }


def prove_red():
    """Show the comparator detects a real disagreement, not just equality.

    `salt_check.py` is proven in both directions -- red on a reverted site, green
    on repair -- and a green-only check is a check nobody can trust. Proving red
    by RUNNING the four-worker config would be stochastic (it disagrees ~27 % of
    the time, so a demonstration could come back green), so this reads two arms
    already on disk and finds a record they actually differ on.
    """
    a, b = OUT / "det" / "rep1.json", OUT / "det" / "rep2.json"
    if not (a.exists() and b.exists()):
        print("  (no rep1/rep2 on disk -- red-direction proof skipped)")
        return
    ra = {r["k"]: r for r in json.load(open(a))}
    rb = {r["k"]: r for r in json.load(open(b))}
    # FEASIBLE, not OPTIMAL. The shipped arms agree on the published plane for
    # every PROVED record -- 0 shape and 0 objective differences in 307 of them,
    # ADR 0046 -- so a proof-only search finds nothing and would report the
    # comparator untested. The instability is entirely in the truncated records.
    hits = 0
    for k in ra:
        if k not in rb or ra[k]["status"] != rb[k]["status"]:
            continue
        if ra[k]["status"] not in ("OPTIMAL", "FEASIBLE"):
            continue
        x, y = published(ra[k]), published(rb[k])
        if x != y:
            if not hits:
                f = next(n for n in x if x[n] != y[n])
                print(f"  red direction PROVEN on the shipped 4-worker arms: "
                      f"{ra[k]['status']} record {k[:28]}... differs on `{f}`")
            hits += 1
    if hits:
        print(f"  ({hits} such records in rep1 vs rep2 -- the comparator is not "
              "green-only)")
    else:
        print("  (rep1/rep2 agree everywhere -- nothing to prove red)")


def main():
    recs = json.load(open(BASELINE))
    # Must contain a two-part Room. The shape class is the most fragile thing on
    # the published plane and the only one derived from the cover, so a sample of
    # all-one-Part dwellings would pass while the classifier was broken. The
    # first draft of this check did exactly that.
    fast = [r for r in recs
            if r["status"] == "OPTIMAL" and r.get("seconds", 99) < FAST
            and any(k >= 2 for k in r.get("k_used", []))]
    picked = [fast[i] for i in
              (0, len(fast) // 2, len(fast) - 1)][:N_DWELLINGS]
    dw, _ = swiss_keys()

    print("repeat check -- the conversion, twice, on one input")
    print(f"  workers={WORKERS}  seed={SEED}  cap={CAP}s wall  "
          f"-- read from fit_rects, not restated here")
    print(f"  {len(picked)} dwellings, each proved OPTIMAL in under {FAST}s\n")

    bad = 0
    for r in picked:
        key = tuple(r["k"].split("|"))
        geoms = load_swiss_geoms(dw[key], [])
        runs = [run_dwelling(geoms, k_max=2, hint="shape", time_limit=CAP,
                             workers=WORKERS) for _ in range(2)]
        a, b = published(runs[0]), published(runs[1])
        ok = a == b
        bad += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {r['k']:<45} "
              f"{a['status']:<9} obj {a['objective']} k {a['k_used']} "
              f"{a['shapes']}")
        if not ok:
            for f in sorted(set(a) | set(b)):
                if a.get(f) != b.get(f):
                    print(f"         {f}: {a.get(f)!r}  vs  {b.get(f)!r}")

    print()
    prove_red()
    if bad:
        print(f"{bad} dwelling(s) disagree on the PUBLISHED plane. A figure "
              "quoted off this rig is not reproducible; do not publish it "
              "until this is green.")
        return 1
    print(f"{len(picked)} dwellings, 0 disagreements on the published plane. "
          "PASS.")
    print("Reproducible ON THIS MACHINE, verified by repeat -- never "
          "cross-machine (ADR 0043 decision 3).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
