"""How much of the real corpus is non-guillotine — re-measured on the shipped
conversion.

Ticket 29's motivating table (6.27 % overall, ~15 % at 8-10 rooms) was measured
by `experiments/rectangularise/guillotine_share.py` against `swiss_fit.json`:
the **k = 1** conversion, one rectangle per Room. ADR 0016 has since superseded
that — a Room is one or two rectangles, and the shipped conversion writes
`swiss_fit_k2.json` whose records carry `parts` and no `rects`. More rectangles
per dwelling can only make a tiling harder to cut apart, so the figure the ticket
rests on is not merely stale, it is stale in a *known direction*.

This re-measures it, and measures both arms where both files exist so the move is
paired on the dwelling rather than inferred.

    python corpus_guillotine.py                       # whatever is in out/
    python corpus_guillotine.py swiss_fit_k2.json

**This file lives here, not in `experiments/rectangularise/`, deliberately.** That
directory is another ticket's to write; this reads its (gitignored) output and
writes only into `solver-toy/results/`. Same reason `experiments/envelope-exposure/`
imports `solver-toy` and never edits it.

The guillotine predicate is `pinwheel.is_guillotine`, the same one the sweep's
treatment arm is verified against, so the corpus and the fixtures are judged by
one definition. It admits cuts through an Envelope notch, because a notch is not
a room — which **overstates** the guillotine share and therefore understates the
untested class.
"""

from __future__ import annotations

import json
import pathlib
import sys
from collections import Counter
from typing import Dict, List, Optional, Tuple

from geometry import Rect
from pinwheel import guillotine_residue, is_guillotine

FIT_OUT = pathlib.Path(__file__).resolve().parents[1] / "rectangularise" / "out"
RESULTS = pathlib.Path(__file__).parent / "results"


def rects_of(rec: dict) -> Optional[List[Rect]]:
    """Every rectangle in a converted dwelling, k = 1 or k = 2.

    `parts` is per-Room and each Room holds one or two rectangles; `rects` is the
    k = 1 shorthand the old file wrote. The guillotine question is about the
    rectangle set the solver tiles, not the Room set, so parts are flattened.
    """
    if "parts" in rec:
        flat = [tuple(r) for g in rec["parts"] for r in g]
    elif "rects" in rec:
        flat = [tuple(r) for r in rec["rects"]]
    else:
        return None
    if not flat:
        return None
    return [Rect(int(a), int(b), int(c), int(d)) for a, b, c, d in flat]


def measure(path: pathlib.Path) -> Tuple[Dict[int, Counter], Dict[str, dict]]:
    """Per-room-count table, plus a per-dwelling map for the paired comparison.

    **The key is the record's position in the file, and nothing else will do.**
    A fit record carries no dwelling identity — no `apartment_id`, no key — and
    `fit_rects.py` writes one record per dwelling in a deterministic order, so
    position *is* identity across two runs at the same N. Indexing by position
    among the *convertible* records instead silently pairs different dwellings,
    because the two arms convert different subsets; the first cut of this file
    did exactly that.
    """
    recs = json.load(open(path))
    by_n: Dict[int, Counter] = {}
    per_key: Dict[str, dict] = {}
    for i, rec in enumerate(recs):
        rs = rects_of(rec)
        if rs is None:
            continue
        n = rec.get("n") or len(rec.get("parts", rec.get("rects", [])))
        g = is_guillotine(rs)
        by_n.setdefault(n, Counter())
        by_n[n]["tot"] += 1
        by_n[n]["g"] += g
        by_n[n]["rects"] += len(rs)
        by_n[n]["res"] += guillotine_residue(rs)
        per_key[str(i)] = {"n": n, "guillotine": g, "rects": len(rs)}
    return by_n, per_key


def _mcnemar(a: int, b: int) -> float:
    """Exact two-sided binomial tail at p = 0.5 over the discordant pairs."""
    from math import comb
    n = a + b
    if n == 0:
        return 1.0
    k = min(a, b)
    return min(1.0, 2.0 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)


