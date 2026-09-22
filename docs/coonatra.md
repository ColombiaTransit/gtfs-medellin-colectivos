# Coonatra

Builder: `scripts/build_gtfs_coonatra.py` · Output: `gtfs-coonatra.zip`

Coonatra's feed is built from **three families**, each sourced differently, joined
into one feed: the original Calasanz-Boston branches (website + KML + PDF),
two ArcGIS-only families with no website presence at all (Floresta-San Juan,
Circular Coonatra), and a handful of routes enhanced or entirely filled in
with data from Medellín's official ArcGIS transport layers and a 2015
government resolution. **17 routes** as of the last build: 768 real stops,
697 trips.

## Data sources

| Source | What it gives us | Where |
|---|---|---|
| `coonatra.com` (scraped) | Route names/descriptions per page, some `Google My Maps` embeds (`mid=`) | `scripts/scrape_coonatra.py` |
| Coonatra KML exports | Real route geometry + named landmark stops, one line per route (not split by direction) | `scripts/fetch_coonatra_kml.py`, `raw/coonatra_kml/` |
| `Frecuencias-rutas-Calasanz.pdf` | Real literal departure times for the Calasanz-Boston family (uploaded directly, not scraped) | `scripts/parse_coonatra_pdf.py` |
| Medellín ArcGIS transport layers (`VC_Transporte`) | Current official route geometry (per-direction) + stops (per-direction), for routes matched to a real `id_ruta` | `scripts/download_medellin_transporte_layers.py`, `raw/medellin_raw/` |
| Gaceta Oficial N°4325 (Resolución 1042 de 2015) | Real official headway/schedule data for 3 routes, from a 336-page municipal gazette uploaded directly (PDF, scanned/OCR'd) | `data/coonatra_gaceta_2015_frequencies.yml` |

## Route families

### Calasanz-Boston (the original family)
- **`310`, `311`**: real KML-derived landmark stop names (e.g. "Plaza La
  Alpujarra"), but **geometry now comes from ArcGIS's real per-direction
  lines**, not the single merged KML line. Cross-checking the KML against
  ArcGIS confirmed the KML's Origen-Destino direction matches closely
  (~3m average) but Destino-Origen diverges significantly for some
  branches (up to ~280m average) — Coonatra's KML only traces one line per
  route, which can't represent a real one-way-street return path that
  differs from the outbound one. Each real stop is assigned to whichever
  direction's real ArcGIS line it's actually closest to (not forced onto
  both) — an earlier version that projected every stop onto every
  direction produced snap distances over 1500m for stops that only
  genuinely belong to one direction.
- **`310 Rosal`**: upgraded from flex-only to real ArcGIS stops (id_ruta
  90363, confident name match on "Rosal"/"Rosales").
- **`310 Metro Rosal`**: still flex-only — no ArcGIS match exists anywhere
  in Coonatra's 17 official routes (confirmed via `sistema` field
  cross-checks too).
- **`Metro 311-i`, `Metro 311-ii`**: matched to ArcGIS `311i` (id_ruta
  90324) and `311iiR` (id_ruta 90361) respectively. The `311iiR` match is
  confirmed via a genuinely strong signal: the KML's internal placemark
  name was `"RUTA 311ii Rosales"`, and the official codigo `311iiR`
  structurally decomposes into exactly that (311ii + R for Rosales) — not
  just a similar-sounding name. `Metro 311-i`'s ambiguity between ArcGIS's
  `311i` and `311ii` (both plausible "Santa Lucia" family candidates) was
  resolved by the project owner's own judgment call, not independently
  re-derived.
- Known correction: `scrape_coonatra.py` has a `KNOWN_MID_SWAPS` fix for
  "Metro 311-ii" ↔ "310 Metro Rosal" — their `mid` map-embed IDs were
  swapped on Coonatra's own website.

### Floresta-San Juan (242/243 family)
Never appeared on the website scrape at all — discovered entirely through
Medellín's `sistema="8A"` field, a real multi-operator corridor tag shared
with Tax Maya (confirmed via Gaceta Oficial N°4325, which names 5 operators
under this one sistema: Autobuses El Poblado Laureles, Conducciones La
América, Coonatra, Tax Maya, Metrosán).
- `242 Divisa`, `242 Quiebra`, `243 Divisa`, `243 Quiebra`: real ArcGIS
  stops/geometry, but **no schedule source exists** — spatial data only.
- `243i Floresta`, `243iD Floresta Directa`: same treatment as above, plus
  **real frequency data** from the Gaceta (see below).

### Circular Coonatra
The corresponding website page was genuinely ambiguous (6 names, 2
schedule blocks, 3 map embeds — could not be cleanly paired). Built
**directly from ArcGIS data instead**, bypassing the website's tangled
pairing entirely: `300`, `301`, `303`, `300 DIR-80`, `301 DIR-80`. All
spatial-only — no schedule source resolved for this family.

## Gaceta Oficial N°4325 (2015) — real frequency data for 3 routes

A citizen uploaded this 336-page municipal gazette directly (containing
Resolución 1042 de 2015, a system-wide route restructuring). It has
individual "FICHA TÉCNICA" pages per route with real headway/schedule
data — but it's **11 years older than the ArcGIS layers**, so per the
project owner's explicit direction: **ArcGIS geometry is trusted over the
Gaceta's stated route length**, but the Gaceta's real frequency numbers
are still paired with routes we've already built from ArcGIS.

| Route | Gaceta length | ArcGIS-calculated length | Confidence |
|---|---|---|---|
| `243-i` | 4.07 km | 3.4–4.5 km | **confirmed** — lengths agree well |
| `243-iD` | 5.58 km | 2.9–3.1 km | **provisional** — real, unexplained ~2x gap |
| `311-ii` | 10.90 km | ~4.35 km | **provisional, weakest** — the Gaceta's own route *name* ("Calasania-Campo Verde-Estación Santa Lucía") doesn't match our route's identity ("Rosales") at all; this pairing rests on codigo+operator alone, and may actually describe the different, still-unbuilt base `311ii` route (ArcGIS id_ruta 90325) instead |

Only the Gaceta's "DÍA" (normal) headway column is used, never "HMD"
(likely peak-hour) — the Gaceta never states clock-time boundaries for
when peak hours apply, and guessing them isn't this project's practice.
Full detail and reasoning: `data/coonatra_gaceta_2015_frequencies.yml`.

These 3 routes use `frequencies.txt` (real weekday/Saturday/Sunday
service via `DiaHabil`/`Sabado`/`Domingo` service_ids), unlike the rest of
the feed which uses a single `Diario` service with literal departure-time
trips. "Festivo" (holidays) isn't modeled as its own service — it would
need `calendar_dates.txt` with real Colombian holiday dates, and its
values matched Sunday's exactly in every route observed anyway.

## A more general finding, worth keeping in mind

A separate, more recent government document (a 2024-2025 Secretaría de
Movilidad management report) diagnosed the city's whole colectivo network:
of 254 routes checked, 12% don't actually operate despite being
authorized, 40% run different physical paths than authorized, and
**"frequencies and schedules are not generally followed on any authorized
route"** city-wide. This means the Gaceta's frequency numbers, while real
and official, are not guaranteed to reflect actual current service — this
is a systemic, government-acknowledged gap, not specific to Coonatra.

## Known gaps / next steps
- `310 Metro Rosal`: no ArcGIS match found anywhere.
- `242 Divisa`, `242 Quiebra`, `243 Divisa`, `243 Quiebra`: real stops,
  still no schedule source.
- All 5 Circular Coonatra routes: real stops, still no schedule source.
- The rest of the 336-page Gaceta hasn't been searched for other Coonatra
  routes outside the 8A system (e.g. `300`/`301`/`303` family) — worth
  checking if time permits.
