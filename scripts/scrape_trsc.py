#!/usr/bin/env python3
"""
Scrape Transportes Rapido San Cristobal (trscsas.com/rutas/) for route
names and Google My Maps IDs, then fetch each route's real KML geometry
via the same Google My Maps export technique already validated for
Sotrames and Coonatra (google.com/maps/d/kml?mid=<mid>&forcekml=1).
Combined into one script/one run, matching this project's established
pattern for the other operators.

IMPORTANT - robots.txt: trscsas.com's robots.txt disallows automated
access, confirmed directly (the environment that wrote this script
could not fetch the page itself for exactly this reason - the person
using this project pasted the real page source by hand instead). This
script uses `requests`, which does NOT check robots.txt on its own -
running it is a deliberate choice to proceed despite the site's stated
preference, made by whoever runs it, not something this script hides.
If that matters for your use case, don't run this against the live
site without your own judgment call on it.

STRUCTURE (confirmed against the real page source, not guessed): the
page has TWO separate Elementor accordion widgets, not one. Each
contains several accordion items, and - unlike Coonatra's site - each
item directly contains BOTH its name and its own single Google Maps
iframe together (no decoupled "several schedule headings then several
maps" ambiguity to resolve here; pairing is inherently 1:1 by
construction).
  - Accordion 1 (14 items seen): mostly "Ruta 255 X" named entries.
  - Accordion 2 (11 items seen): mostly "Itinerario 255 X" or plain
    "255 X" named entries.
Both groups' names reference route "255" specifically - this operator
appears to run one numbered service with many named branches/variants,
unlike Coonatra's multiple distinct route numbers. This script does NOT
guess which accordion is "the real routes" vs "itinerary detail" -
both are captured, tagged with their accordion index, for a human to
interpret.

NO SCHEDULE OR FREQUENCY DATA EXISTS ON THIS RUTAS PAGE AT ALL -
confirmed by reading the real page source directly, not inferred.
Schedule data instead lives as PHOTOGRAPHS on a separate /horarios/
page (see scripts/scrape_trsc_horarios.py) - it needs OCR, and the
photo-to-route pairing is genuinely ambiguous for most of them (see
that script's docstring and the conversation this project came from).
The KML geometry and real stop names fetched here are intended to help
CROSS-REFERENCE against that ambiguous pairing later (e.g. a landmark
visible in one schedule photo matching a stop name on one specific
route's real map) - this script does not attempt that matching itself.

Usage: python scripts/scrape_trsc.py
Output: raw/trsc_routes.json (route names + mids)
        raw/trsc_kml/<route_name>.kml (every route's raw KML)
        raw/trsc_kml_summary.json (per-route: has_points, num_points,
        line length, etc.)
"""

import json
import re
import sys
import time
from pathlib import Path
from xml.etree import ElementTree as ET

import requests
from bs4 import BeautifulSoup

RUTAS_URL = "https://trscsas.com/rutas/"
OUT_PATH = Path("raw/trsc_routes.json")

MAPS_RE = re.compile(r"https://www\.google\.com/maps/d/(?:u/0/)?embed\?mid=([\w-]+)")

KML_URL = "https://www.google.com/maps/d/kml?mid={mid}&forcekml=1"
KML_OUT_DIR = Path("raw/trsc_kml")
KML_SUMMARY_PATH = Path("raw/trsc_kml_summary.json")
KML_NS = {"kml": "http://www.opengis.net/kml/2.2"}


def safe_filename(s: str) -> str:
    return re.sub(r"[^\w\-]+", "_", s).strip("_")


def inspect_kml(kml_bytes: bytes) -> dict:
    """Identical logic to fetch_sotrames_kml.py / fetch_coonatra_kml.py's
    inspect_kml - reused as-is since it's the same Google My Maps KML
    format, already validated against real files in this project."""
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
        "num_point_placemarks": len(points),
        "point_placemarks": points,
        "num_line_placemarks": len(lines),
        "line_placemarks": lines,
    }


