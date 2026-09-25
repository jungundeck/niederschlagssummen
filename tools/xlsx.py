"""Minimaler XLSX-Leser (nur Standardbibliothek): liefert Zeilen eines Tabellenblatts als Listen."""
import re
import zipfile
import xml.etree.ElementTree as ET

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def _col(ref):
    n = 0
    for ch in re.match(r"[A-Z]+", ref).group():
        n = n * 26 + ord(ch) - 64
    return n - 1


def rows(path, sheet):
    with zipfile.ZipFile(path) as z:
        shared = [
            "".join(t.text or "" for t in si.iter(f"{{{NS['m']}}}t"))
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS)
        ]
        root = ET.fromstring(z.read(f"xl/worksheets/{sheet}.xml"))
    for r in root.iter(f"{{{NS['m']}}}row"):
        out = []
        for c in r.findall("m:c", NS):
            i = _col(c.get("r"))
            v = c.find("m:v", NS)
            val = None if v is None else v.text
            if val is not None and c.get("t") == "s":
                val = shared[int(val)]
            elif c.get("t") == "inlineStr":
                val = "".join(t.text or "" for t in c.iter(f"{{{NS['m']}}}t"))
            out.extend([None] * (i - len(out) + 1))
            out[i] = val
        yield out
