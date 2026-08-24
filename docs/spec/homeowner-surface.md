# The Homeowner surface — what C2's user sees and does

**Ticket:** *Homeowner product surface*.
**Depends on:** ADR 0003 (Envelope), ADR 0010 (finished faces), ADR 0012
(`h_clear`), ADR 0013 (the band), `docs/spec/brief.md`,
`docs/spec/annotation.md` §1, `docs/spec/acceptance-bar.md` §11,
`data/standards/room-constraints.json`.
**Primary source:** branch `prototype/homeowner-surface`,
`experiments/homeowner-surface/` — a clickable stub over six real solved
layouts. Every claim below was put on a screen before it was written down.

C2 makes the Homeowner the v1 buyer and defines them by what they cannot do:
not draw a boundary, not read a dimension string, not judge a plan on technical
merit. Every other document on this map is about the engine. This one is about
whether any of it is reachable.

---

## 1. The spine is a document, not a wizard

**One page. The Brief is the page.** It is present from the first parse to the
last export, always visible, always editable; results render beside it. There is
no "review step" you leave behind and no back button.

This is not a layout preference — it is the only spine that matches the
architecture. `brief.md` §1 makes an edit **literally** a re-resolution: one pure
call, provenance maintained by construction. C7 makes edit-and-regenerate the
entire post-generation story. A wizard would make the Brief a stage you pass
through, and would need its own state for "which step am I on" that `resolve`
does not have. A chat thread was rejected for a different reason: it hides
provenance, and C4 requires every assumption visible.

**Consequence.** Every error and every warning in this system can point at the
field that resolves it *and scroll to it*, because that field is on screen. The
zero-survivor diagnosis (§7) uses this directly.

## 2. The surface is Azerbaijani

`profiles.AZ.drawing.language` is `az`, `verified`, and its own note observes
that *the builder, not the Homeowner, reads the drawing*. Nothing decided what
the **Homeowner** reads. It is Azerbaijani, Latin script.

The product counts *otaq*, ships one region profile, and sells into Baku. An
English surface over an Azerbaijani drawing is a product with two audiences and
no user.

Three consequences, one of them a debt:

- **The parse takes Azerbaijani prose.** No change to `brief.md` §10 — the
  `StatedBrief` enum keys are English and never leave the engine; the prompt's
  vocabulary section is generated from `room-constraints.json` either way.
- **Numbers use the decimal comma everywhere**, not only on the sheet.
  `4,10 × 4,60 m`, `18,9 m²`. `profiles.AZ.drawing.thousands_separator` is
  **null** and must stay null in the UI too: CLDR gives `.` as the `az` group
  separator, so a grouped `4.400` reads as a decimal.
- ⚠️ **No Azerbaijani room-name table exists anywhere in this repo.** The
  prototype's names are unsourced placeholders. §10 hands this on.

## 3. What the Homeowner's plan drawing contains

Exactly `annotation.md` §1's `both` set — poché, door swings, glazing, room tag
(name, area, clear dimension pair) — **plus a fixture render**.

The fixture render is not an addition to the model and asserts nothing new. Every
one of the ergonomic layer's eighteen floors is *derived from a named fixture
packing*, and `ergonomic.fixtures_mm` ships the footprints as `verified` data
(AD M Appendix D, Open Government Licence) with `body_zone` = 300. Drawing a
1700 × 700 bath in a bathroom draws the arithmetic that already gates the room.
An unfurnished plan is what makes a floor plan read as a diagram, and it is the
same failure `annotation.md` §2 names for flat linework.

**It is labelled as scale, not design** — *"Mebel yalnız ölçünü göstərmək
üçündür"* — and it is toggleable. The furniture is not in the `Plan`, is not in
the DXF or the IFC, and is not a constraint.

**No 3D view in v1.** ADR 0012 makes an extrusion possible for the first time,
and it still buys nothing: every schematic-design competitor surveyed already
ships one, and it is not what separates two 3-otaq layouts from each other.

**No dimension chain in the Homeowner view**, which preserves
`annotation.md` §1's invariant — a dimension in any unit other than integer
millimetres may not be part of a chain — while still showing the one dimension
a Homeowner does read, the clear pair in metres to 2 dp.

## 4. Provenance is per field, and acknowledging is not editing

**Marker on the field, never a summary block.** An Assumption carries `field`,
`value`, `kind` and one sentence (`brief.md` §6); a summary list divorces the
sentence from the control that resolves it, which is the same discipline §9.1
applies to hard errors. The three kinds get three treatments — an
`invented_room` dashes the whole room card, an `invented_value` dots the field,
a `reading` uses a different colour because **the field is `stated`**.

