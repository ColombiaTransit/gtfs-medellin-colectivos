#!/usr/bin/env python3
"""Check official Medellín publication candidates for six indexed 2025 urban bus acts.

Do not infer full resolution content or GTFS timetables from index-only results.
Outputs short source evidence and checksums, never full PDF/HTML originals to git.
"""
import csv
import hashlib
import json
import re
from pathlib import Path
import requests
from bs4 import BeautifulSoup

OUT = Path("artifacts/medellin-2025-official-acts")
OUT.mkdir(parents=True, exist_ok=True)
ACTS = {
 "202550076168": ("5667", "Combuses / Circular 313"),
 "202550076174": ("5667", "Coonatra and Santra / 301-315"),
 "202550076150": ("5671", "Coinvetrans and Invetrans / Salud-Hotelera"),
 "202550076162": ("5671", "Castilla and Conaltracoop / 2A-2B"),
 "202550079848": ("5671", "Metrosan"),
 "202550079865": ("5671", "Rapido San Cristobal"),
}
BASE = "https://www.medellin.gov.co"
session = requests.Session()
session.headers.update({"User-Agent":"Mozilla/5.0 (compatible; ColombiaTransit-legal-source-check/1.0)", "Accept":"text/html,application/pdf,*/*;q=0.8"})
rows=[]
for number,(gazette,scope) in ACTS.items():
 short=int(number[-6:])  # candidate only; tested against actual response and act text
 # ASTREA filenames use different capitalization on different official source pages.
 candidates=[
   f"{BASE}/normograma/docs/astrea/docs/r_smmed_{short}_2025.htm",
   f"{BASE}/normograma/docs/astrea/docs/R_SMMED_{short}_2025.htm",
 ]
 found=False
 for url in candidates:
  try:
   r=session.get(url,timeout=(12,35),allow_redirects=True)
   mime=r.headers.get("content-type","")
   text=BeautifulSoup(r.text,"html.parser").get_text(" ",strip=True) if r.status_code==200 and "html" in mime.lower() else ""
   match=bool(re.search(r"(?<!\\d)"+re.escape(number)+r"(?!\\d)",text))
   row=dict(act_number=number,gazette=gazette,scope=scope,url=url,http_status=r.status_code,mime_type=mime,has_full_act_number=match,text_length=len(text),sha256=hashlib.sha256(r.content).hexdigest() if r.status_code==200 else "",evidence_status="official_full_text_candidate_confirmed" if match else "unverified_or_missing")
   rows.append(row)
   if match:
    found=True
    # Record only a short passage around act number, not an entire copyrighted original.
    pos=text.find(number)
    (OUT / f"act_{number}_source_excerpt.txt").write_text(text[max(0,pos-400):pos+2000],encoding="utf-8")
    break
  except requests.RequestException as exc:
   rows.append(dict(act_number=number,gazette=gazette,scope=scope,url=url,http_status="error",mime_type="",has_full_act_number=False,text_length=0,sha256="",evidence_status=type(exc).__name__))
 print(f"{number}: {'official text candidate' if found else 'no confirmed full text at tested URLs'}",flush=True)

for gazette in ("5667","5671"):
 url=f"{BASE}/statements/innovaciondigital/gacetas/consulta-publica/{gazette}"
 try:
  r=session.get(url,timeout=(12,35))
  text=BeautifulSoup(r.text,"html.parser").get_text(" ",strip=True) if r.status_code==200 else ""
  checked=[n for n,(g,_) in ACTS.items() if g==gazette and n in text]
  (OUT / f"gaceta_{gazette}_index_check.json").write_text(json.dumps(dict(url=url,status=r.status_code,document_numbers_mentioned=checked,content_bytes=len(r.content)),indent=2)+"\n",encoding="utf-8")
  print(f"Gaceta {gazette}: HTTP {r.status_code}, indexed acts {checked}",flush=True)
 except requests.RequestException as exc:
  (OUT / f"gaceta_{gazette}_index_check.json").write_text(json.dumps(dict(url=url,error=str(exc)))+"\n",encoding="utf-8")
with (OUT/"official_act_link_checks.csv").open("w",newline="",encoding="utf-8") as f:
 fields=["act_number","gazette","scope","url","http_status","mime_type","has_full_act_number","text_length","sha256","evidence_status"]
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
print(f"Checked {len(rows)} URL candidates for {len(ACTS)} acts. No timetable assertions made.")
