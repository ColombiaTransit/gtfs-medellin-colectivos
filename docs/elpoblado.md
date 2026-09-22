# Autobuses El Poblado

Builder: `scripts/build_gtfs_flex_elpoblado.py` · Output: GTFS-Flex feed

**11 routes**, built as **GTFS-Flex**. 4 of the 11 have real operating-hours
data; the rest have geometry/zone only.

## Data sources

| Source | What it gives us | Where |
|---|---|---|
| El Poblado's site (embedded Next.js JSON payload) | Precise GPS route geometry for every route, operating-hours text for most | `scripts/scrape_elpoblado.py` |

## Why GTFS-Flex

Confirmed against the real site's data model: every route has precise
geometry and (for most) operating-hours text, but **no frequency/headway
field anywhere**, and the schema's "stops" field is empty for every real
route (one route had 2 placeholder-looking entries, not real stops).
Same treatment as Sotrames: each route's corridor becomes a flexible
pickup/drop-off zone.

## Differences from the Sotrames builder

- **No `frequencies.txt` at all.** Sotrames has real (if zone-level)
  headway numbers to put there; El Poblado has none — inventing one
  would be fabrication. Each route's flex trip has a pickup/drop-off
  **window** (its operating hours) but no implied repeat interval.
- `calendar.txt` is built per distinct day-range text actually observed
  in the schedule strings ("Lunes a viernes" / "Lunes a sábado" /
  "Lunes a domingo," case-insensitive), not a single fixed pattern.

## Open question: is this the same company as "Autobuses Poblado Laureles"?

Medellín's ArcGIS transport layers contain a separate operator entry,
"Autobuses Poblado Laureles," with 16 routes under very different route
numbering (190s) than this site's route set. **Not confirmed either way**
whether these are the same company under different branding or two
distinct operators — worth resolving before assuming any ArcGIS
enhancement for this feed the way Coonatra and TRSC got.

## Known gaps / next steps
- 7 of 11 routes have geometry/zone only, no operating-hours text.
- The Poblado Laureles identity question above.
- No frequency data exists for any route — would need a different
  source entirely (the site's own data model has no field for it).
