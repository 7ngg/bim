---
id: 2
title: Language and runtime split
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
blocked_by: [3, 4]
---

# Language and runtime split

## Question

Which languages, and where do the process boundaries fall?

Left open deliberately while charting: C#, Go, TypeScript (Bun/Node/React/Next),
Python and C++ are all acceptable to the team. So this is a real design decision,
not a preference poll — and it should be made *after* the export and solver
research, because those two tickets determine which libraries are load-bearing.

The forces in tension:

- **ML lives in Python.** PyTorch, the dataset loaders, the training loop. Not
  negotiable.
- **The solver has options.** OR-Tools CP-SAT has first-class Python, C++, Java and
  C# bindings. If the solve turns out to be the latency bottleneck (see *Solver
  formulation for layout projection*), the binding language matters.
- **The BIM/export layer splits the field.** `ezdxf` and `IfcOpenShell` are
  Python. `hypar-io/Elements` is C# and is the single most reusable artifact the
  research pass found — a BREP/CSG kernel with IFC, glTF, DXF and SVG output. One
  of these choices costs a .NET boundary; the other costs writing the kernel work
  yourself.
- **The frontend is a browser.** TypeScript regardless.

Decide:

1. Engine language — one, or split between solver and BIM lift?
2. `hypar-io/Elements` or the Python export stack? Weigh what *BIM and CAD export
   stack* found about whether Elements covers the **annotation and dimensioning**
   half, which is the part C3 makes mandatory and no competitor documents.
3. Where the process boundary sits between the ML proposer and the solver, and
   what crosses it — the canonical geometry model serialised how?
4. Whether the engine is a library, a service, or a CLI in v1.
5. What the frontend talks to, and in what format.

Bias worth stating up front: a single-language engine is worth a lot to a small
team, and a cross-runtime boundary should have to earn its place. But if the
export research shows the Python stack cannot author real dimension entities, that
bias loses.

## Resolution

**The bias holds. One engine language — Python — and the only cross-runtime
boundaries that survive are ones that buy something other than a library.** Three
processes online, plus an offline fourth.

| Runtime | Language | Why it is its own process |
|---|---|---|
| **Engine** | Python | Solver, validator, geometry, export. The service. |
| **Proposer** | Python (torch) | Keeps torch out of the engine image; model swaps behind a fixed contract. |
| **Frontend** | TypeScript (Next.js) | Browser. Also the BFF — the only thing the browser talks to. |
| **Training** | Python (torch) | **Offline.** Never in the request path. |

Item by item:

1. **Engine language — one, and it is Python.** ML is Python and not negotiable;
   CP-SAT's measured 6.25 s *is* the Python number (the binding is a thin protobuf
   wrapper over C++); `ezdxf` and `ifcopenshell` are Python and are the only things
   verified by execution to author the annotation half C3 makes mandatory. Nothing
   is left for a second language to do.
2. **`hypar-io/Elements` is rejected — and the research behind the question was
   never done.** *BIM and CAD export stack* item 4 was never written up (§5 is absent
   from the findings doc), so the only evidence for Elements is one README-grade
   paragraph in `floorplan-generation-stack.md` §5.5. It does not need a session to
   settle: Elements' unique value is a **BREP/CSG kernel**, and ADR 0001 made the
   geometry **axis-aligned integer-millimetre rectangles and centrelines** — its
   differentiator solves a problem this map deliberately does not have, and it makes
   no annotation claim at all. C# stays available for a future Revit add-in without
   being the engine language.
3. **The proposer↔solver boundary is a process boundary; the solver's is not.** The
   proposer is an **out-of-process service with its own HTTP+JSON API**; the solver
   runs **in-process** in the engine. Per *Proposer architecture survey* the proposer
   needs a **GPU for training only** — at ~20M params and 8–16 ms per Proposal it is
   CPU-servable, so the boundary earns its place by keeping torch out of the engine
   image and making the model swappable, not by needing an accelerator. **gRPC is
   ruled out**: one call per Proposal, latency dominated by inference, and it would
   cost proto definitions maintained across Python and TypeScript for a saving
   invisible next to a 6.25 s solve.
4. **The engine is a service**, behind the Next.js BFF. Not a library, not a CLI.
5. **The frontend talks only to Next.js**, which proxies to the engine. Single
   origin, no CORS, one auth boundary, engine never internet-exposed. The route
   handlers must **stream through** rather than buffer, or incremental candidate
   delivery dies in the proxy.

### Decisions that fell out, and are load-bearing

- **Generation is a job, not a request.** C6 generates many candidates and each is a
  ~6.25 s solve; a request is tens of seconds on hardware not yet chosen. Candidates
  are produced concurrently and **stream out as each passes the acceptance bar**.
- **Candidate parallelism is threads, not processes.** Measured on this machine:
  CP-SAT's `Solve()` **releases the GIL** — two concurrent solves ran 4.05 s against
  8.05 s sequential, a 1.99× overlap. No multiprocessing, no model serialisation
  across a process boundary, region profile and catalogue shared in memory.
- **JSON is the format at every boundary.** ADR 0001's integer millimetres are exact
  in JSON at our magnitudes, so geometry crosses with **no float rounding anywhere**
  — and C4 makes the Brief a user-facing editable object, which a binary format
  fights. This decides the technology, not the schemas.
- **Export is split.** An **SVG preview is eager** for every survivor — the browser
  must render something and it cannot render DXF — while **DXF, IFC and PDF are lazy**
  on request. ADR 0002 already made annotation derived, so this is the model's grain,
  and it keeps `ezdxf`/`ifcopenshell` out of the generation loop.
- **The request path has two external network dependencies**: the Brief parser (C4's
  LLM) and the proposer service. The job model absorbs both; a synchronous one would
  not have.

### What this hands to other tickets

- **Solver timing variance sweep** — a second term to measure. The 6.25 s was
  measured with **all four cores on one solve** (`num_workers=4`). Under candidate
  parallelism each of `k` concurrent candidates gets `cores/k`, and **6.25 s does not
  hold there**. Measure throughput at `k` candidates × `num_workers = cores/k`
  against the single-solve baseline.
- **Acceptance validator spec** — candidate count is now a **cost dial as well as a
  latency dial**, because each candidate is a proposer call plus a solve.
- **Homeowner product surface** — the transport is decided, so its scope narrows to
  the UX. It does **not** have to pick a protocol.
- **Dimensioning and annotation rules** — the SVG preview and the DXF renderer read
  the **same derived `Drawing`**, so it specifies one annotation system, not two.

### Surfaced, and worth not losing

**The export research has a hole.** `docs/research/bim-cad-export-stack.md` runs
§3.7 → §6; **sections 4 (what Revit does on IFC import) and 5 (`hypar-io/Elements`)
were never written**, though both are items in that ticket's own deliverable. The
Elements gap is closed by decision above. The Revit gap is not — the map's line
*"Revit's IFC import is the weak link"* cites a §4 that does not exist, and has been
demoted from finding to open question.
