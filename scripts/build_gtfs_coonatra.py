#!/usr/bin/env python3
"""
Build a GTFS feed for Coonatra from real scraped data: KML geometry
(+ real stop points, where they exist), real per-trip departure times
from the Calasanz-Boston frequencies PDF, and - new - real official
government stop/route data from Medellín's ArcGIS layers (raw/
medellin_raw/, via scripts/download_medellin_transporte_layers.py) for
branches that had no real stops from KML alone.

SCOPE OF THIS BUILD - the 5 Calasanz-Boston branches with a confident
mapping to real PDF departure-time data (see BRANCH_TO_PDF_HEADER):
  - "310", "311": REAL surveyed stop points from KML (35 and 44
    respectively, real named Medellin landmarks) + real per-trip PDF
    departure times -> GENUINE regular GTFS, KML-sourced.
  - "310 Rosal": previously flex-only (line-only KML geometry, no real
    stops) - NOW built as genuine stop-based GTFS instead, using real
    official stops from Medellín's ArcGIS "Parada de transporte
    publico" layer (id_ruta=90363, codigo "310R", nombre "Rosales" -
    a confident name match: "310" + "Rosales"/"Rosal" mirrors this
    branch's own name closely). 39 real stops, split by direction like
    every ArcGIS-sourced route in this project (see
    scripts/build_gtfs_trsc.py's docstring for the full technical
    detail on the CRS transform and per-direction split this relies
    on - identical technique reused here). Real PDF departure times
    (from BRANCH_TO_PDF_HEADER, unchanged) are applied to BOTH
    directions equally, the same direction-symmetry assumption used
    for TRSC, since the PDF gives one time list, not one per direction.
  - "310 Metro Rosal", "Metro 311-i": still line-only geometry (no
    stop points anywhere, KML or ArcGIS) + real per-trip departure
    times -> built as GTFS-Flex (same pickup/drop-off-window pattern
    validated for Sotrames), with ONE NARROW-WINDOW FLEX TRIP PER REAL
    DEPARTURE TIME rather than an all-day window.

NOT YET ENHANCED, pending further investigation - real ArcGIS data
exists for a "311i"/"311ii"/"311iiR" route family that plausibly
corresponds to "Metro 311-i"/"310 Metro Rosal"/"Metro 311-ii", but
which specific official route matches which branch name was NOT
confidently resolved (unlike "310 Rosal", where the name match was
clear) - attaching the wrong stops to the wrong branch would be worse
than leaving them as flex. Also not yet touched: Floresta-San Juan
(242/243 Divisa/Quiebra, still no frequency data anywhere) and Circular
Coonatra (300/301/303, still genuinely ambiguous) - both now have
confirmed real ArcGIS matches too, but adding them is separate work.

DELIBERATELY EXCLUDED from this version, pending a decision, not
because of a bug:
  - "Metro 311-ii": its KML's internal placemark name ("RUTA 311ii
    Rosales") doesn't match any of the 6 PDF table headers the way
    every other branch's does - see BRANCH_TO_PDF_HEADER. Building
    trips from a guessed PDF table risks attributing real departure
    times to the wrong route.

VALIDATED: output run through MobilityData's real gtfs-validator-cli -
see the conversation this script came from for the actual result; if
that predates changes made since, re-run validation before trusting a
new build blindly.
"""

import csv
import json
import sys
import unicodedata
import zipfile
from math import atan2, cos, radians, sin, sqrt
from pathlib import Path
from xml.etree import ElementTree as ET

import yaml
from pyproj import Transformer

ROUTES_PATH = Path("raw/coonatra_routes.json")
KML_DIR = Path("raw/coonatra_kml")
PDF_JSON_PATH = Path("raw/coonatra_pdf_Frecuencias-rutas-Calasanz.json")
ARCGIS_RUTAS_PATH = Path("raw/medellin_raw/vc_transporte_rutas.json")
ARCGIS_PARADA_PATH = Path("raw/medellin_raw/vc_transporte_parada.json")
OUT_DIR = Path("gtfs-coonatra-out")
ZIP_PATH = Path("gtfs-coonatra.zip")

