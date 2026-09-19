#!/usr/bin/env python3

import csv
import json
import time
from collections import defaultdict
from pathlib import Path

import requests


# ---------------------------------------------------------------------------
# Official Medellín ArcGIS services
# ---------------------------------------------------------------------------

ROUTE_LAYER = (
    "https://www.medellin.gov.co/"
    "servidormapas/rest/services/"
    "mapas_nacionales/VC_Transporte/MapServer/6"
)

PARADA_LAYER = (
    "https://www.medellin.gov.co/"
    "servidormapas/rest/services/"
    "transporte/VM_Movilidad/MapServer/0"
)

OUTPUT_DIR = Path("data/medellin")

PAGE_SIZE = 2000
TIMEOUT = 60
RETRIES = 4


session = requests.Session()

session.headers.update({
    "User-Agent": "MedellinPublicTransportRouteScraper/1.0"
})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def clean(value):
    """
    Normalize ArcGIS values.

    Important:
    id_ruta is INTEGER in Parada but STRING in the route layer.
    Therefore IDs are converted to strings.
    """

    if value is None:
        return ""

    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))

    return str(value).strip()


def get_json(url, params):
    """GET JSON with retry handling."""

    last_error = None

    for attempt in range(1, RETRIES + 1):

        try:
            response = session.get(
                url,
                params=params,
                timeout=TIMEOUT,
            )

            response.raise_for_status()

            data = response.json()

            if "error" in data:
                raise RuntimeError(
                    f"ArcGIS error: {data['error']}"
                )

            return data

        except Exception as exc:

            last_error = exc

            print(
                f"Request failed "
                f"{attempt}/{RETRIES}: {exc}"
            )

            if attempt < RETRIES:
                time.sleep(attempt * 2)

    raise RuntimeError(
        f"Request failed after {RETRIES} attempts"
    ) from last_error


# ---------------------------------------------------------------------------
# ArcGIS pagination
# ---------------------------------------------------------------------------

def fetch_features(
    layer_url,
    fields,
    return_geometry=False,
):
    """
    Retrieve all records from an ArcGIS Feature Layer.

    Uses pagination because Medellín's layers have a 2,000
    record maximum.
    """

    records = []
    offset = 0

    while True:

        params = {
            "where": "1=1",
            "outFields": ",".join(fields),
            "returnGeometry": (
                "true"
                if return_geometry
                else "false"
            ),
            "f": "json",
            "resultOffset": offset,
            "resultRecordCount": PAGE_SIZE,
        }

        print(
            f"GET {layer_url}/query "
            f"offset={offset}"
        )

        data = get_json(
            f"{layer_url}/query",
            params,
        )

        features = data.get(
            "features",
            [],
        )

        if not features:
            break

        records.extend(features)

        print(
            f"  received {len(features)} "
            f"(total {len(records)})"
        )

        offset += len(features)

        if (
            not data.get(
                "exceededTransferLimit",
                False,
            )
            and len(features) < PAGE_SIZE
        ):
            break

        time.sleep(0.25)

    return records


# ---------------------------------------------------------------------------
# Route data
# ---------------------------------------------------------------------------

def download_routes():

    fields = [
        "objectid",
        "nombre",
        "id_ruta",
        "codigo",
        "recorrido",
        "from_date",
        "sistema",
        "tipo",
        "empresa",
        "id_gflota",
        "fecha_actualizacion",
    ]

    return fetch_features(
        ROUTE_LAYER,
        fields,
        return_geometry=True,
    )


# ---------------------------------------------------------------------------
# Administrative information
# ---------------------------------------------------------------------------

def download_admin_data():

    fields = [
        "objectid",
        "id_paradero",
        "id_parada",
        "id_ruta",
        "nro_parada",
        "direccion",
        "tipo_parada",
        "recorrido",
        "codigo_ruta",
        "nombre_ruta",
        "sistema_ruta",
        "tipo_ruta",
        "empresa",
        "tipo_actoadmin",
        "numero_actoadmin",
        "anio_actoadmin",
        "estado",
        "fecha_actualizacion",
    ]

    return fetch_features(
        PARADA_LAYER,
        fields,
        return_geometry=False,
    )


# ---------------------------------------------------------------------------
# Administrative-act normalization
# ---------------------------------------------------------------------------

