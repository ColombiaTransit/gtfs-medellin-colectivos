# Targeted legal chains — Cootrabel, Conducciones América and 6H (18 November 2026)

## Purpose and evidence boundaries

The existing official Medellín Secretaría de Movilidad management report provides **act descriptions** and route families, but it is **not the same as the original legal acts**. Previous targeted exact-number searches and the historic ASTREA URL-pattern scan did not retrieve the original full texts of the priority 2017–2023 service decisions. **Do not fill missing tables from a management summary.** The new route-level [28-row register](2017_2025_three_operator_chains_route_review.csv) consolidates source chain, precedence cautions and each old ArcGIS identity without redoing the already completed original-act search.

### Cootrabel — 2 ArcGIS route IDs plus 2025 municipal pilot

- Older source chain: 189/2017 → 202050048359/2020 → 202150163403/2021 → **202350107412/2023**.
- Municipal management report explicitly describes **202350107412/2023** as repealing **202150163403/2021** and changing 170/172/178 services. The original 2023 schedules, code/variant scope and headway table have **not** been recovered.
- ArcGIS snapshot: **90141 / 170 Belén Las Playas**, **90374 / 172-178 FUSION Belén la Gloria**.
- **Newer original municipal primary publication:** [Medellín, 13 November 2025 — nueva ruta 178 Nuevo Amanecer–Centro](https://www.medellin.gov.co/es/?p=475937). The city's press release explicitly calls this a **pilot**, starting 14 November 2025, daily **04:20–21:20**, announced **20-minute headway**. It describes connection from Nuevo Amanecer (Altavista) into Medellín Centro. The published pilot route may be a new/reworked service and is **NOT safely identical to old 90374**.
- A [third-party Moovit stop listing](https://moovitapp.com/index/es-419/transporte_p%C3%BAblico-Centro_Administrativo_La_Alpujarra-Medellin-site_8969876-1642) updated **14 November 2026** still includes route 178 towards Nuevo Amanecer. This supports *operational continuation* rather than simply treating pilot traffic as expired, but **does not prove formal extension, permanence or unchanged 20-minute headway**.
- The source evidence is recorded in [`cootrabel_178_nuevo_amanecer_2025_pilot_evidence.csv`](cootrabel_178_nuevo_amanecer_2025_pilot_evidence.csv). [Issue #19](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/issues/19) tracks exact pilot authorization/extension and geometry-to-ArcGIS checks. **No new GTFS service from pilot figures.**

### Conducciones América — 16 ArcGIS IDs

- Primary legal decisions indexed from municipal report: **201850015842/2018** operating conditions and **201950052919/2019** affecting **202, 220, 223, 240**.
- Subsequent reported changes: **202150006316/2021** for geometry of **223, 201i, 221i**, **202150044996/2021** for route **240** geometry, and **202350001335/2023** for **202i** stop changes.
- Sixteen older ArcGIS route IDs and source-chain priorities have been preserved in the new row-level register. 2019 act scope is *not* proof that every route in the system changed its frequency. A later stop change/geometry amendment is *not* a later timetable unless its actual operative articles say so.
- The operator's historical blog and newer third-party schedules may give corroborating route existence, but they cannot replace the original municipal timetables with unverified frequency numbers.
- **Status:** original 2018/2019 numerical intervals remain missing, and any unchanged/changed 2026 effectivity is unproven. Do not silently import 2015 values.

### Cootransi + Cootransvi — 6H shared system, 10 ArcGIS variants

- Main source chain: **201750022231/2017** shared system 6H → **201950077279/2019** amendment → **202050056226/2020** affecting **103 Las Mirlas/La Sierra** and **107 Perlas/Ratón** → **202350008449/2023** modifying route paths.
- ArcGIS has **4 Cootransi 103 variants** and **6 Cootransvi 107 variants**. Variants are not ten independent copies of the *same legal headway*; preserve the actual operator, itinerary, direction and the common system agreement without multiplying departure counts.
- The **2023** subsequent act is indexed as a geometry amendment. No proof that it changed 2020 service headways, and no original 2020 schedule has been recovered.
- **Status:** system and route identities indexed; original 2020 numerical tables unresolved; no production headway values.

## Already done and intentionally not repeated

The municipality's historical ASTREA URL-pattern scan already checked 38 decision IDs and found only two recoverable originals. Exact-number public search for the three priority original acts was also previously recorded as not yielding direct originals. The new work adds the authoritative 2025 Cootrabel pilot announcement, contemporary 2026 third-party operation evidence, and a **route-specific decision register** with status and source caveats. It does **not** claim that the older missing original acts or their exact frequency tables were recovered.

## Next useful work without repeating old searches

1. For Cootrabel, compare **178 Nuevo Amanecer–Centro** with archived route geometry/stops for 90374 and seek the pilot's authorizing/extension act; if unavailable, keep the current operation status separate from legal authorization.
2. For America and 6H, use actual original resolutions or full official Gazette pages when discovered; until then preserve the route-chain and do not synthesize a timetable.
3. Continue the operator backlog (Cootrabel, America and 6H now have explicit route-level pending status) rather than reopen previously validated 2015 source extraction.

**GTFS generator unchanged.** No invented timetable values, no false route cancellations and no duplicated joint-operation services.
