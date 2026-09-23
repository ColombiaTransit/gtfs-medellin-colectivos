#!/usr/bin/env python3
"""
Build a GTFS feed for Transacoop from Medellín's official ArcGIS
transport layers (raw/medellin_raw/, current) plus real schedule data
from the operator's own website (trasancoop.com), per
data/transacoop_route_mapping.yml. See docs/transacoop.md for the
full source breakdown.

MATCHING: the website's 9 numbered branches are mapped to ArcGIS's
"98 Directa 1" through "98 Directa 9" BY NUMBER ORDER, per the project
owner's explicit direction - NOT independently confirmed by this
project via village-name or geometry cross-referencing (a real attempt
at that found genuine complications - see the mapping file's
docstring). Every route below is built with match_confidence
"provisional_by_number_order", not "confirmed".

SERVICE DAYS: only 2 real patterns exist in the source (Lunes a Sábado
combined, and Domingo) - not the usual 3-way weekday/Saturday/Sunday
split used for other operators in this project, since the source
doesn't actually distinguish Saturday from weekday.

ALL 9 real ArcGIS routes are built - 8 get real frequency-based trips,
the 9th ("Directa 8"/website branch 8) has no frequency given anywhere
on the site and is built spatial-only (real stops/shape, no trips) -
same "don't fabricate a schedule" policy used throughout this project.

Usage: python scripts/build_gtfs_transacoop.py
Requires: raw/medellin_raw/vc_transporte_rutas.json and
          vc_transporte_parada.json (run
          scripts/download_medellin_transporte_layers.py first)
          data/transacoop_route_mapping.yml
Output: gtfs-transacoop.zip
"""

import csv
import json
import sys
import zipfile
from math import cos, radians, sqrt
from pathlib import Path

import yaml
from pyproj import Transformer

RUTAS_PATH = Path("raw/medellin_raw/vc_transporte_rutas.json")
PARADA_PATH = Path("raw/medellin_raw/vc_transporte_parada.json")
MAPPING_PATH = Path("data/transacoop_route_mapping.yml")

OUT_DIR = Path("gtfs-transacoop-out")
ZIP_PATH = Path("gtfs-transacoop.zip")

EMPRESA_NAME = "Transacoop"
AVERAGE_SPEED_KMH = 18
SUSPICIOUS_SNAP_DIST_M = 150
CRS_TRANSFORMER = Transformer.from_crs("EPSG:9377", "EPSG:4326", always_xy=True)

DAY_SERVICE_MAP = [("lunes_sabado", "LunesSabado"), ("domingo", "Domingo")]


def to_xy(lon, lat, lat0):
    m_per_deg_lat = 111_320.0
    m_per_deg_lon = 111_320.0 * cos(radians(lat0))
    return lon * m_per_deg_lon, lat * m_per_deg_lat


def project_point_to_line(px, py, line_xy):
    best_dist_along, best_snap_dist, cum = 0.0, float("inf"), 0.0
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
            best_snap_dist, best_dist_along = snap_dist, cum + t * seg_len
        cum += seg_len
    return best_dist_along, best_snap_dist


