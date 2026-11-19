# Medellín Urbanas — 252 route frequency and service-window coverage (18 November 2026)

## Decision and methodology

**Official 2025/2026 acts first** for max dispatch intervals, operating hours and no-service day rules; then **already captured direct operator websites and original timetable photos** (including TRSC and Trasancoop), then cautiously applied **2015 historical fiches as optional provisional references only**, and finally **Moovit only for real remaining source gaps**. The user explicitly permits **provisional peak/midday clock models**, so there is no additional requirement for a juridical definition of PP/PVM to create research scenarios. Current GitHub production GTFS generators, shape files, trips and frequency feeds were **not modified**.

A deterministic reconciliation script [`audit_medellin_frequency_coverage.py`](../../scripts/audit_medellin_frequency_coverage.py) compares the **252 unique** archived ArcGIS route IDs (504 direction records) against the original route/day-type tables, 2026 route 229i, official 2025-to-ArcGIS candidate mappings, Palenque reconcilation, operators' retained timetables and lastly source-labelled third-party candidate schedules. A separate follow-up [`classify_medellin_remaining_schedule_gaps.py`](../../scripts/classify_medellin_remaining_schedule_gaps.py) enriches routes with existing 2015 official fiche links and flags **unmapped official 2025 route codes** before anybody searches an operator website. [`rank_medellin_operator_schedule_gaps.py`](../../scripts/rank_medellin_operator_schedule_gaps.py) ranks the remaining actual operator-level source gaps.

