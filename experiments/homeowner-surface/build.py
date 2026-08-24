"""PROTOTYPE BUILD — inline the JSON fixtures into a single double-clickable file."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "prototype.src.html"), encoding="utf-8").read()
data = {
    "fixtures": json.load(open(os.path.join(HERE, "fixtures.json"), encoding="utf-8")),
    "standards": json.load(open(os.path.join(HERE, "standards.json"), encoding="utf-8")),
}
out = src.replace("/*__DATA__*/", json.dumps(data, ensure_ascii=False))
open(os.path.join(HERE, "prototype.html"), "w", encoding="utf-8").write(out)
print(f"prototype.html  {len(out)/1024:.0f} KB  ({len(data['fixtures']['plans'])} real plans)")
