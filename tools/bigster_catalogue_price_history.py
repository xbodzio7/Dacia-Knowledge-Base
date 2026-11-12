#!/usr/bin/env python3
"""Build deterministic Bigster MY26 catalogue price history from canonical records."""
from __future__ import annotations
import argparse, csv, json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
DEFAULT_JSON = ROOT / "reports" / "price_history" / "bigster_catalogue_price_history_2026.json"
DEFAULT_MD = ROOT / "reports" / "price_history" / "bigster_catalogue_price_history_2026.md"
OLD = "src_pl_bigster_price_my26_20261001"
NEW = "src_pl_bigster_price_my26_20261102"

class HistoryError(RuntimeError):
    pass

def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))

def build_history() -> dict:
    prices = read_csv(MASTER / "configuration_prices.csv")
    sources = {r["code"]: r for r in read_csv(MASTER / "sources.csv")}
    for code, date in ((OLD, "2026-10-01"), (NEW, "2026-11-02")):
        source = sources.get(code)
        if not source or source["document_date"] != date or source["market"] != "PL":
            raise HistoryError("Missing or mismatched source registration: " + code)
    def select(code):
        result = {}
        for row in prices:
            if row["source_code"] == code and row["market"] == "PL" and row["price_type"] == "catalog_gross" and row["currency_code"] == "PLN":
                key = row["configuration_code"]
                if key in result:
                    raise HistoryError("Duplicate price observation: " + key)
                result[key] = row
        return result
    previous, current = select(OLD), select(NEW)
    if len(previous) != 13 or len(current) != 13 or set(previous) != set(current):
        raise HistoryError(f"Unexpected exact configuration coverage: previous={len(previous)}, current={len(current)}")
    events = []
    for config in sorted(previous):
        old, new = previous[config], current[config]
        old_value, new_value = int(old["amount"]), int(new["amount"])
        delta = new_value - old_value
        pct = Decimal(delta) * 100 / Decimal(old_value) if old_value else Decimal(0)
        disposition = "unchanged" if delta == 0 else "changed"
        events.append({
            "event_id": f"bigster_catalog_price_{config}_20261001_20261102",
            "change_type": "catalogue_price", "market": "PL", "model_year": "MY26",
            "configuration_code": config, "price_type": "catalog_gross", "currency": "PLN",
            "previous_source_code": OLD, "current_source_code": NEW,
            "previous_document_date": "2026-10-01", "current_document_date": "2026-11-02",
            "previous_effective_date": old["price_date"], "current_effective_date": new["price_date"],
            "previous_value": old_value, "current_value": new_value, "delta_value": delta,
            "delta_percent": f"{pct:.2f}", "disposition": disposition,
            "previous_evidence": "catalogue price matrix, printed page 1",
            "current_evidence": "catalogue price matrix, printed page 1",
            "previous_master_observation_code": old["code"], "current_master_observation_code": new["code"],
            "notes": "Both dated official cenniks explicitly price this exact canonical configuration; the values are unchanged."
        })
    changed = sum(e["disposition"] == "changed" for e in events)
    unchanged = sum(e["disposition"] == "unchanged" for e in events)
    if (changed, unchanged) != (0, 13):
        raise HistoryError(f"Unexpected comparison result: changed={changed}, unchanged={unchanged}")
    return {
        "schema_version": "1.0.0", "report_id": "bigster_catalogue_price_history_2026",
        "generated_from": ["data/master/configuration_prices.csv", "data/master/sources.csv"],
        "scope": {
            "market": "PL", "model_year": "MY26", "models": ["Bigster"],
            "price_type": "catalog_gross", "currency": "PLN",
            "comparison_pair": {"previous_source_code": OLD, "current_source_code": NEW,
                                 "previous_document_date": "2026-10-01", "current_document_date": "2026-11-02"},
            "coverage": {"previous_price_observations": 13, "current_price_observations": 13,
                         "changed": changed, "unchanged": unchanged,
                         "explicitly_unavailable": 0, "not_comparable": 0, "total_configurations": 13},
            "limitations": [
                "This report compares the 2026-10-01 and 2026-11-02 official Polish Bigster MY26 cenniks only.",
                "All 13 exact canonical configurations occur in both page-1 price matrices and retain identical catalogue gross prices.",
                "The 2026-07-03 cennik is not used as the comparison baseline because several engine/configuration identifiers were subsequently renamed or restructured; no cross-identifier equivalence is inferred.",
                "This is a derived confirmation report and does not duplicate or overwrite master price observations.",
                "Promotions, financing, leasing, accessories and dealer offers are excluded."
            ]
        },
        "sources": [
            {"source_code": OLD, "document_date": "2026-10-01", "role": "previous_price_baseline",
             "external_reference": sources[OLD]["external_reference"], "sha256": sources[OLD]["sha256"],
             "evidence": "catalogue price matrix, printed page 1"},
            {"source_code": NEW, "document_date": "2026-11-02", "role": "current_price_matrix_and_unchanged_confirmations",
             "external_reference": sources[NEW]["external_reference"], "sha256": sources[NEW]["sha256"],
             "evidence": "catalogue price matrix, printed page 1"}
        ],
        "events": events
    }

