"""Ticket 85. What a non-reproducible conversion costs the figures quoted from it.

`fit_rects.py` ran CP-SAT at `num_search_workers = 4` under a 10 s WALL-CLOCK cap.
ADR 0041 published 1 535 two-part Rooms; the same rig on the same input later gave
1 543. Every corpus number on the map is quoted from that file or a sibling.

THE TICKET'S PREMISE IS HALF RIGHT, AND THE HALF THAT IS WRONG CHANGES THE FIX.
`random_seed` was never set, but CP-SAT's own default IS 1 -- asserted in
`selftest()` below -- so every process already ran at seed 1 and the seed was never
the variable. What varies is WHICH worker finishes what before the wall clock
stops, and a tiling problem's optimum is not unique. Adding `random_seed = 1` is a
no-op. The fix has to remove the race, not key it.

Three arms, all on ONE key list so every comparison is paired:

  REPEAT   the shipped config, run twice. The status-quo defect size. Nothing is
           varied at all -- if these two disagree, wall-clock racing is proved on
           its own and neither seed nor cap is implicated.
  SEED     seed varied, cap held. Isolates the mechanism the ticket named.
  CAP      cap varied, seed held. Isolates the other one. Running only this arm
           is the error 82 caught in the warp: it attributes both to one.
  FIX      a candidate reproducible config, run twice. Determinism is a claim
           about repeat runs, so it is measured the same way the defect was.

Reported per arm, against the arm it is paired with:

  status disagreement   a dwelling that converts in one run and not the other
  cover  disagreement   same status, different rectangles -- the silent one
  k_used disagreement   a Room that is two Parts in one run and one in the other,
                        which is exactly what moves ADR 0041's count
  shape  drift          the L / T / Z / rectangle split, per arm

Run:
  python experiments/rectangularise/determinism.py selftest
  python experiments/rectangularise/determinism.py sample N
  python experiments/rectangularise/determinism.py report ARM_A ARM_B [...]
"""
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
DET = OUT / "det"
DET.mkdir(parents=True, exist_ok=True)
BASELINE = OUT / "swiss_fit_k2.json"
KEYS = DET / "keys.json"

DECIDED = ("OPTIMAL", "FEASIBLE")


# ------------------------------------------------------------------- shapes
def shape_of(parts):
    """`L`, `T`, `Z`, `rectangle`, `single`, or `apart`.

    Independently written from `plane-accounting/arms_parts.shape_of` -- that
    directory belongs to ticket 83 and is not edited here -- and `selftest`
    asserts this one reproduces ADR 0045's published 851 / 334 / 331 / 27 on the
    baseline file. If the two ever disagree, the assert fails loudly rather than
    this rig quietly reporting a different distribution.
    """
    if len(parts) < 2:
        return "single"
    (px1, py1, px2, py2), (qx1, qy1, qx2, qy2) = parts
    if px2 == qx1 or qx2 == px1:
        lo1, hi1, lo2, hi2 = py1, py2, qy1, qy2
    elif py2 == qy1 or qy2 == py1:
        lo1, hi1, lo2, hi2 = px1, px2, qx1, qx2
    else:
        return "apart"
    f_lo, f_hi = lo1 == lo2, hi1 == hi2
    if f_lo and f_hi:
        return "rectangle"
    if f_lo or f_hi:
        return "L"
    if (lo1 < lo2 and hi2 < hi1) or (lo2 < lo1 and hi1 < hi2):
        return "T"
    return "Z"


def shape_counts(recs):
    c = Counter()
    for r in recs:
        for parts in r.get("parts") or []:
            if len(parts) >= 2:
                c[shape_of(parts)] += 1
    return c


def not_l_share(c):
    tot = sum(c.values())
    return (tot - c["L"]) / tot if tot else float("nan")


def figures(recs):
    """The published quantities this file is the source of, recomputed per arm.

    Each one is a headline somewhere on the map, so a drift band is a band on
    THESE and not on a summary statistic invented here.
    """
    dec = [r for r in recs if r["status"] in DECIDED]
    undec = [r for r in recs if r["status"] == "UNKNOWN"]
    # rectangularisation.md 11.0: UNDECIDED is excluded, never counted as a drop.
    denom = [r for r in recs if r["status"] != "UNKNOWN"]
    offered = sum(sum(1 for x in r["k_offered"] if x >= 2) for r in dec)
    used = sum(sum(1 for x in r["k_used"] if x >= 2) for r in dec)
    c = shape_counts(dec)
    rooms = sum(len(r["k_used"]) for r in dec)
    return {
        "converted": len(dec) / len(denom) if denom else float("nan"),
        "undecided": len(undec) / len(recs) if recs else float("nan"),
        "rooms": rooms,
        "two_part": used,
        "offered": offered,
        "used_share": used / offered if offered else float("nan"),
        "two_part_room_share": used / rooms if rooms else float("nan"),
        "L": c["L"], "T": c["T"], "Z": c["Z"], "rect": c["rectangle"],
        "not_l": not_l_share(c),
    }


