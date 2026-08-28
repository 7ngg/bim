"""Fit the toy Envelope to the corpus, per room count.

`envelope_for` scales one interior area linearly in `n` at a fixed aspect and a
fixed notch share, so its perimeter grows as the *root* of its area while a real
dwelling stays articulated. Measured over the 2,238 dwellings of
`experiments/envelope-exposure/series/dwelling_sides.json.gz`, the shipped
fixture is 15 % smaller per room than the corpus median and 3-12 % less
articulated, and the articulation gap widens with `n`.

Two facts decide the shape of the fix, and both are measured here:

1. **A corner notch adds no perimeter at all.** `l_shape` cuts one and
   `u_shape` cuts two, so every Envelope this harness has ever produced has a
   boundary of exactly `2 * (W + H)` — its bounding box's. No notch share, no
   aspect and no notch *count* can change that. Real dwellings run 6-12 % longer
   than their own bounding box, rising with `n`.
2. **A mid-edge notch adds exactly `2 * depth`, at zero extra area cost.** That
   is ADR 0003's **U**, the one member of its rect/L/U/T family the generator
   never emitted. `geometry.u_shape_true` cuts it.

So the two-notch budget ADR 0003 caps at is split **by job**: a corner notch
removes floor and buys no perimeter, a mid-edge notch buys perimeter and removes
little floor. Fitting both against (area, perimeter) hits the corpus on the two
quantities that matter and lets the bbox fill fall where it falls.

Run:  ../../venv/Scripts/python.exe envelope_fit.py
"""

from __future__ import annotations

import gzip
import json
import math
import os
import sys
from typing import Dict, List, Optional, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
SERIES = os.path.join(HERE, "..", "envelope-exposure", "series",
                      "dwelling_sides.json.gz")

from geometry import Envelope, Rect  # noqa: E402

GRID_M = 0.25
# `ground_truth` insists **every** part of the Envelope receives at least one
# room, so a part narrower than the widest habitable minimum -- `living` at
# 2.75 m, 11 grid units -- makes the whole fixture unbuildable rather than merely
# awkward. The first fit centred the mid-edge notch and left 1.5 m side columns:
# geometrically perfect, 0/5 Briefs at four and nine rooms, at every preset.
MIN_COL = 11         # 2.75 m: `living`'s minimum, the binding habitable side
MIN_TOOTH_M2 = 9.0   # and no part below `bedroom`'s floor area
RECESS_FRAC = 0.28   # the mid-edge notch's width, as a share of the bbox


def _q(v: List[float], p: float) -> float:
    v = sorted(v)
    i = (len(v) - 1) * p
    lo = int(i)
    hi = min(lo + 1, len(v) - 1)
    return v[lo] * (1 - (i - lo)) + v[hi] * (i - lo)


def corpus_targets(min_n: int = 25) -> Dict[int, dict]:
    """Per-room-count medians: area, perimeter, bbox aspect, bbox deficit.

    Counts with fewer than `min_n` dwellings are dropped rather than quoted. The
    n = 12 cell holds **17** dwellings and its boundary runs 34.6 % longer than
    its own bounding box against 11.8 % at n = 11 — it is the noise cell, and
    *The toy Envelope is more compact than a real dwelling* led its headline
    table with it.
    """
    with gzip.open(SERIES, "rt", encoding="utf-8") as fh:
        rows = json.load(fh)
    out: Dict[int, dict] = {}
    for n in range(3, 16):
        g = [r for r in rows if r["n_rooms"] == n]
        if len(g) < min_n:
            continue
        out[n] = {
            "N": len(g),
            "area": _q([r["area"] for r in g], .5),
            "perim": _q([r["perimeter"] for r in g], .5),
            "aspect": _q([max(r["bbox"]) / min(r["bbox"]) for r in g], .5),
            "deficit": _q([1 - r["area"] / (r["bbox"][0] * r["bbox"][1])
                           for r in g], .5),
        }
    return out


def build(W: int, H: int, cw: int, ch: int, mw: int, md: int,
          n_rooms: Optional[int] = None) -> Optional[Tuple[Tuple[Rect, ...], Tuple[Rect, ...]]]:
    """Bbox minus a top-right corner notch and a mid-edge notch on the S edge.

    Parts are full-height columns wherever possible rather than the minimal
    dissection, because `ground_truth` insists every part receives at least one
    room and then dissects it — a two-cell tooth is a part that cannot hold one.
    """
    notches: List[Rect] = []
    if cw > 0 and ch > 0:
        notches.append(Rect(W - cw, H - ch, W, H))
    right = W - cw if (cw > 0 and ch > 0) else W

    parts: List[Rect] = []
    if mw > 0 and md > 0:
        off = (right - mw) // 2
        if off < MIN_COL or right - (off + mw) < MIN_COL:
            return None
        notches.append(Rect(off, 0, off + mw, md))
        parts += [Rect(0, 0, off, H),
                  Rect(off, md, off + mw, H),
                  Rect(off + mw, 0, right, H)]
    else:
        parts.append(Rect(0, 0, right, H))
    if cw > 0 and ch > 0:
        if cw < MIN_COL or H - ch < MIN_COL:
            return None
        parts.append(Rect(right, 0, W, H - ch))

    if any(p.w <= 0 or p.h <= 0 for p in parts):
        return None
    if any(min(p.w, p.h) < MIN_COL for p in parts):
        return None
    if any(p.area * GRID_M ** 2 < MIN_TOOTH_M2 for p in parts):
        return None
    # One room per part is not a dissection, it is an assignment, and
    # `area_targets` cannot then honour any target. Leave the generator slack.
    if n_rooms is not None and len(parts) > n_rooms - 1:
        return None
    covered = sum(p.area for p in parts)
    if covered != W * H - sum(n.area for n in notches):
        return None
    return tuple(notches), tuple(parts)


