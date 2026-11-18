#!/usr/bin/env python3
"""Resolution-first coverage audit for 252 archived Medellin ArcGIS route IDs.

Precedence: explicit latest official act > 2025 official act > direct operator
schedule > provisional external schedule > historical reference. Candidate
identity never silently promotes to a confirmed current route or GTFS trip.
"""
from __future__ import annotations
import csv, json, re
from collections import Counter, defaultdict
from pathlib import Path
import yaml

BASE=Path("data/resolutions")
ROUTES=Path("data/medellin/routes.csv")
SUMMARY=BASE/"medellin_252_route_schedule_coverage.csv"
DETAIL=BASE/"medellin_252_route_schedule_daytypes.csv"
BACKLOG=BASE/"medellin_missing_frequency_windows_worklist.csv"
DAYS=("weekday","saturday","sunday_holiday")
def read(path):
 with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def value(row,key):return (row.get(key) or "").strip()
def parts(v):return [x.strip() for x in (v or "").split(";") if x.strip()]
def clock(s):return re.fullmatch(r"\d{1,2}:\d{2}",s or "") is not None
def source_record(kind,code,act,day,start="",end="",peak="",pve="",pvm="",headway="",fixed="",daily="",confidence="",link="",condition="",direction="",source_id=""):
 return dict(source_tier=kind,source_route_code=code,source_act=act,day_type=day,start=start,end=end,peak=peak,pve=pve,pvm=pvm,headway=headway,fixed=fixed,daily=daily,source_confidence=confidence,source_url=link,condition=condition,direction=direction,source_id=source_id)
routes=read(ROUTES)
identities={}
for r in routes:
 rid=value(r,"id_ruta")
 if rid in identities:
  assert identities[rid]["codigo_ruta"]==r["codigo_ruta"]
 else:identities[rid]=r
assert len(identities)==252, len(identities)
evidence=defaultdict(list)
weak=defaultdict(list)
# Source A: reviewed official 2025 window/daytype table; never assume each
# direction can run independently, and do not use any inferred schedule as
# current legal authorization.
official=read(BASE/"2025_official_service_windows_and_headways_by_day.csv")
by_key=defaultdict(list)
for r in official:
 by_key[(value(r,"resolution"),value(r,"legal_route_code"))].append(r)
cross=read(BASE/"2025_legal_to_arcgis_consolidated_register.csv")
candidates=defaultdict(set)
for r in cross:
 key=(value(r,"resolution"),value(r,"legal_route_code"))
 for rid in parts(value(r,"historical_arcgis_id_candidates")):
  if rid not in identities:continue
  candidates[key].add(rid)
for r in cross:
 key=(value(r,"resolution"),value(r,"legal_route_code"))
 ids=candidates.get(key,set())
 if len(ids)!=1:continue
 rid=next(iter(ids))
 status=value(r,"crosswalk_confidence")
 if status in ("no_defensible_arcgis_one_to_one","ambiguous_multiple_arcgis_variants","matching_code_conflicting_route_name","deferred_existing_trsc_crosswalk_issue_18"):
  continue
 # Do not duplicate merged GTPC return direction for same official service.
 for q in by_key.get(key,[]):
  new=source_record("official_2025",key[1],key[0],value(q,"day_type"),value(q,"published_window_start"),value(q,"published_window_end"),
   value(q,"maximum_peak_minutes"),value(q,"maximum_extreme_valley_minutes"),value(q,"maximum_midday_valley_minutes"),
   fixed=value(q,"fixed_departures_raw"),daily=value(q,"number_of_daily_services"),
   confidence="candidate_legal_to_legacy_identity_"+status,
   link=value(q,"source_url"),condition=value(q,"service_condition"),
   source_id=key[0]+":"+key[1])
  if new not in evidence[rid]:evidence[rid].append(new)
