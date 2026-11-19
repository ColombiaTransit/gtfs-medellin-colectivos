# Medellín Urbanas — targeted search for newer headways and hours (19 November 2026)

## Scope
Only 13 historic 2015-fiche routes with later operating decisions: 7 Conducciones América and 6 Coonatra. Neither parked 195II nor parked 082 PILOTO is touched. Production GTFS generator and its inputs remain unchanged.

[Machine-readable route decisions](medellin_13_targeted_missing_recent_tables_research_2026-11-19.csv).

## Targeted source checks
1. Reviewed existing `2017_2024_act_chain_index.csv`, `medellin_13_later_decisions_frequency_window_review_2026-11-19.csv`, historical 2015 source registers and published operator schedule sources. Avoided repeating broad historical Gazette/OCR extraction already completed.
2. Performed focused public search for the exact original resolution identifiers `201850015842`, `389/2017`, `201750008728`, and `202150129154`, including official Medellín material and operator publications. **No original full numeric schedule annex for these three key operating decisions was obtained in this pass.** The municipal administrative handover report confirms decision identities and scopes, but does not print their frequency/working-window tables: <https://www.medellin.gov.co/es/wp-content/uploads/2023/08/AIG-Mateo-Gonzalez-Benitez-Sec-Movilidad.pdf>.
3. Confirmed the 2021 Conducciones América `202150006316` concerns **directional route path** of 223/201i/221i, whereas 2018 `201850015842` changes **operating conditions** for the listed 15 route families. Do not confuse geometry-only act titles with changed dispatch times.
4. Coonatra `202150129154` amends 311i/311ii and the 2017 appeal decision; precise numerical impacts remain unknown. Coonatra 2019 242 decision concerns route paths. No numeric service values may be inferred from the administrative title.
5. Existing **direct operator** first/last departure evidence can be reused now for **four of the 13**: 242 Divisa 03:45–21:30; 242 Quiebra 05:08–18:12; 311i Metro 04:35–21:45; 311ii Metro Directo 04:30–22:30. Day-type scope is unspecified, so these are operational window candidates, not per-day legal windows. Source: <https://coonatra.com/floresta-san-juan/> and <https://coonatra.com/calasanz-boston/>.
6. The already captured Coonatra *operator-family* average intervals (**6 min Floresta–San Juan; 8 min Floresta Integrada; 7 min Calasanz Integrada**) are **not route-specific**. They cannot replace 242, 243i, 311i or 311ii branch frequency tables. <https://coonatra.com/wp-content/uploads/2023/09/POLITICA-PUBLICA-COONATRA.pdf>.
7. An operator-specific modern numeric timetable for the 7 Conducciones América **historic routes 201/201i/202i/221A/221i/222** was not verified. Current third-party results for other families (202, 203, 220) already exist in `2026_moovit_additional_operator_schedules_review.csv` but are not a reason to copy those figures to these 7 old variants.
8. Official Metro integrated-route listings confirm ongoing route-family naming for Conducciones América 202i / 221i but list **Metro station operating hours**, not these bus routes' first/last departure or headways: <https://www.metrodemedellin.gov.co/usuarios/sistema-integrado/linea-b>. This source does not close a timetable gap.

## Outcome
- **13/13** route identities and their target later operating-decision chain documented.
- **4/13** have route-specific *direct operator first/last departure candidate windows*, without confirmed daytype.
- **0/13** have newly recovered route-specific numeric frequency tables from the later original legal acts. The missing table retrieval remains open; prior 2015 frequencies remain historical only.
- For 243i/243iD, no published source-specific terminal window has been independently confirmed.
- Next original acquisition should be a *single bounded request* for the three original decisions and all annexes/technical fiches, rather than rescraping 2015 Gacetas: `201850015842/2018` (Conducciones América), `389/2017` and `202150129154/2021` (Coonatra); optionally `201750008728/2017` to resolve amendment chain. The already drafted Spanish municipal request in `docs/request-medellin-transport-resolutions-es.md` may be adapted; it has **not been submitted**.
- All routes remain `gtfs_import=no`; no assumption that an unlocated PDF proves unchanged 2015 service.
