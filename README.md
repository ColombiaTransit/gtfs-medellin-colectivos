# gtfs-medellin-colectivos

Companion pipeline to [`gtfs-medellin`](https://github.com/ColombiaTransit/gtfs-medellin),
generating a GTFS feed for Medellín's **alimentador/colectivo** buses — the
SITVA feeder buses that connect neighborhoods to Metro and Metroplús
stations, operated by private companies (Sotrames, SAO6, Masivo de
Occidente) rather than by Metro de Medellín directly.

## Why this is a separate pipeline, not a patch to `gtfs-medellin`

`gtfs-medellin` downloads an **already-complete GTFS** from Metro de
Medellín and improves it (better shapes via pfaedle, holiday calendar,
validation). Colectivos have no equivalent ready-made feed — the data is
split across two source types that have to be joined:

| What we need | Source | Format |
|---|---|---|
| Route geometry, stops | [Rutas Alimentadoras](https://datosabiertos-metrodemedellin.opendata.arcgis.com/datasets/890bb205825b44019510b8d8954a7e81_2) / [Paradas Alimentadoras](https://datosabiertos-metrodemedellin.opendata.arcgis.com/datasets/5ab395db7e30403bb85fe599d6af66bd_0) | ArcGIS hosted feature layers |
| Operating hours, headways | Operator sites (Sotrames, SAO6, MDO) | Scattered HTML, no public API |

No one publishes exact departure times for these routes — only headways
("PICO 4 y 5 MINUTOS" / "VALLE 6 MINUTOS"). So the feed uses
**`frequencies.txt`** (`exact_times=0`) instead of a fully enumerated
`stop_times.txt`, which is standard GTFS practice for headway-based service.

## Pipeline

```
scripts/fetch_alimentadoras.py   ArcGIS item -> FeatureServer -> GeoJSON
                                  (routes + stops, fully automated)

scripts/inspect_fields.py        Prints both layers' schema (for CI logs
                                  and for catching future schema drift)

scripts/scrape_sotrames.py       Sotrames' static HTML -> raw route/table
                                  dump for manual reconciliation
                                  (SAO6 + MDO are JS SPAs - see below)

data/operators.yml                Human-curated: route_id -> operator,
                                  headways, first/last departure per
                                  day type. This is the file you edit
                                  when a route or schedule changes.

scripts/build_gtfs.py            Joins geometry + operators.yml ->
                                  gtfs-medellin-colectivos.zip

.github/workflows/
  build-colectivos-gtfs.yml       Weekly build + MobilityData validation
                                  + GitHub Release, same pattern as the
                                  Metro pipeline's validate-gtfs.yml
```

## What's automated vs. what needs a human pass

**Automated:**
- Pulling route/stop geometry from ArcGIS (`fetch_alimentadoras.py`). Confirmed
  live schema: routes have `ruta` (directional itinerary id, e.g. `C3-004P`),
  `linea` (bidirectional route name), `cuenca` (basin), `SHAPE__Length`.
  Stops have `ruta` (join key), `globalid` (unique id), `parada`/`label`
  (name). `build_gtfs.py` is wired to these real field names already.
- `scripts/inspect_fields.py` runs in CI right after the fetch step and
  prints both layers' schema into the Action log, so future schema drift
  shows up immediately instead of as a silent join failure.
- Scraping Sotrames' frequency tables as raw text (`scrape_sotrames.py`).
- Assembling a structurally valid GTFS (`agency/routes/stops/shapes/trips/
  stop_times/frequencies/calendar.txt`) + running it through
  `gtfs-validator-cli` + publishing a release, once `data/operators.yml` is
  filled in.

**Needs a human pass before this is trustworthy:**
1. **Stop order along a route is now computed from geometry, not
   guessed.** Each stop is snapped onto its route's own line (nearest
   point on the polyline) and ordered by distance travelled along that
   line — replacing the earlier `objectid` proxy, which had no real basis
   (ArcGIS doesn't expose a sequence field at all). Stops landing more
   than `SUSPICIOUS_SNAP_DIST_M` (150 m) from their route's line are
   flagged in the build log rather than silently trusted — useful for
   catching a bad `ruta` join or a genuinely mislabeled stop. Verified
   against both a straight-line and a curved synthetic route with
   deliberately scrambled `objectid` values; the geometric order came out
   correct in both cases.
2. **SAO6 and MDO are JavaScript single-page apps** — their route/timetable
   pages don't return usable HTML to a plain HTTP fetch, unlike Sotrames.
   To get their headway data you'll need one of:
   - a browser-automation scrape (Playwright/Selenium) as a separate script, or
   - check whether either site calls a JSON API under the hood (open dev
     tools → Network tab while loading `/rutas`), or
   - fall back to manually transcribing their published schedules into
     `data/operators.yml` (there aren't that many routes).
3. **Reconciling Sotrames' scrape output.** The site's HTML doesn't cleanly
   pair each route name with its frequency table once flattened to text —
   `scrape_sotrames.py` dumps both lists in document order for a human to
   match up by eye against the live page, then transcribe into
   `data/operators.yml`.
4. **Running-time placeholder.** Stops within a trip are spaced evenly across
   a placeholder total running time (route length ÷ an assumed 18 km/h),
   since we don't have real timing data between stops. This is fine for
   headway correctness (that's what `frequencies.txt` controls) but the
   individual `stop_times.txt` clock times are rough. Consider running the
   same `pfaedle` map-matching step the Metro pipeline uses if you want
   geometry cleaned up against OSM roads too — the `medellin.osm.pbf`
   release from `gtfs-medellin`'s `update-medellin-osm.yml` can be reused
   directly instead of duplicating that workflow here.
5. **Two directions per route ≠ one config entry.** `ruta` values like
   `C3-004P` and `C3-004B` are separate directional itineraries of the same
   logical line — each needs its own `data/operators.yml` entry (they'll
   usually share the same headway/hours, just different `route_id`s and
   shapes).
6. **Operator attribution, fully confirmed and now measured against the
   complete route list.** `inspect_fields.py` dumps every distinct `ruta`
   value from the full ArcGIS pull (not just samples) and diffs it
   against `data/operators.yml`. Result: there are exactly **46 distinct
   routes total** (15 cuenca-3, 31 cuenca-6) — matching MDO and SAO6's own
   published route counts exactly. Sotrames genuinely isn't part of this
   layer. `data/operators.yml.example` now has all 46, correctly
   attributed, with empty `day_types` (no schedule data captured for
   either operator yet).
7. **One route-code mismatch, unresolved.** SAO6's own `/rutas` page lists
   `C6-014A` and `C6-015`; the ArcGIS layer instead has `C6-015A` and
   `C6-016A` for that same numeric neighborhood — these don't overlap.
   Flagged inline in `data/operators.yml.example` with a guess at which
   might correspond to which (based on numbering proximity), but not
   verified. Confirm by pulling `C6-015A`/`C6-016A`'s `linea`/`itinerario`
   text from the ArcGIS layer and comparing to SAO6's stated names.
8. **SAO6 does not publish schedule data anywhere found so far.** Checked
   an individual route page (`sao6.com.co/rutas/santa-rita-estacion-
   acevedo`) — it only has a "Mapa del Recorrido" tab (Google MyMaps
   embed) and a "Video del Trayecto" tab, plus a one-sentence description.
   No headway/timetable data. Getting SAO6's actual schedule will need a
   different source (direct contact, printed stop schedules, Metro de
   Medellín's own documentation, etc.) — there's no more of SAO6's own
   website left to check for this. MDO's individual route pages haven't
   been checked yet.
9. **Fixed a real bug: most routes have more than one ArcGIS feature row**
   (102 rows / 46 distinct routes), and `build_gtfs.py` used to process
   each row independently — silently emitting duplicate `route_id` rows
   in `routes.txt` and colliding `shape_pt_sequence` numbers in
   `shapes.txt` for every affected route. Fixed by grouping features by
   `ruta` first: rows sharing the same `sentido` are treated as split line
   segments and concatenated (ordered by `objectid`); rows with different
   `sentido` values are a genuine direction pair, and only one (the
   smallest `sentido`) is currently used, since this feed models one
   shape per `route_id` with no separate reverse-direction trip yet.
   `inspect_fields.py` now also prints, per route, how many feature rows
   it has and whether their `sentido` values repeat or differ — useful
   for spot-checking this assumption once real data is flowing.
7. `build_gtfs.py` used to infer each output file's CSV header from
   `rows[0]`, which crashed (`IndexError`) whenever a route's `day_types`
   was empty (as it now legitimately is for the MDO placeholders above,
   since no trips/stops get referenced). Fixed by using an explicit
   `FIELDNAMES` map per GTFS file instead — worth knowing if you extend
   the script and hit the same pattern elsewhere.

## Setup

```bash
pip install -r requirements.txt
cp data/operators.yml.example data/operators.yml   # then fill in real routes
python scripts/fetch_alimentadoras.py
python scripts/scrape_sotrames.py                  # review raw/sotrames_scrape.json
# ... reconcile into data/operators.yml ...
python scripts/build_gtfs.py
```
