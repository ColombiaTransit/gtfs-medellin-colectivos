#!/usr/bin/env python3
"""Normalize existing official 2025 bus service windows and dispatch constraints.

Research-only evidence register, NOT GTFS production input.
Never infer peak clock times, exact first-trip departures, or interval for blank cells.
"""
import csv
from collections import Counter
from pathlib import Path

ROOT=Path("data/resolutions")
OUTPUT=ROOT/"2025_official_service_windows_and_headways_by_day.csv"
ASTREA=ROOT/"2025_astrea_official_route_timetable_candidates.csv"
PALENQUE=ROOT/"palenque_2025_official_route_service_intervals.csv"
CIRCULAR=ROOT/"2025_circular_313_official_joint_service.csv"
DAYS=("weekday","saturday","sunday_holiday")
FIELDS=[
"resolution","legal_route_code","gtpc","route_name","source_dataset",
"day_type","published_window_start","published_window_end","window_status",
"maximum_peak_minutes","maximum_extreme_valley_minutes","maximum_midday_valley_minutes",
"max_interval_status","number_of_daily_services","fixed_departures_raw",
"service_condition","source_qc_level","source_url",
"period_clock_boundaries","current_2026_effectivity_verified",
"gtfs_generation_approved","interpretation_note"
]
records=[]
def add(r):
 assert set(r)==set(FIELDS), (set(FIELDS)-set(r),set(r)-set(FIELDS))
 records.append(r)
def clean(t):return (t or "").strip()
def hhmm(t):
 t=clean(t)
 if not t:return ""
 parts=t.split(":")
 if len(parts)!=2 or not all(p.isdigit() for p in parts):raise ValueError("Invalid source clock time "+repr(t))
 h,m=map(int,parts)
 if h>29 or m>59:raise ValueError("Out of range source time "+repr(t))
 return f"{h:02d}:{m:02d}"
def triple(raw, route):
 p=[clean(x) for x in raw.split("|")] if raw else []
 if not p:return ["","",""],"no_interval_row"
 if len(p)!=3: raise ValueError(f"Not a triple: {route}: {raw!r}")
 special={"no opera","n/a","-"}
 if all(x.lower() in special for x in p):return ["","",""],"not_operating_interval_row"
 if any(x.lower() in special for x in p):
  v=[x if x.isdecimal() and int(x)>0 else "" for x in p]
  return v,"partially_not_operating_interval_periods"
 if any(not x.isdecimal() or int(x)==0 for x in p):
  return [x if x.isdecimal() and int(x)>0 else "" for x in p],"invalid_or_zero_interval_source"
 return p,"three_maximum_interval_periods"
def make_base(act,code,gtpc,name,origin,day,window,interval,daily="",fixed="",condition="",qc="",url="",note=""):
 vals,status=triple(interval,code)
 start,end=window
 no_service=all(clean(x).lower() in {"no opera","n/a","-"} for x in window) and all(window)
 if no_service:
  winstatus="published_no_service"
 elif start and end:
  start,end=hhmm(start),hhmm(end)
  winstatus="published_operating_span"
 elif fixed:
  winstatus="fixed_departure_schedule_only"
 elif daily:
  winstatus="daily_service_count_only" if not (start or end) else "service_count_with_partial_window"
 else:
  winstatus="no_published_window_in_source_table"
 add(dict(resolution=act,legal_route_code=code,gtpc=gtpc,route_name=name,
  source_dataset=origin,day_type=day,published_window_start="" if no_service else start,
  published_window_end="" if no_service else end,window_status=winstatus,
  maximum_peak_minutes=vals[0],maximum_extreme_valley_minutes=vals[1],
  maximum_midday_valley_minutes=vals[2],max_interval_status=status,
  number_of_daily_services=daily,fixed_departures_raw=fixed,service_condition=condition,
  source_qc_level=qc,source_url=url,period_clock_boundaries="PVE_before_04:30_after_20:30_only_if_Circular313;PP_PVM_unknown",
  current_2026_effectivity_verified="no",gtfs_generation_approved="no",interpretation_note=note))
with ASTREA.open(newline="",encoding="utf-8-sig") as f:
 rows=list(csv.DictReader(f))
