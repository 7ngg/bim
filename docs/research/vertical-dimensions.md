# Vertical dimensions

Findings for *The Plan has no vertical dimension, and three artefacts already
assume one* (ticket 39). Decision: **ADR 0012**. Values:
`data/standards/room-constraints.json`, `profiles.AZ`. Gates:
`experiments/region-profile/gate_check.py`.

---

## 0. The ticket's premise was half false, and the surviving half is different

The ticket states that a grep for a ceiling, storey, room or opening head height
across `room-constraints.json`, `acceptance-bar.md`, `brief.md` and `CONTEXT.md`
returns nothing. **It returns plenty.** Ticket 25 had already landed vertical
numbers; the IFC session that raised this grepped for *names* and not for
*values*.

Against `ifc-export.md` §12's own four-input table, as found:

| §12 input | State before this ticket |
|---|---|
| `h_clear` floor → ceiling | **shipped, `verified`** — 2700 / 2100, AzDTN 2.7-2 cl. 5.8 |
| per-opening `H` / head | **shipped** — every catalogue mark is H × W: `DG 21-7` = 2100 × 700 |
| per-window sill | **absent** |
| `h_storey` floor → floor | **absent** |

Two further unfilled slots the ticket did not count, and one it could not have:

- `annotation.md` general note 4 ships **"Clear ceiling height `H` mm"**, and its
  §Levels routes ceiling height to the general notes — **singular**, one per plan,
  against a profile publishing two heights.
- `CONTEXT.md`'s **Fall barrier** term names "the window's sill height" and
  `annotation.md`'s window schedule ships a `Fall barrier` column. **No guarding
  value exists anywhere in the data** — a sixth vertical slot, and the only one
  that is a safety number.

And a contradiction inside one document: `ifc-export.md` §5 gives `IfcSpace.Body`
as the polygon *"extruded to storey height"*, while §12 assigns `h_clear` to
`IfcSpace Body`. A Space is floor-to-ceiling. §5 is wrong.

So the work was **two numbers and a model decision**, not four numbers.

---

## 1. Source, and how it was read

**AzDTN 2.7-2** *Yaşayış binaları. Layihələndirmə normaları*, Baku 2021, the live
instrument — the same document ticket 25 established as having repealed
СНиП 2.08.01-89\* on 2021-11-30. Retrieved from `arxkom.gov.az`, 30 pages,
87,030 characters of extracted text.

Ticket 35's warning applies and was handled: `pdftotext` mangles this family's
tables. Text was extracted with `pymupdf` and every quotation below was taken from
the extracted stream and matched against the clause number in situ, not
reconstructed.

**The ticket-25 trap was live throughout.** Every number below is from the 2021
instrument. Nothing is quoted from СНиП 2.08.01-89\* or any other repealed
ancestor, and §2 records the one place where a *live* document nearly supplied a
number for a job it was never written for.

---

## 2. `h_storey`: the norm does not publish one, and the near-miss is instructive

**`mərtəbə hündürlüyü` occurs exactly twice in the norm**, and neither is a
requirement:

1. **§3, definitions.** As the term that classifies storeys — a `zirzəmi` storey
   is one where more than half the *storey height* is below planning grade, a
   `kürsülük` storey one where more than half is above it. The term is *used*, not
   *fixed*.
2. **Passenger-lift table, Note 2.** *"Cədvəl adambaşına 18 m² ümumi mənzil sahəsi,
   **mərtəbənin hündürlüyünün 2,8 m**, liftin hərəkət intervalının 81-100 s olması
   hesabı ilə tərtib edilmişdir."* — the table **was compiled on the basis of** a
   2.8 m storey height. Note 3 then directs that the lift count be recomputed
   where the storey height differs.

**This is the finding.** A 2.8 exists, in the right live document, and it is a
**lift-traffic modelling assumption** with an explicit instruction to recompute
when reality differs. Publishing it as `h_storey` would be ticket 25's trap in a
new costume — not a repealed number this time, but a live number doing a job it
was never written for, which is the same failure with better paperwork.

It also fails on arithmetic: **2.8 floor-to-floor over a 2.7 clear leaves ≈100 mm**
for slab plus floor build-up. No reinforced-concrete residential slab is 100 mm
including finish. The 2.8 is round, not measured.

**Recorded as `storey_height_mm: null` with `conf: verified`** — the confidence is
in the *absence*, which was established by reading, not by failing to find.

### What floor-to-floor would have bought

`ifc-export.md` §12 named two consumers. Both are empty:

| Claimed consumer | State |
|---|---|
| `IfcBuildingStorey` spacing | **vacuous** — exactly one storey, `Elevation = 0.0` |
| wall extrusion height | **a choice** — the export authors no `IfcSlab` and no `IfcRoof`, so nothing rests on a wall |

