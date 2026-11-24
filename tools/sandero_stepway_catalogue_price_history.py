#!/usr/bin/env python3
"""Build deterministic Sandero MY26 catalogue price history from canonical records."""
from __future__ import annotations
import argparse, csv, json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SPEC = ROOT / "project" / "sources" / "sandero_stepway_price_my26_20261102_import_spec.json"
DEFAULT_JSON = ROOT / "reports" / "price_history" / "sandero_stepway_catalogue_price_history_2026.json"
DEFAULT_MD = ROOT / "reports" / "price_history" / "sandero_stepway_catalogue_price_history_2026.md"
OLD = "src_pl_sandero_stepway_price_my26_20260811"
NEW = "src_pl_sandero_stepway_price_my26_20261102"
REPORT_METADATA = {
    "schema_version": 1,
    "report_id": "sandero_stepway_catalogue_price_history_2026",
    "generated_at": "2026-11-24T23:50:27.266Z",
    "reviewed_on": "2026-11-25",
    "repository": "xbodzio7/Dacia-Knowledge-Base",
    "base_commit_sha": "b56be440a9c2de592842aae600674a1a964e7e3a",
    "input_files": [
        {
            "path": "data/master/configuration_prices.csv",
            "git_blob_sha": "cf756fe3bec49d650012a52f4b42ccb9702b839a",
            "sha256": "92fca48ed48953c3917867473330a45a35b6e0d1b35c7f43c820994575a1b2ab"
        },
        {
            "path": "data/master/sources.csv",
            "git_blob_sha": "74c8441b6c0170cf4929e9534db2b6072415c3bd",
            "sha256": "c741eaacd1b33dfc7116312605ca80466767844b6bb81a23693f5875925e7f61"
        },
        {
            "path": "project/sources/sandero_stepway_price_my26_20261102_import_spec.json",
            "git_blob_sha": "0bb4437227fb54d6922a9357ba8ebf26c4c8049e",
            "sha256": "15fc37fa0bf7ef312d6c2391b870018510dca73540f2183c74d3b916b483c262"
        },
        {
            "path": "project/sources/sandero_stepway_price_my26_20260811_full_extract.json",
            "git_blob_sha": "be20501fc1a92a868d9ff4854754904e082be77d",
            "sha256": "af3b1957e30d2e01125f11082649c2811522fbe26132230d153a09fd25b10960"
        },
        {
            "path": "data/reporting/sandero_stepway_price_list_20261001_reconciliation_001.json",
            "git_blob_sha": "b85898243880ecf964d32e0ee593e4a43e6c3b2a",
            "sha256": "5dccfe38023d6bed725788b4cfb0aa7d12015a0a7e31c62db1e1119750764049"
        }
    ],
    "scope": "Official Polish MY26 catalogue gross prices for 19 exact Sandero and Sandero Stepway configurations, comparing the complete 2026-08-11 baseline with the 2026-11-02 cennik; promotions, financing, leasing, accessories and dealer offers are excluded.",
    "status": "current"
}

class HistoryError(RuntimeError):
    pass

