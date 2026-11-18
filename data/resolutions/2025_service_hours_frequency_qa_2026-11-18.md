# Medellín 2025 official headways and service windows — consolidated source QA (18 November 2026)

## Scope and output

This is a **source-level service-window and maximum-dispatch-interval register**, not an executable GTFS schedule. The reproducible workflow [#44322146919](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44322146919) completed successfully after a concurrent-run push collision was resolved by the later workflow. Its output is:

- [`2025_official_service_windows_and_headways_by_day.csv`](2025_official_service_windows_and_headways_by_day.csv): **321 daytype records** for **107 source route/direction entries**: 86 ASTREA/2025 Gaceta 5671 source entries + 20 Palenque Robledal Gaceta 5694 legal codes + 1 joint Circular 313 service from Gaceta 5667.
- [`2025_official_schedule_exceptions.csv`](2025_official_schedule_exceptions.csv): **134 daytype exception records**, potentially with multiple exception tags: **17** zero/non-operating numerical interval-cell cases; **7** explicit no-service days; **68** rows with no independent service span (such as paired Metrosan direction rows or trunk corridors); **21** veredal daily-count days; **19** fixed-departure days; **3** Palenque contingency-service daytypes. These are SOURCE classifications, not independently unresolved 134 routes.
- [`2025_official_extreme_valley_windows_derived.csv`](2025_official_extreme_valley_windows_derived.csv): **163 bounded PVE segments** derived by intersection of the official day-specific service spans with the officially defined extreme-valley periods. The result preserves per-route published maximum PVE minutes and original page provenance; it is **not a GTFS trip or exact departure calendar**.

### Important source-interpretation guardrails

1. Published interval triplets are *maximum dispatch intervals* for `PP` (peak), `PVE` (extreme valley) and `PVM` (midday valley). They are **not** exact observed headways or departures at every stop. Publishing a maximum of 15 minutes does not itself authorize fabricating a fixed 15-minute departure sequence.
2. **NEW original-page verification:** the definition `PVE: Período valle extremo, antes de las 4:30 horas y después de las 20:30 horas` appears in original [Gaceta 5671](https://www.medellin.gov.co/statements/innovaciondigital/gacetas/historico-mercurio/descargar/202000087077) at **PDF pp. 13 (Salud-Hotelera 202550076150), 27 (Castilla/Conaltracoop 202550076162), 40 (Metrosan 202550079848), 57 (Rápido San Cristóbal 202550079865)**. All four were independently located in the original PDF text and page images were rendered for verification. Circular 313 already has the same PVE definition in [Gaceta 5667 p56](https://www.medellin.gov.co/statements/innovaciondigital/gacetas/historico-mercurio/descargar/202000087050). **The 20 Palenque entries are not granted the same period definition by implication**; their specific original-act PVE clock definition still needs separate checking.
3. The **PVE overlap generator** clips early service to before 04:30 and late service after 20:30, on each daytype, only where the original source prints a positive numeric extreme-valley maximum. It does not include a PVE segment when the route starts at 04:45, where the PVE cell is blank/zero, or for source rows with no independent timetable. The 04:30 and 20:30 *instant* inclusion is not specified; the output treats them as segment boundaries only.
4. **PP versus PVM clock boundaries remain unknown** in the inspected source footnotes. Do not assign a peak schedule across an arbitrary portion of the remaining day.
5. Original **0**-minute values are not valid positive headways. For seven Rápido veredal routes, the source instead prints **service counts/day**. **Palmitas 11 corregimental routes** have fixed departure times with days expressed as `Lunes a Viernes`, `Lunes a Domingo` or `Domingo` and must not be expanded into minute-based frequency patterns. **Sunday-only does not automatically mean holidays**; the combined daytype column retains the exact raw service scope text.
6. Metrosan's blank paired direction rows are not independently missing service, nor evidence for two independently calculated frequencies. Joint 313 is recorded **once** even though two GTPC directions and four operators exist.
7. **Palenque 250-5i** is a temporary continuity route **only when SITVA Línea J is suspended**. It is not a normal daily duplicate of its parallel service or of the repeated GTPC **207050** with 253-i.
8. The per-day `published_window_start` / `published_window_end` fields are printed legal operating spans; **not necessarily first/last departure time at every terminus or stop**.
9. No row is marked legally effective through every date in 2026: `current_2026_effectivity_verified=no`. **All `gtfs_generation_approved=no`**. The current 252-route review queue remains at conservative unapproved status until route identity, peak period clocks and relevant later modifications pass QA.

## Further research, in priority order

- First, look for *documented* **PP and PVM clock boundaries**, ideally a direct operating timetable from the operator/municipality. No more inference based on generic Colombian rush-hour assumptions.
- Compare service-window and numeric original-page data beyond the previously spot-checked source cells; the 86 ASTREA source rows were structurally parsed and only selected original table pages reviewed visually.
- Validate 2025 Palenque maximum-period clock definitions if actually printed; never copy Circular 313's boundary footnote to Palenque without verifying its own original.
- Reconcile the existing Rápido San Cristóbal timetable photographs with exact route codes under [issue #18](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/issues/18); avoid duplicative schedule research.
- Keep geometry P0 in [issue #20](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/issues/20), **not blocking separate research-source normalization** but blocking GTFS import.

**No changes to production GTFS generator, shapes, trips, calendars or frequencies were made.**
