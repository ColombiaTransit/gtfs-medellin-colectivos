# Medellín Urbanas — research progress and next-action register (18 November 2026)

## Measured scope (current GitHub files, not estimates)

| Metric | Verified count / state | Evidence |
|---|---:|---|
| Operator names represented | **32 / 32** | `data/resolutions/operator_coverage.csv` |
| Unique ArcGIS `id_ruta` identities | **252** | `data/medellin/routes.csv` |
| Direction-specific ArcGIS records | **504** | `data/medellin/routes.csv` |
| Historic 2015 unique source fiche positions visually checked | **114** | 2015 visual audit registers as summarized in [issue #12](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/issues/12) |
| Original 2025 source/directional records | **88** (not 88 services) | `2025_legal_to_arcgis_consolidated_register.csv` |
| 2025 ASTREA direction/source classifications | **50** numerical max-headway rows; **11** fixed rural departures; **7** rural daily-service counts; **8** Metrosan paired direction rows; **10** trunk/corridor identity-only rows | `data/resolutions/README.md` |
| Additional jointly operated Circular 313 directional rows | **2** / **1** service | Original Gaceta 5667 audit, included in the above 88 total |
| Already indexed 2017–2024 priority acts tested for direct ASTREA originals | **38**; **2** direct original texts recovered through URL-pattern check | `2017_2024_act_chain_index.csv`; source availability is not proof of absence |
| Queue entries marked current headway legally verified | **0** | `current_arcgis_legal_review_queue.csv` field `frequency_currently_legally_verified` — this is a conservative approval flag, not a claim that all 252 routes lack published information |

### Research queue priority allocation

| Current queue priority | ArcGIS identities | Intended next action |
|---|---:|---|
| P0 | **3** | Circular 313 source now recovered; validate ArcGIS shape, current legal effectivity and period boundaries; 301/315 geometry-only confirmed |
| P1 | **94** | Complete 2025 candidate-to-ArcGIS shape and stop checks, interval-period interpretation, and latest-act applicability |
| P2 | **153** | Focus on newer operating-condition originals and operator-verified departures for 6F/6G/6H, Conducciones América, Cootrabel, other operators |
| P3 | **2** | Defer low-priority/parked data and source-specific questions until higher priorities close |
| **Total** | **252** | A priority class is *not* a completion state |

**Important:** 32/32 operator names **inventoried** is not 32/32 operator timetables verified. The historical source QA and 2025 source extraction are substantially advanced, but **the legal approval flag is still zero across the current 252-ID review queue** because modern periods, route geometry and modifications require sign-off.

## Newly advanced in this pass

1. **Transacoop 6G:** [nine route branch ledger](system_6g_transacoop_098_nine_variants_evidence.csv) covers all ArcGIS 90257–90265 without multiplying the shared 098 corridor's approximate tourist frequency by nine.
2. **Important historic-source correction:** 25 min weekday / 20 min weekend, 05:20–20:00 in the old Santa Elena transport study describes **Coopetransgur (Guarne)**, *not* Transacoop. Transacoop's historical 2008-area observations refer to 15-minute morning / 10-minute after-13:00 dispatches; its 2011 study proposed 11 peak departures/hour, and the 2024 tourism brochure says approximately 30 minutes from 06:00 for a shared Santa Elena/Arví connection. Different dates, corridor versus route distinctions, and nonlegal source types make **all those values unsuitable as per-variant 2026 headways**. See [6G source audit](system_6g_transacoop_098_source_audit.md).
3. **6F prior work preserved:** the 14 ArcGIS families/variants are reconciled, with Cootransmallat direct operator daily origin-family 04:00–23:30 and Minorista→Bolivia after 18:00. No unverified per-shape headway was fabricated.
4. Backlog [issue #12](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/issues/12) renamed to reflect **remaining historic legal and GTFS acceptance**, rather than a falsely outstanding search for 2025 Gacetas already recovered. [issue #18](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/issues/18) preserves TRSC existing schedule-photo crosswalk; [issue #19](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/issues/19) covers the Cootrabel 178 pilot/permanence question.

## What work is still worth doing, in order

- **P0/P1:** compare current original 2025 route-family codes against government ArcGIS direction-specific geometries and stops, especially Castilla conflicting 289, Metrosan Colinas/Socorro, Circular 313 and shared 229i; avoid duplicated joint services.
- **P1:** determine legally documented clock period boundaries for already published max headways and day-type calendars. Source-specific intervals must not become blanket full-day frequencies.
- **P2:** obtain the **remaining original** 2017–2024 operating-condition acts from genuinely new municipal archives/official correspondence; do *not* rerun the same 38 predictable ASTREA URLs that yielded two originals.
- **P2:** compare **existing** operator website departures for TRSC against 2025 codes (issue #18), and review service-window/variant issues for 6F and 6G.
- **Parked:** Flota Nueva Villa 082 V-LA PILOTO (user directive).
- **Production gate:** until current legal and spatial QA are complete, keep `automatic_gtfs_import=no` and do not change GTFS generation.

This file is a snapshot of current research coverage and queue priorities. It is **not a statement that a particular bus route is currently authorized or active**.
