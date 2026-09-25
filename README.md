# Niederschlagssummen (DWD RADOLAN SF, 1 km)

Interaktive Karte der Niederschlagssummen über 1–30 Tage für das gesamte DWD-Radargebiet.

- `build.py` lädt die letzten 30 RADOLAN-SF-Dateien (24-h-Summen) vom DWD und schreibt
  vorberechnete Summen nach `site/data/` (`sum_01.bin.gz` … `sum_30.bin.gz`, `meta.json`).
- `site/index.html` ist eine statische Seite (Leaflet), die nur die gewählte Summe lädt.
- `.github/workflows/update.yml` führt `build.py` täglich aus und veröffentlicht `site/` auf GitHub Pages.

## Lokal testen

```bash
python3 build.py && python3 -m http.server 8765 -d site
```

Dann http://localhost:8765 öffnen. Benötigt Python 3 und numpy.

## Einrichtung GitHub Pages

1. **Öffentliches** Repository auf GitHub anlegen (GitHub Pages ist nur für öffentliche Repos kostenlos)
   und dieses Verzeichnis hochladen.
2. *Settings → Pages → Build and deployment → Source:* **GitHub Actions** wählen.
3. *Actions → Niederschlagsdaten aktualisieren → Run workflow* einmal starten (läuft auch bei jedem Push).
   Danach täglich um 06:40 UTC. Die Adresse steht anschließend unter *Settings → Pages*.
4. In `site/index.html` oben `IMPRESSUM_URL` und `DATENSCHUTZ_URL` eintragen.

Die berechneten Daten werden nicht ins Repository eingecheckt, sondern bei jedem Lauf neu erzeugt.
GitHub deaktiviert Zeitpläne in öffentlichen Repos nach 60 Tagen ohne Aktivität; der Workflow
setzt diese Frist bei jedem Lauf selbst zurück.

Laufzeit pro Tag ca. 1 Minute; für öffentliche Repos sind Actions-Minuten kostenlos.

Quelle der Radardaten: Deutscher Wetterdienst (DWD), RADOLAN SF; Kartenhintergrund © OpenStreetMap-Mitwirkende;
Leaflet (BSD-2-Lizenz, `site/vendor/leaflet/LICENSE`).
