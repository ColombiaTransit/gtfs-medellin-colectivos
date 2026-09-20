#!/usr/bin/env python3

"""
Harvest the complete Medellín VC_Transporte ArcGIS service.

The goal is to preserve as much source information as possible.

For every layer:
- retrieve all features
- preserve all attributes
- preserve geometry
- preserve the original ArcGIS response
- additionally create GeoJSON
- save layer metadata

No interpretation or route matching is performed here.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import requests


BASE_URL = (
    "https://www.medellin.gov.co/"
    "servidormapas/rest/services/"
    "mapas_nacionales/VC_Transporte/MapServer"
)

OUTPUT_DIR = Path("data/medellin")
RAW_DIR = OUTPUT_DIR / "raw"
GEOJSON_DIR = OUTPUT_DIR / "geojson"
METADATA_DIR = OUTPUT_DIR / "metadata"

PAGE_SIZE = 2000

# All currently exposed layers in VC_Transporte.
#
# We deliberately keep this explicit rather than automatically crawling
# every possible ArcGIS child resource. This makes the scraper predictable
# while still harvesting the complete transport service.
LAYERS = {
    0: "jerarquia_vial",
    1: "lineas_sistema_transporte_masivo",
    2: "estaciones_sistema_transporte_masivo",
    3: "sentido_vial",
    4: "red_ciclista",
    5: "parada_transporte_publico",
    6: "rutas_transporte_publico",
    7: "calzada",
    9: "puente",
}


session = requests.Session()
session.headers.update(
    {
        "User-Agent": "medellin-transport-gis-harvester/1.0",
    }
)


def get_json(
    url: str,
    params: dict[str, Any] | None = None,
    retries: int = 4,
) -> dict[str, Any]:
    """GET JSON from ArcGIS with retries."""

    last_error: Exception | None = None

    for attempt in range(1, retries + 1):
        try:
            response = session.get(
                url,
                params=params,
                timeout=120,
            )

            response.raise_for_status()

            data = response.json()

            if "error" in data:
                raise RuntimeError(
                    f"ArcGIS error: {json.dumps(data['error'], ensure_ascii=False)}"
                )

            return data

        except Exception as exc:
            last_error = exc

            print(
                f"Request failed "
                f"(attempt {attempt}/{retries}): {url}"
            )
            print(exc)

            if attempt < retries:
                time.sleep(attempt * 3)

    raise RuntimeError(
        f"Failed to retrieve {url}"
    ) from last_error


def get_layer_metadata(layer_id: int) -> dict[str, Any]:
    """Retrieve complete ArcGIS layer metadata."""

    url = f"{BASE_URL}/{layer_id}"

    return get_json(
        url,
        {
            "f": "json",
        },
    )


def query_layer(
    layer_id: int,
) -> list[dict[str, Any]]:
    """
    Retrieve every feature from a layer.

    ArcGIS pagination is handled using resultOffset/resultRecordCount.
    """

    url = f"{BASE_URL}/{layer_id}/query"

    features: list[dict[str, Any]] = []
    offset = 0

    while True:
        print(
            f"    Downloading records "
            f"{offset} - {offset + PAGE_SIZE - 1}"
        )

        params = {
            "f": "json",
            "where": "1=1",
            "outFields": "*",
            "returnGeometry": "true",
            "resultOffset": offset,
            "resultRecordCount": PAGE_SIZE,
            "orderByFields": "objectid ASC",
        }

        data = get_json(url, params)

        page = data.get("features", [])

        if not page:
            break

        features.extend(page)

        print(
            f"    Received {len(page)} features "
            f"(total: {len(features)})"
        )

        if not data.get("exceededTransferLimit", False):
            break

        offset += len(page)

        # Safety check in case an ArcGIS service behaves unexpectedly.
        if len(page) < PAGE_SIZE:
            break

    return features


def save_json(
    path: Path,
    data: Any,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open(
        "w",
        encoding="utf-8",
    ) as fh:
        json.dump(
            data,
            fh,
            ensure_ascii=False,
            indent=2,
        )


def to_geojson(
    features: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Convert ArcGIS JSON features into a GeoJSON FeatureCollection.

    ArcGIS uses:
        geometry.paths
        geometry.rings
        geometry.x/y
        geometry.points

    GeoJSON uses:
        LineString / MultiLineString
        Polygon / MultiPolygon
        Point
        MultiPoint
    """

    result = []

    for feature in features:
        attributes = feature.get("attributes") or {}
        geometry = feature.get("geometry")

        geo_geometry = arcgis_geometry_to_geojson(geometry)

        result.append(
            {
                "type": "Feature",
                "properties": attributes,
                "geometry": geo_geometry,
            }
        )

    return {
        "type": "FeatureCollection",
        "features": result,
    }