Above the document sits a **count chip that filters the document**, not a
second list. One source of truth.

> **The load-bearing rule: the acknowledge control and the edit control must not
> look or behave alike.**

`brief.md` §6: *"An edit flips `invented` to `stated`. An acknowledgement does
not."* That fork selects which area rule applies —
`area.invented_envelope_hard` at ±5 % hard when we chose the field, versus
`area.given_envelope_warn` when they did. A surface that lets someone clear
assumptions by clicking a uniform "OK" silently converts every invented value
into a stated one and swaps the hard rule for a warning, invisibly. So the
acknowledge control says *"Düzdür"* and mutates nothing, the edit control is
separate, and the panel says so in words.

## 5. The Envelope is chosen as a ring of typed edges

A non-drawer never places a boundary. They pick a **dwelling type** from
`brief.md` §5's seven presets, shown as pictograms of the edge ring with the
`exterior` edges highlighted, under the question **"which sides get light"**.

That framing is ADR 0003's own: the difference between a flat and a house was
never provenance, it is *which edges can hold a window*. Daylight is the
Homeowner-legible name for that, and it is the thing they actually have an
opinion about.

Shape (rect / L / U / T) is a second control. **Notch positions are never
statable** and the surface says so rather than hiding it — someone who can place
a notch can draw, and C2 says they cannot.

## 6. Waiting shows survivors arriving, never a progress bar

Generation is a job; candidates run on threads and stream out as each passes the
bar. The screen shows **two counters — passed, and examined** — with each
survivor's thumbnail appearing as it lands.

A progress bar would have to lie: the denominator is unknown, because how many
candidates it takes to fill a gallery depends on how many are rejected. Showing
the reject count is not a confession, it is C6's product story — *generate many,
reject most, show survivors* — and it is what makes §7 comprehensible. Someone
who has watched fourteen candidates examined and four pass understands a run
that passes none. Someone shown a spinner does not.

## 7. Nothing to show splits into three screens, and two of them are instant

`acceptance-bar.md` §11 forbids ever showing a failing Plan. That leaves three
distinct empty-handed cases and they must not be conflated, because each names a
different field:

| case | when | what it says |
|---|---|---|
| **No home in the prose** | parse, instant | *"we could not find a home in that description"* — `brief.md` §9.1, never an LLM retry |
| **Accessibility** | parse, instant | *"this engine does not produce accessible layouts"* — `brief.md` §7, a refusal and not an ignore |
| **Room count past the gate** | parse, instant | §8 below |
| **Zero survivors** | after the wait | arithmetic over areas, below |

**The zero-survivor screen is arithmetic and it quotes `engine_view`.** Three
rows — the hard floor, the market recommendation, the Brief's own figure — plus
the dominant hard failure in plain language, plus **buttons that scroll to and
open the field that resolves it**. It reads the same numbers §9.4's parse-time
check reads, from the same block, so `acceptance-bar.md` §11's requirement that
the two produce the same sentence holds by construction rather than by review.

## 8. The gate is measured in one unit and voiced in another

ADR 0013 refuses outside **3–10 engine rooms** and promises **1–4 otaq**, and
says the engine count is never shown. That leaves a copy problem the ADR handed
here: a refusal has to name a number the Homeowner can act on, and the number the
gate fired on is not one they recognise.

**Two forms, selected by where the excess is.**

- Excess is otaq: *"You asked for 6 otaq. We plan flats and houses of 1–4
  otaq."*
- Excess is not otaq — three bathrooms, a utility and a storage: *"You listed
  N rooms. We cannot lay out that many separate rooms on one storey well."*
  N is **rooms the Homeowner listed**, never engine Rooms, so the invented
  circulation is not counted back at them.

**The middle zone runs and warns.** Inside the gate, outside the promise — 4.3 %
of real dwellings. The warning says the engine can build it and that we stand
behind 1–4 otaq, so the result may be weaker than expected. It appears before the
wait, not after.

**A second parse-time notice, from `engine_view`.** Where
`retrieval_pool_size` is low, the surface says how many real homes back this
mix, because `brief.md` §11 already computes it and *"what a Homeowner is told
when their Brief crosses the retrieval line"* stops being a UI question the
moment the number is in the object.

## 9. Export, session, device

**The Homeowner gets the practitioner set.** One primary control — the **PDF of
the full two-sheet set** (`A-101` plan, `A-102` schedules) — one **PNG** of the
`both`-filtered preview for sharing, and **DXF and IFC collapsed behind a single
"for your architect" control** with a line saying they will not open them. The
dimensioned set is C3's whole differentiator and every surveyed competitor stops
short of it; withholding it and handing over a picture ships the same product as
everyone else. They cannot read it. They can forward it.

