---
id: 13
title: Homeowner product surface
parent: map
labels: [wayfinder:prototype]
status: closed
assignee: tng
blocked_by: [9, 10]
writes:
  - prototype only — no shared artifact
  - DECLARED ON RESOLUTION: docs/spec/homeowner-surface.md (new),
    experiments/envelope-exposure/ (new, on master), and
    experiments/homeowner-surface/ on branch prototype/homeowner-surface.
    Nothing else was claimed at the time, so the concurrency rule held —
    ticket 28's precedent. experiments/envelope-exposure/ exists rather than
    experiments/solver-toy/ precisely because 29 claims the latter; the probes
    import it and never edit it.
---

# Homeowner product surface

## Question

What does the Homeowner actually see and do, end to end?

C2 makes the Homeowner the v1 user, and they are defined by what they *cannot*
do: not draw a boundary, not read a dimension string, not judge a plan on
technical merit. Every decision on this map so far has been about the engine. This
one is about whether any of it is usable.

Raise the fidelity by building something rough and concrete to react to — an
outline, wireframes, or a clickable stub. Not production code.

The flow to make concrete:

1. **Prompt.** A blank box, or a guided form, or a box with examples? What does a
   first-time user type, and what happens when they type something useless?
2. **Brief review.** C4 requires assumptions to be visible and the brief to be
   editable. What does a Homeowner see — a list of rooms with sizes they can
   nudge, marked where the system invented a value? How is "I assumed a 12 m²
   second bedroom" said in language they understand?
3. **Envelope.** Whatever *Building scope and envelope handling* decides, this is
   where it gets an interface a non-drawer can use.
4. **Waiting.** Generation and solving take time. What is on screen?
5. **Variants.** How many plans, shown how, compared how? A Homeowner cannot read
   a plan the way a Practitioner can — what makes two options legibly different to
   them? Room labels and furniture, or a 3D view?
6. **Rejection.** What happens when the validator rejects everything and there is
   nothing to show? This is the case that will actually occur and it is the one
   nobody designs.
7. **Export.** C3 delivers DXF, IFC and PDF — none of which a Homeowner opens.
   What do *they* get, and where does the Practitioner-grade export sit without
   cluttering their view?

Deliverable: the prototype, linked from this ticket as an asset, plus the
decisions it settled.

## Inherited from *Dimensioning and annotation rules*

