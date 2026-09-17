#!/usr/bin/env python3
import requests
from pathlib import Path

URL = "https://www.sao6.com.co/rutas/"
OUTPUT_FILE = Path("sao6_rutas.html")

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/153.0 Safari/537.36"
    )
}


def main():
    print(f"Downloading: {URL}")

    response = requests.get(
        URL,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    OUTPUT_FILE.write_text(
        response.text,
        encoding="utf-8"
    )

    print(f"Saved: {OUTPUT_FILE}")
    print(f"HTTP status: {response.status_code}")
    print(f"Size: {len(response.text):,} bytes")


if __name__ == "__main__":
    main()
