"""Render annotation.md section 14's worked example as a sheet set.

Throwaway rig. It exists so the drawing layer can be looked at against the one
Plan on this map whose every number is published.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))

from bim_engine import (build, check, dimensions, dxf, openings, preview,
                        sheet as sheet_mod, tags)
from bim_engine.selftest import s14_plan

JOB = {"project": "annotation.md s14", "job": "BE-S14", "client": "—"}

plan = s14_plan()
openings.place(plan)
dims = dimensions.derive(plan, 50)
wall = build.wall_region(plan)
foot = build.footprint(plan)
fx0, fy0, fx1, fy1 = foot.bounds
sh = sheet_mod.choose(plan, dims, (int(fx1 - fx0), int(fy1 - fy0)))
print("sheet %s 1:%d  extent %.1f x %.1f paper"
      % (sh.size, sh.scale, sh.extent_paper[0], sh.extent_paper[1]))

tg = tags.place(plan, sh.scale)
a1 = sheet_mod.title_attribs(plan, sh, JOB, 1, 2)
a2 = sheet_mod.title_attribs(plan, sh, JOB, 2, 2)
notes = sheet_mod.general_notes(plan)

out = pathlib.Path(__file__).resolve().parent / "out"
out.mkdir(exist_ok=True)
preview.sheet1(plan, dims, tg, sh, wall, foot, a1, notes, str(out / "s14-sheet1.png"))
preview.sheet2(plan, sh, a2, str(out / "s14-sheet2.png"))
path, report = dxf.write(plan, dims, tg, sh, wall, foot, a1, a2, notes,
                         str(out / "s14.dxf"), enforce=False)
print()
for line in report.lines():
    print(line)
print()
print("wrote", path)
