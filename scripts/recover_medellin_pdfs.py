#!/usr/bin/env python3
"""Fetch official Medellín gazette PDFs without silently treating HTML errors as PDFs.

Research utility only: no writes to GTFS data, no inference of current validity.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import urlparse

APPROVED_HOSTS = {"www.medellin.gov.co", "medellin.gov.co"}
SAFE_FILE = re.compile(r"^[a-zA-Z0-9_.-]+\.pdf$")


def download(entry: dict, output: Path) -> dict:
    name = entry["filename"]
    url = entry["url"]
    if not SAFE_FILE.fullmatch(name):
        raise ValueError(f"Unsafe filename: {name!r}")
    if urlparse(url).scheme != "https" or urlparse(url).hostname not in APPROVED_HOSTS:
        raise ValueError(f"Not an approved government URL: {url!r}")

    destination = output / name
    partial = output / (name + ".partial")
    result = {"id": entry["id"], "file": name, "url": url, "status": "failed"}
    cmd = [
        "curl", "--location", "--fail", "--show-error", "--silent",
        "--connect-timeout", "15", "--max-time", "110",
        "--retry", "1", "--retry-delay", "5", "--retry-all-errors",
        "--max-redirs", "5", "--user-agent",
        "Mozilla/5.0 (compatible; ColombiaTransit-official-doc-research/1.0)",
        "--header", "Accept: application/pdf,application/octet-stream;q=0.9,*/*;q=0.5",
        "--output", str(partial), url
    ]
    try:
        completed = subprocess.run(cmd, capture_output=True, text=True, timeout=250)
        if completed.returncode:
            result["error"] = completed.stderr.strip()[-700:] or f"curl exit {completed.returncode}"
            return result
        if not partial.is_file() or partial.stat().st_size < 1024:
            result["error"] = "Download is empty or too small"
            return result
        with partial.open("rb") as fh:
            header = fh.read(32)
        if b"%PDF-" not in header[:16]:
            result["error"] = "Returned content is not a PDF (possible error/HTML page)"
            return result

        partial.replace(destination)
        digest = hashlib.sha256()
        with destination.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                digest.update(chunk)
        result.update(status="downloaded", bytes=destination.stat().st_size,
                      sha256=digest.hexdigest())

        if shutil.which("pdftotext"):
            text_file = destination.with_suffix(".txt")
            try:
                text_run = subprocess.run(
                    ["pdftotext", "-layout", str(destination), str(text_file)],
                    capture_output=True, text=True, timeout=90
                )
                if text_run.returncode == 0 and text_file.exists():
                    result["text_file"] = text_file.name
                else:
                    result["text_error"] = text_run.stderr.strip()[-300:]
            except subprocess.TimeoutExpired:
                result["text_error"] = "pdftotext timed out"
        return result
    except subprocess.TimeoutExpired:
        result["error"] = "Download exceeded total timeout"
        return result
    except Exception as exc:
        result["error"] = str(exc)
        return result
    finally:
        partial.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, default=Path("data/resolutions/official_pdf_sources.json"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/resolutions"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    data = json.loads(args.catalog.read_text(encoding="utf-8"))
    sources = data["sources"]
    if not sources:
        print("No official sources in catalog.", file=sys.stderr)
        return 2

    results = []
    with ThreadPoolExecutor(max_workers=min(4, len(sources))) as pool:
        pending = {pool.submit(download, s, args.output): s for s in sources}
        for future in as_completed(pending):
            try:
                item = future.result()
            except Exception as exc:
                source = pending[future]
                item = {"id": source.get("id"), "file": source.get("filename"),
                        "status": "failed", "error": str(exc)}
            results.append(item)
            print(f"{item['id']}: {item['status']} - "
                  f"{item.get('bytes', item.get('error', ''))}", flush=True)

    results.sort(key=lambda r: r["id"])
    report = {"source": "Alcaldía de Medellín official PDFs",
              "note": "Downloaded documents are not verified as latest legally effective route schedules.",
              "results": results}
    (args.output / "download_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    got = sum(r["status"] == "downloaded" for r in results)
    lines = ["## Medellín official resolution PDF recovery", "",
             f"- Successfully downloaded: **{got}/{len(results)}**", "",
             "| Source | Result | Detail |",
             "|---|---|---|"]
    for r in results:
        detail = (str(r.get("bytes", 0)) + " bytes, SHA256 " + r.get("sha256", "")[:12]
                  if r["status"] == "downloaded" else r.get("error", "No details"))
        detail = detail.replace("|", "/").replace("\n", " ")
        lines.append(f"| {r['id']} | {r['status']} | {detail} |")
    lines += ["", "The files in this artifact are research sources. Do not publish OCR as "
              "verified GTFS timetable data without visual and legal checks."]
    summary = "\n".join(lines) + "\n"
    (args.output / "README.md").write_text(summary, encoding="utf-8")
    print(summary)
    return 0 if got else 1


if __name__ == "__main__":
    raise SystemExit(main())