KML_NS = {"kml": "http://www.opengis.net/kml/2.2"}
SUSPICIOUS_SNAP_DIST_M = 150  # stops farther than this from the line are flagged, not dropped
AVERAGE_SPEED_KMH = 18  # ASSUMED, same figure used elsewhere in this project
CORRIDOR_BUFFER_M = 40  # ASSUMED flex-zone half-width, same as the Sotrames/El Poblado builders
CRS_TRANSFORMER = Transformer.from_crs("EPSG:9377", "EPSG:4326", always_xy=True)

# Branch name -> its matching PDF table header, established by name AND
# by cross-checking each branch's real KML internal placemark name
# against the PDF headers (see module docstring). "Metro 311-ii" is
# deliberately absent - see module docstring for why.
BRANCH_TO_PDF_HEADER = {
    "310": "Ruta 310 Directo Calasanz Boston",
    "311": "Ruta 311 Calasanz Boston",
    "310 Rosal": "Ruta 310 Rosal",
    "310 Metro Rosal": "Ruta 310 Metro Rosal",
    "Metro 311-i": "Ruta 311 Metro",
}

# Branches with real stop points from KML, confirmed via
# raw/coonatra_kml_summary.json
STOP_BASED_BRANCHES = {"310", "311"}

# Branch name -> its real official id_ruta in Medellín's ArcGIS data.
# "310 Rosal": confident name match ("310" + "Rosales"/"Rosal").
# "Metro 311-ii": confirmed via its KML's internal placemark name
# ("RUTA 311ii Rosales") structurally decomposing into the official
# codigo "311iiR" (311ii + R for Rosales) - not just a similar-sounding
# name, the code literally spells out the KML name. This resolves its
# STOP/GEOMETRY identity, but NOT its PDF departure-time header - that
# question (see BRANCH_TO_PDF_HEADER's absence of this branch) is
# still separately unresolved, so this branch gets real stops/shape
# but no trips yet, same "don't fabricate a schedule" policy used for
# TRSC's routes without a transcribed schedule photo.
# "Metro 311-i": KML-internal name ("311 METRO") was genuinely
# ambiguous between official "311i" (Santa Lucia, 23 stops) and "311ii"
# (Santa Lucia Directa, 15 stops) - resolved by the project owner's own
# judgment to "311i", not independently re-derived here.
ARCGIS_STOP_BASED_BRANCHES = {
    "310 Rosal": "90363", "Metro 311-ii": "90361", "Metro 311-i": "90324",
}

FLEX_BRANCHES = {"310 Metro Rosal"}

# Floresta-San Juan (from the CONTÁCTENOS page, confirmed clean 4/4/4
# match) - real KML stops already existed (4-22 points), but this
# family was deliberately never built: no frequency/schedule data
# exists anywhere for it, not on the website, not in any PDF. Real
# ArcGIS data doesn't solve that either (Parada layer has no
# schedule field at all) - built here as spatial-data-only (stops +
# shape, no trips), the same policy as Metro 311-ii. Website branch
# name -> official id_ruta, matched by codigo (242/243) + nombre
# ("La Divisa"/"La Quiebra") - a direct, unambiguous match.
FLORESTA_SAN_JUAN_ROUTES = {
    "242 Divisa": "90318", "242 Quiebra": "90319",
    "243 Divisa": "90320", "243 Quiebra": "90321",
}

# Circular Coonatra - the corresponding trscsas... no, coonatra.com
# page was genuinely ambiguous (6 names, 2 schedules, 3 mids -
# couldn't cleanly pair them, see the conversation this came from).
# Built here DIRECTLY from the official ArcGIS data instead of the
# website's tangled pairing - route identity (codigo, nombre) comes
# straight from Medellín's government registry, bypassing the
# website ambiguity entirely. Also spatial-data-only: no schedule
# source has ever been resolved for this family either.
CIRCULAR_COONATRA_ROUTES = {
    "300": ("90005", "Circular"),
    "301": ("90006", "Circular"),
    "303": ("90001", "Circular Horario 303"),
    "300 DIR-80": ("90367", "Circular (via Carrera 80)"),
    "301 DIR-80": ("90369", "Circular (via Carrera 80)"),
}

