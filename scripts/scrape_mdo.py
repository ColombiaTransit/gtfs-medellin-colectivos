#!/usr/bin/env python3
"""
Best-effort scrape of MDO's per-route schedule info-card IMAGES.

Unlike SAO6 (a JS single-page app that renders nothing to a plain HTTP
fetch), masivodeoccidente.com is a plain WordPress site - the homepage's
"MAPAS MDO" / "Alimentadores del Sistema Metro" section is real, static
HTML, listing all 15 route codes/names in order, each followed by an
<img> whose filename literally includes "con-horarios" ("with
schedules") for at least some of them. Confirmed by inspection: these
are RASTER images with the schedule baked into pixels (first/last
departure per day type, peak/off-peak headway) - not real DOM text, so
OCR is genuinely needed here, unlike everywhere else in this project.

CAVEAT - untested against the real site: this script was written and
its OCR/regex-parsing logic validated against a synthetic mockup of the
same layout, but masivodeoccidente.com could not be reached from the
environment that wrote it (no image-fetch capability, network
allowlist). Two things to verify on a real run:
  1. Route <-> image pairing. The homepage's HTML has one anomaly right
     after the route list (two consecutive "Lugares de referencia
     cercanos" blocks before the first image), which may throw off the
     simple positional pairing used below by one route. Cross-check
     the pairing log (written every run) against the live page by eye
     the first time this runs for real.
  2. OCR accuracy on the actual images - a real infographic (map
     background, colored boxes, mixed fonts) will OCR worse than the
     synthetic mockup this was tested against. Read raw/mdo_ocr/*.txt
     for any route where a field comes out missing and fix by hand.

Requires: pip install pytesseract pillow beautifulsoup4 requests
          + the tesseract-ocr and tesseract-ocr-spa system packages
          (apt-get install tesseract-ocr tesseract-ocr-spa) - Spanish
          language data matters for words like "Sábado"/"Domingo".
"""

import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

import pytesseract
import requests
from bs4 import BeautifulSoup
from PIL import Image

HOMEPAGE_URL = "https://masivodeoccidente.com/"
OUT_DIR = Path("raw/mdo_images")
OCR_DIR = Path("raw/mdo_ocr")
RESULT_PATH = Path("raw/mdo_schedule_ocr.json")
PAIRING_LOG_PATH = Path("raw/mdo_pairing_log.md")

ROUTE_LINE_RE = re.compile(r"^(C3-\S+)\s+(.+)$")

DAY_LABELS = {
    "laborable": r"Lunes\s*a\s*Viernes",
    "sabado": r"S[aá]bado",
    "domingo_festivo": r"Domingo\s*y\s*festivos",
}
TIME_RE = r"(\d{1,2}[:.]\d{2}\s*[ap]\.?\s*m\.?)"


