#!/usr/bin/env python3
"""
Bulk-download ALL data (every record, every field, no operator filter)
from Medellín's official government ArcGIS public-transit layers, and
save it locally. This is a separate step from analysis on purpose: run
this occasionally (see the accompanying workflow - manual trigger for
now, but designed to be put on a monthly schedule later, since this is
government data that presumably changes slowly) to refresh the raw
data, then query/filter/join it LOCALLY as many times as needed for
whichever operator matters at the time - no repeated network calls
against medellin.gov.co for every analysis pass.

LAYERS DOWNLOADED (5 total, across 2 ArcGIS services):
  mapas_nacionales/VC_Transporte:
    5 - "Parada de transporte publico" - POINT stops. Confirmed richer
        than VM_Movilidad's Parada layer for TRSC specifically (real
        stop NAMES, more complete route coverage - see the
        conversation this came from). Same Service Item Id as layer 6
        below - true siblings, same maintainers.
    6 - "Rutas de transporte publico" - POLYLINE route geometry.
  transporte/VM_Movilidad:
    0 - "Parada" - POINT stops. Already proven useful for TRSC (843
        real stops matched), kept even though layer 5 above is
        richer, since it's a different service/dataset that might
        cover routes/operators layer 5 doesn't.
    1 - "Rutas Unificadas" - UNEXPLORED. Schema unknown - this script
        doesn't assume field names, it requests outFields=* (every
        field) rather than a hardcoded list, specifically so an
        unexplored layer's real schema doesn't need to be guessed at
        or verified first. Whatever fields exist will be in the
        output; inspect the saved file to see what's actually there.
    2 - "Rutas de Transporte Público" - UNEXPLORED, same outFields=*
        approach. Name is nearly identical to VC_Transporte layer 6
        but a DIFFERENT service - may overlap, may be complementary,
        not yet determined.

NO OPERATOR FILTER - every record in every layer is downloaded, since
the goal is a full local copy to query repeatedly, not a one-off
TRSC-specific pull. Expect this to be substantially larger than any
previous download in this project (these layers cover the whole city,
every operator, not just Transportes Rapido San Cristobal).

Usage: python scripts/download_medellin_transporte_layers.py
Output: raw/medellin_raw/<layer_label>.json (one file per layer, full
        unfiltered feature list)
        raw/medellin_raw/manifest.json (what was downloaded, when, and
        how many records - so a future run can show what changed)
"""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

OUT_DIR = Path("raw/medellin_raw")
MANIFEST_PATH = OUT_DIR / "manifest.json"

MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 5
BETWEEN_LAYERS_DELAY_SECONDS = 3

LAYERS = [
    {
        "label": "vc_transporte_parada",
        "url": "https://www.medellin.gov.co/servidormapas/rest/services/mapas_nacionales/VC_Transporte/MapServer/5/query",
        "description": "Parada de transporte publico (VC_Transporte/5) - richer stop layer, real stop names",
    },
    {
        "label": "vc_transporte_rutas",
        "url": "https://www.medellin.gov.co/servidormapas/rest/services/mapas_nacionales/VC_Transporte/MapServer/6/query",
        "description": "Rutas de transporte publico (VC_Transporte/6) - route polyline geometry",
    },
    {
        "label": "vm_movilidad_parada",
        "url": "https://www.medellin.gov.co/servidormapas/rest/services/transporte/VM_Movilidad/MapServer/0/query",
        "description": "Parada (VM_Movilidad/0) - stop layer, different service than the two above",
    },
    {
        "label": "vm_movilidad_rutas_unificadas",
        "url": "https://www.medellin.gov.co/servidormapas/rest/services/transporte/VM_Movilidad/MapServer/1/query",
        "description": "Rutas Unificadas (VM_Movilidad/1) - UNEXPLORED schema, outFields=* used",
    },
    {
        "label": "vm_movilidad_rutas_transporte_publico",
        "url": "https://www.medellin.gov.co/servidormapas/rest/services/transporte/VM_Movilidad/MapServer/2/query",
        "description": "Rutas de Transporte Público (VM_Movilidad/2) - UNEXPLORED schema, outFields=* used",
    },
]


def _request_with_retry(url: str, params: dict) -> dict:
    last_exc = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.get(url, params=params, timeout=60)
            if r.status_code != 200:
                raise RuntimeError(
                    f"HTTP {r.status_code} - response body (first 300 chars): "
                    f"{r.text[:300]!r}"
                )
            try:
                data = r.json()
            except ValueError as exc:
                raise RuntimeError(
                    f"response wasn't valid JSON (content-type "
                    f"{r.headers.get('content-type')!r}) - body (first 300 "
                    f"chars): {r.text[:300]!r}"
                ) from exc
            if "error" in data:
                raise RuntimeError(f"ArcGIS query error: {data['error']}")
            return data
        except Exception as exc:
            last_exc = exc
            if attempt < MAX_RETRIES:
                wait = RETRY_BACKOFF_SECONDS * (2 ** (attempt - 1))
                print(f"    attempt {attempt}/{MAX_RETRIES} failed ({exc}) - "
                      f"retrying in {wait}s...", file=sys.stderr)
                time.sleep(wait)
    raise RuntimeError(f"all {MAX_RETRIES} attempts failed - last error: {last_exc}")


def download_full_layer(layer_url: str) -> list:
    """Every record, every field (outFields=*), no WHERE filter beyond
    1=1 (ArcGIS requires some where clause)."""
    all_features = []
    offset = 0
    page_size = 1000  # under every layer's confirmed MaxRecordCount of 2000

    while True:
        params = {
            "where": "1=1",
            "outFields": "*",
            "f": "json",
            "resultOffset": offset,
            "resultRecordCount": page_size,
            "returnGeometry": "true",
        }
        data = _request_with_retry(layer_url, params)

        features = data.get("features", [])
        all_features.extend(features)
        print(f"    fetched {len(features)} feature(s) at offset {offset} "
              f"(running total: {len(all_features)})")

        if len(features) < page_size or not data.get("exceededTransferLimit", False):
            break
        offset += page_size

    return all_features


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {"downloaded_at": datetime.now(timezone.utc).isoformat(), "layers": {}}

    for i, layer in enumerate(LAYERS):
        print(f"Downloading {layer['label']} ({layer['description']})...")
        try:
            features = download_full_layer(layer["url"])
        except Exception as exc:
            print(f"  FAILED after retries: {exc}", file=sys.stderr)
            manifest["layers"][layer["label"]] = {
                "url": layer["url"], "description": layer["description"],
                "error": str(exc),
            }
            continue

        out_path = OUT_DIR / f"{layer['label']}.json"
        out_path.write_text(json.dumps(features, ensure_ascii=False))
        print(f"  {len(features)} record(s) -> {out_path}")

        sample_fields = sorted(features[0]["attributes"].keys()) if features else []
        manifest["layers"][layer["label"]] = {
            "url": layer["url"], "description": layer["description"],
            "num_records": len(features), "fields_seen": sample_fields,
        }

        if i < len(LAYERS) - 1:
            time.sleep(BETWEEN_LAYERS_DELAY_SECONDS)

    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(f"\nManifest -> {MANIFEST_PATH}")
    for label, info in manifest["layers"].items():
        if "error" in info:
            print(f"  {label}: FAILED - {info['error']}")
        else:
            print(f"  {label}: {info['num_records']} record(s), "
                  f"{len(info['fields_seen'])} field(s)")


if __name__ == "__main__":
    main()
