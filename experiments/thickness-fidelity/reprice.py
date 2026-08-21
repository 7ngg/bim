"""Ticket 33 item 3 — price a second `t_int`, at ADR 0009's and ADR 0010's prices.

Item 3 is an argument, not a measurement, but three of its terms are arithmetic
and can be computed rather than asserted. All three read data files; nothing is
written outside `out/`.

  (a) **The residue-class claim survives the layer set.** ADR 0010 turns every
      `t_int` candidate into a TOTAL by adding 2 x `t_finish`. Recompute the
      pair-sharing set over the 19 sourced candidates in
      `docs/research/az-region-profile/thickness.md` §9, at structural values and
      at totals, and check the ticket's assertion that the conclusion does not
      move.

  (b) **How many published minima a second `t_int` would actually duplicate.**
      ADR 0007 binds a region profile's LINEAR minima; ADR 0009 exempts the
      ergonomic layer. So the duplication cost is the count of linear minima the
      AZ *profile* publishes, not the count in the file.

  (c) **What the solve-grid ceiling costs at each `t_int`.** ADR 0009: the
      exemption is not a licence to ignore the erosion — the solver still pays
      `ceil((m + t) / grid)`. Compute the rounding loss over the ergonomic
      layer's own 18 room types at t = 120, 150 and 280, because the only cheap
      way to run two thicknesses in one plan is to solve at the thicker one.

Run:  python experiments/thickness-fidelity/reprice.py
"""
from __future__ import annotations

import io
import json
import math
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STD = ROOT / "data" / "standards" / "room-constraints.json"

GRID = 250
T_FINISH = 15

# docs/research/az-region-profile/thickness.md section 9, table "Every sourced
# candidate t_int". Transcribed, not re-sourced -- this is `reported` from that
# findings doc, which sourced each value first-hand.
CANDIDATES = [60, 80, 90, 100, 120, 138, 140, 160, 180, 190,
              200, 220, 240, 250, 260, 270, 280, 288, 300]


def main() -> None:
    std = json.load(io.open(STD, encoding="utf-8"))
    az = std["profiles"]["AZ"]
    cat = az["construction"]["catalogue"]["brick"]

    print("=" * 72)
    print("(a) does ADR 0010's layer set move the residue-class result?")
    print("=" * 72)
    for label, offset in (("structural (pre-ADR-0010)", 0),
                          (f"total (+2 x t_finish = +{2*T_FINISH})", 2 * T_FINISH)):
        vals = [c + offset for c in CANDIDATES]
        share = [(a, b) for a, b in combinations(sorted(set(vals)), 2)
                 if (a - b) % GRID == 0]
        print(f"\n   {label}: {len(vals)} candidates")
        print(f"   pairs sharing a residue class mod {GRID}: {share}")
    t_int = cat["t_int"]["v"]
    t_bear = cat["t_int_bearing"]["v"] + 2 * T_FINISH
    print(f"\n   shipped t_int total {t_int} -> residue {(-t_int) % GRID}")
    print(f"   a second t_int from t_int_bearing {cat['t_int_bearing']['v']} "
          f"+ 2 x {T_FINISH} = {t_bear} -> residue {(-t_bear) % GRID}")
    print(f"   same class? {((-t_int) % GRID) == ((-t_bear) % GRID)}")

    print("\n" + "=" * 72)
    print("(b) how many published minima would a second t_int duplicate?")
    print("=" * 72)

    def linear_minima(node, path=""):
        found = []
        if isinstance(node, dict):
            if "v" in node and isinstance(node["v"], (int, float)):
                if "min_clear" in path or "min_width" in path or "min_dim" in path:
                    found.append((path, node["v"]))
                return found
            for k, v in node.items():
                found += linear_minima(v, f"{path}.{k}" if path else k)
        return found

    prof_lin = linear_minima(az)
    erg_lin = linear_minima(std["ergonomic"])
    print(f"\n   linear minima published by profiles.AZ ......... {len(prof_lin)}")
    for p, v in prof_lin:
        print(f"       {p} = {v}")
    print(f"   linear minima published by the ergonomic layer .. {len(erg_lin)}")
    print(f"   ADR 0009 exempts the ergonomic layer, so a second t_int costs")
    print(f"   {len(prof_lin)} duplicated row(s) today.")
    print(f"   admissible_linear_minima recorded in the profile: "
          f"{az['construction']['residue_class_mod_grid']['admissible_linear_minima']}")

    print("\n" + "=" * 72)
    print("(c) grid-ceiling cost per axis at each t_int (ADR 0009 consequence 4)")
    print("=" * 72)
    print("\n   clear_w = grid*w - t   and   w = ceil((m + t)/grid)")
    print("   loss = grid*w - t - m,  the millimetres a room grows to pay for "
          "its wall\n")
    rooms = std["ergonomic"]["rooms"]
    header = f"   {'room':<14}{'short':>7}{'long':>7}" + "".join(
        f"{'t=' + str(t):>18}" for t in (120, 150, 280))
    print(header)
    tot = {120: 0, 150: 0, 280: 0}
    for name, r in rooms.items():
        s = r.get("min_clear_short", {}).get("v")
        L = r.get("min_clear_long", {}).get("v")
        if s is None or L is None:
            continue
        cells = f"   {name:<14}{s:>7}{L:>7}"
        for t in (120, 150, 280):
            ls = GRID * math.ceil((s + t) / GRID) - t - s
            ll = GRID * math.ceil((L + t) / GRID) - t - L
            tot[t] += ls + ll
            cells += f"{ls:>8} +{ll:<8}"
        print(cells)
    print(f"\n   summed rounding loss over all {len(rooms)} room types, both axes:")
    for t in (120, 150, 280):
        print(f"      t = {t:3d}   {tot[t]:6,d} mm   "
              f"mean {tot[t]/(2*len(rooms)):.0f} mm per axis per room")
    print("\n   Rounding loss is the WRONG cost metric here and is reported only "
          "to say so:\n   `(-m-t) mod grid` is near-uniform in t, so it barely "
          "moves. What ADR 0007's\n   deletion actually turns on is the number of "
          "SOLVE CELLS a room needs.\n")

    cells_tot = {120: 0, 150: 0, 280: 0}
    gained = 0
    axes = 0
    for name, r in rooms.items():
        s = r.get("min_clear_short", {}).get("v")
        L = r.get("min_clear_long", {}).get("v")
        if s is None or L is None:
            continue
        for m in (s, L):
            axes += 1
            c = {t: math.ceil((m + t) / GRID) for t in (120, 150, 280)}
            for t in c:
                cells_tot[t] += c[t]
            if c[280] > c[150]:
                gained += 1
    print(f"   solve cells needed, summed over {axes} room-axes:")
    for t in (120, 150, 280):
        print(f"      t = {t:3d}   {cells_tot[t]:4d} cells   "
              f"= {cells_tot[t]*GRID:,d} mm of solve domain")
    print(f"\n   room-axes that need one MORE 250 mm cell at t = 280 than at "
          f"t = 150: {gained} of {axes}  ({100*gained/axes:.0f} %)")
    print(f"   extra solve domain: {(cells_tot[280]-cells_tot[150])*GRID:+,d} mm "
          f"summed, i.e. +{(cells_tot[280]-cells_tot[150])/axes*GRID:.0f} mm per "
          f"room-axis.")
    print(f"\n   That is what 'solve at the thicker value, draw the thinner one' "
          f"spends to\n   keep ADR 0001 consequence 5 intact, and it is charged "
          f"to exactly the\n   room-count band ADR 0009 already found 250 mm "
          f"charging.")


if __name__ == "__main__":
    main()
