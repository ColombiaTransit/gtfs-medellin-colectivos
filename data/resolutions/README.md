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
- `gaceta_4325_visual_verified.csv`: 47 fichas whose eight
  `INTERVALO DE DESPACHO` values and printed `HORARIO DE SERVICIO`
  have been read directly from the page images (10 in the first research pass; 37 in the second). Each record contains its PDF page
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

## Source inventory for 2015/2025 amendments

See `priority_source_documents.csv`. Official individual PDFs have been located for 2015 resolutions 1047 (Flota La V, 34 pages), 1166 (Medellín Castilla, 89 pages), and 1169 (Palenque Robledal, 89 pages); their timetables remain **unextracted**. The contents of Gacetas 5667 and 5671 locate six 2025 route-restructuring/modification acts (the official full PDF and their route-level timing tables are not yet recovered). These later acts must be reviewed before interpreting 2015 values as current.

**OCR QA example:** the first raw OCR pass read the weekday DÍA interval for Gaceta 4325 p. 172, route 191, as 5 minutes; the printed dispatch table shows **6 minutes**. The visually verified record uses 6. OCR candidates are never approved merely because their eight numeric fields appear complete.

**Interpretation for the 2015 system 6B:** some route fichas explicitly have different published service windows for weekday, Saturday and Sunday/holidays, all recorded in their respective columns, whereas most 6C and 8A fichas state only a general window. Do not infer a day-specific first/last departure when the source does not specify it.

## Next source batches, ordered by expected yield

- **Gaceta 4327 (2015)**: multiple 6A/6D and 2A operator-specific
  restructuring acts, including Flota La V, Flota La Milagrosa, Copatra,
  Coopcerquin, Cootranscataluña, Cootracovi, Flota Nueva Villa, Palenque Robledal,
  Cootransblan, and Rápido San Cristóbal.
- **Gaceta 4326 (2015)**: Transporte Medellín Castilla (1166/2015).
- **Gacetas 5667/5671 (September 2025)**: Circular 301/313/315 and
  more recent routes for Coinvetrans/Invetrans, Transporte Medellín Castilla,
  Metrosan and Rápido San Cristóbal.
- **2017–2026 later individual acts**: search using the exact resolution
  numbers already indexed in `operator_coverage.csv`, then capture
  changes relative to the 2015 base and verify current applicability.

For each new resolution, store: unique act reference, publication date, effective date,
source URL, PDF page, system, printed route code, printed operator,
operating day type, service span, all eight DÍA/HMD dispatch intervals
(where present), vehicle and route metadata (optional), supersession links,
transcription QA status, and ArcGIS route-link confidence.

**Policy:** Official numbers may be accepted as the authoritative *published*
frequency and service window once transcription and route identification
are checked. They must not be represented as field-observed real-time
operations or automatically assumed to remain current forever.
