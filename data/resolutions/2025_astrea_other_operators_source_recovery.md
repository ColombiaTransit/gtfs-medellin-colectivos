# Official 2025 urban bus restructurings: source recovery and scope audit (18 November 2026)

## Direct official original texts verified through GitHub Actions

The previous secondary Gaceta contents references for the following five acts have been replaced in `priority_source_documents.csv` by confirmed, publicly readable official ASTREA originals. The GitHub runner has verified HTTP 200 and each full resolution number in the document body.

| Official act | Gazette | Operator / route system | Official ASTREA original |
|---|---|---|---|
| 202550076150 (2025-09-19) | 5671, p3 | Coinvetrans / Invetrans, Salud-Hotelera | https://www.medellin.gov.co/normograma/docs/astrea/docs/r_smmed_76150_2025.htm |
| 202550076162 (2025-09-19) | 5671, p14 | Transportes Medellín Castilla / Conaltracoop, 2A/2B | https://www.medellin.gov.co/normograma/docs/astrea/docs/r_smmed_76162_2025.htm |
| 202550076174 (2025-09-19) | 5667, p59 | Coonatra Circular 301 and Santra Circular 315, route geometry | https://www.medellin.gov.co/normograma/docs/astrea/docs/r_smmed_76174_2025.htm |
| 202550079848 (2025-09-26) | 5671, p29 | Metrosan integrated feeders | https://www.medellin.gov.co/normograma/docs/astrea/docs/r_smmed_79848_2025.htm |
| 202550079865 (2025-09-26) | 5671, p42 | Rápido San Cristóbal, urban/integrated/corregimental routes | https://www.medellin.gov.co/normograma/docs/astrea/docs/r_smmed_79865_2025.htm |

**Not recovered:** 202550076168/2025 (Combuses, Circular 313) did not exist at the two tested ASTREA name variants (HTTP 404); this is not evidence that the act does not exist. The Gaceta 5667/5671 public detail URL pattern likewise returned 404 for those historic numbers. Do not synthesize a PDF URL or presume an act's detailed scope.

## Structured tables discovered in official originals

The source-only normalization counts **86 distinct (resolution, GTPC, user route-code) records** in four source acts:
- Salud-Hotelera: **6** route-code entries. Route 304 and 305 share a GTPC code but are separate user route codes.
- Medellín Castilla / Conaltracoop: **30** route/GTPC entries, including ten trunk-corridor entries without ordinary numeric interval tables.
- Metrosan: **16** direction-level entries, corresponding to pairs within the integrated route families. Numeric service figures in the first direction row must not simply be doubled for the blank return-direction row.
- Rápido San Cristóbal: **34** route/GTPC entries, including corregimental routes with specific departures rather than a periodic headway. A printed zero-minute interval is **not** a GTFS frequency value.

The original acts print separate **service-hour** and **maximum dispatch interval** tables by day type; the trip-period headings and source anomalies need an additional dedicated QA pass before production interpretation. The technical data extractor intentionally preserves raw strings (including blanks, `No opera`, `N/A`, zeros and fixed departure lists). These are *published maximum intervals*, not observed intervals, and do not establish peak clock-time boundaries on their own.

The Coonatra/Santra act **202550076174** concerns the route paths of 301 and 315. Its context table with other operators and `Frecuencias DTL` does **not** grant revised timetables to all those operators.

### Research evidence and next control

- [Run #44267814489](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44267814489): official URL verification.
- [Run #44268129743](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44268129743): candidate table and article extraction.
- `2025_astrea_official_route_timetable_candidates.csv`: source-level normalized route/timetable candidates, **not automatically approved GTFS data**. Key by resolution + GTPC + user-code, not GTPC alone.

**Generator policy:** do not change any current routes, agency mapping, trips, shapes, frequency period boundaries, or GTFS production data based solely on these extracted 2025 table candidates. Review later legal amendments, source anomalies and ArcGIS alignment by operator before promoting any values.

**2026-11-18 extraction correction:** expanded GTPC row recognition recovered `TRONCAL-5` and `TRONCAL-6` in Castilla's original act. Validated in workflow [#44273498768](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44273498768); source total is 86. Earlier 84-record counts are superseded.
