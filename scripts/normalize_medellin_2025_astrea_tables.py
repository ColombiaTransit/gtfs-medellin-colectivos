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
fields=["act_number","gtpc","user_route_code","route_type","route_name","route_table_number","hours_table_2","hours_table_4","hours_table_5","interval_weekday","interval_saturday","interval_sunday_holiday","source_QA","gtfs_import"]
for r in D.values():
 r.update(source_QA="official_astrea_html_extracted_not_visually_accepted",gtfs_import="no")
out.parent.mkdir(parents=True,exist_ok=True)
with out.open("w",newline="",encoding="utf-8") as f:
 w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore")
 w.writeheader()
 w.writerows(sorted(D.values(),key=lambda x:(x["act_number"],x["gtpc"],x.get("user_route_code",""))))
from collections import Counter
count=Counter(r["act_number"] for r in D.values())
assert count=={"202550076150":6,"202550076162":28,"202550079848":16,"202550079865":34},count
print("Saved",len(D),"official ASTREA route/direction candidate records:",dict(count),flush=True)
print("All fields are raw source candidates; no frequencies or directions auto-generated.",flush=True)
