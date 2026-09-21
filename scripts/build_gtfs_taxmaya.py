#!/usr/bin/env python3
"""
Build a GTFS feed for Tax Maya from real official government data:
route/stop geometry from Medellín's ArcGIS layers (raw/medellin_raw/,
current), and real frequency/schedule data from Gaceta Oficial N°4325
(data/taxmaya_route_mapping.yml, transcribed from official "FICHA
TÉCNICA" pages - see the conversation this came from for the source
document and full verification).

WHY frequencies.txt, not individual trips: unlike TRSC/Coonatra (built
from literal PDF departure times), the Gaceta gives real HEADWAY data
(minutes between buses) plus a service start/end time - the correct
GTFS primitive for that shape of data is frequencies.txt, not one row
per trip. Only the "DÍA" (general/normal) headway is used, not "HMD"
(likely peak-hour) - see data/taxmaya_route_mapping.yml's docstring for
why: the source doesn't give clock-time boundaries for when peak hours
apply, and guessing them isn't this project's practice.

SERVICE PATTERN: 3 real weekly service days are built (weekday,
Saturday, Sunday) via calendar.txt. "Festivo" (holidays) is NOT built
as a separate service - it would need calendar_dates.txt with actual
Colombian holiday dates, which isn't available, and its real values
matched Sunday's exactly in every route observed anyway.

GEOMETRY: same per-direction ArcGIS approach validated for TRSC and
Coonatra - each route has 2 directional records (Origen-Destino /
Destino-Origen) with genuinely different geometry, stops are matched
per direction, real addresses used as stop names (Tax Maya's ArcGIS
stops don't have a populated 'nombre' field, confirmed same as most
operators' Paradas layer 5 records - direccion is the reliable
fallback, same conclusion reached for TRSC).

Usage: python scripts/build_gtfs_taxmaya.py
Requires: raw/medellin_raw/vc_transporte_rutas.json and
          vc_transporte_parada.json (run
          scripts/download_medellin_transporte_layers.py first)
          data/taxmaya_route_mapping.yml
Output: gtfs-taxmaya.zip
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
MAPPING_PATH = Path("data/taxmaya_route_mapping.yml")

OUT_DIR = Path("gtfs-taxmaya-out")
ZIP_PATH = Path("gtfs-taxmaya.zip")

AVERAGE_SPEED_KMH = 18  # ASSUMED, same figure used elsewhere in this project - not
                         # needed for shapes here (frequencies.txt doesn't need per-
                         # stop times), kept only if a future stop_times build is added
SUSPICIOUS_SNAP_DIST_M = 150
CRS_TRANSFORMER = Transformer.from_crs("EPSG:9377", "EPSG:4326", always_xy=True)


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


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
    """Formats a relative offset (seconds from a trip's own 00:00:00
    base) as HH:MM:SS - used for frequency-based trips' stop_times,
    which are relative timing templates, not real clock times."""
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


def load_taxmaya_arcgis_data():
    all_rutas = json.loads(RUTAS_PATH.read_text())
    all_parada = json.loads(PARADA_PATH.read_text())

    def is_taxmaya(attrs):
        empresa = attrs.get("empresa")
        return bool(empresa) and "MAYA" in strip_accents(empresa.upper())

    rutas_by_id_dir = {}
    for r in all_rutas:
        a = r["attributes"]
        if is_taxmaya(a):
            rutas_by_id_dir[(a["id_ruta"], a["recorrido"])] = r

    parada_by_id_dir = {}
    for p in all_parada:
        a = p["attributes"]
        if is_taxmaya(a):
            key = (str(a["id_ruta"]), a["recorrido"])
            parada_by_id_dir.setdefault(key, []).append(a)

    return rutas_by_id_dir, parada_by_id_dir


def main():
    for p in (RUTAS_PATH, PARADA_PATH, MAPPING_PATH):
        if not p.exists():
            print(f"{p} not found.", file=sys.stderr)
            sys.exit(1)

    mapping = yaml.safe_load(MAPPING_PATH.read_text())["routes"]
    arcgis_rutas, arcgis_parada = load_taxmaya_arcgis_data()
    print(f"Loaded ArcGIS data; building {len(mapping)} mapped route(s).")

    agency_rows = [{
        "agency_id": "taxmaya", "agency_name": "Tax Maya",
        "agency_url": "https://www.taxmaya.com", "agency_timezone": "America/Bogota",
        "agency_lang": "es",
    }]
    # 3 real weekly service patterns - see module docstring for why
    # "Festivo" isn't built as its own service.
    calendar_rows = [
        {"service_id": "DiaHabil", "monday": 1, "tuesday": 1, "wednesday": 1,
         "thursday": 1, "friday": 1, "saturday": 0, "sunday": 0,
         "start_date": "20260101", "end_date": "20271231"},
        {"service_id": "Sabado", "monday": 0, "tuesday": 0, "wednesday": 0,
         "thursday": 0, "friday": 0, "saturday": 1, "sunday": 0,
         "start_date": "20260101", "end_date": "20271231"},
        {"service_id": "Domingo", "monday": 0, "tuesday": 0, "wednesday": 0,
         "thursday": 0, "friday": 0, "saturday": 0, "sunday": 1,
         "start_date": "20260101", "end_date": "20271231"},
    ]

    route_rows, stop_rows, trip_rows, shape_rows, frequency_rows, stop_time_rows = [], [], [], [], [], []
    suspicious_stops, skipped = [], []
    day_service_map = [("dia_normal", "DiaHabil"), ("sabado", "Sabado"), ("domingo", "Domingo")]

    for route_cfg in mapping:
        id_ruta = route_cfg["id_ruta"]
        route_id = f"taxmaya_{id_ruta}"
        route_rows.append({
            "route_id": route_id, "agency_id": "taxmaya",
            "route_short_name": route_cfg["codigo_pdf"],
            "route_long_name": route_cfg["nombre"], "route_type": 3,
        })

        n_trips_built = 0
        for recorrido, dir_suffix in [("Origen-Destino", "OD"), ("Destino-Origen", "DO")]:
            route_rec = arcgis_rutas.get((id_ruta, recorrido))
            dir_stops = arcgis_parada.get((id_ruta, recorrido), [])
            if not route_rec:
                print(f"  WARNING: no {recorrido} ArcGIS geometry for "
                      f"{route_cfg['codigo_pdf']!r} (id_ruta={id_ruta}) - "
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
                print(f"  WARNING: no {recorrido} stops for {route_cfg['codigo_pdf']!r} "
                      f"(id_ruta={id_ruta}) - shape only, no stop_times/trips for this "
                      f"direction", file=sys.stderr)
                continue

            for s in ordered_stops:
                stop_rows.append({"stop_id": s["stop_id"], "stop_name": s["name"],
                                   "stop_lat": s["lat"], "stop_lon": s["lon"]})

            total_len_m = sum(
                sqrt((line_xy[i + 1][0] - line_xy[i][0]) ** 2 + (line_xy[i + 1][1] - line_xy[i][1]) ** 2)
                for i in range(len(line_xy) - 1)
            )
            running_time_s = total_len_m / (AVERAGE_SPEED_KMH * 1000 / 3600)

            # One trip + one frequencies.txt row per real weekly service
            # day, using the PDF's real "DÍA" (normal) headway and real
            # service start/end clock time. GTFS requires stop_times.txt
            # even for frequency-based trips - it defines the template
            # stop sequence/relative timing that frequencies.txt then
            # repeats every headway_secs from start_time to end_time, so
            # every trip still gets a full stop_times block, all
            # starting from the same 00:00:00 base (a frequency-based
            # trip's stop_times are relative, not real clock times).
            for day_key, service_id in day_service_map:
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
                headway_min = route_cfg["headway_min"][day_key]
                frequency_rows.append({
                    "trip_id": trip_id,
                    "start_time": route_cfg["horario_inicio"],
                    "end_time": route_cfg["horario_fin"],
                    "headway_secs": headway_min * 60,
                })
                n_trips_built += 1

        print(f"  {route_cfg['codigo_pdf']} ({route_cfg['nombre']}): "
              f"{n_trips_built} frequency-based trip(s) built")

    if suspicious_stops:
        print(f"\n{len(suspicious_stops)} stop(s) more than {SUSPICIOUS_SNAP_DIST_M}m "
              f"from their route's line (not relocated in this build - flagged only):",
              file=sys.stderr)
        for route_id, name, dist in suspicious_stops[:20]:
            print(f"  {route_id}: {name!r} - {dist}m", file=sys.stderr)

    OUT_DIR.mkdir(exist_ok=True)
    write_csv(OUT_DIR / "agency.txt", ["agency_id", "agency_name", "agency_url",
              "agency_timezone", "agency_lang"], agency_rows)
    write_csv(OUT_DIR / "routes.txt", ["route_id", "agency_id", "route_short_name",
              "route_long_name", "route_type"], route_rows)
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
          f"{len(trip_rows)} trip(s), {len(stop_time_rows)} stop_time row(s), "
          f"{len(frequency_rows)} frequency row(s).")


if __name__ == "__main__":
    main()
