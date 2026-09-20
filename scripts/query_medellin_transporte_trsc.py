#!/usr/bin/env python3
"""
Query THREE of Medellín's official government ArcGIS layers for
Transportes Rapido San Cristobal / route "255" data, and cross-reference
each Paradas (stops) layer against Rutas (route geometry) client-side
(these are separate ArcGIS services - the REST API doesn't support a
server-side SQL join across them, so this script fetches all three and
matches records in Python):

  1. "Rutas de transporte publico" (mapas_nacionales/VC_Transporte/
     MapServer/6) - POLYLINE geometry per route: nombre, id_ruta,
     codigo, recorrido, sistema, tipo, empresa, id_gflota.
  2. "Parada" (transporte/VM_Movilidad/MapServer/0) - POINT stops, from
     a DIFFERENT ArcGIS service than Rutas (different Service Item Id) -
     id_ruta, codigo_ruta, nombre_ruta, sistema_ruta, empresa,
     latitud/longitud, direccion, nro_parada. Already confirmed to join
     well against Rutas via id_ruta (18 of 21 real routes matched, with
     genuine stop counts) - kept as-is, not because it's the best
     structural fit, but because it's already proven to work.
  3. "Parada de transporte publico" (mapas_nacionales/VC_Transporte/
     MapServer/5) - POINT stops, THE TRUE SIBLING of the Rutas layer:
     confirmed same Service Item Id (9d0f7d17b7924c8dab4933f4664a6d7b)
     as layer 6, same MapServer, adjacent layer index - almost
     certainly maintained together, more likely to relate cleanly via
     id_ruta than layer 0's coincidental match. Also has 4 fields layer
     0 lacks entirely: nombre (a real STOP NAME - layer 0 has no name
     field, only direccion/address), orientacion, mobiliario, and
     id_gflota (a second potential join key, since Rutas has this
     field too). NOT YET COMPARED against layer 0 for TRSC specifically -
     this script queries and joins both, so the actual results (not an
     assumption from the schema) show which is more complete.

WHY THIS MATTERS: confirmed via a REAL run of the layer-0-based version
of this script - 18 of 21 distinct TRSC routes matched real stops via
id_ruta==id_ruta (843 stop records total), and this also surfaced real
routes/route variants (e.g. "255P Palmitas-Centro", left/right
"255V3 Boqueron" branches, "Estacion Estadio" routes) that aren't
listed anywhere on trscsas.com's own /rutas/ page. This is genuinely
official, government-sourced data, categorically better than the
photographed schedule boards and Google-My-Maps-only line geometry
this project otherwise has for TRSC (all 25 website-listed routes
confirmed line-only via KML, zero real stop points there).

JOIN STRATEGY: id_ruta is tried FIRST for each Paradas layer against
Rutas (confirmed via real data to work well for layer 0 - see above),
with codigo == codigo_ruta as a fallback. Both layers' id_ruta fields
don't share a consistent TYPE with Rutas' id_ruta (Rutas: STRING,
both Paradas layers: INTEGER, confirmed from each layer's real
metadata) - this script normalizes all three to strings before
comparing, confirmed correct via testing (id_ruta=9001 as int and
id_ruta="9001" as string DO match after normalization).

Usage: python scripts/query_medellin_transporte_trsc.py
Output: raw/medellin_rutas_trsc.json (matching route/line records)
        raw/medellin_paradas_v0_trsc.json (layer 0 matching stops)
        raw/medellin_paradas_v1_trsc.json (layer 5 matching stops -
        the richer, structurally-related layer)
        raw/medellin_transporte_trsc_joined_v0.json (Rutas x layer 0)
        raw/medellin_transporte_trsc_joined_v1.json (Rutas x layer 5)
        raw/medellin_*_empresa_values.json (diagnostic, only written if
        a main query comes back empty - every distinct 'empresa' value
        in that layer, in case TRSC is spelled differently than
        expected)
"""

import json
import sys
from pathlib import Path

import requests

RUTAS_LAYER_URL = "https://www.medellin.gov.co/servidormapas/rest/services/mapas_nacionales/VC_Transporte/MapServer/6/query"
PARADAS_V0_LAYER_URL = "https://www.medellin.gov.co/servidormapas/rest/services/transporte/VM_Movilidad/MapServer/0/query"
PARADAS_V1_LAYER_URL = "https://www.medellin.gov.co/servidormapas/rest/services/mapas_nacionales/VC_Transporte/MapServer/5/query"

