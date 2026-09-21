#!/usr/bin/env python3
"""
Filter and cross-reference an operator's routes/stops from the LOCAL
bulk data downloaded by scripts/download_medellin_transporte_layers.py
- no network calls at all. Run the downloader first (or periodically,
on a schedule), then run this as many times as needed for whichever
operator matters right now, instantly and offline.

Reuses the join logic already validated for TRSC (see
scripts/query_medellin_transporte_trsc.py and the conversation it
came from): id_ruta tried first, codigo == codigo_ruta as fallback,
both normalized to strings since Rutas' id_ruta is a STRING field and
Parada layers' id_ruta fields are INTEGER (confirmed from each layer's
real metadata).

Usage: python scripts/query_local_medellin_operator.py "San Cristobal"
       python scripts/query_local_medellin_operator.py "Sotrames" --code-hint 3
       python scripts/query_local_medellin_operator.py --list-empresas
Requires: raw/medellin_raw/*.json already present (run the downloader
first).
Output: raw/medellin_local_<slug>_routes.json
        raw/medellin_local_<slug>_stops_<layer_label>.json (one per
        Parada-shaped layer that had a route match)
        raw/medellin_local_<slug>_joined_<layer_label>.json
"""

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

RAW_DIR = Path("raw/medellin_raw")

ROUTE_LAYERS = ["vc_transporte_rutas", "vm_movilidad_rutas_unificadas",
                 "vm_movilidad_rutas_transporte_publico"]
STOP_LAYERS = ["vc_transporte_parada", "vm_movilidad_parada"]

# Field names differ slightly between layers (confirmed from each
# layer's real metadata) - map the ones this script actually reads.
ROUTE_FIELD_CANDIDATES = {
    "empresa": ["empresa"],
    "codigo": ["codigo", "codigo_ruta"],
    "nombre": ["nombre", "nombre_ruta"],
    "id_ruta": ["id_ruta"],
}
STOP_FIELD_CANDIDATES = {
    "empresa": ["empresa"],
    "codigo": ["codigo_ruta", "codigo"],
    "nombre": ["nombre_ruta", "nombre"],
    "id_ruta": ["id_ruta"],
}


def get_field(attrs: dict, candidates: list):
    for c in candidates:
        if c in attrs and attrs[c] is not None:
            return attrs[c]
    return None


def load_layer(label: str) -> list:
    path = RAW_DIR / f"{label}.json"
    if not path.exists():
        print(f"  {label}: not found at {path} - skipping (run the downloader "
              f"first if this is unexpected)", file=sys.stderr)
        return []
    return json.loads(path.read_text())


def strip_accents(s: str) -> str:
    """Real operator names in this data have accents ('Rápido San
    Cristóbal') - the original ArcGIS SQL query (UPPER(empresa) LIKE
    '%CRISTOBAL%', no accent) matched that successfully, meaning the
    database's collation is accent-insensitive server-side. Plain
    Python substring matching is NOT accent-insensitive by default -
    confirmed by testing this exact case, where 'San Cristobal' failed
    to match 'Rápido San Cristóbal' until this normalization was
    added. Without it, this script would silently miss real operators
    whenever their name is typed without the accent someone would
    naturally omit."""
    return "".join(c for c in unicodedata.normalize("NFKD", s)
                    if not unicodedata.combining(c))


def matches_operator(attrs: dict, field_map: dict, operator_query: str) -> bool:
    empresa = get_field(attrs, field_map["empresa"])
    if not empresa:
        return False
    return strip_accents(operator_query.upper()) in strip_accents(str(empresa).upper())


def list_distinct_empresas():
    seen = set()
    for label in ROUTE_LAYERS + STOP_LAYERS:
        features = load_layer(label)
        field_map = ROUTE_FIELD_CANDIDATES if label in ROUTE_LAYERS else STOP_FIELD_CANDIDATES
        for f in features:
            v = get_field(f["attributes"], field_map["empresa"])
            if v:
                seen.add(str(v).strip())
    for v in sorted(seen):
        print(v)
    print(f"\n{len(seen)} distinct empresa value(s) across all downloaded layers.")


