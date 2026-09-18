#!/usr/bin/env python3
"""
Batch-download and inspect Sotrames' per-route Google My Maps as KML.

sotrames.com.co/rutas/ embeds one Google My Maps per route
(google.com/maps/d/embed?mid=<ID>). Google provides a standard KML
export for any public My Maps at:
    https://www.google.com/maps/d/kml?mid=<ID>&forcekml=1

Manually checking ONE of these (route "Veredales Pan de Azúcar") showed
real, detailed street-following geometry (735 lines of coordinates) but
ZERO stop markers - only a single LineString Placemark, no Points. This
script checks ALL of Sotrames' routes the same way, since that one
sample doesn't prove every route lacks stop data - the answer matters
for whether Sotrames' service has real fixed stops we just haven't
found yet (regular GTFS, stops added later) or genuinely has none
(GTFS-Flex might be the more honest model - see the exchange that led
to this script for that distinction).

This must be run somewhere with real internet access to google.com -
it was NOT run or verified in the environment that wrote it (no access
to fetch arbitrary URLs there).

Usage: python scripts/fetch_sotrames_kml.py
Output: raw/sotrames_kml/<route_name>.kml (every route's raw KML)
        raw/sotrames_kml_summary.json (per-route: has_points, num_points,
        num_line_points, line_length_km)
"""

import json
import re
import sys
import time
from pathlib import Path
from xml.etree import ElementTree as ET

import requests

# (route_name, mid) pairs, scraped from https://www.sotrames.com.co/rutas/
# on 2026-09-17. Re-scrape the page if this list needs updating - the
# route <-> mid pairing there is by visual proximity (route name heading
# immediately followed by its map embed), not a stable HTML anchor.
ROUTES = [
    ("Itaguí-Veredales_San_Jose", "1WnwrmObKcmwDxHvgDS4mY4BgjS1LlFSe"),
    ("Itaguí-Veredales_Pan_de_Azucar", "1D4xjWGwSWZiBaFpR_3zMC0YhObbLKsQI"),
    ("Itagui-Senorial", "1pMiOHhOfVVI1pwBgnShyljJ8-wRTy28k"),
    ("Ruta_1", "1YAyAePIVtuwnbxIkicMTS61rWjKWRRWl"),
    ("Ruta_2", "1VMYrAj9LgUIN_AagrcE8TtXO6yycahUO"),
    ("Rosellon_Flores_Modelo_2008_Superior_Junin", "1_cgppRt_t8YAJRwvEBgPBGba60F298jP"),
    ("Dorada_La_Paz_Vegas_San_Juan", "10r9PzDFJbJ4yEzwzoFLEltFs124cmPMm"),
    ("Maria_Auxiliadora", "1wrjcAblT-1QUG80sAlZDMJqR__x3rY13"),
    ("Estacion_Envigado-Chingui_2", "1xPl8AxXhf2Jx0r-DfNByL2Dv6VkkgHnT"),
    ("Estacion_Envigado-San_Arenales", "1zWHaTppqJYrL7CTMIMqf3zsAm4KBRPWq"),
    ("Estacion_Envigado-San_Rafael_a", "1-5tJuC4AeCz0Yvsb_pthq8c63jE6GW53"),
    ("Estacion_Envigado-Barrio_Nuevo", "1lZnJNVqBeA1a3USzz52kmryr5eapbor6"),
    ("Estacion_Envigado-El_Salado", "1sWvtdS4Zjft57acLRVRALcy0aQ0sa3WX"),
    ("Estacion_Envigado-Gualandayes", "1sWvtdS4Zjft57acLRVRALcy0aQ0sa3WX"),
    ("Estacion_Envigado-Catedral", "1I04WmqBPK5mxpaXOAG3ANu_KFur6MAKn"),
    ("Estacion_Envigado-La_Mina", "1jW2IbF7zRQZw9VoBO3Mkf3ZbdW62ue9D"),
    ("Estacion_Envigado-San_Rafael_b", "1ijnxra9o8Vuy9mHFNJLA6JgKhGo5Af_x"),
    ("Sabaneta_Vegas-Poblado_San_Juan", "1h1J-tNVNNKzjKFVI2_XDRROyoyOCTwXu"),
    ("Sabaneta_Vegas_Derecho_a", "1-rEWGuhU8_Z5KNYfxTai8QUlFBYQt3hP"),
    ("Sabaneta_Poblado_Vegas-Ejecutiva_a", "15SoEfG_3h84T8iMWqtj_kQAY9lQT8qXy"),
    ("Rosellon_Derecho_R_Vehiculos_2008_Junin", "1UjpWMTEjK1x-RmHbmkS8zvDLMDsQy3Is"),
    ("Rosellon_Derecho_R_San_Juan", "1mRBycCMLVCNM0hiMZ5WtS9hKkQ3KRLVR"),
    ("Dorado_La_Paz_Vegas", "10aX9WPPWHFY-HHjb8CXlq0bEe_78ZhPb"),
    ("La_Estrella_Sabaneta", "1m2eprts8NyTHrWVgeSlmb6GNmiQoipio"),
    ("La_Doctora_Ceramica", "1pPHM7AvA6kSBKm4mElMIlFRilkDmwPHq"),
    ("La_Doctora_San_Isidro", "1yuNSqj9HtyGjcGNO-3mdBIuCC-4qVa3G"),
    ("La_Doctora_Inmaculada", "11JaGbWsgrLbtoUHPMkjSqkMLj93DfKC5"),
    ("Veredales_Sabaneta_Aves_Maria_Monte_Carmelo", "1qQumQy-D5EnspSHwOBNXcJiOBoTblQQa"),
    ("Veredales_Sabaneta_San_Jose", "1sqpJQOjIJgK7ULWg5enQf0u58S5j0ZkK"),
    ("Sabaneta_Poblado_Vegas_Buses_a", "1eGGdBV3LLQrLQvRMnVBxhUeVgpmvmVsC"),
    ("Sabaneta_Vegas_Poblado_Buses", "1WRrhoywu0CkHg29yqvo_N7F_locoSXI_"),
    ("Dorado_La_Paz_Poblado_Cuenca", "1i2-cE2zI5I2u5BMEF10BTe-FmxkjMSA8"),
    ("Dorado_La_Paz_Poblado_Buses_Junin", "15ZojYfzHMTehpv1E-loKjeMgIW4xdDMz"),
    ("Circular_Sur_303", "1gzkZUz4IwdjCpehARhLvfqnQXJpY6Stb"),
]

