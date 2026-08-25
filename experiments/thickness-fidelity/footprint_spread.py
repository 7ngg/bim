"""Ticket 44 - the spread of the per-dwelling partition footprint at `t_int` 150.

`docs/research/single-internal-thickness.md` S6.4 published the footprint's
**centre** - mean 5.7 %, p50 5.7 % - and nothing else. `brief.md` S9.4 bound 6
reads two ends of that distribution, `f_hi` and `f_lo`, and today has to set both
to 0.057, so a hard refusal rests on a point estimate. This script reports the
ends.

The quantity, exactly as S6.4 defines it and as the engine will price it:

    f  =  t_int * Sum(internal wall length) / Sum(Space area)

`t_int` is a constant, so every bit of f's spread is spread in a dwelling's
**internal wall length per square metre of room**. That is the right shape for
this question: the engine also draws one uniform thickness, so the only thing it
can vary is how much partition a layout needs.

Three things are reported, per the ticket:

  1. the ladder p1..p99 pooled, on the same population S6.4 used;
  2. the same ladder **per room count**, because bound 6 bites at four rooms and
     only there (`room-area-bands.md` S5.1), with a bootstrap on the tails so
     "is the split material" is answered rather than asserted;
  3. **which tail is which**, computed rather than argued - the refusal's
     one-way implication fixes the sign, and getting it wrong inverts a hard
     refusal.

Run:  python experiments/thickness-fidelity/footprint_spread.py > out/footprint_spread.txt
"""
from __future__ import annotations

import csv
import gzip
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
# COMMITTED, unlike out/. The whole reason ticket 44 exists is that S6.4's
# distribution was computed once, published as two numbers, and then cost 50
# minutes of corpus work to ask a third question of. Five columns per dwelling
# is ~200 KB gzipped and makes every future percentile free -- and reproducible
# by someone who does not hold the 1.09 GB corpus at all.
SERIES = HERE / "series" / "footprint_150.csv.gz"
FIELDS = ("k", "n_rooms", "sum_area", "len_int", "fill_area")

T_SHIPPED = 150        # AZ t_int TOTAL, ADR 0010
BAND = (4, 10)         # C13 - and the filter S6.4's own numbers were computed under
MIN_L = 3.0            # m of internal wall below which a dwelling is not judged
QS = (1, 5, 10, 25, 50, 75, 90, 95, 99)
BOOT = 2000
SEED = 44


def footprint(r, t=T_SHIPPED):
    """f as a PERCENT of Sum(Space area). Same expression as analyse.py."""
    return 100.0 * t / 1000.0 * sum(w["len_int"] for w in r["internal"]) / r["sum_area"]


def corpus_footprint(r):
    """The corpus's OWN partition footprint, percent of Sum(Space area).

    A second estimator of the same quantity, off the morphological closing
    rather than the per-wall sum. It is not what bound 6 predicts - the engine
    prices at a uniform 150, the surveyor did not - but if the two disagree on
    which tail is the fat one, the sign claim is not safe.
    """
    a = r.get("fill_area")
    if a is None or not np.isfinite(a) or a < 0:
        return None
    return 100.0 * a / r["sum_area"]


def ladder(v, qs=QS):
    return "  ".join(f"p{q}={np.percentile(v, q):.2f}" for q in qs)


def boot_pct(v, q, n=BOOT, seed=SEED):
    """95 % bootstrap interval on one percentile."""
    rng = np.random.default_rng(seed)
    v = np.asarray(v, float)
    s = np.percentile(rng.choice(v, size=(n, len(v)), replace=True), q, axis=1)
    return float(np.percentile(s, 2.5)), float(np.percentile(s, 97.5))


