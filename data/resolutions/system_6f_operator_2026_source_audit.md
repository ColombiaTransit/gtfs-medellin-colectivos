# System 6F — current Cootransmallat operator evidence and ArcGIS identity register (18 November 2026)

## Sources and preservation rules

- **Direct 2026 operator website:** [Cootransmallat](https://www.cootransmallat.com/), checked 18 November 2026. States daily service on its two main 105/106 routes and three principal departure origins. Distinguishes ordinary main routes from time-restricted variants and explicitly says the extra mapped paths are **not independent lines**. This is **operator-published operational information**, not a municipal legal resolution.
- **Municipal depot listing:** [Alcaldía de Medellín — depósitos de buses](https://www.medellin.gov.co/es/secretaria-de-movilidad/transporte-publico/buses-de-medellin/listado-de-depositos/) identifies Cootranspinal's El Pinal depot and routes 087/088; depot records are **not schedules**.
- **Official municipal management report:** existing [6F act-chain index](system_6f_legal_chain.csv) references SITRANSCO approvals and amendments: 201750005329/2017, 202150041167/2021, 202350086596/2023 (Cootransmallat) and 202350089536/2023 (Cootranspinal). These direct original acts **remain missing**; the index may not be treated as numeric operational evidence.
- **Route identity:** `data/medellin/routes.csv` and the new [14-variant 6F ledger](system_6f_2026_operator_arcgis_family_register.csv).

## Verified operator-published current service parameters (105 and 106)

| Operator family/origin | Published weekdays | First → last (general) | Destination rule |
|---|---|---|---|
| 105 Golondrinas | Monday–Sunday | 04:00 → 23:30 | Centro/Maturín ordinary; Minorista by day, Bolivia after 18:00 |
| 105 El Faro | Monday–Sunday | 04:00 → 23:30 | Same day-versus-evening destination concept |
| 106 Tres Esquinas | Monday–Sunday | 04:00 → 23:30 | Same day-versus-evening destination concept |

The service window applies to the **origin family**, **not each eight individual ArcGIS variant geometries**. The operator explicitly says additional mapped paths operate only in special time windows / dispatch schedules and **are not independent routes**. No verified separate headway or peak-period times are posted for these variants. Do not generate daily full-window departures for each ArcGIS shape.

## All 14 older ArcGIS 6F route IDs covered

| Operator | Unique ArcGIS IDs | Route family | Evidence classification |
|---|---:|---|---|
| Cootransmallat | 8 | 105 Golondrinas/El Faro; 106 Tres Esquinas | Current direct operator service-hour and destination-switch source |
| Cootranspinal | 3 | 087/088, including special 087 variant | Official municipal depot route identification, no numeric service tables |
| Copatra | 3 | 090/091, including different 091 destinations | Legacy ArcGIS routes + historic indexed legal chain, no numeric service tables |

**Operational mapping to existing ArcGIS snapshot:** 105 Golondrinas normal `90247`, Minorista `90249`, special `90250`, nighttime `90251`; 105 El Faro `90252`; 106 Tres Esquinas normal `90254`, Minorista `90255`, Minorista special `90256`. The term `horario nocturno` for 90251 and the published Bolivia-after-18:00 rule form a plausible pairing **but geographic correspondence to the Bolivia destination is not yet independently verified**. The exact per-shape start/end is unknown.

The Cootranspinal `90239`, `90240`, `90241` and Copatra `90242`, `90243`, `90244` ArcGIS ID/codes are retained with no timetable inferred from the Cootransmallat website. Shared 6F SITRANSCO cooperation does **not** imply Cootransmallat's published hours/headways apply to other operators, nor should the same service be cloned for every company.

## Open actions for later GTFS conversion

- Confirm the route/direction geometries of each timed 105/106 variant relative to the 18:00 switch, especially 90251, 90250 and 90256.
- Seek actual scheduled departures or legal minute intervals for the individual 105/106 services; only origin-family operating windows are verified.
- Retrieve the latest original legal numeric conditions for Cootranspinal/Cootransmallat, not repeated exact-number URL guess searches.
- Interpret route-level 2017–2023 legal modifications only on documented fields; do not overwrite by older historic 2009/2015 numbers.
- Do not double routes through shared SITRANSCO agency or shape variants; retain source-specific operator attribution.

**Current GTFS disposition:** no new trips, no headway generation, no generator changes. This source resolves coverage and destination-time semantics; it does not finish legal schedule verification.
