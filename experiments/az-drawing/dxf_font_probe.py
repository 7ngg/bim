# -*- coding: utf-8 -*-
import io, ezdxf
out = io.open("probe3.txt", "w", encoding="utf-8")
def p(*a): out.write(" ".join(str(x) for x in a) + "\n")

doc = ezdxf.new("R2010", setup=True)
p("=== text styles ezdxf setup=True creates, and the font each names ===")
for s in doc.styles:
    p("  %-14s font=%-16s bigfont=%r" % (s.dxf.name, s.dxf.font, getattr(s.dxf, "bigfont", "")))

p("")
p("=== can a style name a TrueType font instead of an SHX? ===")
st = doc.styles.add("ARCH-TXT", font="isocpeur.ttf")
p("  style ARCH-TXT font =", st.dxf.font)
try:
    st.set_extended_font_data(family="ISOCPEUR", italic=False, bold=False)
    p("  extended font data (XDATA ACAD family name) set OK")
except Exception as e:
    p("  extended font data FAILED:", e)
doc.modelspace().add_mtext("MƏTBƏX", dxfattribs={"style": "ARCH-TXT"})
doc.saveas("e_ttf.dxf")
d2 = ezdxf.readfile("e_ttf.dxf")
p("  round trip: style font =", d2.styles.get("ARCH-TXT").dxf.font,
  "| text =", repr(d2.modelspace()[0].text))

p("")
p("=== does ezdxf ship SHX shape files it can render glyphs from? ===")
try:
    from ezdxf.fonts import fonts
    p("  ezdxf.fonts.fonts imported OK")
    for name in ["txt.shx", "isocp.shx", "simplex.shx", "romans.shx", "arial.ttf", "isocpeur.ttf"]:
        try:
            ff = fonts.find_font_face(name)
            p("  %-14s -> %s" % (name, ff))
        except Exception as e:
            p("  %-14s -> lookup error %s" % (name, e))
except Exception as e:
    p("  import failed:", e)

out.close()
print("done")