def seconds_to_gtfs_time(total_seconds: float) -> str:
    total_seconds = round(total_seconds)
    h, rem = divmod(total_seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def write_csv(path: Path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_arcgis_data():
    all_rutas = json.loads(RUTAS_PATH.read_text())
    all_parada = json.loads(PARADA_PATH.read_text())

    def is_this_empresa(attrs):
        return attrs.get("empresa") == EMPRESA_NAME

    rutas_by_id, rutas_by_id_dir = {}, {}
    for r in all_rutas:
        a = r["attributes"]
        if is_this_empresa(a):
            rutas_by_id_dir[(a["id_ruta"], a["recorrido"])] = r
            rutas_by_id.setdefault(a["id_ruta"], {"codigo": a["codigo"], "nombre": a["nombre"]})

    parada_by_id_dir = {}
    for p in all_parada:
        a = p["attributes"]
        if is_this_empresa(a):
            key = (str(a["id_ruta"]), a["recorrido"])
            parada_by_id_dir.setdefault(key, []).append(a)

    return rutas_by_id, rutas_by_id_dir, parada_by_id_dir


def main():
    for p in (RUTAS_PATH, PARADA_PATH, MAPPING_PATH):
        if not p.exists():
            print(f"{p} not found.", file=sys.stderr)
            sys.exit(1)

    mapping = yaml.safe_load(MAPPING_PATH.read_text())
    hours = mapping["hours"]
    scheduled_routes = {r["id_ruta"]: r for r in mapping["routes"]}
    rutas_by_id, arcgis_rutas, arcgis_parada = load_arcgis_data()
    print(f"Found {len(rutas_by_id)} real ArcGIS route(s) for {EMPRESA_NAME!r}; "
          f"{len(scheduled_routes)} have real website-sourced frequency data.")

    agency_rows = [{
        "agency_id": "transacoop", "agency_name": "Transacoop",
        "agency_url": "https://www.trasancoop.com", "agency_timezone": "America/Bogota",
        "agency_lang": "es",
    }]
    calendar_rows = [
        {"service_id": "LunesSabado", "monday": 1, "tuesday": 1, "wednesday": 1,
         "thursday": 1, "friday": 1, "saturday": 1, "sunday": 0,
         "start_date": "20260101", "end_date": "20271231"},
        {"service_id": "Domingo", "monday": 0, "tuesday": 0, "wednesday": 0,
         "thursday": 0, "friday": 0, "saturday": 0, "sunday": 1,
         "start_date": "20260101", "end_date": "20271231"},
    ]

    route_rows, stop_rows, trip_rows, shape_rows, frequency_rows, stop_time_rows = [], [], [], [], [], []
    suspicious_stops = []

    for id_ruta, info in sorted(rutas_by_id.items()):
        route_id = f"transacoop_{id_ruta}"
        route_cfg = scheduled_routes.get(id_ruta)
        route_desc = ""
        if route_cfg:
            assumed_note = ""
            if route_cfg.get("frequency_confidence") == "assumed":
                assumed_note = " FRECUENCIA ASUMIDA (no hay dato real en la web para esta rama)."
            route_desc = (f"Coincidencia con la web por numero de orden (rama "
                          f"{route_cfg['website_branch']}) - PROVISIONAL, no confirmada "
                          f"de forma independiente. {route_cfg['descripcion_web']}{assumed_note}")
        route_rows.append({
            "route_id": route_id, "agency_id": "transacoop",
            "route_short_name": info["codigo"], "route_long_name": info["nombre"],
            "route_desc": route_desc, "route_type": 3,
        })

        n_trips_built = 0
        for recorrido, dir_suffix in [("Origen-Destino", "OD"), ("Destino-Origen", "DO")]:
            route_rec = arcgis_rutas.get((id_ruta, recorrido))
            dir_stops = arcgis_parada.get((id_ruta, recorrido), [])
            if not route_rec:
                print(f"  WARNING: no {recorrido} ArcGIS geometry for "
                      f"{info['codigo']!r} (id_ruta={id_ruta}) - "
                      f"skipping this direction", file=sys.stderr)
                continue

            raw_path = route_rec["geometry"]["paths"][0]
            line_lonlat = [CRS_TRANSFORMER.transform(x, y) for x, y in raw_path]
            lat0 = sum(lat for _, lat in line_lonlat) / len(line_lonlat)
            line_xy = [to_xy(lon, lat, lat0) for lon, lat in line_lonlat]

            shape_id = f"{route_id}_{dir_suffix}"
            for seq, (lon, lat) in enumerate(line_lonlat):
                shape_rows.append({
                    "shape_id": shape_id, "shape_pt_lat": lat, "shape_pt_lon": lon,
                    "shape_pt_sequence": seq,
                })

            ordered_stops = []
            for s in sorted(dir_stops, key=lambda a: a.get("nro_parada", 0)):
                px, py = to_xy(s["longitud"], s["latitud"], lat0)
                dist_along, snap_dist = project_point_to_line(px, py, line_xy)
                if snap_dist > SUSPICIOUS_SNAP_DIST_M:
                    suspicious_stops.append((f"{route_id}_{dir_suffix}", s.get("direccion"), round(snap_dist)))
                nro_str = str(s["nro_parada"]).replace(".", "_")
                stop_id = f"{route_id}_{dir_suffix}_{nro_str}_{s['objectid']}"
                ordered_stops.append({"stop_id": stop_id, "name": s.get("direccion") or stop_id,
                                       "lat": s["latitud"], "lon": s["longitud"], "dist_along": dist_along})
            ordered_stops.sort(key=lambda x: x["dist_along"])

            if not ordered_stops:
                print(f"  WARNING: no {recorrido} stops for {info['codigo']!r} "
                      f"(id_ruta={id_ruta}) - shape only, no stop_times/trips for this "
                      f"direction", file=sys.stderr)
                continue

            for s in ordered_stops:
                stop_rows.append({"stop_id": s["stop_id"], "stop_name": s["name"],
                                   "stop_lat": s["lat"], "stop_lon": s["lon"]})

            if len(ordered_stops) < 2 or not route_cfg:
                continue  # spatial-only: real stops/shape above, no trips below

            total_len_m = sum(
                sqrt((line_xy[i + 1][0] - line_xy[i][0]) ** 2 + (line_xy[i + 1][1] - line_xy[i][1]) ** 2)
                for i in range(len(line_xy) - 1)
            )
            running_time_s = total_len_m / (AVERAGE_SPEED_KMH * 1000 / 3600)

            for day_key, service_id in DAY_SERVICE_MAP:
                day_hours = hours[day_key]
                trip_id = f"{route_id}_{dir_suffix}_{service_id}"
                trip_rows.append({"route_id": route_id, "service_id": service_id,
                                   "trip_id": trip_id, "shape_id": shape_id})
                for seq, s in enumerate(ordered_stops):
                    fraction = s["dist_along"] / total_len_m if total_len_m > 0 else 0
                    t = seconds_to_gtfs_time(running_time_s * fraction)
                    stop_time_rows.append({
                        "trip_id": trip_id, "stop_id": s["stop_id"], "stop_sequence": seq,
                        "arrival_time": t, "departure_time": t,
                    })
                frequency_rows.append({
                    "trip_id": trip_id,
                    "start_time": day_hours["inicio"],
                    "end_time": day_hours["fin"],
                    "headway_secs": route_cfg["headway_min"][day_key] * 60,
                })
                n_trips_built += 1

        if route_cfg:
            freq_flag = "ASSUMED headway" if route_cfg.get("frequency_confidence") == "assumed" else "real headway"
            kind = f"frequency-based [PROVISIONAL match, {freq_flag}]"
        else:
            kind = "spatial-only, no frequency given"
        print(f"  {info['codigo']} ({info['nombre']}): {n_trips_built} trip(s) built [{kind}]")

    if suspicious_stops:
        print(f"\n{len(suspicious_stops)} stop(s) more than {SUSPICIOUS_SNAP_DIST_M}m "
              f"from their route's line (flagged only):", file=sys.stderr)
        for route_id, name, dist in suspicious_stops[:20]:
            print(f"  {route_id}: {name!r} - {dist}m", file=sys.stderr)

    OUT_DIR.mkdir(exist_ok=True)
    write_csv(OUT_DIR / "agency.txt", ["agency_id", "agency_name", "agency_url",
              "agency_timezone", "agency_lang"], agency_rows)
    write_csv(OUT_DIR / "routes.txt", ["route_id", "agency_id", "route_short_name",
              "route_long_name", "route_desc", "route_type"], route_rows)
    write_csv(OUT_DIR / "stops.txt", ["stop_id", "stop_name", "stop_lat", "stop_lon"], stop_rows)
    write_csv(OUT_DIR / "trips.txt", ["route_id", "service_id", "trip_id", "shape_id"], trip_rows)
    write_csv(OUT_DIR / "stop_times.txt", ["trip_id", "stop_id", "stop_sequence",
              "arrival_time", "departure_time"], stop_time_rows)
    write_csv(OUT_DIR / "shapes.txt", ["shape_id", "shape_pt_lat", "shape_pt_lon",
              "shape_pt_sequence"], shape_rows)
    write_csv(OUT_DIR / "frequencies.txt", ["trip_id", "start_time", "end_time",
              "headway_secs"], frequency_rows)
    write_csv(OUT_DIR / "calendar.txt", ["service_id", "monday", "tuesday", "wednesday",
              "thursday", "friday", "saturday", "sunday", "start_date", "end_date"], calendar_rows)

    with (OUT_DIR / "feed_info.txt").open("w", newline="") as fh:
        fh.write("feed_publisher_name,feed_publisher_url,feed_lang\n")
        fh.write("ColombiaTransit,https://github.com/ColombiaTransit,es\n")

    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in OUT_DIR.glob("*.txt"):
            zf.write(f, f.name)

    print(f"\nBuilt {ZIP_PATH}: {len(route_rows)} route(s), {len(stop_rows)} stop(s), "
          f"{len(trip_rows)} trip(s), {len(frequency_rows)} frequency row(s).")


if __name__ == "__main__":
    main()
