```python
#!/usr/bin/env python3

import csv
import json
import time
from collections import defaultdict
from pathlib import Path

import requests


# ---------------------------------------------------------------------------
# Medellín official ArcGIS REST services
# ---------------------------------------------------------------------------

ROUTE_LAYER = (
    "https://www.medellin.gov.co/"
    "servidormapas/rest/services/"
    "mapas_nacionales/VC_Transporte/MapServer/6"
)

STOP_LAYER = (
    "https://www.medellin.gov.co/"
    "servidormapas/rest/services/"
    "transporte/VM_Movilidad/MapServer/0"
)

OUTPUT_DIR = Path("data/medellin")

PAGE_SIZE = 2000
REQUEST_TIMEOUT = 60
RETRIES = 4
SLEEP_BETWEEN_REQUESTS = 0.2


session = requests.Session()
session.headers.update(
    {
        "User-Agent": (
            "Mozilla/5.0 "
            "(compatible; MedellinRouteScraper/1.0)"
        )
    }
)


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def request_json(url, params):
    """GET JSON from ArcGIS with retries."""

    last_error = None

    for attempt in range(1, RETRIES + 1):
        try:
            response = session.get(
                url,
                params=params,
                timeout=REQUEST_TIMEOUT,
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
                f"(attempt {attempt}/{RETRIES}): {exc}"
            )

            if attempt < RETRIES:
                time.sleep(attempt * 2)

    raise RuntimeError(
        f"Request failed after {RETRIES} attempts"
    ) from last_error


# ---------------------------------------------------------------------------
# ArcGIS pagination
# ---------------------------------------------------------------------------

def fetch_all_features(layer_url, out_fields, geometry=False):
    """
    Download all records from an ArcGIS Feature Layer.

    Uses resultOffset/resultRecordCount pagination.
    """

    all_features = []
    offset = 0

    while True:
        params = {
            "where": "1=1",
            "outFields": ",".join(out_fields),
            "returnGeometry": "true" if geometry else "false",
            "f": "json",
            "resultOffset": offset,
            "resultRecordCount": PAGE_SIZE,
            "orderByFields": "OBJECTID",
        }

        print(
            f"Downloading {layer_url} "
            f"offset={offset} ..."
        )

        data = request_json(
            f"{layer_url}/query",
            params,
        )

        features = data.get("features", [])

        if not features:
            break

        all_features.extend(features)

        print(
            f"  received {len(features)} "
            f"(total={len(all_features)})"
        )

        offset += len(features)

        # ArcGIS can explicitly tell us that more records exist.
        exceeded = data.get("exceededTransferLimit", False)

        if not exceeded and len(features) < PAGE_SIZE:
            break

        time.sleep(SLEEP_BETWEEN_REQUESTS)

    return all_features


# ---------------------------------------------------------------------------
# Route layer
# ---------------------------------------------------------------------------

def fetch_routes():
    fields = [
        "OBJECTID",
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

    return fetch_all_features(
        ROUTE_LAYER,
        fields,
        geometry=True,
    )


# ---------------------------------------------------------------------------
# Administrative information
# ---------------------------------------------------------------------------

def fetch_route_admin_records():
    fields = [
        "OBJECTID",
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

    return fetch_all_features(
        STOP_LAYER,
        fields,
        geometry=False,
    )


# ---------------------------------------------------------------------------
# Normalisation
# ---------------------------------------------------------------------------

def clean(value):
    if value is None:
        return ""

    if isinstance(value, str):
        return value.strip()

    return value


def route_admin_key(attributes):
    """
    Key used to deduplicate the administrative records.

    A route may have many stops, so the same route/admin-act
    combination normally occurs many times in the Parada layer.
    """

    return (
        clean(attributes.get("id_ruta")),
        clean(attributes.get("codigo_ruta")),
        clean(attributes.get("recorrido")),
        clean(attributes.get("tipo_actoadmin")),
        clean(attributes.get("numero_actoadmin")),
        clean(attributes.get("anio_actoadmin")),
    )


def build_admin_index(features):
    """
    Build:

        id_ruta -> list of administrative records

    while retaining distinct administrative acts.
    """

    index = defaultdict(dict)

    for feature in features:
        attrs = feature.get("attributes", {})

        key = route_admin_key(attrs)

        route_id = clean(attrs.get("id_ruta"))

        if not route_id:
            continue

        index[route_id][key] = attrs

    return {
        route_id: list(records.values())
        for route_id, records in index.items()
    }


# ---------------------------------------------------------------------------
# CSV output
# ---------------------------------------------------------------------------

ROUTE_COLUMNS = [
    "id_ruta",
    "codigo_ruta",
    "nombre_ruta",
    "recorrido",
    "sistema_ruta",
    "tipo_ruta",
    "empresa",
    "id_gflota",
    "from_date",
    "tipo_actoadmin",
    "numero_actoadmin",
    "anio_actoadmin",
    "estado",
    "fecha_actualizacion",
]


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


def write_csv(path, rows, columns):
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

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

        for row in rows:
            writer.writerow(row)


# ---------------------------------------------------------------------------
# GeoJSON
# ---------------------------------------------------------------------------

def build_geojson(routes, admin_index):
    features = []

    for feature in routes:
        attrs = feature.get("attributes", {})
        geometry = feature.get("geometry")

        route_id = clean(attrs.get("id_ruta"))

        admin_records = admin_index.get(
            route_id,
            [],
        )

        # If there are multiple administrative acts,
        # retain all of them in the GeoJSON properties.
        acts = []

        for admin in admin_records:
            acts.append(
                {
                    "tipo_actoadmin": clean(
                        admin.get("tipo_actoadmin")
                    ),
                    "numero_actoadmin": clean(
                        admin.get("numero_actoadmin")
                    ),
                    "anio_actoadmin": clean(
                        admin.get("anio_actoadmin")
                    ),
                    "estado": clean(
                        admin.get("estado")
                    ),
                }
            )

        properties = {
            "id_ruta": route_id,
            "codigo_ruta": clean(
                attrs.get("codigo")
            ),
            "nombre_ruta": clean(
                attrs.get("nombre")
            ),
            "recorrido": clean(
                attrs.get("recorrido")
            ),
            "sistema": clean(
                attrs.get("sistema")
            ),
            "tipo": clean(
                attrs.get("tipo")
            ),
            "empresa": clean(
                attrs.get("empresa")
            ),
            "id_gflota": attrs.get(
                "id_gflota"
            ),
            "from_date": attrs.get(
                "from_date"
            ),
            "fecha_actualizacion": attrs.get(
                "fecha_actualizacion"
            ),
            "administrative_acts": acts,
        }

        features.append(
            {
                "type": "Feature",
                "geometry": geometry,
                "properties": properties,
            }
        )

    return {
        "type": "FeatureCollection",
        "features": features,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("=" * 70)
    print("Medellín Public Transport Route Scraper")
    print("=" * 70)

    # ---------------------------------------------------------------
    # 1. Download route geometry
    # ---------------------------------------------------------------

    print("\nDownloading route layer...")

    route_features = fetch_routes()

    print(
        f"\nDownloaded {len(route_features)} "
        f"route features."
    )

    # ---------------------------------------------------------------
    # 2. Download stops/admin records
    # ---------------------------------------------------------------

    print("\nDownloading Parada layer...")

    admin_features = fetch_route_admin_records()

    print(
        f"\nDownloaded {len(admin_features)} "
        f"stop records."
    )

    # ---------------------------------------------------------------
    # 3. Build administrative-act index
    # ---------------------------------------------------------------

    print("\nBuilding administrative-act index...")

    admin_index = build_admin_index(
        admin_features
    )

    # ---------------------------------------------------------------
    # 4. Build route rows
    # ---------------------------------------------------------------

    route_rows = []
    admin_rows = []

    for feature in route_features:
        attrs = feature.get("attributes", {})

        route_id = clean(
            attrs.get("id_ruta")
        )

        admin_records = admin_index.get(
            route_id,
            [],
        )

        # -----------------------------------------------------------
        # Route CSV
        # -----------------------------------------------------------

        # A route can have more than one administrative act.
        # The CSV therefore uses a semicolon-separated representation.
        act_values = []

        for admin in admin_records:
            act = (
                f"{clean(admin.get('tipo_actoadmin'))} "
                f"{clean(admin.get('numero_actoadmin'))}/"
                f"{clean(admin.get('anio_actoadmin'))}"
            )

            act_values.append(act)

        route_rows.append(
            {
                "id_ruta": route_id,
                "codigo_ruta": clean(
                    attrs.get("codigo")
                ),
                "nombre_ruta": clean(
                    attrs.get("nombre")
                ),
                "recorrido": clean(
                    attrs.get("recorrido")
                ),
                "sistema_ruta": clean(
                    attrs.get("sistema")
                ),
                "tipo_ruta": clean(
                    attrs.get("tipo")
                ),
                "empresa": clean(
                    attrs.get("empresa")
                ),
                "id_gflota": attrs.get(
                    "id_gflota"
                ),
                "from_date": attrs.get(
                    "from_date"
                ),
                "tipo_actoadmin": "; ".join(
                    clean(
                        x.get(
                            "tipo_actoadmin"
                        )
                    )
                    for x in admin_records
                ),
                "numero_actoadmin": "; ".join(
                    clean(
                        x.get(
                            "numero_actoadmin"
                        )
                    )
                    for x in admin_records
                ),
                "anio_actoadmin": "; ".join(
                    str(
                        clean(
                            x.get(
                                "anio_actoadmin"
                            )
                        )
                    )
                    for x in admin_records
                ),
                "estado": "; ".join(
                    clean(
                        x.get("estado")
                    )
                    for x in admin_records
                ),
                "fecha_actualizacion": attrs.get(
                    "fecha_actualizacion"
                ),
            }
        )

        # -----------------------------------------------------------
        # Administrative-act CSV
        # -----------------------------------------------------------

        for admin in admin_records:
            admin_rows.append(
                {
                    "id_ruta": route_id,
                    "codigo_ruta": clean(
                        admin.get(
                            "codigo_ruta"
                        )
                    ),
                    "nombre_ruta": clean(
                        admin.get(
                            "nombre_ruta"
                        )
                    ),
                    "recorrido": clean(
                        admin.get(
                            "recorrido"
                        )
                    ),
                    "sistema_ruta": clean(
                        admin.get(
                            "sistema_ruta"
                        )
                    ),
                    "tipo_ruta": clean(
                        admin.get(
                            "tipo_ruta"
                        )
                    ),
                    "empresa": clean(
                        admin.get(
                            "empresa"
                        )
                    ),
                    "tipo_actoadmin": clean(
                        admin.get(
                            "tipo_actoadmin"
                        )
                    ),
                    "numero_actoadmin": clean(
                        admin.get(
                            "numero_actoadmin"
                        )
                    ),
                    "anio_actoadmin": clean(
                        admin.get(
                            "anio_actoadmin"
                        )
                    ),
                    "estado": clean(
                        admin.get(
                            "estado"
                        )
                    ),
                    "fecha_actualizacion": admin.get(
                        "fecha_actualizacion"
                    ),
                }
            )

    # ---------------------------------------------------------------
    # 5. Write CSV
    # ---------------------------------------------------------------

    print("\nWriting routes.csv...")

    write_csv(
        OUTPUT_DIR / "routes.csv",
        route_rows,
        ROUTE_COLUMNS,
    )

    print(
        f"  {len(route_rows)} route records"
    )

    print("\nWriting route_admin_acts.csv...")

    write_csv(
        OUTPUT_DIR / "route_admin_acts.csv",
        admin_rows,
        ADMIN_COLUMNS,
    )

    print(
        f"  {len(admin_rows)} "
        f"route/admin-act records"
    )

    # ---------------------------------------------------------------
    # 6. Write GeoJSON
    # ---------------------------------------------------------------

    print("\nWriting routes.geojson...")

    geojson = build_geojson(
        route_features,
        admin_index,
    )

    with (
        OUTPUT_DIR / "routes.geojson"
    ).open(
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
        f"  {len(geojson['features'])} "
        f"GeoJSON features"
    )

    # ---------------------------------------------------------------
    # 7. Diagnostics
    # ---------------------------------------------------------------

    routes_without_admin = []

    for feature in route_features:
        attrs = feature.get(
            "attributes",
            {},
        )

        route_id = clean(
            attrs.get("id_ruta")
        )

        if route_id not in admin_index:
            routes_without_admin.append(
                route_id
            )

    print("\nDiagnostics")
    print("-" * 70)

    print(
        f"Routes:                 {len(route_features)}"
    )

    print(
        f"Admin records:          {len(admin_rows)}"
    )

    print(
        f"Routes with admin act:  "
        f"{len(route_features) - len(routes_without_admin)}"
    )

    print(
        f"Routes without admin:   "
        f"{len(routes_without_admin)}"
    )

    if routes_without_admin:
        print("\nRoutes without administrative information:")

        for route_id in routes_without_admin:
            print(
                f"  {route_id}"
            )

    print("\nFinished.")


if __name__ == "__main__":
    main()

