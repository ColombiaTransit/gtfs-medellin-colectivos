# Medellín Urbanas — consolidated 252-route frequency and operating window audit (19 November 2026)

This is the **new research-level source consolidation**, overlaying the previously complete 252-ID/756-daytype audit with historical fiche QA and newly retained operator/third-party shared-family evidence. The original 18 November CSVs remain unchanged for reproducibility. No GTFS generator change or source-to-production promotion.

## Verified reproducibility checks

- **252** unique historical ArcGIS IDs, **756** associated daytype rows (weekday, Saturday, Sunday/holiday)
- Previous audit: **49** legacy route IDs had both frequency and service-window candidates for all three daytypes; **50** had at least one daytype
- Additional **34** 2015 **historical-only provisional fallback** routes found in the 70-case visual fiche QA and subsequent 13/10/11 review; no claim of current legal validity
- Combined **83 / 252** have both fields across all three daytypes **if explicitly labelled 2015 provisional research fallbacks are accepted**. They are NOT 2026 verified scheduled routes. This total intentionally excludes shared-family data where no per-variant/daytype service window is confirmed
- Remaining original **65** source-collection candidates: **28** now carry at least one operator, route variant, or family level source lead; **37** still lack such a linked source in the inspected registers. The 28 source leads may be *family-level only*, and should never be confused with completed individual schedules
- Parked: **90290** (Tax Maya 195ii) and **90370** (Flota Nueva Villa 082 V-LA PILOTO); no further investigation was conducted

## Research tier counts (mutually exclusive by route)

| Tier | ArcGIS IDs |
| --- | ---: |
| shared_family_partial_evidence | 21 |
| no_schedule_evidence | 104 |
| baseline_three_daytype_both | 49 |
| operator_variant_daytype_unknown | 11 |
| historical_provisional_three_daytype_model | 34 |
| historical_2015_blocked_or_ambiguous | 28 |
| baseline_partial_both | 1 |
| parked | 2 |
| third_party_variant_candidate | 2 |
| **TOTAL** | **252** |

## Family service inheritance

The user accepted propagating a **single official family frequency** to each route that belongs to that family. The same rule applies to other family-source evidence, but its provenance must be explicit. This audit carries shared-family source IDs and the original weekday/Saturday/Sunday interval figures in the route rows and daytype rows. All these routes have `do_not_duplicate_shared_service=yes`.

**Critical source distinction:** current 087/088/091/103/107 daytype headways in this overlay are sourced to Moovit/other published third-party family tables, **not an original legal resolution**. Coonatra 2024–27 averages are **operator family averages**, **not individual route or statutory headways**. These observations are inherited as *family-level candidates*, never labeled officially authorized frequencies. No 2025 original legal resolution family headways were newly mapped in this narrow overlay; original 2025 source tables and their uncertain legal↔ArcGIS crosswalk are preserved separately.

- Family-level sources are one shared service record (same identifier on each old route row), never one additive trip supply per historic ArcGIS shape
- Operator-published direct variant first/last times have unspecified daytype, so they do not automatically complete all three calendar categories
- Historical 2015 normal/HMD dispatch intervals and original service windows are kept in the three separate daytype rows when linked, even for blocked/anomalous cases; only **34** narrowly classified provisional fallback routes are counted in the research-only total
- The historical 2015 day/HMD split cannot be renamed into exact PP/PVM periods. Use the separately maintained provisional clock model
- `current_2026_legally_verified=no` and `gtfs_automatic_import=no` remain explicit on all new rows

## Files

- [Consolidated one-row-per-legacy-route audit](medellin_252_schedule_consolidated_2026-11-19.csv)
- [Consolidated one-row-per-route-and-daytype audit](medellin_252_schedule_daytypes_consolidated_2026-11-19.csv)
- Inputs: `medellin_252_route_schedule_coverage.csv`, `medellin_252_route_schedule_daytypes.csv`, `medellin_70_historic_2015_later_amendments_audit_2026-11-19.csv`, `coonatra_current_website_12_variant_departure_windows.csv`, `coonatra_2022_calasanz_exact_departures_by_variant.csv`, `coonatra_2024_2027_operator_published_family_windows_frequencies.csv`, `2026_6f_6h_087_088_091_103_107_public_headways.csv`, `2026_moovit_additional_operator_schedules_review.csv`.
