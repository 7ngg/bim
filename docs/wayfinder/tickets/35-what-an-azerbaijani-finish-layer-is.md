---
id: 35
title: What an Azerbaijani finish layer actually is
parent: map
labels: [wayfinder:research]
status: open
assignee:
blocked_by: []
writes:
  - docs/research/ (new findings doc) — read-only on the profile
---

# What an Azerbaijani finish layer actually is

## Question

**ADR 0010 made the finish layer load-bearing and shipped its thickness as
`engine_choice`.** `profiles.AZ.construction.catalogue.brick.t_finish` is
**15 mm**, and no Azerbaijani document read on this map states a plaster
thickness. Every published dimension and every area in v1 now measures to that
plane, so this is the single weakest number under the largest number of
consumers.

The value is not a guess in the ordinary sense — it is corroborated **from
inside**: `t_party`'s shipped 250 mm leaf was derived from an acoustic table
whose rows read *"brick + 15 plaster both sides"* (250 → 52 dB, passes AzDTN
2.7-2's 50 dB; 120 → 49 dB, fails). So 15 is already load-bearing in a
`verified`-sourced derivation, and changing it re-opens `t_party`. That is
self-consistency, not a source, and *The Azerbaijani region profile* established
exactly why that gap matters: a `REPORTED` number off a repealed ancestor is not
a safe degradation of `VERIFIED`, and publishing folklore is the C8 breach this
map keeps nearly committing.

**Find:**

1. **The normative plaster/render thickness for internal brick masonry in
   Azerbaijan**, read first-hand. `arxkom.gov.az` served the AzDTN corpus on an
   unauthenticated GET for *The Azerbaijani region profile*; start there. The
   likely instruments are the finishing-works norm and the masonry norm
   (`az_azdtn_2_17_1` is already in `sources`). Russian ancestors —
   СП 71.13330, ГОСТ 31377 — may be read for **shape** (that plaster is
   specified by quality class, and how many classes there are) but their
   **numbers must not be transferred**: AzDTN 2.7-2 terminated SNiP's force in
   Azerbaijan in 2021 and the same trap caught this map once already.
2. **Whether it is one number or a class ladder.** If the norm grades plaster by
   quality class — simple / improved / high-quality — then `t_finish` is a
   *choice among published values*, not an invention, and the profile should say
   which class it ships and why. That is a materially better answer than a single
   `engine_choice` even if the shipped millimetres do not move.
3. **Whether the number is a thickness or a tolerance.** Finishing norms often
   publish a *maximum deviation from plane* rather than a build-up depth. Those
   are not the same quantity, and reading one as the other is the failure mode
   this ticket exists to avoid.
4. **What the corpus says, if anything.** Swiss Dwellings and ResPlan record wall
   thicknesses; whether either records a finish layer separately is unknown and
   is a cheap check. A negative result is a finding — *Which region profiles
   ship in v1* got its most useful answer that way.

**Consequences of a different number, so the cost of getting it wrong is
visible.** `t_int = t_int_structural + 2 · t_finish`. At 15 that is 150. At 10 it
is 140, at 20 it is 160. Each of those:

- moves the ADR 0007 residue class (`min + t_int ≡ 0 mod 250`) — 100, 110 or 90;
- shifts every Space area by roughly 1% of the dwelling;
- leaves ADR 0004's even-thickness gate **unbound** — already settled by ADR 0010
  consequence 2, which binds evenness on the numbers that get *halved* and exempts
  a layer component that only ever enters a total *doubled*. `120 + 2 · t_finish`
  is even for every integer `t_finish`. **Do not rule out an odd answer**; the
  gate asserts the exemption explicitly and passes at 15;
- re-opens `t_party` if it contradicts the acoustic table's assumption.

**Deliverable:** the value with `conf: verified` if a document supports it, or an
explicit statement that no Azerbaijani instrument publishes one — in which case
`engine_choice` stands and the note must say that the search was made rather than
skipped. Either outcome closes this ticket; only silence does not.
