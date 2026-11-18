# Research update: historical official acts 2017–2024 and newly recovered operator fiche (18 November 2026)

## Scan of 38 already indexed acts

[GitHub Actions run #44279564844](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44279564844) checked the two conventional ASTREA URL variants for **all 38** acts in `2017_2024_act_chain_index.csv`. **Two** full-text original candidates were recovered and checked for the act number; the other **36** returned 404 at tested patterns. These 404s are **not evidence that the underlying decisions do not exist**, and this bounded URL-pattern check is not an exhaustive gazette or archive search. Direct links and outcome markers have been appended to the original 38-row chain index.

### 202150181337 / Coonatra

The official [ASTREA 2021 original](https://www.medellin.gov.co/normograma/docs/astrea/docs/r_smmed_181337_2021.htm) is recovered. The 2021 Gaceta 4911 original (previously reviewed) authorizes specific changes involving Coonatra's 300/301 integration; it **does not authorize the Tax Maya 195ii frequency** just because the 195ii route appears in context. No separate GTFS headways from this source.

### 202450030616 / shared route 229

The official [ASTREA 2024 original](https://www.medellin.gov.co/normograma/docs/astrea/docs/r_smmed_30616_2024.htm) has now been checked, using [run #44279871150](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44279871150). It concerns the jointly operated route **229i Barrio Nuevo**, with **Tax Maya, Metrosan and Conducciones América** (the system-level sheet also names other 8A operators, which should not automatically be added as route-level co-operators). The historic fiche prints **118 DÍA / 10 HMD** for weekday and Saturday, and **59 DÍA / 5 HMD** for Sunday and holiday in the table headed `FRECUENCIAS DE OPERACIÓN`: these are **service operation counts, not headway minutes**; the text does not establish a current 2026 frequency.

**Critical legal supersession:** ASTREA explicitly annotates **the 2024 act as repealed by Article 11 of 202650039611/2026**. The latter official [2026 act](https://www.medellin.gov.co/normograma/docs/astrea/docs/R_SMMED_39611_2026.htm) already has the later route-229i operating clock windows and maximum headway fields in `route_229i_2026_official_intervals.csv`. The [shared-route provenance](shared_route_229_provenance.csv) now records the 2024 original source, numeric-count semantics and 2026 repeal. **Never import 2024 operation counts or geometry on top of the 2026 act**. Original code `229i` is repeatedly named despite source editorial `299i` in a part of the 2024 operative text.

## Coopetransa 069 / 2023 operator-published fiche

A **new, directly accessible publisher original** was recovered: [Coopetransa's 2023 management report](https://coopetransa.com/wp-content/uploads/2024/05/3-Informe-de-gestion-ano-2023.pdf), printed p. 23 (PDF page index 22), issued/presented in 2024. The page was visually checked against the printed report, which explicitly attributes a reproduced technical fiche to **Resolución 202350107467 of 28 December 2023**, amending **201750008183/2017** for urban **system 6E, route 069 El Jardín**. This is an **operator-published reproduction** of municipal-approved conditions, **NOT the original municipal act**.

The technical fiche states:
- **Convenio TRESCOOP 6E (Unión Temporal)**, member companies **Coopetransa, Cootransmon, Cootranscol**. The route-specific service operator printed in the fiche is **Coopetransa**; do not duplicate the 069 timetable per consortium member.
- **069 El Jardín** with ArcGIS old ID **90238**, general published service window **03:00–23:00**; route origin **Carrera 32 entre calles 91 y 92 (Billares)**; route length **16.08 km**.
- Printed `FRECUENCIAS DE OPERACIÓN` (counts): weekdays **228 DÍA / 24 HMD**, Saturday **228 / 24**, Sunday **137 / 15**, holidays **137 / 15**. **These are not minute headways**, and do not define peaks by clock time.
- The report identifies a distinct **alternate route 069 El Jardín–La Cima**, old ArcGIS ID **90376** code `069 Ramal`, with a reported vehicle allocation of 18–20 buses. The printed 069 main-route numbers **do not demonstrate a separate schedule for the ramal**; avoid splitting or doubling its service without route-specific timing evidence.

All source fields, source type and route-specific caveats have been saved in `coopetransa_069_2023_operator_report_legal_fiche.csv`. This adds previously unavailable original technical **content** to the research backlog; the municipal original **202350107467** itself remains unresolved, and no claim that the 2023 permit is unchanged in 2026 is made.

## Follow-up priorities

1. Route-specific legal changes and timing windows from still-unretrieved originals, prioritizing **Cootrabel 202350107412**, **Conducciones América 201850015842 / 201950052919**, and **Cootransi/Cootransvi 202050056226**.
2. Check 069 Ramal source schedules or geometry *only if relevant existing route source data is incomplete*; never assume that the parent 069 timetable can be duplicated.
3. Retain original 2024 route 229 as a **repealed historical legal source**, with 2026 229i active source as the higher-priority legal record subject to regular status checks.

No GTFS generator updates, no retroactive headway interpolation and no automatic removal of routes.
