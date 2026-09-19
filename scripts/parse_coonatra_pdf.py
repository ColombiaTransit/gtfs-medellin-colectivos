#!/usr/bin/env python3
"""
Extract Coonatra's real per-trip departure-time timetable from a
frequencies PDF (e.g. Frecuencias-rutas-Calasanz.pdf, linked from the
Calasanz-Boston route page) using real word POSITIONS, not text-flow
order.

WHY POSITION-BASED: a plain text extraction of this PDF (tested via
web_fetch) reflows the table into a confusing order - route headers like
"Ruta 310 Directo Calasanz Boston" appear to belong to the block of
times ABOVE them in the flattened text, not below, because the real
layout is columns of times with headers on top, and naive text
extraction reads top-to-bottom without preserving which header sits
above which column of numbers. Guessing that mapping from flattened text
risks silently attributing real departure times to the wrong route -
worse than not having the data at all. This script instead clusters
every word by its x-position (pdfplumber gives real bounding boxes) to
reconstruct actual columns, then reads each column top-to-bottom.

UNTESTED AGAINST THE REAL FILE: the environment that wrote this script
could not download coonatra.com's actual PDF bytes (only a flattened
text preview, same limitation as the text-order problem above - not
useful for testing position-based logic). This MUST be run for real
before trusting its output - it prints the full extracted structure
(every detected column, its header, and its first/last few values)
specifically so you can eyeball it against the actual PDF and confirm
or correct it, rather than silently trusting a guess.

Usage: python scripts/parse_coonatra_pdf.py <pdf_url_or_local_path>
Output: raw/coonatra_pdf_<name>.json (only written after the printed
        structure is shown - read it before using the JSON for anything)
"""

import json
import re
import sys
from pathlib import Path

import pdfplumber
import requests

TIME_RE = re.compile(r"^\d{1,2}:\d{2}$")
AMPM_RE = re.compile(r"^[ap]\.?\s*m\.?$", re.IGNORECASE)
HEADER_KEYWORDS = ("ruta", "planificación", "viajes")

# How close two words' x-positions must be (in PDF points) to be
# considered "the same column" - PDFs vary; if the printed diagnostic
# shows columns being wrongly merged or split, adjust this first.
COLUMN_X_TOLERANCE = 15


def to_24h(hh_mm: str, ampm: str) -> str:
    h, m = hh_mm.split(":")
    h = int(h)
    ampm = ampm.lower().replace(".", "").replace(" ", "")
    if ampm == "pm" and h != 12:
        h += 12
    if ampm == "am" and h == 12:
        h = 0
    return f"{h:02d}:{m}:00"


def cluster_columns(words: list) -> list:
    """words: pdfplumber word dicts (each has 'text', 'x0', 'x1', 'top').
    Returns a list of columns, each a list of words sorted top-to-bottom,
    where a column is a set of words whose x0 values cluster together."""
    sorted_words = sorted(words, key=lambda w: w["x0"])
    columns = []
    current = []
    current_x = None
    for w in sorted_words:
        if current_x is None or abs(w["x0"] - current_x) <= COLUMN_X_TOLERANCE:
            current.append(w)
            current_x = w["x0"] if current_x is None else current_x
        else:
            columns.append(current)
            current = [w]
            current_x = w["x0"]
    if current:
        columns.append(current)
    for col in columns:
        col.sort(key=lambda w: (w["top"], w["x0"]))
    return columns


