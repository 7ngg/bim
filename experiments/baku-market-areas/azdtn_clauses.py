"""Re-read AzDTN 2.7-2 cl. 5.1 / 5.7 and AzDTN 2.7-3 cl. 5.1 first-hand from the
cached PDFs' pypdf text, so every AZ figure this research quotes is `verified`
rather than inherited. Prints the clause bodies verbatim.

md5 of the sources this was run against:
  azdtn_2_7_2.pdf  4b5da47dd11808cd0aef37a75b01b4e9
  azdtn_2_7_3.pdf  d615accb5950c825bed4e3cfbadf6842
"""
import hashlib, os, re, sys

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "finish-layer", "src")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "finish-layer", "out")
WANT = [("azdtn_2_7_2", [r"\n\s*5\.1\.", r"\n\s*5\.7\."]),
        ("azdtn_2_7_3", [r"\n\s*5\.1[\.\s]"])]

for stem, pats in WANT:
    pdf = os.path.join(SRC, stem + ".pdf")
    txt = os.path.join(OUT, stem + ".txt")
    if os.path.exists(pdf):
        print(f"== {stem}.pdf md5 {hashlib.md5(open(pdf,'rb').read()).hexdigest()}")
    if not os.path.exists(txt):
        print(f"   !! {txt} missing; run the finish-layer extraction first")
        continue
    t = open(txt, encoding="utf-8").read()
    for p in pats:
        m = re.search(p, t)
        if not m:
            print(f"   !! clause pattern {p!r} not found")
            continue
        body = t[m.start():m.start() + 2600]
        sys.stdout.reconfigure(encoding="utf-8")
        print(body)
        print("-" * 70)
