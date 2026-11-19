# P1 closeout and deferred worklist — Medellín Urbanas, 19 November 2026

## Status
- **49/49 P1 historic route IDs reviewed** against already extracted official 2025 legal tables (147 route-daytype source rows).
- **5 route IDs have sufficiently described 2026 working source rules:** 90084, 90125, 90126 (three daytypes) and 90012, 90014 (weekday only, explicitly no weekend/holiday service).
- **44 route IDs retain specific follow-up work**, chiefly historical ArcGIS geometry/direction and official-service-code mapping. This includes the **19 formerly unmatched** IDs: all 19 were reclassified by plausible family/geometry, but only **2** received tentative shared-family legal evidence (90079 253-i Aures and 90110 263-1i Tricentenario), and neither is counted as an independent new full route.
- The official 2025 **frequency and working-hour extraction stage for P1 is complete**; the remaining 44 are deferred identity/data-quality tasks, not repeated legal-validity research. This is not a claim that P1 GTFS production is complete.
- The previously reported 109/252 complete three-daytype working-model estimate remains unchanged.
- Do not reopen the parked routes 90290 (Tax Maya 195ii) and 90370 (Flota Nueva Villa 082 PILOTO), and do not alter GTFS generator.

## Pending statuses (mutually exclusive)
- **2** — `MISSING_MODERN_TABLE`
- **4** — `FAMILY_VARIANT_MATCH_OPEN`
- **19** — `FAMILY_CANDIDATES_CLASSIFIED_GEOMETRY_OPEN`
- **1** — `SOURCE_STAGED_CHECK_GEOMETRY_OR_CONFLICT`
- **3** — `RURAL_COUNTS_RETAINED_TRIP_ALLOCATION_OPEN`
- **2** — `SHARED_RURAL_DAILY_COUNTS_DIRECTION_ALLOCATION_OPEN`
- **2** — `SHARED_SERVICE_VARIANT_MATCH_OPEN`
- **1** — `ROUTE_NAME_CONFLICT_OPEN`
- **10** — `CORRIDOR_IDENTITY_ONLY_MISSING_NUMERIC_SOURCE`

## Execution policy
1. Prefer comparing already acquired ArcGIS directional geometry and stops with new official 2025 line descriptions. Do not read the 2025 legal tables again.
2. Old fused route versus multiple legal services: never add the independent headways together automatically.
3. Shared family 253-i, 263-1i or rural 255-7v: keep **one shared service ID** even where several old ArcGIS variants point at it; preserve original source-specific daytypes, counts and operating spans.
4. Where no numeric official timetable exists for an Anillo corridor or Metrosan Colinas/Socorro, log a genuine source gap rather than copy trunk or sibling line headways.
5. Treat already inspected resolutions as the accepted 2026 working model per user instruction; subsequent site checks are optional if they resolve an actual inconsistency.

## Registers
- [Main 146-route register, now including P1 closure/follow-up columns](medellin_146_remaining_routes_action_register_2026-11-19.csv)
- [44 remaining P1 tasks, one row per historical ID](medellin_p1_followup_backlog_2026-11-19.csv)
- [All 49 P1 legal code decisions](medellin_p1_49_route_legal_crosswalk_2026-11-19.csv)
- [All 19 previously unmatched candidate and conflict decisions](medellin_p1_19_unmatched_legacy_routes_family_reconciliation_2026-11-19.csv)

**Next working group after P1 research closeout:** P2, using the existing 146-route queue. P1's 44 follow-ups remain open but should not block progressing to P2.


## Binding 2026 source-selection policy (updated 19 November 2026)

**This decision overrides any older instructions in this report to split/dilute shared legal frequencies or use Moovit in the 2026 timetable.**

1. **Resolution baseline.** The last reviewed official operating resolution provides the accepted 2026 working timetable. Do not rerun a generic validity audit.
2. **Operator website precedence.** When the operator publishes applicable route/variant/family operating hours, headways or exact departures, use its published values **instead of conflicting resolution values** for those fields, preserving original legal source values for traceability. The route identity, source daytype and actual variant scope must be retained; unspecified daytypes are not invented.
3. **Legal family frequency applies without division to EVERY member route.** For example, a resolution family headway of 4 minutes is recorded as 4 minutes for each member route, not 8 minutes for two routes or 20 for five. Retain legal family ID and source on each route. Different historical IDs that are duplicates of the *same physical trip* still require avoiding duplicate GTFS trip records, but that must never justify splitting the official family headway.
4. **Moovit excluded.** Moovit frequencies, night-end times, or variants must not be used as 2026 schedule facts or GTFS generation input. Historical Moovit material remains in archival registers as evidence of earlier research, visibly labelled `moovit_usable=no` and `archive_only=yes`. Retire its P3 Saturday window count as a candidate for 2026 modelling.
5. **Source scope:** Generic Coonatra operator-wide averages can be used only with their own published family scope and provenance. Do not describe them as legal-resolution values or fabricate weekdays/weekends from generic hours.

All P1/P2/P3 route ledgers, P1 legal daytypes, P3 daytype candidate ledger, corresponding backlogs, central 146-route action register and the latest 252-route working model have been updated to reflect these flags. The current all-three-daytype coverage count remains **118/252** as no new official/operator timetable was discovered in this policy-only change. No GTFS generator edit was performed.
