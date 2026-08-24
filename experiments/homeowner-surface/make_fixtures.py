"""PROTOTYPE FIXTURE BUILDER — throwaway.

Runs the solver toy for a few real Briefs and dumps the *solved* layouts as
JSON for the Homeowner-surface prototype to render. The point is that the
prototype shows geometry the engine actually produced, not geometry I drew.

Run:  ../../venv/Scripts/python.exe make_fixtures.py
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "solver-toy"))

from scenarios import scenario            # noqa: E402
from solver import SolveConfig, project   # noqa: E402
from validate import check                # noqa: E402

GRID_MM = 250

# The toy's 10 kinds -> the ergonomic layer's 18 keys (brief.md section 3).
KIND_MAP = {
    "hall": "hall",
    "living": "living",
    "kitchen": "kitchen",
    "dining": "dining",
    "bathroom": "bathroom",
    "bedroom": "bedroom_double",
    "study": "study",
    "wc": "wc",
    "corridor": "corridor",
    "utility": "utility",
}


def dump(n_rooms: int, seed: int, exposure: str, label: str) -> dict | None:
    brief, truth, proposal = scenario(n_rooms, seed=seed, exposure=exposure)
    res = project(brief, proposal, SolveConfig(time_limit_s=15))
    if not res.rooms:
        print(f"  {label}: {res.status}, no rooms")
        return None
    v = check(brief, res.rooms)
    env = brief.env
    out = {
        "label": label,
        "status": res.status,
        "valid": bool(v["ok"]),
        "wall_time_s": round(res.wall_time_s, 2),
        "seed": seed,
        "exposure": exposure,
        "grid_mm": GRID_MM,
        "envelope": {
            "name": env.name,
            "W": env.W, "H": env.H,
            "exterior_sides": env.exterior_sides,
            "notches": [[r.x1, r.y1, r.x2, r.y2] for r in env.notches],
            "exposure": env.exposure,
        },
        "entry": brief.entry,
        "rooms": [
            {
                "i": i,
                "kind": KIND_MAP.get(spec.kind, spec.kind),
                "toy_kind": spec.kind,
                "x1": r.x1, "y1": r.y1, "x2": r.x2, "y2": r.y2,
            }
            for i, (spec, r) in enumerate(zip(brief.rooms, res.rooms))
        ],
    }
    print(f"  {label}: {res.status} {'VALID' if v['ok'] else 'INVALID'} "
          f"in {res.wall_time_s:.2f}s, {len(res.rooms)} rooms")
    return out


def main() -> int:
    # Four candidates for one 5-room Brief (different seeds = different
    # Proposals = different survivors), plus a 6- and an 8-room case.
    plans = []
    EXP = "corpus_median"     # Swiss Dwellings median 0.37, not a detached bungalow
    for seed in (20260817, 991, 4242, 77):
        p = dump(5, seed, EXP, f"5-room seed {seed}")
        if p:
            plans.append(p)
    # 6 rooms is UNAVAILABLE at corpus_median: make_brief finds no valid
    # room-type assignment at any of 5 seeds. See probe_exposure.py.
    for n, seed in ((7, 20260817), (8, 20260817)):
        p = dump(n, seed, EXP, f"{n}-room")
        if p:
            plans.append(p)
    with open(os.path.join(HERE, "fixtures.json"), "w", encoding="utf-8") as f:
        json.dump({"plans": plans}, f, indent=1)
    print(f"wrote {len(plans)} plans")
    return 0


if __name__ == "__main__":
    sys.exit(main())
