#!/usr/bin/env python3
"""Inspect the public Medellín historical Gaceta search UI for its search endpoint.

This is a bounded reconnaissance of the official public page and its JS assets.
No authentication, bypassing access controls or guessed document downloads.
"""
import json,re
from pathlib import Path
from urllib.parse import urljoin,urlparse
import requests
from bs4 import BeautifulSoup
BASE="https://www.medellin.gov.co/statements/innovaciondigital/gacetas/historico-mercurio"
OUT=Path("artifacts/medellin-historical-gaceta-discovery");OUT.mkdir(parents=True,exist_ok=True)
s=requests.Session();s.headers.update({"User-Agent":"Mozilla/5.0 (compatible; ColombiaTransit-Gaceta-original-source-research/1.0)"})
r=s.get(BASE,timeout=(12,45));print("HISTORICAL PAGE",r.status_code,r.url,r.headers.get("content-type"),len(r.content),flush=True);r.raise_for_status()
html=r.text;soup=BeautifulSoup(html,"html.parser")
patterns=(r"gaceta.{0,15}(search|buscar|histor|consult|api)",r"/api/[a-zA-Z0-9/_-]+",r"fetch\(",r"axios\.",r"historico-mercurio",r"merc[uú]rio",r"search[A-Z]?",r"form.*action")
assets=[]
for scr in soup.find_all("script"):
 src=scr.get("src","")
 if src:
  full=urljoin(r.url,src)
  if urlparse(full).hostname=="www.medellin.gov.co":assets.append(full)
inline="\n".join(scr.get_text() for scr in soup.find_all("script") if not scr.get("src"))
def snippets(body):
 output=[];used=set()
 for regex in patterns:
  for m in re.finditer(regex,body,re.I):
   excerpt=body[max(0,m.start()-150):m.end()+260].replace("\n"," ").strip()
   if excerpt in used:continue
   used.add(excerpt);output.append(dict(pattern=regex,excerpt=excerpt[:460]))
   if len(output)>=90:return output
 return output
result={"page_url":r.url,"status":r.status_code,"forms":[dict(action=f.get("action"),method=f.get("method"),inputs=[i.get("name") for i in f.find_all("input")]) for f in soup.find_all("form")],"script_urls":assets,"inline_matches":snippets(inline),"external":[]}
for i,url in enumerate(assets[:25]):
 try:
  t=s.get(url,timeout=(12,25))
  body=t.text if t.status_code==200 and len(t.content)<600000 else ""
  found=snippets(body)
  print("SCRIPT",i,t.status_code,len(t.content),"MATCHES",len(found),url,flush=True)
  if found:result["external"].append(dict(url=url,matches=found))
 except Exception as ex:print("SCRIPT_ERR",type(ex).__name__,url,flush=True)
print("INLINE MATCHES",len(result["inline_matches"]))
for o in result["inline_matches"][:20]:print("INLINE",o["excerpt"])
for a in result["external"][:8]:
 for o in a["matches"][:8]:print("ASSET",a["url"],o["excerpt"])
(OUT/"page_api_evidence.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
