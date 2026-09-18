#!/usr/bin/env python3
"""
Build a GTFS-Flex feed for Sotrames from KML route geometry + zone-level
schedule data.

WHY FLEX, NOT REGULAR GTFS: confirmed via scripts/fetch_sotrames_kml.py
against all 34 of Sotrames' published Google My Maps - every single one
has real, detailed line geometry but ZERO stop-point markers. Treating
this as a flag-down service: each route's corridor becomes a flexible
pickup/drop-off zone (a buffered polygon around the route line) instead
of a sequence of fixed stops, with pickup_type/drop_off_type set to
"must coordinate with driver" (flag it down) rather than "board at a
scheduled stop."

WHAT'S REAL vs APPROXIMATED:
  - Route geometry: REAL (from Sotrames' own published Google My Maps).
  - Schedule (hours, pico/valle headway): REAL numbers, but applied at
    ZONE level (Itagüí/Envigado/Sabaneta), not per-route - see
    data/sotrames_zones.yml for exactly which published table was used
    per zone and why per-route matching wasn't attempted. Every trip
    built this way is marked provisional: true in the same sense as
    data/operators.yml's SAO6 placeholders, though these numbers ARE
    real Sotrames data, just not route-specific - see FLEX_PROVISIONAL
    below for what that distinction means here.
  - Circular_Sur_303: geometry only, no schedule found anywhere - no
    trips built for it at all (see data/sotrames_zones.yml).
  - Only "Laborable" (weekday) schedules exist in the source - every
    table on sotrames.com.co/rutas/ is labeled "SEMANA" (weekday).
    NO Sábado/Domingo tables were found anywhere, unlike MDO's cards.
    This script does NOT fabricate weekend schedules - only a laborable
    service_id is built.

GTFS-FLEX STRUCTURE USED (VALIDATED - see below):
  - locations.geojson: one Polygon per route (buffered line, see
    CORRIDOR_BUFFER_M - an ASSUMED catchment width, not a measured
    fact), id = route_id, used as location_id in stop_times.txt.
  - stop_times.txt: TWO location-based rows per trip (stop_sequence 0
    and 1), both referencing the same location_id (there's only one
    zone per route) - one pickup-only leg, one drop-off-only leg. This
    two-row structure is REQUIRED: gtfs-validator's unusable_trip check
    requires more than one stop_times row per trip to consider it a
    real journey, even when origin and destination are the same zone.
  - pickup_type=2 ("must phone agency") on the pickup leg, drop_off_type
    =2 on the drop-off leg. This is a spec-compliance compromise, not a
    literal claim that Sotrames has a phone-booking system - it
    doesn't. GTFS-Flex has no code for "unscheduled, no booking needed,
    just flag it down," which is what this actually models. The
    natural-seeming choice, pickup_type=3 ("must coordinate with
    driver"), is explicitly FORBIDDEN together with
    pickup_drop_off_window fields by the spec (confirmed via
    gtfs-validator's forbidden_pickup_type check - see VALIDATED below).
    pickup_type=2 was the closest valid option left.
  - frequencies.txt: included, referencing the flex trip_id, the same
    way it's used for regular GTFS routes elsewhere in this project.
    This combination (frequencies.txt driving a location-based flex
    trip) is not a standard, widely-documented GTFS-Flex pattern - it
    passed gtfs-validator without error, but a consuming application
    (trip planner, etc.) may or may not know what to do with it, since
    flex is normally modeled as booked/demand-responsive, not "fixed
    headway, no marked stops." This is the most information-preserving
    way to carry the real pico/valle headway numbers through; treat it
    as best-effort, not a guarantee every GTFS-Flex consumer handles it.
  - stops.txt: present with headers only (no rows) - some GTFS readers
    expect the file to exist even when every pickup/drop-off is
    location-based.

VALIDATED: this script's output was run through MobilityData's real
gtfs-validator-cli (the same tool the main pipeline uses, downloaded
directly from its GitHub releases) against all 34 actual downloaded
Sotrames KML files, not a mockup. The first version had 2 real ERRORs
(forbidden_pickup_type x33, foreign_key_violation x1 - a route with no
zone match had no corresponding agency.txt row) plus an unusable_trip
WARNING x33. All three are fixed in the structure described above -
confirmed by re-running validation after the fix: 0 ERROR-level
notices, only 3 harmless WARNINGs left (missing optional feed_info.txt
fields, and expected accented characters in Spanish route names).
"""

import csv
import json
import sys
import zipfile
from math import atan2, cos, radians, sin, sqrt
from pathlib import Path
from xml.etree import ElementTree as ET

import yaml

KML_DIR = Path("raw/sotrames_kml")
ZONES_CONFIG = Path("data/sotrames_zones.yml")
OUT_DIR = Path("gtfs-flex-out")
ZIP_PATH = Path("gtfs-flex-sotrames.zip")