# Source B: Palenque. The 2025 legal numbering does not generally align 1:1
# with the archival GIS list; separate ambiguous records from one-to-one leads.
pal=read(BASE/"palenque_2025_old_arcgis_to_new_legal_route_candidates.csv")
for item in pal:
 rid=value(item,"arcgis_id_ruta")
 opts=parts(value(item,"2025_legal_route_code_candidates"))
 conf=value(item,"mapping_confidence")
 if not opts or rid not in identities:continue
 if len(opts)!=1:
  weak[rid].append("Palenque_2025_candidates="+value(item,"2025_legal_route_code_candidates"))
  continue
 key=("202550088689",opts[0])
 for q in by_key.get(key,[]):
  evidence[rid].append(source_record("official_2025",opts[0],key[0],value(q,"day_type"),
   value(q,"published_window_start"),value(q,"published_window_end"),value(q,"maximum_peak_minutes"),
   value(q,"maximum_extreme_valley_minutes"),value(q,"maximum_midday_valley_minutes"),
   fixed=value(q,"fixed_departures_raw"),daily=value(q,"number_of_daily_services"),
   confidence="candidate_old_new_Palenque_"+conf,link=value(q,"source_url"),
   condition=value(q,"service_condition"),source_id=key[0]+":"+opts[0]))
# Source C: official 2026 act; new supersedes old field-by-field.
recent=read(BASE/"route_229i_2026_official_intervals.csv")
for q in recent:
 for rid,r in identities.items():
  if rid!="90377":continue
  for day in DAYS:
   period=day
   evidence[rid].append(source_record("official_2026",value(q,"user_route_code"),value(q,"resolution"),day,
    value(q,f"{period}_first"),value(q,f"{period}_last"),
    value(q,f"{period}_max_peak_min"),value(q,f"{period}_max_extreme_valley_min"),value(q,f"{period}_max_midday_valley_min"),
    confidence="legal_229i_2026_legacy_90377_identity_candidate",link=value(q,"source_url"),
    condition="ONE shared service; 2024 act repealed; 2026 GTPC paired direction not extra frequency",source_id="202650039611:229-i"))
# Direct operator window published for 6F, variant-only not independent schedule.
mallat=read(BASE/"cootransmallat_2026_operator_hours_105_106_arcgis_variants.csv")
for q in mallat:
 rid=value(q,"arcgis_id_ruta")
 if rid not in identities:continue
 for day in DAYS:
  evidence[rid].append(source_record("operator_family_window",value(q,"arcgis_code"),"cootransmallat_website",day,
   value(q,"published_family_service_start"),value(q,"published_family_service_end"),
   confidence="only_origin_family_not_specific_route_variant",link=value(q,"source_url"),
   condition="Minorista destination replaced by Bolivia after 18:00; variants NOT independent full-day services",
   source_id="cootransmallat:"+value(q,"operator_published_route_family")))
# Previously collected original operator 6G schedules; route number to GIS
# mapping provisional and some weekend headways are inferred in source.
trans=yaml.safe_load(Path("data/transacoop_route_mapping.yml").read_text(encoding="utf-8"))
for q in trans.get("routes",[]):
 rid=str(q["id_ruta"])
 if rid not in identities:continue
 for day,key in (("weekday","lunes_sabado"),("saturday","lunes_sabado"),("sunday_holiday","domingo")):
  start=trans.get("hours",{}).get(key,{}).get("inicio","")[:5]
  end=trans.get("hours",{}).get(key,{}).get("fin","")[:5]
  hw=q.get("headway_min",{}).get(key)
  note="Branch ID by website order is provisional. Some website headways are derived approximations in mapping file."
  evidence[rid].append(source_record("operator_with_caveats",str(q.get("website_branch","")),"transacoop_original_website",day,start,end,
   headway=str(hw) if hw else "",confidence=value(q,"match_confidence") if isinstance(q,dict) else "provisional",
   link="https://trasancoop.com/",condition=note,source_id="transacoop_website:"+str(q.get("website_branch",""))))
