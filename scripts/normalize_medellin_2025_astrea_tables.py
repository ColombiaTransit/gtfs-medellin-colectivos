#!/usr/bin/env python3
"""Normalize factual route identities and raw timetable strings extracted from official ASTREA HTML.

Does not accept numeric strings as a validated GTFS timetable. Key by act+GTPC+user code;
merged direction cells, special rural fixed departures, and no-service remain untouched.
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

source=Path("artifacts/medellin-2025-official-tables/candidate_table_rows.csv")
out=Path("data/resolutions/2025_astrea_official_route_timetable_candidates.csv")
T=defaultdict(lambda:defaultdict(list))
with source.open(encoding="utf-8",newline="") as f:
 for r in csv.DictReader(f):
  T[r["act_number"]][int(r["table_number"])].append(json.loads(r["cells"]))
spec={
 "202550076150":{"master":[1],"hours":[2],"intervals":[3,4,5]},
 "202550076162":{"master":[1,2,3],"hours":[4],"intervals":[5,6,7]},
 "202550079848":{"master":[1],"hours":[2],"intervals":[3,4,5]},
 "202550079865":{"master":[1,2,3],"hours":[4,5],"intervals":[6,7,8]},
}
D={}
def valid(c):
 return len(c)>=5 and c[0].strip().isdigit() and len(c[0].strip())>=4
for act,S in spec.items():
 for t in S["master"]:
  for cells in T[act][t]:
   if not valid(cells):continue
   code=cells[0].strip()
   key=(act,code,cells[1].strip())
   r=D.setdefault(key,{"act_number":act,"gtpc":code,"user_route_code":key[2]})
   r.update(route_type=cells[2],route_name=cells[3],route_table_number=t)
 for t in S["hours"]:
  for cells in T[act][t]:
   if not valid(cells):continue
   key=(act,cells[0].strip(),cells[1].strip())
   r=D.setdefault(key,{"act_number":act,"gtpc":key[1],"user_route_code":key[2]})
   r["hours_table_"+str(t)]="|".join(cells[3:])
 for i,t in enumerate(S["intervals"]):
  for cells in T[act][t]:
   if not valid(cells):continue
   key=(act,cells[0].strip(),cells[1].strip())
   r=D.setdefault(key,{"act_number":act,"gtpc":key[1],"user_route_code":key[2]})
   r["interval_"+("weekday","saturday","sunday_holiday")[i]]="|".join(cells[3:])
# PDF-source QA: the original Gaceta 5671 pp25-26 visibly publishes three
# day-type interval triples for TRONCAL 65/73. Keep these source rows and fail
# loudly on an extraction mismatch instead of silently marking them missing.
trunk_source_checks = {
    ("23607", "TRONCAL 65"): ("8|15|10", "10|18|12", "13|16|20"),
    ("23609", "TRONCAL 73"): ("4|8|6", "5|10|8", "6|10|13"),
}
for (gtpc, route_code), expected_by_day in trunk_source_checks.items():
    key=("202550076162", gtpc, route_code)
    if key not in D:
        raise RuntimeError(f"Official route missing from 2025 Castilla master: {key}")
    for table_no, field, expected in zip((5, 6, 7),
            ("interval_weekday", "interval_saturday", "interval_sunday_holiday"),
            expected_by_day):
        matches=[cells for cells in T["202550076162"][table_no]
                 if len(cells)>=6 and cells[0].strip()==gtpc and cells[1].strip()==route_code]
        if len(matches)!=1:
            raise RuntimeError(f"Missing/duplicate 2025 original trunk interval {key}, table {table_no}")
        actual="|".join(x.strip() for x in matches[0][3:6])
        if actual!=expected:
            raise RuntimeError(f"Visual original p25-26 mismatch for {key}: {actual!r} != {expected!r}")
        D[key][field]=actual
# Some Palmitas corregimental services publish fixed departures in master table 3,
# not in the separate table 5 or periodic interval tables.
for cells in T["202550079865"][3]:
 if len(cells) >= 8 and cells[0].strip() in {"23726", "23727", "23728"}:
  key=("202550079865",cells[0].strip(),cells[1].strip())
  if key not in D:
   raise RuntimeError("Original Palmitas route missing from master register: "+str(key))
  D[key]["fixed_departures_master_table"]="|".join(cells[6:8])
# Veredal rows in the source interval tables contain service COUNTS, not
# numeric headways. Keep them as per-day counts and never interpolate trips.
import re
for index, table_no in enumerate((6,7,8)):
 field=("weekday_services_per_day","saturday_services_per_day","sunday_holiday_services_per_day")[index]
 for cells in T["202550079865"][table_no]:
  if len(cells) < 4 or cells[0].strip() not in {"23711","23712","23713","23714","23715","23716","23717"}:
   continue
  match=re.fullmatch(r"\s*(\d+)\s+servicios\s+en\s+el\s+d[ií]a\s*",cells[3],re.I)
  if not match:
   raise RuntimeError(f"Unexpected source count for {cells[0]} on table {table_no}: {cells[3]!r}")
  key=("202550079865",cells[0].strip(),cells[1].strip())
  if key not in D: raise RuntimeError(f"Count belongs to absent route: {key}")
  D[key][field]=match.group(1)
counts_by_route={r["gtpc"]:r for r in D.values() if r["act_number"]=="202550079865" and r["gtpc"] in {"23711","23712","23713","23714","23715","23716","23717"}}
if len(counts_by_route)!=7 or any(not all(r.get(k) for k in ("weekday_services_per_day","saturday_services_per_day","sunday_holiday_services_per_day")) for r in counts_by_route.values()):
 raise RuntimeError("Seven veredal route daily counts not fully recovered")
fields=["act_number","gtpc","user_route_code","route_type","route_name","route_table_number","hours_table_2","hours_table_4","hours_table_5","interval_weekday","interval_saturday","interval_sunday_holiday","source_QA","gtfs_import","fixed_departures_master_table","weekday_services_per_day","saturday_services_per_day","sunday_holiday_services_per_day"]
for r in D.values():
 r.update(source_QA="official_astrea_html_extracted_not_visually_accepted",gtfs_import="no")
out.parent.mkdir(parents=True,exist_ok=True)
with out.open("w",newline="",encoding="utf-8") as f:
 w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore")
 w.writeheader()
 w.writerows(sorted(D.values(),key=lambda x:(x["act_number"],x["gtpc"],x.get("user_route_code",""))))
from collections import Counter
count=Counter(r["act_number"] for r in D.values())
assert count=={"202550076150":6,"202550076162":30,"202550079848":16,"202550079865":34},count
print("Saved",len(D),"official ASTREA route/direction candidate records:",dict(count),flush=True)
print("All fields are raw source candidates; no frequencies or directions auto-generated.",flush=True)