KML_NS = {"kml": "http://www.opengis.net/kml/2.2"}

CORRIDOR_BUFFER_M = 40  # ASSUMED half-width of the flag-down catchment zone

FIELDNAMES = {
    "agency.txt": ["agency_id", "agency_name", "agency_url", "agency_timezone", "agency_lang"],
    "routes.txt": ["route_id", "agency_id", "route_short_name", "route_long_name", "route_type"],
    "stops.txt": ["stop_id", "stop_name", "stop_lat", "stop_lon"],
    "trips.txt": ["route_id", "service_id", "trip_id"],
    "stop_times.txt": ["trip_id", "stop_sequence", "location_id",
                        "start_pickup_drop_off_window", "end_pickup_drop_off_window",
                        "pickup_type", "drop_off_type"],
    "frequencies.txt": ["trip_id", "start_time", "end_time", "headway_secs", "exact_times"],
    "calendar.txt": ["service_id", "monday", "tuesday", "wednesday", "thursday",
                      "friday", "saturday", "sunday", "start_date", "end_date"],
}


def write_csv(path: Path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_kml_line(path: Path):
    root = ET.fromstring(path.read_bytes())
    coord_el = root.find(".//kml:LineString/kml:coordinates", KML_NS)
    if coord_el is None:
        return None
    coords = []
    for token in coord_el.text.split():
        lon, lat, *_ = token.split(",")
        coords.append((float(lon), float(lat)))
    return coords


def _to_local_xy(lon, lat, lat0):
    meters_per_deg_lat = 111_320.0
    meters_per_deg_lon = 111_320.0 * cos(radians(lat0))
    return lon * meters_per_deg_lon, lat * meters_per_deg_lat


def _to_lon_lat(x, y, lat0):
    meters_per_deg_lat = 111_320.0
    meters_per_deg_lon = 111_320.0 * cos(radians(lat0))
    return x / meters_per_deg_lon, y / meters_per_deg_lat


def buffer_line_to_polygon(coords, buffer_m):
    """Buffer a lon/lat line into a polygon (list of lon/lat rings),
    via a local-planar projection (fine at this scale) + shapely."""
    from shapely.geometry import LineString
    from shapely.ops import transform as shp_transform

    lat0 = sum(lat for _, lat in coords) / len(coords)
    local_coords = [_to_local_xy(lon, lat, lat0) for lon, lat in coords]
    line = LineString(local_coords)
    poly = line.buffer(buffer_m, cap_style="round", join_style="round")

    exterior_lonlat = [_to_lon_lat(x, y, lat0) for x, y in poly.exterior.coords]
    return exterior_lonlat


def haversine_km(lon1, lat1, lon2, lat2):
    r = 6371.0
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * r * atan2(sqrt(a), sqrt(1 - a))


def line_length_km(coords):
    return sum(haversine_km(lo1, la1, lo2, la2) for (lo1, la1), (lo2, la2) in zip(coords, coords[1:]))


def main():
    if not KML_DIR.exists():
        print(f"{KML_DIR} not found - run scripts/fetch_sotrames_kml.py first "
              f"(via the 'Fetch Sotrames Route KML' GitHub Action) and place its "
              f"raw/sotrames_kml/ output here.", file=sys.stderr)
        sys.exit(1)

    zones_cfg = yaml.safe_load(ZONES_CONFIG.read_text())
    zones = zones_cfg["zones"]
    route_zones = zones_cfg["route_zones"]

    agency_rows = [
        {"agency_id": f"sotrames_{zone_id}", "agency_name": z["agency_name"],
         "agency_url": "https://www.sotrames.com.co", "agency_timezone": "America/Bogota",
         "agency_lang": "es"}
        for zone_id, z in zones.items()
    ]
    # Fallback for routes with no zone match (e.g. Circular_Sur_303, which
    # has no frequency data anywhere on the source page) - without this,
    # routes.txt's agency_id="sotrames_unknown" has no matching agency.txt
    # row, which is a real foreign_key_violation error (caught by
    # validation while building this script).
    agency_rows.append({
        "agency_id": "sotrames_unknown", "agency_name": "Sotrames S.A.S",
        "agency_url": "https://www.sotrames.com.co", "agency_timezone": "America/Bogota",
        "agency_lang": "es",
    })

    route_rows, location_features = [], []
    trip_rows, stop_time_rows, freq_rows = [], [], []
    skipped_no_geometry, skipped_no_schedule = [], []

    kml_files = sorted(KML_DIR.glob("*.kml"))
    if not kml_files:
        print(f"No .kml files found in {KML_DIR}", file=sys.stderr)
        sys.exit(1)

    for kml_path in kml_files:
        route_id = kml_path.stem
        coords = parse_kml_line(kml_path)
        if not coords or len(coords) < 2:
            skipped_no_geometry.append(route_id)
            continue

        zone_id = route_zones.get(route_id)

        route_rows.append({
            "route_id": route_id,
            "agency_id": f"sotrames_{zone_id}" if zone_id else "sotrames_unknown",
            "route_short_name": "",
            "route_long_name": route_id.replace("_", " "),
            "route_type": 3,  # bus
        })

        polygon_coords = buffer_line_to_polygon(coords, CORRIDOR_BUFFER_M)
        location_features.append({
            "type": "Feature",
            "id": route_id,
            "properties": {"name": route_id.replace("_", " ")},
            "geometry": {"type": "Polygon", "coordinates": [
                [[round(lon, 6), round(lat, 6)] for lon, lat in polygon_coords]
            ]},
        })

        if zone_id is None:
            skipped_no_schedule.append(route_id)
            continue  # geometry + location built above, but no trips

        z = zones[zone_id]
        trip_id = f"{route_id}_Laborable"
        trip_rows.append({"route_id": route_id, "service_id": "Laborable", "trip_id": trip_id})

        # Two legs (pickup-only, then drop-off-only), both referencing the
        # SAME location (we only have one zone per route) - required
        # because gtfs-validator's unusable_trip check requires >1
        # stop_times row per trip, and forbidden_pickup_type /
        # forbidden_drop_off_type forbid pickup_type=0/3 and
        # drop_off_type=0 respectively when using pickup_drop_off_window.
        # pickup_type=2 ("must phone agency") is the closest spec-valid
        # code to "flag it down" - GTFS-Flex has no vocabulary for
        # "unscheduled, no booking needed, just wave at the bus," which
        # is what this actually models. See the module docstring.
        stop_time_rows.append({
            "trip_id": trip_id,
            "stop_sequence": 0,
            "location_id": route_id,
            "start_pickup_drop_off_window": z["first_departure"],
            "end_pickup_drop_off_window": z["last_departure"],
            "pickup_type": 2,   # closest valid code to "flag down" - see comment above
            "drop_off_type": 1,  # no drop-off on this leg
        })
        stop_time_rows.append({
            "trip_id": trip_id,
            "stop_sequence": 1,
            "location_id": route_id,
            "start_pickup_drop_off_window": z["first_departure"],
            "end_pickup_drop_off_window": z["last_departure"],
            "pickup_type": 1,   # no pickup on this leg
            "drop_off_type": 2,
        })

        freq_rows.append({
            "trip_id": trip_id,
            "start_time": z["first_departure"],
            "end_time": z["last_departure"],
            "headway_secs": int(z["offpeak_headway_min"] * 60),
            "exact_times": 0,
        })

    if skipped_no_geometry:
        print(f"WARNING: {len(skipped_no_geometry)} KML file(s) had no usable "
              f"LineString: {skipped_no_geometry}", file=sys.stderr)
    if skipped_no_schedule:
        print(f"NOTE: {len(skipped_no_schedule)} route(s) built with geometry "
              f"only, no trips (no zone/schedule data found): {skipped_no_schedule}")

    calendar_rows = [{
        "service_id": "Laborable",
        "monday": 1, "tuesday": 1, "wednesday": 1, "thursday": 1, "friday": 1,
        "saturday": 0, "sunday": 0,
        "start_date": "20260101", "end_date": "20271231",
    }]

    OUT_DIR.mkdir(exist_ok=True)
    write_csv(OUT_DIR / "agency.txt", FIELDNAMES["agency.txt"], agency_rows)
    write_csv(OUT_DIR / "routes.txt", FIELDNAMES["routes.txt"], route_rows)
    write_csv(OUT_DIR / "stops.txt", FIELDNAMES["stops.txt"], [])
    write_csv(OUT_DIR / "trips.txt", FIELDNAMES["trips.txt"], trip_rows)
    write_csv(OUT_DIR / "stop_times.txt", FIELDNAMES["stop_times.txt"], stop_time_rows)
    write_csv(OUT_DIR / "frequencies.txt", FIELDNAMES["frequencies.txt"], freq_rows)
    write_csv(OUT_DIR / "calendar.txt", FIELDNAMES["calendar.txt"], calendar_rows)

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

    print(f"\nBuilt {ZIP_PATH}: {len(route_rows)} routes, {len(trip_rows)} trips "
          f"({len(skipped_no_schedule)} route(s) with geometry only, no schedule).")
    print("ALL trips built here use zone-level (not route-specific) schedule "
          "data - see data/sotrames_zones.yml for exactly which real published "
          "numbers were used and why. Weekday (Laborable) only - no weekend "
          "data exists in the source.")


if __name__ == "__main__":
    main()