def normalize_admin_records(features):

    records = []

    for feature in features:

        a = feature.get(
            "attributes",
            {},
        )

        route_id = clean(
            a.get("id_ruta")
        )

        if not route_id:
            continue

        records.append({
            "id_ruta": route_id,

            "codigo_ruta": clean(
                a.get("codigo_ruta")
            ),

            "nombre_ruta": clean(
                a.get("nombre_ruta")
            ),

            "recorrido": clean(
                a.get("recorrido")
            ),

            "sistema_ruta": clean(
                a.get("sistema_ruta")
            ),

            "tipo_ruta": clean(
                a.get("tipo_ruta")
            ),

            "empresa": clean(
                a.get("empresa")
            ),

            "tipo_actoadmin": clean(
                a.get("tipo_actoadmin")
            ),

            "numero_actoadmin": clean(
                a.get("numero_actoadmin")
            ),

            "anio_actoadmin": clean(
                a.get("anio_actoadmin")
            ),

            "estado": clean(
                a.get("estado")
            ),

            "fecha_actualizacion": clean(
                a.get("fecha_actualizacion")
            ),
        })

    return records


# ---------------------------------------------------------------------------
# Deduplicate administrative acts
# ---------------------------------------------------------------------------

def deduplicate_admin_records(records):

    unique = {}

    for record in records:

        key = (
            record["id_ruta"],
            record["codigo_ruta"],
            record["recorrido"],
            record["tipo_actoadmin"],
            record["numero_actoadmin"],
            record["anio_actoadmin"],
        )

        unique[key] = record

    return list(unique.values())


# ---------------------------------------------------------------------------
# Index admin records by route
# ---------------------------------------------------------------------------

def index_admin_records(records):

    index = defaultdict(list)

    for record in records:

        index[
            record["id_ruta"]
        ].append(record)

    return dict(index)


# ---------------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------------

ADMIN_COLUMNS = [
    "id_ruta",
    "codigo_ruta",
    "nombre_ruta",
    "recorrido",
    "sistema_ruta",
    "tipo_ruta",
    "empresa",
    "tipo_actoadmin",
    "numero_actoadmin",
    "anio_actoadmin",
    "estado",
    "fecha_actualizacion",
]


ROUTE_COLUMNS = [
    "id_ruta",
    "codigo_ruta",
    "nombre_ruta",
    "recorrido",
    "sistema",
    "tipo",
    "empresa",
    "id_gflota",
    "from_date",
    "tipo_actoadmin",
    "numero_actoadmin",
    "anio_actoadmin",
    "estado",
    "fecha_actualizacion",
]


def write_csv(
    filename,
    rows,
    columns,
):

    path = OUTPUT_DIR / filename

    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=columns,
            extrasaction="ignore",
        )

        writer.writeheader()

        writer.writerows(rows)

    print(
        f"Wrote {len(rows)} records -> {path}"
    )


# ---------------------------------------------------------------------------
# GeoJSON
# ---------------------------------------------------------------------------

