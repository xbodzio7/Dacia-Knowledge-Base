#!/usr/bin/env python3
"""Build deterministic Duster MY26 catalogue price history from canonical records."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
AUDIT = ROOT / "data" / "reporting" / "duster_price_list_20261102_commercial_reconciliation.json"
DEFAULT_JSON = ROOT / "reports" / "price_history" / "duster_catalogue_price_history_2026.json"
DEFAULT_MD = ROOT / "reports" / "price_history" / "duster_catalogue_price_history_2026.md"
OLD = "src_pl_duster_price_my26_20260901"
NEW = "src_pl_duster_price_my26_20261102"

class HistoryError(RuntimeError):
    pass

def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))

def build_history() -> dict:
    prices = read_csv(MASTER / "configuration_prices.csv")
    sources = {row["code"]: row for row in read_csv(MASTER / "sources.csv")}
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    for code, date in ((OLD, "2026-09-01"), (NEW, "2026-11-02")):
        if code not in sources or sources[code]["document_date"] != date or sources[code]["market"] != "PL":
            raise HistoryError("Missing or mismatched source registration: " + code)
    evidence = audit.get("reconciliation", {}).get("catalogue_prices", {})
    if evidence.get("previous_source") != OLD or evidence.get("existing_rows_reused") != 16:
        raise HistoryError("The current-source reconciliation does not establish the exact 16-row baseline")
    if evidence.get("new_rows_added") != 0 or "All 16 page-1 catalogue prices" not in evidence.get("result", ""):
        raise HistoryError("The current cennik does not explicitly confirm all 16 unchanged prices")

    selected = {}
    for row in prices:
        if (row["source_code"] == OLD and row["market"] == "PL"
                and row["price_type"] == "catalog_gross" and row["currency_code"] == "PLN"):
            key = row["configuration_code"]
            if key in selected:
                raise HistoryError("Duplicate price observation: " + key)
            selected[key] = row
    if len(selected) != 16:
        raise HistoryError(f"Unexpected previous coverage: {len(selected)}")
    events = []
    for config, row in sorted(selected.items()):
        value = int(row["amount"])
        events.append({
            "event_id": f"duster_catalog_price_{config}_20260901_20261102",
            "change_type": "catalogue_price", "market": "PL", "model_year": "MY26",
            "configuration_code": config, "price_type": "catalog_gross", "currency": "PLN",
            "previous_source_code": OLD, "current_source_code": NEW,
            "previous_document_date": "2026-09-01", "current_document_date": "2026-11-02",
            "previous_effective_date": row["price_date"], "current_effective_date": "2026-11-02",
            "previous_value": value, "current_value": value, "delta_value": 0, "delta_percent": "0.00",
            "disposition": "unchanged",
            "previous_evidence": "catalogue price matrix, printed page 1",
            "current_evidence": "catalogue price matrix, printed page 1",
            "previous_master_observation_code": row["code"], "current_master_observation_code": None,
            "notes": "The 2026-11-02 cennik page-1 value was explicitly reconciled against this exact configuration and matches. No duplicate current master observation was created."
        })
    return {
        "schema_version": "1.0.0", "report_id": "duster_catalogue_price_history_2026",
        "generated_from": ["data/master/configuration_prices.csv", "data/master/sources.csv",
                           "data/reporting/duster_price_list_20261102_commercial_reconciliation.json"],
        "scope": {
            "market": "PL", "model_year": "MY26", "models": ["Duster"],
            "price_type": "catalog_gross", "currency": "PLN",
            "comparison_pair": {"previous_source_code": OLD, "current_source_code": NEW,
                                "previous_document_date": "2026-09-01", "current_document_date": "2026-11-02"},
            "coverage": {"previous_price_observations": 16, "current_price_observations": 16,
                         "changed": 0, "unchanged": 16, "explicitly_unavailable": 0,
                         "not_comparable": 0, "total_configurations": 16},
            "limitations": [
                "The report compares the 2026-09-01 and 2026-11-02 official Polish Duster MY26 cenniks only.",
                "All 16 page-1 catalogue prices in the 2026-11-02 cennik were reconciled with the existing 2026-09-01 master observations and match.",
                "No duplicate 2026-11-02 catalogue price observations were created; current values are source-review confirmations.",
                "The 2026-09-01 PDF URL currently redirects to the 2026-11-02 document; the historical baseline uses the previously registered source and preserved observations.",
                "The raw 2026-11-02 PDF was not locally archived and has no asserted SHA-256.",
                "Promotions, financing, leasing, accessories and dealer offers are excluded."
            ]
        },
        "sources": [
            {"source_code": OLD, "document_date": "2026-09-01", "role": "previous_complete_price_baseline",
             "external_reference": sources[OLD]["external_reference"], "sha256": sources[OLD]["sha256"],
             "evidence": "catalogue price matrix, printed page 1"},
            {"source_code": NEW, "document_date": "2026-11-02", "role": "current_price_matrix_and_unchanged_confirmations",
             "external_reference": sources[NEW]["external_reference"], "evidence": "catalogue price matrix, printed page 1"}
        ],
        "events": events
    }

def render_markdown(data: dict) -> str:
    coverage = data["scope"]["coverage"]
    lines = [
        "# Duster — historia cen katalogowych MY26", "",
        "**Rynek:** Polska · **Porównanie:** 01.09.2026 → 02.11.2026 · **Waluta:** PLN brutto", "",
        "## Podsumowanie", "",
        f"- Wcześniejsze obserwacje cen: **{coverage['previous_price_observations']}**",
        f"- Późniejsze ceny potwierdzone w cenniku: **{coverage['current_price_observations']}**",
        f"- Ceny bez zmian: **{coverage['unchanged']}**",
        f"- Podwyżki / obniżki: **{coverage['changed']}**",
        f"- Brak porównywalnych konfiguracji: **{coverage['not_comparable']}**", "",
        "## Porównanie konfiguracji", "",
        "| Konfiguracja | 01.09.2026 | 02.11.2026 | Różnica |",
        "|---|---:|---:|---:|"
    ]
    for event in data["events"]:
        lines.append(f"| {event['configuration_code']} | {event['previous_value']} | {event['current_value']} | 0 |")
    lines += [
        "", "## Interpretacja i ograniczenia", "",
        "- Wszystkie 16 cen katalogowych z pierwszej strony cennika z 02.11.2026 uzgodniono z odpowiadającymi im obserwacjami z 01.09.2026; wartości są identyczne.",
        "- Raport zapisuje potwierdzenia w warstwie pochodnej. Nie dodaje drugiego zestawu obserwacji cenowych do danych głównych.",
        "- Adres PDF z 01.09.2026 przekierowuje obecnie do dokumentu z 02.11.2026. Historyczny punkt odniesienia pochodzi z wcześniej zarejestrowanego źródła i zachowanych obserwacji.",
        "- Surowy plik PDF z 02.11.2026 nie był dostępny lokalnie; nie deklaruje się dla niego sumy SHA-256.",
        "- Promocje, finansowanie, leasing, akcesoria i oferty dealerskie pozostają poza zakresem.", "",
        "Raport pochodny opiera się na historycznych obserwacjach cen, rejestrze źródeł i raporcie uzgodnienia cennika z 02.11.2026.", ""
    ]
    return "\n".join(lines)

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MD)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = build_history()
    json_text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    markdown_text = render_markdown(data)
    if args.check:
        if not args.json.exists() or args.json.read_text(encoding="utf-8") != json_text:
            raise HistoryError("JSON history report is missing or stale")
        if not args.markdown.exists() or args.markdown.read_text(encoding="utf-8") != markdown_text:
            raise HistoryError("Markdown history report is missing or stale")
        print("Duster catalogue price history: PASS")
    else:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json_text, encoding="utf-8")
        args.markdown.write_text(markdown_text, encoding="utf-8")
        print(f"Generated {len(data['events'])} events")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
