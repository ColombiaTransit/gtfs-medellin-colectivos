#!/usr/bin/env python3
"""Build research-only PROVISIONAL PP/PVM/PVE intervals using observed regional peak clocks.
This is an editable operating model, never an official 2025 TPC period definition.
The official route/day type maximum minutes and route service windows are reused.
"""
import csv
from pathlib import Path
from collections import Counter
ROOT=Path("data/resolutions")
IN=ROOT/"2025_official_service_windows_and_headways_by_day.csv"
OUT=ROOT/"2025_provisional_pp_pvm_operating_intervals.csv"
# Similar system (Metro de Medellin) peak schedules, from a source discussing
# Metro MASS TRANSIT regulation (not the separate 2025 colectivo operating permits).
MODEL=[
 ("PVE","00:00","04:30"),
 ("PVM","04:30","06:00"),
 ("PP","06:00","08:00"),
 ("PVM","08:00","16:00"),
 ("PP","16:00","20:00"),
 ("PVM","20:00","20:30"),
 ("PVE","20:30","24:00"),
]
MODEL_SOURCE="https://es.scribd.com/document/466710173/SUBSECCIO-N-2"
OFFICIAL_MUNI_ALTERNATIVE="https://www.medellin.gov.co/es/wp-content/uploads/2024/10/Gaceta-Oficial-PD-5387.pdf"
FIELDS=["resolution","legal_route_code","gtpc","route_name","day_type","period","start_time","end_time","provisional_target_headway_minutes","official_maximum_headway_minutes","source_window_start","source_window_end","source_window_status","method","scenario","clock_model_evidence_url","alternative_peak_clock_source","source_legal_act","confidence","operating_day_scope_note","auto_gtfs_import","qa_note"]
def minute(s):
 h,m=map(int,s.split(":"));return h*60+m
def hhmm(n):return f"{n//60:02d}:{n%60:02d}"
rows=list(csv.DictReader(IN.open(encoding="utf8",newline="")))
assert len(rows)==321
result=[]
skipped=Counter()
for r in rows:
 if r["window_status"]!="published_operating_span":
  skipped[r["window_status"]]+=1;continue
 if r["number_of_daily_services"] or r["fixed_departures_raw"]:
  skipped["not_minute_frequency_service"]+=1;continue
 start,end=minute(r["published_window_start"]),minute(r["published_window_end"])
 if end<=start:skipped["overnight_or_nonpositive_span"]+=1;continue
 vals={"PP":r["maximum_peak_minutes"],"PVM":r["maximum_midday_valley_minutes"],"PVE":r["maximum_extreme_valley_minutes"]}
 for period,a,b in MODEL:
  headway=vals[period]
  st,en=max(start,minute(a)),min(end,minute(b))
  if st>=en:continue
  if not headway or not headway.isdigit() or int(headway)<=0:
   skipped["unusable_source_headway_"+period]+=1;continue
  # Published figures are maximum dispatch gaps, not exact observed headways.
  # The model uses that maximum as a provisional target, pending timetable QA.
  result.append(dict(
   resolution=r["resolution"],legal_route_code=r["legal_route_code"],gtpc=r["gtpc"],route_name=r["route_name"],day_type=r["day_type"],
   period=period,start_time=hhmm(st),end_time=hhmm(en),
   provisional_target_headway_minutes=headway,official_maximum_headway_minutes=headway,
   source_window_start=r["published_window_start"],source_window_end=r["published_window_end"],
   source_window_status=r["window_status"],method="published_maximum_used_as_provisional_regular_headway",
   scenario="proxy_metro_peak_06_08_16_20_with_city_2025_extreme_valley",
   clock_model_evidence_url=MODEL_SOURCE,alternative_peak_clock_source=OFFICIAL_MUNI_ALTERNATIVE,
   source_legal_act=r["source_url"],confidence="low_nonTPC_period_boundary_proxy",
   operating_day_scope_note="weekday_saturday_sunday_holiday_columns_are_legal_source_categories_not_independently_observed_traffic_peaks",
   auto_gtfs_import="no",
   qa_note="Research-only schedule approximation; no exact terminal departure offsets; joint services once and paired direction cells without headway omitted."
  ))
assert result
with OUT.open("w",newline="",encoding="utf8") as file:
 w=csv.DictWriter(file,fieldnames=FIELDS);w.writeheader();w.writerows(result)
print("RESULT provisional spans",len(result),"source records",len(rows),"source periods",dict(Counter(x["period"] for x in result)),"skipped",dict(skipped))
