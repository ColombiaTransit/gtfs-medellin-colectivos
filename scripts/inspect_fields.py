#!/usr/bin/env python3
"""
Print the attribute schema of the fetched ArcGIS layers so the real field
names can be read straight out of the GitHub Actions log, instead of
guessing at ROUTE_ID_FIELD / STOP_ID_FIELD / etc. in build_gtfs.py.

Also dumps every (ruta, cuenca) pair from the routes layer - not just a
couple of samples - so operator coverage in data/operators.yml can be
checked against the FULL route list rather than the handful of routes
that happened to be visible on MDO's/SAO6's own websites.
"""

import json
from pathlib import Path

import yaml

FILES = [
    Path("raw/rutas_alimentadoras.geojson"),
    Path("raw/paradas_alimentadoras.geojson"),
]


def main():
    for path in FILES:
        if not path.exists():
            print(f"{path}: not found (did fetch_alimentadoras.py run?)")
            continue

        data = json.loads(path.read_text())
        features = data.get("features", [])
        print(f"\n=== {path} ({len(features)} features) ===")

        if not features:
            print("  (no features)")
            continue

        sample = features[0]["properties"]
        print(f"  Fields: {list(sample.keys())}")
        print("  Sample values:")
        for k, v in sample.items():
            print(f"    {k}: {v!r}")

        if len(features) > 1:
            print("  Second sample:")
            for k, v in features[1]["properties"].items():
                print(f"    {k}: {v!r}")

    routes_path = Path("raw/rutas_alimentadoras.geojson")
    if routes_path.exists():
        _dump_route_coverage(routes_path)


def _dump_route_coverage(routes_path: Path):
    data = json.loads(routes_path.read_text())
    all_routes = sorted({
        (f["properties"].get("ruta"), f["properties"].get("cuenca"))
        for f in data.get("features", [])
    })

    print(f"\n=== Full route list ({len(all_routes)} distinct 'ruta' values) ===")
    for ruta, cuenca in all_routes:
        print(f"  {ruta}  (cuenca {cuenca})")

    cuenca_counts = {}
    for _, cuenca in all_routes:
        cuenca_counts[cuenca] = cuenca_counts.get(cuenca, 0) + 1
    print(f"\n  Cuenca distribution: {cuenca_counts}")

    operators_path = Path("data/operators.yml")
    if not operators_path.exists():
        operators_path = Path("data/operators.yml.example")
    if not operators_path.exists():
        print("\n  (no data/operators.yml[.example] to diff against)")
        return

    config = yaml.safe_load(operators_path.read_text())
    configured = {r["route_id"] for r in config.get("routes", [])}
    all_ruta_ids = {ruta for ruta, _ in all_routes if ruta is not None}

    missing = sorted(all_ruta_ids - configured)
    extra = sorted(configured - all_ruta_ids)

    print(f"\n=== Coverage vs. {operators_path} ===")
    print(f"  In ArcGIS but NOT in operators.yml: {len(missing)} routes")
    if missing:
        print(f"    {missing}")
    if extra:
        print(f"  In operators.yml but NOT in current ArcGIS pull: {len(extra)} routes")
        print(f"    {extra}")


if __name__ == "__main__":
    main()
