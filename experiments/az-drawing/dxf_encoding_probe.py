# -*- coding: utf-8 -*-
import io, ezdxf
from ezdxf.lldxf.encoding import has_dxf_unicode, decode_dxf_unicode

BS = chr(92)  # backslash
out = io.open("probe2.txt", "w", encoding="utf-8")
def p(*a): out.write(" ".join(str(x) for x in a) + "\n")

AZ   = "YAŞAYIŞ OTAĞI"
FULL = "ƏĞİıÖŞÜÇ əğıiöşüç"
AREA = "16,06 m²"
TXT  = AZ + BS + "P" + FULL + BS + "P" + AREA
ESC  = (BS + "U+0259").encode("ascii")

p("MTEXT string under test:", repr(TXT))
p("")
p("=== 1. round trip at each DXF version, ezdxf default code page ===")
for ver in ["R2000", "R2004", "R2007", "R2010", "R2018"]:
    doc = ezdxf.new(ver, setup=True)
    doc.modelspace().add_mtext(TXT)
    fn = "a_%s.dxf" % ver
    doc.saveas(fn)
    raw = open(fn, "rb").read()
    t = ezdxf.readfile(fn).modelspace()[0].text
    p(ver, "| file encoding =", doc.encoding,
      "| $DWGCODEPAGE =", doc.header.get("$DWGCODEPAGE"),
      "| lossless =", t == TXT,
      "| raw bytes contain U+escape =", ESC in raw,
      "| raw bytes contain utf8 schwa =", "ə".encode("utf-8") in raw)
    p("      read back:", repr(t))

p("")
p("=== 2. R2000 forced to ANSI_1254 (Turkish code page) ===")
doc = ezdxf.new("R2000", setup=True)
doc.header["$DWGCODEPAGE"] = "ANSI_1254"
doc.encoding = "cp1254"
doc.modelspace().add_mtext(TXT)
doc.saveas("b1254.dxf")
t = ezdxf.readfile("b1254.dxf").modelspace()[0].text
p("lossless =", t == TXT)
p("      read back:", repr(t))

p("")
p("=== 3. can ezdxf decode the U+ escape on demand? ===")
t2000 = ezdxf.readfile("a_R2000.dxf").modelspace()[0].text
p("has_dxf_unicode :", has_dxf_unicode(t2000))
d = decode_dxf_unicode(t2000)
p("decoded         :", repr(d))
p("decoded == orig :", d == TXT)

p("")
p("=== 4. code page coverage of the Azerbaijani Latin alphabet ===")
chars = "ƏəĞğİıÖöŞşÜüÇç"
p("alphabet under test:", chars)
for cp in ["cp1252", "cp1254", "cp1250", "cp1251", "iso8859-9", "cp857", "utf-8"]:
    miss = ""
    for c in chars:
        try:
            c.encode(cp)
        except UnicodeEncodeError:
            miss += c
    p("%-10s missing: %s" % (cp, miss if miss else "(none)"))

p("")
p("=== 5. the superscript-two used by every area string ===")
for cp in ["cp1252", "cp1254", "cp1251"]:
    try:
        p("%-8s m2 sign -> %r" % (cp, "²".encode(cp)))
    except Exception as e:
        p("%-8s m2 sign -> FAILS: %s" % (cp, e))

p("")
p("=== 6. Cyrillic (Russian room names) at R2000 ===")
RU = "ЖИЛАЯ КОМНАТА"  # ЖИЛАЯ КОМНАТА
doc = ezdxf.new("R2000", setup=True)
doc.header["$DWGCODEPAGE"] = "ANSI_1251"
doc.encoding = "cp1251"
doc.modelspace().add_mtext(RU)
doc.saveas("c_ru.dxf")
t = ezdxf.readfile("c_ru.dxf").modelspace()[0].text
p("cp1251 R2000 lossless =", t == RU, "|", repr(t))
doc = ezdxf.new("R2000", setup=True)
doc.modelspace().add_mtext(RU)
doc.saveas("c_ru_default.dxf")
t = ezdxf.readfile("c_ru_default.dxf").modelspace()[0].text
p("cp1252 R2000 lossless =", t == RU, "|", repr(t))
doc = ezdxf.new("R2010", setup=True)
doc.modelspace().add_mtext(RU)
doc.saveas("c_ru_2010.dxf")
t = ezdxf.readfile("c_ru_2010.dxf").modelspace()[0].text
p("       R2010 lossless =", t == RU, "|", repr(t))

p("")
p("=== 7. pure-ASCII English tag at R2000 ===")
EN = "LIVING / KITCHEN" + BS + "P16.06 m2"
doc = ezdxf.new("R2000", setup=True)
doc.modelspace().add_mtext(EN)
doc.saveas("d_en.dxf")
t = ezdxf.readfile("d_en.dxf").modelspace()[0].text
p("ASCII R2000 lossless =", t == EN, "|", repr(t))

out.close()
print("done")
