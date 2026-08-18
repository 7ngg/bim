# Annotation is derived from the Plan, not stored in it

Dimension chains and room tags are a **function** of the geometry, so storing them
in the Plan duplicates state that goes stale the moment a wall moves — and moving
walls is exactly what the deferred interactive re-solve is for. The Plan therefore
holds geometry only; a **Drawing** is derived from a Plan plus a sheet, and the
only thing persisted is an **Annotation override** — a human's correction to a
derived placement, which must survive a re-render.

This reverses the project glossary as it stood, which folded annotation into the
Plan. Recording it because a future reader will otherwise "fix" it by storing
dimension entities, which is the obvious thing to do and is wrong here.

## Consequences

- **Every geometry entity needs a stable identity that survives a re-solve.** This
  is the real content of the decision, not a side effect — an override with
  nothing durable to key on is not an override.
- Identity is anchored in the **Brief**, not in geometry. Rooms keep their identity
  across a regenerate because the Brief says they exist. Walls and openings are
  derived, so they do not, and anything referring to them refers by **relation** —
  the wall segment between two named rooms. A relation-keyed reference dies
  honestly when the topology changes; a geometry-keyed one silently reattaches to
  the wrong wall.
- Corner-case that falls out and is worth keeping: junction resolution ties break
  on **geometry** (longest run, then coordinate order), never on entity id —
  because ids are not stable across a regenerate, so an id tie-break would make
  corner treatment flicker between two runs of an identical brief.
- The override layer is **additive**: shipping pure derivation first and adding
  overrides later changes nothing about the model. There is no lock-in here, which
  is why it was worth taking now.
