#!/usr/bin/env python3

import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import parse_qs, urlparse, urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.sao6.com.co"
ROUTES_URL = f"{BASE_URL}/rutas"

OUTPUT_DIR = Path("sao6_data")
MAPS_DIR = OUTPUT_DIR / "maps"

HTML_FILE = OUTPUT_DIR / "rutas.html"
ROUTES_JSON_FILE = OUTPUT_DIR / "sao6_rutas.json"
MAP_REPORT_FILE = MAPS_DIR / "map_probe_report.json"

TIMEOUT = 30
MAP_DELAY_SECONDS = 1.0

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0 Safari/537.36"
)


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------

session = requests.Session()
session.headers.update(
    {
        "User-Agent": USER_AGENT,
        "Accept": "*/*",
    }
)


def download(url: str) -> requests.Response:
    response = session.get(url, timeout=TIMEOUT)
    response.raise_for_status()
    return response


# ---------------------------------------------------------------------------
# JavaScript parsing
# ---------------------------------------------------------------------------

def find_matching_bracket(text: str, start: int) -> int:
    """
    Find the closing ] matching the [ at `start`.

    Handles strings so brackets inside quoted strings do not interfere.
    """

    depth = 0
    quote = None
    escaped = False

    for i in range(start, len(text)):
        char = text[i]

        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None

            continue

        if char in ('"', "'", "`"):
            quote = char
            continue

        if char == "[":
            depth += 1

        elif char == "]":
            depth -= 1

            if depth == 0:
                return i

    raise ValueError("Could not find matching closing bracket")


def find_array_assignments(js: str):
    """
    Find JavaScript assignments such as:

        const e=[...]
        ,e=[...]
        ;e=[...]

    Returns (variable_name, array_text).
    """

    results = []

    pattern = re.compile(
        r"(?:const|let|var)?\s*([A-Za-z_$][\w$]*)\s*=\s*\["
    )

    for match in pattern.finditer(js):
        variable = match.group(1)

        # Find the opening [
        start = js.find("[", match.start(), match.end())

        try:
            end = find_matching_bracket(js, start)
        except ValueError:
            continue

        array_text = js[start : end + 1]

        results.append((variable, array_text))

    return results


def js_object_to_json(text: str) -> str:
    """
    Convert the simple JavaScript object syntax used by the SAO6 bundle
    into JSON.

    Example:

        [{codigo:"C6-001",nombre:"Santa Rita"}]

    becomes:

        [{"codigo":"C6-001","nombre":"Santa Rita"}]

    Only unquoted property names are modified.
    """

    result = []
    i = 0
    quote = None
    escaped = False

    while i < len(text):
        char = text[i]

        if quote:
            result.append(char)

            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None

            i += 1
            continue

        if char in ('"', "'", "`"):
            quote = char
            result.append(char)
            i += 1
            continue

        # Detect bare object property names:
        #
        # {codigo:
        # ,nombre:
        #
        if char.isalpha() or char in "_$":
            match = re.match(
                r"[A-Za-z_$][A-Za-z0-9_$]*",
                text[i:]
            )

            if match:
                word = match.group(0)

                j = i + len(word)

                # Skip whitespace
                k = j
                while k < len(text) and text[k].isspace():
                    k += 1

                if k < len(text) and text[k] == ":":
                    result.append('"')
                    result.append(word)
                    result.append('"')

                    i = j
                    continue

                result.append(word)
                i = j
                continue

        result.append(char)
        i += 1

    return "".join(result)


def extract_routes(js: str):
    assignments = find_array_assignments(js)

    print(f"Found {len(assignments)} array assignments")

    candidates = []

    for variable, array_text in assignments:
        if "codigo" not in array_text:
            continue

        print(
            f"Candidate variable={variable} "
            f"size={len(array_text):,}"
        )

        candidates.append((variable, array_text))

    for variable, array_text in candidates:
        try:
            json_text = js_object_to_json(array_text)
            data = json.loads(json_text)

            routes = [
                item
                for item in data
                if isinstance(item, dict)
                and "codigo" in item
            ]

            if routes:
                print(
                    f"Successfully parsed {len(routes)} routes "
                    f"from variable={variable}"
                )
                return routes

        except Exception as exc:
            print(
                f"Could not parse candidate variable={variable}: "
                f"{exc}"
            )

    raise RuntimeError("Could not extract SAO6 route data")


