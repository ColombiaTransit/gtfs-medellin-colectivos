#!/usr/bin/env python3
"""
Print the attribute schema of the fetched ArcGIS layers so the real field
names can be read straight out of the GitHub Actions log, instead of
guessing at ROUTE_ID_FIELD / STOP_ID_FIELD / etc. in build_gtfs.py.
"""

import json
from pathlib import Path

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

        # Also show a second sample so field values that look like ids/names
        # are easier to tell apart from constants.
        if len(features) > 1:
            print("  Second sample:")
            for k, v in features[1]["properties"].items():
                print(f"    {k}: {v!r}")


if __name__ == "__main__":
    main()
