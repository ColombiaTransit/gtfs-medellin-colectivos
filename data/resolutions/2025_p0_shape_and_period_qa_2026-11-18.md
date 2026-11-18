# P0 geometry and verified-period audit — 18 November 2026

## Existing ArcGIS source geometry measured (no rescrape)

GitHub workflow [#44318332385](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44318332385) completed successfully. It measured the **existing** official ArcGIS snapshot `data/medellin/geojson/6_rutas_transporte_publico.geojson` with its actual **EPSG:9377 projected coordinates (metres)**. This is a physical polyline measurement of the archived source, **not** proof of legal itinerary correspondence.

The full per-direction source lengths, projected endpoints and flags are in [`2025_p0_arcgis_direction_geometry_audit.csv`](2025_p0_arcgis_direction_geometry_audit.csv); severe anomalies are summarized in [`2025_p0_geometry_discrepancy_triage.csv`](2025_p0_geometry_discrepancy_triage.csv).

| Historical ArcGIS route | Origen–Destino source length | Destino–Origen source length | Official 2025 reference length | Geometry triage |
|---|---:|---:|---:|---|
| 90004 Circular 313 | 13.180 km | 14.536 km | **20.650 km each** | **Critical mismatch:** -36.18% / -29.61%; cannot accept 2025 legal shape from old ArcGIS |
| 90006 Circular 301 | 21.443 km | 10.346 km | Unverified | Strong direction-length asymmetry; official 2025 act changed geometry |
| 90015 Circular 315 | 8.722 km | 11.196 km | Unverified | Reciprocal endpoint pattern; legal 2025 annex comparison required |
| 90124 Castilla route 289 | 11.029 km | 12.500 km | Unverified | Official 2025 `289 Picacho` vs old ArcGIS `289 Pilarica Calle 96`; name conflict |

### Direction caution

For 313 both archived direction polylines **start at the same projected point** (0m source-point separation), with their final vertices ~235m apart. For 301, starts are within ~9m and ends ~28m. For 315 the two paths instead show a normal opposing-endpoint configuration (cross-direction endpoint gaps ~44m and ~39m). This suggests that archived `Origen-Destino` / `Destino-Origen` metadata do **not consistently specify the spatial digitization order**. Do not interpret these geometry rows as legal GTPC directions without source stops/map overlay.

For route 289 both archived polylines have almost matching starts and ends. Without an official 2025 map, the 289 code equality alone is not enough to override the conflicting legal route name.

## Circular 313: original exact PVE period brackets (limited partial advance)

The original 2025 Gaceta 5667 **Article 8 footnote** defines `PVE` *extreme valley* **before 04:30 and after 20:30**, and maximum PVE headway **15 minutes**. It also publishes day-specific full service windows.

The [source-derived PVE segment table](2025_circular313_verified_extreme_valley_windows.csv) records:
- **Weekdays / Saturday:** source-derived window intersections 04:00–04:30 and 20:30–22:00.
- **Sunday / holidays:** early service starts only at 04:45; the source-derived PVE intersection is **20:30–21:00**.

These are **source period overlaps**, not necessarily departure instants at a specific terminus. Exact treatment of the 04:30 and 20:30 boundary instants has not been specified and no GTFS frequencies were generated. **Peak (PP) versus midday valley (PVM) clock boundaries remain unpublished/unconfirmed** in the original act; never fill the rest of the day with assumed 7/8 or 12/12-minute intervals.

## Next work gate

[Issue #20](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/issues/20) now tracks official 2025 annex route geometry for Circular 313, 301/315 and Castilla 289, including spatial directions and any stop changes. Later work must obtain explicit mapped legal paths or use a properly grounded 2025 route GIS resource; comparing current ArcGIS against its *own* archived shape is not independent legal validation. Until then, the old 313 geometry must **not be approved** for current 2025/2026 GTFS.

**GTFS status:** unchanged. 2025 numeric headway source values remain research data; current legal effectivity outside bounded index screening unresolved.
