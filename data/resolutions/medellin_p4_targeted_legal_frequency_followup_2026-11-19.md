# Medellín — targeted P4 frequency and timetable source follow-up (19 November 2026)

## Work performed

Narrowed the **49 P4 IDs** (not another route-wide rescan) to official acts with matching legal scope. Checked Cootransmallat's own webpage, Medellín Secretaría de Movilidad administrative acts register, and an original Coopetransa operator-published 2024 annual report reproducing its 2023 official 069 route decision. No Moovit data used.

## Confirmed new evidence — 069 El Jardín / La Cima

The [2023 annual report by Coopetransa, published 2024, page 23](https://coopetransa.com/wp-content/uploads/2024/05/3-Informe-de-gestion-ano-2023.pdf) directly reproduces route technical fiche approved in **Resolución 202350107467 of 28 December 2023**, replacing/amending the 2017 6E operating framework. It explicitly identifies:
- **069 El Jardín** (old legacy 90238) and **069 El Jardín–La Cima** as an alternative route/branch (old legacy 90376).
- **03:00–23:00** operating window in the original official table.
- Original printed **DÍA/HMD** cells: **weekday 228/24, Saturday 228/24, Sunday 137/15, holiday 137/15**.
- The heading says `FRECUENCIAS DE OPERACIÓN`, but a **228-minute dispatch interval is plainly implausible**. No claim is made about the units/meaning of either printed cell; retain exactly as published, **NOT as minutes**, until the numeric definitions are confirmed. Likewise do not treat all eight entries as separately independent frequency supplies for route 069 and its ramal.
- The operator source has higher precedence than an older conflicting legal figure, under current project policy.

The raw original 8 route/daytype entries and unambiguous 03:00–23:00 are saved in [069 original legal source data](medellin_p4_069_resolution_2023_original_daytypes_2026-11-19.csv), also tagged in the [49-route P4 source register](medellin_p4_49_source_reconciliation_2026-11-19.csv) and the 252-route working model.

## Cootransmallat — precise original act references found

The [official Medellín administrative acts register](https://www.medellin.gov.co/es/wp-content/uploads/2023/08/AIG-Mateo-Gonzalez-Benitez-Sec-Movilidad.pdf) lists:
- Resolution **896 of 27 August 2015** restructuring **087/088/090/091/105/106**. Also 898, 1002/2015 and 2098/2015 under the shared 6F system (not necessarily a 2026 route-specific dispatch schedule).
- **201950020664** of 8 March 2019 (referred to by 2020 amendment).
- **202050081986** of 26 December 2020: route/direction changes in **106 Tres Esquinas / 106 Minorista**.
- **202150041167** of 23 April 2021: 6F collaboration framework.
- **202350086596** of 24 October 2023: 6F operational changes.
- **2023350087382** of 26 October 2023: formal typing correction to the 2023 act; this is not automatically a new numerical timetable.

**The original 2019/2021/2023 annex tables with 105/106 per-daytype numeric dispatch headways were not recovered in this targeted pass.** Do not fabricate headways. The [Cootransmallat operator website](https://www.cootransmallat.com/) continues to specify **04:00–23:30 every day**, with Minorista service replaced by Bolivia destination after 18:00. Relevant **eight old ArcGIS IDs** retain this as a confirmed partial operator timetable.

## Other newly located route-specific legal acts (rather than generic searches)

| Old route IDs | Route | Targeted resolution(s) | What to extract |
|---|---|---|---|
| 90059; 90061 | Cootransblan 246D / 246C | **175 of 3 March 2017** | Official 246C and 246D variant-specific frequency and window |
| 90172 | Autobuses Poblado Laureles 287 | **220 of 13 March 2017** and **202150129293 of 12 August 2021** | Latest route 287 technical fiche |
| 90173;90174 | Flota la V 096 special/main | **201950070736** and **202350064269 of 14 August 2023** | Determine if 2023 amendment updates route only or dispatch tables |
| 90217–90219; 90215;90224 | Autocol 037/039, ATCEX 031 and 51/52 corridor | **392 of 4 May 2017** | Check individual routes/directions within 6C, not a borrowed shared corridor average |
| 90002 | Combuses 286 | Official 2017 restructure in register; act number not yet transcribed | Retrieve route-specific 286 numeric data |
| 90238;90376 | Coopetransa 069 and ramal | **202350107467 of 28 December 2023** | Interpret printed DÍA/HMD values, retaining 03:00–23:00 |
| 90236 | Coopetransa 057 Bello Oriente | 6E family, **not** the 069 legal table | Separate own route/headway source |

The central 146-route queue and 49-route P4 backlog now show these targeted official act IDs and next source-specific tasks. Do not reread 2015 historic fiches unnecessarily.

## Coverage and rules

**118/252** remains the number of old route IDs with all three daytypes' complete interpreted frequency plus service window in the 2026 working model. We have new **documented operating windows** and direct **original numeric source cells**, but the latter aren't safely interpretable as headways. Operator website supersedes resolution where route-specific and applicable; otherwise the reviewed resolution is accepted as 2026 planning baseline; **official family frequency applies unchanged to each member route**; **Moovit excluded**. No GTFS generator changes, no addition of parked IDs.


## Authoritative 069 DÍA/HMD interpretation and rounded working scenario — 19 November 2026

The user confirmed: **DÍA = total daily trips**, **HMD = number of trips per hour during maximum-demand hour**, not an interval in minutes. This supersedes the earlier uncertainty expressed above. Resolución 202350107467 (as reproduced in Coopetransa's annual report) provides a **03:00–23:00** window, **228 trips/day and 24 peak trips/hour** on weekday/Saturday and **137 trips/day and 15 peak trips/hour** on Sunday/public holiday.

The peak clock bands **06:00–08:30** and **16:30–19:30** are **adopted modelling assumptions**, not verified route-069 legal clock times. They total **5.5 peak hours**, leaving **14.5 valley hours**.

The valley headway is derived from the total published daily departures under the additional assumption that all 5.5 peak hours operate at the HMD hourly rate:
`valley_headway_minutes = 60 * 14.5 / (daily_trips - 5.5 * peak_trips_per_hour)`.

| Day type | Original daily trips | Original peak trips/h | Exact peak interval | Exact calculated valley interval | User-requested whole-minute **ceiling** model |
|---|---:|---:|---:|---:|---|
| Weekday | 228 | 24 | 2.5 min | 9.0625 min | **3 min peak / 10 min valley** |
| Saturday | 228 | 24 | 2.5 min | 9.0625 min | **3 min peak / 10 min valley** |
| Sunday | 137 | 15 | 4 min | 15.9633 min | **4 min peak / 16 min valley** |
| Public holiday | 137 | 15 | 4 min | 15.9633 min | **4 min peak / 16 min valley** |

The original **228 and 137 total daily trips** remain authoritative source counts. Whole-minute rounding **does not reproduce exactly** those totals and, for weekday/Saturday, 3-minute peaks amount to **20 departures/hour, not the 24/hour** published as HMD. Therefore the integer headways are an **explicit modelling approximation**, not a faithful restatement of the legal maximum-hour requirement. If the eventual generator must honor exact peak throughput, it will need shorter intervals, alternating 2- and 3-minute departures, or a timetable-based adjustment.

This policy is written in the [069 route/daytype source register](medellin_p4_069_resolution_2023_original_daytypes_2026-11-19.csv), [P4 audit](medellin_p4_49_source_reconciliation_2026-11-19.csv), [49-route backlog](medellin_p4_followup_backlog_2026-11-19.csv), [central worklist](medellin_146_remaining_routes_action_register_2026-11-19.csv) and [252-route working-model table](medellin_252_schedule_2026_working_assumption_p4_updated.csv). It does **not** advance the 118/252 strictly source-backed completion count, and no generator changes were made.


## Focused follow-up — 246 DIRECTA official table, 096 and 105/106 change scope (19 November 2026)

**New original numeric legal source located:** [Gaceta 4348, Resolución 2981/2015, technical fiche 246 DIRECTA](https://www.medellin.gov.co/irj/go/km/docs/pccdesign/SubportaldelCiudadano_2/PlandeDesarrollo_0_15/Publicaciones/Shared%20Content/GACETA%20OFICIAL/2015/Gaceta%204348/RESOLUCION%202981%20DE%202015.pdf), original published page 13. **04:30–23:00**; weekdays **73 trips/day, 6 trips/HMD; published dispatch intervals DÍA 16 minutes / HMD 11 minutes**; Saturday **73/6; 16/10 min**; Sunday and holiday **37/3; 31/20 min**. These are the *officially printed intervals*, which are preserved alongside trips and HMD values; do not overwrite them with a calculated average. Saved as [four official 246 DIRECTA daytype source records](medellin_p4_246_directa_2015_official_daytypes_2026-11-19.csv).

- Legacy **90059 / 246D “Blanquizal Calazanía directa”** is a **directa candidate**, not a verified exact match to old 246 DIRECTA; the 2015 document also describes a **one-for-one alternating service arrangement** under a transitional authorization. Never duplicate transit supply from this ambiguous transitional record.
- Legacy **90061 / 246C** is **not** automatically the 246 DIRECTA fiche. **Resolución 175 of 03 March 2017** explicitly restructured 246, 246C, 246D, 246I and 246ii; its **numeric annex is not yet recovered**. This 2017 route-specific source is the next exact document to inspect before accepting the 2015 numbers for 2026, according to the resolution-baseline/ operator-website-override rule.
- **096 Flota la V**: the published object of **202350064269 (14 Aug 2023)** expressly says it **modifies the route path** of 096 in **201950070736 (01 Aug 2019)**. No evidence that the 2023 route-only change supplies or amends numeric headways; use 2019's numeric schedule as next target, not another generic 2023 search.
- **Cootransmallat 105/106**: official index **202350086596 (24 Oct 2023)** modifies/clarifies 2021 6F framework; **2023350087382 (26 Oct 2023)** fixes a **formal transcription error** in that act. The correction is **not** independent timetable evidence. Source of operating spans remains the [operator's direct website](https://www.cootransmallat.com/), **04:00–23:30 daily**, with 18:00 destination switch. Exact 2023 timetable annex is still absent, so **no invented frequency**.
- Source coverage improves but **the complete schedule count remains 118/252**. The last P4 model and central register retain the original 069 HMD/DÍA/rounded working assumptions unchanged. No Moovit and no generator update.