def build_geojson(
    route_features,
    admin_index,
):

    output = {
        "type": "FeatureCollection",
        "features": [],
    }

    for feature in route_features:

        a = feature.get(
            "attributes",
            {},
        )

        route_id = clean(
            a.get("id_ruta")
        )

        admin = admin_index.get(
            route_id,
            [],
        )

        administrative_acts = []

        for record in admin:

            administrative_acts.append({
                "tipo": record[
                    "tipo_actoadmin"
                ],
                "numero": record[
                    "numero_actoadmin"
                ],
                "anio": record[
                    "anio_actoadmin"
                ],
                "estado": record[
                    "estado"
                ],
            })

        properties = {
            "id_ruta": route_id,

            "codigo_ruta": clean(
                a.get("codigo")
            ),

            "nombre_ruta": clean(
                a.get("nombre")
            ),

            "recorrido": clean(
                a.get("recorrido")
            ),

            "sistema": clean(
                a.get("sistema")
            ),

            "tipo": clean(
                a.get("tipo")
            ),

            "empresa": clean(
                a.get("empresa")
            ),

            "id_gflota": clean(
                a.get("id_gflota")
            ),

            "from_date": clean(
                a.get("from_date")
            ),

            "administrative_acts":
                administrative_acts,

            "fecha_actualizacion": clean(
                a.get(
                    "fecha_actualizacion"
                )
            ),
        }

        output["features"].append({
            "type": "Feature",

            "geometry": feature.get(
                "geometry"
            ),

            "properties": properties,
        })

    return output


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("=" * 70)
    print(
        "MEDELLÍN PUBLIC TRANSPORT ROUTE SCRAPER"
    )
    print("=" * 70)

    # ---------------------------------------------------------------
    # Routes
    # ---------------------------------------------------------------

    print("\n1. Downloading routes")

    route_features = download_routes()

    print(
        f"Routes downloaded: "
        f"{len(route_features)}"
    )

    # ---------------------------------------------------------------
    # Paradas / administrative data
    # ---------------------------------------------------------------

    print(
        "\n2. Downloading Parada records"
    )

    parada_features = download_admin_data()

    print(
        f"Parada records downloaded: "
        f"{len(parada_features)}"
    )

    # ---------------------------------------------------------------
    # Normalize administrative records
    # ---------------------------------------------------------------

    print(
        "\n3. Extracting administrative acts"
    )

    admin_records = normalize_admin_records(
        parada_features
    )

    print(
        f"Records containing route IDs: "
        f"{len(admin_records)}"
    )

    # ---------------------------------------------------------------
    # Deduplicate
    # ---------------------------------------------------------------

    admin_records = (
        deduplicate_admin_records(
            admin_records
        )
    )

    print(
        f"Unique route/admin-act records: "
        f"{len(admin_records)}"
    )

    # ---------------------------------------------------------------
    # Index
    # ---------------------------------------------------------------

    admin_index = index_admin_records(
        admin_records
    )

    print(
        f"Routes with administrative data: "
        f"{len(admin_index)}"
    )

    # ---------------------------------------------------------------
    # Write administrative CSV
    # ---------------------------------------------------------------

    write_csv(
        "route_admin_acts.csv",
        admin_records,
        ADMIN_COLUMNS,
    )

    # ---------------------------------------------------------------
    # Build route CSV
    # ---------------------------------------------------------------

    route_rows = []

    routes_with_admin = 0

    for feature in route_features:

        a = feature.get(
            "attributes",
            {},
        )

        route_id = clean(
            a.get("id_ruta")
        )

        admin = admin_index.get(
            route_id,
            [],
        )

        if admin:
            routes_with_admin += 1

        route_rows.append({

            "id_ruta":
                route_id,

            "codigo_ruta":
                clean(a.get("codigo")),

            "nombre_ruta":
                clean(a.get("nombre")),

            "recorrido":
                clean(a.get("recorrido")),

            "sistema":
                clean(a.get("sistema")),

            "tipo":
                clean(a.get("tipo")),

            "empresa":
                clean(a.get("empresa")),

            "id_gflota":
                clean(a.get("id_gflota")),

            "from_date":
                clean(a.get("from_date")),

            "tipo_actoadmin":
                "; ".join(
                    x["tipo_actoadmin"]
                    for x in admin
                ),

            "numero_actoadmin":
                "; ".join(
                    x["numero_actoadmin"]
                    for x in admin
                ),

            "anio_actoadmin":
                "; ".join(
                    x["anio_actoadmin"]
                    for x in admin
                ),

            "estado":
                "; ".join(
                    x["estado"]
                    for x in admin
                ),

            "fecha_actualizacion":
                clean(
                    a.get(
                        "fecha_actualizacion"
                    )
                ),
        })

    write_csv(
        "routes.csv",
        route_rows,
        ROUTE_COLUMNS,
    )

    # ---------------------------------------------------------------
    # GeoJSON
    # ---------------------------------------------------------------

    print(
        "\n4. Writing GeoJSON"
    )

    geojson = build_geojson(
        route_features,
        admin_index,
    )

    geojson_path = (
        OUTPUT_DIR /
        "routes.geojson"
    )

    with geojson_path.open(
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            geojson,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(
        f"Wrote {len(route_features)} "
        f"features -> {geojson_path}"
    )

    # ---------------------------------------------------------------
    # Diagnostics
    # ---------------------------------------------------------------

    print("\n" + "=" * 70)
    print("DIAGNOSTICS")
    print("=" * 70)

    print(
        f"Route features:          "
        f"{len(route_features)}"
    )

    print(
        f"Parada records:          "
        f"{len(parada_features)}"
    )

    print(
        f"Admin records:           "
        f"{len(admin_records)}"
    )

    print(
        f"Routes with admin data:  "
        f"{routes_with_admin}"
    )

    print(
        f"Routes without admin:    "
        f"{len(route_features) - routes_with_admin}"
    )

    # Show examples
    print(
        "\nFirst administrative records:"
    )

    for record in admin_records[:10]:

        print(
            f"  route={record['id_ruta']} "
            f"code={record['codigo_ruta']} "
            f"act={record['tipo_actoadmin']} "
            f"{record['numero_actoadmin']}/"
            f"{record['anio_actoadmin']} "
            f"estado={record['estado']}"
        )

    print(
        "\nScraping completed successfully."
    )


if __name__ == "__main__":
    main()
