# Tax Maya

Builder: `scripts/build_gtfs_taxmaya.py` · Output: `gtfs-taxmaya.zip`

**11 routes**: the full `C23` "Integrada" family (8 routes) plus the `195`
family (3 routes). 738 real stops, 66 trips, all `frequencies.txt`-based.

## Data sources

| Source | What it gives us | Where |
|---|---|---|
| `taxmaya.com` (scraped) | Route names/descriptions, first/last-departure hours for `C23`/`C23i` only | `scripts/scrape_taxmaya.py` |
| Medellín ArcGIS transport layers (`VC_Transporte`) | Current official route geometry (per-direction) + stops (per-direction) for all 13 known Tax Maya `id_ruta`s | `scripts/download_medellin_transporte_layers.py`, `raw/medellin_raw/` |
| Gaceta Oficial N°4325 (Resolución 1042 de 2015) | Real official headway/schedule data for 9 of the 11 built routes | `data/taxmaya_route_mapping.yml` |
| Real schedule-board photos (shared directly) | Richer real per-day-type hours (not just headway) for `195`/`195i` specifically | `data/taxmaya_route_mapping.yml` |

Unlike `trscsas.com`, `taxmaya.com`'s real content is present in the plain
server-rendered HTML (a Google Sites page) — confirmed directly by
comparing real page source against what a plain HTTP client receives, so
`scrape_taxmaya.py` doesn't need a browser-rendering workaround. Its route
map "images" on the Horarios page are static screenshots, not interactive
Google My Maps embeds — there's no KML export path for this operator at
all, which is part of why ArcGIS is the only real geometry source here.

## Why `frequencies.txt`, not individual trips

Both real sources here (the Gaceta, the schedule-board photos) give real
**headway** data plus a service start/end time, not a list of literal
departure times — the correct GTFS primitive for that shape of data is
`frequencies.txt`. `stop_times.txt` is still required even for
frequency-based trips (a real bug caught during development: GTFS needs it
as the relative timing template that `frequencies.txt` then repeats).

Only the general/off-peak headway is ever used — never a peak-hour figure,
even though both sources give one (the Gaceta's "HMD" column, the photos'
"hora pico" figure). Neither source states clock-time boundaries for when
peak hours actually apply, and guessing them isn't this project's
practice.

## `sistema="8A"` — a real, independently-confirmed multi-operator corridor

All 13 of Tax Maya's ArcGIS routes share `sistema="8A"` — the same tag
found on several Coonatra routes (`243i`, `243iD`, `311i`, `311ii`,
`311iiR`, `242`, `243`). The Gaceta confirms this is real: its Ficha
Técnica pages list 5 operators under one system name ("8A Corredor San
Juan - Carrera 92"): Autobuses El Poblado Laureles, Conducciones La
América, Coonatra, Tax Maya, Metrosán. One genuinely striking piece of
corroborating evidence: `243i`'s real destination address and the
`311i`/`311ii`/`311iiR` family's shared destination address are identical
— these routes converge on one real physical hub, not just a shared
label.

## The `195` family — cross-validated across 11 years

`195` and `195i` have real screenshot data from 2026 *and* real Gaceta
data from 2015, giving a rare chance to cross-check official numbers
against current reality:

| Route | 2015 (Gaceta) | 2026 (screenshot) | Agreement |
|---|---|---|---|
| `195` hours | 5:15 AM–8:40 PM | 5:15 AM–8:36 PM | very close |
| `195` peak headway | 4 min | 3–4 min | very close |
| `195` Sunday headway | 12 min | 12 min | exact |
| `195i` hours | 4:30 AM–11:00 PM | 5:20 AM–8:40 PM | real, meaningful shift |
| `195i` peak headway | 12 min | 12 min | exact |

Given this, `195`/`195i` use the real 2026 screenshot data (richer — real
per-day-type hours, not just headway), and `195ii` uses the Gaceta data,
since no other source exists for it at all.

## The `C23` family — all Gaceta-sourced (2015)

8 routes, all matched to real ArcGIS `id_ruta`s and confirmed as Tax Maya
via the Gaceta's own "EMPRESA PRESTA SERVICIO" field:

| Gaceta route | ArcGIS match | Confidence |
|---|---|---|
| `C23-i` | Split across `C23i IZQUIERA` + `C23i DERECHA` | provisional — same left/right branch inference used for Coonatra's V3 Boquerón |
| `C23-ii` | `C23ii` | confirmed |
| `C23IAV` (Asomadera) | `C23i` "La Asomadera" | confirmed |
| `C23IPV` (El Patio) | `C23i` "El Patio" | confirmed |
| `C23iLPV` (Las Playas) | `C23i` "Las Playas" | confirmed |
| `C23IPAV` (Pedregal **Alto**) | `C23i` "Pedregal **Bajo**" | provisional — real, unexplained Alto/Bajo naming discrepancy; no other Pedregal candidate exists in either source |
| `C23iPALV` (La Palma) | `C23i` "La Palma" | confirmed |

Full detail and reasoning: `data/taxmaya_route_mapping.yml`.

## Not built — real data exists, but no match found

- **`C23_Alterna`** (ArcGIS id_ruta 90326, "San Cristóbal-La Asomadera-Centro")
  and plain **`C23`** (id_ruta 90327): the website's "Rutas urbanas"
  category, distinct from the Gaceta's "Rutas integradas" family. No
  matching Ficha Técnica page found in the 336-page Gaceta — plausibly
  these didn't exist in their current form in 2015, or existed under a
  different code, rather than a missed page.
- **`C23 AL 7`** (Alimentadora La Palma): real Gaceta data exists (Bus,
  27-31 cap, 17.20km, 3:25 AM–11 PM, headway 9/8/16 min) but **no
  confirmed ArcGIS match anywhere**. Plausibly discontinued or
  restructured out of existence by the time of the current ArcGIS
  snapshot — a real, named, government-registered route in 2015 that may
  simply no longer run today.
- A separate Moovit lookup for `C23` gave an implausible ~25-minute total
  trip duration and internally inconsistent route lists across different
  pages — not used as a source, but one interesting, unresolved thread:
  Moovit's own line index labels `C23` as **"Alimentador La Palma"**,
  which matches `C23 AL 7`'s Gaceta name almost exactly, suggesting that
  route may still be running under the plain `C23` label today.

## A more general finding, worth keeping in mind

A separate, more recent government document (a 2024-2025 Secretaría de
Movilidad management report) diagnosed the city's whole colectivo network:
of 254 routes checked, 12% don't actually operate despite being
authorized, 40% run different physical paths than authorized, and
"frequencies and schedules are not generally followed on any authorized
route" city-wide. For Tax Maya specifically, only 26 of 72 registered
vehicles (36%) were transmitting to the government's own real-time
fleet-monitoring system as of January 2024 — the system built to verify
compliance with authorized routes/frequencies. The `195`/`195i`
cross-validation above is a genuinely reassuring counterpoint for those
two routes specifically, but the Gaceta's numbers for the rest of the
fleet are not guaranteed to reflect current service.
