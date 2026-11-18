#!/usr/bin/env python3
"""Distinguish genuinely missing data from historical and unlinked official sources.

Does not assign 2015 service intervals to today's routes without route/source QA.
"""
import csv
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path("data/resolutions")
MAIN=ROOT/"medellin_252_route_schedule_coverage.csv"
HIST=ROOT/"2015_arcgis_route_link_status.csv"
OFFICIAL=ROOT/"2025_official_service_windows_and_headways_by_day.csv"
CROSS=ROOT/"2025_legal_to_arcgis_consolidated_register.csv"
PAL=ROOT/"palenque_2025_old_arcgis_to_new_legal_route_candidates.csv"
ENRICH=ROOT/"medellin_252_coverage_with_historical_fallback.csv"
UNLINK=ROOT/"medellin_unlinked_official_2025_schedule_candidates.csv"
def read(p):
 with p.open(encoding="utf8-sig",newline="") as f:return list(csv.DictReader(f))
def v(r,k):return (r.get(k) or "").strip()
base=read(MAIN);historic={v(x,"arcgis_id_ruta"):x for x in read(HIST)}
cross=read(CROSS);pal=read(PAL);off=read(OFFICIAL)
assert len(base)==252 and len(historic)==252
mapped=defaultdict(set)
qual=defaultdict(list)
for r in cross:
 key=(v(r,"resolution"),v(r,"legal_route_code"))
 for rid in v(r,"historical_arcgis_id_candidates").split(";"):
  if rid:
   mapped[key].add(rid)
   qual[key].append(v(r,"crosswalk_confidence"))
for r in pal:
 key=("202550088689",v(r,"2025_legal_route_code_candidates"))
 if not key[1]:continue
 for code in key[1].split(";"):
  if code: mapped[(key[0],code)].add(v(r,"arcgis_id_ruta"))
  qual[(key[0],code)].append(v(r,"mapping_confidence"))
# 2026 229-i maps as a separate latest legal act to old snapshot ID 90377.
mapped[("202650039611","229-i")].add("90377")
keys=defaultdict(list)
for r in off:
 keys[(v(r,"resolution"),v(r,"legal_route_code"))].append(r)
# Note source categories: official exists independent of ArcGIS one-to-one.
unlinked=[]
for key,rows in sorted(keys.items()):
 ids=sorted(mapped.get(key,set()))
 h=headway=sum(all(v(r,field).isdigit() and int(v(r,field))>0 for field in
      ("maximum_peak_minutes","maximum_extreme_valley_minutes","maximum_midday_valley_minutes")) for r in rows)
 w=sum(bool(v(r,"published_window_start") and v(r,"published_window_end")) for r in rows)
 fixed=sum(bool(v(r,"fixed_departures_raw")) for r in rows)
 daily=sum(bool(v(r,"number_of_daily_services")) for r in rows)
 if key[0]=="202550076168" and key[1]=="313":continue
 if len(ids)==1 and key[0]!="202550079865" and not any("ambiguous" in s for s in qual[key]):
  continue
 unlinked.append(dict(resolution=key[0],legal_code=key[1],route_title=v(rows[0],"route_name"),
  candidate_old_arcgis_ids=";".join(ids),candidate_count=len(ids),source_daytypes=len(rows),
  daytypes_with_period_headways=headway,daytypes_with_source_window=w,
  daytypes_with_fixed_departures=fixed,daytypes_with_daily_counts=daily,
  route_mapping_status="no_candidate" if not ids else "requires_variant_or_legal_identity_qa",
  source_url=v(rows[0],"source_url"),operator_schedule_reuse_note="Existing TRSC operator photo library must be reused, not scraped again" if key[0]=="202550079865" else "Do not discard original official service data merely because old ArcGIS code differs",
  auto_gtfs_import="no"))
out=[]
for r in base:
 rid=v(r,"arcgis_id_ruta")
 h=historic[rid]
 status=v(h,"best_historical_link_status")
 fiche=v(h,"historical_fiche_refs")
 has=bool(fiche)
 # distinct: historic provenance is real but is not approved CURRENT frequency
 new=dict(r)
 new.update(historical_2015_fiche_refs=fiche,
   historical_2015_match_status=status,
   historical_2015_source_available="yes" if has else "no",
   historical_2015_is_current_frequency="no",
   next_lookup_priority=("source_2025_already_present_check_only_missing_daytypes" if r["coverage_status"].startswith("official")
     else "operator_source_already_present_reconcile_variant" if r["coverage_status"]=="operator_only_or_partial"
     else "only_missing_days_after_current_external_schedule" if r["coverage_status"]=="external_only_or_partial"
     else "first_resolve_new_2025_code_to_old_ArcGIS" if v(r,"operator") in {"Palenque Robledal","Rápido San Cristóbal","Metrosan","Transporte Medellín Castilla"}
     else "historic_2015_fiche_usable_only_as_provisional_fallback_after_amendment_check" if has
     else "new_route_specific_operator_source_needed"))
 out.append(new)
assert len(out)==252
for path,rows in [(ENRICH,out),(UNLINK,unlinked)]:
 assert rows
 with path.open("w",encoding="utf8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print("Coverage",dict(Counter(x["coverage_status"] for x in out)))
print("Historic fiche references",sum(x["historical_2015_source_available"]=="yes" for x in out))
print("Unlinked or ambiguous official 2025 legal route records",len(unlinked))
print("Next lookup buckets",dict(Counter(x["next_lookup_priority"] for x in out)))
