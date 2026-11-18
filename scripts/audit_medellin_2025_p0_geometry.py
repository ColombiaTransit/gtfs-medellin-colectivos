#!/usr/bin/env python3
"""Audit existing ArcGIS geometries for legal-priority 2025 routes.

No new scraping, no shape edits and NO assumption of legal direction mapping.
Coordinates in repository GeoJSON are EPSG:9377 (metres), not GPS lon/lat.
"""
import csv
import json
from collections import defaultdict
from math import hypot
from pathlib import Path

SOURCE=Path("data/medellin/geojson/6_rutas_transporte_publico.geojson")
OUT=Path("data/resolutions/2025_p0_arcgis_direction_geometry_audit.csv")
TARGET={"90004":("313",20.65),"90006":("301",None),"90015":("315",None),"90124":("289",None)}
with SOURCE.open(encoding="utf-8") as file:
 source=json.load(file)
assert source["type"]=="FeatureCollection"
crs=source.get("crs",{}).get("properties",{}).get("name","")
if "9377" not in crs: raise ValueError(f"Expected EPSG:9377 metric source; got {crs!r}")

def paths_of(geometry):
 if not geometry:return []
 kind=geometry["type"];co=geometry["coordinates"]
 if kind=="LineString":return [co]
 if kind=="MultiLineString":return co
 return []

fields=["arcgis_id_ruta","arcgis_code","arcgis_route_name","arcgis_direction_label","geometry_source_crs","geometry_type","part_count","vertex_count","arcgis_shape_length_km","legal_reference_length_km","length_difference_km","length_difference_pct","first_vertex_x_9377","first_vertex_y_9377","last_vertex_x_9377","last_vertex_y_9377","length_within_10pct_of_legal","geometry_present","official_direction_match_verified","official_annex_geometry_match_verified","legal_2025_source","source_scope","qa_notes"]
# The layer's GeoJSON may not contain all presentation properties. Join the
# preserved route CSV instead of leaving the route code and name blank.
route_names={}
with Path("data/medellin/routes.csv").open(encoding="utf-8",newline="") as file:
 for record in csv.DictReader(file):
  route_names[(record["id_ruta"],record["recorrido"])]=record
found=defaultdict(list)
for f in source["features"]:
 p=f.get("properties") or {}
 rid=str(p.get("id_ruta") or p.get("ID_RUTA") or "").split(".")[0]
 if rid not in TARGET:continue
 legs=paths_of(f.get("geometry"))
 v=sum(len(path) for path in legs)
 length=sum(hypot(float(b[0])-float(a[0]),float(b[1])-float(a[1])) for path in legs for a,b in zip(path,path[1:]))/1000
 first=legs[0][0] if legs and legs[0] else [None,None]
 last=legs[-1][-1] if legs and legs[-1] else [None,None]
 ref=TARGET[rid][1]; diff=round(length-ref,3) if ref else None
 ratio=round(100*(length-ref)/ref,2) if ref else None
 old=route_names.get((rid,str(p.get("recorrido",""))),{})
 found[rid].append([
 rid,str(p.get("codigo_ruta") or old.get("codigo_ruta") or ""),str(p.get("nombre_ruta") or old.get("nombre_ruta") or ""),str(p.get("recorrido","")),crs,(f.get("geometry") or {}).get("type",""),len(legs),v,
 round(length,3),ref,diff,ratio,*first[:2],*last[:2],
 ("yes" if abs(length-ref)/ref<=.1 else "no") if ref else "not_applicable", "yes" if v>1 else "no", "no","no",
 ("202550076168" if rid=="90004" else "202550076174" if rid in ("90006","90015") else "202550076162"),
 "official route code candidate only; 2025 legal map overlay still needed",
 "ArcGIS projected length is measurable; exact endpoints are EPSG9377, not GPS coordinates; 313 legal 20.65km is PER DIRECTION; shape length is not formal legal correspondence"
 ])
if any(not found[id] for id in TARGET):raise ValueError(f"Missing target ArcGIS routes {[id for id in TARGET if not found[id]]}")
OUT.parent.mkdir(parents=True,exist_ok=True)
with OUT.open("w",newline="",encoding="utf-8") as file:
 w=csv.writer(file);w.writerow(fields)
 for id in TARGET:
  w.writerows(found[id])
print("Projected source CRS:",crs)
for id,rows in found.items():
 print("RESULT",id,len(rows),"source geometries",[(r[3],r[8],r[15]) for r in rows])
print("Wrote",OUT)
