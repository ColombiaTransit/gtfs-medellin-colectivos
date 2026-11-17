#!/usr/bin/env python3
"""Validate official 2025 Palenque route windows and intervals against ASTREA HTML.

Reads only public original HTML and the source-first legal CSV; no PDF or
permanent HTML is stored, and nothing in GTFS is modified.
"""
import csv
import re
import subprocess
from collections import Counter
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data/resolutions/palenque_2025_official_route_service_intervals.csv"
URL = "https://www.medellin.gov.co/normograma/docs/astrea/docs/r_smmed_88689_2025.htm"
CODE = r"(?:\d{3}-\di?|\d{3}-i|251|252|267)"
RE_TIMES = re.compile(rf"(?m)^(\d{{5,6}})\n({CODE})\n([^\n]+)\n((?:\d\d:\d\d\n){{6}})")
RE_INTERVAL = re.compile(rf"(?m)^(\d{{5,6}})\n({CODE})\n([^\n]+)\n(\d{{1,3}})\n(\d{{1,3}})\n(\d{{1,3}})\n")


def get_original_text():
    run = subprocess.run([
        "curl", "-fsSL", "--max-time", "70", "--connect-timeout", "15",
        "-A", "Mozilla/5.0 (compatible; ColombiaTransit-legal-table-qa/1.0)",
        "-H", "Accept: text/html,*/*;q=0.5", URL
    ], capture_output=True, timeout=75)
    if run.returncode:
        raise RuntimeError(f"Could not retrieve original ASTREA: curl {run.returncode}")
    soup = BeautifulSoup(run.stdout, "html.parser")
    panel = soup.select_one(".panel-documento") or soup.select_one(".panel-fondo-documento")
    if panel is None:
        raise RuntimeError("Original municipal legal text panel unavailable")
    for node in panel.select("script,style,noscript,svg"):
        node.decompose()
    text = "\n".join(n.strip() for n in panel.stripped_strings if n.strip())
    if "RESOLUCIÓN 202550088689 DE 2025" not in text or len(text) < 38000:
        raise RuntimeError("Wrong original document / incomplete text")
    return text


def parsed_source(text):
    art3 = text.split("ARTÍCULO TERCERO. HORARIOS DE SERVICIO.", 1)[1].split(
        "ARTÍCULO CUARTO. INTERVALOS MÁXIMOS DE DESPACHO.", 1)[0]
    art4 = text.split("ARTÍCULO CUARTO. INTERVALOS MÁXIMOS DE DESPACHO.", 1)[1].split(
        "ARTÍCULO QUINTO. CAPACIDAD TRANSPORTADORA.", 1)[0]
    times = {}
    for gtpc, code, name, block in RE_TIMES.findall(art3):
        key = (gtpc, code)
        if key in times:
            raise RuntimeError(f"Duplicate time table key {key}")
        times[key] = block.strip().split("\n")
    blocks = re.split(
        r"(?m)^\d\. Intervalo máximo de despacho para día "
        r"(?:típico laboral|sábado|domingo/festivo)\n",
        art4
    )[1:]
    if len(blocks) != 3:
        raise RuntimeError(f"Expected 3 day-type tables, got {len(blocks)}")
    periods = []
    for block in blocks:
        result = {}
        for gtpc, code, name, a, b, c in RE_INTERVAL.findall(block):
            key = (gtpc, code)
            if key in result:
                raise RuntimeError(f"Duplicate interval key {key}")
            result[key] = [int(a), int(b), int(c)]
        periods.append(result)
    if len(times) != 20 or [len(p) for p in periods] != [20,20,20]:
        raise RuntimeError(f"Expected 20 rows per table: {len(times)}, {[len(p) for p in periods]}")
    assert set(times) == set(periods[0]) == set(periods[1]) == set(periods[2])
    return times, periods


def main():
    text = get_original_text()
    times, periods = parsed_source(text)
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 20:
        raise RuntimeError(f"Unexpected number of CSV route records: {len(rows)}")
    fields = [
        "weekday_max_peak_min","weekday_max_extreme_valley_min","weekday_max_midday_valley_min",
        "saturday_max_peak_min","saturday_max_extreme_valley_min","saturday_max_midday_valley_min",
        "sunday_holiday_max_peak_min","sunday_holiday_max_extreme_valley_min",
        "sunday_holiday_max_midday_valley_min"
    ]
    windows = ["weekday_first","weekday_last","saturday_first","saturday_last",
               "sunday_holiday_first","sunday_holiday_last"]
    seen = set()
    for row in rows:
        key = (row["legal_gtpc_code"], row["legal_user_route_code"])
        assert key not in seen, f"Duplicate legal code pair: {key}"
        seen.add(key)
        assert key in times, f"Not in original time table: {key}"
        assert [row[f] for f in windows] == times[key], f"Time mismatch {key}"
        original_intervals = sum([p[key] for p in periods], [])
        assert [int(row[f]) for f in fields] == original_intervals, f"Interval mismatch {key}"
        assert row["legal_resolution"] == "202550088689"
        assert row["gaceta"] == "5694"
        assert row["published_date"] == "2025-11-11"
        assert row["allow_direct_gtfs_build"] == "no"
        assert row["arcgis_2025_variant_match_validated"] == "no"
        assert row["later_2026_effectivity_audited"] == "no"
    assert seen == set(times)
    assert Counter(x["service_scope"] for x in rows) == {
        "regular_authorized_route": 19, "temporary_continuity_only": 1
    }
    by_code = {r["legal_user_route_code"]: r for r in rows}
    assert by_code["250-5i"]["operational_condition"].startswith("Only during suspension")
    assert by_code["253-i"]["legal_gtpc_code"] == by_code["250-5i"]["legal_gtpc_code"]
    print("PASS: 20 authoritative 2025 services compared against original ASTREA HTML; "
          "6 service clock values and 9 maximal headways per service match exactly.")
    print("19 regular authorized services; contingency 250-5i only for Línea J disruption.")
    print("Source GTPC collision 207050 preserved; auto-import into GTFS remains disabled.")


if __name__ == "__main__":
    main()