KML_URL = "https://www.google.com/maps/d/kml?mid={mid}&forcekml=1"
OUT_DIR = Path("raw/sotrames_kml")
SUMMARY_PATH = Path("raw/sotrames_kml_summary.json")
KML_NS = {"kml": "http://www.opengis.net/kml/2.2"}


def inspect_kml(kml_bytes: bytes) -> dict:
    root = ET.fromstring(kml_bytes)
    placemarks = root.findall(".//kml:Placemark", KML_NS)

    points, lines = [], []
    for pm in placemarks:
        name_el = pm.find("kml:name", KML_NS)
        name = name_el.text if name_el is not None else "(unnamed)"
        if pm.find("kml:Point", KML_NS) is not None:
            coords = pm.find("kml:Point/kml:coordinates", KML_NS)
            points.append({"name": name, "coordinates": coords.text.strip() if coords is not None else None})
        line_el = pm.find("kml:LineString/kml:coordinates", KML_NS)
        if line_el is not None:
            coords = [c for c in line_el.text.split() if c]
            lines.append({"name": name, "num_points": len(coords)})

    return {
        "num_placemarks": len(placemarks),
        "num_point_placemarks": len(points),  # >0 means real stop markers exist!
        "point_placemarks": points,
        "num_line_placemarks": len(lines),
        "line_placemarks": lines,
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = {}

    for route_name, mid in ROUTES:
        url = KML_URL.format(mid=mid)
        print(f"Fetching {route_name} ({mid})...")
        try:
            r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
        except requests.RequestException as exc:
            print(f"  FAILED: {exc}", file=sys.stderr)
            summary[route_name] = {"error": str(exc)}
            continue

        kml_path = OUT_DIR / f"{route_name}.kml"
        kml_path.write_bytes(r.content)

        try:
            info = inspect_kml(r.content)
        except ET.ParseError as exc:
            print(f"  KML PARSE FAILED: {exc}", file=sys.stderr)
            summary[route_name] = {"error": f"parse error: {exc}"}
            continue

        info["mid"] = mid
        summary[route_name] = info

        flag = "HAS STOP POINTS!" if info["num_point_placemarks"] > 0 else "line only, no points"
        print(f"  {route_name}: {info['num_placemarks']} placemark(s) - {flag}")

        time.sleep(1)  # be polite to Google's servers across ~34 requests

    SUMMARY_PATH.write_text(json.dumps(summary, indent=2, ensure_ascii=False))

    routes_with_points = [r for r, info in summary.items() if info.get("num_point_placemarks", 0) > 0]
    print(f"\n{'='*60}")
    print(f"Routes with real stop-point markers: {len(routes_with_points)} / {len(ROUTES)}")
    if routes_with_points:
        print("  " + "\n  ".join(routes_with_points))
    else:
        print("  NONE - every Sotrames route map has geometry only, no stops.")
        print("  This is now confirmed across all routes, not just one sample.")
    print(f"\nFull details -> {SUMMARY_PATH}")
    print(f"Raw KML files -> {OUT_DIR}/")


if __name__ == "__main__":
    main()