def fetch_route_list_and_images():
    """Parse the homepage's route list and the <img> tags following it,
    in document order. Returns (routes, image_urls) - two parallel-ish
    lists; see module docstring caveat about possible off-by-one."""
    r = requests.get(HOMEPAGE_URL, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    text = soup.get_text("\n")
    routes = []
    in_section = False
    for line in text.splitlines():
        line = line.strip()
        if "Alimentadores del Sistema Metro" in line:
            in_section = True
            continue
        if not in_section:
            continue
        m = ROUTE_LINE_RE.match(line)
        if m:
            routes.append({"route_id": m.group(1), "name": m.group(2)})
        elif routes and line and not line.startswith("C3-"):
            # First non-route-list line after routes start = end of the list.
            break

    # Images living under the same uploads path as the known
    # "Mapas-MDO-con-horarios" example, in document order.
    all_imgs = [
        urljoin(HOMEPAGE_URL, img["src"])
        for img in soup.find_all("img")
        if img.get("src") and "/wp-content/uploads/" in img["src"]
    ]
    # Narrow to a plausible contiguous run the same length as the route
    # list, anchored on images from the same upload batch as the known
    # "Mapas-MDO-con-horarios" example - heuristic, log everything for
    # review since the exact upload date/path may drift over time.
    candidate_imgs = [u for u in all_imgs if re.search(r"/uploads/2026/", u)]

    return routes, candidate_imgs


def ocr_image(path: Path) -> str:
    try:
        return pytesseract.image_to_string(Image.open(path), lang="spa+eng")
    except pytesseract.TesseractError:
        # Spanish language pack not installed - fall back to English,
        # which still gets numbers/times right, just not accented words.
        return pytesseract.image_to_string(Image.open(path), lang="eng")


def parse_schedule_text(ocr_text: str) -> dict:
    """Best-effort structured extraction from raw OCR text. Returns a
    dict with day_types (possibly incomplete) and headway info; always
    keep ocr_text alongside the parsed result so a human can fix
    whatever the regexes missed."""
    result = {"day_types": {}, "peak_headway_min": None, "offpeak_headway_min": None}

    # Split into a start-times block and an end-times block using the
    # two "Hora de..." headers as anchors.
    start_match = re.search(
        r"Hora de inicio del servicio(.*?)(?:Hora de|$)", ocr_text, re.S | re.I
    )
    end_match = re.search(
        r"Hora de.{0,15}ltimo servicio(.*?)(?:Frecuencia|$)", ocr_text, re.S | re.I
    )

    for day_key, day_pattern in DAY_LABELS.items():
        result["day_types"].setdefault(day_key, {})
        if start_match:
            m = re.search(day_pattern + r".{0,20}?" + TIME_RE, start_match.group(1), re.I)
            if m:
                result["day_types"][day_key]["first_departure_raw"] = m.group(1)
        if end_match:
            m = re.search(day_pattern + r".{0,20}?" + TIME_RE, end_match.group(1), re.I)
            if m:
                result["day_types"][day_key]["last_departure_raw"] = m.group(1)

    peak_m = re.search(r"pico\D{0,15}(\d{1,2})\s*minutos", ocr_text, re.I)
    if peak_m:
        result["peak_headway_min"] = int(peak_m.group(1))
    valle_m = re.search(r"valle\D{0,15}(\d{1,2})\s*minutos", ocr_text, re.I)
    if valle_m:
        result["offpeak_headway_min"] = int(valle_m.group(1))

    return result


def to_24h(raw_time: str) -> str:
    """'03:58 am' -> '03:58:00'; '11:33 pm' -> '23:33:00'."""
    raw_time = raw_time.lower().replace(".", "").replace(" ", "")
    m = re.match(r"(\d{1,2})[:.](\d{2})(am|pm)", raw_time)
    if not m:
        return raw_time  # leave as-is; caller should notice it's unparsed
    h, mins, ampm = int(m.group(1)), m.group(2), m.group(3)
    if ampm == "pm" and h != 12:
        h += 12
    if ampm == "am" and h == 12:
        h = 0
    return f"{h:02d}:{mins}:00"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OCR_DIR.mkdir(parents=True, exist_ok=True)

    routes, image_urls = fetch_route_list_and_images()

    with PAIRING_LOG_PATH.open("w") as log:
        log.write("# MDO route <-> image pairing (verify by eye against the live page)\n\n")
        log.write(f"Routes found: {len(routes)}\nImages found: {len(image_urls)}\n\n")
        for i, r in enumerate(routes):
            img = image_urls[i] if i < len(image_urls) else "MISSING"
            log.write(f"{i}: {r['route_id']} ({r['name']}) -> {img}\n")

    if len(routes) != len(image_urls):
        print(
            f"WARNING: found {len(routes)} routes but {len(image_urls)} candidate "
            f"images - pairing below is positional and may be off. See "
            f"{PAIRING_LOG_PATH} and fix the image list filter if needed.",
            file=sys.stderr,
        )

    results = {}
    for i, route in enumerate(routes):
        route_id = route["route_id"]
        if i >= len(image_urls):
            print(f"  {route_id}: no image available, skipping")
            continue

        img_url = image_urls[i]
        ext = Path(img_url).suffix or ".jpg"
        img_path = OUT_DIR / f"{route_id}{ext}"

        print(f"Fetching image for {route_id}: {img_url}")
        r = requests.get(img_url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        img_path.write_bytes(r.content)

        ocr_text = ocr_image(img_path)
        (OCR_DIR / f"{route_id}.txt").write_text(ocr_text)

        parsed = parse_schedule_text(ocr_text)
        for day in parsed["day_types"].values():
            if "first_departure_raw" in day:
                day["first_departure"] = to_24h(day["first_departure_raw"])
            if "last_departure_raw" in day:
                day["last_departure"] = to_24h(day["last_departure_raw"])

        results[route_id] = parsed

        got_all_days = all(
            "first_departure" in d and "last_departure" in d
            for d in parsed["day_types"].values()
        ) and len(parsed["day_types"]) == 3
        got_headways = parsed["peak_headway_min"] and parsed["offpeak_headway_min"]
        status = "OK" if (got_all_days and got_headways) else "INCOMPLETE - check raw OCR text"
        print(f"  {route_id}: {status}")

    RESULT_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\nSaved parsed results -> {RESULT_PATH}")
    print(f"Saved pairing log -> {PAIRING_LOG_PATH}")
    print(f"Raw OCR text per route -> {OCR_DIR}/<route_id>.txt")
    print(
        "\nNEXT STEP: review raw/mdo_schedule_ocr.json - any route marked "
        "INCOMPLETE above needs its raw OCR text checked by hand before "
        "transcribing into data/operators.yml."
    )


if __name__ == "__main__":
    main()