def merge_time_ampm(column_words: list) -> list:
    """A time is two tokens in this PDF ('4:20' and 'a. m.' as separate
    words per the flattened-text preview, and pdfplumber splits on
    whitespace, so 'a. m.' becomes TWO further tokens: 'a.' and 'm.').
    Pairs a time token with whichever am/pm form follows it (a single
    token like 'am'/'pm', or two split tokens like 'a.'+'m.') into one
    'HH:MM:SS' entry; leaves header text alone.

    FIXED a real off-by-one here: the first version advanced the token
    index by (1 + ampm_tokens_used) where ampm_tokens_used was already
    counting the time token too, double-counting it and overshooting by
    one token every time the split ('a.', 'm.') form matched - silently
    skipping the NEXT time in the column entirely. Confirmed and fixed
    against a synthetic column with 3 real-shaped time entries; the bug
    version only recovered 2 of them.
    """
    entries = []
    i = 0
    texts = [w["text"] for w in column_words]
    n = len(texts)
    while i < n:
        t = texts[i]
        if TIME_RE.match(t) and i + 1 < n:
            single = texts[i + 1]
            if AMPM_RE.match(single):
                entries.append({"type": "time", "value": to_24h(t, single)})
                i += 2
                continue
            if i + 2 < n:
                joined = texts[i + 1] + texts[i + 2]
                if AMPM_RE.match(joined):
                    entries.append({"type": "time", "value": to_24h(t, joined)})
                    i += 3
                    continue
        entries.append({"type": "text", "value": t})
        i += 1
    return entries


def parse_pdf(path: Path) -> list:
    all_columns = []
    with pdfplumber.open(path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            words = page.extract_words()
            if not words:
                continue
            columns = cluster_columns(words)
            for col in columns:
                merged = merge_time_ampm(col)
                header_parts = [e["value"] for e in merged if e["type"] == "text"]
                times = [e["value"] for e in merged if e["type"] == "time"]
                all_columns.append({
                    "page": page_num,
                    "x0": round(col[0]["x0"], 1),
                    "header_guess": " ".join(header_parts) or None,
                    "num_times": len(times),
                    "times": times,
                })
    return all_columns


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/parse_coonatra_pdf.py <pdf_url_or_local_path>",
              file=sys.stderr)
        sys.exit(1)

    source = sys.argv[1]
    if source.startswith("http"):
        print(f"Downloading {source} ...")
        r = requests.get(source, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        pdf_path = Path("raw") / Path(source).name
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        pdf_path.write_bytes(r.content)
    else:
        pdf_path = Path(source)

    columns = parse_pdf(pdf_path)

    print(f"\n{'='*70}")
    print(f"EXTRACTED {len(columns)} COLUMN(S) - VERIFY THIS AGAINST THE REAL PDF")
    print(f"BEFORE TRUSTING ANY OF IT (see module docstring - this was built")
    print(f"without access to the real file's bytes).")
    print(f"{'='*70}\n")
    for i, col in enumerate(columns):
        print(f"Column {i} (page {col['page']}, x0={col['x0']}): "
              f"header_guess={col['header_guess']!r}, {col['num_times']} time(s)")
        if col["times"]:
            preview = col["times"][:3] + (["..."] if len(col["times"]) > 6 else []) + col["times"][-3:]
            print(f"    {preview}")
        print()

    out_path = Path("raw") / f"coonatra_pdf_{pdf_path.stem}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(columns, indent=2, ensure_ascii=False))
    print(f"Saved raw extraction -> {out_path}")
    print(
        "\nKNOWN HARD CASE - check for this specifically: a header like 'Ruta "
        "310 Directo Calasanz Boston' is one wide line of text that may span "
        "MORE horizontal space than the narrower column(s) of times sitting "
        "below it (the flattened-text preview this was built from suggests "
        "one such header sits over 3 time-columns, not 1). This simple "
        "per-word x-clustering can't resolve that by itself - it may either "
        "merge multiple real data columns into one, or split a wide header "
        "across several wrongly-separate 'columns'. If a column's "
        "header_guess is None, or a header's x0 doesn't line up with any "
        "single data column's x0, that's this case - assign that header to "
        "its columns manually by looking at the actual PDF layout, don't "
        "trust an automatic guess here."
    )
    print(
        "\nNEXT STEP: check header_guess against each column's actual header in "
        "the real PDF (open it yourself and look). If a column's header_guess "
        "is None or wrong, or a column has an unexpectedly low/high time count "
        "compared to its neighbors, COLUMN_X_TOLERANCE probably needs "
        "adjusting - columns may be getting merged or split incorrectly."
    )


if __name__ == "__main__":
    main()
