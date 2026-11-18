# Coonatra: exact Calasanz departure tables and later operating caveats (18 November 2026)

## Direct operator original with real timetable entries

Coonatra publishes [`Frecuencias rutas Calasanz.pdf`](https://coonatra.com/wp-content/uploads/2022/08/Frecuencias-rutas-Calasanz.pdf), linked from its current [Calasanz-Boston route page](https://coonatra.com/calasanz-boston/). Its three pages were inspected visually; **six differently named variant-specific original departure tables** appear. Unlike previously collected Coonatra 2024–2027 average family headways, these are **exact printed clock-time departure lists**.

The reproducible [`extract_coonatra_calasanz_original_departures.py`](../../scripts/extract_coonatra_calasanz_original_departures.py) downloads the operator PDF; reads separately bounded table columns via PyMuPDF; normalizes Spanish a.m./p.m. clocks into HH:MM and **sorts each table chronologically** (printed table columns are column-major, not uniformly chronological). It refuses output if the earliest or latest departure differs from manually verified source page values. [GitHub Action #44335426776](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44335426776) **SUCCESS**, with 452 original departure times from the six tables.

| Printed operator variant | Source PDF page | Extracted departures | First | Last | Legacy ArcGIS candidate |
|---|---:|---:|---|---|---|
| 310 Directo Calasanz Boston | 1 | **95** | 04:20 | 21:10 | 90007 / 310 |
| 310 Rosal | 1 | **43** | 05:06 | 20:06 | 90363 / 310R |
| 310 Metro Rosal | 1 | **43** | 05:00 | 21:42 | 90363 / 310R **ambiguous same historic family** |
| 311 Calasanz Boston | 2 | **138** | 04:25 | 21:20 | 90008 / 311 |
| 311 Metro | 2 | **42** | 04:35 | 21:45 | 90324 / 311i |
| 311 Metro Directo | 3 | **91** | 04:30 | 22:30 | 90325 / 311ii |
| **Total** | **3** | **452** | | | **Five distinct old GIS IDs, not six separate proven modern GIS identities** |

**Data files:**
- [`coonatra_2022_calasanz_exact_departures_by_variant.csv`](coonatra_2022_calasanz_exact_departures_by_variant.csv): **452** times with original page, variant, sequence, tentative old ID and quality notes.
- [`coonatra_2022_calasanz_six_variant_exact_schedule_sources.csv`](coonatra_2022_calasanz_six_variant_exact_schedule_sources.csv): source summary for each of six variants.
- [`coonatra_calasanz_2022_six_schedule_legacy_arcgis_candidates.csv`](coonatra_calasanz_2022_six_schedule_legacy_arcgis_candidates.csv): nonduplicating crosswalk to candidate old ArcGIS codes.

### Important unresolved scope

The PDF **does not label the service day (Mon–Sat / Sunday / holidays), exact departure terminal or direction**. It lives under a 2022 upload path and can still be reached through the operator's route page, but this does **not prove unchanged 2026 operation**. The 452 slots must **not** be cloned onto weekday, Saturday and Sunday (or both directions), nor must two separately printed `310 Rosal` and `310 Metro Rosal` tables be blindly summed onto old 90363. Mark these as source-specific departure slots with `gtfs_import=no` until scope is confirmed.

The website independently publishes variant first/last times, consistent with the PDF; its **service page is a family listing, not a source of a three-day schedule**. The prior 2024–2027 management policy reports six **family-averaged** frequencies, not a real per-variant substitute for these departure tables.

## Newer Coonatra annual report materially affects frequency trust

Coonatra's directly published [2024 management annual report, PDF published July 2025](https://coonatra.com/wp-content/uploads/2025/07/3.-Informe-de-Gestioin-2024-Resumido.pdf), printed page 4 / PDF page index 4, was also visually checked.

1. **Floresta–San Juan:** the board subsidized this family in September 2024; its report says fleet was frozen early **2025** for vehicle withdrawals/transfers and the service was operating at **minimum authorized capacity**. That is evidence that the operator's older **6-minute average family headway** cannot be treated as a guaranteed *realized 2026 timetable*. The report **does not state a new minute interval** and does **not claim the service was cancelled**.
2. **Circular Coonatra 300–301:** the operator says its contract **00615CT** for integrated fare collection has been under renegotiation; it refers to changed dispatch frequencies of competing electric vehicles and a joint working group activated **20 February 2025**. This is **not** a new 300/301 numerical interval or definitive route frequency change. Preserve the existing operator **4-minute family average** only as a dated research source; do not pretend that the negotiation altered its own published numeric interval.
3. **Proposed Aguas Frías extension:** operator says an extension of the Circular corridor by ~2km was **submitted for municipal study 7 March 2025**, no approval proven; a proposal is **not** an extra service.

These findings are recorded in [`coonatra_2025_management_report_frequency_caveats.csv`](coonatra_2025_management_report_frequency_caveats.csv), preserving source date, operator claim and implications separately.

## Next targeted work

- Determine day-of-week applicability, origin and direction of the six original Calasanz departure tables, and validate old GIS `310R` versus `310 Metro Rosal`; keep both tables independent.
- For Circular 300/301, reuse the **original city 2025 geometry act** and current operator route website (04:10 first, 21:30 last); do not duplicate four operator family branches.
- For other 65 routes still requiring truly new sources, investigate **Copatra 090/091 and Cootransi/Cootransvi 103/107**, prioritizing original operator or municipal dispatch evidence. No general Moovit route scraping until operator source exhausted.
- Per the user's instruction, source data can be used for **provisional research models** without demanding a legal PP/PVM definition, but route identity, day type and departure direction should remain explicit.

**No changes to GTFS production generator, calendars, trips, or shapes.**
