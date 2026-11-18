# Medellín Urbanas — research progress and next-action register (18 November 2026)

## Measured scope (current GitHub files, not estimates)

| Metric | Verified count / state | Evidence |
|---|---:|---|
| Operator names represented | **32 / 32** | `data/resolutions/operator_coverage.csv` |
| Unique ArcGIS `id_ruta` identities | **252** | `data/medellin/routes.csv` |
| Direction-specific ArcGIS records | **504** | `data/medellin/routes.csv` |
| Historic 2015 unique source fiche positions visually checked | **114** | 2015 visual audit registers as summarized in [issue #12](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/issues/12) |
| Original 2025 source/directional records | **88** (not 88 services) | `2025_legal_to_arcgis_consolidated_register.csv` |
| 2025 ASTREA direction/source classifications | **50** numerical max-headway rows; **11** fixed rural departures; **7** rural daily-service counts; **8** Metrosan paired direction rows; **10** trunk/corridor identity-only rows | `data/resolutions/README.md` |
| Additional jointly operated Circular 313 directional rows | **2** / **1** service | Original Gaceta 5667 audit, included in the above 88 total |
| Already indexed 2017–2024 priority acts tested for direct ASTREA originals | **38**; **2** direct original texts recovered through URL-pattern check | `2017_2024_act_chain_index.csv`; source availability is not proof of absence |
| Queue entries marked current headway legally verified | **0** | `current_arcgis_legal_review_queue.csv` field `frequency_currently_legally_verified` — this is a conservative approval flag, not a claim that all 252 routes lack published information |

### Research queue priority allocation

| Current queue priority | ArcGIS identities | Intended next action |
|---|---:|---|
| P0 | **3** | Circular 313 source now recovered; validate ArcGIS shape, current legal effectivity and period boundaries; 301/315 geometry-only confirmed |
| P1 | **94** | Complete 2025 candidate-to-ArcGIS shape and stop checks, interval-period interpretation, and latest-act applicability |
| P2 | **153** | Focus on newer operating-condition originals and operator-verified departures for 6F/6G/6H, Conducciones América, Cootrabel, other operators |
| P3 | **2** | Defer low-priority/parked data and source-specific questions until higher priorities close |
| **Total** | **252** | A priority class is *not* a completion state |

**Important:** 32/32 operator names **inventoried** is not 32/32 operator timetables verified. The historical source QA and 2025 source extraction are substantially advanced, but **the legal approval flag is still zero across the current 252-ID review queue** because modern periods, route geometry and modifications require sign-off.

## Newly advanced in this pass

1. **Transacoop 6G:** [nine route branch ledger](system_6g_transacoop_098_nine_variants_evidence.csv) covers all ArcGIS 90257–90265 without multiplying the shared 098 corridor's approximate tourist frequency by nine.
2. **Important historic-source correction:** 25 min weekday / 20 min weekend, 05:20–20:00 in the old Santa Elena transport study describes **Coopetransgur (Guarne)**, *not* Transacoop. Transacoop's historical 2008-area observations refer to 15-minute morning / 10-minute after-13:00 dispatches; its 2011 study proposed 11 peak departures/hour, and the 2024 tourism brochure says approximately 30 minutes from 06:00 for a shared Santa Elena/Arví connection. Different dates, corridor versus route distinctions, and nonlegal source types make **all those values unsuitable as per-variant 2026 headways**. See [6G source audit](system_6g_transacoop_098_source_audit.md).
3. **6F prior work preserved:** the 14 ArcGIS families/variants are reconciled, with Cootransmallat direct operator daily origin-family 04:00–23:30 and Minorista→Bolivia after 18:00. No unverified per-shape headway was fabricated.
4. Backlog [issue #12](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/issues/12) renamed to reflect **remaining historic legal and GTFS acceptance**, rather than a falsely outstanding search for 2025 Gacetas already recovered. [issue #18](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/issues/18) preserves TRSC existing schedule-photo crosswalk; [issue #19](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/issues/19) covers the Cootrabel 178 pilot/permanence question.

## What work is still worth doing, in order

- **P0/P1:** compare current original 2025 route-family codes against government ArcGIS direction-specific geometries and stops, especially Castilla conflicting 289, Metrosan Colinas/Socorro, Circular 313 and shared 229i; avoid duplicated joint services.
- **P1:** determine legally documented clock period boundaries for already published max headways and day-type calendars. Source-specific intervals must not become blanket full-day frequencies.
- **P2:** obtain the **remaining original** 2017–2024 operating-condition acts from genuinely new municipal archives/official correspondence; do *not* rerun the same 38 predictable ASTREA URLs that yielded two originals.
- **P2:** compare **existing** operator website departures for TRSC against 2025 codes (issue #18), and review service-window/variant issues for 6F and 6G.
- **Parked:** Flota Nueva Villa 082 V-LA PILOTO (user directive).
- **Production gate:** until current legal and spatial QA are complete, keep `automatic_gtfs_import=no` and do not change GTFS generation.

This file is a snapshot of current research coverage and queue priorities. It is **not a statement that a particular bus route is currently authorized or active**.

## P0 geometric and interval QA advanced (18 November 2026)

A repeatable [projected ArcGIS source audit](2025_p0_arcgis_direction_geometry_audit.csv) ran successfully on existing EPSG:9377 linework [workflow #44318812668](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44318812668). **Circular 313** old 90004 direction shapes measure **13.180/14.536 km** while the 2025 original legal fiche prints **20.650 km each**, a **-36.18% / -29.61%** difference. Their coordinate order starts at one common location despite opposing direction labels. Old Circular 301 90006 shapes have **21.443/10.346 km** and nearly identical coordinate starts and ends; Circular 315 90015 shapes have **8.722/11.196 km** with reciprocal endpoint pattern. Castilla **289** remains a legal-title conflict: 2025 **Picacho** vs ArcGIS **Pilarica Calle 96**. These are *source shape* measurements, not government-annex confirmation. Legal-source geometry comparison is tracked as [issue #20](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/issues/20); detailed assessment: [P0 geometry and period report](2025_p0_shape_and_period_qa_2026-11-18.md).

Original Circular 313 Gaceta Article 8 defines PVE (extreme valley) before **04:30** and after **20:30**. Intersecting with legally published daily service spans gives five bounded PVE segments in [`2025_circular313_verified_extreme_valley_windows.csv`](2025_circular313_verified_extreme_valley_windows.csv). **Other PP/PVM clock period boundaries remain unknown**. This is research timing evidence only, not enough to generate complete GTFS frequencies.

## Circular 313 official annex / latest 2026 physical route research (18 November 2026)

The original 2025 Gaceta 5667 **Article 3 explicitly incorporates a separate route-map annex and city GIS** but the PDF itself contains **zero attached files** and no digitizable official GTPC 29903/49904 linework. Archived ArcGIS 90004 lengths remain materially inconsistent with the official 20.65 km per direction. No line-shape substitution was made.

Two **official 2026 route events** are newly documented: Metro de Medellín's **26 January 2026** Terminal Norte/Caribe construction detour (313 explicitly included; rerouting past Avenida Regional/TCC/Calle 67, no confirmed end date) and the municipality's **28 February 2026** new Olaya Herrera airport-area stop for 304/305/313 (precise coordinates not supplied). A newer public Moovit 313 list has **32 stop positions**, and a Moovit PDF a different **31**, so only the 32 stop names are retained as third-party **un-geocoded candidates**, not definitive counts or legal routes. Its generic 05:00–04:55 and 5-minute schedule must **not** supersede the city's 04:00–22:00 and source-specific interval limits.

See [full annex/source audit](circular313_legal_annex_2026_operational_geometry_audit.md), [2025–2026 route event register](circular313_2025_2026_geometry_changes_evidence.csv), [32-stop-order candidate register](circular313_2026_third_party_stop_order_candidates.csv) and [issue #20](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/issues/20). **GTFS unchanged**.

## Official frequencies and operating windows consolidated (18 November 2026)

[Main schedule QA report](2025_service_hours_frequency_qa_2026-11-18.md) documents the successful [workflow #44322146919](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44322146919) and three generated research tables:
- [321 per-day source rows](2025_official_service_windows_and_headways_by_day.csv) from 86 original 2025 ASTREA records, 20 Palenque records and one joint Circular 313 service.
- [134 exception day-records](2025_official_schedule_exceptions.csv), including source zeros, explicit no-operation, fixed Palmitas departures, 7 veredal daily-count lines and non-numeric trunk / paired GTPC directions.
- [163 verified PVE overlap periods](2025_official_extreme_valley_windows_derived.csv) clipped to the legally authorized daytype service spans without inventing exact departures.

**New visual-source verification in Gaceta 5671**: PVE `before 04:30 and after 20:30` is printed **separately** under Salud-Hotelera (**p13**), Castilla/Conaltracoop (**p27**), Metrosan (**p40**) and Rápido San Cristóbal (**p57**). Circular 313 already had the same definition in original Gaceta 5667 **p56**. The Palenque 2025 act needs a separate clock-period definition check; do not apply the definition automatically. All PP/PVM period boundaries remain unresolved, and no GTFS frequency or trip generation was done.