# -------------------------------------------------------------------- arms
def load(name):
    p = DET / f"{name}.json"
    if not p.exists():
        p = OUT / f"{name}.json"
    return {r["k"]: r for r in json.load(open(p))}


def canon(r):
    """The cover, as a comparable value. Part order within a Room is not meaning."""
    return tuple(tuple(sorted(tuple(b) for b in parts))
                 for parts in (r.get("parts") or []))


def pair(a, b):
    """One arm against another, on the dwellings both decided."""
    keys = sorted(set(a) & set(b))
    st_diff = [k for k in keys if a[k]["status"] != b[k]["status"]]
    both = [k for k in keys if a[k]["status"] == b[k]["status"]
            and a[k]["status"] in DECIDED]
    cover_diff = [k for k in both if canon(a[k]) != canon(b[k])]
    k_diff = [k for k in both if a[k]["k_used"] != b[k]["k_used"]]
    obj_diff = [k for k in both if a[k].get("objective") != b[k].get("objective")]
    # Rooms, not dwellings: the count ADR 0041 publishes is a Room count.
    rooms = sum(len(a[k]["k_used"]) for k in both)
    room_k_diff = sum(sum(1 for x, y in zip(a[k]["k_used"], b[k]["k_used"]) if x != y)
                      for k in both)
    two_a = sum(sum(1 for x in a[k]["k_used"] if x >= 2) for k in both)
    two_b = sum(sum(1 for x in b[k]["k_used"] if x >= 2) for k in both)
    # THE published quantity. A cover can move while the Room stays an L, and
    # ADR 0045's table counts shape classes, not rectangles -- so this is the
    # disagreement rate that reaches a document and the cover rate is not.
    # Counted only where both runs gave the Room the same number of Parts; a
    # 1-vs-2 Room is already counted in `room_k_diff`.
    shp = shp_tot = 0
    for k in both:
        for pa, pb in zip(a[k]["parts"], b[k]["parts"]):
            if len(pa) >= 2 and len(pb) >= 2:
                shp_tot += 1
                shp += shape_of(pa) != shape_of(pb)
    return {"n": len(keys), "decided_both": len(both),
            "status_diff": len(st_diff), "cover_diff": len(cover_diff),
            "k_diff_dwellings": len(k_diff), "obj_diff": len(obj_diff),
            "rooms": rooms, "room_k_diff": room_k_diff,
            "two_part_a": two_a, "two_part_b": two_b,
            "shape_cmp": shp_tot, "shape_diff": shp,
            "status_diff_keys": st_diff[:10]}


def arm(name, extra, n, force=False):
    """One `fit_rects` run, restricted to the shared key list."""
    p = DET / f"{name}.json"
    if p.exists() and not force:
        print(f"  {name}: exists, skipping")
        return
    cmd = [sys.executable, str(HERE / "fit_rects.py"), str(n), "--k2",
           f"--only={KEYS}", f"--out=det/{name}.json", "--every=50"] + extra
    print("  " + " ".join(cmd[1:]), flush=True)
    log = DET / f"{name}.log"
    with open(log, "w") as fh:
        subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT, check=True,
                       cwd=str(HERE))
    print(f"  {name}: {Path(log).read_text().strip().splitlines()[-2]}", flush=True)


def make_sample(n):
    """The first n dwellings of the baseline, which is the same md5 order.

    A prefix of the shipped run, so the baseline file itself is a third repeat of
    the shipped config for free -- and the sample is a random draw of the corpus,
    because `swiss_keys` sorts on the md5 of the key.
    """
    recs = json.load(open(BASELINE))
    keys = [r["k"] for r in recs][:n]
    json.dump(keys, open(KEYS, "w"))
    print(f"{len(keys)} keys -> {KEYS}")


