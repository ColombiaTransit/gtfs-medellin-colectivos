#!/usr/bin/env python3
"""Capture original operator-published Calasanz PDF departure slots, not GTFS.

The PDF is a multi-column layout and printed times are not necessarily in
chronological row order. Use rendered-page, coordinate-isolated group bands;
refuse to publish if observed first/last disagree with operator's webpages.
"""
import csv,re,requests,fitz
from collections import Counter
from pathlib import Path
SOURCE="https://coonatra.com/wp-content/uploads/2022/08/Frecuencias-rutas-Calasanz.pdf"
OUTPUT=Path("data/resolutions/coonatra_2022_calasanz_exact_departures_by_variant.csv")
SPECS=[
 # page, x_left fractional, x_right fractional, text name, route code,
 # GIS candidate, expected earliest, expected latest
 (0,.10,.44,"310 Directo Calasanz Boston","310","90007","04:20","21:10"),
 (0,.44,.68,"310 Rosal","310R","90363","05:06","20:06"),
 (0,.68,.92,"310 Metro Rosal","310 Metro Rosal","90363","05:00","21:42"),
 (1,.12,.65,"311 Calasanz Boston","311","90008","04:25","21:20"),
 (1,.65,.91,"311 Metro","311-i","90324","04:35","21:45"),
 (2,.32,.68,"311 Metro Directo","311-ii","90325","04:30","22:30"),
]
# Accept minor PDF text representation quirks e.g. "4:20 a. m."
PAT=re.compile(r"(?<!\d)(\d{1,2}):(\d{2})\s*([ap])\.?\s*m\.?",re.I)
def hhmm(t):
 h=int(t.group(1));m=int(t.group(2));mer=t.group(3).lower()
 if not 1<=h<=12 or m>59:raise ValueError(t.group())
 h=h%12+(12 if mer=="p" else 0)
 return f"{h:02d}:{m:02d}"
r=requests.get(SOURCE,timeout=50,headers={"User-Agent":"Mozilla/5.0 ColombiaTransit"})
r.raise_for_status()
if not r.content.startswith(b"%PDF"):raise ValueError("Not PDF")
pdf=fitz.open(stream=r.content,filetype="pdf")
assert len(pdf)==3,len(pdf)
out=[]
for page_no,left,right,name,code,candidate,expected_start,expected_end in SPECS:
 page=pdf[page_no];rect=page.rect
 # clip to sub-table column bands and beneath header, above footer.
 clip=fitz.Rect(rect.width*left,rect.height*.13,rect.width*right,rect.height*.90)
 snippet=page.get_text("text",clip=clip,sort=True)
 matches=list(PAT.finditer(snippet))
 clockvals=sorted(hhmm(match) for match in matches)
 if not clockvals:raise ValueError(f"No time strings found {name}, snippet={snippet[:300]!r}")
 print(name,"n=",len(clockvals),"range",clockvals[0],clockvals[-1],flush=True)
 if (clockvals[0],clockvals[-1])!=(expected_start,expected_end):
  raise ValueError(f"First/last cross-check failed for {name} {clockvals[:3]} {clockvals[-3:]} expected {expected_start} {expected_end}")
 if len(clockvals)<25:raise ValueError(f"Suspiciously incomplete table {name}")
 for index,t in enumerate(clockvals,1):
  out.append(dict(operator="Coonatra",published_variant=name,published_route_code=code,
   legacy_arcgis_candidate_id=candidate,departure_sequence=index,published_departure_time=t,
   service_day_scope="not_specified_in_original_pdf",direction="not_specified_in_original_pdf",
   original_pdf_page=page_no,source_type="direct_operator_full_departure_table",
   source_url=SOURCE,arcgis_variant_identity_verified="no",
   fixed_departure_gtfs_import="no",
   confidence_note="Each source table printed in columns: times normalized by clock. Day, terminal, direction, and 2026 validity need confirmation."))
OUTPUT.parent.mkdir(parents=True,exist_ok=True)
with OUTPUT.open("w",newline="",encoding="utf-8") as f:
 w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
print("TOTAL_SLOTS",len(out),"TOTAL_VARIANTS",len(SPECS))
