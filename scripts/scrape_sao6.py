#!/usr/bin/env python3

import json
import re
from pathlib import Path
from urllib.parse import urljoin

import requests


# ============================================================================
# Configuration
# ============================================================================

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
        "q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
    "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
}


# ============================================================================
# HTTP
# ============================================================================

def download(url: str) -> str:
    """
    Download a URL and return its content as text.
    """

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


# ============================================================================
# HTML parsing
# ============================================================================

def find_main_js(html: str) -> str:
    """
    Find the main Vite JavaScript bundle.

    Normally the page contains something like:

        <script type="module" src="/assets/index-XXXX.js">
    """

    patterns = [
        # Normal Vite layout
        r'<script[^>]+type=["\']module["\'][^>]+src=["\']([^"\']+\.js)["\']',

        # Attribute order reversed
        r'<script[^>]+src=["\']([^"\']+\.js)["\'][^>]+type=["\']module["\']',
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            html,
            flags=re.IGNORECASE,
        )

        if match:

            js_url = urljoin(
                BASE_URL,
                match.group(1),
            )

            print(
                f"Found main JavaScript bundle: {js_url}"
            )

            return js_url

    raise RuntimeError(
        "Could not find the main JavaScript bundle "
        "in /rutas HTML."
    )


# ============================================================================
# JavaScript chunk discovery
# ============================================================================

