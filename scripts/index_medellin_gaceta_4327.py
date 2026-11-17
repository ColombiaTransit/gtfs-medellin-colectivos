#!/usr/bin/env python3
"""Produce UNVERIFIED text candidates from a temporary official Gaceta 4327 PDF.

Requires: pip install pymupdf
Run: python scripts/index_medellin_gaceta_4327.py /path/to/gaceta_4327.pdf /path/to/output.csv

Never use these candidates as GTFS timings without page-image verification.
"""
import csv
import re
import sys
from pathlib import Path
from collections import Counter

import fitz

SECTIONS = [
    (1, 89, "1167", "2A"),
    (90, 177, "1168", "2A"),
    (178, 265, "1169", "2A"),
    (266, 355, "1170", "2A"),
    (356, 359, "1045", "6A"),
    (360, 391, "1046", "6A"),
    (392, 424, "1047", "6A"),
    (425, 458, "1048", "6A"),
    (459, 490, "1049", "6A"),
    (491, 524, "1151", "6A"),
    (525, 527, "1018", "6D"),
    (528, 542, "1019", "6D"),
    (543, 556, "1020", "6D"),
]
OFFICIAL_URL = (
    "https://www.medellin.gov.co/irj/go/km/docs/pccdesign/"
    "SubportaldelCiudadano_2/PlandeDesarrollo_0_15/Publicaciones/"
    "Shared%20Content/GACETA%20OFICIAL/2015/Gaceta%204327/4327.pdf"
)


def clean(s):
    return re.sub(r"\s+", " ", s).strip()


def fiche_heading(text):
    intro = text[:max(200, text.upper().find("FICHA"))]
    match = re.search(r"(?im)^\s*(5\.\d+\.\d+)\.\s*RECORRIDO\s+([^\n]{3,150})", intro)
    if match:
        return match.group(1), clean(match.group(2))
    match = re.search(r"(?im)FICHA\s*T[ÉE]CNICA\s+RECORRIDO\s*([^\n]{3,110})", text)
    if match:
        return "", clean(match.group(1))
    return "", clean(intro[-90:])


def candidate_interval_words(page):
    words = page.get_text("words")
    titles = [w for w in words if "INTERVALO" in w[4].upper()]
    if not titles:
        return "", 0
    y = titles[0][1]
    nums = [
        w for w in words
        if y + 19 <= w[1] <= y + 47 and re.fullmatch(r"\d{1,3}", w[4])
    ]
    raw = " ".join(w[4] for w in sorted(nums, key=lambda w: (round(w[1] / 5), w[0])))
    return raw, len(nums)


def extract(pdf, out):
    with fitz.open(pdf) as document:
        if len(document) != 556:
            raise ValueError(f"Expected the complete 556-page Gaceta 4327, got {len(document)}")
        rows = []
        for first, last, act, system in SECTIONS:
            for idx in range(first - 1, last):
                page = document[idx]
                text = page.get_text(sort=True)
                upper = text.upper()
                if "INTERVALO DE DESPACHO" not in upper and "FICHA TÉCNICA" not in upper:
                    continue
                if "HORARIO DE SERVICIO" not in upper and "INTERVALO DE DESPACHO" not in upper:
                    continue
                section, route = fiche_heading(text)
                start = upper.find("HORARIO DE SERVICIO")
                hours = clean(text[start:start + 210]) if start >= 0 else ""
                interval, count = candidate_interval_words(page)
                rows.append(dict(
                    gaceta="4327", resolution=act, year="2015", system=system,
                    printed_gaceta_page=idx + 1, pdf_page=idx + 1,
                    subsection=section, printed_route_heading_ocr=route,
                    raw_horario_text=hours, raw_interval_ocr_numbers=interval,
                    interval_ocr_number_count=count, source_url=OFFICIAL_URL,
                    qa_status="source_pdf_text_index_only_not_visual_validation",
                    current_effectivity="historical_2015_later_resolutions_not_checked",
                ))
    if not rows:
        raise RuntimeError("No technical fichas found")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Indexed {len(rows)} fiche occurrences (NOT validated GTFS data)")
    print("By act:", dict(Counter(r["resolution"] for r in rows)))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: index_medellin_gaceta_4327.py INPUT.pdf OUTPUT.csv")
    extract(Path(sys.argv[1]), Path(sys.argv[2]))