def join_routes_and_stops(routes: list, stops: list, route_field_map, stop_field_map) -> dict:
    def norm(v):
        return str(v).strip().upper() if v is not None else None

    stops_by_codigo, stops_by_id_ruta = {}, {}
    for s in stops:
        a = s["attributes"]
        c = norm(get_field(a, stop_field_map["codigo"]))
        if c:
            stops_by_codigo.setdefault(c, []).append(s)
        i = norm(get_field(a, stop_field_map["id_ruta"]))
        if i:
            stops_by_id_ruta.setdefault(i, []).append(s)

    joined = []
    for route in routes:
        a = route["attributes"]
        codigo_key = norm(get_field(a, route_field_map["codigo"]))
        id_ruta_key = norm(get_field(a, route_field_map["id_ruta"]))

        matched = stops_by_id_ruta.get(id_ruta_key, [])
        basis = "id_ruta" if matched else None
        if not matched:
            matched = stops_by_codigo.get(codigo_key, [])
            basis = "codigo" if matched else None

        joined.append({
            "route": a, "num_matched_stops": len(matched),
            "match_basis": basis, "matched_stops": [m["attributes"] for m in matched],
        })

    return {
        "joined_routes": joined,
        "num_routes": len(routes),
        "num_routes_with_matched_stops": sum(1 for j in joined if j["num_matched_stops"] > 0),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operator", nargs="?", help="Substring to match against each "
                         "layer's 'empresa' field, case-insensitive (e.g. 'San Cristobal', "
                         "'Sotrames', 'Coonatra')")
    parser.add_argument("--list-empresas", action="store_true",
                         help="List every distinct empresa value found across all "
                              "downloaded layers, then exit")
    args = parser.parse_args()

    if not RAW_DIR.exists():
        print(f"{RAW_DIR} not found - run "
              f"scripts/download_medellin_transporte_layers.py first.", file=sys.stderr)
        sys.exit(1)

    if args.list_empresas:
        list_distinct_empresas()
        return

    if not args.operator:
        parser.error("operator is required unless --list-empresas is given")

    slug = re.sub(r"[^\w]+", "_", args.operator.strip()).strip("_").lower()

    all_routes = []
    for label in ROUTE_LAYERS:
        features = load_layer(label)
        matched = [f for f in features if matches_operator(f["attributes"], ROUTE_FIELD_CANDIDATES, args.operator)]
        print(f"  {label}: {len(matched)} / {len(features)} route(s) match {args.operator!r}")
        for m in matched:
            m["_source_layer"] = label
        all_routes.extend(matched)

    if not all_routes:
        print(f"\nNo routes found for {args.operator!r} in any downloaded route layer. "
              f"Run with --list-empresas to see what operator names actually exist "
              f"in the local data.")
        return

    routes_out = Path(f"raw/medellin_local_{slug}_routes.json")
    routes_out.write_text(json.dumps(all_routes, indent=2, ensure_ascii=False))
    print(f"\n{len(all_routes)} total route(s) -> {routes_out}")

    for stop_label in STOP_LAYERS:
        stops = load_layer(stop_label)
        matched_stops = [s for s in stops if matches_operator(s["attributes"], STOP_FIELD_CANDIDATES, args.operator)]
        print(f"\n  {stop_label}: {len(matched_stops)} / {len(stops)} stop(s) match {args.operator!r}")
        if not matched_stops:
            continue

        stops_out = Path(f"raw/medellin_local_{slug}_stops_{stop_label}.json")
        stops_out.write_text(json.dumps(matched_stops, indent=2, ensure_ascii=False))
        print(f"  Saved -> {stops_out}")

        result = join_routes_and_stops(all_routes, matched_stops, ROUTE_FIELD_CANDIDATES, STOP_FIELD_CANDIDATES)
        joined_out = Path(f"raw/medellin_local_{slug}_joined_{stop_label}.json")
        joined_out.write_text(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"  {result['num_routes_with_matched_stops']} / {result['num_routes']} "
              f"route(s) matched at least one stop -> {joined_out}")


if __name__ == "__main__":
    main()
