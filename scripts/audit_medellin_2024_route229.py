#!/usr/bin/env python3
"""Read 2024 legal original for shared route 229; preserve short source excerpts.

Do not infer service frequency or agency permissions from prior-act references.
"""
import csv,json,re
from pathlib import Path
import requests
from bs4 import BeautifulSoup
ROOT=Path("artifacts/medellin-2024-229");ROOT.mkdir(parents=True,exist_ok=True)
URL="https://www.medellin.gov.co/normograma/docs/astrea/docs/r_smmed_30616_2024.htm"
ACT="202450030616"
res=requests.get(URL,timeout=40,headers={"User-Agent":"Mozilla/5.0 (ColombiaTransit legal audit)"})
res.raise_for_status()
soup=BeautifulSoup(res.content,"html.parser")
text=" ".join(soup.stripped_strings)
if ACT not in text:raise RuntimeError("Not original expected 2024 decision")
print("Official original act",ACT,"characters",len(text),"tables",len(soup.find_all("table")))
patterns=[
 ("articles",r"ART[ÍI]CULO\s+(?:PRIMERO|SEGUNDO|TERCERO|CUARTO|QUINTO|SEXTO|S[ÉE]PTIMO|OCTAVO|\d+)[.:]?"),
 ("route_229",r"\b(?:229i?|299i?)\b"),
 ("2023_chain",r"202350(?:074448|102349)"),
 ("2026",r"202650039611"),
 ("service_terms",r"\b(?:INTERVALO|FRECUENCIA|DESPACHO|HORARIO|HORA DE INICIO|HORA DE TERMINACI[ÓO]N)\b"),
]
matches=[]
for typ,pattern in patterns:
 for m in re.finditer(pattern,text,re.I):
  matches.append({"type":typ,"match":m.group(),"position":m.start(),"excerpt":text[max(0,m.start()-160):m.start()+450]})
  if typ=="articles":print("ARTICLE",text[m.start():m.start()+400])
  elif typ=="2023_chain":print("PRIOR ACT",m.group(),text[max(0,m.start()-55):m.start()+100])
for i,table in enumerate(soup.find_all("table"),1):
 print(f"TABLE {i} rows={len(table.find_all('tr'))}")
 for tr in table.find_all("tr")[:4]:
  print("  "+" | ".join(" ".join(c.stripped_strings)[:100] for c in tr.find_all(["td","th"],recursive=False))[:450])
with (ROOT/"source_matches.json").open("w",encoding="utf8") as f:json.dump({"act":ACT,"url":URL,"matches":matches},f,ensure_ascii=False,indent=2)
print("Extracted research-only snippets; no timetable promoted.")
