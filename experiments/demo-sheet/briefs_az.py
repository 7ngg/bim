"""Baku Briefs, from published Azerbaijani room schedules.

`experiments/baku-market-areas/mida_plans_318.json` is 318 distinct plan
geometries read off MIDA's own per-apartment eksplikasiya across five populated
Baku projects. Each apartment's room areas sum to its published `internal_size`
to the cent, so the plane is NET INTERNAL -- the plane ADR 0010 measures -- and
no conversion applies.

WHY THIS AND NOT A CORPUS PROGRAMME. Every Brief the warp has ever been measured
against was a Swiss dwelling's own room list. That measures the corpus against
itself. These are what the market this product sells into actually asks for, in
its own vocabulary, at its own areas.

TWO ASSUMPTIONS, BOTH DECLARED (C4).

  1. `eyvan` IS EXCLUDED, AND IT IS INSIDE THE PUBLISHED TOTAL. Checked, not
     assumed: on record 0 the five rooms sum to 34,97 = `internal`, and one of
     them is a 3,91 m2 eyvan. v1 models no balcony, loggia, terrace or eyvan and
     the area convention excludes all four, so the Brief's target area is
     `internal - eyvan` and a Baku listing's headline is several percent more
     than the rooms a Homeowner gets. That is `area_convention.brief_semantics`
     stated in numbers rather than in prose.
  2. THE ENVELOPE ASPECT IS NOT IN THE SCHEDULE. An eksplikasiya carries areas
     and no geometry, and the retrieval gate's third term is an aspect ratio. It
     is defaulted to the MEDIAN aspect of the converted corpus dwellings sharing
     this Brief's exact room multiset -- a measured default over the population
     the donor will come from, not an invented number -- and it is surfaced as
     an Assumption a Homeowner may edit.
"""
from __future__ import annotations

import json
import pathlib
import statistics as st
from collections import Counter, defaultdict
from typing import Dict, List, Optional

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MIDA = ROOT / "experiments/baku-market-areas/mida_plans_318.json"

#: MIDA's own room words onto the corpus label set the warp speaks. One-way and
#: lossy in exactly the direction `ergonomic.corpus_label_map` already declares.
#: `Eyvan` is absent on purpose -- see the module docstring.
MIDA_TO_LABEL = {
    "Qonaq otağı": "LIVING_ROOM",
    "Mətbəx": "KITCHEN",
    "Yataq otağı": "PRIVATE",
    "Sanitar qovşağı": "BATHROOM",
    "Dəhliz": "CORRIDOR",
    "Qarderob": "STOREROOM",
    "Mətbəx-studio": "KITCHEN_DINING",
}
EXCLUDED = {"Eyvan"}


def load_mida() -> List[dict]:
    doc = json.loads(MIDA.read_text(encoding="utf-8"))
    return doc["plans"]


def brief_from_mida(rec: dict, i: int) -> Optional[dict]:
    """One published apartment -> one Brief record, in the warp's own shape.

    Returns None where a room word has no mapping, rather than defaulting it:
    a silent default here would put an unmapped room into a multiset and the
    retrieval gate would then match on a programme nobody asked for.
    """
    rooms, dropped = [], 0.0
    for r in rec["rooms"]:
        name, sq = r["n"], float(r["sq"])
        if name in EXCLUDED:
            dropped += sq
            continue
        lab = MIDA_TO_LABEL.get(name)
        if lab is None:
            return None
        rooms.append((lab, sq))
    if not rooms:
        return None
    area = round(sum(a for _, a in rooms), 4)
    return {
        "k": "mida-%03d" % i,
        "rooms": rooms,
        "n": len(rooms),
        "area": area,
        "aspect": None,                 # filled by `attach_aspect`
        "ms": tuple(sorted(Counter(t for t, _ in rooms).items())),
        "otaq": rec["nrooms"],
        "listed_internal_m2": rec["internal"],
        "eyvan_m2": round(dropped, 4),
        "external_m2": rec.get("external"),
    }


def attach_aspect(brief: dict, by_ms: Dict[tuple, list]) -> dict:
    """Assumption 2. The median aspect of the donors that share this exact room
    multiset -- so the default is drawn from the population the donor comes from
    rather than from nowhere. Falls back to 1.0 where the bucket is empty, which
    is a Brief retrieval will decline anyway."""
    pool = by_ms.get(brief["ms"], [])
    brief["aspect"] = round(st.median([p["aspect"] for p in pool]), 4) if pool else 1.0
    brief["aspect_src"] = "corpus median of %d donors sharing the multiset" % len(pool)
    return brief


def build(by_ms: Dict[tuple, list], otaq: Optional[List[int]] = None,
          limit: Optional[int] = None) -> List[dict]:
    """Every MIDA apartment that maps cleanly, as Briefs, deduplicated on
    (multiset, rounded area) so a repeated type record is one Brief."""
    out, seen = [], set()
    for i, rec in enumerate(load_mida()):
        if otaq is not None and rec["nrooms"] not in otaq:
            continue
        b = brief_from_mida(rec, i)
        if b is None:
            continue
        key = (b["ms"], round(b["area"], 1))
        if key in seen:
            continue
        seen.add(key)
        out.append(attach_aspect(b, by_ms))
        if limit and len(out) >= limit:
            break
    return out


def census(briefs: List[dict]) -> dict:
    by_otaq = Counter(b["otaq"] for b in briefs)
    return {
        "briefs": len(briefs),
        "by_otaq": dict(sorted(by_otaq.items())),
        "rooms_p50": st.median([b["n"] for b in briefs]) if briefs else None,
        "area_m2_p50": round(st.median([b["area"] for b in briefs]), 2) if briefs else None,
        "eyvan_share_p50": round(st.median(
            [b["eyvan_m2"] / b["listed_internal_m2"] for b in briefs
             if b["listed_internal_m2"]]), 4) if briefs else None,
    }
