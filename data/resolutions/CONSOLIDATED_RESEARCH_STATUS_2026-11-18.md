# Consolidated Medellín urban bus research status — 18 November 2026

This is an **evidence ledger**, not a GTFS timetable or a confirmation that every 2025 route is still legally operative in late 2026. No GTFS generation or import is authorized from this report.

## Registered original 2025 permits (official ASTREA)
The following official full-text sources have been recovered, their route tables extracted, and the current research identities and exceptions preserved in [`2025_legal_to_arcgis_consolidated_register.csv`](2025_legal_to_arcgis_consolidated_register.csv).

| Legal act | Operator scope | Legal GTPC+code records | ArcGIS match status |
|---|---|---:|---|
| [202550076150](https://www.medellin.gov.co/normograma/docs/astrea/docs/r_smmed_76150_2025.htm) | Invetrans / Coinvetrans, Salud-Hotelera | 6 | 6 candidate mappings, original names and legacy-code differences preserved |
| [202550076162](https://www.medellin.gov.co/normograma/docs/astrea/docs/r_smmed_76162_2025.htm) | Transportes Medellín Castilla / Conaltracoop | 30 | 34 historic Castilla ArcGIS IDs checked separately; 3 strong code+name, 1 code/name conflict, 4 ambiguous, 4 route-family candidates, 22 without defensible one-to-one linkage |
| [202550079848](https://www.medellin.gov.co/normograma/docs/astrea/docs/r_smmed_79848_2025.htm) | Metrosan | 16 direction records / 8 service families | 8 name/family candidates to historical ArcGIS; direction GTPC rows retained without doubling |
| [202550079865](https://www.medellin.gov.co/normograma/docs/astrea/docs/r_smmed_79865_2025.htm) | Rápido San Cristóbal | 34 | Reconcile with existing operator website images and mapping under [issue #18](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/issues/18); avoid duplicated schedule research |

**Total 86 individual legal records, NOT 86 independent GTFS services.** Other 2025 original [202550076174](https://www.medellin.gov.co/normograma/docs/astrea/docs/r_smmed_76174_2025.htm) relates to Coonatra's 301 and Santra's 315 geometry and belongs to the legal-act index; no extra frequency records should be inferred from its contextual table. **202550076168/2025** (Combuses / Circular 313) remains original-text-unrecovered; its act index alone is not schedule evidence.

## Castilla-specific controls
- [34-route reverse index](2025_castilla_34_legacy_arcgis_reverse_review.csv), preserving each historical ArcGIS ID, legacy code, candidate legal code(s), and confidence status.
- Exact code **289** is not an exact route identity: 2025 legal label `Picacho` conflicts with older ArcGIS `Pilarica Calle 96`. Marked `matching_code_name_conflict`, not auto-approved.
- Old `261i`, `254i`, `306A/B` route families can have multiple valid interpretations against the 2025 code scheme; keep candidates unresolved until geometry and authorization articles are compared.
- `TRONCAL-4` through `TRONCAL-13` legal corridor entries are **not by themselves standalone timed bus services**. `TRONCAL 65` and `TRONCAL 73` have published windows but no headway in the source extraction. All twelve remain in the source register without invented headways.
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
| P2 | Combuses Circular 313 original 2025 decision | 202550076168 | Direct original link not yet confirmed; leave on hold |
| P2 | Remaining other operators' historic 2017–2024 official acts | `2017_2024_act_chain_index.csv`, prioritize explicit service changes | Official management-report titles indexed, original acts not uniformly verified |
| P2 | 2026 follow-up of late local publication beyond indexed set | ASTREA 2026 and Gaceta public archive | Only bounded scans done; no claim of exhaustive legal currency |
| Parked | Flota Nueva Villa 082 V-LA PILOTO, Resolución 202250106966 | 90370 | User directed to skip until direct original link is available |

All newly processed entries preserve traceable legal source URL, route code, GTPC, published interval/day values, and ArcGIS mapping confidence in the consolidated CSV. Only where reliable historical links exist are old codes and agency names included. **No GTFS generator, calendar, services, route geometry, or frequencies were changed.**


## Historical 2017–2024 direct-source audit and Coopetransa 069 (18 November 2026)

A bounded official ASTREA URL-pattern audit checked **38 previously indexed administrative acts**: **2** original full-text candidates were confirmed, **36** not retrieved via tested URLs. The direct source and retrieval outcome are recorded on each row of `2017_2024_act_chain_index.csv`. The two confirmed originals are Coonatra 202150181337/2021 (already reviewed, affects 300/301; not Tax Maya 195ii), and 202450030616/2024 for joint route 229i.

**Important precedence:** 202450030616/2024 is *expressly repealed* by Art. 11 of the recovered 202650039611/2026 act. Its published `FRECUENCIAS DE OPERACIÓN` figures **118/10 weekday/Saturday** and **59/5 Sunday/holiday** are counts of services, not minute intervals. The current 2026 authorized interval source remains in `route_229i_2026_official_intervals.csv`; historical counts are not imported or combined.

A new operator-published primary-source report was visually reviewed: Coopetransa's 2023 management report, printed p23 (PDF p22), reproduces the 2023 official technical fiche for **069 El Jardín** and confirms **069 El Jardín–La Cima** as an alternate ramal. Old ArcGIS IDs **90238** and **90376** respectively. The parent service window is **03:00–23:00**, and the published operations-count table is **228/24 weekday and Saturday, 137/15 Sunday and holiday**; **these are not minutes or a separate ramal timetable**. Three-member `TRESCOOP 6E` convenio is named, but Coopetransa is the operator printed for 069; no triple-agency duplication. Original municipal act **202350107467/2023** is *still missing* despite its fiche being reproduced by the operator.

All details and QA are in [historic_2017_2024_originals_and_coopetransa_069_review.md](historic_2017_2024_originals_and_coopetransa_069_review.md) and [coopetransa_069_2023_operator_report_legal_fiche.csv](coopetransa_069_2023_operator_report_legal_fiche.csv). The remaining original act retrieval work should prioritize actual service-altering decisions, not already verified geometry-only changes. No GTFS generator modifications.
