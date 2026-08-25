"""Ticket 29 — tables for the non-guillotine sweep.

    python report_ng.py            # every table
    python report_ng.py A T        # just those suites

Reads `results/N9*.jsonl`, writes `results/report_N9.txt` and prints it.

Every table is **paired**: the guillotine arm beside the pinwheel arm on the
same Envelope, room count, seed and config. A cell that says `-` had no row; a
cell that says `no-pin` means the Envelope admits no non-guillotine tiling at
all, which is a fact about the Envelope rather than a solver result.
"""

from __future__ import annotations

import json
import pathlib
import sys
from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Sequence

RESULTS = pathlib.Path(__file__).parent / "results"
OUT = RESULTS / "report_N9.txt"

# The console here is cp1252 and the file is UTF-8; without this a single
# non-ASCII character in a header aborts the whole report after printing half.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:                                      # noqa: BLE001
    pass

LINES: List[str] = []


def say(s: str = "") -> None:
    LINES.append(s)
    print(s)


def load(suite: str) -> List[dict]:
    p = RESULTS / f"N9{suite}.jsonl"
    if not p.exists():
        return []
    rows = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                rows.append(json.loads(line))
            except Exception:                      # noqa: BLE001
                pass
    return rows


# ---------------------------------------------------------------------------
# Summary statistics. A run is a SURVIVOR when the independent validator accepts
# the Plan -- `valid`, not `status`. `valid_at` is wall-clock to the first Plan
# with zero coverage slack, the same quantity Part II.3 reports.
# ---------------------------------------------------------------------------


def pct(num: int, den: int) -> str:
    return "-" if not den else f"{100.0 * num / den:5.1f}%"


def p(xs: Sequence[float], q: float) -> Optional[float]:
    if not xs:
        return None
    s = sorted(xs)
    i = min(len(s) - 1, max(0, int(round(q * (len(s) - 1)))))
    return s[i]


def summarise(rows: Iterable[dict]) -> dict:
    rows = list(rows)
    solved = [r for r in rows if r.get("status") not in
              (None, "NO_BRIEF", "NO_PINWHEEL", "HARNESS_ERROR")]
    nobrief = sum(1 for r in rows if r.get("status") == "NO_BRIEF")
    nopin = sum(1 for r in rows if r.get("status") == "NO_PINWHEEL")
    valid = [r for r in solved if r.get("valid")]
    infeas = sum(1 for r in solved if r.get("status") == "INFEASIBLE")
    va = [r["valid_at"] for r in valid if r.get("valid_at") is not None]
    first = [r["first"] for r in solved if r.get("first") is not None]
    res = [r["structure"]["residue"] for r in solved
           if r.get("structure") and r["structure"].get("residue")]
    adj = [r["structure"]["adj_door_density"] for r in solved
           if r.get("structure")]
    sep = [r["structure"]["unambiguous_sep"] for r in solved
           if r.get("structure")]
    fixed = [r["fixed_relations"] for r in solved
             if r.get("fixed_relations") is not None]
    cand = [r["candidate_relations"] for r in solved
            if r.get("candidate_relations") is not None]
    bad_witness = sum(1 for r in solved if r.get("structure")
                      and r["structure"].get("truth_valid") is False)
    return {
        "rows": len(rows), "solved": len(solved), "nobrief": nobrief,
        "nopin": nopin, "valid": len(valid), "infeasible": infeas,
        "valid_rate": (len(valid) / len(solved)) if solved else None,
        "va_p50": p(va, 0.50), "va_p90": p(va, 0.90), "va_max": max(va) if va else None,
        "first_p50": p(first, 0.50),
        "residue": (sum(res) / len(res)) if res else None,
        "adj": (sum(adj) / len(adj)) if adj else None,
        "sep": (sum(sep) / len(sep)) if sep else None,
        "fixed": (sum(fixed) / len(fixed)) if fixed else None,
        "cand": (sum(cand) / len(cand)) if cand else None,
        "bad_witness": bad_witness,
    }


def fmt(s: dict, key: str, nd: int = 2) -> str:
    v = s.get(key)
    if v is None:
        return f"{'-':>7}"
    return f"{v:>7.{nd}f}"


