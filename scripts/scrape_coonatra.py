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

import copy
import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

RUTAS_URL = "https://coonatra.com/rutas/"
OUT_PATH = Path("raw/coonatra_routes.json")

# Confirmed real URLs (fetched directly and inspected by eye - see the
# conversation this script came from) - used ONLY as a last-resort
# fallback if BOTH dynamic detection methods below find nothing, so a
# CI-environment quirk (bot-blocking, different response to a plain
# `requests` user-agent than a browser gets, etc.) can't silently
# produce zero results the way it did on the first real run. If this
# fallback ever actually triggers, it prints a loud warning - a 5th
# route added later wouldn't be caught by it, so treat that warning as
# a signal to fix the dynamic detection, not to keep relying on this.
FALLBACK_ROUTE_GROUP_URLS = [
    "https://coonatra.com/floresta-san-juan/",
    "https://coonatra.com/calasanz-boston/",
    "https://coonatra.com/copacabana/",
    "https://coonatra.com/circular-coonatra/",
]

SCHEDULE_RE = re.compile(
    r"Inicia:\s*(\d{1,2}:\d{2}\s*[AaPp]\.?\s*[Mm]\.?)\s*[-–]\s*"
    r"(?:Ultima|Última)\s+salida:\s*(\d{1,2}:\d{2}\s*[AaPp]\.?\s*[Mm]\.?)"
    r"(?:\s*[-–]\s*En\s+(?:la\s+|el\s+)?(.+?)\s+(?:a\s+las\s+)?(\d{1,2}:\d{2}\s*[AaPp]\.?\s*[Mm]\.?))?"
)
MAPS_RE = re.compile(r"https://www\.google\.com/maps/d/(?:u/0/)?embed\?mid=([\w-]+)")
HEADING_ONLY_RE = re.compile(r"^#+$")


def get_content_soup(soup):
    """Scope to <main> if present. CONFIRMED NECESSARY against real CI
    output: on 3 of 4 real Coonatra pages, the page's real content
    heading (e.g. "Calasanz-Boston") is ALSO the exact text of an
    earlier nav-menu link on the same page. text.find(heading_text) on
    the whole page's text always finds the nav link first, not the real
    heading - which wrongly anchored names-block extraction at the nav
    menu and swallowed the entire header+footer navigation into
    "names". Scoping to <main> (where nav/header/footer normally don't
    live) sidesteps this entirely. Falls back to a copy of the whole
    soup with <nav>/<header>/<footer> tags removed if no <main> exists.
    """
    main = soup.find("main")
    if main:
        return main
    scoped = copy.copy(soup)
    for tag in scoped.find_all(["nav", "header", "footer"]):
        tag.decompose()
    return scoped


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
    print(f"  GET {RUTAS_URL} -> HTTP {r.status_code}, {len(r.text)} bytes")
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # Strategy 1: exact "Ver ruta" button text (confirmed to match the
    # real page's HTML when checked by hand - see module docstring).
    urls = []
    for a in soup.select("a"):
        if a.get_text(strip=True) == "Ver ruta" and a.get("href"):
            full = urljoin(RUTAS_URL, a["href"])
            if full not in urls:
                urls.append(full)

    # Strategy 2 (fallback): links inside h3/h4 headings under the
    # "rutas" section - the real page also links each route's NAME as a
    # heading to the same URL as its "Ver ruta" button, a redundant and
    # possibly more robust signal if strategy 1 fails for some reason.
    if not urls:
        print("  Strategy 1 ('Ver ruta' text match) found 0 links - trying "
              "heading-link fallback...")
        for tag in soup.select("h3 a, h4 a"):
            href = tag.get("href")
            if href and "coonatra.com" in urljoin(RUTAS_URL, href):
                full = urljoin(RUTAS_URL, href)
                if full not in urls and full != RUTAS_URL:
                    urls.append(full)

    if not urls:
        print("  Both dynamic detection strategies found 0 links. Dumping "
              "diagnostics:", file=sys.stderr)
        print(f"    Total <a> tags on page: {len(soup.select('a'))}", file=sys.stderr)
        sample_texts = [a.get_text(strip=True) for a in soup.select("a")][:30]
        print(f"    First 30 link texts: {sample_texts}", file=sys.stderr)
        print("  Falling back to hardcoded, previously-confirmed URLs - "
              "if this triggers, the site or its response has changed; "
              "fix the detection above rather than relying on this "
              "long-term (a 5th route added later wouldn't be caught).",
              file=sys.stderr)
        urls = list(FALLBACK_ROUTE_GROUP_URLS)

    return urls


def scrape_route_group(url: str) -> dict:
    r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    print(f"  GET {url} -> HTTP {r.status_code}, {len(r.text)} bytes")
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    content = get_content_soup(soup)
    text = content.get_text("\n")

    first_inicia = text.find("Inicia:")
    if first_inicia == -1:
        print(f"  WARNING: no 'Inicia:' found anywhere in the scoped content - "
              f"the schedule format may differ from what this script expects, "
              f"or <main> scoping excluded the real content by mistake.",
              file=sys.stderr)

    # Names: short lines between the LAST heading (h1-h6) appearing
    # BEFORE the first "Inicia:" and that "Inicia:" itself, searched
    # within the CONTENT-SCOPED text only (see get_content_soup - this
    # is what fixes the real nav-menu-swallowing bug confirmed on 3 of
    # 4 real pages).
    headings = content.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    title, title_end_idx = "", 0
    for h in headings:
        h_text = h.get_text(strip=True)
        if not h_text:
            continue
        pos = text.find(h_text)
        if pos != -1 and (first_inicia == -1 or pos < first_inicia):
            title, title_end_idx = h_text, pos + len(h_text)

    names_block = text[title_end_idx:first_inicia] if first_inicia != -1 else ""
    names = [
        l.strip() for l in names_block.splitlines()
        if l.strip() and "http" not in l and not HEADING_ONLY_RE.match(l.strip())
    ]

    schedule_matches = SCHEDULE_RE.findall(text)
    # Maps URLs are inside <iframe src="..."> attributes, CONFIRMED via
    # real CI output to be invisible to soup.get_text() (which only
    # returns rendered text nodes, never attribute values) - every page
    # came back with mids=0 until this was changed to search the RAW
    # HTML response text instead of the flattened text stream.
    mids = MAPS_RE.findall(r.text)

    print(f"  title_anchor={title!r} names_block_len={len(names_block)} "
          f"names={len(names)} schedules={len(schedule_matches)} mids={len(mids)}")
    if not (len(names) == len(schedule_matches) == len(mids)) and names_block:
        print(f"  names found: {names}", file=sys.stderr)

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