FIELDNAMES = {
    "agency.txt": ["agency_id", "agency_name", "agency_url", "agency_timezone", "agency_lang"],
    "routes.txt": ["route_id", "agency_id", "route_short_name", "route_long_name", "route_type"],
    "stops.txt": ["stop_id", "stop_name", "stop_lat", "stop_lon"],
    "trips.txt": ["route_id", "service_id", "trip_id"],
    "stop_times_regular": ["trip_id", "stop_id", "stop_sequence", "arrival_time", "departure_time"],
    "stop_times_flex": ["trip_id", "stop_sequence", "location_id",
                         "start_pickup_drop_off_window", "end_pickup_drop_off_window",
                         "pickup_type", "drop_off_type"],
    "calendar.txt": ["service_id", "monday", "tuesday", "wednesday", "thursday",
                      "friday", "saturday", "sunday", "start_date", "end_date"],
}


def write_csv(path: Path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_kml(path: Path):
    """Returns (line_coords [[lon,lat],...] or None, points [{name,lon,lat},...])."""
    root = ET.fromstring(path.read_bytes())
    placemarks = root.findall(".//kml:Placemark", KML_NS)
    line_coords, points = None, []
    for p in placemarks:
        name_el = p.find("kml:name", KML_NS)
        name = name_el.text if name_el is not None else None
        ls = p.find("kml:LineString/kml:coordinates", KML_NS)
        if ls is not None and ls.text:
            coords = []
            for tok in ls.text.split():
                lon, lat, *_ = tok.split(",")
                coords.append((float(lon), float(lat)))
            line_coords = coords
        pt = p.find("kml:Point/kml:coordinates", KML_NS)
        if pt is not None and pt.text:
            lon, lat, *_ = pt.text.strip().split(",")
            points.append({"name": name, "lon": float(lon), "lat": float(lat)})
    return line_coords, points


def to_xy(lon, lat, lat0):
    m_per_deg_lat = 111_320.0
    m_per_deg_lon = 111_320.0 * cos(radians(lat0))
    return lon * m_per_deg_lon, lat * m_per_deg_lat


def to_lon_lat(x, y, lat0):
    m_per_deg_lat = 111_320.0
    m_per_deg_lon = 111_320.0 * cos(radians(lat0))
    return x / m_per_deg_lon, y / m_per_deg_lat


def project_point_to_line(px, py, line_xy):
    """Nearest-point projection: returns (distance along the line to the
    nearest point, perpendicular snap distance, the projected point's
    own (x,y)). Verified against real Calasanz-Boston 310 data -
    produces a sensible landmark ordering."""
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


def buffer_line_to_polygon(line_coords, buffer_m):
    from shapely.geometry import LineString
    lat0 = sum(lat for _, lat in line_coords) / len(line_coords)
    line_xy = [to_xy(lon, lat, lat0) for lon, lat in line_coords]
    poly = LineString(line_xy).buffer(buffer_m, cap_style="round", join_style="round")
    return [to_lon_lat(x, y, lat0) for x, y in poly.exterior.coords]


def add_seconds(hhmmss: str, seconds: float) -> str:
    h, m, s = (int(x) for x in hhmmss.split(":"))
    total = h * 3600 + m * 60 + s + round(seconds)
    h2, rem = divmod(total, 3600)
    m2, s2 = divmod(rem, 60)
    return f"{h2:02d}:{m2:02d}:{s2:02d}"


def safe_filename(s: str) -> str:
    import re
    return re.sub(r"[^\w\-]+", "_", s).strip("_")


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def load_coonatra_arcgis_data():
    """Loads and filters Medellín's official ArcGIS Rutas/Parada layers
    for Coonatra records only. Returns (rutas_by_id_dir, parada_by_id_dir)
    dicts keyed by (id_ruta: str, recorrido: str)."""
    if not ARCGIS_RUTAS_PATH.exists() or not ARCGIS_PARADA_PATH.exists():
        return {}, {}

    all_rutas = json.loads(ARCGIS_RUTAS_PATH.read_text())
    all_parada = json.loads(ARCGIS_PARADA_PATH.read_text())

    def is_coonatra(attrs):
        empresa = attrs.get("empresa")
        return bool(empresa) and "COONATRA" in strip_accents(empresa.upper())

    rutas_by_id_dir = {}
    for r in all_rutas:
        a = r["attributes"]
        if is_coonatra(a):
            rutas_by_id_dir[(a["id_ruta"], a["recorrido"])] = r

    parada_by_id_dir = {}
    for p in all_parada:
        a = p["attributes"]
        if is_coonatra(a):
            key = (str(a["id_ruta"]), a["recorrido"])
            parada_by_id_dir.setdefault(key, []).append(a)

    return rutas_by_id_dir, parada_by_id_dir


def build_arcgis_stop_route(route_id, id_ruta, pdf_times, arcgis_rutas, arcgis_parada, suspicious_stops):
    """Builds stop_rows/trip_rows/stop_time_rows_regular for one route,
    both directions, from real Medellín ArcGIS data. pdf_times may be
    empty - real stops/shape are built regardless (spatial-data-only
    policy), trips only when pdf_times is non-empty. Same
    direction-symmetry assumption used throughout this project: one
    departure-time list applied to both directions equally, since none
    of this project's data sources give separate times per direction.
    Returns (stop_rows, trip_rows, stop_time_rows, n_trips_built)."""
    stop_rows, trip_rows, stop_time_rows = [], [], []
    n_trips_built = 0

    for recorrido, dir_suffix in [("Origen-Destino", "OD"), ("Destino-Origen", "DO")]:
        route_rec = arcgis_rutas.get((id_ruta, recorrido))
        dir_stops = arcgis_parada.get((id_ruta, recorrido), [])
        if not route_rec or not dir_stops:
            print(f"  WARNING: no {recorrido} ArcGIS geometry/stops for "
                  f"{route_id!r} (id_ruta={id_ruta}) - skipping this direction",
                  file=sys.stderr)
            continue

        raw_path = route_rec["geometry"]["paths"][0]
        line_lonlat = [CRS_TRANSFORMER.transform(x, y) for x, y in raw_path]
        lat0 = sum(lat for _, lat in line_lonlat) / len(line_lonlat)
        line_xy = [to_xy(lon, lat, lat0) for lon, lat in line_lonlat]
        total_len_m = line_length_m(line_xy)
        running_time_s = total_len_m / (AVERAGE_SPEED_KMH * 1000 / 3600)

        ordered = []
        for s in sorted(dir_stops, key=lambda a: a.get("nro_parada", 0)):
            px, py = to_xy(s["longitud"], s["latitud"], lat0)
            dist_along, snap_dist, _ = project_point_to_line(px, py, line_xy)
            if snap_dist > SUSPICIOUS_SNAP_DIST_M:
                suspicious_stops.append((route_id, s.get("direccion"), round(snap_dist)))
            # nro_parada can have genuine duplicates (two different real
            # stops sharing one number) or decimals (inserted stops) -
            # objectid is included as a tiebreaker to guarantee a unique
            # stop_id while keeping it traceable to the real source value.
            nro_str = str(s["nro_parada"]).replace(".", "_")
            stop_id = f"{route_id}_{dir_suffix}_{nro_str}_{s['objectid']}"
            ordered.append({"stop_id": stop_id, "name": s.get("direccion") or stop_id,
                             "lat": s["latitud"], "lon": s["longitud"], "dist_along": dist_along})
        ordered.sort(key=lambda x: x["dist_along"])

        for s in ordered:
            stop_rows.append({"stop_id": s["stop_id"], "stop_name": s["name"],
                               "stop_lat": s["lat"], "stop_lon": s["lon"]})

        for trip_idx, dep_time in enumerate(pdf_times):
            trip_id = f"{route_id}_{dir_suffix}_{trip_idx}"
            trip_rows.append({"route_id": route_id, "service_id": "Diario", "trip_id": trip_id})
            for seq, s in enumerate(ordered):
                fraction = s["dist_along"] / total_len_m if total_len_m > 0 else 0
                t = add_seconds(dep_time, running_time_s * fraction)
                stop_time_rows.append({
                    "trip_id": trip_id, "stop_id": s["stop_id"], "stop_sequence": seq,
                    "arrival_time": t, "departure_time": t,
                })
            n_trips_built += 1

    return stop_rows, trip_rows, stop_time_rows, n_trips_built


def main():
    for p in (ROUTES_PATH, PDF_JSON_PATH):
        if not p.exists():
            print(f"{p} not found - run the Coonatra scrape/KML/PDF scripts first.",
                  file=sys.stderr)
            sys.exit(1)

    pages = json.loads(ROUTES_PATH.read_text())
    pdf_tables = json.loads(PDF_JSON_PATH.read_text())
    pdf_by_header = {t["header"]: t for t in pdf_tables}

    calasanz = next((p for p in pages if p["title"] == "Calasanz-Boston"), None)
    if not calasanz or not calasanz.get("branches"):
        print("Calasanz-Boston page not found or not a clean match in "
              f"{ROUTES_PATH} - nothing to build.", file=sys.stderr)
        sys.exit(1)

    branches_by_name = {b["name"]: b for b in calasanz["branches"]}
    arcgis_rutas, arcgis_parada = load_coonatra_arcgis_data()
    if ARCGIS_STOP_BASED_BRANCHES and not arcgis_rutas:
        print(f"NOTE: {ARCGIS_RUTAS_PATH} / {ARCGIS_PARADA_PATH} not found - "
              f"ArcGIS-sourced branch(es) {list(ARCGIS_STOP_BASED_BRANCHES)} will be "
              f"skipped. Run scripts/download_medellin_transporte_layers.py first "
              f"if this is unexpected.", file=sys.stderr)

    agency_rows = [{
        "agency_id": "coonatra", "agency_name": "Coonatra",
        "agency_url": "https://coonatra.com", "agency_timezone": "America/Bogota",
        "agency_lang": "es",
    }]
    calendar_rows = [{
        "service_id": "Diario", "monday": 1, "tuesday": 1, "wednesday": 1,
        "thursday": 1, "friday": 1, "saturday": 1, "sunday": 1,
        "start_date": "20260101", "end_date": "20271231",
    }]

    route_rows, stop_rows, trip_rows = [], [], []
    stop_time_rows_regular, stop_time_rows_flex = [], []
    location_features = []
    suspicious_stops, skipped = [], []

    all_target_branches = STOP_BASED_BRANCHES | FLEX_BRANCHES | set(ARCGIS_STOP_BASED_BRANCHES)
    for name in sorted(all_target_branches):
        branch = branches_by_name.get(name)
        if not branch:
            skipped.append((name, "not found in coonatra_routes.json"))
            continue

        pdf_header = BRANCH_TO_PDF_HEADER.get(name)
        pdf_times = pdf_by_header.get(pdf_header, {}).get("concatenated", []) if pdf_header else []

        if name in ARCGIS_STOP_BASED_BRANCHES:
            # Real stops/shape don't require a resolved PDF header - only
            # trips do. A branch like "Metro 311-ii" can have a confirmed
            # stop/geometry identity while its schedule question stays
            # separately unresolved (see ARCGIS_STOP_BASED_BRANCHES'
            # comment) - built as spatial-data-only when pdf_times is
            # empty, same policy as TRSC's untranscribed-schedule routes.
            if not pdf_times:
                print(f"  NOTE: {name!r} has no resolved PDF header - building "
                      f"real stops/shape only, no trips.", file=sys.stderr)

            id_ruta = ARCGIS_STOP_BASED_BRANCHES[name]
            route_id = name.replace(" ", "_")
            route_rows.append({
                "route_id": route_id, "agency_id": "coonatra",
                "route_short_name": name,
                "route_long_name": f"Calasanz-Boston - Ruta {name}",
                "route_type": 3,
            })

            new_stops, new_trips, new_stop_times, n_trips_built = build_arcgis_stop_route(
                route_id, id_ruta, pdf_times, arcgis_rutas, arcgis_parada, suspicious_stops
            )
            stop_rows.extend(new_stops)
            trip_rows.extend(new_trips)
            stop_time_rows_regular.extend(new_stop_times)

            print(f"  {name}: {n_trips_built} trip(s) built (stop-based, ArcGIS-sourced)")
            continue

        if not pdf_times:
            skipped.append((name, f"no PDF departure times found for header {pdf_header!r}"))
            continue

        kml_path = KML_DIR / f"Calasanz-Boston__{safe_filename(name)}.kml"
        if not kml_path.exists():
            skipped.append((name, f"KML file not found: {kml_path}"))
            continue
        line_coords, points = parse_kml(kml_path)
        if not line_coords or len(line_coords) < 2:
            skipped.append((name, "no usable line geometry in KML"))
            continue

        route_id = name.replace(" ", "_")
        route_rows.append({
            "route_id": route_id, "agency_id": "coonatra",
            "route_short_name": name,
            # Was accidentally using days_text (schedule days, e.g.
            # "Lunes a sábado") here, which was empty for these branches
            # and fell back to just repeating `name` - triggering GTFS
            # validator's route_long_name_contains_short_name warning
            # for a genuinely wrong reason. No separate route
            # description field exists in the scraped data, so build a
            # real, distinct long name from the page's route-family
            # title plus this branch's identifier instead.
            "route_long_name": f"Calasanz-Boston - Ruta {name}",
            "route_type": 3,
        })

        if name in STOP_BASED_BRANCHES:
            lat0 = sum(lat for _, lat in line_coords) / len(line_coords)
            line_xy = [to_xy(lon, lat, lat0) for lon, lat in line_coords]
            total_len_m = line_length_m(line_xy)
            running_time_s = total_len_m / (AVERAGE_SPEED_KMH * 1000 / 3600)

            ordered_stops = []
            relocated = []
            for pt in points:
                px, py = to_xy(pt["lon"], pt["lat"], lat0)
                dist_along, snap_dist, (proj_x, proj_y) = project_point_to_line(px, py, line_xy)
                lat, lon = pt["lat"], pt["lon"]
                if snap_dist > SUSPICIOUS_SNAP_DIST_M:
                    suspicious_stops.append((route_id, pt["name"], round(snap_dist)))
                    # This point is a landmark near the route, not the
                    # actual on-road stop location (confirmed for "Metro
                    # Estación San Antonio" - its raw coordinate is the
                    # station building, ~296m from the road the bus
                    # actually runs on). Use the projected point ON the
                    # line instead of the raw landmark coordinate, for
                    # every stop this far off, not just that one - the
                    # same landmark-vs-road-stop issue likely affects
                    # all of them equally.
                    lon, lat = to_lon_lat(proj_x, proj_y, lat0)
                    relocated.append(pt["name"])
                stop_id = f"{route_id}_{safe_filename(pt['name'] or 'stop')}_{len(ordered_stops)}"
                ordered_stops.append({"stop_id": stop_id, "name": pt["name"],
                                       "lat": lat, "lon": lon, "dist_along": dist_along})
            ordered_stops.sort(key=lambda s: s["dist_along"])
            if relocated:
                print(f"    relocated {len(relocated)} landmark-style stop(s) onto "
                      f"the route line: {relocated}")

            for s in ordered_stops:
                stop_rows.append({"stop_id": s["stop_id"], "stop_name": s["name"] or s["stop_id"],
                                   "stop_lat": s["lat"], "stop_lon": s["lon"]})

            for trip_idx, dep_time in enumerate(pdf_times):
                trip_id = f"{route_id}_{trip_idx}"
                trip_rows.append({"route_id": route_id, "service_id": "Diario", "trip_id": trip_id})
                for seq, s in enumerate(ordered_stops):
                    fraction = s["dist_along"] / total_len_m if total_len_m > 0 else 0
                    t = add_seconds(dep_time, running_time_s * fraction)
                    stop_time_rows_regular.append({
                        "trip_id": trip_id, "stop_id": s["stop_id"], "stop_sequence": seq,
                        "arrival_time": t, "departure_time": t,
                    })

        else:  # FLEX_BRANCHES
            polygon_coords = buffer_line_to_polygon(line_coords, CORRIDOR_BUFFER_M)
            location_features.append({
                "type": "Feature", "id": route_id, "properties": {"name": name},
                "geometry": {"type": "Polygon", "coordinates": [
                    [[round(lon, 6), round(lat, 6)] for lon, lat in polygon_coords]
                ]},
            })
            for trip_idx, dep_time in enumerate(pdf_times):
                trip_id = f"{route_id}_{trip_idx}"
                trip_rows.append({"route_id": route_id, "service_id": "Diario", "trip_id": trip_id})
                # Narrow window right at the real departure time (+-2 min
                # buffer) - NOT an all-day window like Sotrames/El Poblado,
                # since we have real per-trip precision here, not just hours.
                window_start = add_seconds(dep_time, -120)
                window_end = add_seconds(dep_time, 120)
                stop_time_rows_flex.append({
                    "trip_id": trip_id, "stop_sequence": 0, "location_id": route_id,
                    "start_pickup_drop_off_window": window_start,
                    "end_pickup_drop_off_window": window_end,
                    "pickup_type": 2, "drop_off_type": 1,
                })
                stop_time_rows_flex.append({
                    "trip_id": trip_id, "stop_sequence": 1, "location_id": route_id,
                    "start_pickup_drop_off_window": window_start,
                    "end_pickup_drop_off_window": window_end,
                    "pickup_type": 1, "drop_off_type": 2,
                })

        print(f"  {name}: {len(pdf_times)} trip(s) built "
              f"({'stop-based' if name in STOP_BASED_BRANCHES else 'flex'})")

    print("\nFloresta-San Juan (spatial data only - no schedule source exists):")
    for name, id_ruta in FLORESTA_SAN_JUAN_ROUTES.items():
        route_id = f"floresta_{name.replace(' ', '_')}"
        route_rows.append({
            "route_id": route_id, "agency_id": "coonatra",
            "route_short_name": name, "route_long_name": f"Floresta-San Juan - {name}",
            "route_type": 3,
        })
        new_stops, new_trips, new_stop_times, n_trips_built = build_arcgis_stop_route(
            route_id, id_ruta, [], arcgis_rutas, arcgis_parada, suspicious_stops
        )
        stop_rows.extend(new_stops)
        print(f"  {name}: {len(new_stops)} real stop(s), 0 trip(s) (no schedule)")

    print("\nCircular Coonatra (spatial data only - no schedule source resolved; "
          "route identity from official ArcGIS data directly, bypassing the "
          "website's genuinely ambiguous page):")
    for name, (id_ruta, nombre) in CIRCULAR_COONATRA_ROUTES.items():
        route_id = f"circular_{name.replace(' ', '_')}"
        route_rows.append({
            "route_id": route_id, "agency_id": "coonatra",
            "route_short_name": name, "route_long_name": f"{nombre} {name}",
            "route_type": 3,
        })
        new_stops, new_trips, new_stop_times, n_trips_built = build_arcgis_stop_route(
            route_id, id_ruta, [], arcgis_rutas, arcgis_parada, suspicious_stops
        )
        stop_rows.extend(new_stops)
        print(f"  {name}: {len(new_stops)} real stop(s), 0 trip(s) (no schedule)")

    if skipped:
        print(f"\nSKIPPED {len(skipped)} branch(es):", file=sys.stderr)
        for name, reason in skipped:
            print(f"  {name}: {reason}", file=sys.stderr)

    if suspicious_stops:
        print(f"\nNOTE: {len(suspicious_stops)} stop(s) were more than "
              f"{SUSPICIOUS_SNAP_DIST_M}m from their route's line (landmark "
              f"points, not on-road stop locations - e.g. a metro station "
              f"building, not the actual street the bus runs on). Their "
              f"stop_lat/stop_lon were RELOCATED onto the nearest point on "
              f"the route line rather than left at the landmark's real "
              f"position:", file=sys.stderr)
        for route_id, name, dist in suspicious_stops:
            print(f"  {route_id}: {name!r} - was {dist}m from the line", file=sys.stderr)

    OUT_DIR.mkdir(exist_ok=True)
    write_csv(OUT_DIR / "agency.txt", FIELDNAMES["agency.txt"], agency_rows)
    write_csv(OUT_DIR / "routes.txt", FIELDNAMES["routes.txt"], route_rows)
    write_csv(OUT_DIR / "stops.txt", FIELDNAMES["stops.txt"], stop_rows)
    write_csv(OUT_DIR / "trips.txt", FIELDNAMES["trips.txt"], trip_rows)
    write_csv(OUT_DIR / "calendar.txt", FIELDNAMES["calendar.txt"], calendar_rows)

    # stop_times.txt needs BOTH regular (stop_id-based) and flex
    # (location_id-based) rows in the SAME file, per GTFS-Flex spec -
    # union the fieldnames, missing fields left blank per row.
    all_stop_time_fields = list(dict.fromkeys(
        FIELDNAMES["stop_times_regular"] + FIELDNAMES["stop_times_flex"]
    ))
    write_csv(OUT_DIR / "stop_times.txt", all_stop_time_fields,
              stop_time_rows_regular + stop_time_rows_flex)

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

    print(f"\nBuilt {ZIP_PATH}: {len(route_rows)} route(s), {len(stop_rows)} real stop(s), "
          f"{len(trip_rows)} trip(s).")


if __name__ == "__main__":
    main()
