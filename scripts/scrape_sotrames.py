#!/usr/bin/env python3
"""
Best-effort scrape of https://www.sotrames.com.co/rutas/

Sotrames publishes plain server-rendered HTML (unlike SAO6/MDO, which are
JS single-page apps we can't scrape this way - see NOTES.md). The page has
a repeating pattern per zone:

    <h1>Rutas y frecuencias <ZONE></h1>
    <ul><li>ROUTE NAME</li>...</ul>          (accordion tab labels)
    <table>...</table>                       (one table per route/tab,
                                               in the same order as the <li>s)

The list-length and table-count don't always match 1:1 once flattened to
text (accordions can share a table across tabs), so this script does NOT
try to guess the pairing. It dumps zone -> [route names] and zone -> [table
rows] *in document order* to a JSON file for a human to reconcile once into
data/operators.yml. Re-run only when Sotrames changes their site.
"""

import json
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

URL = "https://www.sotrames.com.co/rutas/"
OUTPUT = Path("raw/sotrames_scrape.json")


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def main():
    r = requests.get(URL, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    content = soup.select_one("main") or soup

    zones = []
    current_zone = None

    for el in content.find_all(["h1", "h2", "ul", "table"]):
        if el.name in ("h1", "h2"):
            text = clean(el.get_text())
            if "rutas y frecuencias" in text.lower() or "rutas" in text.lower():
                current_zone = {"zone": text, "route_labels": [], "tables": []}
                zones.append(current_zone)

        elif el.name == "ul" and current_zone is not None:
            labels = [clean(li.get_text()) for li in el.find_all("li")]
            labels = [l for l in labels if l]
            if labels:
                current_zone["route_labels"].extend(labels)

        elif el.name == "table" and current_zone is not None:
            rows = []
            for tr in el.find_all("tr"):
                cells = [clean(td.get_text()) for td in tr.find_all(["td", "th"])]
                if cells:
                    rows.append(cells)
            if rows:
                current_zone["tables"].append(rows)

    if not zones:
        print("No zones found - Sotrames may have restructured their page. "
              "Inspect the raw HTML manually.", file=sys.stderr)
        sys.exit(1)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(zones, indent=2, ensure_ascii=False))

    print(f"Found {len(zones)} zone sections.")
    for z in zones:
        print(f"  - {z['zone']}: {len(z['route_labels'])} route labels, "
              f"{len(z['tables'])} tables")
    print(f"Saved raw extraction -> {OUTPUT}")
    print(
        "\nNEXT STEP: open this file, manually pair each route label with "
        "its table (they're in the same visual order on the live page even "
        "though the counts can drift after HTML flattening), and transcribe "
        "the result into data/operators.yml."
    )


if __name__ == "__main__":
    main()
