# Research round: PP / PVM clock boundary definitions, Medellín TPC (18 November 2026)

## Result

**No sufficiently authoritative 2025/2026 operating clock intervals for PP (Período Pico) or PVM (Período Valle Meridiano) were recovered** in this targeted research round. The legal originals inspected state the categories and maximum minute intervals for each day type, but **do not say, for example, that PP is 06:00–08:00 and 17:00–19:00 for these authorized bus services**. A different system's study schedule must not be used as a proxy.

**NEW positive official-source result:** all **six** relevant original 2025 decisions define **PVE (Período Valle Extremo) as before 04:30 and after 20:30**:

| Original municipal act | Operator/route scope | Original source | Where verified |
|---|---|---|---|
| 202550076150 | Salud–Hotelera | Gaceta 5671 | Original PDF p13 |
| 202550076162 | Castilla / Conaltracoop | Gaceta 5671 | Original PDF p27 |
| 202550079848 | Metrosan | Gaceta 5671 | Original PDF p40 |
| 202550079865 | Rápido San Cristóbal | Gaceta 5671 | Original PDF p57 |
| 202550076168 | Joint Circular 313 | Gaceta 5667 | Original PDF p56 |
| **202550088689** | **Palenque Robledal** | **Gaceta 5694/official ASTREA** | **Official original, Art. 7, verified in [Actions run #44324071663](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44324071663)** |

The official Palenque original is [Resolución 202550088689/2025](https://www.medellin.gov.co/normograma/docs/astrea/docs/r_smmed_88689_2025.htm), and the original text explicitly prints **PVE: Período valle extremo, antes de las 4:30 horas y después de las 20:30 horas** followed by **PP: Período pico** and **PVM: Período valle meridiano**. The original contains **no PP/PVM clock boundaries in those definitions**. This resolves the former "Palenque PVE definition unverified" source-review item.

## Concrete bounded checks

1. Re-checked original Gaceta 5671 definitions (four resolutions) and prior Gaceta 5667 audit (Circular 313).
2. Ran a [targeted ASTREA Palenque original-text check](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44324071663), searching for `Período pico`, `Período valle meridiano`, `PVE`, `PP`, `PVM`, `franja horaria` and literal clock phrases. The official text's matching definitions specify PVE only.
3. Searched public Medellín / AMVA municipal material and operator schedule contexts for **actual clock intervals** for `PP` and `PVM`, rather than generic "hora pico". No independently applicable 2025 route-operating legal times were found in that search.
4. A [2011 metropolitan origin–destination study](https://studylib.es/doc/8295941/informe__eod_hogares..) used **06:00–08:00 and 17:00–19:00** as peak periods *for its traffic/model validation*, with intervening valley subdivision. **Those are historical analysis time slices, not 2025 Secretaría de Movilidad TPC operating definitions**. They are stored in [`medellin_2025_pp_pvm_clock_boundary_source_audit.csv`](medellin_2025_pp_pvm_clock_boundary_source_audit.csv) solely as REJECTED candidate evidence; never auto-import them.

## Actual register advance

The repeatable daytype source normalizer now allows 202550088689 in the **PVE legally verified scope** and clips its already published service spans against the official bounds. [Run #44324318293](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44324318293) completed successfully.

- [`2025_official_extreme_valley_windows_derived.csv`](2025_official_extreme_valley_windows_derived.csv) has **245** source-derived PVE segments (previously 163), **82** of the new segments contributed by Palenque; other act records unchanged.
- [`medellin_2025_pp_pvm_clock_boundary_source_audit.csv`](medellin_2025_pp_pvm_clock_boundary_source_audit.csv) explicitly distinguishes verified PVE clocks, PP/PVM *terminology without times*, and unrelated model assumptions.
- PP and PVM remain **unknown for all applicable official 2025 acts**, unless a source-specific PSO/operator timetable or a legally incorporated clock schedule is recovered.

**Do not infer full daily headway from any max interval triple.** `PVM` literally refers to *valle meridiano*; it is not necessarily every minute between AM and PM peaks. The exact 04:30 and 20:30 boundary instants are not defined for individual departures. The derived PVE segments are **not current 2026 GTFS trips** and do not settle later amendments, joint operation, shape mapping or headway compliance.

## Next targeted missing source

Look for the **Programa de Servicio Operativo (PSO)** or `Sistema de Ayuda a la Explotación (SAE)` programmed-departure tables of the authorized routes. The original resolutions themselves refer to `Despachos programados PSO referencia (AMVA)` and `Despachos real SAE` in their operational indicators. Those **route-specific operational schedules** are the most promising way to distinguish exact PP/PVM boundaries and/or exact departures without choosing arbitrary rush-hour clocks.

Only obtain and map those actual official/operator scheduling files if available. No generator or GTFS changes in this research round.
