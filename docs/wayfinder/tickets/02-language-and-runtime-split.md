---
id: 2
title: Language and runtime split
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
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
