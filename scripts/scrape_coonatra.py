#!/usr/bin/env python3
"""
Scrape Coonatra's route-group pages (coonatra.com/rutas/ and each named
route's own page) for per-branch schedule text and Google My Maps IDs,
plus any linked frequency-timetable PDF.

Coonatra is a plain WordPress/Elementor site - no JS rendering needed,
unlike SAO6 or El Poblado. Each of the 4 top-level route-group pages
(Floresta-San Juan, Calasanz-Boston, Copacabana, Circular Coonatra) lists
several branch NAMES (e.g. "310", "310 Rosal", "242 Divisa"), followed by
a sequence of (schedule heading, Google My Maps embed) pairs, in that
document order.

CONFIRMED (from the real pages, checked by eye before writing this):
  - Floresta-San Juan and Calasanz-Boston: names/schedules/mids counts
    match exactly (4/4/4 and 6/6/6) - clean positional 1:1 pairing.
  - Copacabana and Circular Coonatra: counts DON'T match (Copacabana:
    5 names vs 7 schedules vs 9 mids; Circular: 3 names vs 2 schedules
    vs 3 mids) - some schedule headings apply to more than one map
    (two directions sharing one schedule), and category names ("Rutas
    autopista", "Urbanas"...) don't correspond 1:1 to individual
    branches. This script does NOT guess a pairing for these - it dumps
    the raw lists in document order for manual reconciliation, same
    principle as scripts/scrape_sotrames.py.
  - Calasanz-Boston links a real frequency-timetable PDF (literal
    per-trip departure times, not just headway) - detected and its URL
    recorded; the OTHER 3 pages have no such link found. This script
    only records the URL - see scripts/parse_coonatra_pdf.py for
    extracting the actual table (a separate step, deliberately not
    combined here, since PDF table parsing needs real bounding-box data
    this HTML scraper has no access to).

TESTED: the schedule/mids regexes and the mismatch-detection logic were
verified against the real text of all 4 pages (copied by hand from
actual fetches, not synthetic mockups) before this was written - see the
conversation this script came from. The names-list filter had a real
bug (a stray markdown "#####" heading marker leaking into the names
list, breaking Calasanz-Boston's otherwise-clean match) - fixed and
reconfirmed.
"""

import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

RUTAS_URL = "https://coonatra.com/rutas/"
OUT_PATH = Path("raw/coonatra_routes.json")

SCHEDULE_RE = re.compile(
    r"Inicia:\s*(\d{1,2}:\d{2}\s*[AaPp]\.?\s*[Mm]\.?)\s*[-–]\s*"
    r"(?:Ultima|Última)\s+salida:\s*(\d{1,2}:\d{2}\s*[AaPp]\.?\s*[Mm]\.?)"
    r"(?:\s*[-–]\s*En\s+(?:la\s+|el\s+)?(.+?)\s+(?:a\s+las\s+)?(\d{1,2}:\d{2}\s*[AaPp]\.?\s*[Mm]\.?))?"
)
MAPS_RE = re.compile(r"https://www\.google\.com/maps/d/(?:u/0/)?embed\?mid=([\w-]+)")
HEADING_ONLY_RE = re.compile(r"^#+$")


def to_24h(t: str) -> str:
    t = t.lower().replace(".", "").replace(" ", "")
    m = re.match(r"(\d{1,2}):(\d{2})(am|pm)", t)
    if not m:
        return t
    h, mm, ampm = int(m.group(1)), m.group(2), m.group(3)
    if ampm == "pm" and h != 12:
        h += 12
    if ampm == "am" and h == 12:
        h = 0
    return f"{h:02d}:{mm}:00"


def fetch_route_group_urls() -> list:
    r = requests.get(RUTAS_URL, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    urls = []
    for a in soup.select("a"):
        text = a.get_text(strip=True)
        href = a.get("href", "")
        if text == "Ver ruta" and href:
            full = urljoin(RUTAS_URL, href)
            if full not in urls:
                urls.append(full)
    return urls


def scrape_route_group(url: str) -> dict:
    r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text("\n")

    # Names: short lines between the page's main heading and the first
    # "Inicia:" occurrence - see module docstring for why this heuristic
    # (and not a specific CSS selector, which would need real HTML tag
    # names this was built without seeing directly).
    h1 = soup.find(["h1", "h2"])
    title = h1.get_text(strip=True) if h1 else ""
    title_idx = text.find(title) if title else 0
    first_inicia = text.find("Inicia:", title_idx if title_idx >= 0 else 0)
    names_block = text[(title_idx + len(title)) if title_idx >= 0 else 0 : first_inicia]
    names = [
        l.strip() for l in names_block.splitlines()
        if l.strip() and "http" not in l and not HEADING_ONLY_RE.match(l.strip())
    ]

    schedule_matches = SCHEDULE_RE.findall(text)
    mids = MAPS_RE.findall(text)

    schedules = []
    for start, end, place, place_time in schedule_matches:
        schedules.append({
            "raw_start": start, "raw_end": end,
            "start_24h": to_24h(start), "end_24h": to_24h(end),
            "intermediate_place": place or None,
            "intermediate_time_24h": to_24h(place_time) if place_time else None,
        })

    clean_match = len(names) == len(schedules) == len(mids)

    pdf_links = [
        urljoin(url, a["href"]) for a in soup.select("a")
        if a.get("href", "").lower().endswith(".pdf")
    ]

    result = {
        "url": url,
        "title": title,
        "names": names,
        "schedules": schedules,
        "mids": mids,
        "clean_1to1_match": clean_match,
        "frequency_pdf_urls": pdf_links,
    }

    if clean_match:
        result["branches"] = [
            {"name": n, **s, "mid": m}
            for n, s, m in zip(names, schedules, mids)
        ]
    else:
        result["branches"] = None  # ambiguous - needs manual reconciliation

    return result


def main():
    print(f"Fetching route-group list from {RUTAS_URL} ...")
    group_urls = fetch_route_group_urls()
    print(f"Found {len(group_urls)} route-group page(s): {group_urls}")

    results = []
    for url in group_urls:
        print(f"\nScraping {url} ...")
        data = scrape_route_group(url)
        results.append(data)

        status = "CLEAN 1:1 MATCH" if data["clean_1to1_match"] else "AMBIGUOUS - needs manual reconciliation"
        print(f"  names={len(data['names'])} schedules={len(data['schedules'])} "
              f"mids={len(data['mids'])} -> {status}")
        if data["frequency_pdf_urls"]:
            print(f"  Frequency PDF(s) found: {data['frequency_pdf_urls']}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\nSaved -> {OUT_PATH}")

    ambiguous = [r["title"] for r in results if not r["clean_1to1_match"]]
    if ambiguous:
        print(f"\nNOTE: {len(ambiguous)} page(s) need manual reconciliation "
              f"(names/schedules/mids counts don't match 1:1): {ambiguous}. "
              f"Check raw/coonatra_routes.json's 'names'/'schedules'/'mids' "
              f"lists for these by eye against the live page.")


if __name__ == "__main__":
    main()