Item 7 ("what do *they* get, and where does the Practitioner-grade export sit
without cluttering their view") is now half-answered, structurally.

There is **one `Drawing`, two presentations**. Every annotation element carries an
**audience** — `both` or `practitioner` — and a render target draws only what is
tagged for it. So the Homeowner's eager SVG preview is not a different drawing
engine, it is a filter: plan graphics (poché, door swings, glazing), room tags,
and nothing else. No chains, no type marks, no title block, no schedules.

Two consequences the prototype should react to rather than re-derive:

- **The preview renders metres to 2 dp** (`4.40 × 3.40 m`, `16.06 m²`) while the
  sheet renders integer millimetres. That is safe only because the preview draws no
  chain — the invariant is that a dimension in any unit other than integer
  millimetres may not be part of one. If the prototype wants a chain in the
  Homeowner view, that invariant is what it is trading against.
- **The clear dimension pair is the one dimension a Homeowner does read**, and it
  is `both` for that reason. The glossary says they cannot read a dimension string;
  it does not say they cannot read `4.40 × 3.40 m` in the middle of a room, which is
  what every estate-agent plan shows. Whether that holds is a question for the
  prototype, and it is a cheap one to put in front of someone.

---

## Handed in by *The room-count envelope v1 promises* (ADR 0013)

**Item 1 gets a stated limit, and item 6 gets a case that is not a solver
failure.** The third product limit, beside C5's two:

> **We plan flats and houses of one to four rooms** — one storey, and house
> layouts come from apartment priors.

Three things the prototype should react to rather than re-derive:

- **The copy counts otaq** — habitable rooms only, how a Baku flat is advertised.
  The engine gate counts something else (engine Rooms, including circulation the
  Homeowner never mentioned) and refuses outside 3–10. **Do not show the engine
  count anywhere**, and do not convert between the two by a constant: one otaq is
  a *median* of four engine Rooms with a spread of two to three.
- **There is a middle zone**, 4.3 % of real dwellings: inside the gate, outside
  the promise. It runs and warns. What that warning says to someone who cannot
  read a plan is a surface question, and it is yours.
- **Refusal happens at parse time, before any waiting screen** — so item 6's
  "nothing to show" case splits in two. A room-count refusal is instant and
  names the count; a zero-survivor rejection comes after the wait and is
  arithmetic about areas. They are different screens, and conflating them tells
  a Homeowner the wrong thing about which field to edit.

---

## Resolution

**The surface is a living document in Azerbaijani, and the two things that
decided it were both already in the repo.**

Spec: `docs/spec/homeowner-surface.md`. Prototype: branch
`prototype/homeowner-surface`, `experiments/homeowner-surface/` — a
double-clickable single file over **six real solved, validated layouts** from
`experiments/solver-toy`, drawn at the shipped constants (`t_int` 150,
`t_ext_total` 500, ADR 0001's erosion), with `check.js` asserting
door-reachability from the entry and every clear dimension against its shipped
ergonomic floor. `#happy/gallery`, `#zero/zero`, `#rooms`, `#big`, `#access`,
trailing `/en` for the English mirror.

### The seven decisions

1. **Living document, not a wizard or a chat.** `brief.md` §1 makes an edit
   literally a re-resolution and C7 makes edit-and-regenerate the whole
   post-generation story; a wizard needs step state `resolve` does not have.
   Chat hides provenance, which C4 requires visible.
2. **Azerbaijani surface**, Latin script, decimal comma everywhere and
   thousands separator **null** (CLDR gives `.` for `az`, so a grouped `4.400`
   reads as a decimal). No change to `brief.md` §10 — the enum keys never leave
   the engine.
3. **`both` set plus a fixture render**, toggleable and labelled as scale not
   design. **No 3D**, though ADR 0012 has just made one possible.
4. **Per-field provenance markers with a filter chip**, never a summary block;
   and the **acknowledge control must not look or behave like the edit
   control**.
5. **A ring of typed edges, asked as "which sides get light."** Notch positions
   stated as unstatable rather than hidden.
6. **Survivors arriving, two counters, no progress bar.**
7. **The practitioner PDF is the Homeowner's download**; DXF/IFC behind one
   "for your architect" control; no accounts, `StatedBrief` in the URL;
   desktop to author, phone to view.

### What the evidence changed

**The fixture decision reversed on the data.** Going in, furniture looked like a
render nobody had funded and the recommendation was to leave it out of v1.
`ergonomic.fixtures_mm` turns out to ship **fourteen footprints as `verified`
data** — AD M Appendix D under the Open Government Licence, `body_zone` 300 —
and **all eighteen** room floors are derived from a *named packing* of them:
*"3-seat settee 850 deep + body 300 + armchair 850 deep"*, *"double bed 1350 ×
1900 + body 300 to one side"*. Drawing the fixtures draws the arithmetic that
already gates the room. It asserts nothing new and it is the strongest
legibility lever available, which is what item 5 was asking for.

**The surface language was never decided by anyone.**
`profiles.AZ.drawing.language` is `az`/`verified` and its own note says *"the
builder, not the Homeowner, reads the drawing"* — which quietly scoped itself to
the sheet and left C2's user unaddressed. It is now decided, and it is the one
decision here that costs real work downstream (§10 of the spec).

### Two defects found in already-settled documents

Both came from putting two numbers on one screen.

- **A stated Brief can contradict itself and survive parse.** §9.4 compares
  realisable ergonomic minima against `target_area`; §9.2's ladder fills silent
  rooms. **Neither compares the Homeowner's own stated room areas against their
  own stated total.** 18 + 8 + 12 + 11 + 11 + 4,2 m² of rooms inside a stated
  45 m² clears all three of §9.1's hard errors and all of §9.4, and dies after a
  full generate cycle — explained back in terms of ergonomic minima rather than
  the number they typed. One addition, at parse time, beside the other two.
- **The Brief promises an area the plan does not deliver, in the same visual
  register.** `Room.target_area` (a request) and `Space` area (a result) render
  identically — `Qonaq otağı 24,5 m²` in the document, `Qonaq otağı 18,9 m²` on
  the plan beside it. §9.3 makes the target a two-sided *band* on purpose, so
  this is the normal case, not drift. It reads as a broken promise.
  `CONTEXT.md`'s Room/Space split is leaking into the UI unmarked.

### One question the ADR handed here, answered

ADR 0013 gates on engine rooms, promises in otaq, and forbids showing the engine
count — leaving a refusal that has to name a number the Homeowner recognises.
**Two forms, selected by where the excess is:** in otaq when the excess is otaq
(*"you asked for 6 otaq; we plan 1–4"*), and in **rooms the Homeowner listed**
when it is not (three bathrooms, a utility, a storage). Never a converted number,
so invented circulation is never counted back at them.

### What could not be done

- **The prototype's plans are not solves of the prototype's Briefs.** The
  layouts are real and the Briefs are hand-built; wiring `resolve` to the toy
  was out of scope for a throwaway. So the second defect above was **observed,
  not measured** — it follows from `CONTEXT.md`'s own Room/Space split and does
  not rest on the observation.
- **The clear-dimension question — whether a Homeowner reads `4,40 × 3,40 m` —
  was rendered but not tested on a person.** It is on the screen, in the tag,
  and it is now a cheap thing to put in front of someone. Unanswered, not
  assumed.
- **`engine_view`'s four numbers are plausible constants in the prototype**, not
  computed. The surface reads them and never recomputes, which is the property
  that mattered.

### Handed on

Five obligations, **no new tickets** — every one lands on a file an existing
frontier ticket already claims. `docs/spec/homeowner-surface.md` §10 carries
them in full:

| obligation | to |
|---|---|
| An Azerbaijani room-name table, one per ergonomic key. **The `az` split is worse than the English one** — `hol` and `dəhliz` are not interchangeable — which sharpens that ticket's own three-into-one gap | *Two room vocabularies in one file* |
| A **locale dimension** on every Homeowner-facing rule message. All 38 are English and §2 makes them Azerbaijani. A schema change, not a translation pass | `rules.json`'s next holder (16, 20, 26) |
| **The room tag has no Homeowner-audience fallback** — `room_tag_fallback` is a room number plus a **`practitioner`** schedule, so a tag too wide for its Space points the Homeowner at a document they never see. Reproduced at a 1,85 m room | *The annotation spec is US-shaped* |
| The self-contradicting Brief, as a parse-time check | *What the engine says when the Envelope is bigger than the programme* |
| Marking which area is a request and which is a result | `brief.md`'s next holder |

### Fog sharpened, not grabbed

- **Fixtures and furniture** — the *surface* half is answered (render, not
  constraint, and the footprints already exist as verified data). Whether
  furniture-fit becomes a constraint is untouched.
- **Persistence, accounts, hosting** — v1 surface needs no backend at all: the
  `StatedBrief` in the URL. The patch stays fog; it now knows what it is not
  blocking.
- **Variant generation and ranking** — §6 fixes what the wait looks like and
  that the reject count is shown. **How many are produced, survive and are
  shown, and how a Homeowner chooses, is untouched** — but the gallery now has a
  concrete difference line (largest room, daylight side, what the front door
  opens onto) that is computed rather than scored, which is a candidate for the
  "how a Homeowner chooses" half.
