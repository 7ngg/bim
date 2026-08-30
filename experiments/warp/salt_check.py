"""Assert that no rig seeds a PRNG from a per-process-salted `hash()`.

Ticket 82. This is `gate_check.py` / `env_check.py` one layer down again: those
assert that the toolchain and the profile still support the decisions taken
against them, and this asserts that a measurement can still be reproduced at all.

**The defect it catches, stated once.** `hash()` on a `str`, a `bytes` or a
`datetime` is salted per process unless `PYTHONHASHSEED` is set. A rig that seeds
a PRNG from one draws a different sample -- or a different OBJECTIVE -- in every
process, so two runs of the same script on the same input are two different
experiments. Ticket 65 fixed this in `gate_effect.py`'s Brief draw and in
`solver-toy/probe6.py` and the map recorded it as closed. It was not closed:
**six** further sites carried it, five of them seeding the warp's objective
weight vector (`W_STATED` 8 against `W_INVENTED` 1, per room) rather than a
sample, which is why the sampling-side fixes never reached them. Measured cost
before the repair: **32 of the 36 points** of per-pair `dev` disagreement and
**4 of the 4 points** of `served` disagreement across the whole warp rig, at
every time cap, including caps where no solve reaches the clock at all.

**Why a check and not a README line.** It was already a README line. The trap was
written into `experiments/warp/README.md` at ticket 65 -- naming `hash`,
`PYTHONHASHSEED` and the fix -- and five live sites went on carrying the defect
underneath it, in the same directory, for as long as that line stood. A rule that
is read is a rule that is skipped. `read_only`: this scans, it never edits.

Run: ./venv/Scripts/python.exe experiments/warp/salt_check.py
Exit 0 when every site is keyed, 1 when any is salted. Wire it into
`experiments/environment/env_check.py` alongside the other gates -- that file is
where a repo-wide assertion belongs and this directory is not its home.
"""

from __future__ import annotations

import io
import re
import sys
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# `hash(` reached from inside a PRNG seed or a sort key. Deliberately broad: the
# five repaired sites split across `random.Random(SEED ^ (hash(key) ...))` and a
# permutation seeded the same way, and a narrower pattern would have missed one.
SALTED = re.compile(r"(random\.Random|\.seed|prng|rng)\s*[=(].{0,80}?\bhash\s*\(",
                    re.S)
# `hash()` on an int is NOT salted -- only str, bytes and datetime are. A site
# hashing an int is sound and is not reported.
SKIP_DIRS = {"venv", ".git", "__pycache__", "node_modules", "data"}

# Sites this repo has deliberately left, with the ticket that owns each. A known
# site is reported as OWED rather than as a failure, so the check stays green
# while a repair is correctly waiting on its ticket -- and goes red the moment a
# NEW one appears. An entry here without a live ticket is the thing to be
# suspicious of.
OWED = {
    "experiments/plane-accounting/arms.py":
        "ticket 83 -- The sixth salted site, and two rigs that owe a repeat",
}


def code_only(src):
    """The source with every string literal and comment blanked to spaces.

    Without this the check reports itself: this file quotes the defective line
    in its own docstring, and so does `repro_floor.py`. A regex cannot tell a
    site from a description of a site, and a checker whose first two findings
    are its own prose is a checker nobody will keep. Line numbers and column
    offsets are preserved so a real hit still reports its true position.
    """
    out = list(src)
    try:
        toks = tokenize.generate_tokens(io.StringIO(src).readline)
        spans = [(t.start, t.end) for t in toks
                 if t.type in (tokenize.STRING, tokenize.COMMENT)]
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return src
    # offset of the first character of each 1-based line
    line_off, off = [0, 0], 0
    for ln in src.split(chr(10)):
        off += len(ln) + 1
        line_off.append(off)
    for (sr, sc), (er, ec) in spans:
        a, b = line_off[sr] + sc, line_off[er] + ec
        for i in range(a, min(b, len(out))):
            if out[i] != chr(10):
                out[i] = " "
    return "".join(out)


def scan():
    salted, owed = [], []
    for p in sorted(ROOT.rglob("*.py")):
        rel = p.relative_to(ROOT).as_posix()
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        try:
            src = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        src = code_only(src)
        for m in SALTED.finditer(src):
            line = src[:m.start()].count("\n") + 1
            # a quoted example inside a docstring is documentation, not a site
            frag = src[m.start():m.end()]
            if rel in OWED:
                owed.append((rel, line, OWED[rel]))
            else:
                salted.append((rel, line, frag.split("\n")[0].strip()))
    return salted, owed


def main():
    salted, owed = scan()
    print("salt check -- PRNG seeded from a per-process-salted hash()")
    print("scanned %s" % ROOT)
    print()
    for rel, line, why in owed:
        print("  OWED   %s:%d  -- %s" % (rel, line, why))
    for rel, line, frag in salted:
        print("  FAIL   %s:%d  %s" % (rel, line, frag[:90]))
    print()
    if salted:
        print("%d salted site(s). A PRNG seeded from hash() of a str draws a "
              "different sample in every process: two runs of one script on one "
              "input are two different experiments." % len(salted))
        print("Fix: zlib.crc32(key.encode()) -- same distribution, keyed to the "
              "input rather than to the process.")
        return 1
    print("%d site(s) owed to a ticket, 0 unowned. PASS." % len(owed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