# ---------------------------------------------------------------- selftest
def selftest():
    from ortools.sat.python import cp_model
    d = cp_model.CpSolver().parameters
    assert d.random_seed == 1, d.random_seed
    print(f"cp_model default random_seed = {d.random_seed}  "
          "-- the rig was never running at an arbitrary seed")
    print(f"cp_model default num_search_workers = {d.num_search_workers} "
          "(0 = pick by core count); fit_rects pinned it to 4")

    recs = json.load(open(BASELINE))
    c = shape_counts(recs)
    print("\nshape classifier against ADR 0045 §8, on the baseline file:")
    want = {"L": 851, "T": 334, "Z": 331, "rectangle": 27}
    for k, v in want.items():
        got = c[k]
        print(f"  {k:<10} published {v:>5}   here {got:>5}   "
              f"{'ok' if got == v else 'MISMATCH'}")
    assert c["apart"] == 0, f"{c['apart']} two-part Rooms are not edge-sharing"
    assert {k: c[k] for k in want} == want, dict(c)
    print(f"  total      published  1543   here {sum(c.values()):>5}")
    print(f"  not-L      published  44,8%  here {100 * not_l_share(c):.1f}%")
    print("\nselftest ok")


# ------------------------------------------------------------------ report
def report(names):
    arms = {n: load(n) for n in names}
    print(f"{'arm':<18} {'n':>5} {'OPT':>5} {'FEAS':>5} {'INF':>5} {'UNK':>5} "
          f"{'2-part':>7} {'L':>5} {'T':>5} {'Z':>5} {'rect':>5} {'not-L':>7}")
    for n, a in arms.items():
        recs = list(a.values())
        st = Counter(r["status"] for r in recs)
        c = shape_counts(recs)
        two = sum(c.values())
        print(f"{n:<18} {len(recs):>5} {st['OPTIMAL']:>5} {st['FEASIBLE']:>5} "
              f"{st['INFEASIBLE']:>5} {st['UNKNOWN']:>5} {two:>7} "
              f"{c['L']:>5} {c['T']:>5} {c['Z']:>5} {c['rectangle']:>5} "
              f"{100 * not_l_share(c):>6.1f}%")

    print(f"\n{'pair':<34} {'dec':>5} {'stat!=':>6} {'cover!=':>7} {'obj!=':>6} "
          f"{'rooms':>6} {'k!=':>5} {'2p A':>6} {'2p B':>6} "
          f"{'shp n':>6} {'shp!=':>6}")
    ns = list(arms)
    for i in range(len(ns)):
        for j in range(i + 1, len(ns)):
            a, b = ns[i], ns[j]
            r = pair(arms[a], arms[b])
            print(f"{a + ' vs ' + b:<34} {r['decided_both']:>5} "
                  f"{r['status_diff']:>6} {r['cover_diff']:>7} {r['obj_diff']:>6} "
                  f"{r['rooms']:>6} {r['room_k_diff']:>5} "
                  f"{r['two_part_a']:>6} {r['two_part_b']:>6} "
                  f"{r['shape_cmp']:>6} {r['shape_diff']:>6}")

    print(f"\n{'arm':<18} {'conv':>7} {'undec':>7} {'rooms':>6} {'offered':>8} "
          f"{'2-part':>7} {'used%':>7} {'2p/room':>8} {'not-L':>7}")
    for n, a in arms.items():
        f = figures(list(a.values()))
        print(f"{n:<18} {f['converted']:>7.4f} {f['undecided']:>7.4f} "
              f"{f['rooms']:>6} {f['offered']:>8} {f['two_part']:>7} "
              f"{100 * f['used_share']:>6.1f}% {100 * f['two_part_room_share']:>7.2f}% "
              f"{100 * f['not_l']:>6.1f}%")

    print("\nseconds per dwelling, and where the cap bites:")
    for n, a in arms.items():
        secs = sorted(r["seconds"] for r in a.values() if "seconds" in r)
        tot = sum(secs)
        capped = sum(1 for r in a.values() if r["status"] in ("FEASIBLE", "UNKNOWN"))
        print(f"  {n:<18} total {tot:>7.0f}s   mean {tot / len(secs):>5.2f}s   "
              f"p50 {secs[len(secs) // 2]:>5.2f}s   p95 {secs[int(0.95 * len(secs))]:>6.2f}s   "
              f"cap-limited {capped:>4} ({100 * capped / len(secs):.1f} %)")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "selftest"
    if cmd == "selftest":
        return selftest()
    if cmd == "sample":
        return make_sample(int(sys.argv[2]))
    if cmd == "arm":
        return arm(sys.argv[2], sys.argv[4:], int(sys.argv[3]))
    if cmd == "report":
        return report(sys.argv[2:])
    raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