**C8 and the three product limits are on the export panel and on the empty
state** — one storey, 1–4 otaq, house layouts from apartment priors, and no
code-compliance claim. Before they invest time, and again at the moment the file
leaves.

**No accounts, and the `StatedBrief` lives in the URL.** Serialised on every
edit, so a refresh restores, browser history is undo, and a bookmark is save.
This keeps *Persistence, accounts, hosting* fog rather than grabbing it, and
still gives the one thing people need — sending their brief to someone else. The
link carries the **request, not the results**: generation is not reproducible
from a Brief alone, and the surface says so.

**Desktop-first to author, phone-legible to view.** The Brief is a form-heavy
object — six to ten rooms, per-field markers, assumption text — and every
surveyed competitor is a desktop tool. But a plan gets shown to a spouse on a
phone, so the single-plan view and the share image must read at 390 px. v1 does
not promise a mobile authoring flow it cannot make good.

## 10. What this hands to other tickets

| obligation | to |
|---|---|
| An **Azerbaijani room-name table**, one name per ergonomic key. The `az` split is worse than the English one: `hol` and `dəhliz` are not interchangeable, which sharpens that ticket's own `hall`/`entrance_lobby`/`corridor` three-into-one gap | *Two room vocabularies in one file* — holds `room-constraints.json` and `CONTEXT.md` |
| A **locale dimension on every Homeowner-facing rule message.** `acceptance-bar.md` §11 requires a plain-language message per rule; all 38 are English, and §2 above makes them Azerbaijani. This is a schema change to `rules.json`, not a translation pass | whoever next holds `data/acceptance/rules.json` |
| **The room tag has no Homeowner-audience fallback.** `room_tag_fallback` is *room number + room schedule reference*, and the schedule is `practitioner` — so a tag too wide for its Space degrades, in the preview only, to a number pointing at a document the Homeowner never sees. Reproduced in the prototype at a 1,85 m room | *The annotation spec is US-shaped and the drawing is now Azerbaijani* — holds `annotation.md` |
| **A Brief may contradict itself and §9 does not notice** — see §11 | *What the engine says when the Envelope is bigger than the programme* — holds `brief.md` §9.4 |
| **`Room.target_area` and `Space` area are different numbers and the surface shows them identically** — see §11 | *What a room's area is allowed to be*'s successor, and `brief.md`'s holder |

## 11. Two defects this surface found in documents that are already settled

Both were found by putting two numbers on one screen, which is what a prototype
is for.

**A stated Brief can contradict itself, and the contradiction survives parse.**
`brief.md` §9.4's pre-check compares the sum of *realisable ergonomic minima*
against `target_area`, and §9.2's ladder fills silent rooms from
`market_default`. Neither path compares the **sum of the Homeowner's own stated
room areas** against their own stated total. A Brief naming rooms of 18 + 8 + 12
+ 11 + 11 + 4,2 m² and a total of 45 m² is arithmetically impossible on its face,
passes all three of §9.1's hard errors, passes §9.4, and fails only after a full
generate cycle — surfacing as zero survivors, which §7 then explains in terms of
*ergonomic* minima rather than in terms of the number the Homeowner typed. The
check is one addition and it belongs at parse time beside the other two.

**The Brief promises an area the plan does not deliver, in the same visual
register.** `CONTEXT.md` separates **Room** (programme: a target) from **Space**
(geometry: what was built). The document column shows `Qonaq otağı 24,5 m²` and
the plan beside it shows `Qonaq otağı 18,9 m²`, both as a room name and an area
in the same typeface. Nothing in the surface says one is a request and the other
is a result. §9.3 makes `Room.target_area` a two-sided band precisely because the
solver is free inside it, so this gap is not a rounding artefact — it is the
normal case, and it reads as a broken promise. The surface must mark which
number is which; whether the Brief should show the delivered area back after a
solve is the open half.

## 12. Honest limits

- **No furniture in the model.** §3's render is scale, not design, and no
  fixture-fit constraint follows from it.
- **No 3D, no interactive re-solve** (C7's deferred half), no direct manipulation
  of a wall.
- **No existing-plan input**, which every surveyed Homeowner-facing product
  accepts. Out of scope, not deferred.
- **The prototype's plans are not solves of the prototype's Briefs**, so §11's
  second defect was observed rather than measured. It follows from
  `CONTEXT.md`'s own Room/Space split and does not depend on the observation.
- **How many candidates are shown, and how a Homeowner chooses between them**, is
  *Variant generation and ranking*. §6 fixes what the wait looks like, not the
  economics behind it.