def find_routes_chunk(main_js: str) -> str:
    """
    Find the JavaScript chunk containing the route definitions.

    Example:

        rutas-B3K6DTqs.js

    Vite changes the hash when the website is rebuilt, so we only
    look for the logical 'rutas' part.
    """

    print(
        "Searching main JS for route JavaScript chunk..."
    )

    patterns = [
        r'(rutas-[A-Za-z0-9_-]+\.js)',
        r'([A-Za-z0-9_-]*rutas[A-Za-z0-9_-]*\.js)',
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

    if not found:

        print(
            "Could not find a rutas JavaScript chunk."
        )

        print(
            "Debug: searching for 'rutas' occurrences..."
        )

        debug_matches = list(
            re.finditer(
                r".{0,150}rutas.{0,300}",
                main_js,
                flags=re.IGNORECASE,
            )
        )

        for index, match in enumerate(
            debug_matches[:20],
            start=1,
        ):

            print(
                f"\n--- rutas occurrence {index} ---"
            )

            print(
                match.group(0)
            )

        raise RuntimeError(
            "Could not find a rutas JavaScript chunk "
            "in the main JavaScript bundle."
        )

    print(
        "Found possible route JavaScript chunk(s):"
    )

    for filename in found:
        print(
            f"  {filename}"
        )

    # Prefer the actual rutas-xxxxx.js file over something
    # like RutasView-xxxxx.js.
    preferred = [
        filename
        for filename in found
        if re.match(
            r"^rutas-",
            filename,
            flags=re.IGNORECASE,
        )
    ]

    if preferred:
        filename = preferred[0]
    else:
        filename = found[0]

    routes_url = urljoin(
        BASE_URL,
        f"/assets/{filename}",
    )

    print(
        f"Selected route chunk: {routes_url}"
    )

    return routes_url


# ============================================================================
# JavaScript bracket handling
# ============================================================================

def find_matching_bracket(
    text: str,
    start: int,
) -> int:
    """
    Find the closing ']' belonging to the '[' at start.

    Handles:

    - nested arrays
    - strings
    - escaped quotes
    - template strings

    This prevents a ']' inside a description or URL from
    prematurely terminating the array.
    """

    if start < 0 or start >= len(text):
        raise ValueError(
            "Invalid start position."
        )

    if text[start] != "[":
        raise ValueError(
            "find_matching_bracket() must start at '['."
        )

    depth = 0

    in_string = False
    quote = None
    escaped = False

    for index in range(
        start,
        len(text),
    ):

        char = text[index]

        # ---------------------------------------------------------------
        # Inside string
        # ---------------------------------------------------------------

        if in_string:

            if escaped:

                escaped = False

            elif char == "\\":
                escaped = True

            elif char == quote:

                in_string = False
                quote = None

            continue

        # ---------------------------------------------------------------
        # Start of string
        # ---------------------------------------------------------------

        if char in (
            '"',
            "'",
            "`",
        ):

            in_string = True
            quote = char

            continue

        # ---------------------------------------------------------------
        # Array nesting
        # ---------------------------------------------------------------

        if char == "[":

            depth += 1

        elif char == "]":

            depth -= 1

            if depth == 0:
                return index

    raise RuntimeError(
        "Could not find matching closing ']' "
        "for JavaScript array."
    )


# ============================================================================
# Route array discovery
# ============================================================================

def find_array_assignments(js: str):
    """
    Find JavaScript arrays assigned to variables.

    This specifically handles minified JavaScript such as:

        const a="something",e=[...]

    The old implementation searched for:

        const e=[

    which fails in this situation.

    We instead look for any variable assignment of the form:

        ,e=[
        ;e=[
        const e=[
        let e=[
        var e=[

    and return the array start positions.
    """

    pattern = re.compile(
        r"""
        (?:
            ^|
            [;,]
        )
        \s*
        (?P<variable>
            [$A-Za-z_][$A-Za-z0-9_]*
        )
        \s*=\s*
        \[
        """,
        flags=re.VERBOSE,
    )

    assignments = []

    for match in pattern.finditer(js):

        array_start = match.end() - 1

        assignments.append(
            {
                "variable": match.group("variable"),
                "start": array_start,
            }
        )

    return assignments


def extract_routes(js: str) -> list[dict]:
    """
    Extract the route array from rutas-*.js.

    We do NOT assume that the route array is named 'e'.

    Instead we:

    1. Find all variable -> array assignments.
    2. Extract each array.
    3. Attempt JSON parsing.
    4. Look for objects containing 'codigo'.
    5. Select the array containing the SAO6 routes.
    """

    print(
        "Searching route JavaScript for route array..."
    )

    assignments = find_array_assignments(
        js
    )

    print(
        f"Found {len(assignments)} array assignment(s)."
    )

    candidates = []

    for number, assignment in enumerate(
        assignments,
        start=1,
    ):

        variable = assignment["variable"]
        start = assignment["start"]

        try:

            end = find_matching_bracket(
                js,
                start,
            )

        except RuntimeError:

            continue

        array_text = js[
            start:end + 1
        ]

        # We only care about arrays that appear to contain
        # route information.
        if "codigo" not in array_text:
            continue

        print(
            f"Candidate array #{number}: "
            f"variable={variable}, "
            f"size={len(array_text):,} characters"
        )

        candidates.append(
            {
                "variable": variable,
                "start": start,
                "end": end,
                "text": array_text,
            }
        )

    if not candidates:

        print(
            "No array containing 'codigo' was found."
        )

        # Additional debugging
        codigo_matches = list(
            re.finditer(
                r"codigo\s*:",
                js,
                flags=re.IGNORECASE,
            )
        )

        print(
            f"Found {len(codigo_matches)} occurrence(s) "
            "of 'codigo:' in the JavaScript."
        )

        for index, match in enumerate(
            codigo_matches[:10],
            start=1,
        ):

            start = max(
                0,
                match.start() - 200,
            )

            end = min(
                len(js),
                match.end() + 500,
            )

            print(
                f"\n--- codigo occurrence {index} ---"
            )

            print(
                js[start:end]
            )

        raise RuntimeError(
            "Could not find route array in "
            "rutas JavaScript."
        )

    # -----------------------------------------------------------------------
    # Try parsing the candidates.
    # -----------------------------------------------------------------------

    for candidate in candidates:

        variable = candidate["variable"]
        array_text = candidate["text"]

        try:

            data = json.loads(
                array_text
            )

        except json.JSONDecodeError as exc:

            print(
                f"Candidate variable '{variable}' "
                "contains 'codigo' but is not valid JSON."
            )

            print(
                f"JSON error: {exc}"
            )

            continue

        if not isinstance(
            data,
            list,
        ):
            continue

        # -------------------------------------------------------------------
        # Validate route objects
        # -------------------------------------------------------------------

        routes = []

        for item in data:

            if not isinstance(
                item,
                dict,
            ):
                continue

            if "codigo" not in item:
                continue

            routes.append(
                item
            )

        if not routes:
            continue

        # -------------------------------------------------------------------
        # We found the route array.
        # -------------------------------------------------------------------

        print(
            f"Selected route array: "
            f"variable={variable}"
        )

        print(
            f"Successfully extracted "
            f"{len(routes)} route(s)."
        )

        return routes

    raise RuntimeError(
        "Found candidate route arrays, but could not "
        "parse any of them as JSON."
    )


# ============================================================================
# Validation
# ============================================================================

def validate_routes(routes: list[dict]) -> None:
    """
    Perform basic validation of extracted route records.
    """

    print()
    print(
        "Validating extracted routes..."
    )

    required_fields = [
        "codigo",
        "nombre",
        "slug",
    ]

    problems = 0

    for index, route in enumerate(
        routes,
        start=1,
    ):

        missing = [
            field
            for field in required_fields
            if not route.get(field)
        ]

        if missing:

            problems += 1

            print(
                f"Warning: route #{index} "
                f"missing fields: {missing}"
            )

    if problems:

        print(
            f"Validation completed with "
            f"{problems} warning(s)."
        )

    else:

        print(
            "Validation successful."
        )


# ============================================================================
# Main
# ============================================================================

def main() -> None:
    """
    Main scraper workflow:

        /rutas
           |
           v
        index-XXXX.js
           |
           v
        rutas-XXXX.js
           |
           v
        route array
           |
           v
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
    # 2. Find main JavaScript bundle
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
    # 3. Find rutas JavaScript chunk
    # -----------------------------------------------------------------------

    routes_js_url = find_routes_chunk(
        main_js
    )

    # -----------------------------------------------------------------------
    # 4. Download rutas JavaScript chunk
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
    # 6. Validate
    # -----------------------------------------------------------------------

    validate_routes(
        routes
    )

    # -----------------------------------------------------------------------
    # 7. Write JSON
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

    print()
    print(
        f"Saved route data: {OUTPUT_JSON}"
    )

    # -----------------------------------------------------------------------
    # 8. Show sample
    # -----------------------------------------------------------------------

    print()
    print("=" * 70)
    print(
        f"SUCCESS: {len(routes)} route(s) extracted"
    )
    print("=" * 70)

    for route in routes[:10]:

        codigo = str(
            route.get(
                "codigo",
                "?",
            )
        )

        nombre = str(
            route.get(
                "nombre",
                "?",
            )
        )

        slug = str(
            route.get(
                "slug",
                "?",
            )
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


# ============================================================================
# Entry point
# ============================================================================

if __name__ == "__main__":
    main()
