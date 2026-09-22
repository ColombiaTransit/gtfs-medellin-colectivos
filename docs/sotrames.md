# Sotrames

Builder: `scripts/build_gtfs_flex_sotrames.py` · Output: GTFS-Flex feed

**34 routes**, built as **GTFS-Flex**, not regular GTFS.

## Data sources

| Source | What it gives us | Where |
|---|---|---|
| Sotrames' published Google My Maps (all 34) | Real, detailed line geometry — confirmed via `scripts/fetch_sotrames_kml.py` that **zero** of them have stop-point markers | `raw/sotrames_kml/` |
| `sotrames.com.co/rutas/` (scraped) | Route names + zone-level schedule tables | `scripts/scrape_sotrames.py` |
| Zone-level schedule reconciliation | Which published table was used per zone, and why per-route matching wasn't attempted | `data/sotrames_zones.yml` |

## Why GTFS-Flex

Every one of Sotrames' 34 published routes has real line geometry but no
stop points at all — confirmed across the full set, not a sample. Treated
as a flag-down service: each route's corridor becomes a flexible
pickup/drop-off zone (a buffered polygon around the route line,
`CORRIDOR_BUFFER_M` — an **assumed** catchment width, not a measured
fact) rather than a sequence of fixed stops.

## What's real vs. approximated

- **Route geometry**: real, from Sotrames' own published maps.
- **Schedule (hours, pico/valle headway)**: real numbers, but applied at
  **zone level** (Itagüí/Envigado/Sabaneta), not per-route — every trip
  built this way is marked `provisional: true`, though the underlying
  numbers are genuine Sotrames data, just not route-specific.
- **`Circular_Sur_303`**: geometry only — no schedule found anywhere, no
  trips built for it at all.
- **Only weekday ("Laborable") schedules exist in the source** — every
  table found is labeled "SEMANA." No Sábado/Domingo tables exist
  anywhere on the site, unlike MDO's schedule cards. This build does not
  fabricate weekend schedules.

## GTFS-Flex structure (validated against MobilityData's real
`gtfs-validator-cli`, not just assumed spec-compliant)

- `locations.geojson`: one buffered polygon per route.
- `stop_times.txt`: two location-based rows per trip (pickup-only leg,
  drop-off-only leg, same `location_id`) — required, since a single-row
  trip fails the validator's `unusable_trip` check.
- `pickup_type=2` ("must phone agency"), not `3` ("coordinate with
  driver") — `3` is explicitly forbidden alongside
  `pickup_drop_off_window` fields by the validator's
  `forbidden_pickup_type` check.

## Known gaps / next steps
- Per-route (not zone-level) schedule data, if a better source ever
  turns up.
- `Circular_Sur_303`'s schedule.
- Weekend service, if it turns out to exist somewhere not yet checked.
