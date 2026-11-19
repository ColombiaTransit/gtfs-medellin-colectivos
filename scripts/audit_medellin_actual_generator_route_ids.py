#!/usr/bin/env python3
"""Audit ACTUAL GTFS output feeds against 252 Medellin urbanas ArcGIS IDs.

Never count configured-only routes as published. Reads latest release and
Actions artifacts (if unexpired), and reports missing evidence explicitly.
"""
import csv
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import urllib.request
import zipfile

ROOT=Path("artifacts/medellin-generator-route-audit")
REPO=os.getenv("GITHUB_REPOSITORY","ColombiaTransit/gtfs-medellin-colectivos")
TOKEN=os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN","")
API=f"https://api.github.com/repos/{REPO}"
WORKFLOWS={
  "elpoblado":("build-elpoblado-flex.yml","gtfs-flex-elpoblado.zip"),
  "sotrames":("build-sotrames-flex.yml","gtfs-flex-sotrames.zip"),
  "taxmaya":("build-taxmaya-gtfs.yml","gtfs-taxmaya.zip"),
  "transacoop":("build-transacoop-gtfs.yml","gtfs-transacoop.zip"),
  "trsc":("build-trsc-gtfs.yml","gtfs-trsc.zip"),
}
MAIN_FEED="gtfs-medellin-colectivos.zip"
MAPS={
  "taxmaya":"data/taxmaya_route_mapping.yml",
  "transacoop":"data/transacoop_route_mapping.yml",
  "trsc":"data/trsc_route_mapping.yml",
}
MAX_BYTES=35*1024*1024

def get(url,accept=None):
    headers={"User-Agent":"ColombiaTransit-audit/1.0",
             "Accept":accept or "application/vnd.github+json"}
    if TOKEN:headers["Authorization"]="Bearer "+TOKEN
    req=urllib.request.Request(url,headers=headers)
    with urllib.request.urlopen(req,timeout=45) as r:
        b=r.read(MAX_BYTES+1)
        if len(b)>MAX_BYTES:raise ValueError("Download larger than permitted audit cap")
        return b
def api(path):
    return json.loads(get(API+path))
def extract_rows(blob,name):
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        candidates=[p for p in z.namelist() if p==name or p.endswith("/"+name)]
        if len(candidates)!=1:raise ValueError("Missing/ambiguous "+name+" in GTFS")
        return list(csv.DictReader(io.StringIO(z.read(candidates[0]).decode("utf-8-sig"))))
def inspect_feed(blob):
    routes=extract_rows(blob,"routes.txt")
    trips=extract_rows(blob,"trips.txt")
    rid={r["route_id"].strip() for r in routes}
    trips_by_id={}
    for t in trips:trips_by_id[t["route_id"]]=trips_by_id.get(t["route_id"],0)+1
    return [{"route_id":r["route_id"],"route_short_name":r.get("route_short_name",""),
             "route_long_name":r.get("route_long_name",""),
             "agency_id":r.get("agency_id",""),
             "trip_count":trips_by_id.get(r["route_id"],0)}
            for r in routes],dict(route_rows=len(routes),unique_route_ids=len(rid),
                                  routes_with_trips=sum(bool(trips_by_id.get(x)) for x in rid),
                                  routes_without_trips=sum(not trips_by_id.get(x) for x in rid),
                                  trip_rows=len(trips))
def load_archive_candidate(payload,expected):
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        names=z.namelist()
        if "routes.txt" in names and "trips.txt" in names:
            return payload
        match=[n for n in names if n==expected or n.endswith("/"+expected)]
        if len(match)==1:
            return z.read(match[0])
        raise ValueError("No expected GTFS ZIP found in Actions artifact, keys="+str(names[:12]))
def load_mapping(path):
    txt=Path(path).read_text(encoding="utf-8")
    return re.findall(r'^\s*-\s*id_ruta:\s*["\']?(\d+)',txt,re.M)
def public_release():
    # release download uses gh to handle release assets, without guessing redirected URLs
    dest=ROOT/"download-main"
    dest.mkdir(exist_ok=True,parents=True)
    cmd=["gh","release","download","latest","-R",REPO,"--pattern",MAIN_FEED,"--dir",str(dest),"--clobber"]
    cp=subprocess.run(cmd,text=True,capture_output=True,timeout=120)
    p=dest/MAIN_FEED
    if cp.returncode or not p.exists():
        raise RuntimeError("gh release download failed: "+cp.stderr[-250:])
    return p.read_bytes(),{"url":f"https://github.com/{REPO}/releases/tag/latest"}
def latest_artifact(wf,expected):
    data=api(f"/actions/workflows/{wf}/runs?status=success&per_page=12")
    found=[]
    for run in data.get("workflow_runs",[]):
        try:
            artifacts=api(f"/actions/runs/{run['id']}/artifacts?per_page=30").get("artifacts",[])
        except Exception as ex:
            found.append({"run":run["id"],"error":str(ex)[:140]})
            continue
        for item in artifacts:
            if item.get("expired"):continue
            try:
                data=get(API+f"/actions/artifacts/{item['id']}/zip", "application/vnd.github+json")
                gtfs=load_archive_candidate(data,expected)
                # verify actual GTFS
                inspect_feed(gtfs)
                return gtfs,dict(run_id=run["id"],run_url=run["html_url"],
                                 artifact_id=item["id"],artifact_name=item["name"])
            except Exception as ex:
                found.append({"run":run["id"],"artifact":item["name"],"error":str(ex)[:140]})
    raise ValueError("No accessible valid GTFS artifact from latest successful runs. "+str(found[:6]))