def fit_one(target: dict, n_rooms: int) -> Optional[Tuple[int, int, int, int, int, int]]:
    """(W, H, cw, ch, mw, md) in grid units, closest to one count's targets.

    A small search rather than a closed form: the grid snap, the tooth-width
    floor and the requirement that every part can hold a room all bind, and a
    solved-then-rounded answer lands outside them often enough to matter.
    """
    A, P, a = target["area"], target["perim"], target["aspect"]
    best = None
    # md is what buys perimeter: bbox perimeter is P - 2*md by construction.
    for md in range(0, 25):
        s = (P - 2 * md * GRID_M) / 2.0          # W + H in metres
        if s <= 0:
            continue
        H0 = s / (1 + a)
        for dH in (-2, -1, 0, 1, 2):
            Hg = int(round(H0 / GRID_M)) + dH
            Wg = int(round(s / GRID_M)) - Hg
            if Hg < MIN_COL * 2 or Wg < MIN_COL * 3:
                continue
            need = Wg * Hg - A / GRID_M ** 2      # total notch cells wanted
            if need < 0:
                continue
            for mw in sorted({int(round(Wg * f)) for f in
                              (0.14, 0.18, 0.22, 0.26, RECESS_FRAC, 0.32)}):
              mid = mw * md
              rest = need - mid
              for ch in range(0, Hg - MIN_COL):
                if ch == 0:
                    cw = 0
                    if abs(rest) > 0.5 * Wg:
                        continue
                else:
                    cw = int(round(rest / ch))
                    if cw < MIN_COL or cw > Wg - MIN_COL * 2:
                        continue
                got = build(Wg, Hg, cw, ch, mw, md, n_rooms)
                if got is None:
                    continue
                notches, _ = got
                Ag = (Wg * Hg - sum(n.area for n in notches)) * GRID_M ** 2
                env = Envelope("fit", Wg, Hg, *got, "detached")
                Pg = sum(hi - lo for (_, _, lo, hi, _) in env.all_faces()) * GRID_M
                dg = sum(n.area for n in notches) / (Wg * Hg)
                # Three targets, not two. Area and perimeter alone are hit by a
                # single enormous corner notch -- 31-35 % of the bbox against a
                # corpus 19-21 % -- because a corner notch costs no perimeter, so
                # the fitter buys the whole boundary from the bbox and carves the
                # area back out. That shape is two thin arms, not a dwelling.
                # Pinning the bbox deficit too is what forces the perimeter onto
                # the mid-edge notch, where real articulation actually lives.
                err = max(abs(Ag / A - 1), abs(Pg / P - 1),
                          abs(dg - target["deficit"]) / target["deficit"])
                if best is None or err < best[0]:
                    best = (err, (Wg, Hg, cw, ch, mw, md))
    return best[1] if best else None


def fit_all() -> Dict[int, Tuple[int, int, int, int, int, int]]:
    return {n: f for n, t in corpus_targets().items()
            if (f := fit_one(t, n)) is not None}


if __name__ == "__main__":
    tg = corpus_targets()
    fits = fit_all()
    print("corpus target vs fitted Envelope, per room count "
          "(grid units, 250 mm)\n")
    hdr = (f"{'n':>3} {'N':>4} | {'A*':>6} {'P*':>6} {'A*/n':>6} {'def*':>6} |"
           f" {'W':>3} {'H':>3} {'cw':>3} {'ch':>3} {'mw':>3} {'md':>3} |"
           f" {'A':>6} {'P':>6} {'A/n':>6} {'notch':>6} |"
           f" {'dA':>6} {'dP':>6} {'ddef':>6}")
    print(hdr)
    print("-" * len(hdr))
    for n in sorted(fits):
        W, H, cw, ch, mw, md = fits[n]
        env = Envelope("fit", W, H, *build(W, H, cw, ch, mw, md, n), "detached")
        A = env.interior_area * GRID_M ** 2
        P = sum(hi - lo for (_, _, lo, hi, _) in env.all_faces()) * GRID_M
        t = tg[n]
        dg = sum(x.area for x in env.notches) / (W * H)
        print(f"{n:>3} {t['N']:>4} | {t['area']:6.1f} {t['perim']:6.1f} "
              f"{t['area']/n:6.2f} {100*t['deficit']:5.1f}% | "
              f"{W:>3} {H:>3} {cw:>3} {ch:>3} {mw:>3} {md:>3} | "
              f"{A:6.1f} {P:6.1f} {A/n:6.2f} {100*dg:5.1f}% | "
              f"{100*(A/t['area']-1):+5.1f}% {100*(P/t['perim']-1):+5.1f}% "
              f"{100*(dg/t['deficit']-1):+5.1f}%")
    print("\nCORPUS_ENVELOPES = " + json.dumps(
        {str(k): list(v) for k, v in sorted(fits.items())}))