def paired_table(rows: List[dict], group_keys: Sequence[str],
                 title: str, note: str = "") -> None:
    """One line per group value, guillotine beside pinwheel."""
    say()
    say(title)
    if note:
        say(note)
    buckets: Dict[tuple, Dict[str, List[dict]]] = defaultdict(
        lambda: defaultdict(list))
    for r in rows:
        buckets[tuple(r.get(k) for k in group_keys)][r["truth"]].append(r)

    head = " ".join(f"{k:>14}" for k in group_keys)
    say(f"{head} | {'n':>4} {'valid':>6} {'p50':>7} {'p90':>7} {'inf':>4} "
        f"{'res':>5} {'adj':>5} | {'n':>4} {'valid':>6} {'p50':>7} {'p90':>7} "
        f"{'inf':>4} {'res':>5} {'adj':>5} | {'d-p50':>7}")
    say(f"{' ' * len(head)} | {'--- guillotine baseline ---':^46} | "
        f"{'---- pinwheel treatment ----':^46} |")
    for key in sorted(buckets, key=lambda k: tuple(
            (x is None, x) for x in k)):
        g = summarise(buckets[key]["guillotine"])
        w = summarise(buckets[key]["pinwheel"])
        lab = " ".join(f"{str(k):>14}" for k in key)
        if w["rows"] and w["nopin"] == w["rows"]:
            say(f"{lab} | {g['solved']:>4} {pct(g['valid'], g['solved']):>6} "
                f"{fmt(g,'va_p50')} {fmt(g,'va_p90')} {g['infeasible']:>4} "
                f"{fmt(g,'residue',1)} {fmt(g,'adj',3)} | "
                f"{'no non-guillotine tiling exists':^46} |")
            continue
        d = ("-" if g["va_p50"] is None or w["va_p50"] is None
             else f"{w['va_p50'] - g['va_p50']:+.2f}")
        say(f"{lab} | {g['solved']:>4} {pct(g['valid'], g['solved']):>6} "
            f"{fmt(g,'va_p50')} {fmt(g,'va_p90')} {g['infeasible']:>4} "
            f"{fmt(g,'residue',1)} {fmt(g,'adj',3)} | "
            f"{w['solved']:>4} {pct(w['valid'], w['solved']):>6} "
            f"{fmt(w,'va_p50')} {fmt(w,'va_p90')} {w['infeasible']:>4} "
            f"{fmt(w,'residue',1)} {fmt(w,'adj',3)} | {d:>7}")


def pooled(rows: List[dict], title: str) -> None:
    say()
    say(title)
    say(f"{'arm':>12} {'solves':>7} {'valid':>7} {'INFEAS':>7} {'no-brief':>9} "
        f"{'p50':>7} {'p90':>7} {'max':>7} {'first p50':>10} "
        f"{'fixed/cand':>12} {'sep':>6}")
    for arm in ("guillotine", "pinwheel"):
        s = summarise([r for r in rows if r.get("truth") == arm])
        fc = ("-" if s["fixed"] is None
              else f"{s['fixed']:.0f}/{s['cand']:.0f}")
        say(f"{arm:>12} {s['solved']:>7} {pct(s['valid'], s['solved']):>7} "
            f"{s['infeasible']:>7} {s['nobrief'] + s['nopin']:>9} "
            f"{fmt(s,'va_p50')} {fmt(s,'va_p90')} {fmt(s,'va_max')} "
            f"{fmt(s,'first_p50')} {fc:>12} {fmt(s,'sep',3)}")
        if s["bad_witness"]:
            say(f"{'':>12} !! {s['bad_witness']} rows whose ground truth failed "
                f"the validator -- the witness guarantee broke, treat as void")


def _binom_two_sided(k: int, n: int) -> float:
    """Exact two-sided binomial tail at p = 0.5 — McNemar without scipy."""
    if n == 0:
        return 1.0
    from math import comb
    k = min(k, n - k)
    return min(1.0, 2.0 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)


