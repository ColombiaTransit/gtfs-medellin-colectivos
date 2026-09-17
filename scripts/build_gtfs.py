#!/usr/bin/env python3
"""
Build a GTFS feed for Medellin's colectivo/alimentador buses from:

  raw/rutas_alimentadoras.geojson   (LineString per route, from ArcGIS)
  raw/paradas_alimentadoras.geojson (Point per stop, from ArcGIS)
  data/operators.yml                (headways/operating hours, human-curated)

Unlike the Metro pipeline, there is no source stop_times.txt with clock
times for every trip - operators only publish headways. So this feed uses
frequencies.txt (exact_times=0) for the actual service frequency, but
stop_times.txt still has to list every stop a trip visits (GTFS requires
it), with a per-stop arrival/departure time for ONE representative trip.
We derive those times by spacing stops evenly across a placeholder total
running time (route length / an assumed average speed) - replace with real
timings if/when available.

Confirmed field names (from scripts/inspect_fields.py output against the
live layers on 2026-09-17):

  Routes (rutas_alimentadoras.geojson):
    ruta        - directional itinerary/shape id, e.g. "C3-004P" (join key)
    linea       - human route name, both directions, e.g.
                  "C3-004P La Perla - Altavista - Belén"
    itinerario  - human name for THIS direction only
    cuenca      - basin ("3" or "6") - roughly maps to operator/zone
    SHAPE__Length - precomputed length in meters

  Stops (paradas_alimentadoras.geojson):
    ruta        - same itinerary id, links a stop back to its route
    globalid    - unique id (safe to use as stop_id)
    parada/label - stop name (identical in both fields)
    objectid    - used here as a best-effort proxy for stop ORDER along
                  the route, since ArcGIS doesn't expose an explicit
                  sequence field. This is an assumption - if actual stop
                  order looks wrong in the validator's map view, this is
                  the first thing to revisit.
"""

import csv
import json
import sys
import zipfile
from math import atan2, cos, radians, sin, sqrt
from pathlib import Path

import yaml

RAW_DIR = Path("raw")
OUT_DIR = Path("gtfs-out")

ROUTE_ID_FIELD = "ruta"
ROUTE_NAME_FIELD = "linea"
ROUTE_LENGTH_FIELD = "SHAPE__Length"  # meters, already computed by ArcGIS

STOP_ID_FIELD = "globalid"
STOP_NAME_FIELD = "parada"
STOP_ROUTE_FIELD = "ruta"
STOP_ORDER_FIELD = "objectid"  # best-effort; see module docstring

AVERAGE_SPEED_KMH = 18  # rough urban feeder-bus speed, for placeholder timing

DAY_TYPE_SERVICE_IDS = {
    "laborable": "Laborable",
    "sabado": "Sabado",
    "domingo_festivo": "Domingo-Festivo",
}

# Explicit GTFS column order per file - not inferred from row 0, since
# routes with an empty day_types (no trips yet) legitimately produce zero
# rows for stops/shapes/trips/stop_times/frequencies.
FIELDNAMES = {
    "agency.txt": ["agency_id", "agency_name", "agency_url", "agency_timezone", "agency_lang"],
    "routes.txt": ["route_id", "agency_id", "route_short_name", "route_long_name", "route_type"],
    "stops.txt": ["stop_id", "stop_name", "stop_lat", "stop_lon"],
    "shapes.txt": ["shape_id", "shape_pt_lat", "shape_pt_lon", "shape_pt_sequence"],
    "trips.txt": ["route_id", "service_id", "trip_id", "shape_id", "direction_id"],
    "stop_times.txt": ["trip_id", "stop_id", "stop_sequence", "arrival_time", "departure_time"],
    "frequencies.txt": ["trip_id", "start_time", "end_time", "headway_secs", "exact_times"],
    "calendar.txt": ["service_id", "monday", "tuesday", "wednesday", "thursday",
                      "friday", "saturday", "sunday", "start_date", "end_date"],
}


def load_geojson(path: Path) -> dict:
    return json.loads(path.read_text())


def haversine_km(lon1, lat1, lon2, lat2):
    r = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * r * atan2(sqrt(a), sqrt(1 - a))


