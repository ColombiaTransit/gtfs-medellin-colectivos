# 2025 urban bus route schedule QA and ArcGIS linkage — 18 November 2026

## Scope and source integrity

The official original ASTREA texts for 202550076150, 202550076162, 202550079848 and 202550079865 were fetched and their timetable tables extracted in GitHub Actions #44268129743 and #44268663729. The source register holds 84 resolution + GTPC + user-code entries. This review distinguishes source semantics from true missing timetable data and avoids treating modern route aliases or direction rows as duplicated GTFS services.

The row-by-row classification is stored in `2025_astrea_route_schedule_qa_classification.csv`. The original values remain in `2025_astrea_official_route_timetable_candidates.csv` and are **not production approved**.

| Official act / system | Total source entries | Three-day interval tables | Other source treatment |
|---|---:|---:|---|
| 202550076150 Salud-Hotelera | 6 | 6 | `308-2` and `309-2` explicitly do not operate on Saturdays or Sundays/holidays |
| 202550076162 Castilla / Conaltracoop | 28 | 18 | 8 trunk-corridor entries lack standalone times and intervals; TRONCAL 65 and TRONCAL 73 have hours but no interval rows |
| 202550079848 Metrosan | 16 | 8 | 8 return-direction rows have empty cells paired with populated outbound direction records; no doubling |
| 202550079865 Rápido San Cristóbal | 34 | 16 | 7 veredal services have hours without intervals; 11 corregimental services have explicit fixed departure lists (8 in table 5, 3 in source master table 3) |

**Total: 48** records with three sets of published interval cells, **8** paired Metrosan direction rows without repeated figures, **11** corregimental fixed-departure records, **8** trunk-corridor records with no standalone times, and **9** entries with a published service window but no extracted interval (2 troncal and 7 veredal). These categories are not mutually identical to route counts.

## Specific recovered source evidence

The normalization previously missed three Palmitas schedules inside the original **202550079865 master table 3**. They have been recovered in the `fixed_departures_master_table` field, with re-generation logic updated to preserve them:

| Source user code | Operator route | Days | Printed departure times |
|---|---|---|---|
| `256-9` (GTPC 23726) | La Sucia–Suiza–Tejar–San Cristóbal | Monday–Friday | 05:30 |
| `256-10` (GTPC 23727) | San Cristóbal–Tejar–Suiza–La Sucia | Monday–Friday | 17:30 |
| `256-1v` (GTPC 23728) | Interveredal Palmitas | Sunday | 08:00, 12:00, 16:00 |

These are **fixed departures**, not headway intervals. The municipality's own schedule may be converted into departure-based GTFS later only after stop sequences, route identification, operating calendars, and legal supersession checks.

The interval cells include explicit `0`, `No opera`, `N/A`, and blank values. These are distinct meanings. A zero is not a valid positive GTFS headway, and no-service should remain no-service. The three numeric interval columns per day are official published period-specific **maximum despacho intervals**, not a clock-based trip schedule. Exact peak-period clock definitions remain an independent requirement.

## Salud-Hotelera / ArcGIS identifiers

All six official rows have recorded hour and interval table data. The modern 2025 legal user codes have been cross-linked as route identity **candidates** against the earlier ArcGIS snapshot in `2025_salud_hotelera_arcgis_code_mapping.csv`:

- Legal `304` ⇄ ArcGIS 90009 / 304; legal `305` ⇄ ArcGIS 90010 / 305
- Legal `308-1` ⇄ ArcGIS 90011 / 308; legal `308-2` ⇄ ArcGIS 90012 / 308D
- Legal `309-1` ⇄ ArcGIS 90013 / 309; legal `309-2` ⇄ ArcGIS 90014 / 309D

Operator names and route titles support these code-identity candidates; **shape/direction geometry has not yet been independently checked**. `304` and `305` share GTPC 82801 but are separate routes identified by *GTPC plus user code*. Never generate an additional service merely because the legal code has changed.

An example from the official Salud-Hotelera timetable: `308-1` operates **04:15–20:00 Monday–Friday**, **04:15–19:00 Saturday**, **05:55–17:55 Sunday/holiday** with published three-period maximum intervals **8/15/8**, **10/18/10**, and **13/24/13 minutes** respectively. Those three intervals must not be extrapolated into a frequency-based feed without knowing the corresponding period boundaries. `308-2` shows weekday-only 16:00–19:00 and explicit non-operation during other day types.

## What is closed vs open

**Closed at source-structure level:** all 84 rows categorized; the missed three Palmitas fixed schedules recovered; six Salud-Hotelera identity candidates reconciled; paired Metrosan returns, trunk corridors, rural fixed departures and source zero-values preserved as distinct semantics.

**Still open:** source page-level numeric acceptance across all acts, actual applicability of later modifying resolutions (post-September 2025 through 2026), precise peak/midday period boundaries, shape/stop/agency mapping, and whether the 9 window-only entries have other legally defined timetable annexes. Do not treat the 48 three-day entries as 48 fully validated present-day GTFS routes.

**No modifications** to GTFS production generation, frequencies, calendar, or services. Resolución 202250106966 and 082 PILOTO remain parked pending a direct original source.
