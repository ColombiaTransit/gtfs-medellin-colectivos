# 6F / 6H frequency and service-window targeted research — 19 November 2026

## Priority and source-selection method

Reviewed existing official route and operator coverage registers for **Copatra**, **Cootranspinal**, **Cootransi** and **Cootransvi** before looking for missing frequency/clock evidence. Repeated municipal original-act URL permutations were **not** performed; the source review already holds 2017 / 2019 / 2020 / 2023 changes with unresolved original numeric schedules.

- **Cootransi** has its own public website [Cooperativa Multiactiva de Transporte La Sierra](https://cootransi-a4fc5c.webnode.com.co/) and a [services page](https://cootransi-a4fc5c.webnode.com.co/servicios/) that confirms community passenger operation, but **does not publish first/last dispatch clock times or numerical headways**. Do not mistake unrelated company phone/office hours for bus operating schedules.
- **Cootransvi** has an independent [official Metro de Medellín Cívica integration announcement](https://www.metrodemedellin.gov.co/al-dia/noticias/cootransvi-cuenta-con-la-primera-ruta-barrial-no-integrada-al-metro-con-recaudo-electronico): 107 actually has **three branches San Antonio / Perlas / Ratón**, served by a shared stated fleet of **25** buses. This establishes three current operational route branches and refutes a six-way identical frequency copy from the legacy ArcGIS map.
- **Copatra / Cootranspinal:** the municipality [Buses directory](https://www.medellin.gov.co/es/secretaria-de-movilidad/transporte-publico/buses-de-medellin/directorio-de-buses/) identifies the companies. No fresh operator-published route/daytime interval table was recovered this pass. The old **SICO UT** 2015 fiches contain `DÍA` and `HMD` *daily service/maximum-demand counts*, **not minute-based headways**; do not use them as such.

## New current public route-frequency candidates

A [24-row research-only table](2026_6f_6h_087_088_091_103_107_public_headways.csv) now preserves all printed weekday/Saturday/Sunday headways **per public service**, without multiplying these over old ArcGIS ramales.

| Agency | Public route | Weekday min | Sat min | Sun min | Verified daytime window |
|---|---|---:|---:|---:|---|
| Cootransi | [103 La Sierra](https://moovitapp.com/index/es-419/transporte_p%C3%BAblico-line-103-Medellin-1642-857167-740711-0) | **3** | **5** | **3–7** | Saturday **05:00–23:00** |
| Cootransvi | [107 Perlas / San Antonio](https://moovitapp.com/index/es-419/transporte_p%C3%BAblico-line-107-Medellin-1642-857167-740712-0) | **4** | **5** | **4–8** | No trustworthy complete end times |
| Cootranspinal | [087 Trece de Noviembre](https://moovitapp.com/index/es-419/transporte_p%C3%BAblico-line-087-Medellin-1642-857167-737559-0) | **4** | **4** | **8** | Saturday **05:00–22:28** |
| Cootranspinal | [088 Enciso / Ladera](https://moovitapp.com/index/es-419/transporte_p%C3%BAblico-line-088-Medellin-1642-857167-737560-0) | **3** | **3** | **3–6** | Saturday **05:00–23:00** |
| Copatra | [091 Los Mangos return loop](https://moovitapp.com/index/es-419/transporte_p%C3%BAblico-line-091-Medellin-1642-857167-737562-0) | **10** | **10** | **10–20** | No trusted full span |
| Copatra | [091 Los Mangos → Carrera 22c](https://moovitapp.com/index/es-419/transporte_p%C3%BAblico-line-091-Medellin-1642-857167-737562-3) | **15** | **15** | **15–30** | No trusted full span |
| Copatra | [091 Carrera 18a loop](https://moovitapp.com/index/es-419/transporte_p%C3%BAblico-line-091-Medellin-1642-857167-737562-2) | **15** | **15** | **15–30** | No trusted full span |
| Copatra | [091 Calle 56a / El Pinal loop](https://moovitapp.com/index/es-419/transporte_p%C3%BAblico-line-091-Medellin-1642-857167-737562-1) | **5** | **5** | **5–10** | Saturday **05:00–21:30** |

**Important anomaly:** Moovit's **05:00–04:55 next-day** / **05:03–04:59 next-day** clock pairs recur across unrelated 087/088/091/103/107 routes. The start times and frequency cells were retained as **secondary research candidates**, but nearly-24-hour service spans were discarded as implausible without independent evidence. These end values can arise from automatic pseudo-frequency synthesis rather than verified actual overnight dispatch. **No claim that those companies operate 24 hours.** Saturday's explicitly bounded end at 21:30, 22:28 and 23:00 is distinguishable but remains a third-party report.

### Conflict for Copatra 091

An older [TransitRun 091 Calle 56a branch](https://transitrun.com/es/public-transit-line_091_58759) reports actual bounded hours **Mon–Fri 03:35–22:00 every 5 min; Saturday 04:00–21:30 every 5 min; Sunday 05:00–22:00 every 10 min**. Moovit's later public **Calle 56a** branch instead reports a first time of 05:00 and 5-min/5–10-min headways with suspect end times. The older times are retained separately as an **alternative dated third-party source, NOT confirmed 2026 truth**, in [`copatra_091_el_pinal_older_daytype_windows_source_conflict.csv`](copatra_091_el_pinal_older_daytype_windows_source_conflict.csv). Do not resolve source conflict by just taking the older more plausible window.

### Route-code caution

- Official Metro announcement identifies 107 as **three 2024 operating branches**. The old snapshot contains **six different ArcGIS 107 IDs** and those cannot be interpreted as six routes each at 4-minute weekday intervals.
- Old ArcGIS **103** includes four physical variants (Sierra, Sierra Minorista, Mirlas, Mirlas Minorista), but Moovit publishes one public 103 line. Three-minute service **does not apply to all four independently**.
- Old Cootranspinal 087 includes a separate 087 special-hour variant; no specific operator service restriction has been proven for that branch.
- Old Copatra **091 Sucre / Llanadas** does not automatically match four different 2026 Moovit public 091 variants (Los Mangos, Carrera 22c, Carrera 18a and Calle 56a). The service code alone is insufficient to assign four copied headways to two historical shapes.
- The original municipal 2017–2023 amendments remain a valid separate source chain; we are using provisional operating headways in user-approved research models, not falsely labelling these as original official intervals.
- Sunday is **not automatically a Colombian holiday** in Moovit source terms.

## Next targeted frequency priorities

1. Locate actual operator trip sheets/service office timetable or recent PSO for **103** and **107** for trustworthy last departures and branch split. Cootransi website is only operational confirmation.
2. Investigate the **four independently shown 091 branches** and Copatra old 090/091 families for branch matching and less synthetic published operating windows.
3. Check other sources for Cootranspinal **087 special** and **088** first/last weekday/Sunday time; currently 087/088 complete hours are only plausible for Saturday.
4. Continue to newly uncovered operators, not to already fully digitized original 2025 ASTREA pages.

**GTFS generator and release unchanged.** No unauthorized adoption of near-24-hour, duplicated family or route-identity-uncertain schedules.
