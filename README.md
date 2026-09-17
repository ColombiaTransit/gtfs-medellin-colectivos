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

## What's automated vs. what needs a human right now

**Automated:**
- Pulling route/stop geometry from ArcGIS (`fetch_alimentadoras.py`).
- Scraping Sotrames' frequency tables as raw text (`scrape_sotrames.py`).
- Assembling GTFS + running it through `gtfs-validator-cli` + publishing a
  release, once `data/operators.yml` is filled in.

**Needs a human pass before this is trustworthy:**
1. **Field names.** I don't have live access to the actual ArcGIS attribute
   schema (`ROUTE_ID_FIELD`, `STOP_ID_FIELD`, etc. in `build_gtfs.py` are
   best-guess placeholders based on common Colombian open-data
   conventions). Run `fetch_alimentadoras.py` once, inspect
   `raw/rutas_alimentadoras.geojson`'s `properties`, and fix those constants.
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
4. **Running-time placeholder.** `build_gtfs.py` currently derives each
   trip's total running time from route length ÷ an assumed 18 km/h, since
   we don't have real timing data between stops. This is fine for headway
   correctness but the intermediate stop-time estimates will be rough.
   Consider running the same `pfaedle` map-matching step the Metro pipeline
   uses if you want geometry cleaned up against OSM roads too — the
   `medellin.osm.pbf` release from `gtfs-medellin`'s `update-medellin-osm.yml`
   can be reused directly instead of duplicating that workflow here.

## Setup

```bash
pip install -r requirements.txt
cp data/operators.yml.example data/operators.yml   # then fill in real routes
python scripts/fetch_alimentadoras.py
python scripts/scrape_sotrames.py                  # review raw/sotrames_scrape.json
# ... reconcile into data/operators.yml ...
python scripts/build_gtfs.py
```
