#!/usr/bin/env python3
"""Extract compact route/table evidence from confirmed official Medellín 2025 ASTREA acts.

Produces research candidates; numeric tables require source QA and route matching.
"""
import csv
import json
import re
from pathlib import Path
import requests
from bs4 import BeautifulSoup

ROOT=Path("artifacts/medellin-2025-official-tables")
ROOT.mkdir(parents=True,exist_ok=True)
ACTS={"202550076150":"76150","202550076162":"76162","202550076174":"76174","202550079848":"79848","202550079865":"79865"}
session=requests.Session()
session.headers.update({"User-Agent":"Mozilla/5.0 (compatible; ColombiaTransit-official-acts-research/1.0)"})
rows=[]
sections=[]
for act,short in ACTS.items():
 url=f"https://www.medellin.gov.co/normograma/docs/astrea/docs/r_smmed_{short}_2025.htm"
 r=session.get(url,timeout=(15,60))
 r.raise_for_status()
 soup=BeautifulSoup(r.content,"html.parser")
 text=soup.get_text(" ",strip=True)
 if act not in text:raise RuntimeError(f"Act number not found in {url}")
 for table_no,table in enumerate(soup.find_all("table"),1):
  for ri,tr in enumerate(table.find_all("tr"),1):
   cells=[" ".join(td.stripped_strings) for td in tr.find_all(["td","th"],recursive=False)]
   if not cells: continue
   compact=" | ".join(cells)
   if not re.search(r"(ruta|c[oó]digo|interval|frecuencia|hora|despacho|servicio|operaci[oó]n|\d{2}:\d{2}|\b\d{3}[a-z]?\b)",compact,re.I):
    continue
   rows.append(dict(act_number=act,url=url,table_number=table_no,row_number=ri,cells=json.dumps(cells,ensure_ascii=False),review_status="unverified_original_html_extraction"))
 for m in re.finditer(r"ART[ÍI]CULO\s+(?:PRIMERO|SEGUNDO|TERCERO|CUARTO|QUINTO|SEXTO|S[ÉE]PTIMO|OCTAVO|NOVENO|D[ÉE]CIMO|\d+)",text,re.I):
  excerpt=text[m.start():m.start()+800]
  sections.append(dict(act_number=act,url=url,article_excerpt=excerpt))
 print(f"{act}: {len(soup.find_all('table'))} tables, {sum(x['act_number']==act for x in rows)} candidate rows, {sum(x['act_number']==act for x in sections)} articles",flush=True)
for fname,data,fields in [
 ("candidate_table_rows.csv",rows,["act_number","url","table_number","row_number","cells","review_status"]),
 ("article_excerpts.csv",sections,["act_number","url","article_excerpt"])
]:
 with (ROOT/fname).open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(data)
print(f"Extracted {len(rows)} candidate rows and {len(sections)} article headings; no GTFS update.")
