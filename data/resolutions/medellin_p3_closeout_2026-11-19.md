# Medellín P3 — 22 route family and third-party timetable research closeout (19 November 2026)

## Scope and outputs

All **22/22** historical ArcGIS P3 route IDs assessed against existing Coonatra published family averages and existing modern 087/088/090/091/103/107/203 public timetables.

- [22 one-row-per-route family evidence records](medellin_p3_22_family_route_evidence_2026-11-19.csv)
- [87 route/daytype/public-variant candidate rows](medellin_p3_family_daytype_candidates_2026-11-19.csv)
- [22 explicit P3 follow-up records](medellin_p3_followup_backlog_2026-11-19.csv)
- [Main 146-route action register with P3 review status](medellin_146_remaining_routes_action_register_2026-11-19.csv)

## Results

| P3 evidence class | ArcGIS ID count |
| --- | ---: |
| Coonatra direct operator averages and generic family operating spans (source daytype unspecified) | 4 |
| Public 087/088/091/103/107 third-party headways attached to the historic family without branch allocation | 15 |
| Other public 090/203 variant candidates with ambiguous old route mapping | 3 |
| **Total** | **22** |

**Twelve old IDs** have at least one source with a plausible Saturday full operating window (including public 203/090 and some 087/088/091/103). These are **provisional**: their individual historical branch identity has not been proven and weekday/Sunday all-day end times are frequently unreliable.

**No additional old route ID** is marked as having all three daytypes' credible frequency AND full working-hour span in the 2026 planning model solely from P3; aggregate stays **118/252**. All 22 receive source-family/variant evidence and remain deferred for specific missing windows or old/new variant identity checks. This is not a repetition of already validated official resolutions.

## Source handling

**Coonatra:** old 303, 300 DIR-80, 301 DIR-80 use the operator's *Circular Coonatra* **4-minute family mean** and published general family window **04:00–21:30**; old 311iiR Rosales uses *Calasanz Intermedia* **5-minute mean** and general window **04:10–21:30**. These are family-level operator observations, not official per-branch legal schedules or daytype-confirmed work hours.

**087 / 088 / 103 / 107:** previously retained Moovit headways are preserved against each related old ArcGIS variant using one shared family service ID. Do not multiply the 103 or 107 public circular's frequency by 4 or 6 old variants. The special-hours 087 variant is not automatically an independent full-day 087 timetable.

**091:** Moovit describes **four distinct** public 091 directions/variants with nonidentical 5/10/15-minute typical intervals. All observations are stored separately. Old 90243 Sucre and 90244 Llanadas cannot both receive all four simultaneous schedules; no sum or manufactured universal route frequency.

**090 and 203:** earlier Moovit end times near 04:50 after 05:00 startup are **not** accepted as proof of 24-hour operations. 090 has a plausible separate Saturday direction window **05:03–21:24**, 203 a Saturday **05:00–22:00** published candidate; neither proves a weeklong operating span or historic branch equivalence.

**Sunday vs Colombian public holiday:** source data for Sunday are held as `sunday_holiday` candidate records for review but `original_daytype_confirmed=sunday_only_holiday_unconfirmed`. This does not assert a published holiday timetable; later model calendar can apply the user's Sunday-holiday assumption transparently.

## Follow-up policy

All 22 P3 IDs remain in the detailed backlog because they require at least one of: exact branch-to-public-line mapping, missing non-suspicious weekday/Sunday closing time, branch daytype clarification or truly route-specific source. The separate 44 P1 and 15 P2 backlogs are unchanged.

Next priority P4: the 49 original IDs with no linked usable frequency+work window. Do not reopen vetted legal regulations or the parked 195ii / 082 PILOTO routes. GTFS generator untouched.

## Corrected binding user policy — 19 November 2026

**Authoritative project rule:** When an **official operating resolution** gives a frequency to a route family, **that same frequency applies to every route within that family**. Never split or dilute the legally published family frequency across member routes (no 50/50 allocation, no N-way multiplication of the headway). The per-route application of the official value is the requested timetable assumption. Retain the original act and family key on each route.

This supersedes any earlier wording in this report suggesting that official family frequency should be divided across branches, or kept only at family level instead of applying it to the member routes. Other evidence types must remain labelled accurately: Coonatra *operator-reported averages* and Moovit figures are **not** automatically the legally specified family frequency, and must not be falsely marked as such. Separate duplicate identity/direction records still need protection against inadvertently generating identical trips twice, but this does not justify dividing a valid official per-family headway.

P3 source records have not been promoted to official-resolution status by this policy correction.


## Binding 2026 source-selection policy (updated 19 November 2026)

**This decision overrides any older instructions in this report to split/dilute shared legal frequencies or use Moovit in the 2026 timetable.**

1. **Resolution baseline.** The last reviewed official operating resolution provides the accepted 2026 working timetable. Do not rerun a generic validity audit.
2. **Operator website precedence.** When the operator publishes applicable route/variant/family operating hours, headways or exact departures, use its published values **instead of conflicting resolution values** for those fields, preserving original legal source values for traceability. The route identity, source daytype and actual variant scope must be retained; unspecified daytypes are not invented.
3. **Legal family frequency applies without division to EVERY member route.** For example, a resolution family headway of 4 minutes is recorded as 4 minutes for each member route, not 8 minutes for two routes or 20 for five. Retain legal family ID and source on each route. Different historical IDs that are duplicates of the *same physical trip* still require avoiding duplicate GTFS trip records, but that must never justify splitting the official family headway.
4. **Moovit excluded.** Moovit frequencies, night-end times, or variants must not be used as 2026 schedule facts or GTFS generation input. Historical Moovit material remains in archival registers as evidence of earlier research, visibly labelled `moovit_usable=no` and `archive_only=yes`. Retire its P3 Saturday window count as a candidate for 2026 modelling.
5. **Source scope:** Generic Coonatra operator-wide averages can be used only with their own published family scope and provenance. Do not describe them as legal-resolution values or fabricate weekdays/weekends from generic hours.

All P1/P2/P3 route ledgers, P1 legal daytypes, P3 daytype candidate ledger, corresponding backlogs, central 146-route action register and the latest 252-route working model have been updated to reflect these flags. The current all-three-daytype coverage count remains **118/252** as no new official/operator timetable was discovered in this policy-only change. No GTFS generator edit was performed.