[Workflow #44332357292](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44332357292): **success**.

## Current 252-route snapshot

| Source coverage class | Unique legacy ArcGIS IDs | Meaning |
|---|---:|---|
| Official 2025/2026 candidate timetable available | **39** | Printed daytype frequency/window data mapped to a historical route **candidate**; route variant not necessarily fully verified |
| Existing operator information, sometimes incomplete | **27** | Reuse operator-provided windows, operator photo departures or source-labelled preliminary branch headways |
| Only secondary current source such as Moovit | **4** | Provisional data, original act / specific operator info still preferred |
| No matched **recent** timetable in current crosswalk | **182** | **NOT** a finding that none exists; resolve old-to-new legal codes and historic source references first |
| **Total** | **252** | Distinct archived ArcGIS `id_ruta` |

The **182** with no matched recent timetable break down into disjoint, actionable routes:
- **47** have a **newer 2025 legal code / old ArcGIS mapping problem** within their source family (e.g. Rápido San Cristóbal, Palenque, Castilla, Metrosan). This is **not** a source-collection task; investigate existing legal→ArcGIS route identity.
- **70** have an existing **2015 official historical fiche**, but no confirmed current source. The old timetable can be a **clearly labelled provisional fallback only if later amendments and route identity do not conflict**, never proof that the 2015 interval is still currently authorized.
- **65** genuinely lack even that already linked newer or 2015 source in the present 252-route registers and should be addressed with **route-specific operator data first**, Moovit only if missing.

**Other evidence:** the complete historical link index contains **111** of 252 with some 2015 printed fiche reference, *including routes which already have newer or operator evidence*. There are **66** official 2025 **legal code records** that still need unambiguous linkage to archived ArcGIS route IDs or represent merged/paired directional source semantics; **66 is not a count of extra bus lines or missing original timetable tables**.

### 32 companies + one incomplete route attribute
The operator index contains **32 named companies**, but official archived ArcGIS ID **90375 / 024 Barrial / Playon de los Comuneros_Barrial** has a *blank* operator field. It is not silently attributed to any of the 32. Therefore, the operator-priority table has 32 company rows plus one `UNKNOWN_OPERATOR_IN_ARCGIS` row, all adding up to 252.

## New machine-readable registers

- [`medellin_252_route_schedule_coverage.csv`](medellin_252_route_schedule_coverage.csv): one row per old ArcGIS ID, primary/secondary evidence class, daytype completeness and missing values.
- [`medellin_252_route_schedule_daytypes.csv`](medellin_252_route_schedule_daytypes.csv): **756** direction-agnostic ID/daytype records (weekday, Saturday, Sunday/holiday), preserving separate source tiers for first/last and frequencies and not assuming they came from the same publication.
- [`medellin_252_coverage_with_historical_fallback.csv`](medellin_252_coverage_with_historical_fallback.csv): adds the historic 2015 source identity (when present) and identifies the next rational research step.
- [`medellin_unlinked_official_2025_schedule_candidates.csv`](medellin_unlinked_official_2025_schedule_candidates.csv): **66** newer official code records already published but not yet uniquely reconciled against ArcGIS.
- [`medellin_missing_frequency_windows_worklist.csv`](medellin_missing_frequency_windows_worklist.csv): **205** route-level worklist entries, because even some routes with an official or operator source still have incomplete days, windows or variant QA. **205 is not the number of routes without any schedule.**
- [`medellin_operator_frequency_gap_priorities.csv`](medellin_operator_frequency_gap_priorities.csv): route-gap counts and recommended action for **32 operators plus 1 unassigned ArcGIS route**.

## Where genuinely new source searches bring the most value

Operator counts of **route IDs in the 65 genuinely absent existing-source category** (not automatically unique legal services):

| Operator | Currently no recent/2015 route match, new source needed |
|---|---:|
| Coonatra | 11 |
| Copatra | 10 |
| Conducciones América | 7 |
| Cootransvi | 6 |
| Cootransi | 4 |
| Autocol | 3 |
| Cootranspinal | 3 |

**Important:** The 2025 geometry-only Circular 301 (Coonatra) and 315 (Santra) decisions confirm that older operating conditions remain unchanged; these acts do **not** themselves print a replacement frequency timetable. Their published 2025 existence is retained separately.

The detailed operator table lists the lower-count operators and exact ArcGIS IDs.

## Provisional modelling and safety boundaries

- The separate [2025 provisional PP/PVM model](2025_provisional_pp_pvm_operating_intervals.csv) holds **1,136** interval segments based on a user-accepted peak-time proxy and the actual source's route/daytype maximum dispatch minutes. This is a **planning model**, not independently observed departures, and is never silently labelled `official_clock_periods`.
- The 245 PVE segments in [official PVE source-derived schedule](2025_official_extreme_valley_windows_derived.csv) use separate confirmed 04:30/20:30 boundaries in six applicable 2025 acts.
- **Do not duplicate Metrosan return GTPC rows or shared Circular 313 and route 229i operations**. One published numeric table for a shared service is not one copy per participating company or physical direction.
- **Palmitas fixed departures, veredal counts/day and temporary 250-5i during Línea J suspension** cannot be transformed into generic minute frequencies.
- Existing **TRSC timetable photos** are important original operator evidence; `data/trsc_route_mapping.yml` includes varying confidence and `data/trsc_schedule_photos.json` contains unresolved photo transcription/direction scope. Keep those candidates flagged, not automatic 2025 legal-to-ArcGIS equivalence.
- Trasancoop's website branch-by-number matching is marked **provisional**; some old source headways are approximations. The separate 19 exact departures for 098-7 are third-party, only one direction, and their identity is unverified.
- All `production_gtfs_approved=no`, no direct generation based only on raw source-candidate coverage.

## Ordered follow-up without redoing completed work

1. **First:** resolve the **47 legacy route IDs associated with newer legal numbering** against the **66 already published unmatched legal code records** (not all of them 1:1). Do not rescrape ASTREA/Gaceta timetable tables.
2. **Then:** apply clearly marked 2015 provisional fiches to **70 routes** only after checking the existing later-act indexes and known cancellations/alterations. Do not upgrade historical values to legal-current facts.
3. **Then:** target the **65 genuinely uncovered IDs**, starting with operators and source-specific line schedules and only finally Moovit, maintaining separate weekday/Saturday/Sunday/holiday scopes.
4. Use the user's accepted provisional PP/PVM periods for scenario modelling where only maximum intervals are printed; keep any actual operator timetable departures instead of synthesizing them.
5. Only after route identity and window/interval coverage meets the chosen model-acceptance thresholds, connect the schedule output to GTFS generation.

**No separate approvals or repeated broad 2015/2025 document acquisition required to continue this research sequence.**


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

## Consolidated update — 19 November 2026

A new **252-route / 756-daytype research overlay** now integrates the 2015 historical provisional fiches and explicit shared operator/third-party family evidence, without changing the original 18 November historical baseline. Results and counting rules: [consolidated report](medellin_252_schedule_consolidation_report_2026-11-19.md), [route CSV](medellin_252_schedule_consolidated_2026-11-19.csv), [daytype CSV](medellin_252_schedule_daytypes_consolidated_2026-11-19.csv).

- Baseline **49** all-three-daytype window+frequency candidates (50 with any).
- Research-only all-three-daytype coverage including **34 additional** vetted historical 2015 fallback candidates: **83 routes**. This figure includes provisional historical data and does *not* certify legal current effectivity or complete GTFS readiness.
- Of the original 65 source gaps, **28** now have source leads in the overlaid route/family evidence; **37** have none in those registers. Shared-family figures are clearly marked as one service and not counted as per-branch complete schedules.
- Parked 195ii and 082 PILOTO excluded. GTFS untouched.

## Adopted 2026 working assumption — 19 November 2026 (supersedes conservative planning count)

Per project decision, previously inspected official resolutions (including verified 2015 fiches) are **accepted as 2026 working timetable values** until specific contradictory evidence is identified. Revalidation via operators' sites is optional, not a prerequisite for further modelling. This is a planning assumption; do not change archival legal-source dates or claim legal confirmation without proof.

**New working-model coverage: 106/252 legacy route IDs with both frequency and operating windows across weekday, Saturday and Sunday/holiday**, consisting of 49 original three-daytype schedule candidates plus 57 additionally assumed historical source routes. The earlier conservative 83-count is retained only as an older research classification. The 57 additional include 13 cases with known later operating acts but no recovered numeric tables, identified for future correction if contradictory timings emerge; structurally shared 2015 fiches are not multiplied into additional services. Ten unresolved variant identities, the original zero HMD on route 110, and the two parked routes are not promoted.

Authoritative new working-model artifacts:
- [2026 timetable assumption and decisions](medellin_2026_resolution_working_assumption_2026-11-19.md)
- [252 route status rows](medellin_252_schedule_2026_working_assumption.csv)
- [756 daytype schedule rows](medellin_252_daytypes_2026_working_assumption.csv)

The 2026 planning acceptance is **not** proof of independently current legal effectivity; the GTFS generator has not been modified.

## P1 original-resolution crosswalk update — 19 November 2026

The initial **49 P1 legacy ArcGIS IDs** have been assessed against existing 2025 official source tables (147 route/daytype evidence rows). See [P1 report](medellin_p1_49_reconciliation_report_2026-11-19.md), [route identity matrix](medellin_p1_49_route_legal_crosswalk_2026-11-19.csv), and [official daytype values](medellin_p1_49_legal_daytypes_2026-11-19.csv).

**2026 working assumption coverage increases from 106 to 109** route IDs with per-daytype frequency+work window candidates: newly 90084 (255i), 90125 (306A), 90126 (306B). The revised 252-route working status CSV is [here](medellin_252_schedule_2026_working_assumption_p1_updated.csv). Two further weekday-only services (90012 308D and 90014 309D) have a **complete official operating/no-service daytype rule**, but cannot count as running on Saturday or Sunday; they are listed separately. The Sunday 255 row 90083 has internally conflicting legal source numeric/no-service metadata and remains unresolved. Rural counts are retained as counts, not converted to arbitrary headways, and source family values are not doubled.

The previous 106-route file remains as immutable earlier research snapshot. GTFS generator unchanged.

## P2 source audit closeout — 19 November 2026

P2 **24/24** route IDs reviewed. **9** additional original 2015 Gaceta **specific-branch** route IDs accepted as the working 2026 source (representing **7 distinct source services** because two historic pairs share a fiche). Aggregate **118/252** legacy route IDs now have three-daytype frequency and work-window data in the 2026 *research model*, up from 109 after P1. [P2 report](medellin_p2_closeout_2026-11-19.md), [P2 all-24 decisions](medellin_p2_24_route_resolution_2026-11-19.csv), [updated 252 model](medellin_252_schedule_2026_working_assumption_p2_updated.csv). The unresolved 15 P2 cases are stored in [P2 follow-up backlog](medellin_p2_followup_backlog_2026-11-19.csv). Explicit caveats: 097 prints unusual early close; Pedregal Bajo does not match Pedregal Alto fiche; 110 HMD prints zero; Coonatra operator tables lack verified service days and distinct 310R variants may not be merged. Original legal resolutions assumed current for planning; GTFS generator unchanged.
