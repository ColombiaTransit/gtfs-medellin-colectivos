# Medellín 47 legacy-route crosswalk — official frequencies and operating windows (2026-11-19)

This is a source-first reconciliation of the **47** archived ArcGIS route identities in the existing 252-route coverage audit marked `first_resolve_new_2025_code_to_old_ArcGIS`. It does **not** change GTFS, assume a candidate source applies to a different branch, or convert maximum interval values into observed departures.

## Results

- Input legacy ArcGIS IDs: **47**; source: `medellin_252_coverage_with_historical_fallback.csv`.
- Explicit source candidate codes from existing original 2025 legal register and the pre-existing 66-code ambiguity queue are written to [47-route reconciliation CSV](medellin_47_legal_frequency_window_reconciliation_2026-11-19.csv).
- Crosswalk statuses: `MULTIPLE_CANDIDATES` **7**; `NO_ROUTE_LEVEL_CROSSWALK` **37**; `CANDIDATE_NOT_VERIFIED` **2**; `CODE_NAME_CONFLICT` **1**.
- 5 legacy IDs have directly referenced official legal-source rows with raw 3-day frequencies and operating windows **as candidate evidence, not safely assigned timetables**.
- 9 legacy IDs appear in the previously compiled unmatched-source schedule candidates list; source-daytype completeness stays attached to the legal code and may not be transferred until direction identity is verified.

## Source hierarchy and constraints

1. Use the already recovered **2025 official decisions** (Castilla `202550076162`, Rápido `202550079865`, Palenque `202550088689`, Metrosan `202550079848`) to select published service windows, official period-specific maximum dispatch intervals, fixed departures or service counts *only for the correctly matched legal variant*. Do not fetch those original documents again.
2. A legal GTPC/direction record with missing numeric cells does not mean the route has no departures; shared service and paired directions must not be doubled.
3. `90124 / 289` is specifically **blocked**: the old GIS names Pilarica Calle 96 while the official 2025 289 names Picacho; same route number is not enough to import its official `6|10|8` weekday period maxima and `04:00|22:00` hours.
4. Distinguish historic Anillo/Carrera 65–73 geometry from timed `TRONCAL 65/73` source entries; the latter cannot automatically be duplicated as timetables on each old GIS ring feature.
5. The Rápido San Cristóbal **operator's already captured exact website/photo schedules** take precedence over third-party approximations for actual departure times; match them to legal variants using the existing photo crosswalk, without new website scraping.
6. **195II Tax Maya** and **082 V-LA PILOTO** are parked and are outside this work batch. Do not open new source-retrieval work for them.
7. Where only PP/PVM/PVE maximum interval categories are available, preserve official legal values and the already accepted *provisional* PP/PVM clock model in separate fields. An original legal headway is not itself a first/last departure from every terminus.

## Next pass (no repeated source scraping)

- Resolve the **candidate identities** first with original legal code, route-name, direction and historic geometry. In particular: Palenque 250/253 branches; Castilla 254/261/263/306; Rápido 255/255V branches; Metrosan 225i-2/227iB-2; and the special Anillo/Carrera 65/73 features.
- Only promote *unambiguous* identity matches into a per-day source frequency/window register, preserving source type, legal decision number, PP/PVM/PVE periods, no-service values and exceptional departures. Keep every ambiguous route excluded from GTFS automatic imports.
- Rerun the coverage audit after actual identity checks, rather than reporting these 47 as automatically completed just because they have a candidate.

## Continuation: original daytype source staging (19 November 2026)

The existing original official daytype table was reused **without document downloading** and staged in [medellin_47_legal_source_daytypes_staging_2026-11-19.csv](medellin_47_legal_source_daytypes_staging_2026-11-19.csv), comprising **276 source/daytype records for 92 distinct legal route codes** across the four relevant resolutions:

| Official decision | Legal service codes | Weekday/Saturday/Sunday-holiday rows |
| --- | ---: | ---: |
| 202550076162 (Castilla) | 30 | 90 |
| 202550079848 (Metrosan) | 8 | 24 |
| 202550079865 (Rápido San Cristóbal) | 34 | 102 |
| 202550088689 (Palenque) | 20 | 60 |
| **Total** | **92** | **276** |

Each row preserves **first/last published service window**, maximum **PP/PVE/PVM dispatch interval** where present, **fixed departures or number of daily services** when the official source does not provide minute headways, source URL, original QA level and unapproved production status. PVE and PP/PVM boundaries remain in their separate source/model fields; no replacement for missing timing data is assumed.

The 47-old-route work queue has **10 old ArcGIS IDs referenced by 11 legal code rows** in this staged source crosswalk; these are still **candidate identity relations**, not 10 newly finished legal schedule imports. The remaining source codes should not be force-fitted to historic shapes. If a legal code is absent from the candidate-ID list, its official frequency is nevertheless safely retained under its *legal code*, ready for subsequent actual match checks.

**Immediate follow-up:** compare the 47 legacy geometry/variant identities to the 92 source codes, respecting specific route restructurings. Rápido operator timetable/photo evidence and special veredal service counts must not be flattened into minute headways; the old ArcGIS Anillo rings must not each get a duplicate TRONCAL 65/73 schedule. Both parked routes 195II and 082 PILOTO remain excluded. No GTFS generator change.
