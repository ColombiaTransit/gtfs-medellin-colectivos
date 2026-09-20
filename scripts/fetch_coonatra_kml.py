#!/usr/bin/env python3
"""
Fetch real route geometry for every Coonatra branch that scrape_coonatra.py
paired cleanly (name + schedule + Google My Maps ID), via Google's
standard KML export for a public My Maps map:
    https://www.google.com/maps/d/kml?mid=<mid>&forcekml=1

Same mechanism, and the same inspect_kml() logic, as
scripts/fetch_sotrames_kml.py - reused directly since it's the same
Google My Maps KML format and this project already validated that
inspection logic against real Sotrames KML files (confirmed: real
Placemark/LineString/Point parsing, no silent failures).

SCOPE: reads raw/coonatra_routes.json (scrape_coonatra.py's output) and
fetches KML for every branch of every page marked clean_1to1_match:
true - currently Floresta-San Juan (4 branches) and Calasanz-Boston (6
branches, the ones with real PDF frequency data too). Copacabana and
Circular Coonatra are excluded automatically since their pages are
still ambiguous (no branches list exists for them) - re-run
scrape_coonatra.py after resolving that reconciliation and this script
will pick up their branches too, with no changes needed here.

Usage: python scripts/fetch_coonatra_kml.py
Requires: raw/coonatra_routes.json already present (run
scripts/scrape_coonatra.py first).
Output: raw/coonatra_kml/<page_title>__<branch_name>.kml (every
        branch's raw KML)
        raw/coonatra_kml_summary.json (per-branch: has_points,
        num_points, num_line_points, line_length info)
"""

import json
import re
import sys
import time
from pathlib import Path
from xml.etree import ElementTree as ET

import requests

ROUTES_PATH = Path("raw/coonatra_routes.json")
KML_URL = "https://www.google.com/maps/d/kml?mid={mid}&forcekml=1"
OUT_DIR = Path("raw/coonatra_kml")
SUMMARY_PATH = Path("raw/coonatra_kml_summary.json")
KML_NS = {"kml": "http://www.opengis.net/kml/2.2"}


def safe_filename(s: str) -> str:
    return re.sub(r"[^\w\-]+", "_", s).strip("_")


def inspect_kml(kml_bytes: bytes) -> dict:
    """Identical logic to fetch_sotrames_kml.py's inspect_kml - reused
    as-is since it's the same Google My Maps KML format, already
    validated against real files in this project."""
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


def collect_branches() -> list:
    """Returns [(page_title, branch_name, mid), ...] for every branch
    of every clean_1to1_match page found in raw/coonatra_routes.json."""
    if not ROUTES_PATH.exists():
        print(f"{ROUTES_PATH} not found - run scripts/scrape_coonatra.py first.",
              file=sys.stderr)
        sys.exit(1)

    pages = json.loads(ROUTES_PATH.read_text())
    branches = []
    for page in pages:
        if not page.get("clean_1to1_match") or not page.get("branches"):
            continue
        for b in page["branches"]:
            branches.append((page["title"], b["name"], b["mid"]))
    return branches


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    branches = collect_branches()

    if not branches:
        print("No clean-matched branches found in raw/coonatra_routes.json - "
              "nothing to fetch. Re-run scrape_coonatra.py first if this is "
              "unexpected.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(branches)} branch(es) with clean name/schedule/map "
          f"pairing to fetch KML for.")

    summary = {}
    for page_title, branch_name, mid in branches:
        key = f"{page_title} / {branch_name}"
        url = KML_URL.format(mid=mid)
        print(f"Fetching {key} ({mid})...")
        try:
            r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
        except requests.RequestException as exc:
            print(f"  FAILED: {exc}", file=sys.stderr)
            summary[key] = {"error": str(exc)}
            continue

        fname = f"{safe_filename(page_title)}__{safe_filename(branch_name)}.kml"
        kml_path = OUT_DIR / fname
        kml_path.write_bytes(r.content)

        try:
            info = inspect_kml(r.content)
        except ET.ParseError as exc:
            print(f"  KML PARSE FAILED: {exc}", file=sys.stderr)
            summary[key] = {"error": f"parse error: {exc}"}
            continue

        info["mid"] = mid
        info["kml_file"] = fname
        summary[key] = info

        flag = "HAS STOP POINTS!" if info["num_point_placemarks"] > 0 else "line only, no points"
        line_desc = ", ".join(f"{l['name']}: {l['num_points']} pts" for l in info["line_placemarks"])
        print(f"  {key}: {info['num_placemarks']} placemark(s) - {flag} - {line_desc}")

        time.sleep(1)  # be polite to Google's servers

    SUMMARY_PATH.write_text(json.dumps(summary, indent=2, ensure_ascii=False))

    errors = [k for k, v in summary.items() if "error" in v]
    with_points = [k for k, v in summary.items() if v.get("num_point_placemarks", 0) > 0]
    print(f"\n{'='*60}")
    print(f"{len(branches) - len(errors)} / {len(branches)} fetched successfully.")
    if errors:
        print(f"Errors: {errors}")
    print(f"Branches with real stop-point markers: {len(with_points)}")
    if with_points:
        print("  " + "\n  ".join(with_points))
    else:
        print("  NONE - every branch's map has geometry only, no stops "
              "(same pattern as Sotrames).")
    print(f"\nFull details -> {SUMMARY_PATH}")
    print(f"Raw KML files -> {OUT_DIR}/")


if __name__ == "__main__":
    main()
