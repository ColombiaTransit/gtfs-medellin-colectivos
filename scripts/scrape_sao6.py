#!/usr/bin/env python3

import json
import re
from pathlib import Path
from urllib.parse import urljoin

import requests


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_URL = "https://www.sao6.com.co"
ROUTES_URL = f"{BASE_URL}/rutas"

OUTPUT_DIR = Path("sao6_data")
OUTPUT_JSON = OUTPUT_DIR / "sao6_rutas.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/139.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
}


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------

def download(url: str) -> str:
    """Download a URL and return its text content."""

    print(f"Downloading: {url}")

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30,
    )

    response.raise_for_status()

    print(
        f"Downloaded {len(response.text):,} bytes "
        f"from {url}"
    )

    return response.text


# ---------------------------------------------------------------------------
# HTML / JavaScript discovery
# ---------------------------------------------------------------------------

def find_main_js(html: str) -> str:
    """
    Find the main Vite JavaScript bundle from the HTML page.
    """

    patterns = [
        # Normal Vite module script
        r'<script[^>]+type=["\']module["\'][^>]+src=["\']([^"\']+\.js)["\']',

        # More permissive variant in case attribute ordering differs
        r'<script[^>]+src=["\']([^"\']+\.js)["\'][^>]+type=["\']module["\']',
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            html,
            re.IGNORECASE,
        )

        if match:
            js_url = urljoin(
                BASE_URL,
                match.group(1),
            )

            print(f"Found main JavaScript bundle: {js_url}")

            return js_url

    raise RuntimeError(
        "Could not find the main JavaScript bundle in /rutas HTML."
    )


def find_routes_chunk(main_js: str) -> str:
    """
    Find the JavaScript chunk containing the route definitions.

    The site uses Vite and the chunk name can change after every build,
    for example:

        rutas-B3K6DTqs.js

    We therefore do not depend on the exact hash.

    Several patterns are tried because Vite may reference the chunk
    directly or indirectly in the generated bundle.
    """

    print("Searching main JS for route chunk...")

    patterns = [
        # Example:
        # rutas-B3K6DTqs.js
        r'(rutas-[A-Za-z0-9_-]+\.js)',

        # More generic:
        # anything containing "rutas"
        r'([A-Za-z0-9_-]*rutas[A-Za-z0-9_-]*\.js)',

        # Quoted JavaScript import:
        # "./rutas-B3K6DTqs.js"
        r'["\'](?:\./)?(rutas-[A-Za-z0-9_-]+\.js)["\']',

        # Generic quoted import
        r'["\'](?:\./)?([A-Za-z0-9_-]*rutas[A-Za-z0-9_-]*\.js)["\']',
    ]

    found = []

    for pattern in patterns:
        matches = re.findall(
            pattern,
            main_js,
            flags=re.IGNORECASE,
        )

        for filename in matches:
            if filename not in found:
                found.append(filename)

    if found:
        print("Found possible route JavaScript chunk(s):")

        for filename in found:
            print(f"  {filename}")

        # Prefer a filename that starts with "rutas-"
        preferred = [
            filename
            for filename in found
            if filename.lower().startswith("rutas-")
        ]

        filename = (
            preferred[0]
            if preferred
            else found[0]
        )

        routes_url = urljoin(
            BASE_URL,
            f"/assets/{filename}",
        )

        print(f"Selected route chunk: {routes_url}")

        return routes_url

    # -----------------------------------------------------------------------
    # Debugging fallback
    # -----------------------------------------------------------------------
    #
    # If the normal regex did not find anything, print all occurrences
    # of "rutas" from the main bundle. This is extremely useful if Vite
    # changes its dependency representation.
    # -----------------------------------------------------------------------

    print(
        "No rutas-*.js filename found using normal patterns."
    )

    print(
        "Searching the main JS for occurrences of 'rutas'..."
    )

    debug_matches = list(
        re.finditer(
            r".{0,150}rutas.{0,250}",
            main_js,
            flags=re.IGNORECASE,
        )
    )

    if debug_matches:
        print(
            f"Found {len(debug_matches)} occurrence(s) "
            "of 'rutas' in the main bundle:"
        )

        for index, match in enumerate(
            debug_matches[:20],
            start=1,
        ):
            snippet = match.group(0)

            print(
                f"\n--- rutas occurrence {index} ---"
            )
            print(snippet)

    else:
        print(
            "No occurrence of 'rutas' was found "
            "in the main JavaScript bundle."
        )

    raise RuntimeError(
        "Could not find a rutas JavaScript chunk in "
        "the main JavaScript bundle. "
        "See the debug output above."
    )


