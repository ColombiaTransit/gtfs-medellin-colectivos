# Medellín urban bus resolutions: source-first evidence register

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

See `priority_source_documents.csv`. Official individual PDFs have been located for 2015 resolutions 1047 (Flota La V, 34 pages), 1166 (Medellín Castilla, 89 pages), and 1169 (Palenque Robledal, 89 pages); their timetables remain **unextracted**. The contents of Gacetas 5667 and 5671 locate six 2025 route-restructuring/modification acts (the official full PDF and their route-level timing tables are not yet recovered). These later acts must be reviewed before interpreting 2015 values as current.

**OCR QA example:** the first raw OCR pass read the weekday DÍA interval for Gaceta 4325 p. 172, route 191, as 5 minutes; the printed dispatch table shows **6 minutes**. The visually verified record uses 6. OCR candidates are never approved merely because their eight numeric fields appear complete.

**Interpretation for the 2015 system 6B:** some route fichas explicitly have different published service windows for weekday, Saturday and Sunday/holidays, all recorded in their respective columns, whereas most 6C and 8A fichas state only a general window. Do not infer a day-specific first/last departure when the source does not specify it.

## Gaceta 4327 recovery and 6A OCR-text candidate register (2026-11-17)

- \`gaceta_4327_res_1047_text_candidates.csv\`: **11 indexed fiche occurrences**
  from Resolución **1047/2015** (Sistema 6A, SICO UT; municipal PDF),
  including separate printed 097 variants. Text index supplies possible
  service windows and, for some fichas, eight DÍA/HMD dispatch intervals.
  **Every row is \`indexed_pdf_text_unverified\`** until the original
  PDF page image is checked. Blank interval cells for routes 110/111
  reflect demonstrably corrupted extracted text, *not zero service*.
- Suspicious printed/indexed values are explicitly flagged: route 097
  weekday end 10:30, route 113M weekday HMD interval 2 minutes, and
  confusing 113B/113M OCR route labels. There is no automatic repair.
- \`official_pdf_sources.json\`: four exact **official** PDF URLs for
  complete Gaceta 4327 plus Resoluciones 1047, 1169 and 1166.
- \`scripts/recover_medellin_pdfs.py\` with workflow
  \`.github/workflows/recover-medellin-resolution-pdfs.yml\`: attempts
  bounded parallel retrieval on GitHub runners, rejects HTML error pages,
  stores successful PDF bytes with SHA-256 and optional \`pdftotext\` output.
  The first successful run produced an **original 30-day Actions artifact**;
  later runs use **7-day artifact retention**. PDFs are never committed to Git. Run manually with **Actions → Recover Medellín
  official resolution PDFs → Run workflow** if the first attempt fails.

**Recovery run succeeded:** [GitHub Actions #44077028708](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44077028708) downloaded **4 of 4 official PDFs** (full Gaceta 4327, resolutions 1047 and 1169 in 4327, and resolution 1166 in 4326). Source archive bytes and SHA-256 checksums are recorded in \`pdf_recovery_provenance_2026-11-17.json\`. The ZIP artifact expires after 30 days; do not treat the artifact as a permanent substitute for the official PDF links.

- \`gaceta_4327_res_1047_visual_verified.csv\`: **all 11 distinct printed technical-fiche occurrences** (ten route codes; 097 has two variants) checked **directly from the recovered original scanned PDF**. The source prints 2015 service windows for weekdays, Saturdays and Sundays/holidays and eight intervals per fiche. This register supersedes the provisional OCR candidate file for the same page.
- The indexed text **misread** the Sunday start for route 097 El Vergel (source prints **05:00**) and the weekday HMD for route 112 (source prints **6 min**, not 5).
- **Genuine printed anomalies, not OCR errors**: the first route 097 fiche prints weekday/saturday end **10:30** and weekday DÍA **48 min** while HMD is **4 min**; route 110 actually prints interval values **32,0,42,0,49,1,49,1**, including zero-minute HMD values. These must not be accepted as literal valid GTFS headways just because they are printed. Route 113M prints weekday HMD **2 min**. Route 113's header has **113M** while its technical \`CÓDIGO\` is **113**; retain the source conflict.
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

`arcgis_post_2015_resolution_candidates.csv` now attaches **516
candidate route-to-act references** to **236/252** ArcGIS IDs. The previous
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
breakdown is P0=3 explicit 2025 title/code links; P1=72 operator-only
2025 scope; P2=161 other later-act candidates; P3=16 without a found
post-2015 act candidate in the sources checked. This is **not a classification of actually amended routes**.

`unresolved_16_after_missing96_search.csv` lists the residual 16:
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

## Next source batches, ordered by expected yield

- **Gacetas 5667/5671 (September 2025)**: retrieve the official full
  documents through publicly accessible municipal sources,
  extract any revised schedules, confirm affected variants and field-level
  precedence over the historical 2015 baseline.
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