# ---------------------------------------------------------------------------
# SAO6 page / JavaScript
# ---------------------------------------------------------------------------

def find_main_script(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    scripts = soup.find_all("script", src=True)

    for script in scripts:
        src = script["src"]

        if src.endswith(".js"):
            return urljoin(BASE_URL, src)

    raise RuntimeError("Could not find main JavaScript bundle")


def find_routes_chunk(main_js: str) -> str:
    """
    Find the lazy-loaded rutas-*.js chunk.
    """

    matches = re.findall(
        r'["\']([^"\']*rutas-[^"\']+\.js)["\']',
        main_js,
    )

    if not matches:
        raise RuntimeError(
            "Could not find rutas-*.js chunk in main bundle"
        )

    # Prefer the actual routes chunk.
    for match in matches:
        if re.search(r"rutas-[^/]+\.js$", match):
            return urljoin(BASE_URL, match)

    return urljoin(BASE_URL, matches[0])


def scrape_routes():
    print("========================================")
    print("SAO6 route scraper")
    print("========================================")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Downloading {ROUTES_URL}")

    response = download(ROUTES_URL)

    HTML_FILE.write_bytes(response.content)

    print(
        f"Saved {HTML_FILE} "
        f"({len(response.content):,} bytes)"
    )

    html = response.text

    # Main JS
    main_js_url = find_main_script(html)

    print(f"Main JS: {main_js_url}")

    main_response = download(main_js_url)
    main_js = main_response.text

    main_js_file = OUTPUT_DIR / Path(
        urlparse(main_js_url).path
    ).name

    main_js_file.write_bytes(main_response.content)

    print(
        f"Saved {main_js_file} "
        f"({len(main_response.content):,} bytes)"
    )

    # Routes chunk
    routes_js_url = find_routes_chunk(main_js)

    print(f"Routes JS: {routes_js_url}")

    routes_response = download(routes_js_url)
    routes_js = routes_response.text

    routes_js_file = OUTPUT_DIR / Path(
        urlparse(routes_js_url).path
    ).name

    routes_js_file.write_bytes(routes_response.content)

    print(
        f"Saved {routes_js_file} "
        f"({len(routes_response.content):,} bytes)"
    )

    # Extract route array
    routes = extract_routes(routes_js)

    # Validate
    required_fields = [
        "codigo",
        "nombre",
        "slug",
    ]

    for route in routes:
        missing = [
            field
            for field in required_fields
            if not route.get(field)
        ]

        if missing:
            raise RuntimeError(
                f"Route {route.get('codigo')} "
                f"is missing: {missing}"
            )

    with ROUTES_JSON_FILE.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            routes,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print()
    print(f"Saved {ROUTES_JSON_FILE}")
    print(f"Routes: {len(routes)}")

    return routes


# ---------------------------------------------------------------------------
# Google My Maps
# ---------------------------------------------------------------------------

def extract_map_id(mapa_url: str) -> str:
    """Extract the Google My Maps mid parameter."""

    parsed = urlparse(mapa_url)
    query = parse_qs(parsed.query)

    values = query.get("mid")

    if not values:
        raise ValueError(
            f"No mid parameter found in {mapa_url}"
        )

    return values[0]


def analyse_map_response(
    content: bytes,
    content_type: str,
) -> dict:
    """
    Determine what Google returned without modifying the raw data.
    """

    result = {
        "content_type": content_type,
        "size_bytes": len(content),
        "is_zip": False,
        "is_xml": False,
        "placemarks": 0,
        "folders": 0,
        "linestrings": 0,
        "points": 0,
        "polygons": 0,
    }

    # ZIP/KMZ signature
    if content[:4] == b"PK\x03\x04":
        result["is_zip"] = True
        return result

    text = content.decode(
        "utf-8",
        errors="replace",
    )

    stripped = text.lstrip()

    result["is_xml"] = (
        stripped.startswith("<?xml")
        or stripped.startswith("<kml")
        or "<kml" in stripped[:1000]
    )

    result["placemarks"] = len(
        re.findall(
            r"<Placemark\b",
            text,
            flags=re.IGNORECASE,
        )
    )

    result["folders"] = len(
        re.findall(
            r"<Folder\b",
            text,
            flags=re.IGNORECASE,
        )
    )

    result["linestrings"] = len(
        re.findall(
            r"<LineString\b",
            text,
            flags=re.IGNORECASE,
        )
    )

    result["points"] = len(
        re.findall(
            r"<Point\b",
            text,
            flags=re.IGNORECASE,
        )
    )

    result["polygons"] = len(
        re.findall(
            r"<Polygon\b",
            text,
            flags=re.IGNORECASE,
        )
    )

    return result


def probe_google_maps(routes):
    """
    Download the raw KML/KMZ response for every SAO6 route.

    This deliberately does NOT attempt to interpret the map data yet.
    """

    print()
    print("========================================")
    print("Google My Maps probe")
    print("========================================")

    MAPS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    results = []

    for index, route in enumerate(
        routes,
        start=1,
    ):
        codigo = route["codigo"]
        nombre = route["nombre"]
        mapa_url = route.get("mapaUrl")

        print()
        print(
            f"[{index}/{len(routes)}] "
            f"{codigo} - {nombre}"
        )

        result = {
            "codigo": codigo,
            "nombre": nombre,
            "mapa_url": mapa_url,
            "map_id": None,
            "kml_url": None,
            "status_code": None,
            "final_url": None,
            "error": None,
            "file": None,
        }

        try:
            if not mapa_url:
                raise ValueError(
                    "Route has no mapaUrl"
                )

            map_id = extract_map_id(mapa_url)

            kml_url = (
                f"https://www.google.com/maps/d/kml"
                f"?mid={map_id}"
                f"&forcekml=1"
            )

            result["map_id"] = map_id
            result["kml_url"] = kml_url

            response = session.get(
                kml_url,
                timeout=TIMEOUT,
                allow_redirects=True,
            )

            result["status_code"] = response.status_code
            result["final_url"] = response.url

            analysis = analyse_map_response(
                response.content,
                response.headers.get(
                    "content-type",
                    "",
                ),
            )

            result.update(analysis)

            extension = (
                ".kmz"
                if analysis["is_zip"]
                else ".kml"
            )

            output_file = (
                MAPS_DIR / f"{codigo}{extension}"
            )

            # Save the raw response unchanged.
            output_file.write_bytes(
                response.content
            )

            result["file"] = str(output_file)

            print(
                f"    HTTP:       "
                f"{response.status_code}"
            )
            print(
                f"    Type:       "
                f"{analysis['content_type']}"
            )
            print(
                f"    Size:       "
                f"{analysis['size_bytes']:,} bytes"
            )
            print(
                f"    ZIP/KMZ:    "
                f"{analysis['is_zip']}"
            )
            print(
                f"    XML/KML:    "
                f"{analysis['is_xml']}"
            )
            print(
                f"    Placemarks: "
                f"{analysis['placemarks']}"
            )
            print(
                f"    Folders:    "
                f"{analysis['folders']}"
            )
            print(
                f"    LineString: "
                f"{analysis['linestrings']}"
            )
            print(
                f"    Points:     "
                f"{analysis['points']}"
            )
            print(
                f"    Polygons:   "
                f"{analysis['polygons']}"
            )

        except Exception as exc:
            result["error"] = str(exc)
            print(f"    ERROR: {exc}")

        results.append(result)

        if index < len(routes):
            time.sleep(
                MAP_DELAY_SECONDS
            )

    with MAP_REPORT_FILE.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            results,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print()
    print(
        f"Saved map probe report: "
        f"{MAP_REPORT_FILE}"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    try:
        routes = scrape_routes()

        # Next step:
        # Probe every Google My Maps URL belonging to the routes.
        probe_google_maps(routes)

        print()
        print("========================================")
        print("SAO6 scraping complete")
        print("========================================")

    except Exception as exc:
        print()
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
