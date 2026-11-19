#!/usr/bin/env python3
"""Targeted public retrieval of two unavailable Medellín bus operating resolutions.

Runs on GitHub Actions to distinguish failed HTTP access from missing records.
No invented PDF URLs and no modification of any GTFS or timetable register.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlencode, urljoin, urlparse

import requests

OUT = Path("artifacts/medellin-p4-official-acts")
HIST = "https://www.medellin.gov.co/statements/innovaciondigital/gacetas/historico-mercurio"
SIMM = "https://www.medellin.gov.co/SIMM/component/jdownloads/"
ASTREA = "https://www.medellin.gov.co/normograma/docs/astrea/docs/"
TARGETS = [
    {"number":"202350086596","year":2023,"route":"105_106","short":"86596"},
    {"number":"202150041167","year":2021,"route":"105_106","short":"41167"},
    {"number":"175","year":2017,"route":"246C_246D","short":"175"},
]
MAX_PDF_BYTES = 18 * 1024 * 1024
TIMEOUT = (12, 27)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.9,*/*;q=0.5",
    "Accept-Language": "es-CO,es;q=0.9,en;q=0.5",
}

class LinkCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.href = None
        self.label = ""
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.href = dict(attrs).get("href")
            self.label = ""
    def handle_data(self, data):
        if self.href is not None:
            self.label += data
    def handle_endtag(self, tag):
        if tag == "a" and self.href:
            self.links.append((self.href, self.label.strip()))
            self.href = None

def origin_ok(url: str) -> bool:
    p = urlparse(url)
    return p.scheme == "https" and p.hostname in ("medellin.gov.co", "www.medellin.gov.co")

def request(session, url, params=None):
    start = time.monotonic()
    try:
        response = session.get(url, params=params, timeout=TIMEOUT, allow_redirects=True,
                               stream=True)
        size = 0
        pieces = []
        for part in response.iter_content(chunk_size=64*1024):
            size += len(part)
            if size > MAX_PDF_BYTES:
                raise ValueError("size_limit")
            pieces.append(part)
        payload = b"".join(pieces)
        report = dict(requested_url=response.request.url, final_url=response.url,
                      http_status=response.status_code,
                      content_type=response.headers.get("Content-Type",""),
                      byte_count=len(payload), elapsed_seconds=round(time.monotonic()-start,2),
                      sha256=hashlib.sha256(payload).hexdigest())
        return report, payload
    except (requests.RequestException, ValueError) as exc:
        return dict(url=url, error=type(exc).__name__+": "+str(exc)[:300],
                    elapsed_seconds=round(time.monotonic()-start,2)), b""

def scan_links(base, content):
    parser = LinkCollector()
    parser.feed(content.decode("utf-8",errors="replace")[:3_000_000])
    return [{"url":urljoin(base, h), "label":label[:130]} for h,label in parser.links
            if origin_ok(urljoin(base, h))]

def candidate_links(links, number):
    last = number[-6:]
    return [link for link in links if number in (link["url"]+" "+link["label"])
            or (len(number)>6 and last in (link["url"]+" "+link["label"]))][:15]

def pdf_save(report, payload, filename):
    if payload[:5] != b"%PDF-":
        return False
    path = OUT / filename
    path.write_bytes(payload)
    report["verified_pdf"] = str(path)
    return True

def run(targets, archive_pages):
    OUT.mkdir(parents=True, exist_ok=True)
    sess = requests.Session()
    sess.headers.update(HEADERS)
    report = dict(run_purpose="bounded official Medellin P4 origin PDF recovery",
                  targets=targets, diagnostic=[], verified_pdfs=[],
                  source_rules="Resolution baseline; current operator site precedence; no Moovit; no GTFS writes")
    for t in targets:
        number = t["number"]
        entry = dict(number=number,route=t["route"],probes=[])
        # Original municipal public Gaceta number search (reuses established workflow).
        hist_report, hist_content = request(sess, HIST, {"numero_acto":number})
        hist_report["probe"]="municipal_historico_mercurio"
        if hist_content and "html" in hist_report.get("content_type","").lower():
            links=scan_links(hist_report.get("final_url",HIST),hist_content)
            hist_report["matched_links"]=candidate_links(links, number)
            text=hist_content.decode("utf-8",errors="replace")
            hist_report["number_in_body"]=number in text
            hist_report["document_identifiers"]=list(dict.fromkeys(
                re.findall(r'historico-mercurio/(?:visualizar|descargar)/(\\d+)',text,re.I)))[:15]
        entry["probes"].append(hist_report)
        # Test only the two established ASTREA source patterns; never equate HTTP 200 to an act match.
        for name in [f'r_smmed_{t["short"]}_{t["year"]}.htm',
                     f'R_SMMED_{t["short"]}_{t["year"]}.htm']:
            url=ASTREA+name
            item,body=request(sess,url)
            item["probe"]="astrea_specific_pattern"
            if body:
                text=body.decode("utf-8",errors="replace")
                item["number_in_body"]=number in text
                item["has_resolution_heading"]=bool(re.search(r"resoluci[oó]n",text,re.I))
                if item["number_in_body"] and item["has_resolution_heading"]:
                    file=OUT/(number+"_"+name+".html")
                    file.write_bytes(body)
                    item["stored_candidate_html"]=str(file)
            entry["probes"].append(item)
        report["diagnostic"].append(entry)

    # jDownloads is paginated. Do not silently imply 276 files have been checked.
    visited=set()
    initial=[SIMM, urljoin(SIMM,"category/42-resoluciones-transporte?Itemid=0")]
    pages=[(url,0) for url in initial]
    for url,depth in pages:
        if url in visited or len(visited)>=archive_pages:
            continue
        visited.add(url)
        item,body=request(sess,url)
        item["probe"]="SIMM_jdownloads_page"
        if body and "html" in item.get("content_type","").lower():
            links=scan_links(item.get("final_url",url),body)
            item["matched_target_links"]={t["number"]:candidate_links(links,t["number"]) for t in targets}
            item["link_count"]=len(links)
            if depth<2:
                for link in links:
                    u=link["url"]
                    if ("jdownloads" in u and ("resoluciones-transporte" in u or
                        "start=" in u or "limitstart=" in u or "category/42" in u)
                        and u not in visited and all(x[0]!=u for x in pages)):
                        pages.append((u,depth+1))
                        if len(pages)>=archive_pages*3:break
            # Download exact-number linked PDFs only, no guessing file IDs.
            matches=[(t,link) for t in targets for link in candidate_links(links,t["number"])]
            for t,link in matches[:6]:
                urlpdf=link["url"]
                if not origin_ok(urlpdf):continue
                p,payload=request(sess,urlpdf)
                p["probe"]="SIMM_exact_number_candidate"
                p["number"]=t["number"]
                if pdf_save(p,payload,t["number"]+"_SIMM_candidate.pdf"):
                    report["verified_pdfs"].append(p)
                else:
                    item.setdefault("non_pdf_number_links",[]).append(p)
        report["diagnostic"].append(item)
    summary=[]
    summary.append("# Medellin official P4 resolution availability from GitHub-hosted runner")
    summary.append("")
    summary.append("Tests are observational. HTTP 403/404/timeout/HTML are **not** evidence that a resolution is invalid.")
    summary.append("Only documents with actual PDF magic are treated as PDFs; any named HTML is a **candidate**, not a validated legal match.")
    summary.append("")
    summary.append("| Number | Historico | ASTREA checks |")
    summary.append("|---|---|---|")
    for e in report["diagnostic"][:len(targets)]:
        probes=e["probes"]
        hh=probes[0]
        aa=probes[1:]
        status=lambda x:str(x.get("http_status",x.get("error","unknown"))).replace("|","/")
        summary.append(f'| {e["number"]} | {status(hh)} | '+", ".join(status(a) for a in aa)+" |")
    summary += ["",f'SIMM pages probed: **{len(visited)}/{archive_pages} maximum**, not the complete 276-file archive.',
                f'Confirmed downloaded PDFs: **{len(report["verified_pdfs"])}**.',
                "", "Review diagnostics.json and recovered HTML/PDF artifacts before changing any timetable."]
    (OUT/"diagnostics.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (OUT/"README.md").write_text("\n".join(summary)+"\n",encoding="utf-8")
    print("\n".join(summary))
    return 0

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--archive-pages",type=int,default=8)
    args=parser.parse_args()
    raise SystemExit(run(TARGETS,max(1,min(args.archive_pages,12))))