def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def build_history():
    prices = read_csv(MASTER / "configuration_prices.csv")
    sources = {r["code"]: r for r in read_csv(MASTER / "sources.csv")}
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    for code, date in ((OLD, "2026-08-11"), (NEW, "2026-11-02")):
        source = sources.get(code)
        if (source is None or source["document_date"] != date or source["market"] != "PL"
                or source["status"] != "active" or not source["sha256"]
                or not source["external_reference"]):
            raise HistoryError("Missing or mismatched source registration: " + code)

    def select(code):
        rows = [r for r in prices if r["source_code"] == code and r["market"] == "PL"
                and r["price_type"] == "catalog_gross" and r["currency_code"] == "PLN"]
        result = {}
        for row in rows:
            key = row["configuration_code"]
            if key in result:
                raise HistoryError("Duplicate price observation: " + key)
            if row["price_date"] != sources[code]["document_date"]:
                raise HistoryError("Price date does not match its registered source: " + key)
            try:
                amount = int(row["amount"])
            except (TypeError, ValueError) as exc:
                raise HistoryError("Invalid catalogue price amount: " + key) from exc
            if amount <= 0:
                raise HistoryError("Catalogue price must be positive: " + key)
            result[key] = row
        return result

    previous, current = select(OLD), select(NEW)
    unchanged = {r["configuration_code"]: int(r["amount"]) for r in spec["unchanged_price_confirmations"]}
    if len(previous) != 19 or len(current) != 15 or len(unchanged) != 4:
        raise HistoryError("Unexpected source coverage: expected 19 previous, 15 current and 4 unchanged")
    if set(current) & set(unchanged) or set(previous) != set(current) | set(unchanged):
        raise HistoryError("Changed and unchanged configurations do not reconcile exactly")
    for key, amount in unchanged.items():
        if key not in previous or amount != int(previous[key]["amount"]):
            raise HistoryError("Unchanged confirmation does not match the previous price: " + key)
    new_values = {k: int(v["amount"]) for k, v in current.items()} | unchanged
    events = []
    for config in sorted(previous):
        old = int(previous[config]["amount"])
        new = new_values[config]
        delta = new - old
        if delta not in (0, 500):
            raise HistoryError(f"Unexpected price delta for {config}: {delta}")
        pct = (Decimal(delta) * 100 / Decimal(old)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        events.append({
            "event_id": f"sandero_catalog_price_{config}_20260811_20261102",
            "change_type": "catalogue_price", "market": "PL", "model_year": "MY26",
            "configuration_code": config, "price_type": "catalog_gross", "currency": "PLN",
            "previous_source_code": OLD, "current_source_code": NEW,
            "previous_document_date": sources[OLD]["document_date"],
            "current_document_date": sources[NEW]["document_date"],
            "previous_effective_date": previous[config]["price_date"],
            "current_effective_date": sources[NEW]["document_date"],
            "previous_value": old, "current_value": new, "delta_value": delta,
            "delta_percent": str(pct), "disposition": "unchanged" if delta == 0 else "changed",
            "previous_evidence": "catalogue price matrix, printed page 1",
            "current_evidence": "catalogue price matrix, printed page 1",
            "current_master_observation_code": current[config]["code"] if config in current else None,
            "notes": ("Current value explicitly confirmed unchanged; no duplicate master price observation created."
                      if config not in current else "Both values are explicit dated master observations.")
        })
    if sum(e["disposition"] == "changed" for e in events) != 15 or sum(e["disposition"] == "unchanged" for e in events) != 4:
        raise HistoryError("Expected 15 increases and four unchanged confirmations")
    return {
        "schema_version": "1.0.0",
        "report_id": "sandero_stepway_catalogue_price_history_2026",
        "report_metadata": REPORT_METADATA,
        "generated_from": ["data/master/configuration_prices.csv", "data/master/sources.csv",
                           "project/sources/sandero_stepway_price_my26_20261102_import_spec.json"],
        "scope": {
            "market": "PL", "model_year": "MY26", "models": ["Sandero", "Sandero Stepway"],
            "price_type": "catalog_gross", "currency": "PLN",
            "comparison_pair": {"previous_source_code": OLD, "current_source_code": NEW,
                                "previous_effective_date": "2026-08-11", "current_effective_date": "2026-11-02"},
            "coverage": {"previous_configurations": 19, "current_changed_observations": 15,
                         "current_unchanged_confirmations": 4, "comparable_configurations": 19,
                         "changed": 15, "unchanged": 4, "not_comparable": 0},
            "limitations": [
                "This MVP compares the complete 2026-08-11 and 2026-11-02 price pair only.",
                "The 2026-10-01 cennik is documentary reconciliation evidence; unchanged prices were not duplicated in master data.",
                "2026-07-03 records have split/partial source coverage and are not a complete baseline for all 19 configurations.",
                "Promotions, financing, leasing, accessories and dealer offers are excluded.",
                "Missing later rows are not interpreted as removals; four unchanged prices have explicit source-review confirmations."
            ]
        },
        "sources": [
            {"source_code": OLD, "document_date": sources[OLD]["document_date"],
             "role": "previous_complete_price_baseline",
             "external_reference": sources[OLD]["external_reference"], "sha256": sources[OLD]["sha256"],
             "evidence": "catalogue price matrix, printed page 1"},
            {"source_code": NEW, "document_date": "2026-11-02", "role": "current_price_and_unchanged_confirmations",
             "external_reference": sources[NEW]["external_reference"], "sha256": sources[NEW]["sha256"],
             "evidence": "catalogue price matrix, printed page 1"}
        ],
        "events": events
    }

def render_markdown(data):
    c = data["scope"]["coverage"]
    lines = [
        "# Sandero / Sandero Stepway — historia cen katalogowych MY26", "",
        f"Report ID: {data['report_metadata']['report_id']}",
        f"Generated: {data['report_metadata']['generated_at']}",
        f"Analysed commit: {data['report_metadata']['base_commit_sha']}",
        f"Status: {data['report_metadata']['status']}",
        f"Scope: {data['report_metadata']['scope']}", "",
        "**Rynek:** Polska · **Porównanie:** 11.08.2026 → 02.11.2026 · **Waluta:** PLN brutto", "",
        "## Podsumowanie", "",
        f"- Porównywalne konfiguracje: **{c['comparable_configurations']}**",
        f"- Podwyżki: **{c['changed']}** (każda o 500 PLN)",
        f"- Ceny bez zmian: **{c['unchanged']}**",
        "- Zmiany usunięcia/wycofania ceny: **0** — brak podstaw do takiego wniosku.", "",
        "## Zmiany według konfiguracji", "",
        "| Konfiguracja | 11.08.2026 | 02.11.2026 | Zmiana | Zmiana % | Status |",
        "|---|---:|---:|---:|---:|---|"
    ]
    for e in data["events"]:
        pct = f"{e['delta_percent']}%"
        status = "bez zmian" if e["disposition"] == "unchanged" else "podwyżka"
        lines.append(f"| {e['configuration_code']} | {e['previous_value']} | {e['current_value']} | {e['delta_value']:+} | {pct} | {status} |")
    lines += [
        "", "## Źródła i ograniczenia", "",
        "- Poprzedni cennik: 11.08.2026, oficjalny cennik Dacia Polska, strona drukowana 1.",
        "- Bieżący cennik: 02.11.2026, oficjalny cennik Dacia Polska, strona drukowana 1.",
        "- Cztery ceny Hybrid 155 potwierdzono jako niezmienione; nie utworzono dla nich dodatkowych rekordów master.",
        "- Cennik 01.10.2026 jest dowodem przeglądu dokumentu; nie dodano powielonych obserwacji cen.",
        "- Rekordy 03.07.2026 mają niejednorodny zakres źródeł i nie stanowią kompletnej bazy dla 19 konfiguracji.",
        "- Promocje, finansowanie, leasing, akcesoria i ceny dealerskie są poza zakresem.", "",
        "Raport jest warstwą pochodną; dane źródłowe pozostają w rejestrze źródeł i configuration_prices.csv.", ""
    ]
    return "\n".join(lines)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json", type=Path, default=DEFAULT_JSON)
    p.add_argument("--markdown", type=Path, default=DEFAULT_MD)
    p.add_argument("--check", action="store_true")
    a = p.parse_args()
    data = build_history()
    j = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    m = render_markdown(data)
    if a.check:
        if not a.json.exists() or a.json.read_text(encoding="utf-8") != j:
            raise HistoryError("JSON history report is missing or stale")
        if not a.markdown.exists() or a.markdown.read_text(encoding="utf-8") != m:
            raise HistoryError("Markdown history report is missing or stale")
        print("Sandero catalogue price history: PASS")
    else:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.markdown.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(j, encoding="utf-8")
        a.markdown.write_text(m, encoding="utf-8")
        print(f"Generated {len(data['events'])} events")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