def arcgis_geometry_to_geojson(
    geometry: dict[str, Any] | None,
) -> dict[str, Any] | None:

    if not geometry:
        return None

    # Point
    if "x" in geometry and "y" in geometry:
        return {
            "type": "Point",
            "coordinates": [
                geometry["x"],
                geometry["y"],
            ],
        }

    # MultiPoint
    if "points" in geometry:
        return {
            "type": "MultiPoint",
            "coordinates": geometry["points"],
        }

    # Polyline
    if "paths" in geometry:
        paths = geometry["paths"]

        if len(paths) == 1:
            return {
                "type": "LineString",
                "coordinates": paths[0],
            }

        return {
            "type": "MultiLineString",
            "coordinates": paths,
        }

    # Polygon
    if "rings" in geometry:
        rings = geometry["rings"]

        return {
            "type": "Polygon",
            "coordinates": rings,
        }

    print(
        "WARNING: Unknown ArcGIS geometry:",
        list(geometry.keys()),
    )

    return None


def harvest_layer(
    layer_id: int,
    layer_name: str,
) -> None:

    print()
    print("=" * 70)
    print(f"LAYER {layer_id}: {layer_name}")
    print("=" * 70)

    metadata = get_layer_metadata(layer_id)

    features = query_layer(layer_id)

    print(
        f"  Total features: {len(features)}"
    )

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    metadata_path = (
        METADATA_DIR /
        f"{layer_id}_{layer_name}.json"
    )

    save_json(
        metadata_path,
        metadata,
    )

    # ------------------------------------------------------------------
    # Raw ArcGIS feature response
    # ------------------------------------------------------------------

    raw_response = {
        "source": f"{BASE_URL}/{layer_id}",
        "layer_id": layer_id,
        "layer_name": metadata.get(
            "name",
            layer_name,
        ),
        "spatialReference": metadata.get(
            "extent",
            {}).get(
                "spatialReference"
            ),
        "features": features,
    }

    raw_path = (
        RAW_DIR /
        f"{layer_id}_{layer_name}.json"
    )

    save_json(
        raw_path,
        raw_response,
    )

    # ------------------------------------------------------------------
    # GeoJSON
    # ------------------------------------------------------------------

    geojson = to_geojson(features)

    geojson["crs"] = {
        "type": "name",
        "properties": {
            "name": "EPSG:9377",
        },
    }

    geojson_path = (
        GEOJSON_DIR /
        f"{layer_id}_{layer_name}.geojson"
    )

    save_json(
        geojson_path,
        geojson,
    )

    print(
        f"  Raw:     {raw_path}"
    )
    print(
        f"  GeoJSON: {geojson_path}"
    )
    print(
        f"  Metadata:{metadata_path}"
    )


def main() -> None:

    print("Medellín VC_Transporte ArcGIS harvester")
    print(f"Source: {BASE_URL}")
    print()

    RAW_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    GEOJSON_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    METADATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Save complete service metadata first.
    service_metadata = get_json(
        BASE_URL,
        {
            "f": "json",
        },
    )

    save_json(
        METADATA_DIR / "service.json",
        service_metadata,
    )

    # Harvest every layer.
    for layer_id, layer_name in LAYERS.items():

        try:
            harvest_layer(
                layer_id,
                layer_name,
            )

        except Exception as exc:
            print()
            print(
                f"ERROR harvesting layer "
                f"{layer_id} ({layer_name})"
            )
            print(exc)

            # Continue with the remaining layers.
            continue

    print()
    print("=" * 70)
    print("HARVEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()