def write_series(every, stride):
    """Persist the five columns every footprint question needs, and nothing else."""
    SERIES.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(SERIES, "wt", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(("# stride", stride, "t_int", T_SHIPPED))
        w.writerow(FIELDS)
        for r in every:
            w.writerow((r["k"], r["n_rooms"], f"{r['sum_area']:.4f}",
                        f"{sum(x['len_int'] for x in r['internal']):.4f}",
                        "" if r.get("fill_area") is None else f"{r['fill_area']:.4f}"))
    print(f"wrote {SERIES}  ({SERIES.stat().st_size / 1e3:.0f} KB)")


def read_series():
    """The committed series, in the same record shape the rest of this file uses."""
    with gzip.open(SERIES, "rt", encoding="utf-8", newline="") as fh:
        rd = csv.reader(fh)
        head = next(rd)
        stride = int(head[1])
        next(rd)
        out = []
        for k, n, sa, li, fa in rd:
            out.append({"k": k, "n_rooms": int(n), "sum_area": float(sa),
                        "internal": [{"len_int": float(li)}],
                        "fill_area": float(fa) if fa else None})
    return {"stride": stride, "repairs": "(not carried in the series)",
            "dwellings": out}


def main() -> None:
    walls = OUT / "walls.json.gz"
    if walls.exists():
        with gzip.open(walls, "rt", encoding="utf-8") as fh:
            d = json.load(fh)
        write_series(d["dwellings"], d["stride"])
    else:
        print(f"{walls.name} absent -- reading the committed series instead. "
              f"Percentiles are identical; `repairs` is not carried.\n")
        d = read_series()
    every = d["dwellings"]

    # `analyse.py`'s own load(), reproduced rather than imported so this file
    # states the population it measures.
    ok = [r for r in every
          if sum(w["len_int"] for w in r["internal"]) >= MIN_L and r["sum_area"] > 10]
    band = [r for r in ok if BAND[0] <= r["n_rooms"] <= BAND[1]]

    print("=" * 74)
    print("POPULATION")
    print("=" * 74)
    print(f"stride                        {d['stride']}")
    print(f"dwellings measured            {len(every):,}")
    print(f"  after >= {MIN_L} m internal wall and > 10 m^2 of room:  {len(ok):,}")
    print(f"  after C13's {BAND[0]}-{BAND[1]} room band:                       "
          f"{len(band):,}   <-- the population S6.4 published on")
    print(f"repairs                       {d['repairs']}")

    f_band = np.array([footprint(r) for r in band])
    f_all = np.array([footprint(r) for r in ok])

    print()
    print("=" * 74)
    print("1 - THE LADDER, POOLED")
    print("=" * 74)
    print("\nour footprint at t_int = 150, percent of Sum(Space area)")
    for nm, v in (("in band 4-10", f_band), ("every n", f_all)):
        print(f"\n   {nm}   n={len(v):,}")
        print(f"      {ladder(v)}")
        print(f"      mean {v.mean():.2f}   sd {v.std(ddof=1):.2f}   "
              f"min {v.min():.2f}   max {v.max():.2f}")
    for q in (5, 95, 99):
        b = boot_pct(f_band, q)
        print(f"   bootstrap 95% CI, in band:   p{q} in [{b[0]:.2f}, {b[1]:.2f}]")
    print(f"\n   shape: skew {float(((f_band - f_band.mean())**3).mean() / f_band.std()**3):+.2f}"
          f"   p99/p50 {np.percentile(f_band,99)/np.percentile(f_band,50):.2f}x"
          f"   max/p50 {f_band.max()/np.percentile(f_band,50):.2f}x")

    # The SAME quantity as a share of INTERIOR rather than of Sum(Space area).
    # These are two different numbers and the document has only ever published
    # one of them, unlabelled. f/(1+f) is the conversion.
    print("\n   the same footprint, two denominators -- they are NOT the same number")
    print(f"      {'':6}{'% of Sum(Space)':>16}{'% of interior':>16}")
    for q in (5, 50, 95, 99):
        a = np.percentile(f_band, q)
        print(f"      p{q:<5}{a:>16.2f}{100*a/(100+a):>16.2f}")

    fc = np.array([x for x in (corpus_footprint(r) for r in band) if x is not None])
    print(f"\n   cross-check, the corpus's OWN partitions (closing estimator)  n={len(fc):,}")
    print(f"      {ladder(fc)}")
    print(f"      mean {fc.mean():.2f}   sd {fc.std(ddof=1):.2f}")

    print()
    print("=" * 74)
    print("2 - AGAINST ROOM COUNT")
    print("=" * 74)
    print("\nbound 6 fires at n = 4 and only there (room-area-bands.md S5.1).")
    print("Partitions scale with the number of rooms, so a pooled percentile may")
    print("be the wrong statistic for the one regime the bound bites in.\n")
    print(f"   {'n':>3}  {'dwellings':>9}  {'mean':>6}  {'p5':>6}  {'p50':>6}  "
          f"{'p95':>6}  {'p99':>6}   {'p95 boot 95% CI':>18}")
    rows = {}
    for n in range(2, 13):
        v = np.array([footprint(r) for r in ok if r["n_rooms"] == n])
        if len(v) < 30:
            print(f"   {n:>3}  {len(v):>9}   (too few to percentile)")
            continue
        rows[n] = v
        b = boot_pct(v, 95)
        print(f"   {n:>3}  {len(v):>9,}  {v.mean():>6.2f}  "
              f"{np.percentile(v, 5):>6.2f}  {np.percentile(v, 50):>6.2f}  "
              f"{np.percentile(v, 95):>6.2f}  {np.percentile(v, 99):>6.2f}   "
              f"[{b[0]:>5.2f}, {b[1]:>5.2f}]")
    v = np.array([footprint(r) for r in ok if r["n_rooms"] >= 13])
    if len(v) >= 30:
        print(f"   13+  {len(v):>9,}  {v.mean():>6.2f}  "
              f"{np.percentile(v, 5):>6.2f}  {np.percentile(v, 50):>6.2f}  "
              f"{np.percentile(v, 95):>6.2f}  {np.percentile(v, 99):>6.2f}")

    # Is the trend real, or is this noise? Rank correlation over the in-band
    # dwellings, plus the plain difference the spec would have to carry.
    nn = np.array([r["n_rooms"] for r in band], float)
    ff = f_band
    rank_n = np.argsort(np.argsort(nn))
    rank_f = np.argsort(np.argsort(ff))
    rho = float(np.corrcoef(rank_n, rank_f)[0, 1])
    print(f"\n   Spearman rho(n, f) in band 4-10:  {rho:+.3f}   n={len(nn):,}")

    if 4 in rows:
        v4 = rows[4]
        print(f"\n   the regime bound 6 fires in, n = 4:")
        print(f"      {ladder(v4)}")
        print(f"      mean {v4.mean():.2f}   n={len(v4):,}")
        for q in (5, 95):
            a = np.percentile(v4, q)
            b = np.percentile(f_band, q)
            print(f"      p{q}:  n=4 {a:.2f}   pooled 4-10 {b:.2f}   "
                  f"difference {a - b:+.2f} points")

    print()
    print("=" * 74)
    print("3 - WHICH TAIL IS WHICH")
    print("=" * 74)
    print("""
Bound 6 refuses when   Sum(upper_band) < interior / (1 + f).

`interior` is stated and fixed. Sum(Space area) = interior / (1 + f), so a
LARGER f means a SMALLER floor area to fill, which is the case a programme is
MOST likely to be able to fill -- so it is the case in which the refusal is
hardest to earn. ADR 0015's one-way implication ("every Plan from this Brief
fails", not "some might") therefore needs the refusal set at the HIGH end:

   f_hi = the UPPER tail   -> refuse only where even the thickest-partition
                              layout the corpus supports cannot rescue it
   f_lo = the LOWER tail   -> warn where a thin-partition layout still could

Worked, so the sign is checked rather than asserted:""")
    interior = 95.0        # m^2, a stated 95 m^2 flat
    for label, f in (("f_lo (p5)", np.percentile(f_band, 5)),
                     ("p50", np.percentile(f_band, 50)),
                     ("f_hi (p95)", np.percentile(f_band, 95))):
        s = interior / (1 + f / 100.0)
        print(f"   {label:<12} f = {f:5.2f}%   ->  Sum(Space) = "
              f"{s:6.2f} m^2   (refuse if Sum(upper_band) < {s:.2f})")
    print("""
   The refusal threshold FALLS as f rises, so the high f is the permissive one
   and belongs on the refusal. The warn, at the low f, has the higher threshold
   and so fires on a strict superset -- which is the nesting a warn/refuse pair
   must have, and it comes out right only with this assignment.""")

    # What the interval is worth: who stops being refused, in square metres.
    v4 = rows.get(4, f_band)
    for tag, src in (("pooled 4-10", f_band), ("n = 4 only", v4)):
        flo = np.percentile(src, 5) / 100.0
        for qhi in (95, 99):
            fhi = np.percentile(src, qhi) / 100.0
            refuse = interior / (1 + fhi)
            warn = interior / (1 + flo)
            today = interior / 1.057
            print(f"\n   {tag}, f_hi = p{qhi}   on a {interior:.0f} m^2 interior")
            print(f"      refuse below {refuse:6.2f} m^2   warn below {warn:6.2f} m^2"
                  f"   band {warn - refuse:.2f} m^2")
            print(f"      today's point estimate refuses below {today:6.2f} m^2, so "
                  f"{today - refuse:+.2f} m^2 of Brief")
            print(f"      stops being refused outright and becomes a warn or a pass.")

    # What the constant actually decides, in the one regime the bound fires in.
    # room-area-bands.md S5.1's commonest 4-room mix, at S6.1's absolute caps:
    #   bathroom 9.15 + corridor 24.84 + kitchen 20.59 + room* 31.09
    # Bound 6 refuses when Sum(upper_band) < interior/(1+f), i.e. when the STATED
    # interior exceeds Sum(upper_band) * (1+f). So f_hi sets a flat size above
    # which a four-room Brief is refused outright, and that is a product line.
    SUM_CAP_N4 = 9.15 + 24.84 + 20.59 + 31.09
    print()
    print("=" * 74)
    print("4 - WHAT THE CONSTANT DECIDES")
    print("=" * 74)
    print(f"""
room-area-bands.md S5.1's commonest four-room mix caps at Sum(upper_band) =
{SUM_CAP_N4:.2f} m^2 (S6.1 absolute caps, no stated target). Bound 6 refuses a
four-room Brief whose stated interior exceeds Sum(upper_band) * (1 + f_hi):
""")
    src4 = rows.get(4, f_band)
    cands = [("today, the point estimate", 5.7),
             ("p95, pooled 4-10", float(np.percentile(f_band, 95))),
             ("p99, pooled 4-10", float(np.percentile(f_band, 99))),
             ("p95, n = 4", float(np.percentile(src4, 95))),
             ("p99, n = 4", float(np.percentile(src4, 99))),
             ("max, n = 4", float(src4.max()))]
    print(f"   {'f_hi from':<26}{'f_hi':>7}   refused above")
    for nm, f in cands:
        print(f"   {nm:<26}{f:>6.2f}%   {SUM_CAP_N4 * (1 + f/100):6.2f} m^2")
    print(f"""
   A 95 m^2 four-otaq flat is the worked example in brief.md S5 and an ordinary
   Baku flat. Whether it is refused is decided by this constant alone.""")

    print()
    print("=" * 74)
    print("5 - RUNG 1 IS A DIFFERENT STATISTIC")
    print("=" * 74)
    p50 = np.percentile(f_band, 50)
    p95 = np.percentile(f_band, 95)
    print(f"""
brief.md S5 rung 1 derives  interior = target_area * (1 + f)  from a stated
total. That is a POINT PREDICTION of geometry, not a one-way refusal, so it
wants the CENTRE -- p50 -- and not a tail. Same constant, two jobs, two
statistics. What a tail would cost there, on a stated 95 m^2:

   at p50  {p50:5.2f}%  ->  interior {95*(1+p50/100):6.2f} m^2
   at p95  {p95:5.2f}%  ->  interior {95*(1+p95/100):6.2f} m^2   """
          f"({95*(p95-p50)/100:+.2f} m^2, a box drawn too big)")


if __name__ == "__main__":
    main()
