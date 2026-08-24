"""Are `l_truth.py`'s L-shaped truths actually L-shaped?

Every number in `sweep_designA.py` rests on this. A "merged pair" that happens to
stack into a bigger rectangle would be a k = 1 Room wearing two boxes, and the
sweep would be measuring nothing. Likewise a pair that shares only a corner is
two rooms, not an L.

Asserts, per generated scenario:
  * the merged Room's two parts are edge-adjacent over at least the leg join;
  * their union is NOT a rectangle -- so the Room genuinely needs two;
  * every part meets the leg floor on both axes;
  * the whole set of parts still tiles the Envelope interior exactly, with no
    overlap -- the merge must not have broken the ground truth it came from;
  * the Brief's Room count is n, not n + j.

Run: python experiments/room-rectangles/l_truth_check.py [scenarios]
"""
from __future__ import annotations

import sys
from pathlib import Path

TOY = Path(__file__).resolve().parents[1] / "solver-toy"
sys.path.insert(0, str(TOY))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import scenarios  # noqa: E402
from geometry import tiling_defects  # noqa: E402
from scenarios import envelope_for, mm  # noqa: E402
from l_truth import l_scenario  # noqa: E402

scenarios.ASSIGN_WORKERS = 4
LEG_MIN = LEG_JOIN = 4
T_INT = 150


def main() -> None:
    want = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    seen = ok = 0
    for n in (7, 8, 10):
        for j in (1, 2):
            for s in range(3):
                if seen >= want:
                    break
                env = envelope_for(n + j, "corpus_median")
                got = l_scenario(env, n, j, 20260817 + s, mm(1.0),
                                 scenarios.WINDOW_MIN, T_INT, LEG_JOIN,
                                 LEG_MIN, mm(0.5))
                seen += 1
                if got is None:
                    print(f"  n={n} j={j} s={s}: no scenario")
                    continue
                brief, parts, pp, _flat = got

                assert len(brief.rooms) == n, f"{len(brief.rooms)} Rooms, wanted {n}"
                ls = [r for r, ps in parts.items() if len(ps) > 1]
                assert len(ls) == j, f"{len(ls)} Ls, wanted {j}"

                for r in ls:
                    a, b = parts[r]
                    join = a.shared_edge_length(b)
                    assert join >= LEG_JOIN, f"legs share {join} < {LEG_JOIN}"
                    bw = max(a.x2, b.x2) - min(a.x1, b.x1)
                    bh = max(a.y2, b.y2) - min(a.y1, b.y1)
                    assert a.area + b.area != bw * bh, \
                        "union is a rectangle -- not an L at all"
                    for q in (a, b):
                        assert min(q.w, q.h) >= LEG_MIN, \
                            f"part {q.w}x{q.h} under the leg floor"

                flat = [q for ps in parts.values() for q in ps]
                d = tiling_defects(flat, env)
                assert d["pairwise_overlap_area"] == 0, "the merge broke H2"
                assert d["uncovered_cells"] == 0, "the merge broke H3"
                assert d["cells_outside_envelope"] == 0, "the merge broke H1"

                ok += 1
                shapes = "; ".join(
                    f"{brief.rooms[r].kind} {parts[r][0].w}x{parts[r][0].h}"
                    f"+{parts[r][1].w}x{parts[r][1].h}" for r in ls)
                print(f"  n={n} j={j} s={s}: OK  [{shapes}]")

    print(f"\nl_truth_check: {ok} of {seen} scenarios generated and all "
          f"assertions hold")
    assert ok, "no scenario generated at all -- the sweep would be empty"


if __name__ == "__main__":
    main()
