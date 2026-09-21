#!/usr/bin/env python3
"""
Build a GTFS feed for Transportes Rapido San Cristobal (TRSC) from
Medellín's official government ArcGIS data (raw/medellin_raw/, from
scripts/download_medellin_transporte_layers.py) plus
data/trsc_route_mapping.yml (which schedule photo, if any, belongs to
each of the 21 real routes) and data/trsc_schedule_photos.json (the
actual transcribed departure times, where transcription was possible).

KEY STRUCTURAL FACTS THIS BUILD RELIES ON, confirmed against real data
(see the conversation this script came from):
  - Each real route (id_ruta) has exactly 2 directional records
    (recorrido = "Origen-Destino" / "Destino-Origen"), each with its
    OWN distinct geometry (not a reversed copy of the other - genuinely
    different point counts and paths per direction).
  - Stops are ALSO split by recorrido, and nro_parada RESTARTS at 1 for
    each direction separately, not counted once per route.
  - Route geometry coordinates are in a PROJECTED CRS (EPSG:9377,
    meters), not lat/lon - transformed here via pyproj to EPSG:4326.
    Validated: the transformed route start point for id_ruta=90093 landed
    within ~5m of that route's own real stop #1 lat/lon (an independent
    field from a different layer) - strong cross-confirmation the
    transformation is correct, not just "runs without error."
  - Paradas layer 5 (vc_transporte_parada) is used exclusively for
    stops - confirmed richer than layer 0 (42/42 TRSC routes matched
    vs 34/42). Its own 'nombre' field is confirmed 0.03% populated
    citywide (essentially unusable) - direccion (99-100% populated for
    TRSC) is used as stop_name instead.
  - The two "Rutas de transporte publico" layers (VC_Transporte/6 and
    VM_Movilidad/2) are confirmed byte-for-byte IDENTICAL - only
    vc_transporte_rutas.json is used here, no need to reconcile a
    second copy.

WHAT'S PROVISIONAL, not confirmed - see data/trsc_route_mapping.yml
for full detail on each: several routes' identity and/or schedule
photo assignment rest on shared-name assumptions, geographic
plausibility, or the project owner's visual comparison of maps, not
independent confirmation. This script writes PROVISIONAL_DATA_WARNING.
txt alongside the feed listing exactly which routes carry that caveat,
rather than embedding it silently in the GTFS files themselves.

TRIPS ARE ONLY BUILT for routes whose assigned schedule photo has
"transcribed": true in data/trsc_schedule_photos.json. Several
routes have a schedule_photo assigned but it points at a photo that
was deliberately left untranscribed (COLORED_GRID_CARCEL,
AE_AURORA_ESTADIO, VEH_GRID - complex multi-column images where
reconstructing exact values from memory carried real error risk) - for
those, and for routes with no schedule_photo at all, this build
produces real stops.txt/shapes.txt geometry but NO trips/stop_times -
spatial data only, same "don't fabricate a schedule" policy used
throughout this project (e.g. Coonatra's Floresta-San Juan branches).

DIRECTION-SYMMETRY ASSUMPTION: the transcribed schedule photos give one
list of departure times each, not separately for each direction. This
build applies that same list of times to BOTH directions (Origen-
Destino and Destino-Origen) of a route, on the assumption that service
runs symmetrically in both directions - a simplification, not
something independently confirmed per direction.

Usage: python scripts/build_gtfs_trsc.py
Requires: raw/medellin_raw/vc_transporte_rutas.json and
          raw/medellin_raw/vc_transporte_parada.json (run
          scripts/download_medellin_transporte_layers.py first)
Output: gtfs-trsc.zip
        PROVISIONAL_DATA_WARNING.txt
"""

import csv
import json
import sys
import unicodedata
import zipfile
from math import cos, radians, sqrt
from pathlib import Path

import yaml
from pyproj import Transformer

RUTAS_PATH = Path("raw/medellin_raw/vc_transporte_rutas.json")
PARADA_PATH = Path("raw/medellin_raw/vc_transporte_parada.json")
MAPPING_PATH = Path("data/trsc_route_mapping.yml")
SCHEDULE_PATH = Path("data/trsc_schedule_photos.json")

OUT_DIR = Path("gtfs-trsc-out")
ZIP_PATH = Path("gtfs-trsc.zip")
WARNING_PATH = Path("PROVISIONAL_DATA_WARNING.txt")

