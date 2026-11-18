#!/usr/bin/env python3
"""Recover missing official 2025 Circular 313 original through public historic Gaceta.

Uses official public search GET and result's own document ID. Does not guess IDs.
The PDF is stored only as an expiring Actions artifact; no production GTFS changes.
"""
import csv, json, re, subprocess, time
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
BASE="https://www.medellin.gov.co/statements/innovaciondigital/gacetas/historico-mercurio"
OUT=Path("artifacts/medellin-2025-historic-gaceta-originals")
OUT.mkdir(parents=True,exist_ok=True)
TESTS=["202550076168","202550076174","202550076150","202550076162","202550079848","202550079865"]
s=requests.Session()
s.headers.update({"User-Agent":"Mozilla/5.0 (compatible; ColombiaTransit-Gaceta-primary-source-audit/1.0)"})
rows=[]
for act in TESTS:
 item=dict(act_number=act,gaceta="",gazette_year="",act_date="",publication_date="",document_id="",title="",official_search_url="",pdf_status="not_downloaded",pdf_sha256="",pdf_bytes="")
 try:
  response=s.get(BASE,params={"numero_acto":act},timeout=(12,45))
  response.raise_for_status()
  item["official_search_url"]=response.url
  soup=BeautifulSoup(response.text,"html.parser")
  found=[]
  for tr in soup.find_all("tr"):
   tds=tr.find_all("td",recursive=False)
   if len(tds)<8:continue
   cells=[" ".join(td.stripped_strings) for td in tds]
   if cells[3].strip()!=act:continue
   actions=str(tds[-1])
   ids=re.findall(r"descargarDocumento\(this,\s*['\"](\d+)['\"]\)",actions,re.I)
   if not ids:
    ids=re.findall(r"visualizarDocumento\(['\"](\d+)['\"]\)",actions,re.I)
   found.append(dict(cells=cells,ids=ids))
  if len(found)!=1:
   item["pdf_status"]="exact_act_result_count_"+str(len(found))
  else:
   data=found[0]
   cells=data["cells"]
   item.update(gaceta=cells[0],gazette_year=cells[1],title=cells[4],act_date=cells[5],publication_date=cells[6],document_id=data["ids"][0] if data["ids"] else "")
   item["pdf_status"]="official_search_result_found"
   if act=="202550076168" and item["document_id"]:
    url=BASE+"/descargar/"+item["document_id"]
    d=s.get(url,timeout=(15,100),stream=True)
    d.raise_for_status()
    out=OUT/("res_"+act+"_gaceta_"+item["gaceta"]+".pdf")
    import hashlib
    h=hashlib.sha256();size=0;prefix=b""
    with out.open("wb") as f:
     for chunk in d.iter_content(131072):
      if not chunk:continue
      size+=len(chunk);h.update(chunk)
      if len(prefix)<8:prefix+=chunk[:8-len(prefix)]
      if size>40000000:raise RuntimeError("PDF exceeds bounded artifact maximum 40 MB")
      f.write(chunk)
    if not prefix.startswith(b"%PDF-"):
     out.unlink(missing_ok=True)
     item["pdf_status"]="download_not_pdf"
    else:
     item.update(pdf_status="official_original_pdf_magic_verified",pdf_sha256=h.hexdigest(),pdf_bytes=size)
     p=subprocess.run(["pdftotext","-layout",str(out),str(OUT/("res_"+act+"_text.txt"))],capture_output=True,text=True)
     item["text_extracted"]=p.returncode==0
     print("RECOVERED",act,"original PDF",size,"bytes SHA256",h.hexdigest(),flush=True)
 except Exception as exc:
  item["pdf_status"]="error_"+type(exc).__name__
  print("ERROR",act,type(exc).__name__,str(exc)[:200],flush=True)
 rows.append(item)
 print("LOOKUP",act,item["pdf_status"],"gaceta",item["gaceta"],"document",item["document_id"],flush=True)
 time.sleep(0.25)
keys=["act_number","gaceta","gazette_year","act_date","publication_date","document_id","title","official_search_url","pdf_status","pdf_sha256","pdf_bytes","text_extracted"]
with (OUT/"official_source_recovery.csv").open("w",newline="",encoding="utf8") as f:
 w=csv.DictWriter(f,fieldnames=keys,extrasaction="ignore");w.writeheader();w.writerows(rows)
print("SUMMARY",sum(x["pdf_status"]=="official_original_pdf_magic_verified" for x in rows),"verified original PDF(s);",sum(bool(x["document_id"]) for x in rows),"historic index hits",flush=True)
