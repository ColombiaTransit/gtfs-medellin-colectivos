# Transacoop

Builder: `scripts/build_gtfs_transacoop.py` · Output: `gtfs-transacoop.zip`

**9 routes, 342 stops, 32 trips**, zero validator errors. Serves Santa
Elena, the rural mountain corregimiento east of Medellín known for its
flower-growing tradition (the silleteros of the Feria de las Flores).

Note on the name: ArcGIS's `empresa` field reads **"Transacoop"**, but
the operator's real domain is **trasancoop.com** (letters transposed).
Treated as the same company based on the obvious name/place match, not
independently verified beyond that.

## Data sources

| Source | What it gives us | Where |
|---|---|---|
| Medellín ArcGIS transport layers (`VC_Transporte`) | Current official route geometry (per-direction) + stops (per-direction) for all 9 known `id_ruta`s | `scripts/download_medellin_transporte_layers.py`, `raw/medellin_raw/` |
| `trasancoop.com/transporte_publico_habitual.html` (fetched directly - no access block, unlike some other operators) | Real hours, and real per-branch frequency for 8 of 9 branches | `data/transacoop_route_mapping.yml` |

Sistema is **"6G"** — a third distinct system in this project, alongside
"8A" (Coonatra/Tax Maya/Metrosán/Poblado Laureles, covered by Gaceta
Oficial N°4325) and "6F" (Cootransmallat). No government frequency
document has been found for this system either — all schedule data
here comes from the operator's own website.

## The number-order matching — genuinely provisional

The website describes 9 numbered branches by their intermediate
villages, and ArcGIS has 9 routes named `98 Directa 1` through
`98 Directa 9`. These are matched **by number order alone**, per the
project owner's explicit direction — **not independently confirmed**.
A real attempt to verify this via village-name and stop-address
cross-referencing found genuine complications rather than confirmation:

- Several website branches name *multiple* villages that individually
  match *different* ArcGIS routes' `nombre` fields (e.g. website branch
  2 mentions both "Mazo" and "Piedras Blancas" — the named villages of
  ArcGIS's `Directa 1` and `Directa 6`/`9` respectively).
- `Directa 6`'s own `nombre` field says "Piedras Blancas," but one of
  its real stop addresses reads **"Vda el Mazo Santa Elena"** — meaning
  even the ArcGIS `nombre` field doesn't fully describe each route's
  real path.

Every scheduled route's `route_desc` field in the actual GTFS output
states this match is provisional, not confirmed — not just this doc.

## Real frequency handling — several genuine translation decisions

| Website source text | How it was built | Why |
|---|---|---|
| "10 min pico / 12 min valle" (branch 1) | 12 min flat | Same standing practice as every operator in this project: no clock-time boundary is ever given for peak hours |
| "30 min entre semana, fin de semana se incrementa" (branch 2) | 30 min for both `LunesSabado` and `Domingo` | The real weekday number is kept as a known floor; no real weekend number is given, so nothing tighter is invented |
| "cada hora" (branches 3, 4, 5, 9) | 60 min flat | Direct |
| "cuatro veces al día" (branches 6, 7) | ~240 min (weekday), ~210 min (Sunday) | Real operating window ÷ 4 — an approximation of even spacing, not a sourced headway |
| *(no frequency given)* (branch 8) | Spatial-only — real stops/shape, no trips | Same "don't fabricate" policy used throughout this project |

**Service days**: only 2 real patterns exist in the source — "Lunes a
Sábado" (one combined window) and "Domingos" — not the usual 3-way
weekday/Saturday/Sunday split used for other operators, since that
finer distinction isn't what this source actually states.

## A real, informative validator warning — not a bug

The rural mountain geometry produces `stop_too_far_from_shape` (15),
`stop_has_too_many_matches_for_shape` (2), and
`fast_travel_between_consecutive_stops` (4) warnings. These reflect a
genuine characteristic of these routes — long, winding roads with
sparse ArcGIS stop-to-line association, including one real stop near
**Guarne** (a neighboring municipality) landing over 5.5km from its
route's simplified geometry — not an error in the build logic.

## A real, dated news finding — not yet built

An April 2026 El Colombiano article describes a **10th, genuinely new
route** — connecting Barro Blanco and El Plan directly via a transfer
point at El Silletero, not a Santa Elena↔Medellín route like any of the
9 built here. Real schedule confirmed (Mon-Sat, 5:50 AM-7:15 PM, ~1hr
frequency), operated jointly by Alcaldía de Medellín and Transacoop,
but **no ArcGIS geometry exists for it** — likely too recent for the
ArcGIS snapshot this project uses. Not yet added to the build; would
need real geometry from somewhere, or a schedule-only entry with no
route line, before it could be included.

A separate AI-generated web summary conflated this specific article
with a general frequency claim about "las directas interveredales" —
checking the real article directly revealed it's about this one new,
different route, not additional confirmation for the 9 `Directa`
routes' frequencies.

## Known gaps / next steps
- The Barro Blanco↔El Plan connector route above.
- Village-name/geometry-based re-verification of the number-order
  match, if worth the effort.
- Branch 8's frequency, if a real number ever turns up.
- Branches 6/7's near-identical website text (same villages, same
  frequency) — worth checking whether these are genuinely 2 distinct
  services or a real site duplication.
