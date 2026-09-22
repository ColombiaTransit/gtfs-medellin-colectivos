# SAO6

Builder: `scripts/build_gtfs.py` (shared with MDO) · Output:
`gtfs-medellin-colectivos.zip`

**31/31 routes exist with real geometry, but NO real schedule data has
been found anywhere.** Every `day_types` entry for SAO6 is fake
placeholder data, explicitly marked `provisional: true` in
`data/operators.yml` — built only because placeholder numbers were
requested to test the pipeline against, not because they should be
trusted as real.

This operator's full decision history lives in the **root `README.md`**,
item 8 — this file is a short pointer, not a duplicate.

## Summary

- Route/stop geometry: real, from the same `Rutas Alimentadoras` /
  `Paradas Alimentadoras` ArcGIS layers used for MDO.
- **SAO6 is a JavaScript single-page app** — its route/timetable pages
  don't return usable HTML to a plain HTTP fetch, unlike Sotrames or
  MDO's plain WordPress site. No browser-automation scrape has been
  built for it.
- Checked an individual route page directly
  (`sao6.com.co/rutas/santa-rita-estacion-acevedo`) — it only has a
  "Mapa del Recorrido" tab (Google MyMaps embed) and a "Video del
  Trayecto" tab, plus a one-sentence description. **No headway/timetable
  data exists on the site at all**, confirmed by checking, not assumed.
- One unresolved route-code mismatch: SAO6's own `/rutas` page lists
  `C6-014A`/`C6-015`; the ArcGIS layer instead has `C6-015A`/`C6-016A`
  for that same numeric neighborhood — flagged in
  `data/operators.yml.example` with a guess at the correspondence, not
  verified.

## Known gaps / next steps
- Getting SAO6's actual schedule needs a different source entirely:
  browser automation (Playwright/Selenium), checking whether the site
  calls a JSON API under the hood, direct contact with the operator, or
  manual transcription of a printed schedule if one exists.
- The `C6-014A`/`C6-015` vs. `C6-015A`/`C6-016A` naming mismatch.
