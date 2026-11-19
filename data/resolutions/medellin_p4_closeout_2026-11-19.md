# Medellín P4 — 49 routes without linked complete service schedules (19 November 2026)

## Scope and source hierarchy

All **49** original P4 ArcGIS route IDs were individually classified, using the previously extracted Medellín 2015 Gaceta tables, reviewed 2025 operating resolutions, and targeted **direct operator webpages**. The user-defined decision is authoritative: **official resolution as 2026 baseline; operator-published route schedule overrides where applicable; no Moovit**. A family frequency printed in a resolution applies **unchanged to each member route**, never divided by their count.

P4 results:
- **8 Cootransmallat historic route IDs** have directly published **daily** family operating windows of **04:00–23:30**. These are **5 old IDs in route family 105** and **3 in family 106**. **No verified headway on the operator's webpage**: these are *partial*, not complete 2026 working schedules.
- The company explicitly says the main routes are **105 Golondrinas/El Faro** and **106 Tres Esquinas**, and that night/special corridor traces are **time-of-day variants of the main services, not standalone full-day route supply**. Both families serve Minorista until **18:00**, when the Bolivia destination replaces it; do not fabricate separate full-day demand from old route labels like 'horario especial' and 'horario nocturno'.
- **1 historical 287 Terminal Norte** directly listed by operator Autobuses El Poblado Laureles; route existence confirmed, **numeric departure frequency and operating windows not published in the fetched page**.
- **1 route 302 Circular Sur Izquierda** has a *historical municipality urban planning document* giving weekday/Saturday 04:30–21:30, Sunday 05:00–21:00, reported peak 2 minutes and nonpeak 2.5 minutes. This is an **older planning description, not an inspected 2025/2026 operating resolution and not a current operator timetable**. Do not silently promote it to a verified current 2026 schedule. Preserve the source and figures only as a historical lead.
- Original 2015 official source family candidates found for selected route IDs, but no safe new exact branch correspondence: **099 special** (normal 099 source), **102D** (normal 102), **246C/D** (246 AL2), **201B and old 200** (201/201-i), **221B**, **223**, **C23 Alterna/C23**. For 096 and 6C corridor variants, no corresponding exact reviewed source record matching the branch was found.
- **19 P4 IDs** are still unlinked to an official or direct-operator route-specific schedule even at the family level within the bounded search. The remainder have partial family, historical or identity evidence. No expired/ambiguous source was substituted as current.
- **0 additional routes** newly have both trustworthy frequency and work window on all three daytypes. Thus the overall **118/252** complete legacy route-ID count stays unchanged. No GTFS generator or feed changes.

## Operator website source

**Cootransmallat**, https://www.cootransmallat.com/ (inspected 19 Nov 2026):
- 105 Golondrinas / El Faro — weekdays, Saturdays, Sundays: 04:00–23:30.
- 106 Tres Esquinas — weekdays, Saturdays, Sundays: 04:00–23:30.
- Destination change 18:00: Minorista to Bolivia. Other daytime destinations include Centro/Maturín.
- 105 / 106 variations described as time-specific route variations, **not independent new route frequencies**.

**Autobuses El Poblado Laureles**, https://www.autopobla.com.co/ (inspected 19 Nov 2026): route 287 Norte Terminal Norte–Centro appears in operator's route list; detailed numeric bus times not available from the retrieved index. The website's **office opening hours are not bus operating hours**.

## Files and next focused work

- [49-route P4 source audit](medellin_p4_49_source_reconciliation_2026-11-19.csv), one row per legacy ArcGIS ID, with provenance, source classification and missing source field.
- [24 Cootransmallat route/daytype operating-span records](medellin_p4_cootransmallat_operator_daytypes_2026-11-19.csv) with family keys and explicit empty headways.
- [P4 49-row follow-up backlog](medellin_p4_followup_backlog_2026-11-19.csv). Source tasks are now bounded: find official frequency/headway for 105 and 106; inspect 287 operator route details; compare historical branch evidence for older 099/102/246/C23 etc. Get actual operator or official schedule for remaining source-free routes.
- [Updated 252-route working model after P4](medellin_252_schedule_2026_working_assumption_p4_updated.csv).
- [Central 146-route action register](medellin_146_remaining_routes_action_register_2026-11-19.csv).

The P1/P2/P3 backlogs remain unchanged and Moovit is excluded from all current 2026 timetable modelling. The two parked old routes 90290 and 90370 stay untouched.

## Targeted frequency follow-up (19 November 2026)

The initial P4 closeout is superseded for source coverage by the [targeted original-act follow-up](medellin_p4_targeted_legal_frequency_followup_2026-11-19.md). This identified specific 2015/2019/2020/2021/2023 Cootransmallat acts affecting 105/106, though their original numeric dispatch annex remains unavailable; added [Coopetransa's 2024 original operator reproduction of the 2023 069 act](medellin_p4_069_resolution_2023_original_daytypes_2026-11-19.csv) giving **03:00–23:00** and original DÍA/HMD cells, *not interpretable yet as minute headways*; and found original act IDs for 246C/D, 096, 287, 6C/037/039 and 286. The 49-route audit, P4 backlog, and 252-route model now carry these links. **No new complete route count**: 118/252.
