# Medellín — worklist for 146 routes without complete 2026 working timetable

Generated from accepted [252-route working assumption](medellin_252_schedule_2026_working_assumption.csv). Total **252 = 106 already modeled all three daytypes + 146 not complete**. The 146 includes **2 explicitly parked routes**, so **144** are active research targets.

## Current mutually exclusive investigation groups

| Group | Route IDs |
|---|---:|
| SHARED_FAMILY_FREQUENCY | 19 |
| NO_LINKED_SOURCE | 49 |
| OPERATOR_VARIANT_WINDOWS | 4 |
| OPERATOR_EXACT_DEPARTURES | 3 |
| OFFICIAL_PARTIAL | 2 |
| OFFICIAL_NEW_LEGACY_CROSSWALK | 10 |
| OFFICIAL_FAMILY_CROSSWALK | 37 |
| HISTORIC_REFERENCE_NOT_APPLIED | 6 |
| HISTORIC_VARIANT_MAPPING | 10 |
| HISTORIC_ZERO_INTERVAL | 1 |
| THIRD_PARTY_VARIANT | 3 |
| PARKED | 2 |
| **Total** | **146** |

## Priority distribution

- **P1: 49** route IDs
- **P2: 24** route IDs
- **P3: 22** route IDs
- **P4: 49** route IDs
- **P9: 2** route IDs

## Research policy

1. User accepts reviewed original official resolutions as operational **2026 working assumptions**; no recurring legal-validity investigation. Only a known contradictory numeric change needs explicit revision.
2. P1 official legal 2025/26 route-family codes should be applied to matching old route branches, with source and daytype evidence; where multiple historic variants share one legal service, use the **same shared service ID**, never multiply its printed frequency or departures.
3. Sources named `SHARED_FAMILY_FREQUENCY` may come from **Moovit** or the **operator's published average**, which is *not equivalent* to legal resolution data; retain that distinction and do not duplicate services.
4. Existing operator timetable rows with daytype unknown do not establish all three daytype windows, even though the printed first/last departure remains a useful working estimate.
5. No automatic GTFS changes in this phase. Two parked IDs **90290 (195ii Tax Maya)** and **90370 (082 PILOTO Flota Nueva Villa)** remain excluded.

## Next concrete sequence

- Resolve P1 old–new legal route code pairs, prioritizing 2025 Castilla, Palenque, Rápido San Cristóbal and Metrosan original official data already staged.
- Reconcile P2 2015 variant references and Coonatra source exact departure/first-last windows.
- Carry family source headways in P3 as shared services, then seek missing credible service-day windows without multiplying intervals.
- Search only genuinely source-free P4 operator routes; avoid re-fetching verified original documents.

[Full 146-route action register](medellin_146_remaining_routes_action_register_2026-11-19.csv).
