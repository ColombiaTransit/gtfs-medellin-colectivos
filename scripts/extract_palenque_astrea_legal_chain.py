#!/usr/bin/env python3
"""Fetch and extract publicly available ASTREA act text for Palenque 250AP/250AiP.

Does not download or preserve PDFs. Original public HTML is used only transiently.
Output in Actions artifacts expires after seven days. No GTFS changes.
"""
from __future__ import annotations
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse
import hashlib
import json
import re
import subprocess
import sys

BASE = "https://www.medellin.gov.co/normograma/docs/astrea/docs/"
ACTS = [
    ("2017_predecessor", "r_smmed_21300_2017.htm"),
    ("2022_amendment", "R_SMMED_15351_2022.htm"),
    ("2025_repeal", "r_smmed_88689_2025.htm"),
    ("2026_route229i", "R_SMMED_39611_2026.htm"),
]
TERMS = ("250AP", "250AIP", "250AiP", "PAJARITO", "PALENQUE",
         "FRECUENCIA", "HORARIO", "INTERVALO", "DESPACHO", "DEROGA",
         "DEROGAR", "ARTÍCULO 1", "ARTICULO 1", "VIGENCIA",
         "CAPACIDAD TRANSPORTADORA", "201750021300", "202250015351")

def fetch(url):
    host = urlparse(url).hostname
    if host != "www.medellin.gov.co":
        raise ValueError("Refusing nonofficial domain")
    tmp = Path("/tmp/palenque_astrea_act.html")
    cmd = [
        "curl", "--silent", "--show-error", "--location", "--max-redirs", "3",
        "--connect-timeout", "15", "--max-time", "65",
        "--max-filesize", "3500000", "--user-agent",
        "Mozilla/5.0 (compatible; ColombiaTransit-public-legal-audit/1.0)",
        "--header", "Accept: text/html,*/*;q=0.5",
        "--write-out", "%{http_code}\t%{url_effective}",
        "--output", str(tmp), url
    ]
    c = subprocess.run(cmd, capture_output=True, text=True, timeout=70)
    out = c.stdout.strip().split("\t")
    result = {"url": url, "http": int(out[0]) if out and out[0].isdigit() else None,
              "final_url": out[1] if len(out)>1 else "", "curl_exit": c.returncode}
    try:
        if tmp.exists() and c.returncode == 0:
            data = tmp.read_bytes()
            result["bytes"] = len(data)
            result["sha256_html"] = hashlib.sha256(data).hexdigest()
            if result["http"] == 200 and b"<html" in data[:10000].lower():
                result["html"] = data.decode("utf-8", "replace")
                result["is_html"] = True
            else:
                result["error"] = "Not a successful HTML response"
        elif c.returncode:
            result["error"] = c.stderr.strip()[-400:]
    finally:
        tmp.unlink(missing_ok=True)
    return result

def text_of(node):
    for k in node.select("script,style,noscript,svg"):
        k.decompose()
    return "\n".join(x.strip() for x in node.stripped_strings if x.strip())

def extract(item, label):
    html = item.pop("html", None)
    if not html:
        return item
    soup = BeautifulSoup(html, "html.parser")
    item["title"] = soup.title.get_text(" ", strip=True) if soup.title else ""
    for meta in soup.select("meta[name='description']"):
        item["description"] = meta.get("content", "")
    # The document pane contains the legal act and ASTREA's annotations.
    div = soup.select_one(".panel-documento") or soup.select_one(".panel-fondo-documento")
    if div is None:
        item["error"] = "ASTREA legal document pane not found"
        return item
    raw = text_of(div)
    clean = re.sub(r"\n{3,}", "\n\n", raw)
    item["legal_body_chars"] = len(clean)
    item["legal_body_excerpt"] = clean[:32000]
    item["legal_body_truncated"] = len(clean) > 32000
    item["term_hits"] = {}
    for term in TERMS:
        found = []
        for m in list(re.finditer(re.escape(term), clean, re.IGNORECASE))[:14]:
            found.append(re.sub(r"\s+", " ", clean[max(0, m.start()-145):m.end()+340])[:520])
        if found:
            item["term_hits"][term] = found
    item["related_astrea_acts"] = [
        urljoin(item["url"], a.get("href"))
        for a in div.select("a[href]")
        if re.search(r"(r_smmed_|r_smm ed_)", a.get("href", ""), re.I)
    ][:70]
    item["heading_top"] = clean[:1400]
    return item

def main():
    out = Path("artifacts/medellin-palenque-legal-chain")
    out.mkdir(parents=True, exist_ok=True)
    documents = {}
    for label, path in ACTS:
        result = extract(fetch(BASE+path), label)
        documents[label] = result
        print(f"{label}: http={result['http']} textchars={result.get('legal_body_chars',0)} "
              f"termhits={len(result.get('term_hits', {}))}", flush=True)
    status = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": ["250AP", "250AiP"],
        "sources": documents,
        "research_safety": {
            "official_html_only": True, "pdf_stored": False,
            "request_submitted": False, "updated_GTFS": False,
            "effective_headways_still_need_individual_validation": True
        }
    }
    (out/"palenque_legal_chain_extraction.json").write_text(
        json.dumps(status, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    lines=["## Official ASTREA legal-act source review", "",
           "| Act | HTTP | Legal text length |", "|---|---|---:|"]
    for label,x in documents.items():
        lines.append(f"| {label} | {x['http']} | {x.get('legal_body_chars', 0)} |")
    lines += ["", "Research-only original HTML transcription. PDF documents never stored.",
              "Review every field and legal supersession before applying new GTFS data."]
    (out/"README.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    print("\n".join(lines))

if __name__ == "__main__":
    sys.exit(main())
