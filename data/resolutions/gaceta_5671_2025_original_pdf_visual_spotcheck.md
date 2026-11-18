# Official Gaceta 5671 PDF source audit — 18 November 2026

- Publication date: **30 September 2025**; Gaceta **5671**, **62 PDF pages**.
- Primary original: [Medellín's historical Gazette PDF](https://www.medellin.gov.co/statements/innovaciondigital/gacetas/historico-mercurio/descargar/202000087077), document ID `202000087077` retrieved from public `numero_acto=202550079865` search, **not guessed**.
- SHA-256: `97558ef103d1f71fc03f641dacfb618c4d223342105426cb50901bc8af8f9607`; verified as original PDF, `pdftotext` confirmed all four legal acts.
- Source recovery successful: [GitHub Action #44288771768](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44288771768); original PDF is transient workflow artifact, never committed.

## Source acts included (municipal original)
- `202550076150` Salud-Hotelera, original Gaceta p3 onward; checked original day-type rows including Sunday table p12.
- `202550076162` Castilla/Conaltracoop, original Gaceta p14 onward; **visually reviewed weekday/saturday/sunday headway tables pp25–26**, uncovering previously omitted `TRONCAL 65` and `TRONCAL 73` maximum legal intervals.
- `202550079848` Metrosan, original Gaceta p29 onward; checked table p38 for paired GTPC direction entries with **merged values not repeated**.
- `202550079865` Rápido San Cristóbal, original Gaceta p42 onward; checked p54 for **daily counts of services** on seven veredal variants, not positive-minute headways.

## Critical original-source repair: Castilla trunk lines

| Legal code | GTPC | Mon–Fri peak/PVE/PVM (min) | Saturday (min) | Sun/holiday (min) | Legal window Mon–Fri and Sat | Sunday window |
|---|---|---|---|---|---|---|
| TRONCAL 65 | 23607 | 8/15/10 | 10/18/12 | 13/16/20 | 04:40–20:00 | 05:00–19:00 |
| TRONCAL 73 | 23609 | 4/8/6 | 5/10/8 | 6/10/13 | 03:25–21:30 | 04:00–20:00 |

The raw HTML source tables DID already contain these values: prior normalization was too restrictive. `scripts/normalize_medellin_2025_astrea_tables.py` now asserts the expected source rows against each numeric day-type table and writes them into the 2025 interval register. [GitHub Action #44289880493](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44289880493) passed with those values intact.

**Do not confuse** legal `TRONCAL 65` and `TRONCAL 73` with the ten separately numbered `TRONCAL-4` through `TRONCAL-13` *corridor rows* (which have no separate normal headway table). Original p26 notes these corridor intervals will be determined based on operational needs upon commencement.

## What is and is not verified
- The recovery validates the **original publication**, all four act numbers and the **specific visually inspected source-page tables** only; it does **not** certify manual transcription of every cell of the 86 ASTREA rows.
- Following the focused correction: **50** ASTREA direction/source records have printed triplet maximum intervals by three day types; **8** Metrosan return GTPC records have paired blank cells; **11** Rápido corregimental services print fixed departures; **7** Rápido veredal services have daily service-count figures; **10** Castilla corridor entries have no separate numeric interval table. That sums to **86 source records**. The additional Circular 313 two direction rows in Gaceta 5667 make **88** rows in the broader 2025 source-to-ArcGIS register.
- Precise clock boundaries for peak/midday periods, 2026 modifications outside the bounded indexed scans, and route-direction geometry applicability remain open. **No GTFS changes.**
