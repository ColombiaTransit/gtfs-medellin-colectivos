#!/usr/bin/env python3
"""Prioritize operator work only after matching all existing source registers."""
import csv
from collections import Counter,defaultdict
from pathlib import Path
R=Path("data/resolutions")
inp=R/"medellin_252_coverage_with_historical_fallback.csv"
out=R/"medellin_operator_frequency_gap_priorities.csv"
with inp.open(newline="",encoding="utf-8") as f: rows=list(csv.DictReader(f))
assert len(rows)==252
by=defaultdict(list)
for row in rows:by[row["operator"] or "UNKNOWN_OPERATOR_IN_ARCGIS"].append(row)
result=[]
for operator,rs in by.items():
 statuses=Counter(x["coverage_status"] for x in rs)
 buckets=Counter(x["next_lookup_priority"] for x in rs)
 route_ids=[x["arcgis_id_ruta"] for x in rs]
 missing=[x["arcgis_id_ruta"] for x in rs if x["coverage_status"]=="no_usable_recent_timetable"]
 result.append(dict(operator=operator,arcgis_route_ids=len(rs),
  official_2025_candidate=statuses["official_route_candidate"]+statuses["official_partial"],
  direct_operator_reference=statuses["operator_only_or_partial"],
  third_party_only=statuses["external_only_or_partial"],
  no_recent_timetable=statuses["no_usable_recent_timetable"],
  historical_2015_fiche_candidates=sum(x["historical_2015_source_available"]=="yes" for x in rs),
  first_reconcile_new_legal_code=buckets["first_resolve_new_2025_code_to_old_ArcGIS"],
  only_historical_fallback=buckets["historic_2015_fiche_usable_only_as_provisional_fallback_after_amendment_check"],
  genuinely_needs_new_route_source=buckets["new_route_specific_operator_source_needed"],
  no_recent_source_route_ids=";".join(missing),
  recommended_next_action=("NO external scraping: official source and windows are already linked" if not missing else
   "Resolve new official 2025 codes to old GIS; do not rescrape schedules" if buckets["first_resolve_new_2025_code_to_old_ArcGIS"]>=len(missing)/2 else
   "Reuse historical source as provisional after later-act check" if buckets["historic_2015_fiche_usable_only_as_provisional_fallback_after_amendment_check"]>=len(missing)/2 else
   "Find operator-specific route-level frequency and first/last departures ONLY for uncovered route IDs"),
  source_policy="official_first_then_existing_operator_then_provisional_2015_then_third_party",
  generator_changed="no"))
result.sort(key=lambda x:(-x["genuinely_needs_new_route_source"],-x["no_recent_timetable"],x["operator"]))
assert len(result)==33 and sum(x["operator"]!="UNKNOWN_OPERATOR_IN_ARCGIS" for x in result)==32
# The 33rd bucket is ArcGIS route 90375 with a blank enterprise name;
# never pretend it belongs to any of the 32 identified operators.
with out.open("w",newline="",encoding="utf-8") as f:
 w=csv.DictWriter(f,fieldnames=list(result[0]));w.writeheader();w.writerows(result)
print("Operator prioritization:",len(result)-1,"named operators + 1 unknown-operator route")
print("Top genuinely missing route sources:",[(x["operator"],x["genuinely_needs_new_route_source"]) for x in result[:12]])
print("Operator counts sum:",sum(x["arcgis_route_ids"] for x in result))
