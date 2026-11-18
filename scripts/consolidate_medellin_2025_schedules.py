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
  source_qc_level=qc,source_url=url,period_clock_boundaries=("PVE_before_04:30_after_20:30_visually_verified_in_original_2025_Gaceta;PP_PVM_unknown" if act in {"202550076150","202550076162","202550079848","202550079865","202550076168","202550088689"} else "PP_PVE_PVM_boundaries_not_verified_for_this_act"),
  current_2026_effectivity_verified="no",gtfs_generation_approved="no",interpretation_note=note))
with ASTREA.open(newline="",encoding="utf-8-sig") as f:
 rows=list(csv.DictReader(f))
assert len(rows)==86,len(rows)
for r in rows:
 hours=clean(r["hours_table_2"] or r["hours_table_4"])
 # Original merged Metrosan return rows encode missing clock cells as delimiters.
 # Empty components do NOT establish no-service or new separate times.
 fields=[] if not hours or not any(x.strip() for x in hours.split("|")) else hours.split("|")
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
# Separate actionable source exceptions from ordinary complete timetable rows.
exceptions=[]
for r in records:
 reason=[]
 if r["max_interval_status"] in ("invalid_or_zero_interval_source","partially_not_operating_interval_periods"):
  reason.append("zero_or_nonoperating_interval_source_cell")
 if r["window_status"]=="published_no_service":
  reason.append("explicit_no_service_day")
 if r["window_status"]=="fixed_departure_schedule_only":
  reason.append("fixed_departures_not_headways")
 if r["number_of_daily_services"]:
  reason.append("daily_service_count_not_headway")
 if r["window_status"]=="no_published_window_in_source_table" and not r["number_of_daily_services"]:
  reason.append("no_independent_service_window_or_paired_direction")
 if r["service_condition"].lower().find("suspension of sitva")>=0:
  reason.append("temporary_rail_suspension_contingency_only")
 if reason:exceptions.append({**r,"source_exception_tags":";".join(reason)})
out=ROOT/"2025_official_schedule_exceptions.csv"
with out.open("w",newline="",encoding="utf-8") as file:
 w=csv.DictWriter(file,fieldnames=FIELDS+["source_exception_tags"])
 w.writeheader();w.writerows(exceptions)
print("Exceptions",len(exceptions),"source-day records",dict(Counter(tag for r in exceptions for tag in r["source_exception_tags"].split(";"))))
# Determine only the part of each published service window that overlaps
# the explicitly defined PVE clock hours (before 04:30 / after 20:30).
# The PDF gives no departure slots, terminal offsets or PP/PVM boundaries.
PVE_ACT_PAGES={"202550076150":"5671:p13","202550076162":"5671:p27",
               "202550079848":"5671:p40","202550079865":"5671:p57",
               "202550076168":"5667:p56","202550088689":"5694:official_ASTREA_Art7"}
pve=[]
def minutes(clock):
 h,m=map(int,clock.split(":"));return h*60+m
def clock(n):return f"{n//60:02d}:{n%60:02d}"
for r in records:
 if r["resolution"] not in PVE_ACT_PAGES:continue
 if r["window_status"]!="published_operating_span":continue
 if r["max_interval_status"] not in ("three_maximum_interval_periods","partially_not_operating_interval_periods","invalid_or_zero_interval_source"):continue
 vmax=r["maximum_extreme_valley_minutes"]
 if not vmax:continue
 a=minutes(r["published_window_start"]);b=minutes(r["published_window_end"])
 if b<=a:continue  # no guess for midnight-spanning services
 for lower,upper,period in [(0,270,"PVE_before_04_30"),(1230,1440,"PVE_after_20_30")]:
  start,end=max(lower,a),min(upper,b)
  if end<=start:continue
  pve.append(dict(resolution=r["resolution"],legal_route_code=r["legal_route_code"],gtpc=r["gtpc"],route_name=r["route_name"],day_type=r["day_type"],period=period,
   overlap_start=clock(start),overlap_end=clock(end),published_maximum_headway_minutes=vmax,original_period_definition_page=PVE_ACT_PAGES[r["resolution"]],
   source_url=r["source_url"],legally_defined_interval_boundary="before_04:30_after_20:30;exact_boundary_inclusivity_not_specified",
   current_effectivity_verified="no",gtfs_frequency_approved="no",
   caution="Derived intersection of a generic legal service span and PVE; not exact terminal departure windows or independent direction frequency"))
PVEFIELDS=["resolution","legal_route_code","gtpc","route_name","day_type","period","overlap_start","overlap_end",
"published_maximum_headway_minutes","original_period_definition_page","source_url",
"legally_defined_interval_boundary","current_effectivity_verified","gtfs_frequency_approved","caution"]
pvefile=ROOT/"2025_official_extreme_valley_windows_derived.csv"
with pvefile.open("w",newline="",encoding="utf8") as f:
 w=csv.DictWriter(f,fieldnames=PVEFIELDS);w.writeheader();w.writerows(pve)
assert pve and not any(x["gtfs_frequency_approved"]=="yes" for x in pve)
print("PVE source-clipped time segments:",len(pve),dict(Counter(x["resolution"] for x in pve)))

