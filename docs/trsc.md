# TRSC (Transportes Rápido San Cristóbal)

Builder: `scripts/build_gtfs_trsc.py` · Output: `gtfs-trsc.zip`

**21 routes, 978 stops, 554 trips**, zero validator errors, built entirely
from Medellín's official ArcGIS transport layers plus transcribed schedule
photos — no usable KML/My Maps source exists for this operator.

## Data sources

| Source | What it gives us | Where |
|---|---|---|
| Medellín ArcGIS transport layers (`VC_Transporte`) | Current official route geometry (per-direction) + stops (per-direction) for all 21 real routes | `scripts/download_medellin_transporte_layers.py`, `raw/medellin_raw/` |
| `trscsas.com/rutas/`, `/horarios/` (scraped) | Route names/website presence | `scripts/scrape_trsc.py`, `scripts/scrape_trsc_horarios.py` — `robots.txt` disallows automated access, documented in both scripts |
| Route mapping decisions | Which website route matches which real ArcGIS `id_ruta`, confidence per match | `data/trsc_route_mapping.yml` |
| Transcribed schedule photos | Real departure times, manually transcribed from horarios-page images where feasible | `data/trsc_schedule_photos.json` |

## Key structural facts (confirmed against real data, not assumed)

- Each real route has exactly 2 directional records (`Origen-Destino` /
  `Destino-Origen`), each with genuinely different geometry — not a
  reversed copy.
- Stops are also split by direction, and `nro_parada` restarts at 1 per
  direction, not counted once per route.
- Geometry coordinates are in EPSG:9377 (meters), transformed to
  EPSG:4326 via `pyproj`. Validated independently: the transformed route
  start for `id_ruta=90093` landed within ~5m of that route's own real
  stop #1 — cross-confirmed against a different layer, not just "ran
  without error."
- The Paradas layer used (`vc_transporte_parada`, layer 5) matched
  42/42 TRSC routes, vs. 34/42 for the older `VM_Movilidad` layer —
  confirmed the richer of the two. Its `nombre` field is ~0.03%
  populated citywide (unusable) — real street `direccion` is used as
  `stop_name` instead.
- The two "Rutas de transporte publico" ArcGIS layers
  (`VC_Transporte/6` and `VM_Movilidad/2`) are confirmed
  byte-for-byte identical — only one is used.

## What's provisional

Several routes' identity and/or schedule-photo assignment rest on
shared-name assumptions, geographic plausibility, or visual map
comparison, not independent confirmation — full detail per route in
`data/trsc_route_mapping.yml`. The build writes
`PROVISIONAL_DATA_WARNING.txt` alongside the feed listing exactly which
routes carry that caveat, rather than embedding it silently in the GTFS
files themselves.

Notable individual resolutions:
- `90086` "Palmitas-Centro" — not on the website at all, resolved via
  ArcGIS + an orphan "255 PALMITAS" schedule photo.
- `90372`/`90373` "Metrocable La Aurora Estación Estadio" — also not on
  the website, resolved via ArcGIS + an "A.E. AURORA ESTADIO" photo
  column.
- `90092`/`90093` — both share one real Google My Maps ("Ruta 255 A
  Moravia"), confirmed by visual map comparison, not text matching alone.

## Trips are only built where a schedule was actually transcribed

`trips.txt`/`stop_times.txt` exist only for routes whose assigned
schedule photo has `"transcribed": true` in
`data/trsc_schedule_photos.json`. Several routes have a photo assigned
that was deliberately left untranscribed — `COLORED_GRID_CARCEL`,
`AE_AURORA_ESTADIO`, `VEH_GRID` — complex multi-column images where
reconstructing exact values from memory carried real error risk. Those
routes, and any with no schedule photo at all, get real
`stops.txt`/`shapes.txt` geometry but no trips — spatial data only, the
same "don't fabricate a schedule" policy used throughout this project
(e.g. Coonatra's Floresta-San Juan).

**Direction-symmetry assumption**: transcribed photos give one departure-
time list each, not one per direction — applied to both directions
equally, a simplification not independently confirmed per direction.

## Known gaps / next steps
- Untranscribed photos (`COLORED_GRID_CARCEL`, `AE_AURORA_ESTADIO`,
  `VEH_GRID`) could still be transcribed later if worth the effort.
- `HUECO_PAJARITO` vs `PARQUE_METRO_PAJARITO` column ambiguity for
  `90085` unresolved.
- No confirmed schedule for several routes at all: `90081`, `90083`,
  `90088`–`90091`, `90347`, `90349`, `90353`, and more.