def paired_flip(rows: List[dict], axis: str, lo, hi, title: str) -> None:
    """McNemar over scenarios present at both values of `axis`.

    The unpaired rate hides the thing that matters: whether the *same* Brief,
    Envelope, seed and Proposal stops producing a survivor. 24 solves a cell is
    far too few for a rate difference to mean anything; a discordant count is
    exactly what a paired design buys instead.
    """
    say()
    say(title)
    # The slot a scenario occupies, with the pairing axis removed — otherwise
    # every key holds one value of the axis and nothing is ever paired.
    slot = [k for k in ("truth", "n", "exposure", "seed") if k != axis]
    idx: Dict[tuple, dict] = {}
    for r in rows:
        idx.setdefault(tuple(r.get(k) for k in slot), {})[r.get(axis)] = r
    dead = ("NO_BRIEF", "NO_PINWHEEL", "HARNESS_ERROR")

    arms = (("guillotine", "pinwheel", "*both arms*") if axis != "truth"
            else ("*both arms*",))
    say(f"{'arm':>12} {'both':>6} {'neither':>8} {f'lost at {hi}':>14} "
        f"{f'gained at {hi}':>15} {'p (McNemar)':>12}  {'no-Brief lost':>14}")
    for arm in arms:
        both = neither = lost = gained = nolost = 0
        for key, d in idx.items():
            a = key[0] if axis != "truth" else arm
            if arm != "*both arms*" and a != arm:
                continue
            if lo not in d or hi not in d:
                continue
            x, y = d[lo], d[hi]
            if x.get("status") not in dead and y.get("status") in dead:
                nolost += 1
            # A slot where one side had no scenario to solve is a fact about the
            # GENERATOR, not the solver, and must not enter the McNemar — it
            # would read "the pinwheel arm lost" where nothing was ever solved.
            if x.get("status") in dead or y.get("status") in dead:
                continue
            vx, vy = bool(x.get("valid")), bool(y.get("valid"))
            both += vx and vy
            neither += not vx and not vy
            lost += vx and not vy
            gained += vy and not vx
        p = _binom_two_sided(min(lost, gained), lost + gained)
        say(f"{arm:>12} {both:>6} {neither:>8} {lost:>14} {gained:>15} "
            f"{p:>12.4f}  {nolost:>14}")

    say()
    say(f"{'arm':>12} {'n':>5} {'both':>6} {f'lost at {hi}':>14} "
        f"{f'gained at {hi}':>15}")
    per: Dict[tuple, List[int]] = defaultdict(lambda: [0, 0, 0])
    ni = slot.index("n")
    for key, d in idx.items():
        a = key[0] if axis != "truth" else "*both arms*"
        n = key[ni]
        if lo not in d or hi not in d:
            continue
        if d[lo].get("status") in dead or d[hi].get("status") in dead:
            continue
        vx, vy = bool(d[lo].get("valid")), bool(d[hi].get("valid"))
        c = per[(a, n)]
        c[0] += vx and vy
        c[1] += vx and not vy
        c[2] += vy and not vx
    for (a, n) in sorted(per, key=lambda k: (k[0], k[1])):
        c = per[(a, n)]
        if any(c):
            say(f"{a:>12} {n:>5} {c[0]:>6} {c[1]:>14} {c[2]:>15}")


def budget_table(rows: List[dict], title: str) -> None:
    """Part II.3's budget curve, one column per arm. Answers `does 15 s still
    catch the same share` without re-solving."""
    say()
    say(title)
    say(f"{'budget':>8} " + " ".join(
        f"{a[:10]:>12}" for a in ("guillotine", "pinwheel")) +
        f" {'  (share of solves reaching a zero-slack Plan)':<46}")
    arms = {a: [r for r in rows if r.get("truth") == a
                and r.get("status") not in
                (None, "NO_BRIEF", "NO_PINWHEEL", "HARNESS_ERROR")]
            for a in ("guillotine", "pinwheel")}
    for b in (3.0, 5.0, 7.5, 10.0, 15.0):
        cells = []
        for a in ("guillotine", "pinwheel"):
            rs = arms[a]
            hit = sum(1 for r in rs if r.get("valid_at") is not None
                      and r["valid_at"] <= b)
            cells.append(pct(hit, len(rs)))
        say(f"{b:>7.1f}s " + " ".join(f"{c:>12}" for c in cells))


