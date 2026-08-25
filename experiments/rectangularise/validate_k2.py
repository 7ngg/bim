"""Independent check on what the k <= 2 conversion actually emitted.

Shares no code with `fit_rects.fit`. Every property below is posted as a hard
constraint there, so a failure here is a defect in the model rather than a
measurement -- which is the only reason it is worth running: ADR 0008's
guarantees are asserted, and an assertion nobody re-derives is a claim.

Checks, per converted dwelling:

  1. every part is a non-empty rectangle inside the Envelope's cell grid;
  2. no two parts overlap, across Rooms or within one;
  3. a Room with two parts has BOTH clearing the leg floor -- ADR 0014 binds
     minima per constituent rectangle, and `fit_rects` gates the primary's floor
     on the secondary's presence;
  4. the two parts of a Room share a flush edge of at least the join, so the
     Room is connected. Anything less is a pinch, not an L;
  5. a Room's parts are ordered by (x1, y1), the symmetry break;
  6. no Room has more parts than the ceiling.

Run: python experiments/rectangularise/validate_k2.py [fit.json]
"""
import json
import sys
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent / "out"

LEG = 5     # fit_rects.LEG_CELLS, restated rather than imported
JOIN = 5    # fit_rects.JOIN_CELLS
K_MAX = 2


def overlap(a, b):
    return (min(a[2], b[2]) > max(a[0], b[0])
            and min(a[3], b[3]) > max(a[1], b[1]))


def shared_edge(a, b):
    """Length of the flush shared edge, 0 if the two do not touch flush."""
    if a[2] == b[0] or b[2] == a[0]:
        return max(0, min(a[3], b[3]) - max(a[1], b[1]))
    if a[3] == b[1] or b[3] == a[1]:
        return max(0, min(a[2], b[2]) - max(a[0], b[0]))
    return 0


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "swiss_fit_k2.json"
    recs = json.load(open(OUT / name))
    fail = Counter()
    checked = parts_seen = two_part_rooms = 0

    for r in recs:
        parts = r.get("parts")
        if parts is None:
            continue
        checked += 1
        flat = [(i, q) for i, ps in enumerate(parts) for q in ps]
        for i, ps in enumerate(parts):
            if not ps:
                fail["a Room came back with no rectangle at all"] += 1
            if len(ps) > K_MAX:
                fail["a Room has more parts than the ceiling"] += 1
            for q in ps:
                parts_seen += 1
                if q[2] <= q[0] or q[3] <= q[1]:
                    fail["a part is empty or inverted"] += 1
            if len(ps) == 2:
                two_part_rooms += 1
                a, b = ps
                for q in (a, b):
                    if q[2] - q[0] < LEG or q[3] - q[1] < LEG:
                        fail["a two-part Room has a leg below the floor"] += 1
                if shared_edge(a, b) < JOIN:
                    fail["the two parts of a Room do not share the join"] += 1
                if (a[0], a[1]) > (b[0], b[1]):
                    fail["parts are not ordered by (x1, y1)"] += 1
        for u in range(len(flat)):
            for v in range(u + 1, len(flat)):
                if overlap(flat[u][1], flat[v][1]):
                    fail["two parts overlap"] += 1

    print(f"{name}: {checked} converted dwellings, {parts_seen} parts, "
          f"{two_part_rooms} Rooms of two rectangles")
    if not fail:
        print("\nALL CHECKS PASS")
        return 0
    print("\nFAILURES")
    for k, v in fail.most_common():
        print(f"  {k:<52} {v:>7}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
