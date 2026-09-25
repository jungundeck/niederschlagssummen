#!/usr/bin/env python3
"""Berechnet Niederschlagssummen (1–30 Tage) aus DWD RADOLAN SF und schreibt sie nach site/data/.

Läuft täglich per GitHub Action; lokal:
    python3 build.py && python3 -m http.server 8765 -d site   → http://localhost:8765
"""
import gzip
import json
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

BASE_URL = "https://opendata.dwd.de/climate_environment/CDC/grids_germany/daily/radolan/recent/bin/"
HERE = Path(__file__).resolve().parent
CACHE = HERE / "cache"
OUT = HERE / "site" / "data"
MAX_DAYS = 30
N = 900  # RADOLAN-Gitter 900x900, Zeile 0 = Süden
NODATA = 0xFFFF


def parse_radolan(raw: bytes) -> np.ndarray:
    """RADOLAN-Binärformat → uint16 in 0,1 mm (NODATA = keine Daten)."""
    h = raw.index(b"\x03")
    header = raw[:h].decode("latin-1")
    if "PR E-01" not in header:
        raise ValueError(f"Unerwartete Genauigkeit im Header: {header[:60]}")
    a = np.frombuffer(raw[h + 1:h + 1 + N * N * 2], "<u2").reshape(N, N)
    v = a & 0x0FFF
    v[(a & 0x4000) != 0] = 0  # negative Werte (sehr selten) → 0
    v[(a & 0x2000) != 0] = NODATA
    return v


def stamp_name(t: datetime) -> str:
    return f"raa01-sf_10000-{t:%y%m%d%H%M}-dwd---bin.gz"


def download(t: datetime):
    """SF-Datei holen (mit lokalem Cache). None, wenn sie beim DWD fehlt."""
    p = CACHE / stamp_name(t)
    if not p.exists():
        try:
            with urllib.request.urlopen(BASE_URL + stamp_name(t), timeout=60) as r:
                p.write_bytes(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            raise
    return parse_radolan(gzip.decompress(p.read_bytes()))


def exists(t: datetime) -> bool:
    req = urllib.request.Request(BASE_URL + stamp_name(t), method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=15):
            return True
    except urllib.error.HTTPError:
        return False


def latest_stamp() -> datetime:
    """Neuester verfügbarer :50-Zeitpunkt (UTC) auf dem DWD-Server."""
    now = datetime.now(timezone.utc)
    t = now.replace(minute=50, second=0, microsecond=0)
    if t > now:
        t -= timedelta(hours=1)
    for _ in range(24):
        if exists(t):
            return t
        t -= timedelta(hours=1)
    raise RuntimeError("Keine aktuelle SF-Datei gefunden")


def main():
    CACHE.mkdir(exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    end = latest_stamp()
    # Nicht überlappende 24-h-Summen, neueste zuerst
    stamps = [end - timedelta(days=i) for i in range(MAX_DAYS)]
    with ThreadPoolExecutor(6) as ex:
        days = list(ex.map(download, stamps))

    total = np.zeros((N, N), np.uint32)
    valid = np.zeros((N, N), bool)
    missing = []
    for d, (t, a) in enumerate(zip(stamps, days), start=1):
        if a is None:
            missing.append(d)
        else:
            ok = a != NODATA
            total[ok] += a[ok]
            valid |= ok
        out = np.minimum(total, NODATA - 1).astype("<u2")
        out[~valid] = NODATA
        (OUT / f"sum_{d:02d}.bin.gz").write_bytes(gzip.compress(out.tobytes(), 9))

    meta = {
        "end": end.isoformat(),
        "max_days": MAX_DAYS,
        "missing_days": missing,  # Tagesnummern (1 = jüngster Tag), die beim DWD fehlten
        "built": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    (OUT / "meta.json").write_text(json.dumps(meta))

    keep = {stamp_name(t) for t in stamps}
    for p in CACHE.iterdir():
        if p.name not in keep:
            p.unlink()
    print(f"Fertig: Stand {end:%d.%m.%Y %H:%M} UTC, fehlende Tage: {missing or 'keine'}")


if __name__ == "__main__":
    main()
