#!/usr/bin/env python3
"""Find ORIGINAL municipal ASTREA full-text URLs for already-indexed historic bus acts.

Bounded source-first lookup; do not imply that failed URL patterns mean absent acts.
Never stores full third-party HTML in version control.
"""
import csv
import hashlib
import json
import re
from pathlib import Path
import requests
from bs4 import BeautifulSoup

ROOT=Path("data/resolutions")
OUT=Path("artifacts/medellin-2017-2024")
OUT.mkdir(parents=True,exist_ok=True)
SRC=ROOT/"2017_2024_act_chain_index.csv"
act_rows=list(csv.DictReader(SRC.open(encoding="utf-8")))
session=requests.Session()
session.headers.update({"User-Agent":"Mozilla/5.0 (ColombiaTransit legal provenance research)", "Accept":"text/html,*/*"})
results=[]
for act in act_rows:
 no=act["resolution"]
 year=act["issued_on"][:4]
 if not year.isdigit() or not no.isdigit():continue
 short=str(int(no[-6:])) if len(no)>7 else no
 root="https://www.medellin.gov.co/normograma/docs/astrea/docs/"
 urls=[root+f"r_smmed_{short}_{year}.htm",root+f"R_SMMED_{short}_{year}.htm"]
 last_status=""
 for url in urls:
  try:
   response=session.get(url,timeout=(10,20),allow_redirects=True)
   last_status=str(response.status_code)
   if response.status_code!=200:continue
   html=response.text
   body=" ".join(BeautifulSoup(html,"html.parser").stripped_strings)
   if not re.search(r"(?<!\\d)"+re.escape(no)+r"(?!\\d)",body):
    continue
   # The number might be mentioned incidentally in another resolution:
   # require official resolution type and number in beginning of body too.
   full=bool(re.search(r"resoluci[oó]n",body[:3500],re.I))
   if not full:continue
   results.append(dict(resolution=no,year=year,operator=act["operators_named_in_official_report"],reported_effect=act["reported_act_effect"],original_url=response.url,sha256=hashlib.sha256(response.content).hexdigest(),text_chars=len(body),retrieval_status="official_candidate_original_html_requires_subject_qa"))
   print(f"FOUND {no} {response.url}",flush=True)
   break
  except requests.RequestException as exc:
   last_status=type(exc).__name__
 else:
  results.append(dict(resolution=no,year=year,operator=act["operators_named_in_official_report"],reported_effect=act["reported_act_effect"],original_url="",sha256="",text_chars=0,retrieval_status="not_found_in_tested_urls_"+last_status))
  print(f"NOT FOUND {no}: {last_status}",flush=True)
fields=["resolution","year","operator","reported_effect","original_url","sha256","text_chars","retrieval_status"]
with (OUT/"original_source_discovery.csv").open("w",newline="",encoding="utf-8") as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(results)
print(f"Confirmed ASTREA candidates {sum(bool(r['original_url']) for r in results)}/{len(results)} original acts",flush=True)
