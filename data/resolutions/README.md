# Medellín urban bus resolutions: source-first evidence register

## Latest consolidated register (18 November 2026)

**Original Gaceta 5671 confirmed:** [verified 62-page original and selected visual QA](gaceta_5671_2025_original_pdf_visual_spotcheck.md) include all four 2025 acts; `TRONCAL 65` and `TRONCAL 73` have legally published maximum interval triples (not missing), with script assertions and corrected central registers. Seven veredal route records publish services per day rather than minutes. Source-only 86 ASTREA records now classify as **50 maximum-headway, 8 Metrosan paired return rows, 11 fixed rural departures, 10 standalone corridor entries without headway tables, 7 veredal daily-service counts**. Including the two separate joint Circular313 GTPC directions, the central consolidated register has **88 source records**, not 88 independent GTFS services. [Issue #12](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/issues/12) tracks remaining old originals and legal applicability; both original 2025 Gacetas are now recovered.


**New original recovered:** [Gaceta 5667 Circular 313 and 301/315 original audit](gaceta_5667_2025_circular313_301_315_original_visual_audit.md) closes previously open 202550076168 source gap. Circular 313's one shared 4-operator service uses validated official 2025 maxima and GTPC direction pair; frequencies/hours of 301 and 315 are expressly unchanged in 202550076174 Art1 para3. Precise GTFS period/shape mapping and current 2026 applicability still require separate checks.


**Read first:** [CONSOLIDATED_RESEARCH_STATUS_2026-11-18.md](CONSOLIDATED_RESEARCH_STATUS_2026-11-18.md) and [2025_legal_to_arcgis_consolidated_register.csv](2025_legal_to_arcgis_consolidated_register.csv). The latter now has **88 source-direction records: 86 from four official 2025 ASTREA resolutions and 2 GTPC directions of recovered Circular 313 in official Gaceta 5667**, keeping legal GTPC, route code, service windows, original day-specific intervals/counts/fixed departures, historical ArcGIS candidates, confidence and `automatic_gtfs_import=no`. These are research records, not 86 independent currently operative GTFS routes.

The [Castilla 34-variant reverse check](2025_castilla_34_legacy_arcgis_reverse_review.csv) conservatively flags code/name mismatch `289`, ambiguous variants and cases without defensible links. [Metrosan](2025_metrosan_legal_to_arcgis_crosswalk.csv) and [Salud-Hotelera](2025_salud_hotelera_arcgis_code_mapping.csv) retain their own historical ID mappings. [Coonatra/Santra 301/315](2025_coonatra_santra_301_315_geometry_legal_register.csv) identifies geometry-only 2025 route amendments without new inferred headways. Original ASTREA links replace secondary Gazette index URLs in `priority_source_documents.csv` and `2025_amendment_route_scopes.csv`; the legacy ArcGIS legal-review action queue has also been updated to stop requesting already recovered acts. Existing TRSC website schedule photos are not to be re-researched; their 2025 crosswalk is tracked in [GitHub issue #18](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/issues/18).

The targeted official 2026 ASTREA scan read 25 indexed Movilidad acts; it is **not exhaustive proof** that a 2025 authorization remains unamended. Original 2015 fichas remain historical, 2025 period boundaries and modern shape/direction matching require review, and the 2025 Circular 313 original (202550076168) has now been recovered and visually verified from Gaceta 5667. Flota Nueva Villa 082 PILOTO 202250106966 remains parked by user instruction.


This research directory is **not consumed by any GTFS generator**. It intentionally separates
published legal schedule data from OCR candidates and from uncertain ArcGIS matches.

## Coverage (17 November 2026)

- `operator_coverage.csv`: one row for **each of the 32 operator names** in
  `data/medellin/routes.csv`, including the count of distinct ArcGIS `id_ruta` values,
  indexed administrative acts, and known 2025 amendments requiring review.
  An **indexed act is not an extracted timetable or proof of current validity**.
- `gaceta_4325_ocr_candidates.csv`: 129 indexed technical fichas from the 336-page
  Gaceta Oficial 4325 (2015), representing 61 unique system-and-route keys.
  18 fiche rows relate to 6C, 21 to 6B, and 90 to 8A.
  **All rows in this file require visual QA before reuse**; the OCR layer contains
  mistaken figures, missing frequency cells, and wrong time readings.
  Even `ocr_candidate_complete` means *all fields were OCR-extracted*, not validated.
  Indexed route codes are positional references pending comparison against actual page headings.
- `gaceta_4325_visual_verified.csv`: **63** fiche occurrences, covering all **61 unique
  system/route positions** indexed for Gaceta 4325; the eight `INTERVALO DE DESPACHO`
  values and printed `HORARIO DE SERVICIO` have been read directly from page images
  (10 initial, 37 second pass, 16 third pass). The remaining **66** OCR candidate occurrences
  are repeat appearances in other resolutions; these repeated source pages still require QA
  if they are to be cited independently. Each verified record contains its PDF page
  and the resolution number. These are **verified as historical official values**,
  not proof that the same timetable was still in force in November 2026.
  Where the source says only a general service window, Saturday and
  Sunday window cells are deliberately left empty.

**Official source:** [Gaceta 4325, 2015](https://www.medellin.gov.co/irj/go/km/docs/pccdesign/SubportaldelCiudadano_2/PlandeDesarrollo_0_15/Publicaciones/Shared%20Content/GACETA%20OFICIAL/2015/Gaceta%204325/4325.pdf).

## Interpretation: important safeguards

1. `INTERVALO DE DESPACHO` is an **interval in minutes**. The separate row
   `FRECUENCIAS DE OPERACIÓN` contains counts and is not a headway in minutes.
2. Every day type has **DÍA** (normal) and **HMD** (Hora de Máxima Demanda).
   Retain both. Do **not** place the HMD figure into GTFS peak windows unless
   the corresponding peak clock windows are documented.
3. `HORARIO DE SERVICIO` is a published service span; it does **not**
   necessarily establish the first or last **departure from every terminus**.
4. A printed end time earlier than the start time (e.g. 03:00–02:00 in 6C)
   signifies service crossing midnight. A later GTFS conversion must
   handle after-midnight times correctly, potentially using GTFS hours >24.
5. Acts covering the same route system can repeat the same technical fiche.
   Do not duplicate the service merely because the fiche occurs in
   multiple operator-specific resolutions.
6. The route identity and the official document identity are separate checks:
   confirmed transcription ≠ confirmed modern ArcGIS `id_ruta` match.
7. Later route-specific acts supersede earlier information **for the fields they
   actually modify**. Maintain a chain of amendments, not a blanket
   highest-year overwrite. Old fichas remain historical evidence.

## Verified technical-fiche clusters in Gaceta 4325

| System | Page ranges containing route fichas | Acts | Association / context |
|---|---|---|---|
| 6C | 5–21 and 27–43 (odd pages) | 1042 and 1043 (2015) | ATCEX C6; participating transport companies |
| 6B | 58–70, 78–90 and 124–136 (even pages) | 1160, 1161, 1162 (2015) | UT Sistema 6B, multiple operators |
| 8A | 148–236 and 244–332 (even pages) | 1154 and 1155 (2015) | Shared 8A route system; `EMPRESA PRESTA SERVICIO` identifies the actual operator for each fiche |

**Source correction for existing repository notes:** Resolución **1042/2015**
concerns Transconor and system **6C** (see Gaceta p. 3).
The 8A route fichas in this document appear under **1154/2015**
(Autobuses El Poblado–Laureles act, starting p. 145) and
**1155/2015** (Tax Maya act, starting p. 241). Existing comments
assigning the Tax Maya / Coonatra 8A fichas to resolution 1042
should be corrected, without modifying any actual schedule values.

## Cross-checks and original-source anomalies

- **Gaceta 4325, p. 154**: subsection heading explicitly identifies route
  `CSJ22`, but the table's `CÓDIGO` cell prints `CSJ21`, identical to
  p. 152. Registry uses subsection identifier `CSJ22` and records the printed
  conflict in `caveat`. These are distinct route variants, not licence to
  duplicate one timetable.
- **Gaceta 4325, pp. 148/150/152/154**: all four CSJ trunk fichas
  print **03:50–10:40** as the service window. This unusual early end
  has been transcribed as printed, and is explicitly marked for contextual
  investigation before using in GTFS. Do not silently change it to 22:40.
- **Gaceta 4325, pp. 228–236**: five different C23i rural variants show
  an unusually high **weekday HMD interval (60 min) versus DÍA (58 min)**.
  This is how the official tables are printed; avoid correcting it by
  intuition. Their printed `CÓDIGO` cells are used to differentiate
  variants, rather than the common C23i family label.
- **Gaceta 4327**: the official table of contents identifies **13 acts**
  (including 2A, 6A and 6D). See `gaceta_4327_act_index.csv`.
  The individual PDF of resolution 1169 includes technical fichas for
  *several* companies under the 2A system, so an act's title/operator
  must not be assigned to every route fiche inside it. Its timetable
  values have not been visually accepted because image retrieval from the
  municipal server is intermittently timing out.

## Source inventory for 2015/2025 amendments

See `priority_source_documents.csv`. Official individual PDFs have been located for 2015 resolutions 1047 (Flota La V, 34 pages), 1166 (Medellín Castilla, 89 pages), and 1169 (Palenque Robledal, 89 pages); their historical timetable fiches have since been extracted and visually verified (see 1166/1169 cross-index and 1047 visual register). Gaceta 5667's original official PDF is now recovered (202550076168 Circular 313 and 202550076174 geometry-only 301/315); the five other 2025 original ASTREA texts for Gacetas 5667/5671 are also available and extracted in source registers. Current legal numeric QA remains separate. These later acts must be reviewed before interpreting 2015 values as current.

**OCR QA example:** the first raw OCR pass read the weekday DÍA interval for Gaceta 4325 p. 172, route 191, as 5 minutes; the printed dispatch table shows **6 minutes**. The visually verified record uses 6. OCR candidates are never approved merely because their eight numeric fields appear complete.

**Interpretation for the 2015 system 6B:** some route fichas explicitly have different published service windows for weekday, Saturday and Sunday/holidays, all recorded in their respective columns, whereas most 6C and 8A fichas state only a general window. Do not infer a day-specific first/last departure when the source does not specify it.

## Gaceta 4327 recovery and 6A OCR-text candidate register (2026-11-17)

- `gaceta_4327_res_1047_text_candidates.csv`: **11 indexed fiche occurrences**
  from Resolución **1047/2015** (Sistema 6A, SICO UT; municipal PDF),
  including separate printed 097 variants. Text index supplies possible
  service windows and, for some fichas, eight DÍA/HMD dispatch intervals.
  **Every row is `indexed_pdf_text_unverified`** until the original
  PDF page image is checked. Blank interval cells for routes 110/111
  reflect demonstrably corrupted extracted text, *not zero service*.
- Suspicious printed/indexed values are explicitly flagged: route 097
  weekday end 10:30, route 113M weekday HMD interval 2 minutes, and
  confusing 113B/113M OCR route labels. There is no automatic repair.
- `official_pdf_sources.json`: four exact **official** PDF URLs for
  complete Gaceta 4327 plus Resoluciones 1047, 1169 and 1166.
- `scripts/recover_medellin_pdfs.py` with workflow
  `.github/workflows/recover-medellin-resolution-pdfs.yml`: attempts
  bounded parallel retrieval on GitHub runners, rejects HTML error pages,
  stores successful PDF bytes with SHA-256 and optional `pdftotext` output.
  The first successful run produced an **original 30-day Actions artifact**;
  later runs use **7-day artifact retention**. PDFs are never committed to Git. Run manually with **Actions → Recover Medellín
  official resolution PDFs → Run workflow** if the first attempt fails.

**Recovery run succeeded:** [GitHub Actions #44077028708](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44077028708) downloaded **4 of 4 official PDFs** (full Gaceta 4327, resolutions 1047 and 1169 in 4327, and resolution 1166 in 4326). Source archive bytes and SHA-256 checksums are recorded in `pdf_recovery_provenance_2026-11-17.json`. The ZIP artifact expires after 30 days; do not treat the artifact as a permanent substitute for the official PDF links.

- `gaceta_4327_res_1047_visual_verified.csv`: **all 11 distinct printed technical-fiche occurrences** (ten route codes; 097 has two variants) checked **directly from the recovered original scanned PDF**. The source prints 2015 service windows for weekdays, Saturdays and Sundays/holidays and eight intervals per fiche. This register supersedes the provisional OCR candidate file for the same page.
- The indexed text **misread** the Sunday start for route 097 El Vergel (source prints **05:00**) and the weekday HMD for route 112 (source prints **6 min**, not 5).
- **Genuine printed anomalies, not OCR errors**: the first route 097 fiche prints weekday/saturday end **10:30** and weekday DÍA **48 min** while HMD is **4 min**; route 110 actually prints interval values **32,0,42,0,49,1,49,1**, including zero-minute HMD values. These must not be accepted as literal valid GTFS headways just because they are printed. Route 113M prints weekday HMD **2 min**. Route 113's header has **113M** while its technical `CÓDIGO` is **113**; retain the source conflict.
- Printed values are verified **as historical source values**, not automatically current, operator-allocated, or GTFS-compatible. The shared SICO UT listing identifies participating companies but does not mean each runs every trip.

**No source in this section is enabled as GTFS timetable input.**
First review originals and later amendment chain for current applicability.

## Full Gaceta 4327 extraction, original 2A/6D technical fichas (17 November 2026)

The municipal source files were successfully fetched **once** from a GitHub
runner (run [44077028708](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44077028708)).
No PDFs are committed or published as GitHub releases. **Future recovery
artifacts expire in 7 days** and the workflow is **manual only**. The original
run predates the policy change and retains its original artifact expiry; the
Git repository stores only provenance/checksums, source URLs and normalized
research datasets. See `recovered_pdf_provenance.csv`.

- `gaceta_4327_fiche_text_index.csv`: 211 technical-fiche **occurrences**
  across the full 556-page 2015 gazette, using the *existing PDF text layer*
  (no new OCR). Breakdown: **2A 150** (1167:38, 1168:38, 1169:37,
  1170:37), **6A 53** (1046:10, 1047:11, 1048:10,
  1049:11, 1151:11), **6D 8** (1019:4, 1020:4).
  Most occurrences in one system represent repeats of the same route fiche
  inside operator-specific legal acts: **never treat 211 as distinct GTFS routes**.
  Raw interval text and original-page numbers are preserved only as
  `source_pdf_text_index_only_not_visual_validation` candidates.
- `gacetas_4326_4327_visual_verified_2a_6d.csv`: **42 visually
  verified official route fichas**, covering **all 38 unique 2A route
  positions** under Resolución 1166/2015 (Gaceta 4326) and all four
  6D route positions under Resolución 1019/2015 (Gaceta 4327).
  Every record includes the official service window and eight checked
  DÍA/HMD dispatch intervals. Cross-act copies of the 2A fichas in
  Gaceta 4327 are *not* claimed visually verified merely because their
  route identities match; source modifications remain to be reviewed.
  Later legal applicability is not yet established.
- Already verified separately: `gaceta_4327_res_1047_visual_verified.csv`
  covers 11 6A fiche occurrences under Resolución 1047/2015.

**Aggregate historical research coverage:** `verified_2015_system_coverage.csv`
now summarizes **116 verified fiche occurrences / 114 unique system-route
positions** across 6C, 6B, 8A, 2A, 6A and 6D. These are the 2015 source
positions, **not** a count of active/current GTFS routes or a guarantee
that every one of the 32 contemporary operators is fully covered.

**Important finding for 6D:** the actual holiday DÍA headway differs from
Sunday on three fichas: route 081 has **8 vs 15 minutes**, route 082
**8 vs 16**, and route 085 **3 vs 7**. These were read from the official
pages 534, 536, and 538. Do **not** globally model public holidays as
Sunday service. The 085 service span ends at `24:00`, which is not
an invalid printed timetable time. All values remain historical 2015 sources.

**2A operator association:** the same 2A route-system fichas appear in
several acts (1166, 1167, 1168, 1169 and 1170). The 38 unique 2A source fichas are now visually checked in Resolución
1166. The latest applicable legal value for each route must eventually be
selected and deduplicated by route identity,
with participating companies recorded as attributions when shared, not
by creating multiple copies of the same route. Compare amended versions
field by field before deciding whether their values are identical. The
cross-act text layer is not a substitute for final page-image QA.

## Post-2015 legal amendments: 2017–2025 (research on 17 November 2026)

**These registers DO NOT contain new verified frequency or first/last
departure figures.** They identify which previously verified **2015**
schedule fichas require a more recent legal-source check.

- `2017_2024_act_chain_index.csv`: **38 indexed acts** reported in the
  official Secretaría de Movilidad management handover document (source
  URL stored per row), distinguishing operating/service conditions,
  explicit geometry/stop changes, appeals, repeals and joint-operation
  grants. The route-code field is **reported or related**, not guaranteed
  to be verbatim from every original resolution. **None of the 38
  original individual resolutions has been fully reviewed in this batch**;
  citation of their number/subject is not verification of new headways.
- `2025_amendment_route_scopes.csv`: **six numbered acts** from the
  official Gaceta contents for **5667 (2025-09-24)** and **5671
  (2025-09-30)**, represented in **seven rows** because resolution
  202550076174 describes two separate circular routes. Only routes
  313 (Combuses), 301 (Coonatra), 315 (Santra) are matched by **explicit
  code/operator**; the 2A/2B, Salud-Hotelera, Metrosan and Rápido
  San Cristóbal rows list **operator or system candidate** ArcGIS ids
  rather than confirmed route-level amendments.
- `shared_route_229_provenance.csv`: official 2023/2024 sequence
  for the **joint route 229** (Metrosan / Tax Maya / Conducciones América),
  with tentative match to the current ArcGIS **229i, id_ruta 90377**.
  There is no proof yet that every 229 variant or trip should be assigned
  to all three agencies; do not duplicate GTFS service.

### Prioritize original documents that can change GTFS schedules

1. **Gaceta 5671, 202550079848 and 202550079865**:
   Metrosan and Rápido San Cristóbal operating restructurings; do not
   claim their 2015 schedule values remain active without reading these.
2. **Gaceta 5671, 202550076150 and 202550076162**:
   Salud-Hotelera Coinvetrans/Invetrans, and Castilla/Conaltracoop
   system 2A/2B changes. Some candidate ArcGIS routes belong to these
   operators, but the exact affected variants still need confirmation.
3. **Gaceta 5667, 202550076168**: Circular 313 joint operation and
   route restructuring; source is not yet sufficient to derive frequency.
   **202550076174** concerns route paths of Coonatra 301 / Santra 315;
   do not overwrite frequency schedules solely because it is newer.
4. **Cootrabel 202350107412/2023**: explicitly **repeals**
   202150163403/2021 and adjusts the services for **170/172/178**.
   Strong supersession lead, but no new headway/timing table extracted.
5. **Conducciones América 201850015842/2018 and
   201950052919/2019**: service/operating conditions and selected 8A
   routes need review before the corresponding 2015 8A values are used.
6. Follow up historical amendments for **Coonatra**, **Metrosan 229**
   joint operator identities, **6E Coopetransa**, **6H Cootransi/Cootransvi**,
   and **6A SICO UT**.

### Attempted recovery of 2025 primary source PDFs

The manually triggerable `.github/workflows/probe-medellin-2025-gacetas.yml`
and `scripts/probe_medellin_2025_gacetas.py` test **municipal domains
only** for official Gaceta 5667/5671 files. On
[GitHub Actions run 44083111487](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44083111487):

- The municipal **historico-mercurio** landing page was reachable (HTTP 200).
- The historical **Mercurio IndiceServlet and Gacetas.jsp** services
  returned server errors (HTTP 500), including a blocked-URL response.
- The guessed direct 2025 PDF URLs and 2026-style public Gaceta endpoints
  returned HTTP 404. **No 2025 original PDFs were recovered.**
- The new `consulta-publica` archive explicitly says it hosts Gacetas
  **from 28 August 2026 onward**, so it is not a source for 2025.

The repository does not retain the downloaded HTML responses or PDFs:
this Action writes a **seven-day temporary artifact** with a probe
summary and response metadata. Its `workflow_dispatch` trigger is now
**manual-only**, avoiding wasted periodic requests to a known broken
archive. The official 2025 decisions can also be requested from the
Alcaldía's original publication/records custodians; do not use the
secondary contents excerpt as evidence of specific frequencies.

### Source precedence

For the GTFS generator, **only after** independent route-code
reconciliation and source table QA: use the latest legally applicable
act *for the particular field modified*; retain earlier untouched
operating-window or frequency fields when newer acts only change road
geometry; record the new act's effective date and old act's supersession
status. For shared operation, one variant gets one service, with
operator attributions as appropriate. **No active GTFS feed is changed
by these research files.**

## Route-level amendment review and uncovered systems (17 November 2026)

### Current ArcGIS review queue, not a GTFS change

`current_arcgis_legal_review_queue.csv` maps the existing **504 direction
records** to **252 unique ArcGIS route IDs** and assigns *research order*
(not route activity status or evidence of a specific schedule change):

| Queue | ArcGIS IDs | Meaning |
|---|---:|---|
| P0 | 3 | Explicit route-code match in the 2025 gazette contents: Circular 301, 313, 315 |
| P1 | 72 | Listed operator/systems potentially in scope of 2025 acts; exact affected variants not established |
| P2 | 81 | 2017–2024 legal-change leads or 6F/SITRANSCO original text pending |
| P3 | 96 | No direct relevant amendment in the current index, or older-source route matching still needed |

Only **73/252** currently have a candidate exact normalized
**route-code + system** match with a visually checked *2015* fiche.
Even those 73 are **not legally validated as current**; three normalized
route-code keys correspond to different historical route-title variants.
Unmatched does not mean a route lacks legal authorization: system 6F,
the 6G Santa Elena variants and other later routes are outside the
verified 2015 source collections or have non-identical naming schemes.

Every queue entry has `frequency_currently_legally_verified=no`.
No row should be used to suppress a GTFS route, modify its departure
headways, or claim an amendment actually affected it merely because its
*operator* appears in a later act.

### System 6F: SITRANSCO

`system_6f_legal_chain.csv` identifies **14 historical act references**
from 2009–2023 for **Cootransmallat, Cootranspinal and Copatra**.
The official Secretaría de Movilidad report explicitly associates
**087, 088, 090, 091, 105 and 106** with 6F; its 2021 act
`202150041167` approves a joint-operation agreement for SITRANSCO.
The later `202350086596` (Cootransmallat) and
`202350089536` (Cootranspinal) modify/clarify operating conditions.
The reported number `2023350087382` for a 2023 typo correction
has an unusual format and **must be checked against the primary act**.

A 2009 Cootransmallat act `005` is explicitly said to contain
frequencies, but **none of its numerical tables has been obtained**.
Do not sum independently duplicated 6F service if operators run
the same variant together.

### System 6G: Transacoop / Santa Elena

`system_6g_transacoop_source_leads.csv` preserves three different
kinds of evidence: a historical reference to a 1998 authorization;
a **2024 Medellín tourism brochure** reporting buses from Placita de
Flórez **from 06:00 at an advertised 30-minute interval** toward
Santa Elena / Parque Arví; and a 2025 tariff-related legal reference.
The brochure is *not* a technical operational authorization, and
the cited 30 minutes **must not be applied to each of the nine
distinct 98 Directa ArcGIS variants**. Fare acts are not schedules.

### Source retrieval and 2026 monitoring

- `docs/request-medellin-transport-resolutions-es.md`: prepared but
  **unsent** request for the full 2025 Gacetas (5667 and 5671),
  6F operating changes, 6G 098 frequency acts and later amendments,
  including the original annexes in PDF/CSV if available.
- The **official citizen intake channel** is the [PQRSD request form](https://www.medellin.gov.co/es/pqrsd/),
  selecting **Solicitud de copia** or **Solicitud de información**.
  Medellín lists **10 business days** for these requests. The 2025
  citizen-service manual explicitly says `atencion.ciudadana@medellin.gov.co`
  serves *internal* intake, not the official citizen filing channel.
  `publicacion.gacetaoficial@medellin.gov.co` is a municipal **publication
  process** address, not a replacement for PQRSD. The draft was **not sent**.
- `scripts/index_medellin_gaceta_2026_transit_acts.py` and
  `.github/workflows/index-medellin-2026-transit-acts.yml` scan
  the new *official* public archive from **28 August 2026 onward**.
  Only official **act titles** are indexed; no PDF is downloaded or
  retained. This workflow uses a seven-day research artifact.
  A successful [official scan on 17 November 2026](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44090270994)
  reviewed **68 of 68** listed Gaceta detail pages from **28 August to
  12 November 2026** with **zero direct TPC operator/route restructuring
  title matches**. This is title-level negative evidence only:
  `late_2026_public_gaceta_scan.json` preserves the exact scope and
  method. It does **not** establish that there were no relevant
  unpublished, pre-August-2026 or post-November-12 changes, nor verify
  actual headways.

## ArcGIS 2025 ↔ historical 2015 fiche linkage (November 2026)

**Policy:** the 2015 Gacetas are a historical **published** timetable baseline,
not confirmation of currently authorized or actually operated service.
ArcGIS is the source for **present-listed route identities / operators /
itinerary geometry**, but it is not itself a published timetable and does not
prove a route still operates in November 2026.

The `data/medellin/routes.csv` transport-layer snapshot stores the same
`from_date` and `fecha_actualizacion` value on **all 252 unique
`id_ruta` values**: **2025-08-14T14:41:03.247Z** (504 direction rows).
This is consistent with a **bulk import/update timestamp**, not 252
independent last-modified observations, and predates the September 2025
amendments. Do not label this layer "current as of November 2026".

### Candidate registers

- `2015_arcgis_fiche_candidate_links.csv`: one row for each 2015-source
  candidate and one explicitly unmatched row for each current route without
  any candidate. Each linkage records the actual current `id_ruta`,
  `codigo`, current `nombre`, `sistema`, operator, and 2015
  **Gaceta, resolution, PDF page, official route code and printed variant**.
  Contains **267 rows**, including repeated/competing 2015 candidate pages.
  These are research links; no route-specific frequency is enabled.
- `2015_arcgis_route_link_status.csv`: **252 ArcGIS IDs, exactly one
  row each** with the best source-link *research* confidence.
  Count by category: **41 strong historical identity** (same normalized
  code/system and high name agreement without code duplication),
  **32 code/variant-review**, **38 name/family-only provisional
  candidates**, **141 no fiche candidate**; thus **111** current route IDs
  have at least one historical reference, **141** do not.
- `2015_arcgis_manual_candidates.csv`: **44 human-reviewed proposals**
  for 43 ArcGIS IDs whose modern route code differs from a printed
  2015 code, or where a source code is shared by multiple directions/
  variants. Every row includes a reason. The matching is **not**
  established legal supersession, and some proposed links intentionally
  conflict and must remain tentative.

Examples of *candidate* changes: modern `031 P-C` ↔ historical
`6C2 POPULAR-CENTRO`; `51-52 CV-O` ↔ `6C7 CAMPO VALDEZ-ORIENTAL`;
`080 V-M` ↔ historical `080 MANSIÓN`; `252 Kennedy` ↔
`252 AL8 Ferrini-Kennedy`. These support **historical route-family
identification only**; a newer direct, integrated or special-service
variant must NOT inherit the 2015 headway by default.

Counterexamples explicitly held for review:
- `C23i` maps to several **different** ArcGIS village names; the
  Gaceta's generic `C23-i` is not interchangeable with `C23iAV`,
  `C23iPV`, `C23iLPV`, `C23iPAV` or `C23iPALV`.
  **ArcGIS Pedregal Bajo vs printed Pedregal Alto** is a known conflict.
- `097` is two separately named original fiches, while several modern
  `97` records repeat the code. `255A` and `111` have multiple
  newer subvariants with one older base code.
- `041D/041I` are separate modern anillo directions; the historical
  `041A` fiche is merely a possible older family.
- A pilot route, direct route, feeder `AL` or detour may have its own
  timetable. No splitting, summing, averaging or copying of headways
  is performed here.

**No candidate is verified as the currently legal frequency in 2026.**
Every mapping explicitly sets `verified_current_frequency=no` and
`gtfs_import_allowed=no`. No old frequency may enter the GTFS solely
due to a name or code match. Actual effectivity and modifications from
2017–2026 remain separate research in
`current_arcgis_legal_review_queue.csv` and the amendment registers.
Validate the mapping integrity with
`python scripts/validate_2015_arcgis_links.py`.
No PDF is committed or retained through this linkage process.

### Post-2015 legal amendment overlay (separate from the 2015 historical identity)

`arcgis_post_2015_resolution_candidates.csv` now attaches **540
candidate route-to-act references** to **250/252** ArcGIS IDs. The previous
96 without a post-2015 act lead were researched separately; 80 of those
now have at least one *candidate* source, 16 remain unmatched.
The underlying official municipality **report/contents references** are
retained, with act number, issued date, reported effect, route-vs-operator
matching method and explicit `original_act_read=no`,
`revised_frequency_verified=no`, `permit_gtfs_schedule_use=no`.

- **206 existing candidate links** to the report-indexed **2017–2024 acts**.
  The report's route-code lists are **reported or related families**,
  not necessarily verbatim from the original resolution.
- **75 links** to the six distinct **2025 Gaceta act numbers**:
  **three specific route-code matches** (Circular 301 / 313 / 315) and
  **72 operator/system-level candidates** (affected route variants
  not confirmed). The 2025 contents cannot establish altered
  frequency, operating times or actual legal effectivity.
- **75 links** to **post-2015 SITRANSCO / 6F** amendment references.
  The older 2009 and 2015 predecessor decisions remain in
  `system_6f_legal_chain.csv` and are intentionally **not** counted
  as post-2015 modifications.
- **157 newly recovered leads** from 36 report/Gaceta resolution numbers,
  covering 80 of the former 96 unlinked IDs. These are stored in
  `recovered_acts_for_original_96.csv`: official secondary municipal
  resolution references, not individually reviewed legal text. This batch
  explicitly separates restructurings and operational amendments from
  temporary road works, capacity changes, shared-operation agreements
  and appeals. In particular, the 2019 acts for Tax Maya C23 and 195,
  Copatra 093–095 and Transacoop 098 are primarily **temporary geometry**
  and must not be treated as continuing schedule authorization.
- **Three links** for the joint route 229 (2023/2024) are explicitly
  **provisional** for ArcGIS `229i`; the three companies must not
  produce duplicate trips.

`arcgis_historical_and_later_acts_overview.csv` is the **single
252-row research overview** joining the historic fiche status,
Gaceta/page references and the later-act lists. Its review priority
breakdown is **P0=3** exact code matches for 2025 contents,
**P1=94** operator/system-scope candidates, **P2=153** other later
act leads and **P3=2** without later-act candidates. This is **not a classification of actually amended routes**.

`unresolved_16_after_missing96_search.csv` is the earlier **snapshot** of 16:
**14 Palenque Robledal** variants, **Tax Maya 195ii**, and **Flota Nueva
Villa 082 V-LA PILOTO**. In 2019, several 250/253 Palenque routes had
specific temporary road diversions, but those do not prove other 250,
251, 252, 253 or 260 variants had the same act. Similarly the 2019
Tax Maya 195/195i act is **not** evidence for 195ii, and a base 082
act cannot authorize a later pilot without an explicit validity period.

**Do not initiate PQRSD at this stage:** the project owner deferred a
formal records request. Continue checking already-public Gazette act
indexes, official operator references and municipal documents instead.

**No 2017–2025 original timetable table has been visually verified
in this overlay**, and there is no general rule that the latest legal
act changed frequency: some acts relate only to route geometry,
appeals, shared operation or fares. The final legally effective
headway/service span must be resolved **per field and variant**, not
simply by taking the newest act. All integrated rows carry
`verified_latest_effective_frequency=no` and
`2015_to_GTFS_automated_import_allowed=no`.

### Focused follow-up: 14 formerly unlinked Palenque Robledal variants

- `palenque_14_post2015_source_evidence.csv` audits **all 14**
  route IDs in the 2025-08-14 ArcGIS snapshot. The **official 2017
  Medellín transport plan for the papal visit** lists **nine exact
  current codes** (250M, 252, 260CL, 260C, 260BR, 260T, 250AH, 251,
  250AP). It also mentions family codes 250VF and 253IZQ/253DER,
  which do **not** establish the current variants 250VF_C and 253iAR.
  Codes 250AiP, 250Aii and 260i are not explicitly in this 2017
  list. This document is historical proof of *published route
  identification*, **not a route-operating resolution or timetable**.
- The municipal Secretaría de Movilidad's official **2023
  management handover report**, entry 239, explicitly references
  **Resolución 202250015351 (2022-02-24)** as a partial amendment of
  operating conditions concerning both **250AP (ArcGIS 90073) and
  250AiP (ArcGIS 90065)**. The report truncates the 2017
  antecedent's number as `2017500213…`; do not conflate it with
  any other act or guess its missing digits.
  **No original 2022 resolution/annex or current headway has been
  read.** These are two **exact route-level act-reference leads**,
  not two newly verified timetables.
- Historical snapshot prior to finding the full 2025 act: the route
  association register then contained **518** links across **238/252**
  ArcGIS IDs. See the newer 2025 restructuring section for current counts. `arcgis_historical_and_later_acts_overview.csv`
  and `current_arcgis_legal_review_queue.csv` now have P0=3,
  P1=72, P2=163, P3=14.
- `unresolved_14_after_palenque_search.csv` is the **current
  research shortlist**: **12 distinct Palenque Robledal variants**
  plus Tax Maya 195ii and Flota Nueva Villa 082 V-LA PILOTO.
  The old `unresolved_16_after_missing96_search.csv` is retained
  for historical/audit purposes only.

**Remaining Palenque questions:** 250M, 250Aii, 252, 253iAR, 260CL,
260C, 260i, 260BR, 260T, 250AH, 251, and 250VF_C.
Some had exact 2017 public-route-list mentions; **that cannot replace
a route-specific operating act**. A 2019 temporary detour decision
for the 250 family or 253iA is not authority to assign a new timetable
to 250VF_C or 253iAR.

2017 municipal route list:
https://www.medellin.gov.co/irj/go/km/docs/pccdesign/medellin/Temas/ElPapaenMedelln/Publicaciones/Shared%20Content/Publicaciones/2017/Indicaciones%20Movilidad%20por%20visita%20del%20Papa.pdf

Official 2023 handover / 2022 act reference:
https://www.medellin.gov.co/es/wp-content/uploads/2023/08/AIG-Mateo-Gonzalez-Benitez-Sec-Movilidad.pdf

All matching remains *research-only*. Neither a 2017 route notice nor
a 2022 amendment title verifies a 2026 effective frequency, service
window or even actual operation. The GTFS must not import these
historical values. No PDF files are permanently retained; no PQRSD
has been submitted.

## Original ASTREA legal chain — Palenque Robledal 2025 restructuring

**Primary municipal HTML:** [Resolución 202550088689 of 30 October 2025](https://www.medellin.gov.co/normograma/docs/astrea/docs/r_smmed_88689_2025.htm),
published **11 November 2025**, Gaceta **5694**, p. 3 onward.
This **operator-wide** restructuring of system **2A** supersedes earlier
Palenque Robledal operating permissions including the verified **2015
Resolución 1169**, **2017 201750021300**, and **2022 202250015351**.
Article 7 expressly repeals **16 named acts**; those are indexed in
`palenque_2025_expressly_repealed_previous_acts.csv`. Publication
marks its legal start; its status against possible *later* 2026
amendments has not yet been definitively audited.

The original [2022 resolution](https://www.medellin.gov.co/normograma/docs/astrea/docs/R_SMMED_15351_2022.htm)
is in **Gaceta 4933 (25 February 2022), p. 16**.
It only modified **routing geometry** of **250AP and 250AiP** via
Article 1 of **201750021300 (19 December 2017)**, keeping all
other 2017 provisions unchanged. Original 2022 text has a typo
`250IP` in a route header; the actual scope is `250AIP`.
**Neither 2017 nor 2022 is the operative legal timetable after the
2025-wide repeal.**

### Extracted official 2025 timetable tables

`palenque_2025_official_route_service_intervals.csv` contains **20
official legal user codes** from Articles 2, 3 and 4 of the 2025
resolution: **19 ordinary routes plus one conditional `250-5i`**
which replaces `250-3i` **only when Línea J is suspended** for
authorized maintenance/continuity. Never treat both as independent
regular simultaneously active routes.

For **each** route, the source CSV stores six first/last service clock
values (weekday, Saturday, Sunday/holiday), plus **nine maximum dispatch
intervals**: peak, extreme off-peak and midday off-peak for each of the
three day types. These are legally published **maximum** intervals,
not measured current headways or a timetable with an inferred peak
clock period. Article 7 defines **extreme off-peak (PVE) before 04:30
and after 20:30**, but does not fully define every peak clock boundary.
Do not generate 24-hour GTFS frequencies by extrapolating these
intervals without further period definitions and timetable logic.

**Source anomalies preserved:**
- Printed GTPC code **207050** occurs both for normal `253-i`
  Aures Integrada and conditional `250-5i` Aurora integrada
  continuidad; use **GTPC + user route code**, not GTPC alone.
- Sunday/holiday `251` Margaritas ends at **11:50** in the original
  source; recorded verbatim (not silently extended).
- Article 7's final repeals clause is headed **ARTÍCULO SÉPTIMO**
  again after Article 8; the duplication is a source editorial defect,
  not a reason to discount the explicit repeal.

**QA:** the read-only workflow
`.github/workflows/validate-palenque-2025-official-tables.yml`
retrieves the official ASTREA HTML in a GitHub runner, checks the
**20 route-code pairs, every 6 service clock values and all 9 headway
values** against its table text and rejects discrepancies. See
[run 44115217984](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44115217984).
The original HTML is read transiently; no PDF or full document is
committed to Git or long-term artifact storage.

### ArcGIS 2025 vs legally restructured 2A routes

The earlier ArcGIS snapshot (14 August 2025) lists **22 Palenque
Robledal route IDs** using *older* codes. The 2025 law was
published **after** that snapshot and now has **19 regular newly
coded services** (and the one Línea J contingency).
It merges some older services, e.g. `260C + 260T` into
`260-1 Córdoba/Torres` and `260CL + 260BR` into
`260-2 Clínica/Brisas`, and changes user-code nomenclature.

`palenque_2025_old_arcgis_to_new_legal_route_candidates.csv`
preserves the **22 pre-restructure ArcGIS ID/code/name records** with
**conservative possible 2025 legal replacements** and explicit
`automatic_GTFS_import_allowed=no`. Several are one-to-many or
many-to-one, and `253iAR` appears in the municipal rationale as a
proposed removal, not as a separately authorized service in Article 2.
Do not simply delete an ArcGIS ID or map a new legal route to an old
shape before checking the official map annex. Every old ArcGIS ID has
an **operator/scope** link to the official 2025 act
`202550088689` (not a one-to-one legal variant match).

After this original-act recovery, the project has **540** route-to-act
candidate links across **250/252** ArcGIS route IDs.
The **only two ArcGIS IDs without any later-act candidate** are
Tax Maya `195ii` and Flota Nueva Villa `082 V-LA PILOTO`, recorded in
`unresolved_2_after_palenque_2025_astrea.csv`. This is *source
discovery coverage*, not verification that each old route is active in
November 2026. Original 2015 frequencies are kept as historical
research data and are **not** used to override the newer 2025
authorization. PQRSD has not been filed and is not currently planned.

### Focused 2026 ASTREA source-index cross-check

On **17 November 2026**, a bounded GitHub-runner scan of the public
**Secretaría de Movilidad / ASTREA 2026** legal-act index read **25 of
25 available 2026 resolution texts** with no failed fetches. None
mentioned **Conducciones Palenque Robledal** in the returned text.
This is evidence only for the **25 indexed acts**, not an exhaustive
claim about all 2026 legal sources or a judicial determination that
the 2025 timetable is still in force. The reproducible script is
`scripts/scan_astrea_2026_palenque_acts.py`, with concise retained
metadata in `astrea_2026_palenque_latest_act_index_audit.json`.
[2026 index audit workflow](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44117111899).

A separate **2026 official original** was found for the jointly
operated **229i** Barrio Nuevo, in **Resolución 202650039611**
(Gaceta 5830, 14 May 2026, p. 14), which *pre-dates* the public
Gaceta portal period scanned earlier. The original Article 1/2
incorrectly spells `299i` while Article 3 and other references
give `229i`; source figures were preserved in
`route_229i_2026_official_intervals.csv`. Original tables list
two direction codes (899010 / 899020) but numeric clock/interval
cells only appear on the first direction row, likely due merged
cells; **do not double-count** the shared service. This research
finding must be route-reconciled separately before use in GTFS.

## Tax Maya 195ii: historical legal fiche, 2021 official contextual map and newer operator schedule

The official [Gaceta **4911**](https://www.medellin.gov.co/irj/go/km/docs/pccdesign/medellin/Temas/NuestroGobierno/Publicaciones/Shared%20Content/Documentos/2022/4911.pdf), published **30 December 2021**, includes **Resolución 202150181337** dated **6 December 2021** (pp. 32–35). Its **p. 34** map and reasons name route **195ii** alongside 195i, 250iVF, 250iR, 253iAR, 246i and 246ii as *already existing integrated services* sharing corridors with Coonatra 300/301. The operative decision authorizes **Coonatra 300/301** integration and validators, **not Tax Maya 195ii operating permission, headway or hours**. The official PDF text was inspected; web PDF screenshot service timed out, so detailed page-image QA remains pending.

For ArcGIS ID **90290**, actual historical **Gaceta 4325**, **Resolución 1154/2015, PDF page 194**, fiche `195-ii` is already visually verified: **04:30–23:00** general operation; weekday **14 min DÍA / 12 min HMD**; Saturday **14 / 12**; Sunday/holiday **26 / 20**. These are **2015 historical**, not automatically a valid timetable in 2026.

The operator's [public official route page](https://www.taxmaya.com/ruta-c23-san-cristobal-san-javier-centro) continues to identify **195ii** as **Santa Lucía → Floresta → Carrera 80 → Laureles Campestre → San Juan → Santa Lucía**. [Moovit's current published route schedule](https://moovitapp.com/index/es-419/transporte_p%C3%BAblico-time-195ii-Medellin-1642-2304926-47604481-7759294-0) shows **05:15–19:55 daily at 20-minute intervals**, but an older Moovit PDF reports approximately **04:30–22:54**. Keep this discrepancy open. **Moovit is a third-party timetable, not a legal operator authorization**.

All five distinct source classifications are registered in `taxmaya_195ii_2015_2026_source_evidence.csv`. A 2021 municipal management-report act **202150159197** concerns **195i** (single i), not **195ii**; do not merge them.

**Research status:** route identity and public timetable evidence substantially corroborated, **but no independently verified post-2015 route-specific authorization for 195ii has been found**. The route stays in the two-item *legal-decision gap*, alongside Flota Nueva Villa `082 V-LA PILOTO`. No GTFS frequency or production file changes; no PQRSD request.

## Next source batches, ordered by expected yield

- **Gacetas 5667/5671 (September 2025)**: originals for all six prioritized acts are now recovered (five official ASTREA full texts and Gaceta 5667 PDF for Circular 313); continue source period/geometry QA, not original-retrieval work.
- **2017–2024 operating-condition changes**: prioritize the eight
  service-impact leads in `2017_2024_act_chain_index.csv`, plus Cootrabel's
  explicit repeal and joint operation for 229.
- **Historical duplicate QA**: if needed, compare the repeated technical
  fichas in other operator-specific 2015 resolutions for actual textual
  changes; do not blindly duplicate them in the GTFS.
- **2026 follow-up**: search for acts after September 2025 that amend the
  same operators before claiming legal currentness.

For each new resolution, store: unique act reference, publication date, effective date,
source URL, PDF page, system, printed route code, printed operator,
operating day type, service span, all eight DÍA/HMD dispatch intervals
(where present), vehicle and route metadata (optional), supersession links,
transcription QA status, and ArcGIS route-link confidence.

**Policy:** Official numbers may be accepted as the authoritative *published*
frequency and service window once transcription and route identification
are checked. They must not be represented as field-observed real-time
operations or automatically assumed to remain current forever.


## Historical 2017–2024 direct-source audit and Coopetransa 069 (18 November 2026)

A bounded official ASTREA URL-pattern audit checked **38 previously indexed administrative acts**: **2** original full-text candidates were confirmed, **36** not retrieved via tested URLs. The direct source and retrieval outcome are recorded on each row of `2017_2024_act_chain_index.csv`. The two confirmed originals are Coonatra 202150181337/2021 (already reviewed, affects 300/301; not Tax Maya 195ii), and 202450030616/2024 for joint route 229i.

**Important precedence:** 202450030616/2024 is *expressly repealed* by Art. 11 of the recovered 202650039611/2026 act. Its published `FRECUENCIAS DE OPERACIÓN` figures **118/10 weekday/Saturday** and **59/5 Sunday/holiday** are counts of services, not minute intervals. The current 2026 authorized interval source remains in `route_229i_2026_official_intervals.csv`; historical counts are not imported or combined.

A new operator-published primary-source report was visually reviewed: Coopetransa's 2023 management report, printed p23 (PDF p22), reproduces the 2023 official technical fiche for **069 El Jardín** and confirms **069 El Jardín–La Cima** as an alternate ramal. Old ArcGIS IDs **90238** and **90376** respectively. The parent service window is **03:00–23:00**, and the published operations-count table is **228/24 weekday and Saturday, 137/15 Sunday and holiday**; **these are not minutes or a separate ramal timetable**. Three-member `TRESCOOP 6E` convenio is named, but Coopetransa is the operator printed for 069; no triple-agency duplication. Original municipal act **202350107467/2023** is *still missing* despite its fiche being reproduced by the operator.

All details and QA are in [historic_2017_2024_originals_and_coopetransa_069_review.md](historic_2017_2024_originals_and_coopetransa_069_review.md) and [coopetransa_069_2023_operator_report_legal_fiche.csv](coopetransa_069_2023_operator_report_legal_fiche.csv). The remaining original act retrieval work should prioritize actual service-altering decisions, not already verified geometry-only changes. No GTFS generator modifications.


## November 2026 follow-up: Cootrabel, América and 6H

The targeted [Cootrabel / Conducciones América / 6H research note](cootrabel_america_6h_followup_2026-11-18.md) now includes the [28-route legal-chain register](2017_2025_three_operator_chains_route_review.csv) (2 Cootrabel, 16 Conducciones América, 4 Cootransi, 6 Cootransvi). Original legal frequency tables for the priority 2018–2023 acts remain unrecovered; their absence is not a route cancellation or a headway estimate.

**New official 2025 Cootrabel evidence:** Medellín announced route **178 Nuevo Amanecer–Centro** starting **14 November 2025** as a **pilot**, daily **04:20–21:20**, at a stated **20-minute** interval. Moovit stop lists updated in November 2026 still show 178 to Nuevo Amanecer, indicating later operation but **not a formal permanent permit or validated 2026 headway**. The pilot's relationship to old ArcGIS `90374 / 172-178 FUSION` remains unverified. See `cootrabel_178_nuevo_amanecer_2025_pilot_evidence.csv` and [issue #19](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/issues/19). No GTFS changes.


## System 6F: 2026 operator-published hours and destination variants (18 November 2026)

A newly verified [Cootransmallat operator page](https://www.cootransmallat.com/) publishes daily **04:00–23:30** general service windows for route **105 Golondrinas / El Faro** and **106 Tres Esquinas**. It also explicitly says the **Minorista destination is replaced by Bolivia after 18:00** and time-specific paths in its map are **variants, not independent additional routes**. This is operational operator evidence, not a municipal resolution or a minute-frequency table.

The [6F system audit](system_6f_operator_2026_source_audit.md) and [14-ArcGIS-ID ledger](system_6f_2026_operator_arcgis_family_register.csv) cover Cootransmallat 8 shapes, Cootranspinal 3 (087/088; independently confirmed by the municipal depot list), and Copatra 3 (090/091). Old per-variant headways and latest official 2023 original legal texts remain unknown. Do not multiply a common headway by the eight 105/106 ArcGIS shapes or assign the published general window to all special shapes; no generator changes.