def render_markdown(data: dict) -> str:
    c = data["scope"]["coverage"]
    lines = [
        "# Bigster — historia cen katalogowych MY26", "",
        "**Rynek:** Polska · **Porównanie:** 01.10.2026 → 02.11.2026 · **Waluta:** PLN brutto", "",
        "## Podsumowanie", "",
        f"- Wcześniejsze obserwacje cen: **{c['previous_price_observations']}**",
        f"- Późniejsze obserwacje cen: **{c['current_price_observations']}**",
        f"- Ceny bez zmian: **{c['unchanged']}**",
        f"- Podwyżki / obniżki: **{c['changed']}**",
        f"- Konfiguracje bez porównywalnego potwierdzenia: **{c['not_comparable']}**", "",
        "## Porównanie konfiguracji", "",
        "| Konfiguracja | 01.10.2026 | 02.11.2026 | Różnica |",
        "|---|---:|---:|---:|"
    ]
    for e in data["events"]:
        lines.append(f"| {e['configuration_code']} | {e['previous_value']} | {e['current_value']} | {e['delta_value']:+d} |")
    lines += [
        "", "## Źródła i ograniczenia", "",
        "- Porównano wyłącznie ceny katalogowe z pierwszej strony dwóch oficjalnych polskich cenników Bigstera MY26.",
        "- Wszystkie 13 dokładnych konfiguracji występuje w obu macierzach; ceny są identyczne.",
        "- Cennik z 03.07.2026 nie jest bezpośrednim baseline'em: zmieniono/rozbito część identyfikatorów silników i konfiguracji. Nie zakładano równoważności nazw.",
        "- Nie utworzono duplikatów obserwacji cenowych; raport potwierdza wartości zapisane w danych głównych.",
        "- Promocje, finansowanie, leasing, akcesoria i oferty dealerskie pozostają poza zakresem.", "",
        "Raport pochodny opiera się na plikach configuration_prices.csv i sources.csv.", ""
    ]
    return "\n".join(lines)

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MD)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = build_history()
    outputs = {args.json: json.dumps(data, ensure_ascii=False, indent=2) + "\n",
               args.markdown: render_markdown(data)}
    if args.check:
        stale = [str(p) for p, content in outputs.items() if not p.exists() or p.read_text(encoding="utf-8") != content]
        if stale:
            raise HistoryError("Generated report is stale: " + ", ".join(stale))
        print("Bigster catalogue price history is current.")
        return 0
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    print(f"Generated {args.json} and {args.markdown}")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except HistoryError as exc:
        raise SystemExit(str(exc))
