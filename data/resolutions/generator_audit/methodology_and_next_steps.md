# Comparison of actual Medellín GTFS outputs with 252 legacy urbanas routes

Audit date: 2026-11-19. Source of counts: [workflow run 44562065885](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44562065885), which read a **real released GTFS ZIP** and rebuilt three existing urbanas GTFS generators from checked-in ArcGIS layers and their current schedule mappings. This is a GTFS inventory, **not a proposal to overwrite generators**.

## Verified output

| Feed/generator | Data provenance | routes.txt IDs | IDs with trips | Geometry-only IDs |
|---|---|---:|---:|---:|
| MDO/SAO6 | Latest published release | 46 | 46 | 0 |
| Tax Maya | Existing code freshly executed, not verified published release | 11 | 11 | 0 |
| Transacoop | Existing code freshly executed, not verified published release | 9 | 9 | 0 |
| TRSC | Existing code freshly executed, not verified published release | 21 | 9 | 12 |
| El Poblado Flex | No unexpired downloadable GTFS artifact, site scraper requires source access | unknown | unknown | unknown |
| Sotrames Flex | No unexpired downloadable GTFS artifact, KML inputs not checked in | unknown | unknown | unknown |
| Coonatra | Existing standalone builder but no dedicated inspected published release or persisted KML/PDF inputs for this audit | unknown | unknown | unknown |

**Precisely verified:** 46 real release route IDs with trips for the separate MDO/SAO6 alimentadoras; **29 ArcGIS numeric legacy route IDs with trips** in 3 newly generated operator-specific GTFS archives; 12 TRSC numeric IDs with route rows but no trips. In the 252-route provisional working schedule model, **118** legacy IDs have complete weekday, Saturday and Sunday source-modeled schedules. Of those, **18** have demonstrable trip rows in these 3 operator GTFS rebuilds; **100** are **not yet proven present in the inspected GTFS trip outputs**, NOT necessarily 100 truly new routes. See [actual GTFS route rows](actual_gtfs_routes.csv), [100 IDs requiring generator reconciliation](ready_not_in_verified_gtfs.csv) and [machine-readable per-feed results](inventory.json).

## Major untapped route families among the 100 still not shown as trips

- Palenque Robledal: **16** full-workmodel routes.
- Transporte Medellín Castilla: **9**.
- Conducciones América: **9**.
- Metrosan: **9**.
- Transporte Aranjuez Santa Cruz: **7**.
- Flota la Milagrosa: **6**.
- Flota Nueva Villa: **6**.
- Autobuses Poblado Laureles: **6**, some may be present in uninspected El Poblado Flex.
- Coonatra: **6**, standalone Coonatra code may already generate some.
- Expreso Campo Valdés: **5**.
- The remaining **21** are spread across other operators and one missing operator label.

These are schedules in the **252 legacy ArcGIS working model**, not independently validated build-ready routes. Reconcile variant identity, service permissions, geometry/stop availability and family-frequency scope before import.

## Anomalies to handle before consolidation

1. **Tax Maya 90290 (195ii)**: has actual trips in the fresh legacy Tax Maya generator, but was **explicitly parked in the 2026 investigation** for unmatched modern service identity. Existing trip rows must not automatically change its parked status or be copied into a consolidated 2026 urbanas GTFS.
2. **Tax Maya 90333 (C23i historic Pedregal Bajo)**: has actual trips in the existing builder, yet the original historic 2015 legal fiche referred to Pedregal **Alto**. Needs identity reconciliation before promoting.
3. **Transacoop 90264 (Directa 8)**: actual trip rows exist even though older developer commentary describes this branch as having no verified frequency and spatial-only. Inspect generated trip mechanism and source mapping before assuming its times are independently verified; no automatic downgrade or manual edit here.
4. The 46 MDO/SAO6 main-feed codes are **not** numeric legacy urbanas IDs. Some are flagged provisional in `data/operators.yml`; `routes.txt` and `trips.txt` existence alone does not prove every schedule is official.
5. The ArcGIS 252 route-ID register and the separate alimentadoras layer must never be naively concatenated as the same universe.

## Follow-up

- Resolve the 100 candidate legacy IDs against Coonatra and El Poblado/Sotrames generator output first, using actual stable IDs, operator names and geometry rather than weak short-name matches.
- For all remaining fully scheduled 252 IDs, confirm exact current ArcGIS directions/stops and unique identity, then pass through the MobilityData validator in an isolated new-build draft.
- Keep source priority: official resolution baseline; directly published operator timetable supersedes; official legal family frequency copied unchanged to *each* family member; no Moovit.
- No production generator has been changed by this audit.
