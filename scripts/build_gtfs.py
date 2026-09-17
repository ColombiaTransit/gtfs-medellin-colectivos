#!/usr/bin/env python3
"""
Build a GTFS feed for Medellin's colectivo/alimentador buses from:

  raw/rutas_alimentadoras.geojson   (LineString per route, from ArcGIS)
  raw/paradas_alimentadoras.geojson (Point per stop, from ArcGIS)
  data/operators.yml                (headways/operating hours, human-curated)

Unlike the Metro pipeline, there is no source stop_times.txt with clock
times for every trip - operators only publish headways. So this feed uses
frequencies.txt (exact_times=0) instead of literal stop_times for most of
the day. stop_times.txt still needs ONE representative trip per route
(GTFS requires at least one stop_times row per trip referenced by
frequencies.txt) with stop-to-stop relative timing; we derive that timing
from cumulative distance along the shape / an assumed average speed as a
placeholder - replace with real running times if/when available.

IMPORTANT: field names below (ROUTE_ID_FIELD, ROUTE_NAME_FIELD, etc.) are
GUESSES at common ArcGIS attribute-table conventions. Run
fetch_alimentadoras.py first, print(properties) on a sample feature, and
correct these constants before trusting the output.
"""

import csv
import json
import sys
import zipfile
from pathlib import Path

import yaml

RAW_DIR = Path("raw")
OUT_DIR = Path("gtfs-out")

# --- ADJUST THESE after inspecting raw/rutas_alimentadoras.geojson -------
ROUTE_ID_FIELD = "RUTA_ID"          # or "OBJECTID", "NOMBRE_RUT", etc.
ROUTE_NAME_FIELD = "NOMBRE"
STOP_ID_FIELD = "COD_PARADA"
STOP_NAME_FIELD = "NOMBRE"
STOP_ROUTE_FIELD = "RUTA_ID"        # field on stops linking back to a route
# ---------------------------------------------------------------------

AVERAGE_SPEED_KMH = 18  # rough urban feeder-bus speed, for placeholder timing

DAY_TYPE_SERVICE_IDS = {
    "laborable": "Laborable",
    "sabado": "Sabado",
    "domingo_festivo": "Domingo-Festivo",
}


def load_geojson(path: Path) -> dict:
    return json.loads(path.read_text())


def haversine_km(lon1, lat1, lon2, lat2):
    from math import radians, sin, cos, sqrt, atan2

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
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    routes_gj = load_geojson(RAW_DIR / "rutas_alimentadoras.geojson")
    stops_gj = load_geojson(RAW_DIR / "paradas_alimentadoras.geojson")

    operators_path = Path("data/operators.yml")
    if not operators_path.exists():
        print(
            "data/operators.yml not found.\n"
            "This file is human-curated (route schedules aren't published "
            "as structured data anywhere) and isn't generated automatically.\n"
            "  1. Run scripts/inspect_fields.py to see the real ArcGIS field "
            "names and fix ROUTE_ID_FIELD/STOP_ID_FIELD/etc. below.\n"
            "  2. Copy data/operators.yml.example -> data/operators.yml and "
            "fill in real routes (see scripts/scrape_sotrames.py for "
            "Sotrames' headways).\n"
            "See README.md for the full setup steps.",
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

    skipped = []

    for feature in routes_gj["features"]:
        props = feature["properties"]
        route_id = str(props.get(ROUTE_ID_FIELD))

        cfg = config_routes.get(route_id)
        if cfg is None:
            skipped.append(route_id)
            continue

        operator = cfg["operator"]

        route_rows.append({
            "route_id": route_id,
            "agency_id": operator,
            "route_short_name": cfg.get("route_short_name", ""),
            "route_long_name": cfg.get(
                "route_long_name", props.get(ROUTE_NAME_FIELD, "")
            ),
            "route_type": 3,  # bus
        })

        geom = feature["geometry"]
        coords = (
            geom["coordinates"]
            if geom["type"] == "LineString"
            else geom["coordinates"][0]  # first part of a MultiLineString
        )

        for seq, (lon, lat) in enumerate(coords):
            shape_rows.append({
                "shape_id": route_id,
                "shape_pt_lat": lat,
                "shape_pt_lon": lon,
                "shape_pt_sequence": seq,
            })

        length_km = line_length_km(coords)
        running_time_min = max(1, round(length_km / AVERAGE_SPEED_KMH * 60))

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

            # Minimal two-point stop_times: start and end of the route,
            # spanning the placeholder running time. frequencies.txt makes
            # this trip repeat at the configured headway.
            stop_time_rows.append({
                "trip_id": trip_id, "stop_sequence": 0,
                "arrival_time": sched["first_departure"],
                "departure_time": sched["first_departure"],
            })
            stop_time_rows.append({
                "trip_id": trip_id, "stop_sequence": 1,
                "arrival_time": _add_minutes(sched["first_departure"], running_time_min),
                "departure_time": _add_minutes(sched["first_departure"], running_time_min),
            })

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

    stop_rows = []
    for feature in stops_gj["features"]:
        props = feature["properties"]
        lon, lat = feature["geometry"]["coordinates"][:2]
        stop_rows.append({
            "stop_id": str(props.get(STOP_ID_FIELD)),
            "stop_name": props.get(STOP_NAME_FIELD, ""),
            "stop_lat": lat,
            "stop_lon": lon,
        })

    if skipped:
        print(
            f"WARNING: {len(skipped)} route(s) in the ArcGIS layer have no "
            f"entry in data/operators.yml and were skipped: "
            f"{sorted(set(skipped))[:10]}{'...' if len(skipped) > 10 else ''}"
        )

    OUT_DIR.mkdir(exist_ok=True)
    write_csv(OUT_DIR / "agency.txt", agency_rows[0].keys(), agency_rows)
    write_csv(OUT_DIR / "routes.txt", route_rows[0].keys(), route_rows)
    write_csv(OUT_DIR / "stops.txt", stop_rows[0].keys(), stop_rows)
    write_csv(OUT_DIR / "shapes.txt", shape_rows[0].keys(), shape_rows)
    write_csv(OUT_DIR / "trips.txt", trip_rows[0].keys(), trip_rows)
    write_csv(OUT_DIR / "stop_times.txt", stop_time_rows[0].keys(), stop_time_rows)
    write_csv(OUT_DIR / "frequencies.txt", freq_rows[0].keys(), freq_rows)
    write_csv(OUT_DIR / "calendar.txt", calendar_rows[0].keys(), calendar_rows)

    with (OUT_DIR / "feed_info.txt").open("w", newline="") as fh:
        fh.write("feed_publisher_name,feed_publisher_url,feed_lang\n")
        fh.write("ColombiaTransit,https://github.com/ColombiaTransit,es\n")

    zip_path = Path("gtfs-medellin-colectivos.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in OUT_DIR.glob("*.txt"):
            zf.write(f, f.name)

    print(f"Built {zip_path} with {len(route_rows)} routes, "
          f"{len(stop_rows)} stops, {len(trip_rows)} trips.")


def _add_minutes(hhmmss: str, minutes: int) -> str:
    h, m, s = (int(x) for x in hhmmss.split(":"))
    total = h * 60 + m + minutes
    return f"{total // 60:02d}:{total % 60:02d}:{s:02d}"


if __name__ == "__main__":
    main()
