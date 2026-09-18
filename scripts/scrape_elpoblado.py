#!/usr/bin/env python3
"""
Extract Autobuses El Poblado's route data DIRECTLY from their homepage's
embedded JSON - no OCR, no Google Maps export, no headless browser needed.

Unlike Sotrames/SAO6/MDO, autopobla.com.co is a Next.js app that
server-renders its route data into the initial HTML response as part of
React's "Flight"/RSC streaming payload (inside a
`self.__next_f.push([1, "..."])` script tag). That payload contains a
"routes" array with, per route: code, name, zone, a free-text "schedule"
string (operating hours - NO headway/frequency anywhere in the schema),
precise LineString geometry (real GPS coordinates, not a rough sketch),
and a "stops" array that EXISTS in the data model but is empty for every
real route seen so far (one route, 130, had exactly 2 entries named
"Nombre de la para"/"Parada 2" - obviously leftover placeholder/test
data, not real stops).

CONFIRMED (matches what the user independently found): real map
geometry, real operating-hours text, NO frequency/headway data anywhere.
Same situation as Sotrames - being treated as a flag-down service
(GTFS-Flex), not modeled with fabricated headways.

COVERAGE: the site's homepage stat claims "35 Rutas Urbanas," but the
site actually only has 11 real routes - confirmed by the person who
gave this script the page to build from. A single homepage fetch
returns all 11; there's no pagination gap to worry about, despite the
misleading marketing figure.

Usage: python scripts/scrape_elpoblado.py
Output: raw/elpoblado_routes.json - the parsed route list, as found.
"""

import json
import re
import sys
from pathlib import Path

import requests

HOMEPAGE_URL = "https://www.autopobla.com.co/"
OUT_PATH = Path("raw/elpoblado_routes.json")

# Two real formats confirmed in the actual data (schedule text isn't
# entered consistently across routes):
#   "Lunes a sábado: 5:00 AM - 10:30 PM"        (colon + dash)
#   "Lunes a Sábado de 5:00 am a 9:00 pm"        ("de X a Y", lowercase)
SCHEDULE_RE_COLON = re.compile(
    r"(?P<days>[A-Za-zÁÉÍÓÚáéíóúñÑ ]+?):\s*"
    r"(?P<start>\d{1,2}:\d{2}\s*[AP]M)\s*-\s*(?P<end>\d{1,2}:\d{2}\s*[AP]M)",
    re.IGNORECASE,
)
SCHEDULE_RE_DE_A = re.compile(
    r"(?P<days>[A-Za-zÁÉÍÓÚáéíóúñÑ ]+?)\s+de\s+"
    r"(?P<start>\d{1,2}:\d{2}\s*[ap]m)\s+a\s+(?P<end>\d{1,2}:\d{2}\s*[ap]m)",
    re.IGNORECASE,
)


def _find_balanced(text: str, start_idx: int) -> str:
    """text[start_idx] must be '['. Returns the substring from there to
    its matching ']', respecting nested brackets and JSON string quoting
    (so brackets inside strings don't confuse the counter)."""
    assert text[start_idx] == "["
    depth = 0
    in_string = False
    escape = False
    for i in range(start_idx, len(text)):
        c = text[i]
        if in_string:
            if escape:
                escape = False
            elif c == "\\":
                escape = True
            elif c == '"':
                in_string = False
            continue
        if c == '"':
            in_string = True
        elif c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                return text[start_idx : i + 1]
    raise ValueError("unbalanced brackets - no matching ']' found")


def _extract_js_string_literal(text: str, quote_idx: int) -> str:
    """text[quote_idx] must be the opening '"' of a JSON-style quoted
    string. Returns the full literal INCLUDING both quotes, correctly
    respecting backslash escapes (so escaped quotes \" don't end the
    string early) - a naive '".*?"' regex gets this wrong on real Flight
    payloads, where every quote inside the JSON content is backslash-
    escaped."""
    assert text[quote_idx] == '"'
    i = quote_idx + 1
    while i < len(text):
        c = text[i]
        if c == "\\":
            i += 2  # skip the escaped character too
            continue
        if c == '"':
            return text[quote_idx : i + 1]
        i += 1
    raise ValueError("unterminated string literal")


