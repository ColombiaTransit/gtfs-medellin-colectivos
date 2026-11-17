#!/usr/bin/env python3
"""Audit conservative links between 2015 Medellín legal fichas and ArcGIS routes.

Read-only validation. Never writes official 2015 headways to any GTFS builder.
Run from repository root: python scripts/validate_2015_arcgis_links.py
"""
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
import csv
import re
import sys
import unicodedata

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RES = DATA / "resolutions"


def load(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def normalized_code(value):
    value = "".join(
        ch for ch in unicodedata.normalize("NFD", value.upper())
        if unicodedata.category(ch) != "Mn"
    )
    value = re.sub("[^A-Z0-9]", "", value)
    return re.sub(r"^0+(?=\d)", "", value)


def assert_unique(items, key, where):
    keys = [key(x) for x in items]
    assert len(keys) == len(set(keys)), f"Duplicate keys in {where}"


def main():
    arcs = load(DATA / "medellin" / "routes.csv")
    one = load(RES / "gaceta_4325_visual_verified.csv")
    two = load(RES / "gacetas_4326_4327_visual_verified_2a_6d.csv")
    three = load(RES / "gaceta_4327_res_1047_visual_verified.csv")
    manual = load(RES / "2015_arcgis_manual_candidates.csv")
    links = load(RES / "2015_arcgis_fiche_candidate_links.csv")
    summary = load(RES / "2015_arcgis_route_link_status.csv")

    # The official ArcGIS transport layer has two direction records per id_ruta.
    arc_by_id = {}
    for r in arcs:
        arc_by_id.setdefault(r["id_ruta"], r)
    assert len(arc_by_id) == 252, "ArcGIS route count changed; rerun the legal link review"
    assert len(arcs) == 504, "ArcGIS direction-record count changed"

    source_by_page = {}
    for r in one:
        key = (r["system"], r["pdf_page"])
        assert key not in source_by_page, f"Duplicate historical page {key}"
        source_by_page[key] = (r["route_code"], r["gaceta"], r["resolution"])
    for r in two:
        key = (r["system"], r["printed_page"])
        assert key not in source_by_page, f"Duplicate historical page {key}"
        source_by_page[key] = (r["official_route_code"], r["gaceta"], r["resolution"])
    for r in three:
        key = (r["system"], r["printed_page"])
        assert key not in source_by_page, f"Duplicate historical page {key}"
        source_by_page[key] = (r["route_code"], r["gaceta"], r["resolution"])
    assert len(source_by_page) == 116, "Historical source has gained or lost fichas"

    manual_keys = {
        (m["arcgis_id_ruta"], m["historical_system"], m["historical_pdf_page"])
        for m in manual
    }
    assert_unique(manual, lambda x: (
        x["arcgis_id_ruta"], x["historical_system"], x["historical_pdf_page"]
    ), "manual link overrides")

    assert len(summary) == len(arc_by_id), "Need exactly one status per route"
    assert_unique(summary, lambda x: x["arcgis_id_ruta"], "route-link summary")
    assert len({x["arcgis_id_ruta"] for x in links}) == len(arc_by_id), (
        "Every current ArcGIS id needs at least one linked or unmatched entry"
    )

    by_id = defaultdict(list)
    historical_only = "official_2015_printed_schedule_only"
    for row in links:
        route_id = row["arcgis_id_ruta"]
        assert route_id in arc_by_id, f"Unknown current route {route_id}"
        r = arc_by_id[route_id]
        assert row["current_route_code"] == r["codigo_ruta"]
        assert row["current_system"] == r["sistema"]
        assert row["current_operator"] == r["empresa"]
        assert row["verified_current_frequency"] == "no"
        assert row["gtfs_import_allowed"] == "no"
        assert row["arcgis_snapshot_date"] == "2025-08-14"

        method = row["link_method"]
        if method == "no_source_candidate":
            assert not row["historical_code"]
            assert row["historical_schedule_status"] == "no_2015_source_matched"
        else:
            key = (r["sistema"], row["historical_pdf_page"])
            assert key in source_by_page, f"Unrecognized source reference {key}"
            code, gaceta, act = source_by_page[key]
            assert row["historical_code"] == code
            assert row["historical_resolution"] == act
            assert row["historical_gaceta"] == gaceta
            assert row["historical_schedule_status"] == historical_only
            exact = normalized_code(r["codigo_ruta"]) == normalized_code(code)
            manually_curated = (route_id, r["sistema"], row["historical_pdf_page"]) in manual_keys
            if method == "code_and_system_match":
                assert exact
            elif method == "manual_name_or_family_candidate":
                assert manually_curated
                assert not exact
            elif method == "code_and_manual_variant_annotation":
                assert exact and manually_curated
            else:
                raise AssertionError(f"Unsupported link method: {method}")
        by_id[route_id].append(row)

    status_counter = Counter()
    for s in summary:
        route_id = s["arcgis_id_ruta"]
        assert route_id in arc_by_id
        assert s["verified_as_current_service"] == "no"
        assert s["allow_2015_schedule_auto_import"] == "no"
        assert s["legal_applicability"] == "2015_historical_reference_not_operationally_current"
        assert int(s["number_of_historical_source_candidates"]) == sum(
            bool(x["historical_code"]) for x in by_id[route_id]
        )
        label = s["best_historical_link_status"]
        assert label in {
            "strong_2015_identity", "code_variant_review",
            "possible_historical_family", "no_2015_candidate"
        }
        if label == "no_2015_candidate":
            assert len(by_id[route_id]) == 1
            assert not by_id[route_id][0]["historical_code"]
        status_counter[label] += 1

    assert status_counter == {
        "strong_2015_identity": 41,
        "code_variant_review": 32,
        "possible_historical_family": 38,
        "no_2015_candidate": 141
    }, f"Changes to match buckets require review: {status_counter}"

    # All official ArcGIS time fields were equal to a single ingest timestamp;
    # never interpret this as independently verified update dates.
    for r in arc_by_id.values():
        for field in ("from_date", "fecha_actualizacion"):
            d = datetime.fromtimestamp(int(r[field]) / 1000, tz=timezone.utc)
            assert d.date().isoformat() == "2025-08-14", (
                "ArcGIS snapshot field date changed: re-check data freshness"
            )
    print(f"OK: {len(arc_by_id)} ArcGIS IDs; {len(links)} linkage rows; "
          f"{len(source_by_page)} 2015 fiche occurrences; status: {dict(status_counter)}")
    print("Every 2015 source is historical only; GTFS auto-import disabled.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
