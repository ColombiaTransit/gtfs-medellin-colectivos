#!/usr/bin/env python3
"""
Query TWO of Medellín's official government ArcGIS layers for
Transportes Rapido San Cristobal / route "255" data, and cross-reference
them client-side (these are two separate ArcGIS services - the REST API
doesn't support a server-side SQL join across them, so this script
fetches both and matches records in Python):

  1. "Rutas de transporte publico" (mapas_nacionales/VC_Transporte/
     MapServer/6) - POLYLINE geometry per route: nombre, id_ruta,
     codigo, recorrido, sistema, tipo, empresa.
  2. "Parada" (transporte/VM_Movilidad/MapServer/0) - POINT stops:
     id_ruta, codigo_ruta, nombre_ruta, sistema_ruta, empresa,
     latitud/longitud, direccion, nro_parada.

SUPERSEDES scripts/query_medellin_paradas_trsc.py (the Paradas-only
version) - this does everything that one did, plus the Rutas layer and
the cross-reference step the person running this project asked for.

WHY THIS MATTERS: if TRSC's 255-family routes are represented in
either layer, this would be genuinely official, government-sourced
route geometry and/or stop locations - categorically better than the
photographed schedule boards and Google-My-Maps-only line geometry
this project has had for every TRSC route so far (all 25 confirmed
line-only via KML, zero real stop points).

UNTESTED AGAINST REAL RESULTS - genuinely, for both layers. The
environment that wrote this script could fetch each layer's METADATA
directly (confirming the field names above are real - see the
conversation this script came from), but every attempt to fetch an
actual QUERY result (adding a `where=` clause and other parameters, on
EITHER layer) returned the same blank HTML query FORM page instead of
real JSON data - the fetching tool available seems to strip
query-string parameters for this whole medellin.gov.co domain, not
just one layer. This script's query logic is standard ArcGIS REST API
usage (the same pattern already used successfully elsewhere in this
project for other ArcGIS layers, e.g. the Metro colectivos data), but
it has NOT been run against real data by the environment that wrote
it - only its pagination and error-handling logic were unit-tested
against synthetic ArcGIS-shaped responses. Run it for real and share
the output back.

JOIN STRATEGY: id_ruta is tried FIRST (per the project owner's
hypothesis that both layers, hosted on the same government server,
share one underlying internal route-numbering system - plausible since
they're maintained by the same department), with codigo == codigo_ruta
as a fallback. The two layers' id_ruta fields don't share a consistent
TYPE - confirmed from each layer's real metadata: Rutas' id_ruta is a
STRING field, Parada's is an INTEGER field - but this script's join
normalizes both to strings before comparing, so id_ruta=9001 (int) and
id_ruta="9001" (string) DO match correctly. CORRECTION to an earlier
version of this docstring: it claimed the id_ruta fallback "essentially
cannot match in practice," based on a synthetic test that used
arbitrary, deliberately UNRELATED id values on each side - that only
tested whether the comparison mechanism works at all (it does), not
whether real id_ruta values actually correspond between the two
layers, which remains genuinely unknown until this runs against real
data.

Usage: python scripts/query_medellin_transporte_trsc.py
Output: raw/medellin_rutas_trsc.json (matching route/line records)
        raw/medellin_paradas_trsc.json (matching stop records)
        raw/medellin_transporte_trsc_joined.json (cross-referenced:
        each matched route with its matched stops, plus anything that
        didn't join on either side)
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
PARADAS_LAYER_URL = "https://www.medellin.gov.co/servidormapas/rest/services/transporte/VM_Movilidad/MapServer/0/query"

RUTAS_OUT = Path("raw/medellin_rutas_trsc.json")
PARADAS_OUT = Path("raw/medellin_paradas_trsc.json")
JOINED_OUT = Path("raw/medellin_transporte_trsc_joined.json")

RUTAS_FIELDS = ["objectid", "nombre", "id_ruta", "codigo", "recorrido",
                "sistema", "tipo", "empresa", "id_gflota"]
PARADAS_FIELDS = ["id_paradero", "id_parada", "id_ruta", "nro_parada", "direccion",
                   "tipo_parada", "recorrido", "codigo_ruta", "nombre_ruta",
                   "sistema_ruta", "tipo_ruta", "empresa", "latitud", "longitud", "estado"]

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


def main():
    routes = run_query_with_fallback(
        RUTAS_LAYER_URL, TRSC_WHERE_RUTAS, RUTAS_FIELDS, RUTAS_OUT, "empresa", "Rutas"
    )
    paradas = run_query_with_fallback(
        PARADAS_LAYER_URL, TRSC_WHERE_PARADAS, PARADAS_FIELDS, PARADAS_OUT, "empresa", "Paradas"
    )

    if not routes and not paradas:
        print("\nNeither layer returned any TRSC/255 matches - nothing to join.")
        return

    print(f"\nJoining {len(routes)} route(s) with {len(paradas)} stop(s)...")
    result = join_routes_and_stops(routes, paradas)
    JOINED_OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False))

    print(f"\n{result['num_routes_with_matched_stops']} / {result['num_routes']} "
          f"route(s) have at least one matched stop.")
    print(f"{len(result['unmatched_paradas'])} stop(s) didn't match any route "
          f"found in the Rutas layer.")
    for j in result["joined_routes"]:
        r = j["route"]
        print(f"  {r.get('codigo')} - {r.get('nombre')}: "
              f"{j['num_matched_stops']} stop(s) [{j['match_basis'] or 'no match'}]")

    print(f"\nSaved -> {JOINED_OUT}")
    print(
        "\nCHECK BY EYE before trusting the join: match_basis shows which key "
        "linked each route to its stops - id_ruta is tried first, codigo as "
        "fallback (see module docstring). A route with match_basis=None or "
        "0 matched stops means NEITHER key lined up for it in the real data - "
        "check unmatched_paradas for anything that looks like it should "
        "have matched, since a real mismatch here (rather than no real "
        "stops existing) is entirely possible until this has been checked "
        "against actual results."
    )


if __name__ == "__main__":
    main()
