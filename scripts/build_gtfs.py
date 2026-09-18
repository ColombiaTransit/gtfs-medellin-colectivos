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

  Stop ORDER along a route is not read from any ArcGIS field (there
  isn't one) - each stop is snapped onto its route's own line geometry
  and ordered by distance travelled along that line
  (order_stops_along_line). Stops landing implausibly far from their
  route's line (SUSPICIOUS_SNAP_DIST_M) are flagged in the build log as
  a possible bad 'ruta' join rather than silently trusted.
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

AVERAGE_SPEED_KMH = 18  # rough urban feeder-bus speed, for placeholder timing
SUSPICIOUS_SNAP_DIST_M = 150  # flag stops further than this from their route's line

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


def _to_local_xy(lon, lat, lat0):
    """Flat-earth approximation (equirectangular) centered at lat0, in
    meters. Fine for city-scale distances (a few km); not for anything
    long enough that Earth's curvature matters."""
    meters_per_deg_lat = 111_320.0
    meters_per_deg_lon = 111_320.0 * cos(radians(lat0))
    x = lon * meters_per_deg_lon
    y = lat * meters_per_deg_lat
    return x, y


def _prepare_line(line_coords):
    """Precompute local-xy coordinates and cumulative segment-start
    distances for a line, for reuse across many point projections."""
    lat0 = sum(lat for _, lat in line_coords) / len(line_coords)
    line_xy = [_to_local_xy(lon, lat, lat0) for lon, lat in line_coords]
    seg_cum = [0.0]
    for (x1, y1), (x2, y2) in zip(line_xy, line_xy[1:]):
        seg_cum.append(seg_cum[-1] + sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))
    return line_xy, seg_cum, lat0


def _project_point(lon, lat, line_xy, seg_cum, lat0):
    """Snap one point onto a prepared line. Returns (dist_along_m,
    perp_dist_m): distance travelled along the line to the nearest
    point, and the point's perpendicular distance off the line."""
    if len(line_xy) < 2:
        return 0.0, float("inf")

    px, py = _to_local_xy(lon, lat, lat0)
    best_dist_along = 0.0
    best_perp_dist = float("inf")

    for i, ((x1, y1), (x2, y2)) in enumerate(zip(line_xy, line_xy[1:])):
        dx, dy = x2 - x1, y2 - y1
        seg_len_sq = dx * dx + dy * dy
        if seg_len_sq == 0:
            t = 0.0
        else:
            t = ((px - x1) * dx + (py - y1) * dy) / seg_len_sq
            t = max(0.0, min(1.0, t))
        proj_x, proj_y = x1 + t * dx, y1 + t * dy
        perp_dist = sqrt((px - proj_x) ** 2 + (py - proj_y) ** 2)

        if perp_dist < best_perp_dist:
            best_perp_dist = perp_dist
            seg_len = sqrt(seg_len_sq) if seg_len_sq else 0.0
            best_dist_along = seg_cum[i] + t * seg_len

    return best_dist_along, best_perp_dist


