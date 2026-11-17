#!/usr/bin/env python3
"""Targeted public ASTREA Secretaría de Movilidad 2026 index audit.

Scans only documents currently listed under 2026 in municipal ASTREA.
Keeps compact metadata and relevant title snippets; never archives source
HTML/PDF or concludes absence of unindexed legal acts.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
import csv
import json
import re
import subprocess

INDEX="https://www.medellin.gov.co/normograma/docs/astrea/nddnddptyedord_secretaria_movilidad.html"
OUTPUT=Path("artifacts/medellin-astrea-2026-audit")
class Anchors(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag=="a":
            val=dict(attrs).get("href","")
            if val:self.links.append(val)
def fetch(url):
    if urlparse(url).hostname!="www.medellin.gov.co":
        raise ValueError("non-municipal")
    p=subprocess.run(["curl","-fsSL","--connect-timeout","13",
        "--max-time","45","--max-filesize","3200000","-A",
        "Mozilla/5.0 (compatible; ColombiaTransit-2026-ASTREA-legal-audit/1.0)",
        url],capture_output=True,timeout=50)
    if p.returncode:raise RuntimeError(f"HTTP or network failure: curl {p.returncode}")
    return p.stdout.decode("utf-8","replace")
def normalize(text):
    return re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",text)).strip()
def scan(url):
    html=fetch(url)
    match=re.search(r'<div[^>]+class="[^"]*panel-documento[^"]*"[^>]*>',html,re.I)
    txt=normalize(html[match.start():]) if match else normalize(html)
    title=re.search(r"(?is)<title[^>]*>(.*?)</title>",html)
    heading=(title.group(1) if title else "").strip()
    candidates=[term for term in ["PALENQUE ROBLEDAL","CONDUCCIONES PALENQUE",
        "CUENCA 2A","250AP","250AIP","RUTA 229I"] if term.lower() in txt.lower()]
    primary=txt[:950]
    return dict(url=url,document_title=heading,starts_with=primary[:420],
        relevant_keywords=";".join(candidates),
        full_text_contains_palenque=bool(
          re.search(r"palenque.{0,10}robledal|conducciones palenque",txt,re.I)))
def main():
    OUTPUT.mkdir(parents=True,exist_ok=True)
    html=fetch(INDEX)
    parser=Anchors();parser.feed(html)
    urls=sorted(set(urljoin(INDEX,a) for a in parser.links
        if re.search(r"/(?:R|r)_SMMED_\d+_2026\.htm",a,re.I)))
    if not (15<=len(urls)<=60):
        raise RuntimeError(f"Unexpected 2026 index size {len(urls)}")
    out=[];failed=[]
    with ThreadPoolExecutor(max_workers=5) as pool:
        future={pool.submit(scan,url):url for url in urls}
        for task in as_completed(future):
            try:r=task.result();out.append(r)
            except Exception as exc:failed.append({"url":future[task],"error":str(exc)})
    out.sort(key=lambda r:r["url"])
    report={"checked_at_utc":datetime.now(timezone.utc).isoformat(),
       "index":INDEX,"published_2026_links_found":len(urls),
       "read_success":len(out),"read_failure":len(failed),
       "palenque_mentions":[r for r in out if r["full_text_contains_palenque"]],
       "relevant_matches":[r for r in out if r["relevant_keywords"]],
       "failed":failed,"disclaimer":"Indexed title and text screen only, not exhaustive legal supersession verification"}
    (OUTPUT/"audit.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    with (OUTPUT/"act_index.csv").open("w",encoding="utf-8",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=["url","document_title","relevant_keywords"])
        w.writeheader()
        for r in out:w.writerow({k:r[k] for k in w.fieldnames})
    print(f"Indexed {len(urls)} 2026 municipal ASTREA acts: "
          f"{len(out)} read, {len(failed)} failed; "
          f"{len(report['palenque_mentions'])} mention Palenque.")
    for r in report["palenque_mentions"]:
        print(f"PALENQUE CANDIDATE: {r['url']} {r['document_title']}")
    for r in report["relevant_matches"]:
        print(f"RELEVANT CANDIDATE: {r['url']} {r['relevant_keywords']}")
    if failed:
        raise RuntimeError(f"{len(failed)} 2026 act pages could not be checked")
if __name__=="__main__":main()
