#!/usr/bin/env python3
"""Probe only publicly available, municipal sources for 2025 gazette PDFs.

Research-only: network metadata/link discovery and optional PDFs are transient
GitHub Actions artifacts (7 days), never committed to git.
"""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
import hashlib
import json
import re
import subprocess

ROOT = "https://www.medellin.gov.co"
HOSTS = {"www.medellin.gov.co", "medellin.gov.co", "mercurio.medellin.gov.co"}
URLS = [
    ROOT + "/statements/innovaciondigital/gacetas/historico-mercurio",
    ROOT + "/mercurio/indices/Gacetas.jsp",
    "https://mercurio.medellin.gov.co/mercurio/indices/Gacetas.jsp",
    ROOT + "/mercurio/IndiceServlet",
    "https://mercurio.medellin.gov.co/mercurio/IndiceServlet",
    ROOT + "/statements/innovaciondigital/gacetas/consulta-publica/5671",
    ROOT + "/statements/innovaciondigital/gacetas/consulta-publica/5667",
    ROOT + "/es/wp-content/uploads/2025/09/Gaceta-Oficial-5671.pdf",
    ROOT + "/es/wp-content/uploads/2025/09/Gaceta-Oficial-5667.pdf",
    ROOT + "/es/wp-content/uploads/2025/09/Gaceta-5671.pdf",
    ROOT + "/es/wp-content/uploads/2025/09/Gaceta-5667.pdf",
    ROOT + "/irj/go/km/docs/pccdesign/SubportaldelCiudadano_2/PlandeDesarrollo_0_15/Publicaciones/Shared%20Content/GACETA%20OFICIAL/2025/Gaceta%205671/5671.pdf",
    ROOT + "/irj/go/km/docs/pccdesign/SubportaldelCiudadano_2/PlandeDesarrollo_0_15/Publicaciones/Shared%20Content/GACETA%20OFICIAL/2025/Gaceta%205667/5667.pdf",
]
class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.forms = []
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag in {"a", "script", "link", "iframe", "form"}:
            a = d.get("href") or d.get("src") or d.get("action")
            if a:
                self.links.append(a)

def fetch(i, url, dest):
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in HOSTS:
        raise ValueError("Nonmunicipal source")
    target = dest / f"probe_{i:02}.download"
    hdr = dest / f"probe_{i:02}.headers"
    cmd = ["curl", "--location", "--show-error", "--silent", "--max-redirs", "4",
           "--connect-timeout", "12", "--max-time", "50", "--retry", "0",
           "--max-filesize", "60000000",
           "--user-agent", "Mozilla/5.0 (compatible; ColombiaTransit-open-legal-research/1.0)",
           "--header", "Accept: text/html,application/pdf;q=0.9,*/*;q=0.5",
           "--dump-header", str(hdr), "--output", str(target),
           "--write-out", "%{http_code}\t%{url_effective}\t%{content_type}", url]
    result = {"source_url": url, "probe": i, "verified_official_hostname": True}
    try:
        c = subprocess.run(cmd, capture_output=True, text=True, timeout=62)
        p = c.stdout.strip().split("\t")
        result.update(status=int(p[0]) if p and p[0].isdecimal() else None,
                      final_url=p[1] if len(p)>1 else None,
                      content_type=p[2] if len(p)>2 else None,
                      curl_exit=c.returncode)
        if c.returncode: result["error"]=c.stderr.strip()[-200:]
        if target.exists():
            content = target.read_bytes()
            result["bytes"]=len(content)
            if content[:16].find(b"%PDF-")>=0 and len(content)>1024 and result["status"]==200:
                pdf=dest/f"official_candidate_{i:02}.pdf"
                target.rename(pdf)
                result.update(pdf_file=pdf.name,sha256=hashlib.sha256(content).hexdigest(),
                              result_type="pdf")
            elif b"<html" in content[:4000].lower() or b"<!doctype" in content[:4000].lower():
                parser=LinkParser()
                text=content[:500000].decode("utf-8","replace")
                parser.feed(text)
                links=[urljoin(result.get("final_url") or url, l) for l in parser.links]
                result["page_title"]=re.search(r"<title[^>]*>(.*?)</title>",text,re.S|re.I).group(1).strip()[:170] if re.search(r"<title[^>]*>(.*?)</title>",text,re.S|re.I) else ""
                result["relevant_links"]=[u for u in links if urlparse(u).hostname in HOSTS and any(t in u.lower() for t in ["gaceta","mercurio","indice","descarga","pdf","historico"])][:25]
                result["all_js_links"]=[u for u in links if u.lower().endswith(".js")][:12]
                for hit in ["5671","5667","Gacetas.jsp","IndiceServlet","download","pdf"]:
                    result[f"mentions_{hit}"]=text.lower().count(hit.lower())
                result["snippet"]=re.sub(r"\s+"," ",re.sub(r"<[^>]*>"," ",text[:5000]))[:900]
                result["result_type"]="html"
                target.unlink(missing_ok=True)
            else:
                result["result_type"]="other"
                result["start_bytes"]=content[:80].decode("utf-8","replace")
                target.unlink(missing_ok=True)
    except Exception as exc:
        result["error"]=str(exc)[:300]
    finally:
        hdr.unlink(missing_ok=True)
        target.unlink(missing_ok=True)
    return result

def main():
    out=Path("artifacts/medellin-2025-probe")
    out.mkdir(parents=True,exist_ok=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures={pool.submit(fetch,i,url,out):i for i,url in enumerate(URLS)}
        results=[]
        for task in as_completed(futures):
            r=task.result()
            results.append(r)
            print(f"{r['probe']:02d}: HTTP={r.get('status')} {r.get('result_type','error')} "
                  f"{r.get('bytes',0)} bytes {r['source_url']}",flush=True)
    results.sort(key=lambda r:r["probe"])
    report={"created_at_utc":datetime.now(timezone.utc).isoformat(),
            "purpose":"public official municipal archive discovery, no legal validation",
            "results":results}
    (out/"probe_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines=["# Medellín 2025 official archive URL probes","","| HTTP | Type | URL |",
           "|---|---|---|"]
    for r in results:
        lines.append(f"| {r.get('status','?')} | {r.get('result_type','failed')} | {r['source_url']} |")
    lines += ["",f"PDFs recovered: {sum(r.get('result_type')=='pdf' for r in results)}/{len(results)}",
              "All files are ephemeral research artifacts, not authoritative current timetables."]
    (out/"README.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print("\n".join(lines))
if __name__=="__main__": main()
