#!/usr/bin/env python3
"""Index pages containing technical fichas in already recovered official Medellín PDFs.

Research-only inventory: never interprets OCR numbers as verified service frequencies.
"""
from __future__ import annotations

import csv
from pathlib import Path
import re
import subprocess

ROOT = Path("artifacts/resolutions")
FILES = {
    "res_1166_2015.pdf": ("1166", "Transporte Medellín Castilla", "2A"),
    "res_1169_2015.pdf": ("1169", "Palenque Robledal", "2A"),
}
FIELDS = ("document", "resolution", "operator_context", "system", "pdf_page",
          "printed_page_candidates", "route_code_candidates", "has_dispatch_interval",
          "has_service_window", "page_text_excerpt", "qa_status")


def tidy(text: str) -> str:
    return " ".join(text.split())


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    records = []
    for name, (resolution, operator, system) in FILES.items():
        pdf = ROOT / name
        if not pdf.exists():
            raise SystemExit(f"Required official PDF missing: {pdf}")
        # Preserves \f page separators, so PDF page numbers are reproducible.
        result = subprocess.run(["pdftotext", "-layout", str(pdf), "-"],
                                check=True, capture_output=True, text=True)
        pages = result.stdout.split("\f")
        if pages and not pages[-1].strip():
            pages.pop()
        for page_no, page in enumerate(pages, 1):
            upper = page.upper()
            has_intervals = "INTERVALO DE DESPACHO" in upper
            has_window = "HORARIO DE SERVICIO" in upper
            if not (has_intervals or has_window):
                continue
            # Codes in source headings; candidates only, not definitive route matching.
            codes = re.findall(r"(?im)^\s*(?:C[ÓO]DIGO(?: DE RUTA)?|RUTA)\s*[:\-]?\s*([A-Z0-9][A-Z0-9/ .\-]{0,45})", page)
            printed = re.findall(r"(?im)^\s*(?:P[ÁA]GINA\s+)?(\d{1,4})\s*$", page)
            records.append(dict(
                document=name, resolution=resolution, operator_context=operator,
                system=system, pdf_page=page_no,
                printed_page_candidates=";".join(printed[:5]),
                route_code_candidates=";".join(tidy(c) for c in codes[:8]),
                has_dispatch_interval="yes" if has_intervals else "no",
                has_service_window="yes" if has_window else "no",
                page_text_excerpt=tidy(page)[:450],
                qa_status="pdf_text_candidate_visual_QA_required",
            ))
            # Keep the full page transcript as temporary QA material, not as source registry.
            target = ROOT / f"candidate_{resolution}_pdfpage_{page_no:03d}.txt"
            target.write_text(page, encoding="utf-8")
    output = ROOT / "historical_1166_1169_fiche_page_candidates.csv"
    with output.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)
    print(f"Wrote {len(records)} candidate pages across resolutions 1166 and 1169: {output}")
    for r in records:
        print(f"{r['resolution']} pdf-page {r['pdf_page']}: "
              f"interval={r['has_dispatch_interval']} window={r['has_service_window']} "
              f"codes={r['route_code_candidates'][:65]}")


if __name__ == "__main__":
    main()
