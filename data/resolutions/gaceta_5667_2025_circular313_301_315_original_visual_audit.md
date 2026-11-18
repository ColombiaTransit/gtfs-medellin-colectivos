# Gaceta Oficial 5667 (2025) — original Circular 313 and 301/315 audit

**Review date:** 18 November 2026. **Status:** primary municipal 67-page PDF recovered, text extracted and legal/interval tables visually checked. **GTFS changes:** none.

## Original municipal publication

- Original source: [Gaceta Oficial 5667, published 24 September 2025](https://www.medellin.gov.co/statements/innovaciondigital/gacetas/historico-mercurio/descargar/202000087050) from the district's [historical Gaceta search](https://www.medellin.gov.co/statements/innovaciondigital/gacetas/historico-mercurio).
- The official public lookup uses `numero_acto=202550076168` and returns Gaceta 5667, document ID **202000087050**. The ID comes from the *actual result row*, not a guessed file path.
- PDF magic header verified, **67 pages**, SHA-256 `e2265c4e5f454dad8e858909ba48d3a640e8237f23c6a67bf5423006df6af499`. Original PDF retained only as a transient, 7-day GitHub Actions artifact in [run #44286122403](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44286122403); committed source tables, pages, checksum and URL here, not copyrighted original PDF bytes.

## Resolución 202550076168 (19 September 2025): Circular 313

Original operative clauses and printed table numbers visually verified on **Gaceta PDF pages 55–57**.

- **Article 1** officially restructures jointly operated Circular 313.
- **Article 2** explicitly retains **one coordinated joint operation**, by Compañía Metropolitana de Buses S.A. (Combuses), Cooperativa Metropolitana de Transportadores del Valle de Aburrá Ltda. (Coometropol), Coinvetrans S.A.S. and Autobuses El Poblado Laureles S.A. This is **one joint legal service** with separate contributor/operator attributions; no multiplying the service by four agencies.
- **Article 3**: code `313`; north-to-south `GTPC 29903` and south-to-north `GTPC 49904`, both stated at **20.65 km**. They describe **two directions** of a shared route and are not two sets of four operators.
- **Article 4**: published service windows **Monday–Friday 04:00–22:00**, **Saturday 04:00–22:00**, **Sunday/holiday 04:45–21:00**.
- **Article 5**: maximum legal dispatch intervals expressed as **minutes**. Period order = peak / extreme valley / midday valley:

| Day type | Peak | Extreme valley | Midday valley |
|---|---:|---:|---:|
| Monday–Friday | 7 | 15 | 8 |
| Saturday | 7 | 15 | 8 |
| Sunday/holiday | 12 | 15 | 12 |

The numerical cells are visually printed once spanning GTPC `29903` and `49904`; **do not double the interval-based supply** or silently generate independent return-direction departures. For GTFS, keep both direction geometries and times separate when actually confirmed.

- **Article 6** defines transport fleet capacity per operator: Combuses 6–7, Coometropol 6–7, Coinvetrans 1–2, Autobuses El Poblado Laureles 3–4 (total 16–20). These are **fleet vehicles**, not headways, and are intentionally ignored by the GTFS generator. Provenance saved in `2025_circular313_joint_operators_capacity.csv`.
- **Article 8 footnote**, PDF p56: `PVE` (extreme valley) is **before 04:30 and after 20:30**. `PP` means peak and `PVM` midday valley. Exact peak-vs-midday clock boundaries **are not defined** there; do not invent those clock boundaries for `frequencies.txt`.
- **Article 11**, p57: expressly repeals **Resolución 177 of 3 March 2017** and all prior operational authorizations/changes for Circular 313 covered by the decision. Old frequency values for the service cannot be used over this 2025 act.

The old ArcGIS identity candidate is `id_ruta=90004`, `codigo_ruta=313`, recorded with north/south trip-direction geometry **not yet matched** to the legal diagram annex. No claim that no 2026 act superseded the resolution outside indexed ASTREA searches.

**Machine-readable records:** [`2025_circular_313_official_joint_service.csv`](2025_circular_313_official_joint_service.csv), [`2025_circular313_legal_gtpc_directions.csv`](2025_circular313_legal_gtpc_directions.csv), [`2025_circular313_joint_operators_capacity.csv`](2025_circular313_joint_operators_capacity.csv).

## Resolución 202550076174 (19 September 2025): Circular 301 and 315

Original printed **Gaceta PDF p65**, operative Article 1 and paragraphs visually verified:

- Circular **301** is operated by **Coonatra** and Circular **315** by **Santra**. The act changes their paths and recognizes a specific existing stop for **315** on **Diagonal 75 between Transversal 41A and Carrera 80**.
- Two route maps are legally incorporated as annexes, but their line geometry has **not** been independently checked against ArcGIS.
- **Article 1 paragraph 3 explicitly states that the other operational conditions — including frequencies, service hours, fleet capacity, vehicle class and fare — are not modified**. No new legal interval or departure is authorized by this act.

Both directions remain identifiable by old ArcGIS `90006` for 301 and `90015` for 315. The explicit *no change in frequency* has been recorded in [`2025_coonatra_santra_301_315_geometry_legal_register.csv`](2025_coonatra_santra_301_315_geometry_legal_register.csv).

## Provenance and generator safety

Official Gaceta 5667 and its two acts were recovered via the municipality's `historico-mercurio` search; no ASTREA filename guessed. Secondary vLex references in `priority_source_documents.csv` and `2025_amendment_route_scopes.csv` were replaced by the verified official download link.

- Mark exact 2025 legal **maximum headway figures for 313** as reviewed, but **current 2026 effectiveness is not exhaustively proven** and full periodic clock boundaries are incomplete.
- Mark 301/315 as **geometry-only change; original hours/headways unchanged**.
- Keep existing 2017–2024 official-report index sources for unrelated operators; the new historic Gaceta portal gave positive 2024–25 results but no search results for the tested earlier 2018–23 act numbers. This is not evidence those acts did not exist.
- Do not alter GTFS generator, create duplicate agencies/trips, or silently replace historical ArcGIS geometries.
