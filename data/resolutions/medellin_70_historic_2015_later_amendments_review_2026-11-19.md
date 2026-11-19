# Medellín Urbanas — 70 historic 2015 fiches, later-decision check (19 November 2026)

## Scope and decision

The **70** archived ArcGIS routes in the 18 November 252-route audit marked `historic_2015_fiche_usable_only_as_provisional_fallback_after_amendment_check` have now been reconciled against the existing **visually verified 2015 Gaceta 4325/4326/4327 fiche registers** and the **previously indexed 2017–2024 operating and route change decisions**. No new Gazette PDFs were downloaded, and 2015 times have not been asserted to be in force in November 2026.

**Two parked routes remain explicitly excluded from active work:** `90290 / 195ii / Tax Maya` and `90370 / 082 V-LA PILOTO / Flota Nueva Villa`. The active working set is **68** archived route IDs.

The complete, source-linked comparison is [medellin_70_historic_2015_later_amendments_audit_2026-11-19.csv](medellin_70_historic_2015_later_amendments_audit_2026-11-19.csv).

## Outcome

| Preliminary research classification | ArcGIS IDs | Treatment |
| --- | ---: | --- |
| Historical source candidate without *identified route-specific later operating replacement* in the bounded index | **34** | Historical-only provisional candidate; use published day/HMD and service windows for research, subject to legal effectivity screening |
| Historical variant/source ambiguity | **10** | Preserve multiple source possibilities; resolve branch or direction before applying |
| Historic fiche with printed anomaly or warning | **11** | Keep source transcription but do not adopt abnormal values without context/QA |
| Later operating decision affecting route or service | **13** | Withhold 2015 current-frequency assertion; check indexed 2017–2024 effect and original timetable tables |
| Parked by user | **2** | Do not continue research |
| **Total** | **70** | **68 active, 2 parked** |

All **70** have at least one page match against existing visually checked historical registers. This says the *2015 source was verified*, **not** that the current line variant and legal service remain unchanged.

The CSV records for each source fiche: printed general/weekday and daytype window candidates; weekday, Saturday, Sunday and holiday **normal/HMD interval pairs**; relevant later resolution numbers; source URL; warning/crosswalk status; and explicit `gtfs_automatic_import=no`.

## Later-source checks already performed

- **Coonatra 242/243/311 variants**: later indexed decisions include **389/2017**, appeal **201750008728**, and **202150129154** for 311 variants. **201950089585** changes geometry of 242, not independently proven new numerical headways. Inspect field-level changes before accepting old 2015 frequency.
- **Conducciones América 201/201i/202i/221/222**: the 2018 operating act **201850015842** is relevant; **201950052919** affects additional specific route families. **202150006316** and **202350001335** are geometry/stop changes and must not be treated as automatic headway replacements. Original 2018–2019 tables are still missing.
- **6A SICO operators (Flota la V / Copatra / Flota la Milagrosa / Cootranscataluña / Coopcerquin)**: registered joint-approval **201950070736** is a later system-wide event; it is *not* proof of changed frequency. The original 2015 097 and 110 printed anomalies remain explicitly flagged (e.g. 10:30 weekday end and zero HMD values). Later acts may affect any of these lines; bounded indexing cannot prove they are unchanged.
- **Tax Maya 195ii** and **Flota Nueva Villa 082 PILOTO**: parked; no renewed source lookup.

## Interpretation

**34 provisional candidates** means only that the available comparison found no specifically identified later *frequency replacement* in the already indexed data, not that the frequency is legally confirmed as current. These historical values may be used as **clearly labeled research defaults** only. The original source's `DÍA` and `HMD` columns are dispatch headways in minutes; do not mistake the separate `FRECUENCIAS DE OPERACIÓN` trip counts for headways.

Do not turn HMD into exact PP peak hours without the accepted **separately labeled provisional model**; maintain published weekend and holiday distinctions. Do not duplicate a shared 2A/6A/8A system fiche across multiple operating companies or variants.

## Next actions

1. Resolve the **13 operating-act blocker routes** using the existing legal chain and source artifacts; prioritize 2018 Conducciones América and 2017/2021 Coonatra originals instead of researching already verified 2015 pages again.
2. Resolve the **10 variant ambiguity** items with existing ArcGIS route names and directional shapes.
3. Examine only the **11 historical print anomalies**, keeping the original source numbers unchanged.
4. Retain the **34** as *2015 provisional candidates*, preserving citations and daytype-specific timings; do not promote to a verified modern schedule or GTFS until applicability is checked.

No GTFS generator, operator schedules or production frequency files have been changed.