def extract_routes(html: str) -> list:
    """Find every `self.__next_f.push([1,"..."])` call, unescape its
    string payload, and pull out the first "routes":[...] array found
    across all of them."""
    anchor = "self.__next_f.push([1,"
    positions = [m.start() + len(anchor) for m in re.finditer(re.escape(anchor), html)]
    if not positions:
        raise ValueError('no self.__next_f.push([1,"...") calls found - '
                          "page structure may have changed")

    for start in positions:
        if html[start] != '"':
            continue
        raw_str_literal = _extract_js_string_literal(html, start)
        try:
            unescaped = json.loads(raw_str_literal)
        except json.JSONDecodeError:
            continue

        marker = '"routes":['
        idx = unescaped.find(marker)
        if idx == -1:
            continue

        array_start = idx + len(marker) - 1  # position of the '['
        array_str = _find_balanced(unescaped, array_start)
        return json.loads(array_str)

    raise ValueError('no "routes":[...] array found in any push() payload')


def parse_schedule(schedule_text: str) -> dict:
    """'Lunes a sábado: 5:00 AM - 10:30 PM' -> structured start/end in
    24h time, plus the raw day-range text (deliberately NOT mapped to
    specific weekday flags here - 'Lunes a sábado', 'Lunes a domingo',
    'Lunes a viernes' etc. vary per route and should be reviewed by a
    human before being encoded into calendar.txt)."""
    if not schedule_text:
        return {"raw": None, "days_text": None, "start_24h": None, "end_24h": None}

    m = SCHEDULE_RE_COLON.search(schedule_text) or SCHEDULE_RE_DE_A.search(schedule_text)
    if not m:
        return {"raw": schedule_text, "days_text": None, "start_24h": None, "end_24h": None}

    def to_24h(t: str) -> str:
        t = t.upper().replace(" ", "")
        hh, rest = t.split(":")
        mm, ampm = rest[:2], rest[2:]
        h = int(hh)
        if ampm == "PM" and h != 12:
            h += 12
        if ampm == "AM" and h == 12:
            h = 0
        return f"{h:02d}:{mm}:00"

    return {
        "raw": schedule_text,
        "days_text": m.group("days").strip(),
        "start_24h": to_24h(m.group("start")),
        "end_24h": to_24h(m.group("end")),
    }


def main():
    print(f"Fetching {HOMEPAGE_URL} ...")
    r = requests.get(HOMEPAGE_URL, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()

    routes = extract_routes(r.text)
    print(f"Found {len(routes)} route(s) in the embedded payload "
          f"(confirmed complete - the homepage's '35 Rutas Urbanas' stat "
          f"is stale marketing copy, not the real route count).")

    for route in routes:
        route["schedule_parsed"] = parse_schedule(route.get("schedule"))
        route["num_geometry_points"] = len(route.get("geometry") or [])
        route["num_stops"] = len(route.get("stops") or [])

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(routes, indent=2, ensure_ascii=False))

    print(f"\nSaved -> {OUT_PATH}\n")
    print(f"{'code':8s} {'schedule (raw)':38s} {'geom pts':>9s} {'stops':>6s}")
    for route in routes:
        print(f"{route['code']:8s} {str(route.get('schedule'))[:36]:38s} "
              f"{route['num_geometry_points']:9d} {route['num_stops']:6d}")

    no_schedule = [r["code"] for r in routes if not r.get("schedule")]
    if no_schedule:
        print(f"\nNOTE: {len(no_schedule)} route(s) have NO schedule text at all "
              f"(null in the source data): {no_schedule}")

    with_stops = [r["code"] for r in routes if r["num_stops"] > 0]
    if with_stops:
        print(f"\nNOTE: {len(with_stops)} route(s) have non-empty 'stops' - "
              f"check raw/elpoblado_routes.json before trusting these, they "
              f"may be placeholder/test data (confirmed for route 130 in the "
              f"page this script was built from: 'Nombre de la para'/'Parada 2').")


if __name__ == "__main__":
    main()