def assign_stops_to_directions(stops, direction_coords):
    """direction_coords: {sentido_value: line_coords} - one entry per
    direction a route actually has (usually 1 or 2).

    The 'paradas' layer has no 'sentido' field, so every stop tagged
    with a given 'ruta' is a candidate for EVERY direction that route
    has - we can't tell from the data alone which direction a stop
    belongs to. Instead of assuming they all belong to whichever
    direction we happened to pick a shape from (which produced dozens of
    false "stop far from route" flags when outbound/return use different
    streets), each stop is snapped against ALL of the route's directions
    and assigned to whichever one it's actually closest to.

    Returns {sentido_value: [stops ordered by distance along that
    direction's line]}. Each stop dict gains '_dist_along_m' (for its
    assigned direction) and '_snap_dist_m' (perpendicular distance to
    that direction's line - still a real distance to check, just no
    longer inflated by comparing against the wrong direction).
    """
    prepared = {
        sentido: _prepare_line(coords)
        for sentido, coords in direction_coords.items()
        if len(coords) >= 2
    }

    by_sentido = {sentido: [] for sentido in prepared}

    for stop in stops:
        best_sentido, best_dist_along, best_perp = None, 0.0, float("inf")
        for sentido, (line_xy, seg_cum, lat0) in prepared.items():
            dist_along, perp = _project_point(
                stop["stop_lon"], stop["stop_lat"], line_xy, seg_cum, lat0
            )
            if perp < best_perp:
                best_sentido, best_dist_along, best_perp = sentido, dist_along, perp

        if best_sentido is None:
            continue
        stop["_dist_along_m"] = best_dist_along
        stop["_snap_dist_m"] = best_perp
        by_sentido[best_sentido].append(stop)

    for stop_list in by_sentido.values():
        stop_list.sort(key=lambda s: s["_dist_along_m"])

    return by_sentido


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

    # --- group stops by route (ruta) - NOT sorted here; real stop order
    # is computed per-route further down, once each route's shape
    # geometry is known, by snapping stops onto that geometry (see
    # order_stops_along_line). --------------------------------------------
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
        }
        stops_by_route.setdefault(route_key, []).append(stop_record)
        all_stops_by_id[stop_id] = stop_record

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
    skipped_direction_no_stops = []  # (route_id, sentido) - direction had <2 stops assigned
    suspicious_stops = []  # (route_id, stop_id, snap_distance_m) - stop far from BOTH its route's directions
    provisional_trip_ids = []  # trip_ids built from a day_type marked provisional: true (fake/placeholder data)

    # --- group route features by ruta, since ~most routes have MORE THAN
    # ONE feature row (confirmed via inspect_fields.py: 102 rows / 46
    # distinct 'ruta' values). Processing rows independently used to
    # silently produce duplicate route_id rows and colliding
    # shape_pt_sequence numbers for every such route - fixed by grouping
    # first. Within a ruta, rows can differ by 'sentido' (a real
    # direction pair) or share the same 'sentido' (split line segments of
    # one direction, meant to be concatenated) - segments sharing a
    # sentido are concatenated in objectid order below.
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

        # Build ONE set of coords per sentido this route actually has
        # (usually 1 or 2), concatenating same-sentido segments in
        # objectid order.
        features_by_sentido = {}
        for f in route_features:
            features_by_sentido.setdefault(f["properties"].get("sentido"), []).append(f)

        direction_coords = {}
        direction_length_km = {}
        for sentido, segs in features_by_sentido.items():
            segs = sorted(segs, key=lambda f: f["properties"].get("objectid", 0))
            coords = []
            for seg in segs:
                geom = seg["geometry"]
                seg_coords = (
                    geom["coordinates"]
                    if geom["type"] == "LineString"
                    else geom["coordinates"][0]  # first part of a MultiLineString
                )
                coords.extend(seg_coords)
            direction_coords[sentido] = coords

            seg_lengths = [s["properties"].get(ROUTE_LENGTH_FIELD) for s in segs]
            direction_length_km[sentido] = (
                sum(seg_lengths) / 1000 if all(seg_lengths) else line_length_km(coords)
            )

        # route-level metadata (linea, etc.) from whichever direction has
        # the smallest sentido value, just for a consistent, deterministic
        # choice - doesn't affect either direction's geometry or stops.
        primary_sentido = sorted(direction_coords.keys(), key=lambda s: (s is None, s))[0]
        primary_props = sorted(
            features_by_sentido[primary_sentido],
            key=lambda f: f["properties"].get("objectid", 0),
        )[0]["properties"]

        # Stops have no 'sentido' field at all - every stop tagged with
        # this 'ruta' is a candidate for EVERY direction the route has.
        # Snap each stop against all of them and keep whichever is
        # actually closest, instead of assuming they all belong to one
        # arbitrarily chosen direction (which produced dozens of false
        # "stop far from route" flags on routes whose outbound/return
        # legs use different streets).
        stops_by_sentido = assign_stops_to_directions(route_stops, direction_coords)

        for sentido, stop_list in stops_by_sentido.items():
            for stop in stop_list:
                if stop.get("_snap_dist_m", 0) > SUSPICIOUS_SNAP_DIST_M:
                    suspicious_stops.append((route_id, stop["stop_id"], stop["_snap_dist_m"]))

        operator = cfg["operator"]

        route_rows.append({
            "route_id": route_id,
            "agency_id": operator,
            "route_short_name": cfg.get("route_short_name", route_id),
            "route_long_name": cfg.get(
                "route_long_name", primary_props.get(ROUTE_NAME_FIELD, "")
            ),
            "route_type": 3,  # bus
        })

        # direction_id: smallest sentido -> 0, next -> 1, etc. (only
        # matters for internal consistency between shapes/trips - GTFS
        # doesn't care which physical direction is "0").
        sentido_to_direction_id = {
            sentido: i
            for i, sentido in enumerate(
                sorted(direction_coords.keys(), key=lambda s: (s is None, s))
            )
        }

        for sentido, coords in direction_coords.items():
            direction_id = sentido_to_direction_id[sentido]
            shape_id = f"{route_id}_{direction_id}"

            direction_stops = stops_by_sentido.get(sentido, [])
            if len(direction_stops) < 2:
                skipped_direction_no_stops.append((route_id, sentido))
                continue

            for seq, (lon, lat) in enumerate(coords):
                shape_rows.append({
                    "shape_id": shape_id,
                    "shape_pt_lat": lat,
                    "shape_pt_lon": lon,
                    "shape_pt_sequence": seq,
                })

            length_km = direction_length_km[sentido]
            running_time_min = max(1, round(length_km / AVERAGE_SPEED_KMH * 60))
            n_stops = len(direction_stops)

            for day_type, sched in cfg["day_types"].items():
                service_id = DAY_TYPE_SERVICE_IDS.get(day_type, day_type)
                trip_id = f"{route_id}_{direction_id}_{service_id}"

                if sched.get("provisional"):
                    provisional_trip_ids.append(trip_id)

                trip_rows.append({
                    "route_id": route_id,
                    "service_id": service_id,
                    "trip_id": trip_id,
                    "shape_id": shape_id,
                    "direction_id": direction_id,
                })

                # Space stops evenly across the placeholder running time.
                # Real per-segment timings would replace this if ever available.
                for i, stop in enumerate(direction_stops):
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
    if skipped_direction_no_stops:
        print(
            f"NOTE: {len(skipped_direction_no_stops)} direction(s) had fewer "
            f"than 2 stops assigned to them (out of all directions their route "
            f"has) and were skipped - normal for a route where one direction "
            f"genuinely has few/no ArcGIS-mapped stops: "
            f"{skipped_direction_no_stops[:10]}"
            f"{'...' if len(skipped_direction_no_stops) > 10 else ''}"
        )
    if suspicious_stops:
        print(
            f"WARNING: {len(suspicious_stops)} stop(s) are more than "
            f"{SUSPICIOUS_SNAP_DIST_M}m from BOTH of their route's directions "
            f"(after checking each direction and keeping the closer one) - "
            f"possible bad 'ruta' join or a genuinely offset stop. "
            f"Worth checking on a map: "
            f"{[(r, s, round(d)) for r, s, d in suspicious_stops[:10]]}"
            f"{'...' if len(suspicious_stops) > 10 else ''}"
        )

    if provisional_trip_ids:
        print(
            f"\n{'!' * 70}\n"
            f"WARNING: THIS BUILD CONTAINS {len(provisional_trip_ids)} TRIP(S) "
            f"BUILT FROM FAKE/PLACEHOLDER SCHEDULE DATA\n"
            f"(day_types marked 'provisional: true' in data/operators.yml).\n"
            f"DO NOT publish or treat this feed's frequencies/times as real "
            f"for those routes until real data replaces the placeholders.\n"
            f"{'!' * 70}\n",
            file=sys.stderr,
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

    if provisional_trip_ids:
        warning_path = Path("PROVISIONAL_DATA_WARNING.txt")
        warning_path.write_text(
            "THIS BUILD CONTAINS FAKE/PLACEHOLDER SCHEDULE DATA.\n\n"
            f"{len(provisional_trip_ids)} trip(s) were built from day_types "
            "marked 'provisional: true' in data/operators.yml - these are "
            "invented round numbers (e.g. 05:00 start, 10/15 min headways), "
            "NOT real schedules, used only so the pipeline has something to "
            "build and validate against while real data is gathered.\n\n"
            "DO NOT publish this feed's frequencies/times for these routes "
            "as real. Affected trip_ids:\n"
            + "\n".join(f"  {t}" for t in provisional_trip_ids)
        )
        print(f"Wrote {warning_path} - see it for the full list of affected trips.")

    print(f"Built {zip_path} with {len(route_rows)} routes, "
          f"{len(stop_rows)} stops, {len(trip_rows)} trips"
          + (f" ({len(provisional_trip_ids)} from FAKE placeholder data - "
             f"see PROVISIONAL_DATA_WARNING.txt)" if provisional_trip_ids else "")
          + ".")


if __name__ == "__main__":
    main()