AVERAGE_SPEED_KMH = 18  # ASSUMED, same figure used elsewhere in this project
SUSPICIOUS_SNAP_DIST_M = 150  # same threshold used for Coonatra

CRS_TRANSFORMER = Transformer.from_crs("EPSG:9377", "EPSG:4326", always_xy=True)


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def to_xy(lon, lat, lat0):
    m_per_deg_lat = 111_320.0
    m_per_deg_lon = 111_320.0 * cos(radians(lat0))
    return lon * m_per_deg_lon, lat * m_per_deg_lat


def to_lon_lat(x, y, lat0):
    m_per_deg_lat = 111_320.0
    m_per_deg_lon = 111_320.0 * cos(radians(lat0))
    return x / m_per_deg_lon, y / m_per_deg_lat


def project_point_to_line(px, py, line_xy):
    """Same technique as build_gtfs_coonatra.py - nearest-point
    projection, returns (distance along the line, perpendicular snap
    distance, projected (x,y))."""
    best_dist_along, best_snap_dist, cum = 0.0, float("inf"), 0.0
    best_point = (px, py)
    for i in range(len(line_xy) - 1):
        x1, y1 = line_xy[i]
        x2, y2 = line_xy[i + 1]
        seg_len = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        if seg_len == 0:
            continue
        t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / (seg_len ** 2)))
        cx, cy = x1 + t * (x2 - x1), y1 + t * (y2 - y1)
        snap_dist = sqrt((px - cx) ** 2 + (py - cy) ** 2)
        if snap_dist < best_snap_dist:
            best_snap_dist, best_dist_along, best_point = snap_dist, cum + t * seg_len, (cx, cy)
        cum += seg_len
    return best_dist_along, best_snap_dist, best_point


def line_length_m(line_xy):
    return sum(sqrt((line_xy[i+1][0]-line_xy[i][0])**2 + (line_xy[i+1][1]-line_xy[i][1])**2)
               for i in range(len(line_xy) - 1))


def add_seconds(hhmmss: str, seconds: float) -> str:
    parts = hhmmss.split(":")
    h, m = int(parts[0]), int(parts[1])
    s = int(parts[2]) if len(parts) > 2 else 0
    total = h * 3600 + m * 60 + s + round(seconds)
    h2, rem = divmod(total, 3600)
    m2, s2 = divmod(rem, 60)
    return f"{h2:02d}:{m2:02d}:{s2:02d}"


