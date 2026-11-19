# Medellín Urbanas: practical 2026 schedule assumption (19 November 2026)

## User decision

**Use every reviewed official resolution as the working 2026 timetable until a later contradictory source is confirmed.** Stop repeatedly checking whether the same reviewed 2015 source remains formally valid; future operator website checks are optional. This is a planning/GTFS-model working assumption, **not** a legal conclusion that 2015 authorization is presently effective.

## Recalculated research route model

- **252** legacy ArcGIS identities; **756** route-daytype entries.
- **49** baseline all-daytype frequency+operating window source candidates.
- **57** additional historic 2015 reviewed routes assumed usable as the current 2026 *working model* (34 normal historic provisional + 13 with later act changes not yet numerically retrievable + 10 structurally explained historic overnight/shared cases).
- **106 of 252** routes have both frequency and operating windows in the *working 2026 research model* across the three daytypes; this supersedes the previous 83-route *conservatively reviewed* research count **only as an explicit user-approved modeling assumption**.
- **10** legacy variant identities remain ambiguous: no forced branch-specific timetable mapping; they still retain original historical evidence.
- **1** historic source print zero headway (Flota la Milagrosa 110) remains invalid for headway generation.
- **2** parked routes (90290 Tax Maya 195ii; 90370 Flota Nueva Villa 082 PILOTO) remain untouched.
- The **13** with later operating acts are marked `later_operating_amendment_caution`; their reviewed 2015 figures are accepted *for now* rather than blocking the entire model. Where separate newer direct operator first/last departures are already known for Coonatra, keep them as source-specific candidate windows; they do not imply exact weekdays/weekends.
- A service ending 02:00 the following day can be represented as 26:00 in the new working daytype table (5 legacy 6C routes).
- Shared 2015 fiche families/directions are tagged with one `shared_historic_2015_service_id` and `avoid_duplicate_2015_service=yes`, not multiple independently additive trip supplies.
- Already recorded Moovit/public shared 087/088/091/103/107 family headways and operator family averages remain attached to each matching route in the existing consolidated register but are not misrepresented as **official resolutions** or automatic individual headways.

## Clear separation of meanings

`assumed_2026_window_and_frequency_three_daytypes=yes` = the project chooses to build a 2026 working hypothesis using reviewed resolution values. It **does not mean** `current_2026_legally_verified=yes`, route identity is guaranteed, GTFS validator approved, or the model has live schedule observations. Legal QA and production import flags remain `no` pending the future generator phase.

## Output files

- [252-route working model audit](medellin_252_schedule_2026_working_assumption.csv)
- [756 source-preserving working daytype rows](medellin_252_daytypes_2026_working_assumption.csv)

No original legal source register was rewritten and no GTFS generator changes were made.