def scrape() -> list:
    r = requests.get(RUTAS_URL, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    print(f"  GET {RUTAS_URL} -> HTTP {r.status_code}, {len(r.text)} bytes")
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    accordion_widgets = soup.select(".elementor-widget-accordion")
    print(f"  Found {len(accordion_widgets)} accordion widget(s)")

    routes = []
    for widget_idx, widget in enumerate(accordion_widgets):
        items = widget.select(".elementor-accordion-item")
        print(f"    accordion {widget_idx}: {len(items)} item(s)")
        for item in items:
            title_el = item.select_one(".elementor-accordion-title")
            iframe_el = item.select_one("iframe[src]")
            name = title_el.get_text(strip=True) if title_el else None
            mid_match = MAPS_RE.search(iframe_el["src"]) if iframe_el else None
            mid = mid_match.group(1) if mid_match else None

            if not name or not mid:
                print(f"    WARNING: incomplete item in accordion {widget_idx} - "
                      f"name={name!r} mid={mid!r} - skipped", file=sys.stderr)
                continue

            routes.append({"accordion_index": widget_idx, "name": name, "mid": mid})

    return routes


def fetch_kml_for_routes(routes: list) -> dict:
    KML_OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = {}

    for route in routes:
        name, mid = route["name"], route["mid"]
        url = KML_URL.format(mid=mid)
        print(f"  Fetching KML for {name!r} ({mid})...")
        try:
            r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
        except requests.RequestException as exc:
            print(f"    FAILED: {exc}", file=sys.stderr)
            summary[name] = {"error": str(exc)}
            continue

        kml_path = KML_OUT_DIR / f"{safe_filename(name)}.kml"
        kml_path.write_bytes(r.content)

        try:
            info = inspect_kml(r.content)
        except ET.ParseError as exc:
            print(f"    KML PARSE FAILED: {exc}", file=sys.stderr)
            summary[name] = {"error": f"parse error: {exc}"}
            continue

        info["mid"] = mid
        info["kml_file"] = kml_path.name
        summary[name] = info

        flag = "HAS STOP POINTS" if info["num_point_placemarks"] > 0 else "line only, no points"
        line_desc = ", ".join(f"{l['name']}: {l['num_points']} pts" for l in info["line_placemarks"])
        print(f"    {info['num_placemarks']} placemark(s) - {flag} - {line_desc}")

        time.sleep(1)  # be polite to Google's servers across 25 requests

    return summary


def main():
    print(f"Scraping {RUTAS_URL} ...")
    routes = scrape()

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(routes, indent=2, ensure_ascii=False))

    print(f"\nFound {len(routes)} route/itinerary entries.")
    by_accordion = {}
    for r in routes:
        by_accordion.setdefault(r["accordion_index"], []).append(r["name"])
    for idx, names in by_accordion.items():
        print(f"  Accordion {idx} ({len(names)} items): {names}")
    print(f"Saved -> {OUT_PATH}")

    print(f"\nFetching KML for all {len(routes)} route(s)...")
    kml_summary = fetch_kml_for_routes(routes)
    KML_SUMMARY_PATH.write_text(json.dumps(kml_summary, indent=2, ensure_ascii=False))

    errors = [k for k, v in kml_summary.items() if "error" in v]
    with_points = [k for k, v in kml_summary.items() if v.get("num_point_placemarks", 0) > 0]
    print(f"\n{'='*60}")
    print(f"KML: {len(routes) - len(errors)} / {len(routes)} fetched successfully.")
    if errors:
        print(f"Errors: {errors}")
    print(f"Routes with real stop-point markers: {len(with_points)}")
    if with_points:
        print("  " + "\n  ".join(with_points))
    else:
        print("  NONE - every route's map has geometry only, no stops.")
    print(f"\nSaved -> {KML_SUMMARY_PATH}")
    print(f"Raw KML files -> {KML_OUT_DIR}/")

    print("\nNOTE: no schedule/frequency data exists on the /rutas/ page - see "
          "module docstring. Schedule photos live on a separate /horarios/ "
          "page (scripts/scrape_trsc_horarios.py) with a genuinely ambiguous "
          "photo-to-route pairing for most routes - use this KML geometry "
          "and real stop names to help cross-reference that, once needed.")


if __name__ == "__main__":
    main()