# ---------------------------------------------------------------------------
# JavaScript parsing
# ---------------------------------------------------------------------------

def find_matching_bracket(
    text: str,
    start: int,
) -> int:
    """
    Find the closing ']' matching the '[' at `start`.

    This handles strings and escaped characters so that brackets
    inside strings do not affect the nesting depth.
    """

    if start >= len(text):
        raise ValueError(
            "Start position is outside the JavaScript text."
        )

    opening = text[start]

    if opening != "[":
        raise ValueError(
            "find_matching_bracket() must start at '['"
        )

    depth = 0

    in_string = False
    string_quote = None
    escaped = False

    for i in range(
        start,
        len(text),
    ):
        char = text[i]

        # ---------------------------------------------------------------
        # Inside a JavaScript string
        # ---------------------------------------------------------------

        if in_string:

            if escaped:
                escaped = False

            elif char == "\\":
                escaped = True

            elif char == string_quote:
                in_string = False
                string_quote = None

            continue

        # ---------------------------------------------------------------
        # Start of a JavaScript string
        # ---------------------------------------------------------------

        if char in (
            '"',
            "'",
            "`",
        ):
            in_string = True
            string_quote = char
            continue

        # ---------------------------------------------------------------
        # Array nesting
        # ---------------------------------------------------------------

        if char == "[":
            depth += 1

        elif char == "]":
            depth -= 1

            if depth == 0:
                return i

    raise RuntimeError(
        "Could not find matching closing bracket "
        "for route array."
    )


