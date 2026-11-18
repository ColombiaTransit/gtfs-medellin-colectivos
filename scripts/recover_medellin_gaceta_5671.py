#!/usr/bin/env python3
"""Recover official 2025 Gaceta 5671 PDF by its public exact-number lookup.

Requires a verified official query/result/document ID relationship.
The original is retained only as a transient Actions artifact.
"""
import csv,hashlib,re,subprocess
from pathlib import Path
import requests
from bs4 import BeautifulSoup
BASE="https://www.medellin.gov.co/statements/innovaciondigital/gacetas/historico-mercurio"
ACT="202550079865"
OUT=Path("artifacts/medellin-original-gaceta-5671")
OUT.mkdir(parents=True,exist_ok=True)
s=requests.Session();s.headers.update({"User-Agent":"Mozilla/5.0 (compatible; ColombiaTransit-Gaceta-official-source-recovery/1.0)"})
r=s.get(BASE,params={"numero_acto":ACT},timeout=(12,40));r.raise_for_status()
found=[]
for tr in BeautifulSoup(r.text,"html.parser").find_all("tr"):
 tds=tr.find_all("td",recursive=False)
 if len(tds)<8:continue
 cols=[" ".join(td.stripped_strings) for td in tds]
 if cols[3].strip()!=ACT:continue
 ids=re.findall(r"descargarDocumento\(this,\s*['\"](\d+)['\"]\)",str(tds[-1]),re.I)
 if ids:found.append((cols,ids[0]))
if len(found)!=1:raise RuntimeError(f"Expected one exact official record, got {len(found)}")
meta,docid=found[0]
if meta[0]!="5671":raise RuntimeError("Unexpected official Gaceta number "+meta[0])
url=BASE+"/descargar/"+docid
rr=s.get(url,timeout=(15,120),stream=True);rr.raise_for_status()
p=OUT/"gaceta_5671_2025_official.pdf";h=hashlib.sha256();size=0;head=b""
with p.open("wb") as f:
 for b in rr.iter_content(131072):
  if not b:continue
  size+=len(b);h.update(b)
  if len(head)<5:head+=b[:5-len(head)]
  if size>40000000:raise RuntimeError("Original Gaceta PDF > 40 MB cap")
  f.write(b)
if not head.startswith(b"%PDF-"):raise RuntimeError("Response was not a PDF")
txt=OUT/"gaceta_5671_original.txt"
subprocess.run(["pdftotext","-layout",str(p),str(txt)],check=True)
info=subprocess.run(["pdfinfo",str(p)],capture_output=True,text=True,check=True).stdout
pages=re.search(r"^Pages:\s*(\d+)",info,re.M)
text=txt.read_text(errors="replace")
for num in ("202550076150","202550076162","202550079848","202550079865"):
 if num not in text:raise RuntimeError("Expected act omitted from original Gazette: "+num)
record={"gaceta":"5671","act_search_number":ACT,"document_id":docid,"published_on":meta[6],"pdf_sha256":h.hexdigest(),"pdf_bytes":size,"pages":pages.group(1) if pages else "","official_url":url,"four_expected_acts_in_extracted_text":"yes","source_class":"verified_official_original_gaceta_pdf"}
keys=list(record)
with (OUT/"official_gaceta_recovery.csv").open("w",newline="",encoding="utf8") as f:
 w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerow(record)
print(f"RECOVERED Gaceta 5671: {size} bytes, pages={record['pages']}, SHA256={record['pdf_sha256']}, all 4 acts found, URL={url}")