# Existing TRSC photo transcriptions are a separate original-operator evidence
# library. Do not pretend that photos with provisional identity are exact
# departures for a current legal GTPC.
photo=json.loads(Path("data/trsc_schedule_photos.json").read_text(encoding="utf-8"))
trsc=yaml.safe_load(Path("data/trsc_route_mapping.yml").read_text(encoding="utf-8"))
for q in trsc.get("routes",[]):
 rid=str(q["id_ruta"])
 if rid not in identities:continue
 photo_id=q.get("schedule_photo")
 if not photo_id:continue
 entry=photo.get(photo_id,{})
 if not isinstance(entry,dict) or not entry.get("transcribed"):continue
 departures=entry.get("times") or []
 if not departures:continue
 for day in DAYS:
  evidence[rid].append(source_record("operator_photo_unassigned_days",str(q.get("codigo","")),"trsc_website_photo",day,
   fixed=";".join(map(str,departures)),confidence="schedule_identity_"+str(q.get("schedule_confidence","provisional")),
   link="https://trscsas.com/horarios/",
   condition="PHOTO TIMES ARE UNASSIGNED TO DAY TYPES / DIRECTION HERE; existing builder and photo QA must be consulted. Not approved as full-day schedule.",
   source_id="trsc_photo:"+photo_id))
# Ancillary external source only where official/owner frequency+span absent.
external=read(BASE/"2026_moovit_additional_operator_schedules_review.csv")
for q in external:
 rid=value(q,"arcgis_candidate_id")
 if rid not in identities:continue
 scope=value(q,"day_scope")
 applicable=(DAYS if scope in ("monday_sunday","all_days") else
 ("weekday","saturday") if scope in ("monday_saturday","monday_friday") else
 ("saturday",) if scope=="saturday" else
 ("sunday_holiday",) if scope=="sunday" else ())
 for day in applicable:
  evidence[rid].append(source_record("external_provisional",value(q,"route_code_public"),"moovit",day,
   value(q,"first_reported") if value(q,"last_reported") else "",
   value(q,"last_reported"),headway=value(q,"headway_min"),
   confidence=value(q,"arcgis_identity_confidence"),link=value(q,"source_url"),
   condition=value(q,"notes"),direction=value(q,"direction"),source_id="moovit:"+value(q,"route_code_public")+":"+value(q,"direction")))
# Exact 098-7 has stronger specificity than family headway but direction/old
# ArcGIS ID still needs verification.
exact=read(BASE/"transacoop_098_7_2026_moovit_explicit_departures.csv")
times=sorted({value(r,"published_departure_at_origin") for r in exact})
assert len(times)==19 and all(clock(t) for t in times)
for day in DAYS:
 evidence["90263"].append(source_record("external_exact_departures","098-7","moovit_2026",day,
  fixed=";".join(times),confidence="public_branch_to_old_arcgis_not_verified",link=value(exact[0],"source_url"),
  condition="19 exact origin departures 03:30-21:30; one direction; public listing says Diariamente but holiday status unknown",
  direction="Santa_Elena_to_Medellin",source_id="098-7_exact"))
# Operator's official 2025 pilot is a specific 178 service, NOT a match
# to 90374's 172-178 FUSION; record as reference only.
weak["90374"].append("2025_Cootrabel_178_pilot_is_not_proven_identical_to_legacy_172-178_FUSION")
# Do not copy the Coopetransa 069 main schedule to the 'Ramal'.
coop=read(BASE/"coopetransa_069_2023_operator_report_legal_fiche.csv")
for q in coop:
 rid=value(q,"arcgis_id_candidate")
 if rid not in identities:continue
 if value(q,"route_variant")!="main":
  weak[rid].append("069_La_Cima_branch_requires_separate_dispatch_data")
  continue
 for day,col in (("weekday","weekday"),("saturday","saturday"),("sunday_holiday","sunday")):
  evidence[rid].append(source_record("operator_reproduced_legal_fiche",value(q,"printed_route"),value(q,"legal_act"),day,
   value(q,"general_service_start"),value(q,"general_service_end"),
   daily=value(q,f"{col}_day_service_count"),
   confidence="operator_2023_historical_fiche_not_current_2026",link=value(q,"source_url"),
   condition="DIA/HMD are service counts, not minute headways; avoid duplicating with TRESCOOP partners",
   source_id="coopetransa_fiche_069"))
