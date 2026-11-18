# System 6G — Transacoop / Santa Elena, source separation and route-family audit (18 November 2026)

## What has been checked
- The **nine** independent historical ArcGIS geometry IDs `90257`–`90265` are all labelled `98 Directa 1`–`98 Directa 9` and all list **Transacoop**, but are **different branches of route family 098**, not evidence of nine equal simultaneous 30-minute services.
- The 2024 [Parque Arví visitor brochure](https://www.medellin.travel/wp-content/uploads/2024/09/Parque-Arvi.pdf) says buses depart Placita de Flórez for Santa Elena, some going directly to Arví; it mentions the first departure 06:00 and an approximate 30-minute interval. This is *tourism guidance for a shared corridor*, not a current legal permit or separate schedule for nine route shapes.
- A historical [Santa Elena operating study transcription](https://pdfcoffee.com/encuesta-origen-destino-carga-pdf-free.html) separately describes **Transacoop** observations around 2008 of approximately 15-minute morning departures and 10-minute departures after 13:00 for an Arví-area operation. It records an **operational proposal** around 2011 of 11 departures/hour towards Medellín at high-demand periods and proposals for three rural feeders. Neither the historical observation nor the proposal is the current 2026 timetable.
- **Critical misattribution:** the same historical study's **25-minute weekday / 20-minute weekend departures, 05:20–20:00, refer to the separate company Coopetransgur of Guarne**, NOT to Transacoop. The fact this description is adjacent to the Santa Elena section is not enough to make it a 098 headway. This trap is explicitly recorded in [`system_6g_transacoop_source_leads.csv`](system_6g_transacoop_source_leads.csv).
- The 2025 act `202550091562` was quoted in a 2026 fare story concerning event fares for Transacoop. A **fare exception does not license any minutes-based headway**.

## Mapping of all nine ArcGIS route IDs

[`system_6g_transacoop_098_nine_variants_evidence.csv`](system_6g_transacoop_098_nine_variants_evidence.csv) enumerates the nine separate branches: 90257 Mazo–Las Brisas, 90258 Barro Blanco–Las Brisas, 90259 Las Brisas, 90260 Perico–Las Brisas, 90261 El Plan–Las Brisas, 90262 Piedras Blancas, 90263 Barro Blanco, 90264 El Cerro–Las Brisas and 90265 Piedras Blancas–Las Brisas. Each retains the full legacy code `98 Directa N`.

**Unresolved:** authorized current departure counts / frequencies *by branch and direction*, operating days, morning/evening trip boundaries, 2025/2026 legal effectivity and variants that may have merged since the ArcGIS snapshot. A route-family-level 2024 tourist approximation must not become nine 30-minute GTFS frequencies.

## GTFS disposition
No GTFS import, no invented clock-times or services; all nine spatial IDs remain distinct as route-identity candidates. Continue with modern operator-provided schedules or municipal acts where available. Do **not** research or reread the old Santa Elena study again to guess present-day times.
