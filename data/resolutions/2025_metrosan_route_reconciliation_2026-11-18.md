# Metrosan 2025 legal route crosswalk and source QA (18 November 2026)

## Authoritative sources
- [Resolución 202550079848/2025 (official ASTREA original)](https://www.medellin.gov.co/normograma/docs/astrea/docs/r_smmed_79848_2025.htm).
- `data/resolutions/2025_astrea_official_route_timetable_candidates.csv` — original official table values, still requiring full period-definition and numeric acceptance.
- `data/medellin/routes.csv` — older Medellín ArcGIS snapshot.
- `data/resolutions/2025_metrosan_legal_to_arcgis_crosswalk.csv` — identity candidates and unmatched historical records.

## Route identities
The 2025 original publishes **8 user route codes** with **16 directional GTPC records**. Exactly **8** of the direction records contain the published numerical service-time/headway cells. The alternating return-direction rows have blank numeric cells. These *must not* be treated as missing independent routes, duplicated headway services, or proof of identical departure times in both directions; distinguish table formatting from directional timetables.

Eight name/family-supported candidates join the original to older ArcGIS IDs:

| Legal user code | Older ArcGIS id_ruta / code | Name |
|---|---|---|
| 225-i | 90307 / 225i-1 | 20 de Julio |
| 226-1i | 90309 / 226i | Salado |
| 226-2i | 90310 / 226i-D | Depósito |
| 227-1i | 90312 / 227i-A | Peñitas |
| 227-2i | 90313 / 227i-B | Gabriela |
| 227-3i | 90315 / 227i-C | Caseta |
| 227-4i | 90311 / 227i-1 | Quintas |
| 228-i | 90316 / 228i | Conquistadores |

These are **route identity candidates**, not validated shape matches. In particular, the printed `legal GTPC code` is direction-sensitive. Use the pair (resolution, user code) for legal service family identity while retaining both directional GTPC rows.

## Do not silently discard unmatched older ArcGIS records
- 90308 / 225i-2 Colinas — no matching route/name in the eight published 2025 Metrosan families.
- 90314 / 227iB-2 Socorro — no matching route/name in those eight families.
- 90377 / 229i Barrio Nuevo — belongs to a **different shared-operation decision**, 202650039611/2026, already indexed separately. Never attach its timetable to 202550079848/2025 or double its joint service.

**Interpretation:** no appearance in the 2025 service table is *not* an independently confirmed cancellation; investigate explicit repeals or replacements before excluding these old ArcGIS records.

## Targeted 2026 index scan
GitHub Actions [#44272664218](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44272664218) scanned all 25 documents in the official indexed 2026 Secretaría de Movilidad ASTREA list successfully. It found two documents with incidental operator group terms, including the separate 2026 shared 229i decision. The January 2026 act 202650000843 concerns transport fares, not evidence of Metrosan headway/restructuring changes. **This limited text screen is not exhaustive evidence that no later amendments exist**; the municipal post-August 2026 Gaceta title scan was likewise an index-only screen.

## Next focused work
1. Validate route direction and geometry against ArcGIS shape/stop data for the eight candidates.
2. Inspect the original 2025 article wording on transitional/withdrawal rules for 225i-2 Colinas and 227iB-2 Socorro; do not infer repeal by omission.
3. Verify 2025 clock period definitions before interpreting maximum `despacho` intervals.
4. Keep shared 229i in its separate operator/joint-service register.

**No new GTFS generation and no automatic route retirement based on this research.**
