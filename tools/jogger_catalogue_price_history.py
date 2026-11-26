#!/usr/bin/env python3
"""Build deterministic Jogger MY26 catalogue price history from canonical records."""
from __future__ import annotations

import argparse
import csv
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
CORRECTION = ROOT / "project" / "sources" / "jogger_price_matrix_correction_20261001_import_spec.json"
DEFAULT_JSON = ROOT / "reports" / "price_history" / "jogger_catalogue_price_history_2026.json"
DEFAULT_MD = ROOT / "reports" / "price_history" / "jogger_catalogue_price_history_2026.md"
OLD = "src_pl_jogger_price_my26_20260703"
NEW = "src_pl_jogger_price_my26_20261001"


class HistoryError(RuntimeError):
    pass


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def build_history() -> dict:
    prices = read_csv(MASTER / "configuration_prices.csv")
    sources = {row["code"]: row for row in read_csv(MASTER / "sources.csv")}
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    for code, date in ((OLD, "2026-07-03"), (NEW, "2026-10-01")):
        if code not in sources or sources[code]["document_date"] != date or sources[code]["market"] != "PL":
            raise HistoryError("Missing or mismatched source registration: " + code)

    def select(code: str) -> dict[str, dict[str, str]]:
        selected = {}
        for row in prices:
            if (row["source_code"] == code and row["market"] == "PL"
                    and row["price_type"] == "catalog_gross" and row["currency_code"] == "PLN"):
                key = row["configuration_code"]
                if key in selected:
                    raise HistoryError("Duplicate price observation: " + key)
                selected[key] = row
        return selected

    previous, current = select(OLD), select(NEW)
    if len(previous) != 22 or len(current) != 11:
        raise HistoryError(f"Unexpected coverage: previous={len(previous)}, current={len(current)}")

    unavailable = {
        item["configuration_code"]
        for item in correction["corrections"]
        if item["disposition"] == "requires_update" and item.get("new_value") == "no price row"
    }
    if unavailable != {"jogger_essential_7seat_ecog120_manual"}:
        raise HistoryError("Explicitly unavailable configuration does not match reviewed correction spec")
    if unavailable & set(current):
        raise HistoryError("Explicitly unavailable configuration also has a current price row")

    events = []
    for config in sorted(previous):
        old_row = previous[config]
        new_row = current.get(config)
        if new_row:
            old_value, new_value = int(old_row["amount"]), int(new_row["amount"])
            delta = new_value - old_value
            disposition = "unchanged" if delta == 0 else "changed"
            pct = (Decimal(delta) * 100 / Decimal(old_value)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            notes = "Both values are explicit dated master observations."
            current_code = new_row["code"]
        elif config in unavailable:
            old_value, new_value, delta, pct = int(old_row["amount"]), None, None, None
            disposition = "explicitly_unavailable"
            notes = "The 2026-10-01 page-1 cell is an explicit dash; no current price observation is retained."
            current_code = None
        else:
            old_value, new_value, delta, pct = int(old_row["amount"]), None, None, None
            disposition = "not_comparable"
            notes = (
                "Configuration is absent from the later page-1 matrix, but the reviewed correction "
                "spec does not authorize inferring removal or unavailability from this omission."
            )
            current_code = None
        events.append({
            "event_id": f"jogger_catalog_price_{config}_20260703_20261001",
            "change_type": "catalogue_price",
            "market": "PL",
            "model_year": "MY26",
            "configuration_code": config,
            "price_type": "catalog_gross",
            "currency": "PLN",
            "previous_source_code": OLD,
            "current_source_code": NEW,
            "previous_document_date": "2026-07-03",
            "current_document_date": "2026-10-01",
            "previous_effective_date": old_row["price_date"],
            "current_effective_date": "2026-10-01" if new_row or config in unavailable else None,
            "previous_value": old_value,
            "current_value": new_value,
            "delta_value": delta,
            "delta_percent": str(pct) if pct is not None else None,
            "disposition": disposition,
            "previous_evidence": "catalogue price matrix, printed page 1",
            "current_evidence": (
                "catalogue price matrix, printed page 1"
                if new_row or config in unavailable else
                "not established for this exact configuration in the reviewed later matrix"
            ),
            "previous_master_observation_code": old_row["code"],
            "current_master_observation_code": current_code,
            "notes": notes,
        })

    counts = {key: sum(event["disposition"] == key for event in events)
              for key in ("changed", "unchanged", "explicitly_unavailable", "not_comparable")}
    if counts != {"changed": 0, "unchanged": 11, "explicitly_unavailable": 1, "not_comparable": 10}:
        raise HistoryError("Unexpected Jogger comparison dispositions: " + repr(counts))

    return {
        "schema_version": "1.0.0",
        "report_id": "jogger_catalogue_price_history_2026",
        "generated_from": [
            "data/master/configuration_prices.csv",
            "project/sources/jogger_price_matrix_correction_20261001_import_spec.json",
        ],
        "scope": {
            "market": "PL",
            "model_year": "MY26",
            "models": ["Jogger"],
            "price_type": "catalog_gross",
            "currency": "PLN",
            "comparison_pair": {
                "previous_source_code": OLD,
                "current_source_code": NEW,
                "previous_document_date": "2026-07-03",
                "current_document_date": "2026-10-01",
            },
            "coverage": {
                "previous_price_observations": len(previous),
                "current_price_observations": len(current),
                **counts,
                "total_previous_configurations": len(events),
            },
            "limitations": [
                "This report compares the 2026-07-03 and 2026-10-01 official Polish cenniks only.",
                "The later source has 11 price observations for 12 linked configurations; one exact cell is an explicit dash.",
                "Ten earlier configurations are absent from the later price matrix; their omission is not treated as discontinuation or unavailability.",
                "The earlier source's historical price observations are retained; no master rows are overwritten.",
                "Promotions, financing, leasing, accessories and dealer offers are excluded.",
            ],
        },
        "sources": [
            {
                "source_code": OLD,
                "document_date": "2026-07-03",
                "role": "previous_price_baseline",
                "external_reference": sources[OLD]["external_reference"],
                "evidence": "catalogue price matrix, printed page 1",
            },
            {
                "source_code": NEW,
                "document_date": "2026-10-01",
                "role": "current_price_matrix_and_explicit_unavailability",
                "external_reference": sources[NEW]["external_reference"],
                "sha256": sources[NEW]["sha256"],
                "evidence": "catalogue price matrix, printed page 1",
            },
        ],
        "events": events,
    }


def render_markdown(data: dict) -> str:
    coverage = data["scope"]["coverage"]
    lines = [
        "# Jogger — historia cen katalogowych MY26",
        "",
        "**Rynek:** Polska · **Porównanie:** 03.07.2026 → 01.10.2026 · **Waluta:** PLN brutto",
        "",
        "## Podsumowanie",
        "",
        f"- Wcześniejsze konfiguracje z ceną: **{coverage['previous_price_observations']}**",
        f"- Późniejsze obserwacje cen: **{coverage['current_price_observations']}**",
        f"- Ceny bez zmian: **{coverage['unchanged']}**",
        f"- Zmiany cen: **{coverage['changed']}**",
        f"- Jawnie niedostępne w macierzy: **{coverage['explicitly_unavailable']}**",
        f"- Brak porównywalnego potwierdzenia dla pominiętych konfiguracji: **{coverage['not_comparable']}**",
        "",
        "## Porównanie konfiguracji",
        "",
        "| Konfiguracja | 03.07.2026 | 01.10.2026 | Różnica | Status |",
        "|---|---:|---:|---:|---|",
    ]
    for event in data["events"]:
        old = str(event["previous_value"])
        new = str(event["current_value"]) if event["current_value"] is not None else "—"
        delta = f"{event['delta_value']:+}" if event["delta_value"] is not None else "—"
        labels = {
            "unchanged": "bez zmian",
            "changed": "zmiana ceny",
            "explicitly_unavailable": "jawnie niedostępna",
            "not_comparable": "brak porównywalnego potwierdzenia",
        }
        lines.append(f"| {event['configuration_code']} | {old} | {new} | {delta} | {labels[event['disposition']]} |")
    lines += [
        "",
        "## Interpretacja i ograniczenia",
        "",
        "- Strona 1 cennika z 01.10.2026 zawiera 11 cen dla 12 powiązanych konfiguracji.",
        "- Dla 7-miejscowego Eco-G 120 manual / Essential wydrukowano kreskę; jest to jawna niedostępność ceny w tej macierzy.",
        "- Dziesięć innych wcześniejszych konfiguracji nie występuje w późniejszej macierzy. Zgodnie z korektą źródłową nie uznano samego pominięcia za dowód wycofania.",
        "- Wszystkie 11 porównywalnych cen pozostało bez zmian. Nie stwierdzono podwyżek ani obniżek.",
        "- Zachowano wcześniejsze obserwacje historyczne; raport nie tworzy duplikatów w danych głównych.",
        "- Promocje, finansowanie, leasing, akcesoria i oferty dealerskie są poza zakresem.",
        "",
        "Raport pochodny opiera się na rejestrze źródeł, obserwacjach cen i zatwierdzonej korekcie macierzy.",
        "",
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
        print("Jogger catalogue price history: PASS")
    else:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json_text, encoding="utf-8")
        args.markdown.write_text(markdown_text, encoding="utf-8")
        print(f"Generated {len(data['events'])} events")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
