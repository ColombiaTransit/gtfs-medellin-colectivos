# Additional current service windows and frequency evidence — 18 November 2026

## Scope: modern service claims, no new legal requirement

Following the user's decision to allow provisional PP/PVM clock windows, the **separate model generator** [`model_medellin_provisional_peak_windows.py`](../../scripts/model_medellin_provisional_peak_windows.py) was run successfully in [Actions run #44325634014](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44325634014). It writes **1,136 provisional period rows** in [`2025_provisional_pp_pvm_operating_intervals.csv`](2025_provisional_pp_pvm_operating_intervals.csv): peaks 06:00–08:00 / 16:00–20:00, meridian/nonpeak 04:30–06:00 / 08:00–16:00 / 20:00–20:30, and verified PVE before 04:30 / after 20:30. The *times* are a regional-transport proxy; the *minutes* come from each original 2025 route's legal maximum. This is a provisional **scheduled target**, not actual first dispatch offsets or independent present-day observations; the generator is not connected to production GTFS.

## Newly researched current source records

[The 18-row direction/daytype source ledger](2026_moovit_additional_operator_schedules_review.csv) preserves 172, 178, 202, 203, 220 and 090 findings separately from 2025 authorization tables.

| Operator | Public route, direction | Mon–Sat | Sunday | Evidence and mapping |
|---|---|---|---|---|
| **Cootrabel** | **172 Altavista → Centro** | **05:00–20:00, 10 min** | **06:00–19:00, 20 min** | [Moovit direction 0](https://moovitapp.com/index/es-419/transporte_p%C3%BAblico-line-172-Medellin-1642-857167-319916020-0); old 90374 is **172-178 FUSION**, not confirmed identical |
| **Cootrabel** | **172 Centro → Altavista** | **05:45–20:55, 10 min** | **06:45–19:45, 20 min** | [Moovit direction 1](https://moovitapp.com/index/es-419/transporte_p%C3%BAblico-line-172-Medellin-1642-857167-319916020-1); directional start/end difference matters |
| **Conducciones América** | **202 Santa Mónica / El Corazón loop** | **05:00–20:00, 10 min** | **06:00–19:00, 20 min** | [Moovit](https://moovitapp.com/index/es-419/transporte_p%C3%BAblico-line-202-Medellin-1642-857167-749568-0), old GIS 90297 candidate |
| **Conducciones América** | **220 San Javier / 20 de Julio** | **05:00–20:00, 10 min** | **06:00–19:00, 20 min** | [Moovit](https://moovitapp.com/index/es-419/transporte_p%C3%BAblico-line-220-Medellin-1642-857167-319491626-0), old GIS 90301 candidate; route names differ |
| **Conducciones América** | **203 El Corazón / Belencito** | **10 min**; Saturday **05:00–22:00** | **20 min** | [Moovit](https://moovitapp.com/index/es-419/transporte_p%C3%BAblico-line-203-Medellin-1642-857167-319321470-0). Source reports 05:00–04:50 for several days, so **end window REJECTED** as unverified overnight operation; old GIS 90300/90299 ambiguous |
| **Cootrabel** | **178 Nuevo Amanecer** | **20 min** (all seven days) | **20 min** | [Moovit](https://moovitapp.com/index/es-419/transporte_p%C3%BAblico-line-178-Medellin-1642-857167-319916021-0); city's **2025 official launch** already reported **04:20–21:20** and 20 min, but Moovit's purported 05:00–04:40 24h window is **NOT accepted** |
| **Copatra** | **090 El Pinal** | **9 min** reported | **9–15 / 9–20 min**, direction-dependent | [Direction 0](https://moovitapp.com/index/es-419/transporte_p%C3%BAblico-line-090-Medellin-1642-857167-737561-0) and [direction 1](https://moovitapp.com/index/es-419/transporte_p%C3%BAblico-line-090-Medellin-1642-857167-737561-1). Many purported end times around 04:55 after a 05:05 start must NOT become 24-hour GTFS operation. Saturday direction 1 **05:03–21:24** is separately preserved but operator/variant mapping is still uncertain |

### Strongest new find: actual Transacoop 098-7 departures

[Moovit's 098-7 timetable](https://moovitapp.com/index/es-419/transporte_p%C3%BAblico-time-098_7-Medellin-1642-1202368-751797-7759177-0) (source reports update **30 August 2026**) prints **19 exact departures** **every day** from **Santa Elena–Las Brisas–Taberna Santa Elena** toward **Medellín–Santa Elena–Centro Logístico de Transporte**:

**03:30, 04:30, 05:30, 06:30, 07:30, 08:30, 09:30, 10:30, 11:30, 12:30, 13:30, 14:30, 15:30, 16:30, 17:30, 18:30, 19:30, 20:30, 21:30**.

The printed online table lists 03:30 and 04:30 as its final two columns, so the [19-row normalized departure ledger](transacoop_098_7_2026_moovit_explicit_departures.csv) deliberately sorts chronologically. These are **actual advertised departure slots**, a much better temporary route-specific model than the 2024 tourism brochure's 30-minute *corridor* estimate. It is one **098-7 branch and one direction only**; do **NOT** multiply by nine historical Santa Elena GIS variants or adopt the website's generic "24-hour" header as actual service availability.

**Old ArcGIS candidate 90263 / 98 Directa 7** mentions Barro Blanco while the public timetable uses Las Brisas; numbered family alone is not definitive identity. Keep match provisional pending stop/geometry crosswalk.

## Key model safeguards

- Use operator first, direction second, date third; do not overwrite official 2025 maxima blindly with scraped third-party averages.
- Current published third-party data are **provisional observations**, with separate source update dates and source URLs.
- The 172 two directional windows are materially different: do not use one common 05:00 start or a common 20:55 last departure for both.
- **No one-off near-24-hour Moovit end times** are taken as true night service until verified. The same issue affects 090, 178, 203 and some other routes.
- Sunday != Colombian public holidays unless confirmed by source/operator. Published route source data should not automatically create holiday service based on Sunday.
- The 2025 official act and the already collected TRSC exact photo departures remain first-class evidence sources.
- The source register is **research-only**, with `production_auto_import=no`. Routing geometry and later supersession remain independent follow-up work.

## Next focused search

Expand the existing route-level source index to other operators and 2025 route families by retrieving line-specific **first/last span and weekday/Saturday/Sunday headway** from currently published operator schedules. Treat close-of-service-before-start anomalies as invalid spans until independent verification. Use the 19 exact 098-7 departures as a reference template for explicit timetable storage, not as a generic 6G frequency.
