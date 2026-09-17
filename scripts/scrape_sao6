#!/usr/bin/env python3

import json
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.sao6.com.co"
ROUTES_URL = f"{BASE_URL}/rutas"

OUTPUT_DIR = Path("output")
KML_DIR = OUTPUT_DIR / "kml"

OUTPUT_DIR.mkdir(exist_ok=True)
KML_DIR.mkdir(exist_ok=True)

session = requests.Session()
session.headers.update(
    {
        "User-Agent": "Mozilla/5.0 (GTFS Builder)"
    }
)


def get_soup(url):
    r = session.get(url, timeout=60)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")


def get_route_links():
    soup = get_soup(ROUTES_URL)

    route_links = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if "/rutas/" in href:
            route_links.add(urljoin(BASE_URL, href))

    return sorted(route_links)


def extract_route_code(text):
    match = re.search(r"(C\d+-\d+[A-Z]?)", text)
    if match:
        return match.group(1)
    return None


def get_google_iframe(soup):
    for iframe in soup.find_all("iframe", src=True):
        src = iframe["src"]

        if "google.com/maps" in src:
            return src

    return None


def extract_mid(embed_url):
    if not embed_url:
        return None

    parsed = urlparse(embed_url)
    qs = parse_qs(parsed.query)

    if "mid" in qs:
        return qs["mid"][0]

    match = re.search(r"mid=([^&]+)", embed_url)

    if match:
        return match.group(1)

    return None


def download_kml(mid, route_code):
    url = f"https://www.google.com/maps/d/kml?mid={mid}&forcekml=1"

    try:
        r = session.get(url, timeout=60)

        if r.status_code != 200:
            return None

        filename = KML_DIR / f"{route_code}.kml"

        with open(filename, "wb") as f:
            f.write(r.content)

        return str(filename)

    except Exception as ex:
        print(f"KML download failed: {ex}")

    return None


def scrape_route(route_url):
    print(f"Scraping {route_url}")

    soup = get_soup(route_url)

    title = ""

    h1 = soup.find("h1")
    if h1:
        title = h1.get_text(" ", strip=True)

    page_text = soup.get_text(" ", strip=True)

    route_code = extract_route_code(
        title if title else page_text
    )

    embed_url = get_google_iframe(soup)

    mid = extract_mid(embed_url)

    kml_file = None

    if mid and route_code:
        kml_file = download_kml(mid, route_code)

    return {
        "route_code": route_code,
        "title": title,
        "url": route_url,
        "google_embed": embed_url,
        "google_mid": mid,
        "kml_file": kml_file,
    }


def main():
    routes = []

    route_links = get_route_links()

    print(f"Found {len(route_links)} route pages")

    for route_url in route_links:
        try:
            route = scrape_route(route_url)
            routes.append(route)

        except Exception as ex:
            print(f"ERROR {route_url}: {ex}")

    output_file = OUTPUT_DIR / "routes.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(routes, f, ensure_ascii=False, indent=2)

    print()
    print(f"Saved {len(routes)} routes")
    print(output_file)


if __name__ == "__main__":
    main()