# Ranking is intentional; official numerical content takes precedence over
# third-party content, while missing official fields may use operator info.
TIERS=["official_2026","official_2025","operator_reproduced_legal_fiche",
       "operator_with_caveats","operator_family_window","operator_photo_unassigned_days",
       "external_exact_departures","external_provisional"]
tier_index={k:i for i,k in enumerate(TIERS)}
detail=[]
summ=[]
work=[]
for rid,r in sorted(identities.items(),key=lambda x:int(x[0])):
 ev=evidence[rid]
 day_summary=[]
 for day in DAYS:
  sources=[x for x in ev if x["day_type"]==day]
  sources.sort(key=lambda x:tier_index[x["source_tier"]])
  # Fields chosen separately: an old official table may have a span but no
  # source headway; operator may legitimately fill the missing field.
  def choose(check):
   return next((x for x in sources if check(x)),None)
  window=choose(lambda x: clock(x["start"]) and clock(x["end"]))
  headway=choose(lambda x: all(x[k].isdigit() and int(x[k])>0 for k in ("peak","pve","pvm")))
  scalar=choose(lambda x: x["headway"].isdigit() and int(x["headway"])>0)
  exacts=choose(lambda x: x["fixed"] and x["source_tier"]=="external_exact_departures")
  daily=choose(lambda x: x["daily"].isdigit() and int(x["daily"])>0)
  ownphoto=choose(lambda x: x["fixed"] and x["source_tier"]=="operator_photo_unassigned_days")
  no_service=choose(lambda x:x["source_tier"]=="official_2025" and x["condition"].lower().find("no opera")>=0)
  slots=[x for x in (window,headway,scalar,exacts,daily,ownphoto) if x]
  statuses=[]
  if headway: statuses.append("official_period_headways" if headway["source_tier"].startswith("official") else "period_headways")
  elif scalar: statuses.append("published_scalar_headway")
  elif daily: statuses.append("daily_count_not_headway")
  elif exacts: statuses.append("external_fixed_departures")
  elif ownphoto: statuses.append("operator_photo_unverified_day_scope")
  else: statuses.append("missing_frequency")
  if window:statuses.append("operating_window")
  else:statuses.append("missing_window")
  if any(x["source_tier"].startswith("official") for x in slots):grade="official_candidate"
  elif any(x["source_tier"].startswith("operator") for x in slots):grade="operator_reference"
  elif slots:grade="external_reference"
  else:grade="missing"
  profile=dict(arcgis_id_ruta=rid,arcgis_route_code=value(r,"codigo_ruta"),operator=value(r,"empresa"),
   day_type=day,coverage_grade=grade,frequency_status=statuses[0],window_status=statuses[1],
   selected_window_start=window["start"] if window else "",selected_window_end=window["end"] if window else "",
   window_source_tier=window["source_tier"] if window else "",headway_PP=headway["peak"] if headway else "",
   headway_PVE=headway["pve"] if headway else "",headway_PVM=headway["pvm"] if headway else "",
   published_flat_headway=scalar["headway"] if scalar else "",
   headway_source_tier=headway["source_tier"] if headway else scalar["source_tier"] if scalar else "",
   count_per_day=daily["daily"] if daily else "",
   exact_departures_count=len(exacts["fixed"].split(";")) if exacts else 0,
   operator_photo_available="yes_unverified_day_direction" if ownphoto else "no",
   source_route_codes=";".join(sorted({x["source_route_code"] for x in slots if x["source_route_code"]})),
   selected_sources=";".join(sorted({x["source_id"] for x in slots if x["source_id"]})),
   mapping_status="candidate_only" if slots else "none",
   notes="; ".join(sorted(set(x["condition"] for x in slots if x["condition"])))[:650],
   gtfs_automatic_import="no")
  detail.append(profile)
  day_summary.append(profile)
 types={q["coverage_grade"] for q in day_summary}
 legal_days=sum(q["coverage_grade"]=="official_candidate" for q in day_summary)
 full=sum(q["window_status"]=="operating_window" and q["frequency_status"] in ("official_period_headways","published_scalar_headway","period_headways") for q in day_summary)
 missingfreq=sum(q["frequency_status"]=="missing_frequency" for q in day_summary)
 missingwin=sum(q["window_status"]=="missing_window" for q in day_summary)
 if legal_days:
  status="official_route_candidate" if full else "official_partial"
 elif "operator_reference" in types:
  status="operator_only_or_partial"
 elif "external_reference" in types:
  status="external_only_or_partial"
 else:status="no_usable_recent_timetable"
 # An ambiguous mapping is not an independently confirmed operating schedule
 # even when all three time tables exist at the candidate source level.
 source_summary=";".join(sorted({q["selected_sources"] for q in day_summary if q["selected_sources"]}))
 entry=dict(arcgis_id_ruta=rid,arcgis_code=value(r,"codigo_ruta"),arcgis_route_name=value(r,"nombre_ruta"),
  operator=value(r,"empresa"),system=value(r,"sistema"),coverage_status=status,
  official_source_daytypes=legal_days,days_with_window_and_interval=full,
  missing_frequency_daytypes=missingfreq,missing_operating_window_daytypes=missingwin,
  candidate_source_refs=source_summary[:900],weak_or_ambiguous_identity_notes=";".join(weak[rid]),
  identity_verification="unverified_source_candidate" if ev else "no_current_source_link",
  production_gtfs_approved="no")
 summ.append(entry)
 reason=[]
 if not ev:reason.append("no_new_timetable_source_link")
 if missingfreq:reason.append("frequency_gap_"+str(missingfreq)+"_daytypes")
 if missingwin:reason.append("window_gap_"+str(missingwin)+"_daytypes")
 if weak[rid]:reason.append("ambiguous_legal_to_legacy_mapping")
 if status=="external_only_or_partial":reason.append("validate_secondary_source")
 if any(x["source_tier"]=="operator_photo_unassigned_days" for x in ev):
  reason.append("reuse_existing_TRSC_photo_day_direction_QA")
 if reason:
  work.append(dict(arcgis_id_ruta=rid,arcgis_code=value(r,"codigo_ruta"),
   operator=value(r,"empresa"),priority="P1_official_candidate" if legal_days else "P2_secondary_partial" if ev else "P3_no_new_source",
   missing_items=";".join(reason),source_evidence=source_summary[:600],
   suggested_action="Resolve matched route/family direction and missing days; prioritize original official schedule, reuse operator website, third-party only for true gaps.",
   gtfs_automatic_import="no"))
def write(path,rows):
 with path.open("w",encoding="utf8",newline="") as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]))
  writer.writeheader();writer.writerows(rows)
write(SUMMARY,summ);write(DETAIL,detail);write(BACKLOG,work)
assert len(summ)==252 and len(detail)==756
print("Route coverage",dict(Counter(x["coverage_status"] for x in summ)))
print("Official candidate days",sum(x["official_source_daytypes"] for x in summ))
print("Full window plus interval day records",sum(x["days_with_window_and_interval"] for x in summ))
print("Gaps",len(work),"routes; official/secondary/missing priority",dict(Counter(x["priority"] for x in work)))
print("Outputs",SUMMARY,DETAIL,BACKLOG)
