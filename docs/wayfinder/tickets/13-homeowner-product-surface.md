---
id: 13
title: Homeowner product surface
parent: map
labels: [wayfinder:prototype]
status: open
assignee:
blocked_by: [9, 10]
writes:
  - prototype only — no shared artifact
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