def main() -> None:
    want = [s.upper() for s in sys.argv[1:]] or ["A", "D", "T", "B", "C", "E"]

    say("=" * 118)
    say("Ticket 29 -- does the solver handle a target no sequence of cuts can")
    say("take apart? Guillotine baseline against a pinwheel treatment, paired")
    say("on Envelope, room count, seed, noise and config.")
    say("=" * 118)

    if "A" in want:
        rows = load("A")
        if rows:
            pooled(rows, "A. Pooled over the whole main grid")
            paired_flip(rows, "truth", "guillotine", "pinwheel",
                        "A. THE HEADLINE TEST -- paired across arms on the same "
                        "(n, exposure, seed) slot. `lost` means the guillotine "
                        "arm produced a survivor there and the pinwheel arm did "
                        "not.")
            budget_table(rows, "A. Time budget -- Part II.3's curve, per arm")
            paired_table(rows, ["n"],
                         "A. By room count (both exposures pooled)")
            paired_table(rows, ["exposure", "n"], "A. By exposure and count")

    if "T" in want:
        rows = load("T")
        if rows:
            pooled(rows, "T. Pooled -- t_int 100 and 150 together")
            paired_table(rows, ["t_int", "n"],
                         "T. t_int: what every published number was fitted at "
                         "(100) against what ADR 0010 ships (150)")
            paired_flip(rows, "t_int", 100, 150,
                        "T. PAIRED -- the same Envelope, seed and Proposal at "
                        "both t_int. This is the test that carries the finding.")
            say()
            say("T. The same rows read as a t_int effect within each arm:")
            say(f"{'arm':>12} {'t_int':>6} {'solves':>7} {'valid':>7} "
                f"{'INFEAS':>7} {'no-brief':>9} {'p50':>7} {'p90':>7}")
            for arm in ("guillotine", "pinwheel"):
                for t in (100, 150):
                    s = summarise([r for r in rows if r.get("truth") == arm
                                   and r.get("t_int") == t])
                    say(f"{arm:>12} {t:>6} {s['solved']:>7} "
                        f"{pct(s['valid'], s['solved']):>7} "
                        f"{s['infeasible']:>7} {s['nobrief'] + s['nopin']:>9} "
                        f"{fmt(s,'va_p50')} {fmt(s,'va_p90')}")

    if "B" in want:
        rows = load("B")
        if rows:
            paired_table(rows, ["tau"],
                         "B. tau -- the valve on relation-hardness",
                         "The shipped value is 4. If a denser relation graph "
                         "moves the optimum, it moves here.")
            paired_table(rows, ["n", "tau"], "B. tau by room count")

    if "C" in want:
        rows = load("C")
        if rows:
            paired_table(rows, ["sigma"],
                         "C. sigma -- Proposal noise, and the feasibility cliff",
                         "Part II found v1's 0.5 m sits one notch below a cliff. "
                         "n = 8 and 24 only: underpowered, see suite E.")
            paired_table(rows, ["n", "sigma"], "C. sigma by room count")

    if "D" in want:
        rows = load("D")
        if rows:
            pooled(rows, "D. The top of the range at 30 s, not the shipped 15")
            paired_flip(rows, "truth", "guillotine", "pinwheel",
                        "D. Paired across arms at 30 s")
            paired_table(rows, ["n"],
                         "D. Does the pinwheel arm catch up given 30 s?",
                         "If it does, 20-24 is a time-limit finding. If it does "
                         "not, it is a feasibility one.")

    if "E" in want:
        rows = load("E")
        if rows:
            paired_table(rows, ["sigma"],
                         "E. sigma at n = 10, 12, 16 -- the band where a "
                         "pinwheel exists and the solver is not saturated")
            paired_flip(rows, "truth", "guillotine", "pinwheel",
                        "E. Paired across arms, pooled over sigma")
            paired_table(rows, ["n", "sigma"], "E. sigma by room count")

    say()
    OUT.write_text("\n".join(LINES) + "\n", encoding="utf-8")
    print(f"\n-> {OUT}")


if __name__ == "__main__":
    main()
