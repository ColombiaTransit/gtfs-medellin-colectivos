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

**New visual-source verification in Gaceta 5671**: PVE `before 04:30 and after 20:30` is printed **separately** under Salud-Hotelera (**p13**), Castilla/Conaltracoop (**p27**), Metrosan (**p40**) and Rápido San Cristóbal (**p57**). Circular 313 already had the same definition in original Gaceta 5667 **p56**. Palenque 202550088689 independently confirms the same PVE definition in Article 7; see focused PP/PVM audit. All PP/PVM period boundaries remain unresolved, and no GTFS frequency or trip generation was done.

## Focused PP/PVM clock boundary round (18 November 2026)

[Research result and source audit](2025_pp_pvm_clock_boundary_research_2026-11-18.md): **NO official exact PP/PVM clock boundaries found** in the six inspected 2025 Medellín TPC decisions or targeted current online searches. **PVM is `Período Valle Meridiano`, not arbitrary all-day off-peak**. The 2011 AMVA traffic-model peaks 06:00–08:00 and 17:00–19:00 are not legal TPC timetable periods and were explicitly rejected as production assumptions in [source lead register](medellin_2025_pp_pvm_clock_boundary_source_audit.csv).

**Positive official result:** Palenque Robledal **202550088689/2025, Article 7** separately confirms the PVE extremes **before 04:30 and after 20:30**. This was checked against its original ASTREA full text in [workflow #44324071663](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44324071663), rather than extrapolated from Circular 313. It joins 2025 Salud-Hotelera, Castilla, Metrosan, Rápido San Cristóbal and Circular 313. The [PVE derived evidence register](2025_official_extreme_valley_windows_derived.csv) therefore now has **245** legal-window overlaps (**82** Palenque + previous 163), rebuilt successfully in [workflow #44324318293](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44324318293).

**Next evidence target:** actual `Programa de Servicio Operativo` (PSO) dispatch programmes or `Sistema de Ayuda a la Explotación` (SAE) service tables, referenced explicitly in municipal indicators. Only those or another applicable official/operator schedule can settle peak and meridian-valley clock boundaries; no GTFS extrapolation.


## 2026 published operator timetables and provisional PP/PVM scenario (18 November 2026)

[Current timetable reconnaissance](2026_additional_operator_headways_and_windows_2026-11-18.md) has added [18 direction/day-type public schedule entries](2026_moovit_additional_operator_schedules_review.csv) for Cootrabel **172/178**, Conducciones América **202/203/220** and Copatra **090**, distinguishing credible 05:00–20:00 10-min weekday / 06:00–19:00 20-min Sunday services from erroneous-looking Moovit 05:00–04:50 overnight spans. Cootrabel 172 has **different** direction-specific departure windows (05:00–20:00 vs 05:45–20:55 on Mon–Sat). The 178 frequency of 20 minutes corroborates the municipality's 2025 pilot but its published 24h third-party window is not accepted.

**Important new exact evidence:** [19 explicit departures for Transacoop 098-7](transacoop_098_7_2026_moovit_explicit_departures.csv), source updated 2026-08-30, one direction Santa Elena/Las Brisas to Medellín, every hour from **03:30 through 21:30**. The existing historical 90263 / `98 Directa 7` is only a provisional candidate; the exact 098-7 departure list is not nine branch frequencies or 24-hour service.

The [provisional PP/PVM model](2025_provisional_pp_pvm_operating_intervals.csv) was built successfully by [workflow #44325634014](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44325634014) and contains **1,136 period rows**, using regional peak-hour proxy 06:00–08:00 / 16:00–20:00 as user-accepted *provisional* periods with official legal maxima clipped to original route/day windows. No new production GTFS files or automatic imports.


## Complete official-first frequency coverage audit — 18 November 2026

[Full research and prioritization report](medellin_frequency_coverage_review_2026-11-18.md), reproducible in [Actions #44332357292](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44332357292), reconciles all **252 archived ArcGIS route IDs** (504 direction records), and writes [252 route status](medellin_252_route_schedule_coverage.csv), [756 daytype details](medellin_252_route_schedule_daytypes.csv), [252 with 2015 historic-source fallback flags](medellin_252_coverage_with_historical_fallback.csv), [66 unmatched 2025 legal-route code entries](medellin_unlinked_official_2025_schedule_candidates.csv), [205 focused route work-items](medellin_missing_frequency_windows_worklist.csv) and [priorities across 32 operators + one unattributed route](medellin_operator_frequency_gap_priorities.csv).

Source coverage by old route IDs: **39 official 2025/2026 candidates**, **27 operator-source candidates**, **4 Moovit-only** and **182 not yet matched to a recent timetable**. The latter 182 are subdivided into **47 old/new official route code issues** (use already recovered resolutions), **70 with historical 2015 original fiche matches as provisional fallback** (do not assume unchanged in 2026), and **65 requiring a genuinely new operator/route-specific schedule source**. The 2015 historical index contains 111 references overall, including 41 routes which already have newer material. ArcGIS `90375` has an empty operator field, kept as `UNKNOWN_OPERATOR_IN_ARCGIS` rather than inventing a company. **No GTFS generator modifications.**


## First truly uncovered operator source recovered: Coonatra (18 November 2026)

A [direct Coonatra original 2024–2027 presentation](https://coonatra.com/wp-content/uploads/2023/09/POLITICA-PUBLICA-COONATRA.pdf) was visually checked, capturing **six family-level average headways and operating windows**: Circular Coonatra **4min 04:00–21:30**; Circular Sur **3min 04:00–21:30**; Calasanz Intermedia **5min 04:10–21:30**; Calasanz Integrada **7min 04:00–23:00**; Floresta–San Juan **6min 03:45–21:30**; Floresta Integrada **8min 04:00–23:15**. See [source table](coonatra_2024_2027_operator_published_family_windows_frequencies.csv) and [visually checked operator document review](coonatra_2024_2027_operator_source_frequency_review.md). The actual Coonatra Circular website adds **04:10 first / 21:30 last dispatch** for 300/301 variants. **Do not multiply average headway by the number of ramales, copy the same hours indiscriminately to each route or treat family Circ. Sur as Santra's 315**; detailed source-to-ArcGIS crosswalk still open. Therefore the 252 individual legacy route coverage totals do not mechanically change.


## Additional Coonatra source research: six Calasanz tables (18 November 2026)

A **new directly published full original timetable PDF** was found on Coonatra's own [Calasanz-Boston site](https://coonatra.com/calasanz-boston/): [`Frecuencias rutas Calasanz.pdf`](https://coonatra.com/wp-content/uploads/2022/08/Frecuencias-rutas-Calasanz.pdf). After visual verification of its three pages, [run #44335426776](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44335426776) successfully extracted **452 exact clock-time departures** for six operator-defined 310/311 variants (95/43/43/138/42/91). [Full source table](coonatra_2022_calasanz_exact_departures_by_variant.csv); [six family-to-ArcGIS candidate mapping rows](coonatra_calasanz_2022_six_schedule_legacy_arcgis_candidates.csv); [source review](coonatra_calasanz_departures_and_2025_operational_changes.md). Service-day and direction applicability **not stated in the PDF**; older 310R geometry may represent more than one operator-published variant, so do NOT triple or double departure supply in GTFS.

A separate newer [Coonatra original 2024 annual report (published 2025)](https://coonatra.com/wp-content/uploads/2025/07/3.-Informe-de-Gestioin-2024-Resumido.pdf) confirms **Floresta–San Juan operated at minimum authorized capacity following early-2025 fleet withdrawals** and Circular 300/301 contract negotiations began February 2025. These are real operating caveats, **not** newly documented replacement frequency numbers or route cancellation. [Management report evidence ledger](coonatra_2025_management_report_frequency_caveats.csv). The historical 6-minute Floresta family average remains a model lead, not assumed 2026 realized headway.


## Coonatra follow-up: 12 exact variant windows on current operator pages (18 November 2026)

[12 operator variant first/last spans](coonatra_current_website_12_variant_departure_windows.csv) were added: four **Floresta–San Juan** variants 242 Divisa **03:45–21:30**, 242 Quiebra **05:08–18:12**, 243 Divisa **05:45–17:55** and 243 Quiebra **06:05–17:13**; six **Calasanz 310/311** variants, plus Circular **300/301 04:10–21:30**. The fields come from Coonatra's own [Floresta](https://coonatra.com/floresta-san-juan/), [Calasanz](https://coonatra.com/calasanz-boston/) and [Circular](https://coonatra.com/circular-coonatra/) route pages; intermediate stop arrival clocks are explicitly separated from last terminal departures. These 12 lines refer to **11 legacy ArcGIS candidate IDs** because **310 Rosal and 310 Metro Rosal both map only provisionally to 90363/310R**. The Calasanz source PDF prints 310 Metro Rosal last **21:42**, while the general operator site says **22:00**; both versions are retained and the conflict is flagged, not silently resolved. Daytype, route direction, date of timetable validity and 2025 legal shape identity remain to check. **The older 65 no-source bucket in the previous snapshot predates this operator variant evidence; it should not be treated as an updated live deficit count.** No GTFS generator changes.


## 2026-11-19: Additional 6F/6H current frequency candidates

The [focused 6F/6H timetable source audit](6f_6h_frequency_window_research_2026-11-19.md) yielded [24 public-route/daytype headway records](2026_6f_6h_087_088_091_103_107_public_headways.csv) across **8 public service variants**: Cootransi 103 (**3min weekday, 5min Saturday, 3–7min Sunday**); Cootransvi 107 (**4, 5, 4–8min**); Cootranspinal 087 (**4, 4, 8min**) and 088 (**3, 3, 3–6min**); Copatra 091 four branches (**5/10/15min weekday, distinct Sunday ranges**). More credible bounded reported Saturday work windows: 103 **05:00–23:00**, 087 **05:00–22:28**, 088 **05:00–23:00**, and 091/Calle 56a **05:00–21:30**.

**Critical:** Most public Moovit weekday/Sunday end times look like **05:00–04:55 next-day**, repeated even across unrelated lines, and are **excluded** from verified work windows. [Older TransitRun 091 Calle56a alternative](copatra_091_el_pinal_older_daytype_windows_source_conflict.csv) reports 03:35–22:00 weekdays, 04:00–21:30 Saturday, 05:00–22:00 Sunday, but is **a dated different source, not confirmed current**. Original [Metro Medellín Cootransvi 107 announcement](https://www.metrodemedellin.gov.co/al-dia/noticias/cootransvi-cuenta-con-la-primera-ruta-barrial-no-integrada-al-metro-con-recaudo-electronico) identifies **three** operating branches (San Antonio/Perlas/Ratón) despite six historical 107 GIS shape IDs. No multiplied headways by 103/107/091 branches. Cootransi's own [operator site](https://cootransi-a4fc5c.webnode.com.co/) provides no numerical schedule. Official older decision chains were **not rescraped**, no GTFS changes. The 252-ID coverage scoreboard precedes these additional family-level findings and must not be inflated to match family counts.
