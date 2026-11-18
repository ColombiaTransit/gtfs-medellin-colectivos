#!/usr/bin/env python3
"""Targeted lookups in official municipal historical Gazette search.

Uses the same public GET form's numero_acto field. Only reports evidence
that is actually returned; no fabricated PDF paths or timing records.
"""
import json,re,time
from pathlib import Path
import requests
from bs4 import BeautifulSoup
BASE="https://www.medellin.gov.co/statements/innovaciondigital/gacetas/historico-mercurio"
ROOT=Path("artifacts/medellin-historico-lookups")
ROOT.mkdir(parents=True,exist_ok=True)
TESTS=["202350107412","201850015842","201950052919","202050056226","202350008449","202450030616","202550079865"]
s=requests.Session()
s.headers.update({"User-Agent":"Mozilla/5.0 (compatible; ColombiaTransit-public-archive-research/1.0)"})
results=[]
for num in TESTS:
 try:
  r=s.get(BASE,params={"numero_acto":num},timeout=(15,50))
  soup=BeautifulSoup(r.text,"html.parser")
  tables=[]
  for table in soup.select("table"):
   rows=table.select("tr")
   found=[]
   for tr in rows:
    cells=[" ".join(td.stripped_strings) for td in tr.find_all(["td","th"])]
    v=" | ".join(cells)
    if num in v:
     found.append(dict(cells=cells[:10],html_tag_excerpt=str(tr)[:1800],links=[a.get("href") for a in tr.find_all("a")]))
   if found:tables.append(dict(id=table.get("id"),found=found[:10]))
  text=" ".join(soup.stripped_strings)
  doc_ids=list(dict.fromkeys(re.findall(r"(?:visualizarDocumento|descargarDocumento|verDocumento)\\s*\\(\\s*['\\\"]?(\\d+)",r.text,re.I)))[:10]
  marker={a:bool(re.search(a,text,re.I)) for a in ("No se encontraron","No hay resultados","Utilice los filtros","Resultados de búsqueda","Error")}
  item=dict(number=num,url=r.url,status=r.status_code,size=len(r.content),tables=tables,document_ids=doc_ids,marker=marker,text_excerpt=text[-1300:] if not tables else "")
  results.append(item)
  print(f"{num}: HTTP {r.status_code} rows={sum(len(t['found']) for t in tables)} doc_ids={doc_ids} page={len(r.content)} final={r.url}",flush=True)
 except Exception as ex:
  results.append(dict(number=num,error=type(ex).__name__+": "+str(ex)))
  print(f"{num}: ERROR {type(ex).__name__}: {ex}",flush=True)
 time.sleep(0.25)
(ROOT/"pilot_lookup_results.json").write_text(json.dumps(results,ensure_ascii=False,indent=2)+"\\n",encoding="utf-8")
