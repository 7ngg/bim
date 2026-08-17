---
id: 13
title: Homeowner product surface
parent: map
labels: [wayfinder:prototype]
status: open
assignee:
blocked_by: [9, 10]
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