def write_csv(path: Path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_trsc_data():
    if not RUTAS_PATH.exists() or not PARADA_PATH.exists():
        print(f"{RUTAS_PATH} / {PARADA_PATH} not found - run "
              f"scripts/download_medellin_transporte_layers.py first.", file=sys.stderr)
        sys.exit(1)

    all_rutas = json.loads(RUTAS_PATH.read_text())
    all_parada = json.loads(PARADA_PATH.read_text())

    def is_trsc(attrs):
        empresa = attrs.get("empresa")
        return bool(empresa) and "CRISTOBAL" in strip_accents(empresa.upper())

    rutas = [f for f in all_rutas if is_trsc(f["attributes"])]
    parada = [f for f in all_parada if is_trsc(f["attributes"])]
    return rutas, parada


def main():
    rutas, parada = load_trsc_data()
    print(f"Loaded {len(rutas)} TRSC route record(s), {len(parada)} TRSC stop record(s)")

    mapping = yaml.safe_load(MAPPING_PATH.read_text())["routes"]
    schedules = json.loads(SCHEDULE_PATH.read_text())

    rutas_by_id_dir = {}
    for r in rutas:
        a = r["attributes"]
        rutas_by_id_dir[(a["id_ruta"], a["recorrido"])] = r

    parada_by_id_dir = {}
    for p in parada:
        a = p["attributes"]
        key = (str(a["id_ruta"]), a["recorrido"])
        parada_by_id_dir.setdefault(key, []).append(a)

    agency_rows = [{
        "agency_id": "trsc", "agency_name": "Transportes Rapido San Cristobal",
        "agency_url": "https://trscsas.com", "agency_timezone": "America/Bogota",
        "agency_lang": "es",
    }]
    calendar_rows = [{
        "service_id": "Diario", "monday": 1, "tuesday": 1, "wednesday": 1,
        "thursday": 1, "friday": 1, "saturday": 1, "sunday": 1,
        "start_date": "20260101", "end_date": "20271231",
    }]

    route_rows, stop_rows, trip_rows, shape_rows, stop_time_rows = [], [], [], [], []
    provisional_notes = []
    suspicious_stops = []
    routes_with_trips, routes_without_trips = 0, 0

    for route_cfg in mapping:
        id_ruta = route_cfg["id_ruta"]
        codigo = route_cfg["codigo"]
        nombre = route_cfg["nombre"]
        route_id = f"trsc_{id_ruta}"

        if route_cfg.get("identity_confidence") == "provisional":
            provisional_notes.append(f"ROUTE IDENTITY provisional: {codigo} ({nombre}, "
                                      f"id_ruta={id_ruta}) - see data/trsc_route_mapping.yml")

        route_rows.append({
            "route_id": route_id, "agency_id": "trsc",
            "route_short_name": codigo, "route_long_name": nombre, "route_type": 3,
        })

        schedule_key = route_cfg.get("schedule_photo")
        times = None
        if schedule_key:
            sched = schedules.get(schedule_key, {})
            if sched.get("transcribed"):
                times = sched["times"]
                if route_cfg.get("schedule_confidence") == "provisional":
                    provisional_notes.append(f"SCHEDULE provisional: {codigo} ({nombre}, "
                                              f"id_ruta={id_ruta}) uses {schedule_key} - "
                                              f"see data/trsc_route_mapping.yml")
            else:
                provisional_notes.append(f"SCHEDULE NOT BUILT: {codigo} ({nombre}, "
                                          f"id_ruta={id_ruta}) references {schedule_key}, "
                                          f"which was never transcribed (see "
                                          f"data/trsc_schedule_photos.json) - stops/shape "
                                          f"only, no trips")

        any_trips_for_route = False
        for recorrido, dir_suffix in [("Origen-Destino", "OD"), ("Destino-Origen", "DO")]:
            route_rec = rutas_by_id_dir.get((id_ruta, recorrido))
            stops = parada_by_id_dir.get((id_ruta, recorrido), [])
            if not route_rec:
                print(f"  WARNING: no {recorrido} geometry found for id_ruta={id_ruta} "
                      f"({nombre}) - skipping this direction", file=sys.stderr)
                continue
            if not stops:
                print(f"  WARNING: no {recorrido} stops found for id_ruta={id_ruta} "
                      f"({nombre}) - skipping this direction", file=sys.stderr)
                continue

            raw_path = route_rec["geometry"]["paths"][0]
            line_lonlat = [CRS_TRANSFORMER.transform(x, y) for x, y in raw_path]
            lat0 = sum(lat for _, lat in line_lonlat) / len(line_lonlat)
            line_xy = [to_xy(lon, lat, lat0) for lon, lat in line_lonlat]
            total_len_m = line_length_m(line_xy)
            running_time_s = total_len_m / (AVERAGE_SPEED_KMH * 1000 / 3600)

            shape_id = f"{route_id}_{dir_suffix}"
            for seq, (lon, lat) in enumerate(line_lonlat):
                shape_rows.append({
                    "shape_id": shape_id, "shape_pt_lat": lat, "shape_pt_lon": lon,
                    "shape_pt_sequence": seq,
                })

            ordered_stops = []
            for s in sorted(stops, key=lambda a: a.get("nro_parada", 0)):
                px, py = to_xy(s["longitud"], s["latitud"], lat0)
                dist_along, snap_dist, _ = project_point_to_line(px, py, line_xy)
                if snap_dist > SUSPICIOUS_SNAP_DIST_M:
                    suspicious_stops.append((route_id, dir_suffix, s.get("direccion"), round(snap_dist)))
                ordered_stops.append({
                    "name": s.get("direccion"), "lat": s["latitud"], "lon": s["longitud"],
                    "dist_along": dist_along, "orig_nro_parada": s["nro_parada"],
                })
            ordered_stops.sort(key=lambda x: x["dist_along"])

            # nro_parada can have real decimal values (e.g. 7.0, 7.1, 7.2 -
            # inserted stops between existing numbers, confirmed real for
            # several routes - see the conversation this came from for the
            # full list). stop_id is kept tied to this original source
            # value (decimal preserved as an underscore, e.g. "..._7_1")
            # so it stays a stable, traceable identifier back to the real
            # Paradas record - only stop_times.txt's stop_sequence (below,
            # via enumerate() over this same real sorted order) is
            # renumbered cleanly; stop_id itself is deliberately NOT
            # renumbered.
            for s in ordered_stops:
                nro_str = str(s["orig_nro_parada"]).replace(".", "_")
                s["stop_id"] = f"{route_id}_{dir_suffix}_{nro_str}"
                s["name"] = s["name"] or s["stop_id"]

            for s in ordered_stops:
                stop_rows.append({"stop_id": s["stop_id"], "stop_name": s["name"],
                                   "stop_lat": s["lat"], "stop_lon": s["lon"]})

            if times:
                any_trips_for_route = True
                for trip_idx, dep_time in enumerate(times):
                    trip_id = f"{shape_id}_{trip_idx}"
                    trip_rows.append({"route_id": route_id, "service_id": "Diario",
                                       "trip_id": trip_id, "shape_id": shape_id})
                    for seq, s in enumerate(ordered_stops):
                        fraction = s["dist_along"] / total_len_m if total_len_m > 0 else 0
                        t = add_seconds(dep_time, running_time_s * fraction)
                        stop_time_rows.append({
                            "trip_id": trip_id, "stop_id": s["stop_id"], "stop_sequence": seq,
                            "arrival_time": t, "departure_time": t,
                        })

        if any_trips_for_route:
            routes_with_trips += 1
        else:
            routes_without_trips += 1

    print(f"\n{routes_with_trips} route(s) with real trips, "
          f"{routes_without_trips} route(s) with stops/shape only (no schedule)")

    if suspicious_stops:
        print(f"\n{len(suspicious_stops)} stop(s) relocated onto their route line "
              f"(>{SUSPICIOUS_SNAP_DIST_M}m from raw position):", file=sys.stderr)
        for route_id, dir_suffix, name, dist in suspicious_stops[:20]:
            print(f"  {route_id} {dir_suffix}: {name!r} - was {dist}m away", file=sys.stderr)
        if len(suspicious_stops) > 20:
            print(f"  ... and {len(suspicious_stops) - 20} more", file=sys.stderr)

    # Deduplicate stops (same stop_id can appear once per direction built,
    # never truly duplicated since stop_id includes dir_suffix + nro_parada)
    OUT_DIR.mkdir(exist_ok=True)
    write_csv(OUT_DIR / "agency.txt", ["agency_id", "agency_name", "agency_url",
              "agency_timezone", "agency_lang"], agency_rows)
    write_csv(OUT_DIR / "routes.txt", ["route_id", "agency_id", "route_short_name",
              "route_long_name", "route_type"], route_rows)
    write_csv(OUT_DIR / "stops.txt", ["stop_id", "stop_name", "stop_lat", "stop_lon"], stop_rows)
    write_csv(OUT_DIR / "trips.txt", ["route_id", "service_id", "trip_id", "shape_id"], trip_rows)
    write_csv(OUT_DIR / "shapes.txt", ["shape_id", "shape_pt_lat", "shape_pt_lon",
              "shape_pt_sequence"], shape_rows)
    write_csv(OUT_DIR / "stop_times.txt", ["trip_id", "stop_id", "stop_sequence",
              "arrival_time", "departure_time"], stop_time_rows)
    write_csv(OUT_DIR / "calendar.txt", ["service_id", "monday", "tuesday", "wednesday",
              "thursday", "friday", "saturday", "sunday", "start_date", "end_date"], calendar_rows)

    with (OUT_DIR / "feed_info.txt").open("w", newline="") as fh:
        fh.write("feed_publisher_name,feed_publisher_url,feed_lang\n")
        fh.write("ColombiaTransit,https://github.com/ColombiaTransit,es\n")

    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in OUT_DIR.glob("*.txt"):
            zf.write(f, f.name)

    WARNING_PATH.write_text(
        "TRSC GTFS feed - PROVISIONAL DATA WARNING\n"
        "==========================================\n\n"
        "This feed mixes confirmed and provisional route identity/schedule\n"
        "assignments. See data/trsc_route_mapping.yml for full detail on\n"
        "every route. Provisional items in this build:\n\n"
        + "\n".join(f"- {n}" for n in provisional_notes) + "\n"
    )

    print(f"\nBuilt {ZIP_PATH}: {len(route_rows)} route(s), {len(stop_rows)} stop(s), "
          f"{len(trip_rows)} trip(s), {len(shape_rows)} shape point(s).")
    print(f"Provisional-data notes -> {WARNING_PATH} ({len(provisional_notes)} item(s))")


if __name__ == "__main__":
    main()