RUTAS_OUT = Path("raw/medellin_rutas_trsc.json")
PARADAS_V0_OUT = Path("raw/medellin_paradas_v0_trsc.json")
PARADAS_V1_OUT = Path("raw/medellin_paradas_v1_trsc.json")
JOINED_V0_OUT = Path("raw/medellin_transporte_trsc_joined_v0.json")
JOINED_V1_OUT = Path("raw/medellin_transporte_trsc_joined_v1.json")

RUTAS_FIELDS = ["objectid", "nombre", "id_ruta", "codigo", "recorrido",
                "sistema", "tipo", "empresa", "id_gflota"]
PARADAS_V0_FIELDS = ["id_paradero", "id_parada", "id_ruta", "nro_parada", "direccion",
                      "tipo_parada", "recorrido", "codigo_ruta", "nombre_ruta",
                      "sistema_ruta", "tipo_ruta", "empresa", "latitud", "longitud", "estado"]
PARADAS_V1_FIELDS = ["id_paradero", "id_parada", "id_ruta", "nro_parada", "nombre",
                      "direccion", "orientacion", "mobiliario", "tipo_parada", "recorrido",
                      "codigo_ruta", "nombre_ruta", "sistema_ruta", "tipo_ruta", "empresa",
                      "id_gflota", "latitud", "longitud", "estado"]

TRSC_WHERE_RUTAS = (
    "UPPER(empresa) LIKE '%CRISTOBAL%' OR UPPER(empresa) LIKE '%RAPIDO%' "
    "OR UPPER(codigo) LIKE '%255%' OR UPPER(nombre) LIKE '%255%'"
)
TRSC_WHERE_PARADAS = (
    "UPPER(empresa) LIKE '%CRISTOBAL%' OR UPPER(empresa) LIKE '%RAPIDO%' "
    "OR UPPER(codigo_ruta) LIKE '%255%' OR UPPER(nombre_ruta) LIKE '%255%'"
)


