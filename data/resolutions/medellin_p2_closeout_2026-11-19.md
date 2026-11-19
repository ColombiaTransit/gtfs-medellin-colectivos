# Medellín P2 — 24-route source reconciliation and closeout (19 November 2026)

## Outcome

The **24/24 P2 ArcGIS route identities** were reviewed against already stored visual verified 2015 fiches, Coonatra direct operator windows and exact departure tables, and the existing 2025 Rápido San Cristóbal legal source family. No full legal-resolution rescan or GTFS generator change was needed.

- **9 additional historic route IDs** have now been adopted as *2026 working-model* frequency+operating-window candidates using their **specific, inspected original 2015 fiche**, under the user's approved 2026 source assumption.
- The **nine ArcGIS IDs correspond to seven distinct source service keys**; two pairs share a printed service. No doubled dispatch supply is implied.
- **15/24** P2 identities still require an exact route/daytype or numeric-data follow-up (7 Coonatra, 6 Rápido San Cristóbal, 1 Flota la Milagrosa 110, 1 Tax Maya C23i Pedregal).
- The aggregate **252-ID three-daytype working-model count rises from 109 to 118**. This is a route-ID *source coverage count*, not a GTFS trip count or legal independently corroborated 2026 effectivity.
- All P2 24 source/decisions and the 15 remaining follow-ups are recorded in the central 146-route action register. The two parked IDs remain excluded; the GTFS generator is untouched.

## Accepted original 2015 source records (2026 planning assumption)

| Historical ArcGIS ID | Route/branch | Inspected original fiche | Shared service key treatment |
|---|---|---|---|
| 90175, 90176 | Flota la V 097 Cauces–Quinta Linda | Gaceta 4327, Resolución 1047, p398 | Same **one** 097 Cauces printed service for both IDs |
| 90179 | Flota la V 097 Quinta Linda–El Vergel | Gaceta 4327, Resolución 1047, p396 | Separate 097 El Vergel service; printed weekday/Sat **03:50–10:30**, weekday **48/4 min normal/HMD**, copied literally, **not silently corrected** |
| 90206, 90207 | Transporte Aranjuez Santa Cruz 024 Playón de los Comuneros | Gaceta 4325, p132 | One **shared** published 024 service for two old directional/shape IDs |
| 90329 | Tax Maya C23i Asomadera | Gaceta 4325, p228, C23iAV | Own Veredal Asomadera fiche, not generic C23-i |
| 90330 | Tax Maya C23i El Patio | Gaceta 4325, p230, C23iPV | Own Veredal El Patio fiche |
| 90331 | Tax Maya C23i La Palma | Gaceta 4325, p236, C23iPALV | Own Veredal La Palma fiche |
| 90332 | Tax Maya C23i Las Playas | Gaceta 4325, p232, C23iLPV | Own Veredal Las Playas fiche |

**Not promoted:** 90333 / old route C23i **Pedregal Bajo** points toward p234 **Pedregal Alto Veredal**. The original official record is reusable as family evidence, but Bajo and Alto are not demonstrated to be one and the same variant. This discrepancy remains a single targeted identity check, not another complete legal research round.

## Coonatra (7 P2 IDs)

- 90005 Circular 300: 04:10–21:30 direct operator published; no verified route-specific daytype headways.
- 90006 Circular 301: 04:10–21:30 direct operator published; no verified route-specific daytype headways.
- 90007 Circular 310 Directo Calasanz Boston: **95** operator-published exact departures; original daytype and direction unspecified.
- 90008 Circular 311 Calasanz Boston: **138** operator-published exact departures; same daytype/direction caveat.
- 90320 route 243 Divisa: **05:45–17:55**, operator website.
- 90321 route 243 Quiebra: **06:05–17:13**, operator website.
- 90363 route 310R: **two distinct printed 310 Rosal/310 Metro Rosal variants**, 05:06–20:06 vs 05:00–22:00 operator website, **43 exact departures each** in one older PDF. Do not merge or add both lists to the same historic service without matching the branch.