Verified by entity census over `ifc-export.md`: `IfcWall`, `IfcSpace`, `IfcSite`,
`IfcDoor`, `IfcWindow`, `IfcOpeningElement`, `IfcBuildingStorey` — **no
`IfcSlab`, no `IfcRoof`, anywhere.**

### Why "just omit it" was not available

A wall body **cannot** omit its height the way `Pset_WallCommon.LoadBearing` omits
itself. An `IfcExtrudedAreaSolid` needs a depth. ADR 0011's *present is a claim,
absent is unknown* does not reach an extrusion, so the choice was forced between a
number derived from a statutory `verified` figure and one invented from an
unsourced build-up. See ADR 0012.

---

## 3. `h_clear`: cl. 5.8 verbatim, and what the shipped cells were missing

> **5.8.** Yaşayış otaqlarının və mətbəxin hündürlüyü **2,7 m**-dən az olmamalıdır.
> Mansarda mərtəbələrinin yüksək hissəsində hündürlüyü **(döşəmədən tavanadək)**
> 2,7 m-dən az olmamalıdır.
> Mənzildaxili dəhlizlərin, holların, antresolların (və onların alt hissələrinin)
> hündürlükləri **insanların hərəkətinin təhlükəsizliyini təmin etmək şərtilə**
> 2,1 m-dən az olmamalıdır.

Both shipped values are confirmed. Two things the cells did not record:

- **The plane is quoted, not inferred.** *(döşəmədən tavanadək)* — floor to
  ceiling. `h_clear` is the source's own quantity. Given how much of this map's
  history is plane confusion (ADR 0010 exists because four documents claimed
  finished faces over a bare-leaf erosion), a source that states its own plane is
  worth recording as such.
- **The corridor figure is conditional.** *…provided the safety of people's
  movement is ensured.* It is an **allowance to reduce**, not a second
  requirement. Exercising it asserts a safety judgement this engine cannot make,
  and buys a dropped ceiling whose build-up the model does not carry. Flagged
  **inert in v1**, kept as data — the posture `area_convention`'s balcony
  coefficients already hold.

Register: `az olmamalıdır` = **məcburi**, so `statutory_floor`, per the profile's
own `source_force_vocabulary`.

---

## 4. Sill: the norm publishes none, so it is derived

**`pəncərə altlığı`: zero occurrences in the full 2021 text.** No window sill
height is published. Searched further and also absent: any window-specific
guarding clause, and any child-safety clause. A measured negative, in the class of
ticket 14's *"the corpus has no module at all."*

A per-room-type sill table would therefore have been **four invented numbers**. One
datum and an identity replaces it:

```
sill = head_datum − catalogue H
```

**`head_datum_mm` = 2200**, and it is not invented either: it is the **balcony
door's own catalogue head**, `BS 22-7,5`. A balcony door and the window beside it
share a lintel — the ordinary post-Soviet living-room composition — so the tallest
catalogue opening sets the head line and every window hangs from it. Doors sit
100 mm below at their own 2100, which is what a real elevation does.

Structure derived, one constant taken from the catalogue rather than from nowhere.
ADR 0009's shape.

| Opening | Mark | H | Derived sill |
|---|---|---|---|
| `window_living` | `OR 15-15` | 1500 | **700** |
| `window_bedroom` | `OR 15-12` | 1500 | **700** |
| `window_kitchen` | `OS 12-9` | 1200 | **1000** |
| `balcony_door` | `BS 22-7,5` | 2200 | 0 — it is a door, floor-mounted, and it *is* the datum |

The kitchen sill lands at **1000, clearing a 900 mm counter** — which is why the
kitchen window is the short one in the catalogue, a relationship nobody had noticed
and which the gate now asserts. All three sills are even, so ADR 0004 holds on
derived sills as well as on quoted openings.

⚠️ **A GOST opening mark is `<type> <height dm>-<width dm>` — height first.** The
first draft of this ticket read `OR 15-12` as 1200 tall and produced a bedroom sill
of 900. It is 1500 × 1200 and the sill is 700. The gate caught it. The profile's
own `catalogue` notes state the dimensions in `H × W` order and were correct
throughout; the misreading was ours.

---

## 5. Fall barrier: the height is statutory, the trigger is refused

> **8.3.** Pilləkən, balkon, lociya, terras, dam və **yıxılma təhlükəsi olan digər
> yerlərdə** məhəccərlərin hündürlüyü **1,2 m**-dən az olmamalıdır.

Register `az olmamalıdır` = **məcburi**. Corroborated at cl. 8.10, which requires
1.2 m guarding on trafficable flat roofs. Shipped `verified`.

**Windows are never named.** The clause reaches them only through *other places
where there is a risk of falling*, and **no sill threshold appears anywhere in the
norm.**

