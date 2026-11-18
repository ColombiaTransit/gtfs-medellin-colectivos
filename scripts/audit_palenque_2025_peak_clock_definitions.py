#!/usr/bin/env python3
"""One-off focused legal-period evidence scan, not a recurrent scraper.
Reads the official 2025 Palenque original and scans for clock-specific PP/PVM
mentions. Does not apply any generic rush hour assumptions to GTFS.
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.request import Request,urlopen
import re,json
URL="https://www.medellin.gov.co/normograma/docs/astrea/docs/r_smmed_88689_2025.htm"
OUT=Path("artifacts/palenque-pico-period-evidence")
OUT.mkdir(parents=True,exist_ok=True)
class T(HTMLParser):
 def __init__(self):super().__init__();self.parts=[]
 def handle_data(self,s):self.parts.append(s)
req=Request(URL,headers={"User-Agent":"Mozilla/5.0","Accept":"text/html"})
with urlopen(req,timeout=45) as h:html=h.read().decode("utf8","replace")
parser=T();parser.feed(html)
txt=re.sub(r"\s+"," "," ".join(parser.parts))
if "202550088689" not in txt:raise RuntimeError("Unexpected official document")
patterns=["Período pico","Periodo pico","Período valle meridiano","periodo valle meridiano","Período valle extremo","PVE:","PP:","PVM:","4:30","20:30","franja horaria","hora pico"]
hits=[]
for p in patterns:
 for m in re.finditer(re.escape(p),txt,re.I):
  context=txt[max(0,m.start()-230):m.end()+390]
  hits.append({"needle":p,"position":m.start(),"context":context})
report={"source":URL,"document_id":"202550088689","html_length":len(html),"text_length":len(txt),"hits":hits,"matching_count":len(hits),"caveat":"Keyword audit only; absence is not proof no definitions in annexes."}
(OUT/"palenque_period_snippets.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf8")
print("MATCHES",len(hits))
for x in hits:print(x["needle"],x["context"][:520])
