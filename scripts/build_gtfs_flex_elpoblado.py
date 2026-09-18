#!/usr/bin/env python3
"""
Build a GTFS-Flex feed for Autobuses El Poblado from
scripts/scrape_elpoblado.py's output.

WHY FLEX: confirmed via scrape_elpoblado.py against the real site - every
route has precise GPS geometry and (for most routes) operating-hours
text, but NO frequency/headway field anywhere in the data model, and the
"stops" field that exists in the schema is empty for every real route
(one route had 2 placeholder-looking entries, not real stops). Same
treatment as Sotrames: each route's corridor becomes a flexible
pickup/drop-off zone instead of a sequence of fixed stops.

STRUCTURE - reuses the exact pattern validated (against MobilityData's
real gtfs-validator-cli) for Sotrames' flex feed:
  - locations.geojson: one buffered polygon per route.
  - stop_times.txt: TWO location-based rows per trip (pickup-only leg +
    drop-off-only leg, both referencing the same location_id) -
    required because a single-row trip fails gtfs-validator's
    unusable_trip check. pickup_type=2 ("must phone agency") on the
    pickup leg / drop_off_type=1 on that same row (no drop-off there);
    reversed on the second row. pickup_type=2 is a spec-compliance
    choice, not a literal claim of a phone-booking system - see the
    Sotrames builder's docstring for the full reasoning (pickup_type=3,
    "coordinate with driver," is explicitly forbidden alongside
    pickup_drop_off_window fields by gtfs-validator's
    forbidden_pickup_type check).

DIFFERENCES from the Sotrames builder:
  - NO frequencies.txt at all. Sotrames has real (if zone-level, not
    per-route) headway numbers to put there; El Poblado has none -
    inventing one would be fabrication, and the fake-data pattern used
    for SAO6 (provisional: true, loud build-time warnings) was for a
    case where the person explicitly asked for placeholder numbers to
    test against. Nobody's asked for that here, so this builder simply
    omits frequencies.txt - each route's flex trip has a pickup/drop-off
    WINDOW (the route's operating hours) but no implied repeat interval.
  - calendar.txt is built per distinct day-range text actually seen in
    the schedule strings ("Lunes a viernes" / "Lunes a sábado" / "Lunes
    a domingo" variants - case-insensitive), each mapped to the
    matching weekday flags - not the fixed Laborable/Sabado/Domingo-
    Festivo split used elsewhere in this project, since El Poblado's
    source doesn't give separate weekend hours to justify that split.
  - Routes with schedule: null (confirmed 4 of 11: 135, 136, 136A, 136D)
    get a route + shape + location built, but NO trip - there's no
    operating-hours window to build one from. Not an error; matches how
    Sotrames' Circular_Sur_303 (no schedule found) is handled.

Requires: pip install shapely pyyaml (shapely for the corridor buffer,
matching the Sotrames builder).
"""

import csv
import json
import sys
import zipfile
from math import cos, radians
from pathlib import Path

ROUTES_PATH = Path("raw/elpoblado_routes.json")
OUT_DIR = Path("gtfs-flex-out-elpoblado")
ZIP_PATH = Path("gtfs-flex-elpoblado.zip")

CORRIDOR_BUFFER_M = 40  # ASSUMED half-width of the flag-down catchment zone - same as Sotrames

AGENCY_ID = "elpoblado"

FIELDNAMES = {
    "agency.txt": ["agency_id", "agency_name", "agency_url", "agency_timezone", "agency_lang"],
    "routes.txt": ["route_id", "agency_id", "route_short_name", "route_long_name", "route_type"],
    "stops.txt": ["stop_id", "stop_name", "stop_lat", "stop_lon"],
    "trips.txt": ["route_id", "service_id", "trip_id"],
    "stop_times.txt": ["trip_id", "stop_sequence", "location_id",
                        "start_pickup_drop_off_window", "end_pickup_drop_off_window",
                        "pickup_type", "drop_off_type"],
    "calendar.txt": ["service_id", "monday", "tuesday", "wednesday", "thursday",
                      "friday", "saturday", "sunday", "start_date", "end_date"],
}

