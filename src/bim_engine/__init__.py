"""bim-engine — the drawing layer.

The first shipping module in this repo. Everything above it (retrieval, warp,
projection) still lives in `experiments/`; what lives here is the implementation
of three specs that had never been executed:

    docs/spec/openings.md     which opening, where, hinged which way
    docs/spec/annotation.md   graphics, dimensioning, annotation, schedules
    docs/spec/ifc-export.md   (not yet — see the demo-sheet README)

The contract is one way: a `Plan` (solved rectangles + a typed Envelope, in
integer millimetres on the clear plane) goes in, a `Drawing` comes out, and the
Drawing check (annotation.md §13) refuses to emit a file it knows is wrong.
"""

__all__ = ["profile", "model", "build", "openings", "dimensions", "tags",
           "schedules", "sheet", "dxf", "preview", "check", "fmt"]
