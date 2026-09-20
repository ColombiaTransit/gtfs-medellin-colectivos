#!/usr/bin/env python3
"""
Scrape Transportes Rapido San Cristobal's /horarios/ page for its
schedule images - confirmed to be photographs (not text/tables) of
printed schedule boards, so this script only collects image metadata,
NOT schedule content (that needs OCR, and given how ambiguous the
route-to-image pairing already is - see below - OCR work is deliberately
deferred until that's resolved, rather than compounding one uncertainty
with another).

IMPORTANT - robots.txt: same situation as scripts/scrape_trsc.py -
trscsas.com's robots.txt disallows automated access, confirmed
directly. This script's `requests` calls don't check robots.txt
themselves; running it is a deliberate choice made by whoever runs it.

CONFIRMED (by reading the real page source directly): 11 schedule
photos, of which only ONE has a real caption in the page HTML itself
(a <figcaption> reading "Cárcel", on the image at 421x487px) - matched
by hand, together with the person running this project, against a
real screenshot of that same image to confirm it's the colored/no-title
grid, NOT the differently-titled image originally guessed. The other 10
photos have no page-level caption; several have a title baked into the
photographed content itself (e.g. "255 A MORAVIA", "255 LLANO"), read
by eye from the uploaded images, not OCR'd yet - this script does not
attempt to read image content at all, only page metadata.

KNOWN PROBLEM THIS SCRIPT DOES NOT SOLVE: there are 25 routes on
/rutas/ but only 11 schedule photos here, and several photo titles
plausibly cover MULTIPLE routes that appear to share one schedule
(e.g. one "255 LLANO" photo for four differently-named "Llano" routes -
confirmed only by the project owner's judgment, not by anything in the
data itself). This script exists to gather real position/dimension
metadata that a later cross-reference step (matching against
scripts/fetch_trsc_kml.py's route geometry/stop names, once built) can
use to help resolve that pairing - it does not attempt the pairing
itself.

Usage: python scripts/scrape_trsc_horarios.py
Output: raw/trsc_horarios_images.json
"""

import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

HORARIOS_URL = "https://trscsas.com/horarios/"
OUT_PATH = Path("raw/trsc_horarios_images.json")


def scrape() -> list:
    r = requests.get(HORARIOS_URL, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    print(f"  GET {HORARIOS_URL} -> HTTP {r.status_code}, {len(r.text)} bytes")
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    images = []
    position = 0
    for img in soup.select("img"):
        src = img.get("src", "")
        if not src or "wp-content/uploads" not in src:
            continue
        # Excludes the site logo (confirmed real filename pattern
        # "LOGO-RSC-SVG-01-...") and any other non-uploads asset - only
        # real content-area photos should end up in the output.
        if "logo" in src.lower():
            continue

        full_url = urljoin(HORARIOS_URL, src)
        width = img.get("width")
        height = img.get("height")

        # A captioned image is wrapped: <figure class="wp-caption"><img>...
        # <figcaption>TEXT</figcaption></figure> - confirmed real
        # structure for the one captioned image on this page.
        figure = img.find_parent("figure", class_="wp-caption")
        caption = None
        if figure:
            fc = figure.find("figcaption")
            if fc:
                caption = fc.get_text(strip=True)

        images.append({
            "position": position,
            "url": full_url,
            "width": int(width) if width else None,
            "height": int(height) if height else None,
            "caption": caption,
        })
        position += 1

    return images


def main():
    print(f"Scraping {HORARIOS_URL} ...")
    images = scrape()

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(images, indent=2, ensure_ascii=False))

    print(f"\nFound {len(images)} schedule image(s):")
    for img in images:
        cap = f" caption={img['caption']!r}" if img["caption"] else ""
        print(f"  [{img['position']}] {img['width']}x{img['height']} "
              f"{img['url']}{cap}")

    captioned = [i for i in images if i["caption"]]
    print(f"\n{len(captioned)} of {len(images)} image(s) have a real page-level "
          f"caption.")
    print(f"Saved -> {OUT_PATH}")
    print(
        "\nNEXT STEPS: (1) download these images and match each URL to its "
        "content by eye - filenames/timestamps and dimensions are the "
        "reliable identifiers, not visual guessing; (2) build "
        "scripts/fetch_trsc_kml.py once scripts/scrape_trsc.py's route "
        "list is finalized, to get real route geometry/stop names that "
        "might help resolve which image belongs to which ambiguous route."
    )


if __name__ == "__main__":
    main()
