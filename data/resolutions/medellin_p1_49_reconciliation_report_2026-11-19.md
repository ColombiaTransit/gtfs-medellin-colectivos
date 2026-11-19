# P1 49 routes — official frequencies and operating windows, first reconciliation (19 November 2026)

The 49 P1 historic ArcGIS IDs from [the 146-route queue](medellin_146_remaining_routes_action_register_2026-11-19.csv) were cross-checked against the **already recovered** original 2025 official legal tables for Coinvetrans, Castilla, Rápido San Cristóbal, Palenque and Metrosan, with a distinct entry for each weekday/Saturday/Sunday-holiday source state.

Outputs:
- [49 route-to-legal-code identity decisions](medellin_p1_49_route_legal_crosswalk_2026-11-19.csv)
- [147 route×daytype legal source decisions](medellin_p1_49_legal_daytypes_2026-11-19.csv)
- [Updated 252-route 2026 working model](medellin_252_schedule_2026_working_assumption_p1_updated.csv)

## New working-model acceptances

| Old ArcGIS route | Official 2025 code and act | Result |
|---|---|---|
| 90084 / 255i Aurora–Cárcel | 255-1i, 202550079865 | 3 daytypes with official operating spans and max headways; accepted as a strong route candidate |
| 90125 / 306A left/anticlockwise | 306-2i, 202550076162 | 3 daytypes operating windows/headways; directional equivalence assumed for 2026 |
| 90126 / 306B right/clockwise | 306-1i, 202550076162 | 3 daytypes operating windows/headways; directional equivalence assumed for 2026 |

**2026 working-model routes with three active-day-type frequency+window candidates now increase from 106 to 109.** This is a *route-level planning assumption*, not production GTFS or proof of independent present-day legal effectivity.

Also resolved calendar/service rules:
- 90012 / **308D → 308-2**, 90014 / **309D → 309-2**: **16:00–19:00 weekdays, max peak interval 15 min**; the 2025 original explicitly says **no Saturday and no Sunday/holiday service**. These **two routes are schedule-rule complete** (including explicit non-operating days), but are not counted in 109 as having active window+frequency on all three daytypes.
- 90083 / **255 → 255-1** San Cristóbal/Doña María: weekday 08:00–19:40, Saturday 08:00–19:40; Sunday row is marked `published_no_service` **yet retains numerical interval cells**, so the no-service vs Sunday interval inconsistency requires row-level source check before being called complete. Do not infer Sunday departures.

## P1 matched source findings

The 49-route ledger distinguishes:
- 4 direct route-code or strong-name matches (308D,309D,255,255i)
- 2 Castilla 306 directions matched based on left=antihorario and right=horario (planning confidence: candidate)
- 3 rural 255V identity-name candidates whose official source lists *daily service counts*, not minute headways (El Llano, Yolombó, La Cuchilla)
- 2 old Boquerón direction IDs sharing **one** source 255-7v daily-service count. The same legal source is attached to both, with one `shared_service_key`; **never double count** the legal 15/13/2 daily services.
- 4 Palenque broad family source matches, 2 Castilla 263-1i shared candidates, and 1 conflict (old 289 Pilarica Calle 96 vs legal 289 Picacho); **no automatic branch frequency assignment** until variant or source identity resolved.
- 10 Castilla TRONCAL-4 through TRONCAL-13 entries where a legal description references a historic street corridor **without a route-specific published frequency/window**. A trunk 65 or 73 headway must not be copied to every ring segment.
- 2 Metrosan old IDs **90308 Colinas / 90314 Socorro** which are not in the eight 2025 numerical legal service tables. Do not pretend the other Metrosan family headways apply.
- 19 old IDs with no defensible single new official service-code match; retained in the P1 unresolved queue.

The recovered 2025 route-family source numbers are accepted as the 2026 working baseline where an identity is defensible. Current working policy is to **stop rechecking generic legal validity** and focus only on identity conflicts and actual missing numbers. This change **does not modify the GTFS generator**.

## Next focus

Resolve the 19 unmatched P1 routes by comparing 2025 legal names, directional shape identity and the existing operator timetable/photo crosswalk. For rural service-count sources, use count-based service modelling rather than inventing minute headways. Resolve special 255V branches and old Castilla Anillo only where source-specific coverage is unambiguous.