An `engine_choice` trigger of 1000 mm was drafted, gated, and **withdrawn** — and
the reason it was withdrawn is worth more than the number would have been. Under a
1000 mm threshold every window in the shipped catalogue came back guarded,
including the kitchen at 1000, which is visibly wrong for a post-Soviet flat. That
prompted the right question, which is not *what threshold* but *can this model
evaluate one at all*:

**It cannot, and not for want of a constant.** Whether a window is a place with a
risk of falling depends on **the drop below it** — which storey the dwelling is
on, and what lies outside. v1 has exactly one Storey at `Elevation = 0.0`,
`IfcSite` is out of scope, and the site is ruled out of scope on the map. A
ground-floor window needs no barrier; the identical window eight floors up does;
**nothing in the model distinguishes them.**

So the height is published and the trigger is refused. `annotation.md`'s `Fall
barrier` column reads `—` for every window in v1 — which that spec already
provides for: *"carries the guarding height where the model holds one, and `—`
where it does not."*

Choosing a threshold would have been a **safety** claim with no source and no way
to evaluate it. C8. A refusal in the same class as accessibility, and as §6 below.

---

## 6. The ergonomic layer owes no height

Zero occurrences of *height*, *vertical*, *sill* or *head* in the entire
`ergonomic` layer. Every figure in it is a **fixture footprint in plan**, generated
by `build_ergonomic_layer.py` from `fixtures_mm` and one calibrated body zone.

A height is not a footprint. There is no region-free ergonomic ceiling height to
derive, and the layer's own source corpus turned out to be accessibility
clearances throughout — the finding that already forced one calibration and one
refusal in ADR 0009.

**Recorded as an explicit refusal in the layer**, per the ticket's own instruction:
an empty answer written down is worth more than a borrowed one, and this layer has
already refused a number it was handed once.

---

## 7. What each value fills

| Artefact slot | Filled by |
|---|---|
| `annotation.md` door schedule, `Structural opening W × H` | catalogue mark, H from the mark's first group |
| `annotation.md` window schedule, `Structural opening W × H` | catalogue mark |
| `annotation.md` window schedule, `Sill height` | `head_datum − H` → 700 / 700 / 1000 |
| `annotation.md` window schedule, `Fall barrier` | **`—`, deliberately** — §5 |
| `annotation.md` general note 4, *Clear ceiling height `H` mm* | `h_clear`, one per Plan |
| `ifc-export.md` `IfcSpace` `Height`, `NetVolume` | `h_clear` |
| `ifc-export.md` wall body extrusion | `h_clear` — floor-to-ceiling, declared |
| `ifc-export.md` `IfcWindow` placement | derived sill |
| `ifc-export.md` `IfcDoor` head | catalogue mark |
| `ifc-export.md` `IfcBuildingStorey` spacing | **deleted** — vacuous at one storey |

---

## 8. Gates

`experiments/region-profile/gate_check.py`, **33 → 67 assertions, all pass.**

With `h_storey` deleted there is no floor-to-floor left to hide a bad opening in,
which makes the vertical gates load-bearing rather than decorative:

- `h_storey` is null — a non-null value is a claim the source does not make
- every catalogue head ≤ `h_clear`; every window `H` ≤ `head_datum`
- every derived sill is even (ADR 0004) and strictly inside the room
- the kitchen sill is above the living sill — the counter relationship, asserted
- the guarding height is `verified` **and** `fall_barrier_trigger_mm` is absent —
  the refusal is gated, so a later session cannot quietly supply one

---

## 9. What this leaves owed

Routed rather than written, because ticket 39's `writes:` does not reach them:

| Owed | Owner |
|---|---|
| `ceiling_height` field on the Brief, two-rung ladder, floored at 2700, `Assumption` when unstated | `docs/spec/brief.md` — ticket 38 is sole claimant |
| one hard Brief predicate: stated height below the statutory floor rejects the request, on `area.convention_agrees`' precedent | `data/acceptance/rules.json` — tickets 16 / 20 / 26 |
| `ifc-export.md` §12 four inputs → two; §5's `IfcSpace.Body` *"storey height"* → `h_clear` | `docs/spec/ifc-export.md`, no open claimant |
| window-schedule `Sill height` and `Fall barrier` column semantics; general note 4's `H` | `docs/spec/annotation.md` — ticket 32 |
| opening **placement** prose, which inherits this boundary rather than colliding with it | `docs/spec/openings.md` — ticket 16 creates it |

**`docs/spec/openings.md` was deliberately not created.** The ticket instructed
that the catalogue-versus-instance boundary be written into it, but the file does
not exist and ticket 16 creates it. Writing a new spec file another ticket owns, to
carry two sentences, maximises exactly the collision the map's `writes:` rule
exists to prevent — and 39 already had the widest write-set on the map. The
boundary is in `CONTEXT.md`'s **Opening** and **Head datum** terms and in the
profile data instead, so 16 inherits it. 39's write-set drops from three shared
artefacts to two.
