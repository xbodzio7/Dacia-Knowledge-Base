from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise RuntimeError(f"expected one patch anchor in {path}: {text.count(old)}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


config = ROOT / "tools/configuration_shortlist.py"
replace_once(
    config,
    '_SPRING_MEDIA_SOURCE = Path(\n    "project/sources/dacia-pl-spring-model-media-20260801.json"\n)\n',
    '_SPRING_MEDIA_SOURCE = Path(\n    "project/sources/dacia-pl-spring-model-media-20260801.json"\n)\n_REVIEWED_GAP_REPORT = Path(\n    "data/reporting/registered_source_completeness_reconciliation.json"\n)\n',
)

HELPERS = r'''

def _read_reviewed_gap_report(repository: Path) -> dict[str, Any]:
    path = repository / _REVIEWED_GAP_REPORT
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ShortlistError(f"cannot read reviewed gap report: {exc}") from exc
    if not isinstance(payload, dict) or payload.get("status") != "complete":
        raise ShortlistError("reviewed gap report is not complete")
    groups = payload.get("review_groups")
    if not isinstance(groups, list):
        raise ShortlistError("reviewed gap report has no review_groups list")
    return payload


def _commercial_review_decisions(
    payload: Mapping[str, Any],
) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}

    def add(
        group: Mapping[str, Any],
        item_code: str,
        configuration_code: str,
        candidate_amount: Any = None,
    ) -> None:
        key = (configuration_code, item_code)
        if key in result:
            raise ShortlistError(f"duplicate commercial review decision: {key}")
        amount = candidate_amount
        if amount is None:
            amount = group.get("candidate_amount_pln")
        result[key] = {
            "review_state": str(group.get("classification", "")),
            "review_reason_code": str(group.get("reason_code", "")),
            "reviewed_on": str(payload.get("generated_on", "")),
            "candidate_amount_pln": amount,
            "candidate_source_code": str(group.get("candidate_source_code", "")),
        }

    for raw_group in payload.get("review_groups", []):
        if not isinstance(raw_group, Mapping) or raw_group.get("area") != "optional-price":
            continue
        configuration_code = str(raw_group.get("configuration_code", ""))
        rows = raw_group.get("rows")
        if isinstance(rows, list):
            for row in rows:
                if not isinstance(row, list):
                    raise ShortlistError("invalid commercial review row")
                if configuration_code and len(row) == 2:
                    add(raw_group, str(row[0]), configuration_code, row[1])
                elif not configuration_code and len(row) == 3:
                    add(raw_group, str(row[0]), str(row[1]), row[2])
                else:
                    raise ShortlistError("unsupported commercial review row shape")
            continue
        item_codes = raw_group.get("commercial_item_codes")
        if configuration_code and isinstance(item_codes, list):
            for item_code in item_codes:
                add(raw_group, str(item_code), configuration_code)
            continue
        item_code = str(raw_group.get("commercial_item_code", ""))
        configurations = raw_group.get("configurations")
        if item_code and isinstance(configurations, list):
            for code in configurations:
                add(raw_group, item_code, str(code))
            continue
        raise ShortlistError("unsupported commercial review group")

    if len(result) != 29:
        raise ShortlistError(
            f"expected 29 commercial review decisions, found {len(result)}"
        )
    return result


def _technical_review_states(
    payload: Mapping[str, Any],
) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for raw_group in payload.get("review_groups", []):
        if not isinstance(raw_group, Mapping) or raw_group.get("area") != "active-comparison":
            continue
        classification = str(raw_group.get("classification", ""))
        reason = str(raw_group.get("reason_code", ""))
        source = str(raw_group.get("source_code", ""))
        configuration_code = str(raw_group.get("configuration_code", ""))
        items = raw_group.get("items")
        if configuration_code and isinstance(items, list):
            pairs = [(configuration_code, str(item)) for item in items]
        else:
            item = str(raw_group.get("item", ""))
            configurations = raw_group.get("configurations")
            if not item or not isinstance(configurations, list):
                raise ShortlistError("unsupported technical review group")
            pairs = [(str(code), item) for code in configurations]
        for code, item in pairs:
            attribute_code, separator, fuel_type = item.partition(":")
            comparison_key = f"{attribute_code}::{fuel_type if separator else 'all'}"
            display = (
                "nie dotyczy — skrzynia automatyczna"
                if reason == "automatic_transmission_scope"
                else "niepodane w dokładnym źródle"
            )
            result.append(
                {
                    "configuration_code": code,
                    "comparison_key": comparison_key,
                    "classification": classification,
                    "reason_code": reason,
                    "source_code": source,
                    "display_value": display,
                }
            )
    if len(result) != 22:
        raise ShortlistError(
            f"expected 22 technical review states, found {len(result)}"
        )
    return result


def _apply_reviewed_gap_states(
    catalog: dict[str, Any],
    repository: Path,
) -> None:
    payload = _read_reviewed_gap_report(repository)
    configurations = catalog.get("configurations")
    facets = catalog.get("facets")
    if not isinstance(configurations, list) or not isinstance(facets, dict):
        raise ShortlistError("invalid browser catalog for gap materialization")
    by_code = {
        str(item.get("configuration_code", "")): item
        for item in configurations
        if isinstance(item, dict)
    }
    comparison_facets = facets.get("comparison_values", [])
    facet_by_key = {
        str(item.get("key", "")): item
        for item in comparison_facets
        if isinstance(item, dict)
    }
    reviewed_on = str(payload.get("generated_on", ""))
    technical_count = 0
    for review in _technical_review_states(payload):
        configuration = by_code.get(review["configuration_code"])
        facet = facet_by_key.get(review["comparison_key"])
        if configuration is None or facet is None:
            raise ShortlistError(
                "reviewed technical gap does not match the browser catalog: "
                f"{review['configuration_code']} / {review['comparison_key']}"
            )
        values = configuration.setdefault("comparison_values", {})
        if review["comparison_key"] in values:
            raise ShortlistError(
                "reviewed technical gap already has a recorded value: "
                f"{review['configuration_code']} / {review['comparison_key']}"
            )
        values[review["comparison_key"]] = {
            **facet,
            "kind": "reviewed_gap",
            "value": "",
            "display_value": review["display_value"],
            "observation_date": reviewed_on,
            "source_code": review["source_code"],
            "review_state": review["classification"],
            "review_reason_code": review["reason_code"],
        }
        technical_count += 1

    decisions = _commercial_review_decisions(payload)
    commercial_count = 0
    for configuration_code, configuration in by_code.items():
        components = configuration.get("price_components", [])
        if not isinstance(components, list):
            continue
        for component in components:
            if not isinstance(component, dict):
                continue
            key = (configuration_code, str(component.get("code", "")))
            decision = decisions.get(key)
            if decision is None:
                continue
            component.update(decision)
            commercial_count += 1

    catalog["reviewed_gap_materialization"] = {
        "reviewed_on": reviewed_on,
        "technical_states": technical_count,
        "commercial_states": commercial_count,
        "commercial_decisions": len(decisions),
    }
'''

replace_once(
    config,
    '\n\ndef render_html(catalog: Mapping[str, Any]) -> str:\n',
    HELPERS + '\n\ndef render_html(catalog: Mapping[str, Any]) -> str:\n',
)
replace_once(
    config,
    '            _apply_supplemental_model_media(catalog, selected_repository)\n            write_atomic(arguments.html, render_html(catalog))\n',
    '            _apply_supplemental_model_media(catalog, selected_repository)\n            _apply_reviewed_gap_states(catalog, selected_repository)\n            write_atomic(arguments.html, render_html(catalog))\n',
)

pricing = ROOT / "tools/reporting/configuration_shortlist_v12_pricing.js"
replace_once(
    pricing,
    '      source_code: String(component.source_code || ""),\n      equipment_codes: unique(component.equipment_codes || [])\n',
    '      source_code: String(component.source_code || ""),\n      equipment_codes: unique(component.equipment_codes || []),\n      review_state: String(component.review_state || ""),\n      review_reason_code: String(component.review_reason_code || ""),\n      reviewed_on: String(component.reviewed_on || ""),\n      candidate_amount_pln: Number.isFinite(Number(component.candidate_amount_pln))\n        ? Number(component.candidate_amount_pln) : null,\n      candidate_source_code: String(component.candidate_source_code || "")\n',
)
replace_once(
    pricing,
    '          kind: component.kind,\n          amount: component.amount\n',
    '          kind: component.kind,\n          amount: component.amount,\n          review_state: component.review_state,\n          review_reason_code: component.review_reason_code,\n          reviewed_on: component.reviewed_on,\n          candidate_amount_pln: component.candidate_amount_pln,\n          candidate_source_code: component.candidate_source_code,\n          source_code: component.source_code\n',
)

STATUS_HELPER = r'''

  function reviewedUnknownPriceStatus(component) {
    const state = String(component && component.review_state || "");
    const reason = String(component && component.review_reason_code || "");
    const candidate = Number(component && component.candidate_amount_pln);
    const hasCandidate = Number.isFinite(candidate);
    const candidateText = hasCandidate ? formatMoney(candidate, component.currency_code || "PLN") : "";
    if (state === "source-conflict") {
      return "sprzeczne dane źródłowe — cena nie została doliczona";
    }
    if (state === "context-unmodeled") {
      if (reason === "stock-selection-and-standalone-price-are-separate-record-contexts") {
        return hasCandidate
          ? `wybrane w egzemplarzu; odrębna cena cennikowa ${candidateText} — nie doliczono`
          : "wybrane w egzemplarzu; odrębna cena nie została doliczona";
      }
      if (reason === "model-year-and-paint-price-class-not-modeled") {
        return hasCandidate
          ? `cena ${candidateText} dotyczy innego rocznika lub klasy lakieru — nie doliczono`
          : "cena zależy od rocznika lub klasy lakieru — nie doliczono";
      }
      if (reason === "model-year-stock-context-not-modeled") {
        return hasCandidate
          ? `cena ${candidateText} dotyczy zapasu MY25 — nie doliczono`
          : "cena dotyczy nieodwzorowanego zapasu modelowego — nie doliczono";
      }
      return "cena zależy od nieodwzorowanego kontekstu — nie doliczono";
    }
    if (state === "source-not-stated") return "cena niepodana w dokładnym źródle";
    return component && component.source_code
      ? "cena niepodana w źródle"
      : "brak powiązania z cennikiem";
  }
'''
replace_once(
    pricing,
    '\n\n  function selectedEquipmentStatus(item) {\n',
    STATUS_HELPER + '\n\n  function selectedEquipmentStatus(item) {\n',
)
replace_once(
    pricing,
    '        const price = component.amount === null ? "cena niepodana w źródle" : "dopłata ujęta powyżej";\n',
    '        const price = component.amount === null\n          ? reviewedUnknownPriceStatus(component)\n          : "dopłata ujęta powyżej";\n',
)
replace_once(
    pricing,
    '        const status = component.source_code\n          ? "cena niepodana w źródle"\n          : "brak powiązania z cennikiem";\n',
    '        const status = reviewedUnknownPriceStatus(component);\n',
)
replace_once(
    pricing,
    '    selectedEquipmentStatus, selectedEquipmentMarkup\n',
    '    selectedEquipmentStatus, selectedEquipmentMarkup,\n    reviewedUnknownPriceStatus\n',
)

state_path = ROOT / "project/state.json"
state = json.loads(state_path.read_text(encoding="utf-8"))
state["updated_on"] = "2026-08-02"
state["phase"] = "Reviewed Gap State Materialization"
state["reference_delivery"] = {
    "name": "Registered Source Completeness Reconciliation",
    "pull_request": 448,
    "head_sha": "7abf536dd07e3417a8604196ecb469a9d2d9b70a",
    "quality_run": 30721504297,
}
state["baseline"]["tests"] = 1788
state["current_package"] = {
    "package_id": "reviewed_gap_state_materialization_001",
    "kind": "comparison_and_price_state_materialization",
    "name": "Reviewed Gap State Materialization",
    "status": "complete",
    "goal": "Import the two exact current Spring Extreme package prices and materialize reviewed source-not-stated, source-conflict and context-unmodeled states in comparison and price presentation without filling contextual blank rows or inferring sibling values.",
    "manifest_paths": [
        "CHANGELOG.md",
        "README.md",
        "data/imports/reviewed_gap_state_materialization_20260802.csv",
        "data/master/commercial_item_configurations.csv",
        "data/reporting/reviewed_gap_state_materialization.json",
        "data/reporting/reviewed_gap_state_materialization.md",
        "project/ROADMAP.md",
        "project/SESSION_STATE.md",
        "project/packages/reviewed-gap-state-materialization-20260802.md",
        "project/state.json",
        "project/STATE_SUMMARY.md",
        "tests/test_reviewed_gap_state_materialization_20260802.py",
        "tools/apply_reviewed_gap_state_materialization_20260802.py",
        "tools/configuration_shortlist.py",
        "tools/reporting/configuration_shortlist_v12_pricing.js",
    ],
}
state["next_package"] = {
    "package_id": "spring_commercial_context_resolution_001",
    "kind": "source_conflict_and_context_resolution",
    "name": "Spring Commercial Context Resolution",
    "status": "planned",
    "goal": "Resolve the Spring Type 2 cable conflict and current paint, stock and model-year price contexts from exact official states before any further commercial import.",
    "manifest_paths": [
        "data/reporting/spring_commercial_context_resolution.json",
        "data/reporting/spring_commercial_context_resolution.md",
        "project/packages/spring-commercial-context-resolution-20260802.md",
        "project/sources/dacia-pl-spring-commercial-context-20260802.json",
        "project/state.json",
        "project/STATE_SUMMARY.md",
        "tests/test_spring_commercial_context_resolution_20260802.py",
        "tools/review_spring_commercial_context_20260802.py",
    ],
}
state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
