#!/usr/bin/env python3
"""
Fetch the "Rutas Alimentadoras" and "Paradas Alimentadoras" layers from
Metro de Medellin's ArcGIS Hub as GeoJSON.

ArcGIS Hub dataset URLs look like:
  .../datasets/<item_id>_<layer_index>/explore

<item_id> is the AGO item id. <layer_index> is the layer within that
item's hosted FeatureServer. We resolve the FeatureServer base url via
the item's sharing/rest metadata, then query that layer directly -
this is more robust than guessing a Hub "download" URL, which changes
format across portal versions.
"""

import json
import re
import sys
from pathlib import Path

import requests

# hub dataset id -> (item_id, layer_index, output filename)
DATASETS = {
    "rutas_alimentadoras": ("890bb205825b44019510b8d8954a7e81", 2, "rutas_alimentadoras.geojson"),
    "paradas_alimentadoras": ("5ab395db7e30403bb85fe599d6af66bd", 0, "paradas_alimentadoras.geojson"),
}

OUTPUT_DIR = Path("raw")


def resolve_layer_url(item_id: str) -> str:
    """Given an AGO item id, return the hosted FeatureServer base url."""
    r = requests.get(
        f"https://www.arcgis.com/sharing/rest/content/items/{item_id}",
        params={"f": "json"},
        timeout=30,
    )
    r.raise_for_status()
    meta = r.json()

    url = meta.get("url")
    if not url:
        raise RuntimeError(
            f"Item {item_id} has no 'url' field - it may not be a hosted "
            f"feature layer, or may require auth. Response: {meta}"
        )
    return url.rstrip("/")


def fetch_layer_geojson(item_id: str, layer_index: int) -> dict:
    base_url = resolve_layer_url(item_id)

    # base_url from an item is usually the *service* url (…/FeatureServer),
    # sometimes it already points at a specific layer (…/FeatureServer/2).
    # Normalize to the service root, then append the requested layer index.
    service_url = re.sub(r"/\d+$", "", base_url)

    query_url = f"{service_url}/{layer_index}/query"

    features = []
    offset = 0
    page_size = 2000

    while True:
        r = requests.get(
            query_url,
            params={
                "where": "1=1",
                "outFields": "*",
                "outSR": 4326,
                "f": "geojson",
                "resultOffset": offset,
                "resultRecordCount": page_size,
            },
            timeout=60,
        )
        r.raise_for_status()
        page = r.json()

        page_features = page.get("features", [])
        features.extend(page_features)

        if len(page_features) < page_size:
            break
        offset += page_size

    return {"type": "FeatureCollection", "features": features}


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for name, (item_id, layer_index, out_file) in DATASETS.items():
        print(f"Fetching {name} (item {item_id}, layer {layer_index})...")
        try:
            geojson = fetch_layer_geojson(item_id, layer_index)
        except Exception as exc:  # noqa: BLE001
            print(f"  FAILED: {exc}", file=sys.stderr)
            sys.exit(1)

        out_path = OUTPUT_DIR / out_file
        out_path.write_text(json.dumps(geojson))
        print(f"  Saved {len(geojson['features'])} features -> {out_path}")


if __name__ == "__main__":
    main()
