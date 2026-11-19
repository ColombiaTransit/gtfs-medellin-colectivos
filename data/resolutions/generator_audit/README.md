# Verified generator route-ID inventory

This audit reads actual released or archived GTFS routes.txt and trips.txt, not just scripts or YAML route declarations.

| Generator | GTFS evidence | Routes | With trips | Without trips |
|---|---|---:|---:|---:|
| main | verified_actual_GTFS | 46 | 46 | 0 |
| elpoblado | no_accessible_GTFS | – | – | – |
| sotrames | no_accessible_GTFS | – | – | – |
| taxmaya | verified_fresh_local_GTFS_not_published_release | 11 | 11 | 0 |
| transacoop | verified_fresh_local_GTFS_not_published_release | 9 | 9 | 0 |
| trsc | verified_fresh_local_GTFS_not_published_release | 21 | 9 | 12 |

### Unavailable or expired generator outputs

- elpoblado: No accessible valid GTFS artifact from latest successful runs. []
- sotrames: No accessible valid GTFS artifact from latest successful runs. []

2026 research complete 3-daytype route IDs: **118/252**.
Confirmed exact ArcGIS IDs present with trips in inspected GTFS: **29**.
Of the 118 ready IDs, found as actual trips: **18**.
Of the 118 ready IDs, not established as actual trips: **100**.

**Caution:** Unknown or expired workflow artifacts and unmapped names are NOT evidence a route was never generated.
Download actual_gtfs_routes.csv, ready_not_in_verified_gtfs.csv and inventory.json from the workflow artifact for details.