def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    register=Path("data/resolutions/medellin_252_schedule_2026_working_assumption_p4_updated.csv")
    with register.open(encoding="utf-8",newline="") as f:
        old=list(csv.DictReader(f))
    byid={x["arcgis_id_ruta"]:x for x in old}
    assert len(byid)==252
    legacy_valid={k for k,v in byid.items() if v.get("assumed_2026_window_and_frequency_three_daytypes")=="yes"}
    evidence=[]
    summary=[]
    mapping_lookup={key:set(load_mapping(path)) for key,path in MAPS.items()}
    for kind in ["main",*WORKFLOWS]:
        try:
            data,src=public_release() if kind=="main" else latest_artifact(*WORKFLOWS[kind])
            routes,info=inspect_feed(data)
            status="verified_actual_GTFS"
        except Exception as exc:
            routes=[];info=dict(error=str(exc)[:700]);src={};status="no_accessible_GTFS"
        summary.append(dict(generator=kind,status=status,**src,**info))
        for r in routes:
            rid=r["route_id"]
            arcgis=""
            if kind in ("taxmaya","trsc","transacoop"):
                m=re.fullmatch(kind+r"_(\d+)",rid)
                if m and m.group(1) in mapping_lookup[kind]:
                    arcgis=m.group(1)
            entry=byid.get(arcgis,{})
            evidence.append(dict(generator=kind,gtfs_route_id=rid,
                short_name=r["route_short_name"],long_name=r["route_long_name"],
                agency=r["agency_id"],trip_count=r["trip_count"],has_trips="yes" if r["trip_count"] else "no",
                arcgis_legacy_id=arcgis,arcgis_id_mapping="verified_config_prefix" if arcgis else "not_proven",
                in_252="yes" if entry else "no_or_unmapped",
                schedule_ready_2026="yes" if arcgis in legacy_valid else "no_or_unmapped",
                model_operator=entry.get("operator","")))
    actual_ids={e["arcgis_legacy_id"] for e in evidence if e["arcgis_legacy_id"] and e["has_trips"]=="yes"}
    only_spatial_ids={e["arcgis_legacy_id"] for e in evidence if e["arcgis_legacy_id"] and e["has_trips"]=="no"}
    ready_missing=legacy_valid-actual_ids
    stats={
        "legacy_universe":len(byid),
        "legacy_complete_2026_working_schedules":len(legacy_valid),
        "actual_feeds_inspected":sum(x["status"]=="verified_actual_GTFS" for x in summary),
        "actual_legacy_ids_with_trips_identified":len(actual_ids),
        "actual_ready_legacy_ids_with_trips":len(actual_ids&legacy_valid),
        "ready_legacy_ids_not_in_verified_trip_feeds":len(ready_missing),
        "explicit_geometry_only_ids":len(only_spatial_ids-actual_ids),
        "caution":"Unmapped Coonatra/El Poblado/Sotrames route_ids cannot be counted as new or existing until geometry/ID mapping. Missing expired artifact means unknown, not absent."
    }
    (ROOT/"inventory.json").write_text(json.dumps({"stats":stats,"generators":summary},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    keys=["generator","gtfs_route_id","short_name","long_name","agency","trip_count","has_trips","arcgis_legacy_id","arcgis_id_mapping","in_252","schedule_ready_2026","model_operator"]
    with (ROOT/"actual_gtfs_routes.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(evidence)
    with (ROOT/"ready_not_in_verified_gtfs.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["arcgis_id","code","operator","route_name"])
        w.writeheader()
        for id in sorted(ready_missing):
            m=byid[id]
            w.writerow(dict(arcgis_id=id,code=m.get("arcgis_code",""),
                            operator=m.get("operator",""),route_name=m.get("arcgis_route_name","")))
    report=["# Verified generator route-ID inventory", "",
            "This audit reads actual released or archived GTFS routes.txt and trips.txt, not just scripts or YAML route declarations.", "",
            "| Generator | GTFS evidence | Routes | With trips | Without trips |",
            "|---|---|---:|---:|---:|"]
    for s in summary:
        report.append(f'| {s["generator"]} | {s["status"]} | {s.get("unique_route_ids","–")} | {s.get("routes_with_trips","–")} | {s.get("routes_without_trips","–")} |')
    report += ["",f'2026 research complete 3-daytype route IDs: **{len(legacy_valid)}/252**.',
               f'Confirmed exact ArcGIS IDs present with trips in inspected GTFS: **{len(actual_ids)}**.',
               f'Of the 118 ready IDs, found as actual trips: **{len(actual_ids & legacy_valid)}**.',
               f'Of the 118 ready IDs, not established as actual trips: **{len(ready_missing)}**.',
               "", "**Caution:** Unknown or expired workflow artifacts and unmapped names are NOT evidence a route was never generated.",
               "Download actual_gtfs_routes.csv, ready_not_in_verified_gtfs.csv and inventory.json from the workflow artifact for details."]
    (ROOT/"README.md").write_text("\n".join(report)+"\n",encoding="utf-8")
    print("\n".join(report))
if __name__=="__main__":
    main()
