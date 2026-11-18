#!/usr/bin/env python3
"""Bounded screening of official indexed 2026 Movilidad acts for 2025 urban-bus changes."""
import csv, json, re, sys, unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin
from html.parser import HTMLParser
sys.path.insert(0,"scripts")
from scan_astrea_2026_palenque_acts import fetch, Anchors, INDEX
out=Path("artifacts/medellin-2026-targeted-supersession")
out.mkdir(parents=True,exist_ok=True)
def norm(s):
 s=unicodedata.normalize("NFKD",s)
 return "".join(c for c in s if not unicodedata.combining(c)).lower()
operators={
 "202550076150":["coinvetrans","invetrans","salud hotelera"],
 "202550076162":["castilla","conaltracoop","conaltracoopo","conaltracoo"],
 "202550079848":["metrosan","metro san"],
 "202550079865":["rapido san cristobal"],
 "202550076174":["coonatra","santra"],
}
refs=set(operators)
html=fetch(INDEX);a=Anchors();a.feed(html)
urls=sorted(set(urljoin(INDEX,x) for x in a.links if re.search(r"/(?:r|R)_SMMED_\\d+_2026\\.htm",x,re.I)))
if not (15<=len(urls)<=60):raise RuntimeError(f"2026 ASTREA index changed unexpectedly: {len(urls)}")
rows=[];errors=[]
for url in urls:
 try:
  body=fetch(url)
  clean=re.sub(r"\\s+"," ",re.sub(r"<[^>]*>"," ",body))
  normalized=norm(clean)
  found=[act for act in refs if act in normalized]
  hits={act:[k for k in keys if norm(k) in normalized] for act,keys in operators.items()}
  hits={k:v for k,v in hits.items() if v}
  if found or hits:
   rows.append(dict(url=url,linked_2025_acts=";".join(found),operator_groups=";".join(hits),keyword_matches=json.dumps(hits,ensure_ascii=False),evidence_status="2026_index_candidate_only_scope_review_required"))
  print(f"Checked {url.split('/')[-1]}: {len(found)} act-number matches, {len(hits)} operator groups",flush=True)
 except Exception as ex:errors.append(dict(url=url,error=str(ex)))
with (out/"candidate_amendments.csv").open("w",newline="",encoding="utf-8") as f:
 w=csv.DictWriter(f,fieldnames=["url","linked_2025_acts","operator_groups","keyword_matches","evidence_status"]);w.writeheader();w.writerows(rows)
report={"checked_at":datetime.now(timezone.utc).isoformat(),"source":INDEX,"indexed_2026_act_count":len(urls),"read_success":len(urls)-len(errors),"read_failure":len(errors),"candidate_count":len(rows),"matching_pages":rows,"errors":errors,"caveat":"Index-limited textual screen, hits may be incidental mentions; no proof of lack of 2026 amendments outside index."}
(out/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\\n",encoding="utf-8")
print(f"RESULT: {len(rows)} candidate pages / {len(urls)} indexed; {len(errors)} errors")
if errors:raise RuntimeError("2026 act screen incomplete; do not claim exhaustive coverage")
