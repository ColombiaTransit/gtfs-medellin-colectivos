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