Coonatra's 2024–27 reported network averages are **operator-family averages**, not individual statutory branch frequencies. The 2022 PDF exact departures are retained as usable candidate *times*, not assigned to Monday–Sunday without source daytype evidence.

## Rápido San Cristóbal (6 P2 IDs)

Old 90085 255iD Aurora direct, 90086 255P Palmitas Centro, 90087 255V1 El Llano Parque, 90092 255A Nuevo Occidente El Tirol, 90093 255A Las Flores Moravia Centro, 90351 255i El Llano have 2025 legal family candidates, but no proven old historical variant-to-single-current-service link:
- 90085 ↔ modern **255-1i** (direct sibling of 90084, avoid duplicating 255-1i)
- 90086 ↔ **256-1/2/3/4** fixed departure directions (not a generic interval)
- 90087 ↔ **255-1v / 255-5v** El Llano veredal services
- 90092 ↔ **255-4 / 255-5**, old El Tirol name absent from the modern legal table
- 90093 ↔ **255-6 / 255-7**, mixed Flores/Moravia route names
- 90351 ↔ **255-1v / 255-2v / 255-5v**, ambiguous El Llano variants

Keep already known exact operator departures for Rápido San Cristóbal in their existing original register. This pass did not overwrite them with fictitious headways.

## Remaining blocker

- 90188 / Flota la Milagrosa 110: original official 2015 weekday/Sat **HMD = 0 min**, cannot form a valid positive dispatch interval. No automatic conversion to 'no service' or substitution from another route.

## Files

- [P2 detailed decisions, all 24 routes](medellin_p2_24_route_resolution_2026-11-19.csv)
- [P2 ten historical routes, 30 daytype records and specific original fiche values](medellin_p2_historic_10_variant_daytypes_2026-11-19.csv)
- [252-route 2026 working status after P2](medellin_252_schedule_2026_working_assumption_p2_updated.csv)
- [P2 deferred 15-route backlog](medellin_p2_followup_backlog_2026-11-19.csv)
- [Main 146-route action register](medellin_146_remaining_routes_action_register_2026-11-19.csv)

## Next

Continue with P3 (shared family-level headways and external timetable sources) and then P4 genuine missing timetable references. P1's previously deferred 44 and P2's deferred 15 should not cause repeated broad source research.


## Binding 2026 source-selection policy (updated 19 November 2026)

**This decision overrides any older instructions in this report to split/dilute shared legal frequencies or use Moovit in the 2026 timetable.**

1. **Resolution baseline.** The last reviewed official operating resolution provides the accepted 2026 working timetable. Do not rerun a generic validity audit.
2. **Operator website precedence.** When the operator publishes applicable route/variant/family operating hours, headways or exact departures, use its published values **instead of conflicting resolution values** for those fields, preserving original legal source values for traceability. The route identity, source daytype and actual variant scope must be retained; unspecified daytypes are not invented.
3. **Legal family frequency applies without division to EVERY member route.** For example, a resolution family headway of 4 minutes is recorded as 4 minutes for each member route, not 8 minutes for two routes or 20 for five. Retain legal family ID and source on each route. Different historical IDs that are duplicates of the *same physical trip* still require avoiding duplicate GTFS trip records, but that must never justify splitting the official family headway.
4. **Moovit excluded.** Moovit frequencies, night-end times, or variants must not be used as 2026 schedule facts or GTFS generation input. Historical Moovit material remains in archival registers as evidence of earlier research, visibly labelled `moovit_usable=no` and `archive_only=yes`. Retire its P3 Saturday window count as a candidate for 2026 modelling.
5. **Source scope:** Generic Coonatra operator-wide averages can be used only with their own published family scope and provenance. Do not describe them as legal-resolution values or fabricate weekdays/weekends from generic hours.

All P1/P2/P3 route ledgers, P1 legal daytypes, P3 daytype candidate ledger, corresponding backlogs, central 146-route action register and the latest 252-route working model have been updated to reflect these flags. The current all-three-daytype coverage count remains **118/252** as no new official/operator timetable was discovered in this policy-only change. No GTFS generator edit was performed.
