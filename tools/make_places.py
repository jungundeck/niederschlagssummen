#!/usr/bin/env python3
"""Erzeugt site/places.json aus dem Gemeindeverzeichnis (GV-ISys) des Statistischen Bundesamts.

Einmalig bzw. bei Bedarf ausführen:
    python3 tools/make_places.py

Quelle: © Statistisches Bundesamt (Destatis), Gemeindeverzeichnis, Lizenz dl-de/by-2-0.
Ausgabe: [[Name, Breite, Länge, Einwohner], …], absteigend nach Einwohnern.
"""
import json
import sys
import tempfile
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import xlsx  # noqa: E402

URL = ("https://www.destatis.de/DE/Themen/Laender-Regionen/Regionales/Gemeindeverzeichnis/"
       "Administrativ/Archiv/GVAuszugJ/31122024_Auszug_GV.xlsx?__blob=publicationFile&v=2")
OUT = Path(__file__).resolve().parent.parent / "site" / "places.json"


def main():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "gv.xlsx"
        req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as r:
            path.write_bytes(r.read())
        places, skipped = [], []
        for row in xlsx.rows(path, "sheet2"):
            if not row or row[0] != "60":  # Satzart 60 = Gemeinde
                continue
            name = row[7].split(",")[0].strip()  # "Kempten (Allgäu), Stadt" → "Kempten (Allgäu)"
            pop = int(row[9] or 0)
            if pop == 0:  # gemeindefreie Gebiete (Forste, Seen)
                continue
            if not (row[14] and row[15]):
                skipped.append(name)
                continue
            lon, lat = (float(v.replace(",", ".")) for v in row[14:16])
            places.append([name, round(lat, 4), round(lon, 4), pop])
    places.sort(key=lambda p: -p[3])
    OUT.write_text(json.dumps(places, ensure_ascii=False, separators=(",", ":")))
    print(f"{len(places)} Gemeinden → {OUT} ({OUT.stat().st_size // 1024} KB)")
    if skipped:
        print(f"Ohne Koordinaten übersprungen: {', '.join(skipped)}")


if __name__ == "__main__":
    main()
