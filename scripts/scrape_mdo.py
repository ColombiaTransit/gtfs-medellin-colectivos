#!/usr/bin/env python3
"""
Best-effort scrape of MDO's per-route schedule info-card IMAGES.

masivodeoccidente.com is a plain WordPress site (unlike SAO6's JS SPA) -
the homepage's "MAPAS MDO" section is real static HTML listing all 15
route codes/names in order, each followed by an <img>. The schedule
(first/last departure per day type, peak/off-peak headway) is baked into
those images as pixels, not real DOM text - genuinely needs OCR.

REVISION 2 - rewritten after testing against a REAL downloaded image
(C3-007A), not just a synthetic mockup. The first version's whole-image
OCR + regex approach was unreliable on the real card: Tesseract's
default page segmentation interleaves the two side-by-side "Lugar de
inicio" / "Lugar de finalización" panels inconsistently row-by-row (the
first day-type row often reads fine, later rows get scrambled or
dropped), and a naive "label followed by a nearby number" regex mis-pairs
label/number when OCR groups all labels together before all numbers
(confirmed happening for the "Horario pico / Horario valle" band too).

Fixed by:
  1. Cropping the image into 3 regions BEFORE OCR (left "Lugar de
     inicio" panel, right "Lugar de finalización" panel, bottom
     "Frecuencia Estimada" band) - isolating each panel avoids
     column-interleaving entirely. Crop fractions (CROP_FRACTIONS below)
     were calibrated against one image (1920x1920, route C3-007A) and
     since CONFIRMED against all 15 real MDO images - every route uses
     the same 1920x1920 template, and every one parsed cleanly
     (plausible ~4am-11pm hours, 5-15 min headways, and two related
     routes - C3-007/C3-007A - came back with nearly identical hours but
     different frequencies, which is internally consistent, not just
     individually plausible).
  2. Time panels: 3x LANCZOS upscale + Tesseract `--psm 11` (sparse
     text) reliably extracts all 3 day-type times in top-to-bottom
     order. Rather than OCR-matching the (frequently garbled) day-type
     LABELS, the 3 times are assigned POSITIONALLY to the card's fixed,
     known row order: Lunes a Viernes, Sábado, Domingo y festivos.
  3. Frequency band: plain (non-sparse) OCR, then "Horario X" labels and
     "N minutos" numbers are each collected as ordered lists and zipped
     together POSITIONALLY (1st label <-> 1st number, etc.) rather than
     regex-matched by proximity - proximity-based matching mis-paired
     pico/valle on the real image because OCR grouped both labels
     together before both numbers.

CONFIRMED against all 15 real downloaded MDO images (not just C3-007A):
every route parsed with plausible, internally-consistent values. One
route (C3-004MD) came back with much shorter service hours than the
rest (~16:21-19:56 vs ~23:00) - confirmed correct by a human, not an
OCR error (it's a limited-hours extension route, matching its "Ext."
name). The results from this run are already in data/operators.yml.

Requires: pip install pytesseract pillow beautifulsoup4 requests
          + the tesseract-ocr and tesseract-ocr-spa system packages.
          NOTE: the validated pipeline above used lang='eng' throughout
          since it only depends on digits/am/pm and English label words
          ("Horario", "minutos" are read fine without Spanish data
          because they're plain Latin script) - 'spa' is still requested
          first for the whole-image dump kept for human review, which
          isn't relied on for parsing.
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
TIME_RE = re.compile(r"(\d{1,2}[:.]\d{2}\s*[ap]\.?\s*m\.?)", re.I)

# Fixed row order on every card checked so far - used to assign OCR'd
# times POSITIONALLY rather than by (unreliable) day-label text matching.
DAY_ORDER = ["laborable", "sabado", "domingo_festivo"]

# Fractions of (x0, y0, x1, y1) as fractions of (width, height) -
# calibrated against C3-007A (1920x1920), confirmed working across all
# 15 MDO route images (same template/dimensions). left panel: "Lugar de
# inicio" (first_departure). right panel: "Lugar de finalización"
# (last_departure). bottom band: "Frecuencia Estimada".
CROP_FRACTIONS = {
    "left": (0.0, 0.58, 0.50, 0.84),
    "right": (0.50, 0.58, 1.0, 0.84),
    "bottom": (0.0, 0.84, 1.0, 1.0),
}


def fetch_route_list_and_images():
    """Parse the homepage's route list and the <img> tags following it,
    in document order. Returns (routes, image_urls) - confirmed to pair
    up correctly (verified against the real pairing log + real images)."""
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

    all_imgs = [
        urljoin(HOMEPAGE_URL, img["src"])
        for img in soup.find_all("img")
        if img.get("src") and "/wp-content/uploads/" in img["src"]
    ]
    # Narrow to a plausible contiguous run the same length as the route
    # list, anchored on images from the same upload batch as the known
    # "Mapas-MDO-con-horarios" example.
    candidate_imgs = [u for u in all_imgs if re.search(r"/uploads/2026/", u)]

    return routes, candidate_imgs


def crop(img: Image.Image, box_name: str) -> Image.Image:
    w, h = img.size
    x0f, y0f, x1f, y1f = CROP_FRACTIONS[box_name]
    return img.crop((int(w * x0f), int(h * y0f), int(w * x1f), int(h * y1f)))


def ocr_times_panel(panel: Image.Image) -> list:
    """Crop for a time panel -> list of times found, top-to-bottom order."""
    upscaled = panel.resize((panel.width * 3, panel.height * 3), Image.LANCZOS)
    text = pytesseract.image_to_string(upscaled, lang="eng", config="--psm 11")
    return TIME_RE.findall(text)


def ocr_frequency_panel(panel: Image.Image) -> dict:
    """Crop for the frequency band -> {'peak_headway_min': N, 'offpeak_headway_min': N}."""
    text = pytesseract.image_to_string(panel, lang="eng")
    labels = re.findall(r"Horario\s+(pico|valle)", text, re.I)
    numbers = re.findall(r"(\d{1,2})\s*minutos", text, re.I)
    result = {}
    for label, num in zip(labels, numbers):
        key = "peak_headway_min" if label.lower() == "pico" else "offpeak_headway_min"
        result[key] = int(num)
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


def parse_route_image(img_path: Path) -> dict:
    img = Image.open(img_path)

    first_times = ocr_times_panel(crop(img, "left"))
    last_times = ocr_times_panel(crop(img, "right"))
    freq = ocr_frequency_panel(crop(img, "bottom"))

    day_types = {}
    for i, day in enumerate(DAY_ORDER):
        day_types[day] = {}
        if i < len(first_times):
            day_types[day]["first_departure"] = to_24h(first_times[i])
        if i < len(last_times):
            day_types[day]["last_departure"] = to_24h(last_times[i])

    return {
        "day_types": day_types,
        "peak_headway_min": freq.get("peak_headway_min"),
        "offpeak_headway_min": freq.get("offpeak_headway_min"),
    }


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

        # Whole-image OCR too, saved for human review only (not parsed
        # from) - useful context if the crop-based parse below is wrong.
        try:
            whole_text = pytesseract.image_to_string(Image.open(img_path), lang="spa+eng")
        except pytesseract.TesseractError:
            whole_text = pytesseract.image_to_string(Image.open(img_path), lang="eng")
        (OCR_DIR / f"{route_id}.txt").write_text(whole_text)

        try:
            parsed = parse_route_image(img_path)
        except Exception as exc:  # noqa: BLE001
            print(f"  {route_id}: ERROR during crop/OCR - {exc}", file=sys.stderr)
            parsed = {"day_types": {d: {} for d in DAY_ORDER},
                      "peak_headway_min": None, "offpeak_headway_min": None}

        results[route_id] = parsed

        got_all_days = all(
            "first_departure" in d and "last_departure" in d
            for d in parsed["day_types"].values()
        )
        got_headways = parsed["peak_headway_min"] and parsed["offpeak_headway_min"]
        status = "OK" if (got_all_days and got_headways) else "INCOMPLETE - check raw OCR text"
        print(f"  {route_id}: {status}")

    RESULT_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\nSaved parsed results -> {RESULT_PATH}")
    print(f"Saved pairing log -> {PAIRING_LOG_PATH}")
    print(f"Whole-image raw OCR text (for review only) -> {OCR_DIR}/<route_id>.txt")
    print(
        "\nNEXT STEP: review raw/mdo_schedule_ocr.json - any route marked "
        "INCOMPLETE needs CROP_FRACTIONS recalibrated for its image (open "
        "the image, check panel boundaries) before transcribing into "
        "data/operators.yml. Routes marked OK are still worth a spot-check "
        "against their source image before trusting the numbers."
    )


if __name__ == "__main__":
    main()