def line_length_km(coords):
    total = 0.0
    for (lon1, lat1), (lon2, lat2) in zip(coords, coords[1:]):
        total += haversine_km(lon1, lat1, lon2, lat2)
    return total


def write_csv(path: Path, fieldnames, rows):
    """fieldnames is always an explicit list now (not inferred from
    rows[0]) - with placeholder routes that have empty day_types (no
    trips), several of these lists can legitimately be empty, and
    inferring fieldnames from a nonexistent rows[0] used to crash."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _add_minutes(hhmmss: str, minutes: float) -> str:
    h, m, s = (int(x) for x in hhmmss.split(":"))
    total = h * 60 + m + minutes
    total_int = int(round(total))
    return f"{total_int // 60:02d}:{total_int % 60:02d}:{s:02d}"


def main():
    routes_gj = load_geojson(RAW_DIR / "rutas_alimentadoras.geojson")
    stops_gj = load_geojson(RAW_DIR / "paradas_alimentadoras.geojson")

    operators_path = Path("data/operators.yml")
    if not operators_path.exists():
        print(
            "data/operators.yml not found.\n"
            "This file is human-curated (schedules aren't published as "
            "structured data anywhere) and isn't generated automatically.\n"
            "Copy data/operators.yml.example -> data/operators.yml and fill "
            "in real routes (see scripts/scrape_sotrames.py for Sotrames' "
            "headways). See README.md for the full setup steps.",
            file=sys.stderr,
        )
        sys.exit(1)

    config = yaml.safe_load(operators_path.read_text())

    if any(r["route_id"] == "REPLACE_ME" for r in config.get("routes", [])):
        print(
            "data/operators.yml still contains the REPLACE_ME placeholder "
            "route. Fill in real route_ids before running this in CI.",
            file=sys.stderr,
        )
        sys.exit(1)

    config_routes = {r["route_id"]: r for r in config["routes"]}
    operators = config["operators"]

    # --- group stops by route (ruta), ordered by objectid -----------------
    stops_by_route = {}
    all_stops_by_id = {}
    for feature in stops_gj["features"]:
        props = feature["properties"]
        route_key = str(props.get(STOP_ROUTE_FIELD))
        stop_id = str(props.get(STOP_ID_FIELD))
        lon, lat = feature["geometry"]["coordinates"][:2]

        stop_record = {
            "stop_id": stop_id,
            "stop_name": props.get(STOP_NAME_FIELD, ""),
            "stop_lat": lat,
            "stop_lon": lon,
            "_order": props.get(STOP_ORDER_FIELD, 0),
        }
        stops_by_route.setdefault(route_key, []).append(stop_record)
        all_stops_by_id[stop_id] = stop_record

    for route_key, stop_list in stops_by_route.items():
        stop_list.sort(key=lambda s: s["_order"])

    # --- agency.txt ---------------------------------------------------------
    agency_rows = [
        {
            "agency_id": key,
            "agency_name": op["agency_name"],
            "agency_url": op["agency_url"],
            "agency_timezone": "America/Bogota",
            "agency_lang": "es",
        }
        for key, op in operators.items()
    ]

    route_rows, shape_rows, trip_rows, stop_time_rows, freq_rows = [], [], [], [], []
    used_stop_ids = set()

    calendar_rows = [
        {
            "service_id": "Laborable",
            "monday": 1, "tuesday": 1, "wednesday": 1, "thursday": 1,
            "friday": 1, "saturday": 0, "sunday": 0,
            "start_date": "20260101", "end_date": "20271231",
        },
        {
            "service_id": "Sabado",
            "monday": 0, "tuesday": 0, "wednesday": 0, "thursday": 0,
            "friday": 0, "saturday": 1, "sunday": 0,
            "start_date": "20260101", "end_date": "20271231",
        },
        {
            "service_id": "Domingo-Festivo",
            "monday": 0, "tuesday": 0, "wednesday": 0, "thursday": 0,
            "friday": 0, "saturday": 0, "sunday": 1,
            "start_date": "20260101", "end_date": "20271231",
        },
    ]

    skipped_no_config = []
    skipped_no_stops = []

    # --- group route features by ruta, since ~most routes have MORE THAN
    # ONE feature row (confirmed via inspect_fields.py: 102 rows / 46
    # distinct 'ruta' values). Processing rows independently used to
    # silently produce duplicate route_id rows and colliding
    # shape_pt_sequence numbers for every such route - fixed by grouping
    # first. Within a ruta, rows can differ by 'sentido' (a real
    # direction pair) or share the same 'sentido' (split line segments of
    # one direction, meant to be concatenated). Since this feed models
    # one shape per route_id (direction_id is always 0 - seven "two
    # directions" is not modeled as separate GTFS directions yet), we
    # pick ONE sentido group per ruta (the smallest sentido value seen,
    # for determinism) and concatenate its segments in objectid order.
    features_by_route = {}
    for feature in routes_gj["features"]:
        route_id = str(feature["properties"].get(ROUTE_ID_FIELD))
        features_by_route.setdefault(route_id, []).append(feature)

    for route_id, route_features in features_by_route.items():
        cfg = config_routes.get(route_id)
        if cfg is None:
            skipped_no_config.append(route_id)
            continue

        route_stops = stops_by_route.get(route_id, [])
        if len(route_stops) < 2:
            skipped_no_stops.append(route_id)
            continue

        # Pick one sentido group; concatenate its segments in objectid order.
        by_sentido = {}
        for f in route_features:
            by_sentido.setdefault(f["properties"].get("sentido"), []).append(f)
        chosen_sentido = sorted(by_sentido.keys(), key=lambda s: (s is None, s))[0]
        segments = sorted(
            by_sentido[chosen_sentido],
            key=lambda f: f["properties"].get("objectid", 0),
        )

        props = segments[0]["properties"]  # for route-level metadata (linea, etc.)

        coords = []
        for seg in segments:
            geom = seg["geometry"]
            seg_coords = (
                geom["coordinates"]
                if geom["type"] == "LineString"
                else geom["coordinates"][0]  # first part of a MultiLineString
            )
            coords.extend(seg_coords)

        operator = cfg["operator"]

        route_rows.append({
            "route_id": route_id,
            "agency_id": operator,
            "route_short_name": cfg.get("route_short_name", route_id),
            "route_long_name": cfg.get(
                "route_long_name", props.get(ROUTE_NAME_FIELD, "")
            ),
            "route_type": 3,  # bus
        })

        for seq, (lon, lat) in enumerate(coords):
            shape_rows.append({
                "shape_id": route_id,
                "shape_pt_lat": lat,
                "shape_pt_lon": lon,
                "shape_pt_sequence": seq,
            })

        # Sum SHAPE__Length across the chosen sentido's segments if every
        # segment has it; otherwise recompute from the concatenated coords.
        seg_lengths = [s["properties"].get(ROUTE_LENGTH_FIELD) for s in segments]
        if all(seg_lengths):
            length_km = sum(seg_lengths) / 1000
        else:
            length_km = line_length_km(coords)
        running_time_min = max(1, round(length_km / AVERAGE_SPEED_KMH * 60))

        n_stops = len(route_stops)
        for day_type, sched in cfg["day_types"].items():
            service_id = DAY_TYPE_SERVICE_IDS.get(day_type, day_type)
            trip_id = f"{route_id}_{service_id}"

            trip_rows.append({
                "route_id": route_id,
                "service_id": service_id,
                "trip_id": trip_id,
                "shape_id": route_id,
                "direction_id": 0,
            })

            # Space stops evenly across the placeholder running time.
            # Real per-segment timings would replace this if ever available.
            for i, stop in enumerate(route_stops):
                offset_min = running_time_min * i / (n_stops - 1)
                t = _add_minutes(sched["first_departure"], offset_min)
                stop_time_rows.append({
                    "trip_id": trip_id,
                    "stop_id": stop["stop_id"],
                    "stop_sequence": i,
                    "arrival_time": t,
                    "departure_time": t,
                })
                used_stop_ids.add(stop["stop_id"])

            windows = sched.get("peak_windows") or []
            if not windows:
                freq_rows.append({
                    "trip_id": trip_id,
                    "start_time": sched["first_departure"],
                    "end_time": sched["last_departure"],
                    "headway_secs": int(sched["offpeak_headway_min"] * 60),
                    "exact_times": 0,
                })
            else:
                bounds = sorted(windows, key=lambda w: w[0])
                cursor = sched["first_departure"]
                for start, end in bounds:
                    if cursor < start:
                        freq_rows.append({
                            "trip_id": trip_id, "start_time": cursor, "end_time": start,
                            "headway_secs": int(sched["offpeak_headway_min"] * 60),
                            "exact_times": 0,
                        })
                    freq_rows.append({
                        "trip_id": trip_id, "start_time": start, "end_time": end,
                        "headway_secs": int(sched["peak_headway_min"] * 60),
                        "exact_times": 0,
                    })
                    cursor = end
                if cursor < sched["last_departure"]:
                    freq_rows.append({
                        "trip_id": trip_id, "start_time": cursor,
                        "end_time": sched["last_departure"],
                        "headway_secs": int(sched["offpeak_headway_min"] * 60),
                        "exact_times": 0,
                    })

    # Only emit stops actually referenced by a built trip.
    stop_rows = [
        {k: v for k, v in s.items() if not k.startswith("_")}
        for sid, s in all_stops_by_id.items()
        if sid in used_stop_ids
    ]

    if skipped_no_config:
        print(
            f"NOTE: {len(skipped_no_config)} route(s) in the ArcGIS layer have "
            f"no entry in data/operators.yml and were skipped: "
            f"{sorted(set(skipped_no_config))[:10]}"
            f"{'...' if len(skipped_no_config) > 10 else ''}"
        )
    if skipped_no_stops:
        print(
            f"WARNING: {len(skipped_no_stops)} configured route(s) have fewer "
            f"than 2 matching stops in the stops layer and were skipped "
            f"(check the 'ruta' join key matches): {sorted(set(skipped_no_stops))}"
        )

    if not route_rows:
        print("No routes were built - nothing in data/operators.yml matched "
              "the ArcGIS routes layer. Check that route_id values match the "
              "'ruta' field exactly (case-sensitive).", file=sys.stderr)
        sys.exit(1)

    routes_with_no_trips = sorted(
        {r["route_id"] for r in route_rows}
        - {t["route_id"] for t in trip_rows}
    )
    if routes_with_no_trips:
        print(
            f"NOTE: {len(routes_with_no_trips)} route(s) were built with no "
            f"trips (empty day_types in data/operators.yml - expected for "
            f"placeholder routes waiting on real schedule data): "
            f"{routes_with_no_trips}"
        )

    OUT_DIR.mkdir(exist_ok=True)
    write_csv(OUT_DIR / "agency.txt", FIELDNAMES["agency.txt"], agency_rows)
    write_csv(OUT_DIR / "routes.txt", FIELDNAMES["routes.txt"], route_rows)
    write_csv(OUT_DIR / "stops.txt", FIELDNAMES["stops.txt"], stop_rows)
    write_csv(OUT_DIR / "shapes.txt", FIELDNAMES["shapes.txt"], shape_rows)
    write_csv(OUT_DIR / "trips.txt", FIELDNAMES["trips.txt"], trip_rows)
    write_csv(OUT_DIR / "stop_times.txt", FIELDNAMES["stop_times.txt"], stop_time_rows)
    write_csv(OUT_DIR / "frequencies.txt", FIELDNAMES["frequencies.txt"], freq_rows)
    write_csv(OUT_DIR / "calendar.txt", FIELDNAMES["calendar.txt"], calendar_rows)

    with (OUT_DIR / "feed_info.txt").open("w", newline="") as fh:
        fh.write("feed_publisher_name,feed_publisher_url,feed_lang\n")
        fh.write("ColombiaTransit,https://github.com/ColombiaTransit,es\n")

    zip_path = Path("gtfs-medellin-colectivos.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in OUT_DIR.glob("*.txt"):
            zf.write(f, f.name)

    print(f"Built {zip_path} with {len(route_rows)} routes, "
          f"{len(stop_rows)} stops, {len(trip_rows)} trips.")


if __name__ == "__main__":
    main()
