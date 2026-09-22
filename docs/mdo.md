# MDO (Masivo de Occidente)

Builder: `scripts/build_gtfs.py` (shared with SAO6) · Output:
`gtfs-medellin-colectivos.zip` · Scraper: `scripts/scrape_mdo.py`

**15/15 routes have real schedule data** — the only operator in this
project whose schedule required OCR rather than text scraping or manual
transcription from a photo.

This operator's full decision history lives in the **root `README.md`**,
items 8–10 — this file is a short pointer, not a duplicate, since the
root README already documents it in detail (image cropping fractions,
OCR failure/fix, verification against all 15 real downloaded images,
etc.).

## Summary

- MDO's site is plain WordPress, not a JS SPA (unlike SAO6) — but its
  per-route schedule is a **raster image** per route, not real DOM text,
  so getting the schedule out meant OCR (`pytesseract`), not HTML
  scraping.
- The first OCR attempt (whole-image + regex) failed on every route in a
  real CI run — Tesseract's reading order interleaves the two side-by-
  side panels inconsistently. Fixed by cropping each image into three
  regions **before** OCR (left panel / right panel / bottom frequency
  band), calibrated against one route's 1920×1920 image and confirmed
  to be the same template across all 15.
- `data/operators.yml` has real `day_types` for all 15 routes. Peak
  windows use a general Medellín pico/valle/noche schedule, **not**
  MDO-specific — flagged inline as an assumption pending a route-
  specific figure.
- `C3-004MD` ("Ext. Los Alpes - Mano de Dios") has much earlier last-
  departure times (~16:21–19:56) than every other route (~23:00) —
  confirmed correct, not an OCR error: it's a limited-hours extension
  route, matching the "Ext." in its name.

Route geometry comes from the same `Rutas Alimentadoras` /
`Paradas Alimentadoras` ArcGIS layers used for SAO6 — see the root
README's "Automated" section for confirmed field names and the
Cuenca 3 (MDO) / Cuenca 6 (SAO6) split.
