# Medellín P1 — 19 unresolved old-to-new route links, targeted resolution (19 November 2026)

## Outcome

The 19 unmatched historical ArcGIS route IDs from the 49-route P1 cohort have now been **individually matched to plausible legal family/corridor candidates or explicitly ruled out as safe one-to-one mappings**. The research is recorded in [the 19-row family crosswalk register](medellin_p1_19_unmatched_legacy_routes_family_reconciliation_2026-11-19.csv), which preserves the original 2025 resolution family, candidate codes, matching basis, reasons for uncertainty, and next focused geometry/stop check.

**Two old route IDs have relatively strong shared-service family name associations**, and their three official daytype headway/window rows are available in [this six-row evidence file](medellin_p1_19_shared_family_2026_daytype_evidence_2026-11-19.csv):
- **90079 / 253iAR (Palenque)** ↔ **253-i / Aures Integrada** (202550088689). The old record is a *ramal*: the modern 253-i legal service is not automatically a second independent service for this branch.
- **90110 / 261ii Estación Tricentenario (Castilla)** ↔ **263-1i / Estación Tricentenario** (202550076162). Old 90113 and 90114 were already candidate linked to the *same* new legal 263-1i; do **not** independently multiply the family timetable across three legacy records.

The 2025 official tables are treated as 2026 working-service baseline, **not rejected on recurring legal-effectivity grounds**. However, using a valid source does not by itself prove which *old* ArcGIS shape corresponds to a *new* 2025 service.

## Other candidates and why no unique numerical import is appropriate yet

- **90066 (250Aii)** old La Huerta Integrada, versus new 250-4 La Huerta and 250-4i Moravia Integrada: the name and integrated status point to *different* newer codes.
- **90365 (250VF_C)** combined Villa Flora–Curazao corresponds to *two independent* new named lines 250-1 and 250-2; one old fused route may not be assigned the sum of two headways.
- **90081 (255A)** Nuevo Occidente–Las Flores overlaps legal 255-4 Nuevo Occidente/Pajarito and 255-6 Lusitania/Flores; no exact combined destination match.
- **90347 (255V4 Las Playas)** lacks a matching named vereda in 2025 legal 255 route rows.
- **90372 and 90373 (255i Estadio, direct/regular)**: both share terminal/corridor attributes of 255-5i and 255-6i. Old La Aurora versus legal San Cristóbal/Nuevo Occidente identity is unresolved; do not duplicate two service tables on a shared corridor.
- **90105, 90106, 90371 (254/Pilarica)**: new Hospital-integrated 254-1i/254-2i and/or Troncal73 may be related, but there is no proven old Pilarica branch equivalence.
- **90108 and 90109 (261i right/left Estación Universidad)**: legal 261 integrated family uses other branch names (San Judas, López, Kennedy, Belalcázar). Only family-level reference is defensible.
- **90115 (265 Castillita)**: old code 265 absent from newer legal 2025 service codes. No arbitrary substitution.
- **90117 and 90118 (280 Santander Carrera73/direct)**: the official **TRONCAL 73** interval is a *corridor-wide* figure, not an independent 280 route frequency.
- **90131** matches legal Carrera65 horario **TRONCAL-7** geometrically, but old special-hours variant needs its own timetable and the 2025 Troncal-7 source row has no numerical interval.
- **90133** old Anillo F2 Carrera65 Av Regional/San Diego has no unique matching Troncal4/11 route geometry or numeric table.
- **90140** old Carrera73 Parque Los Periodistas and new Troncal13 Carrera65 Parque Los Periodistas are **not the same road**, despite sharing a landmark.

## Counting and work decision

- **19/19 old records reviewed** for modern source family and name conflicts.
- **2/19** now have daytype-specific official data **linked as family-level references** (six daytype records, no duplicate family trips).
- **0/19** are added as new *independent fully mapped* historical ArcGIS services because all require a specific branch/direction match or lack a corresponding legal route; **109/252** remains the conservative 2026 working full-window+headway count from the preceding P1 pass.
- **17/19** are still family/corridor/legacy-only crosswalk questions requiring historical shape/stop comparison or a newer exact branch record. These are **not** a request to reread already extracted 2025 regulations.
- The separately parked Tax Maya 195ii and Flota Nueva Villa 082 PILOTO remain out of scope. GTFS generator and production files were not touched.

## Recommended next bounded evidence operation

Use existing ArcGIS directional shapes and any 2025 legal GTPC/route geometry to compare the 17 unresolved branch candidates; focus first on 250Aii, 250VF_C, 255A, 255i Estadio and 254 Pilarica. For Anillos, map shared corridor evidence without manufacturing extra route-level headways. Keep all legal headway/max interval and service-day values attached to the candidate modern services even when the old shape correspondence remains unresolved.
