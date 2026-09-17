#!/usr/bin/env python3

import json
import re
from pathlib import Path
from urllib.parse import urljoin

import requests


BASE_URL = "https://www.sao6.com.co"
ROUTES_URL = f"{BASE_URL}/rutas"

OUTPUT_DIR = Path("sao6_data")
OUTPUT_JSON = OUTPUT_DIR / "sao6_rutas.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/139.0 Safari/537.36"
    )
}


def download(url: str) -> str:
    """Download a text resource."""
    print(f"Downloading: {url}")

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30,
    )
    response.raise_for_status()

    return response.text


def find_main_js(html: str) -> str:
    """Find the main Vite JavaScript bundle in the HTML."""

    # Example:
    # <script type="module" crossorigin src="/assets/index-DoO8Sp9e.js">
    match = re.search(
        r'<script[^>]+type=["\']module["\'][^>]+src=["\']([^"\']+\.js)["\']',
        html,
        re.IGNORECASE,
    )

    if not match:
        raise RuntimeError("Could not find the main JavaScript bundle.")

    return urljoin(BASE_URL, match.group(1))


def find_routes_chunk(main_js: str) -> str:
    """
    Find the rutas-*.js chunk referenced by the main bundle.

    Example:
        ./rutas-B3K6DTqs.js
    """

    match = re.search(
        r'["\']\.?/?(rutas-[A-Za-z0-9_-]+\.js)["\']',
        main_js,
    )

    if not match:
        raise RuntimeError(
            "Could not find the rutas-*.js chunk in the main JavaScript bundle."
        )

    filename = match.group(1)

    return urljoin(BASE_URL, f"/assets/{filename}")


def extract_routes(js: str) -> list[dict]:
    """
    Extract the route array from rutas-*.js.

    The SAO6 bundle has this structure:

        const a = "...";
        const e = [
            {...},
            {...}
        ];

        function o(a) {
            return e.find(...)
        }

        export { e as R, o as g, a as h };
    """

    # Locate:
    #
    # const e=[ ... ];
    #
    # We cannot simply use a regular expression ending at the first "]"
    # because each route also contains a keywords array.

    match = re.search(
        r'const\s+e\s*=\s*\[',
        js,
    )

    if not match:
        raise RuntimeError("Could not find the route array.")

    start = match.end() - 1

    # Find the matching closing ] while respecting strings.
    end = find_matching_bracket(js, start)

    array_text = js[start:end + 1]

    # The data is valid JSON except that the JavaScript uses normal
    # JSON-compatible object syntax in this particular bundle.
    try:
        routes = json.loads(array_text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Route array was found, but could not be parsed as JSON: {exc}"
        ) from exc

    if not isinstance(routes, list):
        raise RuntimeError("The extracted route data is not a list.")

    return routes


def find_matching_bracket(text: str, start: int) -> int:
    """
    Find the closing bracket matching text[start].

    Handles:
    - nested [] and {}
    - strings
    - escaped quotes
    """

    opening = text[start]

    if opening != "[":
        raise ValueError("find_matching_bracket() must start at '['")

    depth = 0
    in_string = False
    string_quote = None
    escaped = False

    for i in range(start, len(text)):
        char = text[i]

        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == string_quote:
                in_string = False

            continue

        if char in ('"', "'"):
            in_string = True
            string_quote = char
            continue

        if char == "[":
            depth += 1

        elif char == "]":
            depth -= 1

            if depth == 0:
                return i

    raise RuntimeError("Could not find matching closing bracket.")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------
    # 1. Download /rutas
    # ---------------------------------------------------------

    html = download(ROUTES_URL)

    html_file = OUTPUT_DIR / "rutas.html"
    html_file.write_text(html, encoding="utf-8")

    print(f"Saved: {html_file}")

    # ---------------------------------------------------------
    # 2. Find main JavaScript bundle
    # ---------------------------------------------------------

    main_js_url = find_main_js(html)

    print(f"Main JS: {main_js_url}")

    main_js = download(main_js_url)

    main_js_file = OUTPUT_DIR / Path(main_js_url).name
    main_js_file.write_text(main_js, encoding="utf-8")

    print(f"Saved: {main_js_file}")

    # ---------------------------------------------------------
    # 3. Find rutas-*.js
    # ---------------------------------------------------------

    routes_js_url = find_routes_chunk(main_js)

    print(f"Routes JS: {routes_js_url}")

    routes_js = download(routes_js_url)

    routes_js_file = OUTPUT_DIR / Path(routes_js_url).name
    routes_js_file.write_text(routes_js, encoding="utf-8")

    print(f"Saved: {routes_js_file}")

    # ---------------------------------------------------------
    # 4. Extract routes
    # ---------------------------------------------------------

    routes = extract_routes(routes_js)

    print(f"Found {len(routes)} routes.")

    # ---------------------------------------------------------
    # 5. Write JSON
    # ---------------------------------------------------------

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

    print(f"Saved: {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
