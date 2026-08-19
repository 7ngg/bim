"""Can the corpus supply the region profile's wall-thickness catalogue?

*Which region profiles ship in v1* needs one, and `model.thickness_in_catalogue`
is the only *hard* acceptance rule that reads the region profile. The standards
research offers only REPORTED numbers from books that were never read and cannot
lawfully be transcribed (DIN 1053 / DIN 4172 via Neufert, findings §5.6, §7.6).
Swiss Dwellings ships 1,519,546 WALL separator polygons in WKT metres under
CC BY 4.0 — so the obvious move is to measure the catalogue instead of quoting it.

This script exists to record that the move fails, and why.

Thickness = the minor side of each separator's minimum rotated rectangle,
restricted to separators that are genuinely straight strips (area within 5% of
their own bounding rectangle).

Run: python experiments/corpus-smoke/wall_thickness_swiss.py [sample_n]
"""

import sys
from collections import Counter

import pandas as pd
from shapely import wkt

GEOM = "data/corpora/swiss-dwellings/swiss-dwellings-v3.0.0/geometries.csv"
SAMPLE = int(sys.argv[1]) if len(sys.argv) > 1 else 200_000

# Catalogues to test coverage against: a minimal one, the shape a masonry
# profile takes, and a generous twelve-entry one.
CANDIDATES = [
    [100, 150, 200, 250, 300],
    [80, 100, 120, 150, 180, 200, 250, 300],
    [80, 100, 120, 140, 160, 180, 200, 240, 250, 300, 350, 400],
]


def thicknesses(geoms) -> tuple[list[int], int]:
    out, skipped = [], 0
    for g in geoms:
        try:
            p = wkt.loads(g)
        except Exception:
            skipped += 1
            continue
        if p.is_empty or p.area <= 0:
            skipped += 1
            continue
        mrr = p.minimum_rotated_rectangle
        if mrr.area <= 0 or p.area / mrr.area < 0.95:      # not a straight strip
            skipped += 1
            continue
        c = list(mrr.exterior.coords)[:4]
        a = ((c[1][0] - c[0][0]) ** 2 + (c[1][1] - c[0][1]) ** 2) ** 0.5
        b = ((c[2][0] - c[1][0]) ** 2 + (c[2][1] - c[1][1]) ** 2) ** 0.5
        out.append(round(min(a, b) * 1000))
    return out, skipped


def main() -> None:
    df = pd.read_csv(GEOM, usecols=["entity_type", "entity_subtype", "geometry"])
    walls = df[(df.entity_type == "separator") & (df.entity_subtype == "WALL")]
    print(f"WALL separators in corpus: {len(walls):,}")
    if SAMPLE and SAMPLE < len(walls):
        walls = walls.sample(SAMPLE, random_state=0)
        print(f"sampled: {len(walls):,}  (seed 0)")

    t, skipped = thicknesses(walls.geometry)
    n = len(t)
    print(f"measured: {n:,}   skipped as non-rectangular: {skipped:,}")

    s = pd.Series(t)
    print("\npercentiles (mm):  " + "  ".join(
        f"p{q}={s.quantile(q / 100):.0f}" for q in (1, 5, 25, 50, 75, 95, 99)))

    # Is there a module? If walls were designed to a 10 mm grid and surveyed with
    # noise, most measurements sit near a multiple of 10. Uniform noise gives 50%.
    near10 = sum(1 for x in t if min(x % 10, 10 - x % 10) <= 2)
    near5 = sum(1 for x in t if min(x % 5, 5 - x % 5) <= 1)
    even = sum(1 for x in t if x % 2 == 0)
    print(f"\nwithin +/-2 mm of a multiple of 10: {100 * near10 / n:.1f}%  (uniform: 50%)")
    print(f"within +/-1 mm of a multiple of  5: {100 * near5 / n:.1f}%  (uniform: 60%)")
    print(f"even millimetres:                   {100 * even / n:.1f}%  (uniform: 50%)")

    print("\nsnapped to nearest 10 mm, top 20:")
    cum = 0
    for v, c in Counter(round(x / 10) * 10 for x in t).most_common(20):
        cum += c
        print(f"  {v:4d} mm  {c:7,}  {100 * c / n:5.2f}%   cumulative {100 * cum / n:5.1f}%")

    print("\ncoverage of a candidate catalogue, +/-10 mm:")
    for cat in CANDIDATES:
        hit = sum(1 for x in t if any(abs(x - c) <= 10 for c in cat))
        print(f"  {len(cat):2d} entries  {100 * hit / n:5.1f}%   {cat}")


if __name__ == "__main__":
    main()