assert len(rows)==86,len(rows)
for r in rows:
 hours=clean(r["hours_table_2"] or r["hours_table_4"])
 fields=hours.split("|") if hours else []
 if fields and len(fields)!=6:raise ValueError(f"Unexpected six source hour fields {r['act_number']} {r['user_route_code']} {hours!r}")
 for i,day in enumerate(DAYS):
  start,end=(fields[i*2:i*2+2] if fields else ("",""))
  interval=r[{"weekday":"interval_weekday","saturday":"interval_saturday","sunday_holiday":"interval_sunday_holiday"}[day]]
  counts=clean(r[{"weekday":"weekday_services_per_day","saturday":"saturday_services_per_day","sunday_holiday":"sunday_holiday_services_per_day"}[day]])
  fixed=clean(r["fixed_departures_master_table"] or r["hours_table_5"])
  # Preserve original service-day scope; 'Domingo' alone does not establish
  # holiday departures and 'Lunes a Domingo' must not imply holiday service.
  lower=fixed.lower()
  if "lunes a viernes" in lower: active_days={"weekday"}
  elif "lunes a domingo" in lower: active_days={"weekday","saturday","sunday_holiday"}
  elif "domingo" in lower: active_days={"sunday_holiday"}
  else: active_days=set()
  fixedDay=fixed if day in active_days else ""
  make_base(r["act_number"],r["user_route_code"],r["gtpc"],r["route_name"],
   ASTREA.name,day,(start,end),interval,counts,fixedDay,
   ("Source fixed departures explicitly state "+fixed.split("|")[-2]+"; Sunday-only does not prove holiday operation" if fixedDay and "|" in fixed else "Verify printed operating-day scope" if fixedDay else ""),
   "ASTREA_html_structural_QA_partial_Gaceta_visual_spotcheck",
   {"202550076150":"https://www.medellin.gov.co/normograma/docs/astrea/docs/r_smmed_76150_2025.htm",
    "202550076162":"https://www.medellin.gov.co/normograma/docs/astrea/docs/r_smmed_76162_2025.htm",
    "202550079848":"https://www.medellin.gov.co/normograma/docs/astrea/docs/r_smmed_79848_2025.htm",
    "202550079865":"https://www.medellin.gov.co/normograma/docs/astrea/docs/r_smmed_79865_2025.htm"}[r["act_number"]],
   "Source values are per day/period maxima or counts, NOT complete trip schedules; no inferred GTFS trips.")
with PALENQUE.open(newline="",encoding="utf-8-sig") as f:
 pal=list(csv.DictReader(f))
assert len(pal)==20,len(pal)
for r in pal:
 for day in DAYS:
  start,end=r[f"{day}_first"],r[f"{day}_last"]
  head="|".join(r[f"{day}_max_{period}_min"] for period in ("peak","extreme_valley","midday_valley"))
  make_base(r["legal_resolution"],r["legal_user_route_code"],r["legal_gtpc_code"],r["route_name"],
   PALENQUE.name,day,(start,end),head,"","",r["operational_condition"],
   r["transcription_status"],r["official_source_url"],
   ("Temporary contingency service ONLY during suspension of SITVA Line J; not a normal daily route. " if r["service_scope"]=="temporary_continuity_only" else "")
   +"The same printed GTPC may be used by multiple route codes; keep code and conditions separate.")
with CIRCULAR.open(newline="",encoding="utf-8-sig") as f:
 circ=list(csv.DictReader(f))
assert len(circ)==1,len(circ)
for r in circ:
 for day in DAYS:
  start,end=r[f"{day}_first"],r[f"{day}_last"]
  prefix=day
  h="|".join(r[f"{prefix}_max_{period}_min"] for period in ("peak","extreme_valley","midday_valley"))
  make_base(r["resolution"],r["legal_route_code"],r["gtpc_north_to_south"]+";"+r["gtpc_south_to_north"],r["service_name"],
   CIRCULAR.name,day,(start,end),h,"","",
   "One coordinated four-operator service; the numeric source spans the two directions without repeating the headway.",
   "original_Gaceta_5667_pages_55_57_visually_checked",r["source_url"],
   "PVE before 04:30 and after 20:30; PP/PVM clock boundaries not yet established. One shared frequency table, never four operator copies.")
assert len(records)==(86+20+1)*3,len(records)
counts=Counter(r["max_interval_status"] for r in records)
with OUTPUT.open("w",newline="",encoding="utf-8") as f:
 w=csv.DictWriter(f,fieldnames=FIELDS)
 w.writeheader();w.writerows(records)
print("Wrote",OUTPUT,"records",len(records),"source family/day entities",len(records)//3)
print("Interval status:",dict(counts))
print("Window status:",dict(Counter(r["window_status"] for r in records)))
print("GTFS approvals:",Counter(r["gtfs_generation_approved"] for r in records))
