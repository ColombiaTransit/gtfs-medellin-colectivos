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