# days_text (lowercased) -> weekday flags. Extend if a new pattern shows
# up in the source data - scrape_elpoblado.py's parse_schedule() leaves
# days_text=None for anything not matching its two known formats, and
# such routes are treated the same as schedule=null (no trip built).
DAY_RANGE_TO_FLAGS = {
    "lunes a viernes": {"monday": 1, "tuesday": 1, "wednesday": 1, "thursday": 1,
                         "friday": 1, "saturday": 0, "sunday": 0},
    "lunes a sábado": {"monday": 1, "tuesday": 1, "wednesday": 1, "thursday": 1,
                        "friday": 1, "saturday": 1, "sunday": 0},
    "lunes a sabado": {"monday": 1, "tuesday": 1, "wednesday": 1, "thursday": 1,
                        "friday": 1, "saturday": 1, "sunday": 0},
    "lunes a domingo": {"monday": 1, "tuesday": 1, "wednesday": 1, "thursday": 1,
                         "friday": 1, "saturday": 1, "sunday": 1},
}


def write_csv(path: Path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _to_local_xy(lon, lat, lat0):
    meters_per_deg_lat = 111_320.0
    meters_per_deg_lon = 111_320.0 * cos(radians(lat0))
    return lon * meters_per_deg_lon, lat * meters_per_deg_lat


def _to_lon_lat(x, y, lat0):
    meters_per_deg_lat = 111_320.0
    meters_per_deg_lon = 111_320.0 * cos(radians(lat0))
    return x / meters_per_deg_lon, y / meters_per_deg_lat


def buffer_line_to_polygon(coords, buffer_m):
    from shapely.geometry import LineString

    lat0 = sum(lat for _, lat in coords) / len(coords)
    local_coords = [_to_local_xy(lon, lat, lat0) for lon, lat in coords]
    line = LineString(local_coords)
    poly = line.buffer(buffer_m, cap_style="round", join_style="round")
    return [_to_lon_lat(x, y, lat0) for x, y in poly.exterior.coords]


def service_id_for(days_text: str) -> str:
    # Lowercased first: "Lunes a sábado" and "Lunes a Sábado" (both seen
    # in real data, differing only in capitalization) must map to the
    # SAME service_id, not two functionally-identical calendar rows.
    # e.g. "Lunes a sábado" -> "lunes_a_sabado"
    text = days_text.strip().lower()
    return (
        text.replace(" ", "_")
        .replace("á", "a").replace("é", "e").replace("í", "i")
        .replace("ó", "o").replace("ú", "u")
    )


def main():
    if not ROUTES_PATH.exists():
        print(f"{ROUTES_PATH} not found - run scripts/scrape_elpoblado.py first.",
              file=sys.stderr)
        sys.exit(1)

    routes = json.loads(ROUTES_PATH.read_text())

    agency_rows = [{
        "agency_id": AGENCY_ID, "agency_name": "Autobuses El Poblado",
        "agency_url": "https://www.autopobla.com.co", "agency_timezone": "America/Bogota",
        "agency_lang": "es",
    }]

    route_rows, location_features = [], []
    trip_rows, stop_time_rows = [], []
    calendars = {}  # service_id -> row dict
    skipped_no_geometry, skipped_no_schedule, skipped_bad_days_text = [], [], []

    for route in routes:
        route_id = route["code"]
        coords = route.get("geometry") or []
        if len(coords) < 2:
            skipped_no_geometry.append(route_id)
            continue

        route_rows.append({
            "route_id": route_id,
            "agency_id": AGENCY_ID,
            "route_short_name": route_id,
            "route_long_name": route.get("name") or f"Ruta {route_id}",
            "route_type": 3,  # bus
        })

        polygon_coords = buffer_line_to_polygon(coords, CORRIDOR_BUFFER_M)
        location_features.append({
            "type": "Feature",
            "id": route_id,
            "properties": {"name": route.get("name")},
            "geometry": {"type": "Polygon", "coordinates": [
                [[round(lon, 6), round(lat, 6)] for lon, lat in polygon_coords]
            ]},
        })

        sched = route.get("schedule_parsed") or {}
        start, end, days_text = sched.get("start_24h"), sched.get("end_24h"), sched.get("days_text")

        if not route.get("schedule"):
            skipped_no_schedule.append(route_id)
            continue
        if not (start and end and days_text):
            skipped_bad_days_text.append(route_id)
            continue

        flags_key = days_text.strip().lower()
        flags = DAY_RANGE_TO_FLAGS.get(flags_key)
        if flags is None:
            skipped_bad_days_text.append(route_id)
            continue

        service_id = service_id_for(days_text)
        if service_id not in calendars:
            calendars[service_id] = {
                "service_id": service_id, **flags,
                "start_date": "20260101", "end_date": "20271231",
            }

        trip_id = f"{route_id}_{service_id}"
        trip_rows.append({"route_id": route_id, "service_id": service_id, "trip_id": trip_id})

        stop_time_rows.append({
            "trip_id": trip_id, "stop_sequence": 0, "location_id": route_id,
            "start_pickup_drop_off_window": start, "end_pickup_drop_off_window": end,
            "pickup_type": 2, "drop_off_type": 1,
        })
        stop_time_rows.append({
            "trip_id": trip_id, "stop_sequence": 1, "location_id": route_id,
            "start_pickup_drop_off_window": start, "end_pickup_drop_off_window": end,
            "pickup_type": 1, "drop_off_type": 2,
        })

    if skipped_no_geometry:
        print(f"WARNING: {len(skipped_no_geometry)} route(s) had no usable geometry: "
              f"{skipped_no_geometry}", file=sys.stderr)
    if skipped_no_schedule:
        print(f"NOTE: {len(skipped_no_schedule)} route(s) built with geometry only, "
              f"no trip (schedule is null in the source): {skipped_no_schedule}")
    if skipped_bad_days_text:
        print(f"NOTE: {len(skipped_bad_days_text)} route(s) had a schedule string that "
              f"didn't match a known day-range pattern - built with geometry only, no "
              f"trip: {skipped_bad_days_text}. Check their raw schedule text in "
              f"{ROUTES_PATH} and extend DAY_RANGE_TO_FLAGS if it's a new real format.")

    OUT_DIR.mkdir(exist_ok=True)
    write_csv(OUT_DIR / "agency.txt", FIELDNAMES["agency.txt"], agency_rows)
    write_csv(OUT_DIR / "routes.txt", FIELDNAMES["routes.txt"], route_rows)
    write_csv(OUT_DIR / "stops.txt", FIELDNAMES["stops.txt"], [])
    write_csv(OUT_DIR / "trips.txt", FIELDNAMES["trips.txt"], trip_rows)
    write_csv(OUT_DIR / "stop_times.txt", FIELDNAMES["stop_times.txt"], stop_time_rows)
    write_csv(OUT_DIR / "calendar.txt", FIELDNAMES["calendar.txt"], list(calendars.values()))

    (OUT_DIR / "locations.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": location_features}, ensure_ascii=False)
    )

    with (OUT_DIR / "feed_info.txt").open("w", newline="") as fh:
        fh.write("feed_publisher_name,feed_publisher_url,feed_lang\n")
        fh.write("ColombiaTransit,https://github.com/ColombiaTransit,es\n")

    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in OUT_DIR.glob("*"):
            if f.suffix in (".txt", ".geojson"):
                zf.write(f, f.name)

    print(f"\nBuilt {ZIP_PATH}: {len(route_rows)} routes, {len(trip_rows)} trips, "
          f"{len(calendars)} distinct service pattern(s): {list(calendars.keys())}")
    print("No frequencies.txt - no headway data exists for this operator (unlike "
          "Sotrames). Each trip has an operating-hours WINDOW only, no repeat interval.")


if __name__ == "__main__":
    main()
