# Consolidated Medellín urban bus research status — 18 November 2026

This is an **evidence ledger**, not a GTFS timetable or a confirmation that every 2025 route is still legally operative in late 2026. No GTFS generation or import is authorized from this report.

## Registered original 2025 permits (official ASTREA and Gaceta 5667)
The following official full-text sources have been recovered, their route tables extracted, and the current research identities and exceptions preserved in [`2025_legal_to_arcgis_consolidated_register.csv`](2025_legal_to_arcgis_consolidated_register.csv).

| Legal act | Operator scope | Legal GTPC+code records | ArcGIS match status |
|---|---|---:|---|
| [202550076150](https://www.medellin.gov.co/normograma/docs/astrea/docs/r_smmed_76150_2025.htm) | Invetrans / Coinvetrans, Salud-Hotelera | 6 | 6 candidate mappings, original names and legacy-code differences preserved |
| [202550076162](https://www.medellin.gov.co/normograma/docs/astrea/docs/r_smmed_76162_2025.htm) | Transportes Medellín Castilla / Conaltracoop | 30 | 34 historic Castilla ArcGIS IDs checked separately; 3 strong code+name, 1 code/name conflict, 4 ambiguous, 4 route-family candidates, 22 without defensible one-to-one linkage |
| [202550079848](https://www.medellin.gov.co/normograma/docs/astrea/docs/r_smmed_79848_2025.htm) | Metrosan | 16 direction records / 8 service families | 8 name/family candidates to historical ArcGIS; direction GTPC rows retained without doubling |
| [202550079865](https://www.medellin.gov.co/normograma/docs/astrea/docs/r_smmed_79865_2025.htm) | Rápido San Cristóbal | 34 | Reconcile with existing operator website images and mapping under [issue #18](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/issues/18); avoid duplicated schedule research |
| [202550076168](https://www.medellin.gov.co/statements/innovaciondigital/gacetas/historico-mercurio/descargar/202000087050) | Joint Circular 313 (Combuses/Coometropol/Coinvetrans/Autobuses El Poblado Laureles) | 2 GTPC direction rows / 1 jointly operated service | Original Gaceta 5667 pp55–57 visually verified: legal service windows, maximum intervals, 177/2017 repeal; ArcGIS 90004 geometry still requires comparison |

**Total 88 legal direction/source records in the consolidated register (86 from four ASTREA originals plus 2 Circular 313 direction GTPC rows), NOT 88 independent GTFS services.** Other 2025 original [202550076174](https://www.medellin.gov.co/normograma/docs/astrea/docs/r_smmed_76174_2025.htm) relates to Coonatra's 301 and Santra's 315 geometry and belongs to the legal-act index; no extra frequency records should be inferred from its contextual table. **202550076168/2025 Circular 313 now has an original municipal Gaceta 5667 PDF visually verified**: joint 4-operator service, GTPC 29903/49904, 2025 service hours and maximum intervals, express repeal of Resolución 177/2017 (see `2025_circular_313_official_joint_service.csv`).

## Castilla-specific controls
- [34-route reverse index](2025_castilla_34_legacy_arcgis_reverse_review.csv), preserving each historical ArcGIS ID, legacy code, candidate legal code(s), and confidence status.
- Exact code **289** is not an exact route identity: 2025 legal label `Picacho` conflicts with older ArcGIS `Pilarica Calle 96`. Marked `matching_code_name_conflict`, not auto-approved.
- Old `261i`, `254i`, `306A/B` route families can have multiple valid interpretations against the 2025 code scheme; keep candidates unresolved until geometry and authorization articles are compared.
- `TRONCAL-4` through `TRONCAL-13` legal corridor entries are **not by themselves standalone timed bus services**. `TRONCAL 65` and `TRONCAL 73` have published service windows **and** maximum legal interval triples; confirmed visually from original Gaceta 5671 pp25–26 and corrected in the centralized source register. All twelve remain in the source register without invented headways.
- The municipal ArcGIS snapshot has 34 unique `id_ruta` for **Transporte Medellín Castilla**, and **no operator entry explicitly named Conaltracoop**. The latter absence is not proof Conaltracoop ceased operation; do not assign routes to it solely because it is named jointly in the 2025 act.
- Historic 2015 [Resoluciones 1166/1169](1166_1169_shared_2a_2015_interval_visual_verified.csv) were separately validated as a repeated, shared 2A family; they must **not** supersede new 2025 operating terms.

## Field precedence and data quality
1. Keep source order **official later act > applicable earlier act** only for *actually affected* route/field; retain the 2015 originals for provenance and do not assume all old 2A frequencies remain valid.
2. The source table gives maximum departure intervals per day type and operating-period categories, not the exact period start/end times needed to generate every `frequencies.txt` entry.
3. The seven Rápido San Cristóbal veredal routes have **numbers of services/day** in the legal tables, not minute headways. All 11 corregimental Palmitas routes have fixed departure records, some in the master table. Existing operator timetable photo data is a separate source; match before use.
4. Metrosan's second direction entries have intentionally blank numerical source cells. They should not double headways; neither should the blanks be interpreted as confirmation of equal timetables in each direction.
5. The [2026 indexed official-act screen](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44272664218) read all **25 currently indexed 2026 Movilidad ASTREA texts** successfully. Two pages matched target operator-group keywords, including the separate published 229i decision. This is *bounded index evidence*, not a legal warranty that no 2026 act elsewhere modifies a route.
6. Status `automatic_gtfs_import=no` is intentional everywhere in the consolidated register.

## Outstanding work, without repeating completed source retrieval

| Priority | Task | Scope | Current status |
|---|---|---|---|
| P1 | Castilla 2025 legal code ↔ actual ArcGIS geometry and stop-direction check | 34 older routes, 30 legal records, including conflict 289 | Cross-index done, geometry/legal amendments unresolved |
| P1 | Verify 2025 published period boundaries / first-last departure semantics | Salud, Castilla, Metrosan, Rápido | Source extraction done, production interpretation open |
| P1 | Metrosan Colinas 90308 and Socorro 90314 actual 2025 legal disposition | Both absent as separate lines in 2025 table | Do not infer repeal |
| P1 | TRSC actual operator-photo departure-time ↔ 2025 code crosswalk | Existing photo data; issue #18 | Deferred at user request, no duplicate scraper |
| Closed source QA / open geometry and period QA | Circular 313 original 2025 decision | 202550076168 | Gaceta 5667 original pages 55–57 visually verified; check route-shape and peak/midday clock boundaries before GTFS |
| P2 | Remaining other operators' historic 2017–2024 official acts | `2017_2024_act_chain_index.csv`, prioritize explicit service changes | Official management-report titles indexed, original acts not uniformly verified |
| P2 | 2026 follow-up of late local publication beyond indexed set | ASTREA 2026 and Gaceta public archive | Only bounded scans done; no claim of exhaustive legal currency |
| Parked | Flota Nueva Villa 082 V-LA PILOTO, Resolución 202250106966 | 90370 | User directed to skip until direct original link is available |

All newly processed entries preserve traceable legal source URL, route code, GTPC, published interval/day values, and ArcGIS mapping confidence in the consolidated CSV. Only where reliable historical links exist are old codes and agency names included. **No GTFS generator, calendar, services, route geometry, or frequencies were changed.**


## Historical 2017–2024 direct-source audit and Coopetransa 069 (18 November 2026)

A bounded official ASTREA URL-pattern audit checked **38 previously indexed administrative acts**: **2** original full-text candidates were confirmed, **36** not retrieved via tested URLs. The direct source and retrieval outcome are recorded on each row of `2017_2024_act_chain_index.csv`. The two confirmed originals are Coonatra 202150181337/2021 (already reviewed, affects 300/301; not Tax Maya 195ii), and 202450030616/2024 for joint route 229i.

**Important precedence:** 202450030616/2024 is *expressly repealed* by Art. 11 of the recovered 202650039611/2026 act. Its published `FRECUENCIAS DE OPERACIÓN` figures **118/10 weekday/Saturday** and **59/5 Sunday/holiday** are counts of services, not minute intervals. The current 2026 authorized interval source remains in `route_229i_2026_official_intervals.csv`; historical counts are not imported or combined.

A new operator-published primary-source report was visually reviewed: Coopetransa's 2023 management report, printed p23 (PDF p22), reproduces the 2023 official technical fiche for **069 El Jardín** and confirms **069 El Jardín–La Cima** as an alternate ramal. Old ArcGIS IDs **90238** and **90376** respectively. The parent service window is **03:00–23:00**, and the published operations-count table is **228/24 weekday and Saturday, 137/15 Sunday and holiday**; **these are not minutes or a separate ramal timetable**. Three-member `TRESCOOP 6E` convenio is named, but Coopetransa is the operator printed for 069; no triple-agency duplication. Original municipal act **202350107467/2023** is *still missing* despite its fiche being reproduced by the operator.

All details and QA are in [historic_2017_2024_originals_and_coopetransa_069_review.md](historic_2017_2024_originals_and_coopetransa_069_review.md) and [coopetransa_069_2023_operator_report_legal_fiche.csv](coopetransa_069_2023_operator_report_legal_fiche.csv). The remaining original act retrieval work should prioritize actual service-altering decisions, not already verified geometry-only changes. No GTFS generator modifications.

## Primary source recovered: Gaceta 5667 Circular 313 and 301/315 (18 November 2026)

The municipal **historical Gaceta search** now supplies the original 67-page Gaceta 5667 PDF under documented ID `202000087050`. The operator-coordinated Circular **313** was approved 19 September 2025 and published 24 September: one joint service by **Combuses, Coometropol, Coinvetrans and Autobuses El Poblado Laureles**, with GTPC **29903/49904**, legal windows **04:00–22:00 weekdays/Saturday** and **04:45–21:00 Sunday/holidays**, maximum peak/extreme-valley/midday-valley intervals **7/15/8** and **12/15/12 minutes** respectively. Source p56 defines extreme valley as before 04:30 and after 20:30, but does not fully define other period boundaries. Article 11 repeals 177/2017 and all previous Circular 313 operating terms. No duplicate services by participant operator. The source is linked from [2025_circular_313_official_joint_service.csv](2025_circular_313_official_joint_service.csv).

The same original Gaceta p65 confirms that **202550076174** changes geometry of Circular 301 (Coonatra) and 315 (Santra), including an authorized existing stop for 315, but its **Article 1 paragraph 3 explicitly leaves all frequency and hours unchanged**. Full visual evidence and source SHA are in [Gaceta 5667 original audit](gaceta_5667_2025_circular313_301_315_original_visual_audit.md).

Old status text in earlier 2025 source-finding reports indicating that original Circular 313 was missing is superseded by this direct recovery. No change to GTFS generation; later-2026 legal effectivity and ArcGIS geometry alignment remain open.

## Original Gaceta 5671 secured and 2025 classification corrected (18 November 2026)

Official municipal [Gaceta 5671](https://www.medellin.gov.co/statements/innovaciondigital/gacetas/historico-mercurio/descargar/202000087077), original **62 pages**, SHA256 `97558ef103d1f71fc03f641dacfb618c4d223342105426cb50901bc8af8f9607`, contains all four 2025 ASTREA resolutions and was verified in [GitHub run #44288771768](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44288771768). Original pp25–26 confirm **TRONCAL 65: weekday 8/15/10, Saturday 10/18/12, Sunday/holiday 13/16/20 minutes**; **TRONCAL 73: weekday 4/8/6, Saturday 5/10/8, Sunday/holiday 6/10/13 minutes**. These are **maximum legally published period headways**, not guaranteed observed departures. The source correction ran successfully in [#44289880493](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44289880493). Gaceta 5671 p54 confirms seven veredal **counts/day** (rather than headway minutes). Correct source QA split: **50 legal maximum-headway records, 8 paired direction blanks, 11 corregimental fixed departures, 10 untimed standalone trunk corridor records, 7 veredal service-count records** = 86 ASTREA rows; joint Circular313 makes the central legal-to-ArcGIS table 88 direction/source records in all. See [original 5671 audit](gaceta_5671_2025_original_pdf_visual_spotcheck.md). **GTFS untouched.**


## November 2026 follow-up: Cootrabel, América and 6H

The targeted [Cootrabel / Conducciones América / 6H research note](cootrabel_america_6h_followup_2026-11-18.md) now includes the [28-route legal-chain register](2017_2025_three_operator_chains_route_review.csv) (2 Cootrabel, 16 Conducciones América, 4 Cootransi, 6 Cootransvi). Original legal frequency tables for the priority 2018–2023 acts remain unrecovered; their absence is not a route cancellation or a headway estimate.

**New official 2025 Cootrabel evidence:** Medellín announced route **178 Nuevo Amanecer–Centro** starting **14 November 2025** as a **pilot**, daily **04:20–21:20**, at a stated **20-minute** interval. Moovit stop lists updated in November 2026 still show 178 to Nuevo Amanecer, indicating later operation but **not a formal permanent permit or validated 2026 headway**. The pilot's relationship to old ArcGIS `90374 / 172-178 FUSION` remains unverified. See `cootrabel_178_nuevo_amanecer_2025_pilot_evidence.csv` and [issue #19](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/issues/19). No GTFS changes.


## System 6F: 2026 operator-published hours and destination variants (18 November 2026)

A newly verified [Cootransmallat operator page](https://www.cootransmallat.com/) publishes daily **04:00–23:30** general service windows for route **105 Golondrinas / El Faro** and **106 Tres Esquinas**. It also explicitly says the **Minorista destination is replaced by Bolivia after 18:00** and time-specific paths in its map are **variants, not independent additional routes**. This is operational operator evidence, not a municipal resolution or a minute-frequency table.

The [6F system audit](system_6f_operator_2026_source_audit.md) and [14-ArcGIS-ID ledger](system_6f_2026_operator_arcgis_family_register.csv) cover Cootransmallat 8 shapes, Cootranspinal 3 (087/088; independently confirmed by the municipal depot list), and Copatra 3 (090/091). Old per-variant headways and latest official 2023 original legal texts remain unknown. Do not multiply a common headway by the eight 105/106 ArcGIS shapes or assign the published general window to all special shapes; no generator changes.

## Verified progress snapshot (18 November 2026)

The [live research scoreboard](RESEARCH_PROGRESS_2026-11-18.md) counts **32 inventoried operator names, 252 unique ArcGIS route IDs, 504 direction records and 88 source-direction records from the known 2025 decisions**. The current ArcGIS review queue has **P0 3 / P1 94 / P2 153 / P3 2**. Its `frequency_currently_legally_verified` field is still **no for all 252** (conservative production acceptance); source recovery is much further along than per-route legal/geometry QA.

**Transacoop 6G** newly reconciled in [nine-route crosswalk](system_6g_transacoop_098_nine_variants_evidence.csv) and [source audit](system_6g_transacoop_098_source_audit.md). Beware: the old study's **25/20 min** headways belong to **Coopetransgur of Guarne**, *not* Transacoop; the study's older Transacoop 15/10 min observations, proposed 11 peak departures/hour and the 2024 tourism brochure's ~30 min shared-corridor guidance are also **not 2026 branch schedules**.

The broad research backlog remains [GitHub issue #12](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/issues/12), renamed from the now-complete Gaceta-acquisition wording; [issue #18](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/issues/18) tracks pre-existing Rápido San Cristóbal operator-photo reuse; [issue #19](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/issues/19) tracks Cootrabel 178 pilot effectivity.

## P0 geometric and interval QA advanced (18 November 2026)

A repeatable [projected ArcGIS source audit](2025_p0_arcgis_direction_geometry_audit.csv) ran successfully on existing EPSG:9377 linework [workflow #44318812668](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44318812668). **Circular 313** old 90004 direction shapes measure **13.180/14.536 km** while the 2025 original legal fiche prints **20.650 km each**, a **-36.18% / -29.61%** difference. Their coordinate order starts at one common location despite opposing direction labels. Old Circular 301 90006 shapes have **21.443/10.346 km** and nearly identical coordinate starts and ends; Circular 315 90015 shapes have **8.722/11.196 km** with reciprocal endpoint pattern. Castilla **289** remains a legal-title conflict: 2025 **Picacho** vs ArcGIS **Pilarica Calle 96**. These are *source shape* measurements, not government-annex confirmation. Legal-source geometry comparison is tracked as [issue #20](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/issues/20); detailed assessment: [P0 geometry and period report](2025_p0_shape_and_period_qa_2026-11-18.md).

Original Circular 313 Gaceta Article 8 defines PVE (extreme valley) before **04:30** and after **20:30**. Intersecting with legally published daily service spans gives five bounded PVE segments in [`2025_circular313_verified_extreme_valley_windows.csv`](2025_circular313_verified_extreme_valley_windows.csv). **Other PP/PVM clock period boundaries remain unknown**. This is research timing evidence only, not enough to generate complete GTFS frequencies.
