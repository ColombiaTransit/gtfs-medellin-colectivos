#!/usr/bin/env python3
"""
Scrape Tax Maya (taxmaya.com) for route descriptions and schedule
info, from two pages:
  - /ruta-c23-san-cristobal-san-javier-centro ("Nuestras rutas") - 11
    routes, each a bullet item: <strong>NAME:</strong> description
    text. Real content confirmed present in the server-rendered HTML
    (unlike trscsas.com, a plain `requests` GET gets the real content
    here - verified directly against real page source, not assumed).
  - /Mapas-rutas-y-horarios ("Horarios") - same bullet-item pattern for
    route descriptions, PLUS standalone "Inicia X y ultimo despacho Y"
    paragraphs (basic first/last-departure hours - confirmed real for
    C23 and C23i only), PLUS route-map images, some with a bold-text
    caption identifying the route (e.g. "Ruta 195ii Almeria II"), most
    without any caption at all.

WHAT THIS SCRIPT DELIBERATELY DOES NOT DO: associate uncaptioned
images with a specific route by their position in the page. Several
richer schedule images exist for the 195/195i routes specifically
(real frequency data: weekday/Saturday/Sunday hours, peak/off-peak
minutes, round-trip time - confirmed from two real screenshots shared
directly, not scraped, since this data lives in the image content
itself, not the page text) - but that's a human judgment call the same
way TRSC's horarios photos needed careful, collaborative pairing, not
something to guess from image order in the DOM.

STRUCTURAL NOTE: Google Sites' CSS class names (e.g. "TYR86d",
"n8H08c") look like auto-generated build artifacts that could change
between page rebuilds - this script anchors on TEXT content ("RUTAS:",
"Rutas urbanas:", "Inicia ... despacho ...") and DOM structure (next
sibling <ul>, parent <li>) instead of exact class names, for
resilience against a site rebuild changing those classes.

Usage: python scripts/scrape_taxmaya.py
Output: raw/taxmaya_routes.json (11 routes: name + description)
        raw/taxmaya_horarios.json (route bullets on this page, "Inicia
        ... despacho ..." blocks, and images with position + caption,
        all in real DOM order)
"""

import json
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

RUTAS_URL = "https://www.taxmaya.com/ruta-c23-san-cristobal-san-javier-centro"
HORARIOS_URL = "https://www.taxmaya.com/Mapas-rutas-y-horarios"
ROUTES_OUT = Path("raw/taxmaya_routes.json")
HORARIOS_OUT = Path("raw/taxmaya_horarios.json")

INICIA_RE = re.compile(r"Inicia\s+([\d:apm\s]+?)\s+y\s+ultimo\s+despacho\s+([\d:apm\s]+)", re.IGNORECASE)


def fetch(url: str) -> BeautifulSoup:
    r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    print(f"  GET {url} -> HTTP {r.status_code}, {len(r.text)} bytes")
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")


def extract_route_bullets(soup: BeautifulSoup) -> list:
    """Finds every <li> whose text starts with a bold NAME: followed
    by a description - the real, confirmed structure for the RUTAS
    page's route list specifically. The HORARIOS page's route bullets
    are NOT bold (confirmed from its real page source: plain
    "C23: Deposito de buses..." text, no <strong> at all) - calling
    this on that page legitimately returns nothing for those, which is
    accurate, not a bug; that page's real unique content is its Inicia
    blocks and images, extracted separately below. Returns
    [{"name": ..., "description": ...}, ...] in DOM order."""
    routes = []
    for li in soup.find_all("li"):
        p = li.find("p", recursive=False)
        if not p:
            continue
        strong = p.find("strong")
        if not strong or not strong.get_text(strip=True):
            continue
        name = strong.get_text(strip=True).rstrip(":").strip()
        full_text = p.get_text(" ", strip=True)
        # Description is everything after the bold name + colon
        description = full_text[len(strong.get_text(strip=True)):].lstrip(": ").strip()
        if not description:
            continue
        routes.append({"name": name, "description": description})
    return routes


def extract_inicia_blocks(soup: BeautifulSoup) -> list:
    """Finds every standalone 'Inicia X y ultimo despacho Y' paragraph
    - confirmed real, centered, bold text blocks giving basic first/
    last-departure hours for the route(s) listed immediately before
    them. Returns matches in DOM order; associating each with a
    specific route is left to a human, not guessed here."""
    blocks = []
    for p in soup.find_all("p"):
        text = p.get_text(" ", strip=True)
        m = INICIA_RE.search(text)
        if m:
            blocks.append({"raw_text": text, "start": m.group(1).strip(),
                            "end": m.group(2).strip()})
    return blocks


def extract_images(soup: BeautifulSoup) -> list:
    """Finds every route-map image in DOM order, with its caption if
    one exists. A REAL caption (confirmed from the page source, e.g.
    "Ruta 195ii Almeria II") sits ALONE in its own dedicated <section>
    with nothing else in it, immediately before the image's own
    <section> - tested directly against a case that initially
    (wrongly) picked up "Rutas urbanas:"/"Rutas integradas:" as
    captions, since those bold headers also happen to sit in a
    preceding section, just one that ALSO contains a full bullet list
    and Inicia block, not a dedicated caption section. Only a preceding
    section with NO <ul> inside is trusted as a real caption source."""
    images = []
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if not src or "lh7-us.googleusercontent.com" not in src:
            continue  # skip logos/icons, keep only real content images

        caption = None
        section = img.find_parent("section")
        prev = section.find_previous_sibling("section") if section else None
        if prev and not prev.find("ul"):
            strong = prev.find("strong")
            if strong:
                text = strong.get_text(strip=True)
                if text and len(text) < 150:
                    caption = text

        images.append({"position": len(images), "url": src, "caption": caption})
    return images


def main():
    print(f"Scraping {RUTAS_URL} ...")
    rutas_soup = fetch(RUTAS_URL)
    routes = extract_route_bullets(rutas_soup)
    ROUTES_OUT.parent.mkdir(parents=True, exist_ok=True)
    ROUTES_OUT.write_text(json.dumps(routes, indent=2, ensure_ascii=False))
    print(f"  {len(routes)} route(s) found -> {ROUTES_OUT}")
    for r in routes:
        print(f"    {r['name']}")

    print(f"\nScraping {HORARIOS_URL} ...")
    horarios_soup = fetch(HORARIOS_URL)
    horarios_routes = extract_route_bullets(horarios_soup)
    inicia_blocks = extract_inicia_blocks(horarios_soup)
    images = extract_images(horarios_soup)

    horarios_data = {
        "route_bullets": horarios_routes,
        "inicia_blocks": inicia_blocks,
        "images": images,
    }
    HORARIOS_OUT.write_text(json.dumps(horarios_data, indent=2, ensure_ascii=False))
    print(f"  {len(horarios_routes)} route bullet(s), {len(inicia_blocks)} "
          f"'Inicia...' block(s), {len(images)} image(s) -> {HORARIOS_OUT}")
    for b in inicia_blocks:
        print(f"    Inicia {b['start']} - despacho {b['end']}")
    captioned = [i for i in images if i["caption"]]
    print(f"  {len(captioned)} of {len(images)} image(s) have a caption")
    for i in images:
        cap = f" ({i['caption']})" if i["caption"] else " (no caption)"
        print(f"    [{i['position']}]{cap}")

    print(
        "\nNEXT STEP: associate uncaptioned images and 'Inicia...' blocks with "
        "specific routes by hand - same collaborative process used for TRSC's "
        "horarios photos, not something this script guesses."
    )


if __name__ == "__main__":
    main()
