"""Verify from glyph COORDINATES (not from -layout column guessing) that the '15'
on the plaster rows of AzDTN 2.12-4* Appendix 8* Table 1 sits in the
"Layin qalinligi, mm" (layer thickness) column, not the resistance column.

pdftotext -layout scrambled the top of this table, so the extracted text alone is
not trustworthy evidence for a column assignment. This reads the text-showing
operators via pypdf's visitor and reports each token's x position.
"""
import os, re
import pypdf

PDF = os.path.join("experiments", "finish-layer", "src", "azdtn_2_12_4.pdf")
PAGE_INDEX = 65  # 0-based; PDF page 66

items = []  # (y, x, text)

def visit(text, cm, tm, font_dict, font_size):
    t = (text or "").strip()
    if not t:
        return
    items.append((round(tm[5], 1), round(tm[4], 1), t))

r = pypdf.PdfReader(PDF)
page = r.pages[PAGE_INDEX]
page.extract_text(visitor_text=visit)

# group into visual lines by y (descending down the page)
items.sort(key=lambda z: (-z[0], z[1]))
lines, cur, cury = [], [], None
for y, x, t in items:
    if cury is None or abs(y - cury) < 3:
        cur.append((x, t)); cury = y if cury is None else cury
    else:
        lines.append((cury, cur)); cur = [(x, t)]; cury = y
if cur:
    lines.append((cury, cur))

def show(label, pred):
    print(f"--- {label} ---")
    for y, ws in lines:
        joined = " ".join(t for _, t in ws)
        if pred(joined):
            print(f"  y={y:7.1f} | " + "  ".join(f"[{t}]@x={x:.0f}" for x, t in ws))
    print()

show("HEADER (column anchors)",
     lambda j: ("qalınlığı" in j) or ("Havanüfuzetmə" in j) or ("materiallar" in j)
               or ("Cədvəl" in j) or ("Əlavə" in j))
show("PLASTER ROWS 27-29", lambda j: "suvaq" in j)
show("NEIGHBOUR ROWS 26 / 30 (sanity)",
     lambda j: bool(re.match(r"^\s*(26|30|31)\.", j)))

print("=== FULL ROW BLOCK, rows 26-31 (y 700 down to 480) ===")
for y, ws in lines:
    if 480 <= y <= 700:
        print(f"  y={y:7.1f} | " + "  ".join(f"[{t}]@x={x:.0f}" for x, t in ws))
