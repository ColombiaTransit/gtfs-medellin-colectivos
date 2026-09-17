#!/usr/bin/env python3

"""
SAO6 route scraper

Downloads the SAO6 route page and extracts the static route catalogue
from the JavaScript bundle.

Output:
    sao6_data/rutas.html
    sao6_data/index-*.js
    sao6_data/rutas-*.js
    sao6_data/sao6_rutas.json

The scraper deliberately stops at extracting the route catalogue.
Google Maps / KML processing is handled separately in a later step.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_URL = "https://www.sao6.com.co"
ROUTES_URL = f"{BASE_URL}/rutas"

OUTPUT_DIR = Path("sao6_data")

HTML_FILE = OUTPUT_DIR / "rutas.html"
ROUTES_JSON_FILE = OUTPUT_DIR / "sao6_rutas.json"

REQUEST_TIMEOUT = 30

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0 Safari/537.36"
)


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------

def create_session() -> requests.Session:
    """Create an HTTP session with a browser-like User-Agent."""

    session = requests.Session()

    session.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept": "*/*",
        }
    )

    return session


def download(
    session: requests.Session,
    url: str,
) -> str:
    """Download a text resource."""

    print(f"Downloading: {url}")

    response = session.get(
        url,
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    text = response.text

    print(
        f"Downloaded {len(text):,} bytes from {url}"
    )

    return text


# ---------------------------------------------------------------------------
# JavaScript bundle discovery
# ---------------------------------------------------------------------------

def find_main_javascript(
    html: str,
    base_url: str,
) -> str:
    """
    Find the main JavaScript bundle from the HTML page.

    Vite applications normally contain something like:

        <script type="module" src="/assets/index-XXXX.js">
    """

    soup = BeautifulSoup(html, "html.parser")

    candidates: list[str] = []

    for script in soup.find_all("script"):
        src = script.get("src")

        if not src:
            continue

        full_url = urljoin(base_url, src)

        if full_url.endswith(".js"):
            candidates.append(full_url)

    if not candidates:
        raise RuntimeError(
            "Could not find a JavaScript bundle in the HTML."
        )

    # Prefer an index bundle.
    index_candidates = [
        url
        for url in candidates
        if re.search(r"/index-[^/]+\.js$", url)
    ]

    if index_candidates:
        selected = index_candidates[0]
    else:
        selected = candidates[0]

    print(
        f"Found main JavaScript bundle: {selected}"
    )

    return selected


def find_route_javascript(
    main_js: str,
    base_url: str,
) -> list[str]:
    """
    Find JavaScript chunks related to routes.

    Current SAO6 bundles contain references such as:

        rutas-B3K6DTqs.js
        RutasView-TSg5kUWX.js
    """

    patterns = [
        r'["\']([^"\']*rutas-[^"\']+\.js)["\']',
        r'["\']([^"\']*RutasView-[^"\']+\.js)["\']',
        r'["\']([^"\']*DetalleRutaView-[^"\']+\.js)["\']',
    ]

    found: list[str] = []

    for pattern in patterns:
        for match in re.finditer(pattern, main_js):
            filename = match.group(1)

            url = urljoin(
                base_url + "/assets/",
                filename.split("/")[-1],
            )

            if url not in found:
                found.append(url)

    return found


def select_route_chunk(
    route_chunks: list[str],
) -> str:
    """
    Select the JavaScript chunk containing the static route data.

    Prefer rutas-*.js because that is where the route array currently lives.
    """

    if not route_chunks:
        raise RuntimeError(
            "Could not find any route JavaScript chunks."
        )

    print("Found possible route JavaScript chunk(s):")

    for url in route_chunks:
        print(f"  {url.rsplit('/', 1)[-1]}")

    rutas_chunks = [
        url
        for url in route_chunks
        if re.search(r"/rutas-[^/]+\.js$", url)
    ]

    if rutas_chunks:
        selected = rutas_chunks[0]
    else:
        selected = route_chunks[0]

    print(
        f"Selected route chunk: {selected}"
    )

    return selected


# ---------------------------------------------------------------------------
# JavaScript parsing
# ---------------------------------------------------------------------------

def find_matching_bracket(
    text: str,
    start: int,
) -> int:
    """
    Find the closing bracket matching the opening bracket at `start`.

    Handles:
        [...]
        {...}
        (...)
    
    while correctly ignoring brackets inside quoted strings.
    """

    opening = text[start]

    matching = {
        "[": "]",
        "{": "}",
        "(": ")",
    }

    if opening not in matching:
        raise ValueError(
            f"Expected opening bracket at position {start}, "
            f"got {opening!r}"
        )

    closing = matching[opening]

    depth = 0

    in_string = False
    string_quote: str | None = None
    escaped = False

    i = start

    while i < len(text):
        ch = text[i]

        if in_string:
            if escaped:
                escaped = False

            elif ch == "\\":
                escaped = True

            elif ch == string_quote:
                in_string = False
                string_quote = None

            i += 1
            continue

        if ch in ("'", '"', "`"):
            in_string = True
            string_quote = ch
            i += 1
            continue

        if ch == opening:
            depth += 1

        elif ch == closing:
            depth -= 1

            if depth == 0:
                return i

        i += 1

    raise ValueError(
        f"Could not find matching {closing!r} for "
        f"{opening!r} at position {start}"
    )


def find_array_assignments(
    js_text: str,
) -> list[dict[str, str]]:
    """
    Find JavaScript variable assignments containing arrays.

    Handles both:

        const e=[...]

    and:

        const a="...",e=[...]

    The second form is what the SAO6 route bundle currently uses.
    """

    assignments: list[dict[str, str]] = []

    # We intentionally allow either:
    #
    #   const e=[
    #
    # or:
    #
    #   ,e=[
    #
    # or:
    #
    #   ;e=[
    #
    pattern = re.compile(
        r"(?:^|[,;])\s*"
        r"(?P<variable>[A-Za-z_$][A-Za-z0-9_$]*)"
        r"\s*=\s*\[",
        re.MULTILINE,
    )

    for match in pattern.finditer(js_text):
        variable = match.group("variable")

        # Locate the actual opening [
        array_start = js_text.find(
            "[",
            match.start(),
            match.end(),
        )

        if array_start < 0:
            continue

        try:
            array_end = find_matching_bracket(
                js_text,
                array_start,
            )
        except ValueError as exc:
            print(
                f"Warning: could not parse array assigned to "
                f"{variable}: {exc}"
            )
            continue

        array_text = js_text[
            array_start:array_end + 1
        ]

        assignments.append(
            {
                "variable": variable,
                "array": array_text,
            }
        )

    return assignments


def js_object_to_json(
    text: str,
) -> str:
    """
    Convert the limited JavaScript object-literal syntax used by SAO6
    into valid JSON.

    Example:

        {codigo:"C6-001",nombre:"Santa Rita",slug:"santa-rita"}

    becomes:

        {"codigo":"C6-001","nombre":"Santa Rita","slug":"santa-rita"}

    Only bare property names outside strings are changed.

    This avoids modifying URLs, descriptions, or other string values
    that may contain ':' or JavaScript-looking text.
    """

    result: list[str] = []

    i = 0
    n = len(text)

    in_string = False
    string_quote: str | None = None
    escaped = False

    while i < n:
        ch = text[i]

        # ---------------------------------------------------------------
        # Inside a quoted string
        # ---------------------------------------------------------------

        if in_string:
            result.append(ch)

            if escaped:
                escaped = False

            elif ch == "\\":
                escaped = True

            elif ch == string_quote:
                in_string = False
                string_quote = None

            i += 1
            continue

        # ---------------------------------------------------------------
        # Start of string
        # ---------------------------------------------------------------

        if ch in ('"', "'"):
            in_string = True
            string_quote = ch

            result.append(ch)

            i += 1
            continue

        # ---------------------------------------------------------------
        # JavaScript identifier
        # ---------------------------------------------------------------

        if ch.isalpha() or ch in "_$":
            start = i

            i += 1

            while i < n and (
                text[i].isalnum()
                or text[i] in "_$"
            ):
                i += 1

            word = text[start:i]

            # Look past whitespace.
            j = i

            while j < n and text[j].isspace():
                j += 1

            # If followed by ':', this is an object property.
            if j < n and text[j] == ":":
                result.append(
                    json.dumps(word)
                )

                result.append(
                    text[i:j]
                )

                result.append(":")

                i = j + 1

                continue

            result.append(word)

            continue

        result.append(ch)

        i += 1

    return "".join(result)


def extract_routes(
    js_text: str,
) -> list[dict]:
    """
    Extract the static SAO6 route array.

    The current SAO6 bundle contains something similar to:

        const a="/assets/...",e=[{codigo:"C6-001",...},...]

    The route array is JavaScript, not strict JSON.

    Therefore we:
      1. locate the array;
      2. convert its object-literal syntax;
      3. parse it as JSON;
      4. validate the resulting route records.
    """

    print(
        "Searching route JavaScript for route array..."
    )

    assignments = find_array_assignments(
        js_text
    )

    print(
        f"Found {len(assignments)} array assignment(s)."
    )

    candidates: list[str] = []

    for idx, assignment in enumerate(
        assignments,
        start=1,
    ):
        variable = assignment["variable"]
        array_text = assignment["array"]

        print(
            f"Candidate array #{idx}: "
            f"variable={variable}, "
            f"size={len(array_text):,} characters"
        )

        # The SAO6 route objects contain the field "codigo".
        if (
            '"codigo"' not in array_text
            and "codigo" not in array_text
        ):
            continue

        candidates.append(array_text)

    if not candidates:
        raise RuntimeError(
            "Could not find a candidate route array "
            "containing 'codigo'."
        )

    for idx, array_text in enumerate(
        candidates,
        start=1,
    ):
        json_text = ""

        try:
            print(
                f"Converting candidate route array #{idx} "
                "from JavaScript syntax to JSON..."
            )

            json_text = js_object_to_json(
                array_text
            )

            routes = json.loads(
                json_text
            )

            if not isinstance(routes, list):
                print(
                    "Candidate did not produce a JSON list."
                )
                continue

            valid_routes: list[dict] = []

            for route in routes:
                if not isinstance(route, dict):
                    continue

                if "codigo" not in route:
                    continue

                valid_routes.append(route)

            if not valid_routes:
                print(
                    "Candidate contained no valid route objects."
                )
                continue

            print(
                f"Successfully parsed "
                f"{len(valid_routes)} SAO6 routes."
            )

            return valid_routes

        except json.JSONDecodeError as exc:
            print(
                f"Candidate #{idx} still could not "
                "be parsed as JSON."
            )

            print(
                f"JSON error: {exc}"
            )

            if json_text:
                print(
                    "Converted array beginning:"
                )

                print(
                    json_text[:1500]
                )

        except Exception as exc:
            print(
                f"Unexpected error parsing "
                f"candidate #{idx}: "
                f"{type(exc).__name__}: {exc}"
            )

    raise RuntimeError(
        "Found candidate route arrays, "
        "but could not parse any of them."
    )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_routes(
    routes: list[dict],
) -> None:
    """
    Validate the minimum fields needed for the SAO6 route catalogue.
    """

    if not routes:
        raise RuntimeError(
            "Route list is empty."
        )

    required_fields = (
        "codigo",
        "nombre",
        "slug",
    )

    errors: list[str] = []

    for index, route in enumerate(
        routes,
        start=1,
    ):
        for field in required_fields:
            if field not in route:
                errors.append(
                    f"Route #{index} missing field '{field}'"
                )

        if not route.get("codigo"):
            errors.append(
                f"Route #{index} has empty codigo"
            )

        if not route.get("nombre"):
            errors.append(
                f"Route #{index} has empty nombre"
            )

        if not route.get("slug"):
            errors.append(
                f"Route #{index} has empty slug"
            )

    if errors:
        for error in errors[:20]:
            print(
                f"Validation error: {error}"
            )

        if len(errors) > 20:
            print(
                f"... and {len(errors) - 20} more errors."
            )

        raise RuntimeError(
            f"Route validation failed with "
            f"{len(errors)} error(s)."
        )


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def save_json(
    routes: list[dict],
    path: Path,
) -> None:
    """Save routes as formatted JSON."""

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            routes,
            handle,
            ensure_ascii=False,
            indent=2,
        )

        handle.write("\n")

    print(
        f"Saved route JSON: {path}"
    )


def print_route_summary(
    routes: list[dict],
) -> None:
    """Print a short route summary."""

    print()
    print("=" * 70)
    print(
        f"SAO6 routes extracted: {len(routes)}"
    )
    print("=" * 70)

    for route in routes[:10]:
        codigo = route.get(
            "codigo",
            "",
        )

        nombre = route.get(
            "nombre",
            "",
        )

        slug = route.get(
            "slug",
            "",
        )

        print(
            f"{codigo:10} | "
            f"{nombre} | "
            f"{slug}"
        )

    if len(routes) > 10:
        print(
            f"... {len(routes) - 10} more routes"
        )

    print("=" * 70)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Main scraper entry point."""

    print(
        "=" * 70
    )

    print(
        "SAO6 route scraper"
    )

    print(
        "=" * 70
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    session = create_session()

    # ------------------------------------------------------------------
    # 1. Download route page
    # ------------------------------------------------------------------

    html = download(
        session,
        ROUTES_URL,
    )

    HTML_FILE.write_text(
        html,
        encoding="utf-8",
    )

    print(
        f"Saved HTML: {HTML_FILE}"
    )

    # ------------------------------------------------------------------
    # 2. Find main JavaScript bundle
    # ------------------------------------------------------------------

    main_js_url = find_main_javascript(
        html,
        BASE_URL,
    )

    main_js = download(
        session,
        main_js_url,
    )

    main_js_filename = Path(
        main_js_url
    ).name

    main_js_file = (
        OUTPUT_DIR
        / main_js_filename
    )

    main_js_file.write_text(
        main_js,
        encoding="utf-8",
    )

    print(
        f"Saved main JS: {main_js_file}"
    )

    # ------------------------------------------------------------------
    # 3. Find route JavaScript chunk
    # ------------------------------------------------------------------

    print(
        "Searching main JS for route "
        "JavaScript chunk..."
    )

    route_chunks = find_route_javascript(
        main_js,
        BASE_URL,
    )

    if not route_chunks:
        raise RuntimeError(
            "Could not find route JavaScript chunk."
        )

    route_js_url = select_route_chunk(
        route_chunks
    )

    route_js = download(
        session,
        route_js_url,
    )

    route_js_filename = Path(
        route_js_url
    ).name

    route_js_file = (
        OUTPUT_DIR
        / route_js_filename
    )

    route_js_file.write_text(
        route_js,
        encoding="utf-8",
    )

    print(
        f"Saved route JS: {route_js_file}"
    )

    # ------------------------------------------------------------------
    # 4. Extract routes
    # ------------------------------------------------------------------

    routes = extract_routes(
        route_js
    )

    # ------------------------------------------------------------------
    # 5. Validate
    # ------------------------------------------------------------------

    validate_routes(
        routes
    )

    # ------------------------------------------------------------------
    # 6. Save JSON
    # ------------------------------------------------------------------

    save_json(
        routes,
        ROUTES_JSON_FILE,
    )

    # ------------------------------------------------------------------
    # 7. Show result
    # ------------------------------------------------------------------

    print_route_summary(
        routes
    )

    print()
    print(
        "SAO6 scraping completed successfully."
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print(
            "\nInterrupted.",
            file=sys.stderr,
        )

        sys.exit(130)

    except Exception as exc:
        print(
            file=sys.stderr,
        )

        print(
            f"ERROR: {exc}",
            file=sys.stderr,
        )

        sys.exit(1)
