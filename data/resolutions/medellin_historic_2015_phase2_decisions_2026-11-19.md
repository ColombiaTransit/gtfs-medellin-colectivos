# Medellín Urbanas — 2015 fallback phase 2: later acts, variants, anomalous fiches
Date: 2026-11-19

## Scope, order and resulting datasets
Reconciliation was performed in the user-requested order against existing source files only (do not reacquire already checked 2015 Gacetas):
1. [13 routes affected by later operating acts](medellin_13_later_decisions_frequency_window_review_2026-11-19.csv)
2. [10 historic ambiguous route variants](medellin_10_historic_variant_disambiguation_2026-11-19.csv)
3. [11 historical apparent anomaly records](medellin_11_historic_anomaly_resolution_2026-11-19.csv)

The starting 70-route audit remains [here](medellin_70_historic_2015_later_amendments_audit_2026-11-19.csv). Neither 195ii (90290) nor 082 PILOTO (90370) has been reopened. No production GTFS or frequency generator modifications were made.

## 13 later-decision routes — findings
- **Seven Conducciones América archived IDs** (201, 201i, 202i, 221A, 221i, 222, including two 201 ArcGIS records): `201850015842` (2018) is indexed as an operating-conditions act. Later route-specific `202150006316` (201i/221i) is a geometry change; `202350001335` (202i) concerns a stop, not verified frequency replacement. The original 2018 numerical tables are **not recovered**. The 2015 day/HMD maxima and windows remain **historical only**.
- **Six Coonatra IDs** (242 La Divisa/La Quiebra, 243i/243iD, 311i/311ii): 389/2017 expressly modifies operation; 201750008728 concerns appeal; 201950089585 modifies 242 geometry; 202150129154 is an indexed 311i/311ii amendment whose changed numerical fields cannot be assumed from the title. The original 2017/2021 tables are still **unrecovered**.
- **Newer direct operator windows** already retained in `coonatra_current_website_12_variant_departure_windows.csv`, now linked to the four relevant blocked historical IDs:
  - 90318 / 242 Divisa: 03:45–21:30
  - 90319 / 242 Quiebra: 05:08–18:12
  - 90324 / 311i Metro: 04:35–21:45
  - 90325 / 311ii Metro Directo: 04:30–22:30
  These are first/last *operator-published terminal departures* with daytype unspecified, **not** new official statutory maximum period headways and **not** automatically applicable every weekday/Saturday/Sunday. Other 243i/243iD operating-window needs remain. See <https://coonatra.com/floresta-san-juan/> and <https://coonatra.com/calasanz-boston/>.
- Company-wide **Floresta–San Juan 6 min** and **Floresta Integrada 8 min** are **family-level averages**, *not* per-branch timetables (see existing 2024–2027 Coonatra operator policy report). Do not copy them across all six routes or duplicate service.

**Decision:** All 13 route identities remain review-flagged for current legal frequency, although 4 have useful newer operator window evidence. The missing original tables are a real source limitation, not a reason to make up replacement headways.

## 10 historical variants — targeted disambiguation
- **097 / Flota la V**: page 396 is **Quinta Linda–El Vergel** (legacy 90179, name-based); page 398 **Cauces–Quinta Linda** (90175 and 90176 both candidate historic shape identities). This improves source selection without proving direction-specific operation. Page 396 unusually reports 48/4 weekday normal/HMD and an 03:50–10:30 working window; retain as printed but do not promote as current.
- **024 / Transporte Aranjuez Santa Cruz**: IDs 90206 and 90207 both map to the *same* historic p132 fiche. They may differ in route shape or direction; one source frequency must not become two identical full services.
- **C23i / Tax Maya**: IDs 90329–90333 now preferentially map their specific branch fiche by printed code (AV p228, PV p230, PALV p236, LPV p232, PAV p234). Generic p224/p320 citations remain historical family context only. Original unusual printed HMD values are preserved; a branch source does not confirm the service in 2026.

Nine of these ten historic identities now have a **specific fiche page or name-based candidate** (including shared historic tables) but none is automatically cleared for 2026 production imports. One route identity still has no unique one-to-one timetable mapping because its historical source is shared.

## 11 historical anomalies — classification corrected
The prior `HISTORICAL_PRINT_ANOMALY_REVIEW` group was too broad. The original printing is retained; **we do not invent corrected numeric values**:
- **1 genuine source value blocking direct GTFS conversion**: Flota la Milagrosa **110**, 2015 weekday and Saturday HMD `0` minutes. A zero-minute headway is invalid. Retain in provenance, never convert to a GTFS frequency.
- **5 time-format cases**, not source errors: Expreso Campo Valdés **6C** routes show `03:00–02:00` crossing midnight, which corresponds to a next-day **26:00** endpoint for GTFS **if** later validated for production. This is not a 1-hour working day or a source print error.
- **3 repeated shared-fiche variants**, not source errors: Flota Nueva Villa historic **080** fiche is reused by V-33/V-M/V-O old ArcGIS variants. The single printed family interval does not prove three additive services.
- **2 shared direction cases**, not source errors: Tax Maya **C23-i** left/right historic variants 90328/90355 share one fiche. Do not double headways.

Thus **10 of the 11** are not individual numerical-print errors; they have a structural or time-encoding explanation. The remaining **1** still needs later operational evidence before it can be converted. These findings do not establish legal current effectivity.

## Remaining targeted work
1. Obtain the original **201850015842** table(s) for Conducciones América and **389/2017 + 202150129154/2021** for Coonatra; first check existing indexed administrative act sources and already collected operator evidence, without re-OCR'ing 2015 pages. Preserve scope-specific legal changes.
2. For 243i/243iD, obtain direct variant-specific operator windows or verified legal hours; no family-level service multiplication.
3. For 097 p396 abnormal service end and 110 zero HMD, retain as printed and require new reliable evidence before converting.
4. Verify directional/variant mapping for 024 and C23i before generating GTFS.

The 34 other 2015 candidate routes remain historical provisional candidates from the prior audit; not certified as legally current in 2026.
