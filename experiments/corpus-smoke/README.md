# Corpus smoke probes

Cheap questions asked directly of the raw corpora, before anything is fitted to
them. Run everything from the repo root with the pinned interpreter:

```
./venv/Scripts/python.exe experiments/corpus-smoke/<script>.py
```

Outputs go to `out/`, which is gitignored.

## The window-rule study — ticket 51

Three scripts, added by *A third of real kitchens have no window and the engine
may not draw one*. They settle whether `win.habitable_has_window`'s corpus cost is
a **retrieval** cost. It is not; the decision is ADR 0025 and `proposer.md` §4.5.

| script | what it answers | runtime |
|---|---|---|
| `window_rule_overlap.py` | the rule at index scale, and the **paired 2×2** against ADR 0016's conversion drop — the overlap the ticket demanded be measured rather than assumed | ~8 min |
| `boundary_contact.py` | the property the warp actually inherits: can each `needs_window` Room reach a wall, and with how much run against the solver's frontage budget | ~5 min, no corpus stream |
| `kitchen_niche_test.py` | is a windowless kitchen adjoining a lit room a `taxça-mətbəx`, or a dark room behind a **door**? | ~9 min |

Run `window_rule_overlap.py` first — `boundary_contact.py` §3 joins its
`out/window_rule_index.json` and degrades to a warning without it.

### Four things that will bite whoever runs these next

**The method is `h8-frontage/window_rules_corpus.py`'s, verbatim, and that is the
point.** Bridge 0.12 m to assemble a dwelling across its wall gaps, windows kept
only where they meet that envelope's own boundary band (0.60 m), a room has a
window where one meets its own band. Change any of the three and the numbers stop
being comparable with the 561-dwelling measurement they supersede. Double
attribution is left in deliberately: it biases toward *finding* a window, which is
the safe direction for a study that argues against a window rule.

**Read the room geometry from `rectangularise/out/swiss_dw.pkl`, not from the
CSV.** It holds all 46,800 dwellings with `NOT_A_ROOM` already dropped, and it
turns an 8-minute study into a 5-minute one. It carries **no openings**, so
anything about windows or doors still needs the stream. Copy it in; that directory
belongs to other tickets and nothing here writes to it.

**Three numbers for one rule, and they answer three questions.** `rules.json`'s
`corpus_cost` **0.4519** is `acceptance-thresholds/`'s **raw** arm over 42,985
unconverted dwellings; **38.55 %** is this study's converted index; and
**15.97 points** is the same rule's leave-one-out contribution to the whole bar.
None supersedes another. Do not overwrite `rules.json` with a figure from here.

**`frontage_reach` is a lower bound and is quoted as one.** It measures boundary
**contact**, because the conversion cannot tell `exterior` from `party`
(`proposer.md` §2.2.6). A room with reach may still take no window in the target
Envelope. The rank built on it demotes and never excludes, so under-counting costs
ordering and never coverage.

## The older probes

`smoke_swiss_dwellings.py`, `smoke_resplan.py`, `resplan_probe.py`,
`wall_thickness_swiss.py`, `exposure_swiss_dwellings.py` and `windowless_swiss.py`
predate the study above and are read by `docs/research/dataset-inventory.md`.
`exposure_swiss_dwellings.py` fixes the seed (`20260819`) and floor count (150)
that `h8-frontage/` and `envelope-exposure/` both inherit, so a dwelling sampled
in one appears in the others.

⚠️ `windowless_swiss.py`'s nine ~0.00-exterior dwellings were the first hint of
this study's question and are **not** the same population: they are dwellings with
no façade at all, where §4.5's residue is dwellings with a *room* that has none.
