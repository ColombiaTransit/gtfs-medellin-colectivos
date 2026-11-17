#!/usr/bin/env python3
"""Index late-2026 Medellín Gaceta acts without downloading or storing PDFs.

Research index only: titles can identify possibly relevant legal changes,
but a title never proves which routes, headways or operating times changed.
"""
from __future__ import annotations
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse
import csv
import json
import re
import sys
import time
import unicodedata

import requests
from bs4 import BeautifulSoup

BASE = "https://www.medellin.gov.co/statements/innovaciondigital/gacetas/consulta-publica"
HOST = "www.medellin.gov.co"
MAX_LIST_PAGES = 20
MAX_GACETAS = 140
USER_AGENT = "Mozilla/5.0 (compatible; ColombiaTransit-public-legal-index/1.0)"
HEADINGS = [
    "gaceta", "gaceta_date", "act_number", "act_type", "act_description",
    "act_date", "issuing_department", "official_gaceta_detail_url",
    "classification", "evidence_status"
]
HIGH = (
    "transporte publico colectivo", "transporte terrestre automotor colectivo",
    "transporte publico automotor", "rutas de transporte publico", "cootran",
    "metrosan", "coinvetrans", "invetrans", "copatra", "coonatra",
    "flota la v", "tax maya", "taxmaya", "conducciones america",
    "transacoop", "santra", "rapido san cristobal",
    "transportes medellin castilla", "paleneque robledal",
    "sitransco", "sistema de rutas", "rutas 2a", "rutas 6f",
)
TRANSPORT = ("transporte", "movilidad", "ruta", "integrado", "operacion")
PUBLIC = ("colectiv", "bus", "transportador", "sistema de rutas")


def clean(value):
    return re.sub(r"\s+", " ", value or "").strip()


def normalize(value):
    value = unicodedata.normalize("NFD", clean(value).lower())
    return "".join(c for c in value if unicodedata.category(c) != "Mn")


def classify(value):
    text = normalize(value)
    if any(term in text for term in HIGH):
        return "transport_route_act_candidate"
    if any(t in text for t in TRANSPORT) and any(t in text for t in PUBLIC):
        return "transport_possible_relevance"
    return None


def request(session, url):
    if urlparse(url).hostname != HOST:
        raise ValueError("Refusing nonmunicipal URL: " + url)
    response = session.get(url, timeout=(12, 30))
    response.raise_for_status()
    return response.text


def discover(session):
    found = {}
    page_logs = []
    for page_no in range(1, MAX_LIST_PAGES + 1):
        address = BASE + "?page=" + str(page_no)
        html = request(session, address)
        soup = BeautifulSoup(html, "html.parser")
        ids = sorted(set(re.findall(r"/consulta-publica/(\d{4,5})(?!\d)", html)), reverse=True)
        page_logs.append({"page": page_no, "ids": ids})
        fresh = 0
        for gaceta_id in ids:
            if gaceta_id not in found:
                found[gaceta_id] = BASE + "/" + gaceta_id
                fresh += 1
        print(f"Index page {page_no}: {len(ids)} IDs, {fresh} new", flush=True)
        if not ids or not fresh or len(found) >= MAX_GACETAS:
            break
        time.sleep(0.25)
    return found, page_logs


def get_acts(session, number, url):
    html = request(session, url)
    soup = BeautifulSoup(html, "html.parser")
    fulltext = clean(soup.get_text(" ", strip=True))
    date_match = re.search(r"Fecha de Publicaci[oó]n:\s*(\d{2}/\d{2}/\d{4})", fulltext, flags=re.I)
    pub_date = date_match.group(1) if date_match else ""
    acts = []
    for tr in soup.select("table tr"):
        td = [clean(x.get_text(" ", strip=True)) for x in tr.find_all("td")]
        if len(td) < 5:
            continue
        act, kind, description, act_date, department = td[:5]
        category = classify(description)
        if category:
            acts.append({
                "gaceta": number, "gaceta_date": pub_date,
                "act_number": act, "act_type": kind,
                "act_description": description, "act_date": act_date,
                "issuing_department": department,
                "official_gaceta_detail_url": url,
                "classification": category,
                "evidence_status": "official_2026_public_index_only_original_act_not_checked"
            })
    return acts, {"number": number, "date": pub_date,
                  "act_count": len(soup.select("table tr")), "matching_acts": len(acts)}


def main():
    out = Path("artifacts/medellin-gaceta-2026")
    out.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept": "text/html,*/*;q=0.8"})
    try:
        docs, pages = discover(session)
    except Exception as exc:
        (out / "scan_error.txt").write_text(str(exc) + "\n", encoding="utf-8")
        raise
    if not docs:
        raise RuntimeError("Official archive returned no Gaceta detail IDs; do not claim coverage")

    allrows = []
    checked = []
    errors = []
    for i, (number, url) in enumerate(sorted(docs.items(), reverse=True), 1):
        try:
            rows, meta = get_acts(session, number, url)
            allrows.extend(rows)
            checked.append(meta)
        except Exception as exc:
            errors.append({"gaceta": number, "detail_url": url, "error": str(exc)})
        if i % 15 == 0:
            print(f"Reviewed {i}/{len(docs)} official detail pages; matches: {len(allrows)}", flush=True)
        time.sleep(0.15)
    if not checked:
        raise RuntimeError("No official details could be read")
    with (out / "late_2026_transport_act_candidates.csv").open("w", newline="", encoding="utf-8") as fd:
        writer = csv.DictWriter(fd, fieldnames=HEADINGS)
        writer.writeheader()
        writer.writerows(allrows)
    report = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "source": BASE, "max_gacetas": MAX_GACETAS,
        "listing_pages": pages, "details_checked": checked,
        "errors": errors, "counts": {
            "details_found": len(docs), "details_read": len(checked),
            "details_failed": len(errors), "matching_acts": len(allrows),
            "classifications": dict(Counter(r["classification"] for r in allrows))
        },
        "warning": "No evidence of absence when detail downloads fail; act titles alone do not prove route-level changes"
    }
    (out / "scan_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    summary = [
        "## Public Gaceta index scan, 2026",
        f"- Gacetas discovered: **{len(docs)}**",
        f"- Gacetas read: **{len(checked)}**",
        f"- Failed details: **{len(errors)}**",
        f"- Transport act candidates: **{len(allrows)}**",
        "This index holds municipal act titles only, not reviewed resolution text or current GTFS headways."
    ]
    (out / "README.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print("\n".join(summary))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
