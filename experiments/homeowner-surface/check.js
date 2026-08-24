// PROTOTYPE CHECK — parse the prototype's script and exercise the pure
// geometry/render functions headlessly. Catches syntax errors and renders.
const fs = require("fs");
const vm = require("vm");
const html = fs.readFileSync("prototype.html", "utf8");
const m = html.match(/<script>([\s\S]*)<\/script>/);
let src = m[1];
// strip the DOM wiring tail (everything from the WIRING banner)
src = src.split("/* ============================================================ WIRING */")[0];
const ctx = { console, document: { documentElement: {}, getElementById: () => null,
  createElement: () => ({ set innerHTML(v){}, get firstElementChild(){return null} }),
  querySelectorAll: () => [] }, setTimeout };
vm.createContext(ctx);
src += ";globalThis.__X={PLANS,planSVG,diffLine,deriveDoors,deriveWindows,packFixtures,clearOf,areaM2,S,STD};";
vm.runInContext(src, ctx, { filename: "prototype-inline.js" });
const { PLANS, planSVG, diffLine, deriveDoors, deriveWindows, packFixtures,
        clearOf, areaM2, S, STD } = ctx.__X;
let bad = 0;
console.log(`plans: ${PLANS.length}`);
for (const p of PLANS) {
  const doors = deriveDoors(p), wins = deriveWindows(p);
  const cls = p.rooms.map(clearOf);
  const tot = cls.reduce((a, c) => a + areaM2(c), 0);
  let fx = 0;
  p.rooms.forEach((r, i) => { fx += packFixtures(r.kind, cls[i]).length; });
  const svg = planSVG(p, { w: 400 });
  const reach = new Set([p.entry]); doors.forEach(d => reach.add(d.into));
  const ok = reach.size === p.rooms.length;
  if (!ok) bad++;
  if (!svg.startsWith("<svg") || svg.length < 500) { bad++; console.log("  BAD SVG"); }
  console.log(`  ${p.label.padEnd(22)} rooms=${p.rooms.length} doors=${doors.length}` +
    ` windows=${wins.length} fixtures=${fx} Σarea=${tot.toFixed(1)}m²` +
    ` svg=${(svg.length/1024).toFixed(1)}KB reachable=${reach.size}/${p.rooms.length}${ok?"":"  <-- UNREACHABLE"}`);
  // smallest clear dimension, against the shipped ergonomic floor
  p.rooms.forEach((r, i) => {
    const c = cls[i], sh = Math.min(c.x2-c.x1, c.y2-c.y1);
    const flo = STD.rooms[r.kind] && STD.rooms[r.kind].min_short;
    if (flo && sh < flo) { bad++; console.log(`    ! ${r.kind} short dim ${sh} < ergonomic floor ${flo}`); }
  });
}
console.log(`diffLine sample: ${diffLine(PLANS[0])}`);
S.lang = "en";
console.log(`diffLine EN:     ${diffLine(PLANS[0])}`);
console.log(bad ? `FAIL (${bad})` : "OK");
process.exit(bad ? 1 : 0);