def query_layer(layer_url: str, where_clause: str, fields: list) -> list:
    all_features = []
    offset = 0
    page_size = 1000  # under both layers' MaxRecordCount of 2000

    while True:
        params = {
            "where": where_clause,
            "outFields": ",".join(fields),
            "f": "json",
            "resultOffset": offset,
            "resultRecordCount": page_size,
            "returnGeometry": "true",
        }
        r = requests.get(layer_url, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()

        if "error" in data:
            raise RuntimeError(f"ArcGIS query error: {data['error']}")

        features = data.get("features", [])
        all_features.extend(features)
        print(f"    fetched {len(features)} feature(s) at offset {offset} "
              f"(running total: {len(all_features)})")

        if len(features) < page_size or not data.get("exceededTransferLimit", False):
            break
        offset += page_size

    return all_features


def get_distinct_empresa_values(layer_url: str, empresa_field: str) -> list:
    params = {
        "where": "1=1",
        "outFields": empresa_field,
        "returnDistinctValues": "true",
        "f": "json",
    }
    r = requests.get(layer_url, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    if "error" in data:
        raise RuntimeError(f"ArcGIS query error: {data['error']}")
    return sorted({f["attributes"].get(empresa_field) for f in data.get("features", [])
                   if f["attributes"].get(empresa_field)})


def run_query_with_fallback(layer_url, where, fields, out_path, empresa_field, label):
    print(f"Querying {label} layer for TRSC/255 matches...")
    try:
        features = query_layer(layer_url, where, fields)
    except Exception as exc:
        print(f"  {label} QUERY FAILED: {exc}", file=sys.stderr)
        features = []

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(features, indent=2, ensure_ascii=False))
    print(f"  {len(features)} matching record(s) -> {out_path}")

    if not features:
        diag_path = Path(f"raw/medellin_{label.lower()}_empresa_values.json")
        print(f"  No matches - fetching distinct '{empresa_field}' values as a "
              f"diagnostic...")
        try:
            values = get_distinct_empresa_values(layer_url, empresa_field)
            diag_path.write_text(json.dumps(values, indent=2, ensure_ascii=False))
            print(f"  {len(values)} distinct value(s) -> {diag_path} - check by "
                  f"eye for a TRSC variant spelling.")
        except Exception as exc:
            print(f"  Diagnostic query also failed: {exc}", file=sys.stderr)

    return features


def join_routes_and_stops(routes: list, paradas: list) -> dict:
    def norm(v):
        return str(v).strip().upper() if v is not None else None

    stops_by_codigo = {}
    for p in paradas:
        key = norm(p["attributes"].get("codigo_ruta"))
        if key:
            stops_by_codigo.setdefault(key, []).append(p)

    stops_by_id_ruta = {}
    for p in paradas:
        key = norm(p["attributes"].get("id_ruta"))
        if key:
            stops_by_id_ruta.setdefault(key, []).append(p)

    joined, matched_stop_indices = [], set()
    for route in routes:
        attrs = route["attributes"]
        codigo_key = norm(attrs.get("codigo"))
        id_ruta_key = norm(attrs.get("id_ruta"))

        matched = stops_by_id_ruta.get(id_ruta_key, [])
        match_basis = "id_ruta == id_ruta" if matched else None
        if not matched:
            matched = stops_by_codigo.get(codigo_key, [])
            match_basis = "codigo == codigo_ruta" if matched else None

        for m in matched:
            matched_stop_indices.add(id(m))

        joined.append({
            "route": attrs,
            "matched_stops": [m["attributes"] for m in matched],
            "match_basis": match_basis,
            "num_matched_stops": len(matched),
        })

    unmatched_paradas = [p["attributes"] for p in paradas if id(p) not in matched_stop_indices]

    return {
        "joined_routes": joined,
        "unmatched_paradas": unmatched_paradas,
        "num_routes": len(routes),
        "num_paradas": len(paradas),
        "num_routes_with_matched_stops": sum(1 for j in joined if j["num_matched_stops"] > 0),
    }


def summarize_join(result: dict, label: str):
    print(f"\n{result['num_routes_with_matched_stops']} / {result['num_routes']} "
          f"route(s) have at least one matched stop in {label}.")
    print(f"{len(result['unmatched_paradas'])} stop(s) in {label} didn't match any "
          f"route found in the Rutas layer.")
    for j in result["joined_routes"]:
        r = j["route"]
        print(f"  {r.get('codigo')} - {r.get('nombre')}: "
              f"{j['num_matched_stops']} stop(s) [{j['match_basis'] or 'no match'}]")


def main():
    routes = run_query_with_fallback(
        RUTAS_LAYER_URL, TRSC_WHERE_RUTAS, RUTAS_FIELDS, RUTAS_OUT, "empresa", "Rutas"
    )
    paradas_v0 = run_query_with_fallback(
        PARADAS_V0_LAYER_URL, TRSC_WHERE_PARADAS, PARADAS_V0_FIELDS, PARADAS_V0_OUT,
        "empresa", "Paradas_v0"
    )
    paradas_v1 = run_query_with_fallback(
        PARADAS_V1_LAYER_URL, TRSC_WHERE_PARADAS, PARADAS_V1_FIELDS, PARADAS_V1_OUT,
        "empresa", "Paradas_v1"
    )

    if not routes:
        print("\nRutas layer returned no TRSC/255 matches - nothing to join.")
        return

    if paradas_v0:
        print(f"\nJoining {len(routes)} route(s) with {len(paradas_v0)} stop(s) "
              f"from Paradas layer 0 (VM_Movilidad)...")
        result_v0 = join_routes_and_stops(routes, paradas_v0)
        JOINED_V0_OUT.write_text(json.dumps(result_v0, indent=2, ensure_ascii=False))
        summarize_join(result_v0, "layer 0 (VM_Movilidad)")
        print(f"Saved -> {JOINED_V0_OUT}")

    if paradas_v1:
        print(f"\nJoining {len(routes)} route(s) with {len(paradas_v1)} stop(s) "
              f"from Paradas layer 5 (VC_Transporte, Rutas' true sibling)...")
        result_v1 = join_routes_and_stops(routes, paradas_v1)
        JOINED_V1_OUT.write_text(json.dumps(result_v1, indent=2, ensure_ascii=False))
        summarize_join(result_v1, "layer 5 (VC_Transporte)")
        print(f"Saved -> {JOINED_V1_OUT}")

    if paradas_v0 and paradas_v1:
        print(
            f"\n{'='*60}\nCOMPARISON: layer 0 gave {len(paradas_v0)} matching "
            f"stop(s) ({result_v0['num_routes_with_matched_stops']}/{result_v0['num_routes']} "
            f"routes matched); layer 5 gave {len(paradas_v1)} matching stop(s) "
            f"({result_v1['num_routes_with_matched_stops']}/{result_v1['num_routes']} "
            f"routes matched). Layer 5 also carries real stop NAMES "
            f"('nombre' field) that layer 0 doesn't have at all - check "
            f"{PARADAS_V1_OUT} for that even if layer 0's route/stop coverage "
            f"turns out broader."
        )

    print(
        "\nCHECK BY EYE before trusting either join: match_basis shows which "
        "key linked each route to its stops - id_ruta is tried first, codigo "
        "as fallback (see module docstring). A route with match_basis=None "
        "or 0 matched stops means NEITHER key lined up for it in that "
        "layer's real data - check that layer's unmatched_paradas for "
        "anything that looks like it should have matched."
    )


if __name__ == "__main__":
    main()
