#!/usr/bin/env python3
"""Public-source search for Medellín Resolución 202250015351 / 250AP / 250AiP.

Research only. Queries official ASTREA pages and its municipal static mirror.
No PQRSD submission, no frequency synthesis, no persistent PDF storage.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
import json
import re
import subprocess

OFFICIAL = "https://www.medellin.gov.co/normograma/docs"
MIRROR = "https://normograma.com/documentospdf"
INDEX = "/astrea/nddnddptyedord_secretaria_movilidad.html"
HOSTS = {"www.medellin.gov.co", "normograma.com"}
# These are probe candidates, NOT verified source URLs.
CANDIDATE_DOCS = [
    "/astrea/docs/R_SMMED_15351_2022.htm",
    "/astrea/docs/R_SMMED_015351_2022.htm",
    "/astrea/docs/R_SMMED_202250015351_2022.htm",
    "/astrea/docs/R_SMMED_202250015351.htm",
    "/astrea/docs/R_SMMED_15351_2022.html",
]
NEEDLES = ("202250015351", "250aip", "250aip", "250ap", "2017500213",
           "conducciones palenque", "palenque robledal")

class HTMLInfo(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.script_src = []
        self.selects = []
        self.in_select = False
        self.current_select = None
        self.capture = False
        self.scripts_inline = []
        self.script_buf = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag == "script":
            if a.get("src"):
                self.script_src.append(a["src"])
            else:
                self.capture = True
                self.script_buf = []
        if tag == "select":
            self.in_select = True
            self.current_select = {
                "attrs": a, "options": [], "events": {
                    k: v[:1000] for k, v in a.items() if k.startswith("on")
                }
            }
        if tag == "option" and self.in_select:
            self.current_select["options"].append(a.get("value", ""))
    def handle_endtag(self, tag):
        if tag == "select" and self.in_select:
            self.selects.append(self.current_select)
            self.in_select = False
        if tag == "script" and self.capture:
            self.scripts_inline.append("".join(self.script_buf))
            self.capture = False
    def handle_data(self, data):
        if self.capture:
            self.script_buf.append(data)

def probe(url, number):
    if urlparse(url).hostname not in HOSTS or urlparse(url).scheme != "https":
        raise ValueError(f"Not an approved source: {url}")
    target = Path(f"/tmp/medellin_astrea_probe_{number:03d}.html")
    p = subprocess.run([
        "curl", "--location", "--silent", "--show-error",
        "--connect-timeout", "10", "--max-time", "38", "--max-redirs", "3",
        "--max-filesize", "3000000", "--user-agent",
        "Mozilla/5.0 (compatible; ColombiaTransit-open-legal-research/1.0)",
        "--header", "Accept: text/html,*/*;q=0.5", "--output", str(target),
        "--write-out", "%{http_code}\t%{content_type}\t%{url_effective}", url,
    ], capture_output=True, text=True, timeout=46)
    values = p.stdout.strip().split("\t")
    result = {"url": url, "http": int(values[0]) if values and values[0].isdigit() else None,
              "content_type": values[1] if len(values) > 1 else "",
              "final_url": values[2] if len(values) > 2 else "",
              "curl_exit": p.returncode}
    if p.returncode:
        result["error"] = p.stderr.strip()[-400:]
    if not target.exists():
        return result
    try:
        buf = target.read_bytes()
        result["bytes"] = len(buf)
        if b"%PDF-" in buf[:20]:
            result["kind"] = "pdf_unretained"
            return result
        if b"<html" not in buf[:10000].lower() and b"<!doctype" not in buf[:10000].lower():
            result["kind"] = "non_html"
            result["head"] = buf[:150].decode("utf-8", "replace")
            return result
        text = buf.decode("utf-8", "replace")
        parser = HTMLInfo()
        parser.feed(text)
        result["kind"] = "html"
        result["title"] = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S).group(1).strip()[:200] if re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S) else ""
        result["found_needles"] = {s: len(re.findall(re.escape(s), text, re.I)) for s in NEEDLES}
        result["year_2022_count"] = len(re.findall(r"\b2022\b", text))
        result["script_urls"] = [urljoin(url, s) for s in parser.script_src][:30]
        result["selects"] = parser.selects[:8]
        result["interesting_links"] = [urljoin(url, x) for x in parser.links if any(y in x.lower() for y in ("2022", "smm ed", "smm ed", "smm", "palenque"))][:60]
        # Only return a short section around the act, never full copied documents.
        result["hit_context"] = []
        for key in ("202250015351", "250AIP", "250AP"):
            m = re.search(re.escape(key), text, re.I)
            if m:
                result["hit_context"].append(re.sub(r"\s+", " ", text[max(0, m.start()-250):m.end()+400])[:650])
        # Useful clues for year switches, without copying the underlying site.
        result["javascript_2022_snippets"] = []
        for script in parser.scripts_inline:
            for keyword in ("2022", "change", "ano", "anio", "year", "select"):
                m = re.search(re.escape(keyword), script, re.I)
                if m and len(result["javascript_2022_snippets"]) < 12:
                    result["javascript_2022_snippets"].append(
                        re.sub(r"\s+", " ", script[max(0, m.start()-120):m.end()+180])[:300]
                    )
        return result
    finally:
        target.unlink(missing_ok=True)

def main():
    out = Path("artifacts/medellin-palenque-2022")
    out.mkdir(parents=True, exist_ok=True)
    urls = [OFFICIAL + INDEX, MIRROR + INDEX] + [
        host + path for host in (OFFICIAL, MIRROR) for path in CANDIDATE_DOCS
    ]
    results = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(probe, url, i): i for i, url in enumerate(urls)}
        for fut in as_completed(futures):
            x = fut.result()
            results.append(x)
            print(f"HTTP {x['http']} / {x.get('kind', 'error')}: {x['url']}", flush=True)
    results.sort(key=lambda x: urls.index(x["url"]))
    report = {
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
        "target_act": "202250015351/2022",
        "target_routes": ["250AP", "250AiP"],
        "searched_public_sources_only": True,
        "no_pqrsd": True, "no_pdf_persisted": True,
        "status": "probed_official_astrea_indexes_and_limited_url_candidates",
        "results": results
    }
    (out / "astrea_2022_probe.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = ["## Palenque 250AP / 250AiP – original resolution web access", "",
             "| HTTP | Source | Match |", "|---|---|---|"]
    for x in results:
        yes = ", ".join(k for k, v in x.get("found_needles", {}).items() if v)
        lines.append(f"| {x['http']} | {x['url']} | {yes or x.get('kind','')} |")
    lines += ["", "These checks do not establish timetable values or current legal effectivity."]
    (out / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))

if __name__ == "__main__":
    main()