def table(name: str, by_n: Dict[int, Counter]) -> List[str]:
    out = [f"\n{name}"]
    tot = sum(c["tot"] for c in by_n.values())
    gee = sum(c["g"] for c in by_n.values())
    if not tot:
        return out + ["  (no records)"]
    out.append(f"  {tot} dwellings, guillotine {gee} ({gee / tot:.4f}), "
               f"NOT guillotine {tot - gee} ({1 - gee / tot:.4f})")
    out.append(f"  {'rooms':>6} {'dwellings':>10} {'guillotine':>11} "
               f"{'rects/dw':>9} {'mean residue':>13}")
    for k in sorted(by_n):
        c = by_n[k]
        out.append(f"  {k:>6} {c['tot']:>10} {c['g'] / c['tot']:>11.4f} "
                   f"{c['rects'] / c['tot']:>9.2f} {c['res'] / c['tot']:>13.2f}")
    return out


def main() -> None:
    names = sys.argv[1:] or ["swiss_fit_k2.json", "swiss_fit_k1.json",
                             "swiss_fit.json", "resplan_fit_k2.json"]
    lines: List[str] = ["Non-guillotine share of the real corpus, by conversion.",
                        "A tiling is guillotine when some sequence of full-width",
                        "cuts takes it apart. Cuts may pass through an Envelope",
                        "notch, so these OVERSTATE the guillotine share."]
    seen: Dict[str, Dict[str, dict]] = {}
    for nm in names:
        p = FIT_OUT / nm
        if not p.exists():
            lines.append(f"\n{nm}: not present — run "
                         f"`python experiments/rectangularise/fit_rects.py "
                         f"2600 {'--k2 ' if 'k2' in nm else ''}--out={nm}`")
            continue
        by_n, per_key = measure(p)
        seen[nm] = per_key
        lines += table(f"{nm}", by_n)

    # Paired move, where both arms exist on the same dwellings.
    k1 = next((v for k, v in seen.items() if "k1" in k or k == "swiss_fit.json"),
              None)
    k2 = seen.get("swiss_fit_k2.json")
    if k1 and k2:
        common = sorted(set(k1) & set(k2))
        lines.append(f"\nPaired on {len(common)} dwellings converted by BOTH arms "
                     f"(keyed on file position, see `measure`):")
        lines.append(f"  {'rooms':>6} {'n':>6} {'guillotine k1':>14} "
                     f"{'guillotine k2':>14} {'G->non-G':>10} {'non-G->G':>10} "
                     f"{'rects/dw k1':>12} {'rects/dw k2':>12}")
        by: Dict[int, Counter] = {}
        for key in common:
            n = k2[key]["n"]
            g1, g2 = k1[key]["guillotine"], k2[key]["guillotine"]
            by.setdefault(n, Counter())
            by[n]["tot"] += 1
            by[n]["g1"] += g1
            by[n]["g2"] += g2
            by[n]["flip"] += g1 and not g2
            by[n]["back"] += g2 and not g1
            by[n]["r1"] += k1[key]["rects"]
            by[n]["r2"] += k2[key]["rects"]
        for n in sorted(by):
            c = by[n]
            lines.append(f"  {n:>6} {c['tot']:>6} {c['g1'] / c['tot']:>14.4f} "
                         f"{c['g2'] / c['tot']:>14.4f} {c['flip']:>10} "
                         f"{c['back']:>10} {c['r1'] / c['tot']:>12.2f} "
                         f"{c['r2'] / c['tot']:>12.2f}")
        t = sum(c["tot"] for c in by.values())
        S = lambda k: sum(c[k] for c in by.values())          # noqa: E731
        lines.append(f"  {'all':>6} {t:>6} {S('g1') / t:>14.4f} "
                     f"{S('g2') / t:>14.4f} {S('flip'):>10} {S('back'):>10} "
                     f"{S('r1') / t:>12.2f} {S('r2') / t:>12.2f}")
        lines.append(f"\n  non-guillotine share {1 - S('g1') / t:.4f} -> "
                     f"{1 - S('g2') / t:.4f}   "
                     f"({S('flip')} moved to non-guillotine, {S('back')} back)")
        lines.append(f"  exact McNemar p = {_mcnemar(S('flip'), S('back')):.3g}")

    text = "\n".join(lines)
    print(text)
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "corpus_guillotine.txt").write_text(text + "\n", encoding="utf-8")
    print(f"\n-> {RESULTS / 'corpus_guillotine.txt'}")


if __name__ == "__main__":
    main()