def extract_routes(js: str) -> list[dict]:
    """
    Extract the static route array from rutas-*.js.

    The current site contains something similar to:

        const e=[{codigo:"C6-001", ...}, ...]

    Because the JavaScript uses JSON-compatible double-quoted
    strings in the route data, the extracted array can be parsed
    with json.loads().
    """

    print("Searching route JavaScript for route array...")

    # Current known structure
    patterns = [
        r'const\s+e\s*=\s*\[',
        r'const\s+[A-Za-z_$][A-Za-z0-9_$]*\s*=\s*\[',
        r'(?:const|let|var)\s+[A-Za-z_$][A-Za-z0-9_$]*\s*=\s*\[',
    ]

    match = None

    for pattern in patterns:
        match = re.search(
            pattern,
            js,
        )

        if match:
            print(
                f"Found route array using pattern: {pattern}"
            )
            break

    if not match:
        # Debug information if the route array structure changes
        print(
            "Could not find a JavaScript array assigned "
            "to a variable."
        )

        print(
            "Searching for occurrences of 'codigo'..."
        )

        debug_matches = list(
            re.finditer(
                r".{0,150}codigo.{0,300}",
                js,
                flags=re.IGNORECASE,
            )
        )

        for index, debug_match in enumerate(
            debug_matches[:10],
            start=1,
        ):
            print(
                f"\n--- codigo occurrence {index} ---"
            )
            print(debug_match.group(0))

        raise RuntimeError(
            "Could not find the route array in rutas JavaScript."
        )

    # match.end() points immediately after the '['
    start = match.end() - 1

    end = find_matching_bracket(
        js,
        start,
    )

    array_text = js[
        start:end + 1
    ]

    print(
        f"Extracted route array: "
        f"{len(array_text):,} characters"
    )

    try:
        routes = json.loads(
            array_text
        )

    except json.JSONDecodeError as exc:
        print(
            "The extracted JavaScript array is not valid JSON."
        )

        print(
            "First 1,000 characters of extracted data:"
        )
        print(
            array_text[:1000]
        )

        raise RuntimeError(
            "Could not parse route array as JSON."
        ) from exc

    if not isinstance(
        routes,
        list,
    ):
        raise RuntimeError(
            "The extracted route data is not a list."
        )

    # Basic validation
    valid_routes = []

    for route in routes:

        if not isinstance(
            route,
            dict,
        ):
            print(
                "Warning: skipping route entry "
                "that is not an object."
            )
            continue

        valid_routes.append(
            route
        )

    if not valid_routes:
        raise RuntimeError(
            "Route array was found but contains "
            "no valid route objects."
        )

    print(
        f"Successfully extracted "
        f"{len(valid_routes)} route(s)."
    )

    return valid_routes


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """
    Main scraper workflow:

        /rutas
          ↓
        index-*.js
          ↓
        rutas-*.js
          ↓
        route array
          ↓
        sao6_rutas.json
    """

    print("=" * 70)
    print("SAO6 route scraper")
    print("=" * 70)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # -----------------------------------------------------------------------
    # 1. Download /rutas
    # -----------------------------------------------------------------------

    html = download(
        ROUTES_URL
    )

    html_file = (
        OUTPUT_DIR /
        "rutas.html"
    )

    html_file.write_text(
        html,
        encoding="utf-8",
    )

    print(
        f"Saved HTML: {html_file}"
    )

    # -----------------------------------------------------------------------
    # 2. Find and download main JavaScript bundle
    # -----------------------------------------------------------------------

    main_js_url = find_main_js(
        html
    )

    main_js = download(
        main_js_url
    )

    main_js_file = (
        OUTPUT_DIR /
        Path(main_js_url).name
    )

    main_js_file.write_text(
        main_js,
        encoding="utf-8",
    )

    print(
        f"Saved main JS: {main_js_file}"
    )

    # -----------------------------------------------------------------------
    # 3. Find route JavaScript chunk
    # -----------------------------------------------------------------------

    routes_js_url = find_routes_chunk(
        main_js
    )

    # -----------------------------------------------------------------------
    # 4. Download route JavaScript chunk
    # -----------------------------------------------------------------------

    routes_js = download(
        routes_js_url
    )

    routes_js_file = (
        OUTPUT_DIR /
        Path(routes_js_url).name
    )

    routes_js_file.write_text(
        routes_js,
        encoding="utf-8",
    )

    print(
        f"Saved route JS: {routes_js_file}"
    )

    # -----------------------------------------------------------------------
    # 5. Extract routes
    # -----------------------------------------------------------------------

    routes = extract_routes(
        routes_js
    )

    # -----------------------------------------------------------------------
    # 6. Write JSON
    # -----------------------------------------------------------------------

    output = {
        "source": ROUTES_URL,
        "route_count": len(routes),
        "routes": routes,
    }

    OUTPUT_JSON.write_text(
        json.dumps(
            output,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"Saved route data: {OUTPUT_JSON}"
    )

    # -----------------------------------------------------------------------
    # 7. Print a small summary
    # -----------------------------------------------------------------------

    print()
    print("=" * 70)
    print(
        f"SUCCESS: {len(routes)} route(s) extracted"
    )
    print("=" * 70)

    for route in routes[:10]:

        codigo = route.get(
            "codigo",
            "?",
        )

        nombre = route.get(
            "nombre",
            "?",
        )

        slug = route.get(
            "slug",
            "?",
        )

        print(
            f"{codigo:10} | "
            f"{nombre} | "
            f"{slug}"
        )

    if len(routes) > 10:
        print(
            f"... and {len(routes) - 10} more route(s)"
        )


if __name__ == "__main__":
    main()
