from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping

from cache_model_media import MediaCacheError, data_uri as model_media_data_uri

from reporting import configuration_shortlist as core
from reporting.cargo_context import (
    CARGO_ATTRIBUTE_CODE,
    CargoContextError,
    annotate_scalar_values,
    read_context_rows,
    semantic_signature,
    technical_context,
)
from reporting.commercial_offers import collect_commercial_components

HTML_REPORT_VERSION = 1
_MODEL_MEDIA_SOURCE = Path("project/sources/dacia-pl-model-media-20260724.json")
_OFFICIAL_MEDIA_PREFIXES = (
    "https://www.dacia.pl/",
    "https://cdn.group.renault.com/",
)
_ENUM_LABELS_PL = {
    "4x4": "napęd 4×4",
    "fwd": "napęd na przednie koła",
    "euro_6": "Euro 6",
    "euro_6e_bis": "Euro 6e BIS",
    "hev": "pełna hybryda",
    "mhev": "miękka hybryda",
    "dct": "automatyczna dwusprzęgłowa",
    "hybrid": "automatyczna hybrydowa",
    "manual": "manualna",
    "lithium_ion": "litowo-jonowy",
    "direct_injection": "wtrysk bezpośredni",
    "multi_point_injection": "wtrysk wielopunktowy",
    "port_injection": "wtrysk pośredni",
}
_FUEL_LABELS_PL = {
    "petrol": "benzyna",
    "lpg": "LPG",
    "diesel": "olej napędowy",
    "electricity": "energia elektryczna",
    "lpg_petrol": "LPG / benzyna",
}
_UNIT_LABELS = {
    "cm3": "cm³",
    "m3": "m³",
    "g/km": "g/km",
    "l/100 km": "l/100 km",
}


def _safe_json(value: Mapping[str, Any]) -> str:
    return (
        json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def _read_json_object(path: Path, label: str, *, optional: bool = False) -> dict[str, Any]:
    if optional and not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise core.ShortlistError(f"cannot read {label}: {exc}") from exc
    if not isinstance(payload, dict):
        raise core.ShortlistError(f"invalid {label}: expected JSON object")
    return payload


def _attribute_labels_pl() -> dict[str, str]:
    payload = _read_json_object(
        Path(__file__).with_name("configuration_attribute_labels_pl.json"),
        "Polish comparison labels",
    )
    if not all(isinstance(code, str) and isinstance(label, str) for code, label in payload.items()):
        raise core.ShortlistError("invalid Polish comparison label contract")
    return {code: label for code, label in payload.items() if label.strip()}


def _model_media(repository: Path) -> dict[str, dict[str, str]]:
    payload = _read_json_object(
        repository / _MODEL_MEDIA_SOURCE,
        "official Dacia model media source",
        optional=True,
    )
    models = payload.get("models", {})
    if not isinstance(models, dict):
        return {}
    captured_on = str(payload.get("captured_on", ""))
    result: dict[str, dict[str, str]] = {}
    for model_code, source in models.items():
        if not isinstance(model_code, str) or not isinstance(source, dict):
            continue
        image_url = str(source.get("image_url", ""))
        page_url = str(source.get("source_page_url", ""))
        if not image_url.startswith(_OFFICIAL_MEDIA_PREFIXES):
            continue
        if not page_url.startswith("https://www.dacia.pl/"):
            continue
        result[model_code] = {
            "image_url": image_url,
            "source_page_url": page_url,
            "source_name": str(source.get("source_name", "Dacia Polska")),
            "captured_on": captured_on,
        }
        try:
            local_image = model_media_data_uri(repository, model_code)
        except (MediaCacheError, OSError):
            local_image = ""
        if local_image:
            result[model_code]["image_data_uri"] = local_image
    return result


def _enum_labels(master: Path) -> dict[str, dict[str, str]]:
    mapping_path = master / "attribute_enum_domains.csv"
    if not mapping_path.exists():
        return {}
    result: dict[str, dict[str, str]] = {}
    for mapping in core.read_csv(mapping_path):
        if mapping.get("status") != "active":
            continue
        domain_path = master / "enums" / mapping.get("domain_file", "")
        if not domain_path.exists():
            continue
        result[mapping.get("attribute_code", "")] = {
            row.get("code", ""): row.get("name", row.get("code", ""))
            for row in core.read_csv(domain_path)
            if row.get("status", "active") == "active" and row.get("code")
        }
    return result


def _comparison_key(
    attribute_code: str,
    fuel_type_code: str,
    cargo_context_signature: str = "",
    gear_number: str = "",
) -> str:
    base = f"{attribute_code}::{fuel_type_code or 'all'}"
    if gear_number:
        base = f"{base}::gear::{gear_number}"
    return (
        base
        if not cargo_context_signature
        else f"{base}::cargo::{cargo_context_signature}"
    )


def _unit_label(unit: str) -> str:
    return _UNIT_LABELS.get(unit, unit)


def _number_label(value: str) -> str:
    return value.replace(".", ",")


def _scalar_display(
    value: str,
    attribute: Mapping[str, str],
    enum_labels: Mapping[str, Mapping[str, str]],
) -> str:
    data_type = attribute.get("data_type", "")
    if data_type == "boolean":
        return {"true": "tak", "false": "nie"}.get(value.lower(), value)
    if data_type == "enum":
        translated = _ENUM_LABELS_PL.get(value)
        if translated:
            return translated
        return enum_labels.get(attribute.get("code", ""), {}).get(value, value)
    if data_type in {"integer", "decimal"}:
        return _number_label(value)
    return value


def _technical_value_state(
    row: Mapping[str, str],
    attribute: Mapping[str, str],
    labels: Mapping[str, str],
    enum_labels: Mapping[str, Mapping[str, str]],
) -> dict[str, Any]:
    attribute_code = row.get("attribute_code", "")
    fuel_type_code = row.get("fuel_type_code", "")
    unit = _unit_label(attribute.get("unit", ""))
    value = _scalar_display(row.get("value", ""), attribute, enum_labels)
    display_value = f"{value} {unit}".strip()
    cargo_context = row.get("_cargo_context")
    context_payload = (
        dict(cargo_context)
        if isinstance(cargo_context, Mapping)
        else None
    )
    signature = str(row.get("_cargo_context_signature", ""))
    gear_number = str(row.get("gear_number", ""))
    return {
        "key": _comparison_key(attribute_code, fuel_type_code, signature, gear_number),
        "attribute_code": attribute_code,
        "label": labels.get(attribute_code, attribute.get("name", attribute_code)),
        "category": attribute.get("category", "Pozostałe"),
        "data_type": attribute.get("data_type", ""),
        "unit": unit,
        "fuel_type_code": fuel_type_code,
        "fuel_type_label": _FUEL_LABELS_PL.get(fuel_type_code, fuel_type_code),
        "gear_number": gear_number,
        "cargo_context": context_payload,
        "cargo_context_signature": signature,
        "cargo_context_label": (
            semantic_signature(context_payload)
            if context_payload is not None
            else ""
        ),
        "context": technical_context(fuel_type_code, context_payload, gear_number),
        "kind": "value",
        "value": row.get("value", ""),
        "display_value": display_value,
        "observation_date": row.get("observation_date", ""),
        "source_code": row.get("source_code", ""),
    }


def _technical_range_state(
    row: Mapping[str, str],
    attribute: Mapping[str, str],
    labels: Mapping[str, str],
) -> dict[str, Any]:
    attribute_code = row.get("attribute_code", "")
    fuel_type_code = row.get("fuel_type_code", "")
    unit = _unit_label(attribute.get("unit", ""))
    minimum = _number_label(row.get("minimum_value", ""))
    maximum = _number_label(row.get("maximum_value", ""))
    display_value = f"{minimum}–{maximum} {unit}".strip()
    return {
        "key": _comparison_key(attribute_code, fuel_type_code),
        "attribute_code": attribute_code,
        "label": labels.get(attribute_code, attribute.get("name", attribute_code)),
        "category": attribute.get("category", "Pozostałe"),
        "data_type": attribute.get("data_type", ""),
        "unit": unit,
        "fuel_type_code": fuel_type_code,
        "fuel_type_label": _FUEL_LABELS_PL.get(fuel_type_code, fuel_type_code),
        "kind": "range",
        "minimum_value": row.get("minimum_value", ""),
        "maximum_value": row.get("maximum_value", ""),
        "lower_inclusive": row.get("lower_inclusive", ""),
        "upper_inclusive": row.get("upper_inclusive", ""),
        "display_value": display_value,
        "observation_date": row.get("observation_date", ""),
        "source_code": row.get("source_code", ""),
    }


def collect_browser_catalog(
    repository: Path,
    criteria: core.ShortlistCriteria,
) -> dict[str, Any]:
    criteria = core.normalize_criteria(criteria)
    master = repository / "data" / "master"
    models = {row["code"]: row for row in core.read_csv(master / "models.csv")}
    versions = {row["code"]: row for row in core.read_csv(master / "versions.csv")}
    attributes = {row["code"]: row for row in core.read_csv(master / "attributes.csv")}
    labels = _attribute_labels_pl()
    enum_labels = _enum_labels(master)
    media = _model_media(repository)
    configurations = [
        row for row in core.read_csv(master / "configurations.csv")
        if row.get("status") == "active"
    ]
    if not configurations:
        raise core.ShortlistError("no active configurations found")
    configuration_codes = {row["code"] for row in configurations}

    for configuration in configurations:
        version_code = configuration.get("version_code", "")
        if version_code not in versions:
            raise core.ShortlistError(f"configuration references unknown version: {version_code!r}")
        model_code = versions[version_code].get("model_code", "")
        if model_code not in models:
            raise core.ShortlistError(f"version references unknown model: {model_code!r}")

    price_rows = [
        row for row in core.read_csv(master / "configuration_prices.csv")
        if row.get("configuration_code") in configuration_codes
        and row.get("market") == core.PRICE_MARKET
        and row.get("price_type") == core.PRICE_TYPE
        and row.get("currency_code") == core.PRICE_CURRENCY
    ]
    value_rows = [
        row for row in core.read_csv(master / "configuration_attribute_values.csv")
        if row.get("configuration_code") in configuration_codes
    ]
    try:
        value_rows = annotate_scalar_values(
            value_rows,
            read_context_rows(master, core.read_csv),
        )
    except CargoContextError as exc:
        raise core.ShortlistError(str(exc)) from exc
    range_path = master / "configuration_attribute_value_ranges.csv"
    range_rows = [
        row for row in core.read_csv(range_path)
        if row.get("configuration_code") in configuration_codes
    ] if range_path.exists() else []
    seat_rows = [
        row for row in value_rows
        if row.get("attribute_code") == "number_of_seats"
        and row.get("fuel_type_code", "") == ""
    ]
    availability_rows = [
        row for row in core.read_csv(master / "configuration_attribute_availability.csv")
        if row.get("configuration_code") in configuration_codes
    ]
    as_of = core._effective_as_of(
        criteria.as_of,
        price_rows,
        [*value_rows, *range_rows],
        availability_rows,
    )
    prices = core._latest(price_rows, ("configuration_code",), "price_date", as_of)
    seats = core._latest(seat_rows, ("configuration_code",), "observation_date", as_of)
    availability = core._latest(
        availability_rows,
        ("configuration_code", "attribute_code"),
        "observation_date",
        as_of,
    )
    latest_values = core._latest(
        value_rows,
        (
            "configuration_code",
            "attribute_code",
            "fuel_type_code",
            "gear_number",
            "_cargo_context_signature",
        ),
        "observation_date",
        as_of,
    )
    latest_ranges = core._latest(
        range_rows,
        ("configuration_code", "attribute_code", "fuel_type_code"),
        "observation_date",
        as_of,
    )
    commercial_components = collect_commercial_components(repository, configuration_codes, as_of)

    value_index: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    comparison_facets: dict[str, dict[str, Any]] = {}
    for (configuration_code, attribute_code, _, _, _), row in latest_values.items():
        attribute = attributes.get(attribute_code, {"code": attribute_code, "name": attribute_code})
        state = _technical_value_state(row, attribute, labels, enum_labels)
        value_index[configuration_code][state["key"]] = state
        comparison_facets[state["key"]] = {key: state[key] for key in (
            "key", "attribute_code", "label", "category", "data_type", "unit",
            "fuel_type_code", "fuel_type_label", "gear_number", "cargo_context",
            "cargo_context_signature", "cargo_context_label", "context",
        )}
    for (configuration_code, attribute_code, _), row in latest_ranges.items():
        attribute = attributes.get(attribute_code, {"code": attribute_code, "name": attribute_code})
        state = _technical_range_state(row, attribute, labels)
        value_index[configuration_code][state["key"]] = state
        comparison_facets[state["key"]] = {key: state[key] for key in (
            "key", "attribute_code", "label", "category", "data_type", "unit",
            "fuel_type_code", "fuel_type_label",
        )}

    active_model_codes = {versions[row["version_code"]]["model_code"] for row in configurations}
    active_version_codes = {row["version_code"] for row in configurations}
    equipment_codes = {key[1] for key in availability if key[1]}
    core._validate_codes("model", criteria.models, active_model_codes)
    core._validate_codes("version", criteria.versions, active_version_codes)
    core._validate_codes(
        "equipment attribute",
        (*criteria.required_equipment, *criteria.required_standard_equipment),
        equipment_codes,
    )

    catalog_configurations: list[dict[str, Any]] = []
    equipment_counts: dict[str, Counter[str]] = {code: Counter() for code in sorted(equipment_codes)}
    for configuration in configurations:
        code = configuration["code"]
        version = versions[configuration["version_code"]]
        model = models[version["model_code"]]
        equipment: dict[str, dict[str, Any]] = {}
        for attribute_code in sorted(equipment_codes):
            row = availability.get((code, attribute_code))
            if row is None:
                continue
            status = row.get("availability_status", "")
            equipment_counts[attribute_code][status] += 1
            equipment[attribute_code] = {
                "availability_status": status,
                "observation_date": row.get("observation_date", ""),
                "source_code": row.get("source_code", ""),
            }
        transmission = configuration.get("transmission_type", "")
        transmission_label = {"manual": "manualna", "automatic": "automatyczna"}.get(transmission, transmission)
        model_media = media.get(model["code"], {})
        catalog_configurations.append(
            {
                "configuration_code": code,
                "model_code": model["code"],
                "model_name": model.get("name", ""),
                "model_media": model_media,
                "version_code": version["code"],
                "version_name": version.get("name", ""),
                "display_name": (
                    f"{model.get('name', '')} — {version.get('name', '')} · "
                    f"{configuration.get('powertrain_label', '')} · skrzynia {transmission_label}"
                ),
                "powertrain_label": configuration.get("powertrain_label", ""),
                "transmission_type": transmission,
                "catalog_price": core._price_state(prices.get((code,))),
                "number_of_seats": core._seat_state(seats.get((code,))),
                "comparison_values": value_index.get(code, {}),
                "cargo_volumes": sorted(
                    [
                        state
                        for state in value_index.get(code, {}).values()
                        if state.get("attribute_code") == CARGO_ATTRIBUTE_CODE
                    ],
                    key=lambda state: (
                        state.get("cargo_context_signature", ""),
                        state.get("observation_date", ""),
                        state.get("key", ""),
                    ),
                ),
                "equipment": equipment,
                "price_components": commercial_components.get(code, []),
            }
        )

    def sort_key(item: Mapping[str, Any]) -> tuple[Any, ...]:
        price = item["catalog_price"]
        missing = price.get("state") != "recorded"
        amount = float(price["amount"]) if not missing else float("inf")
        return (missing, amount, item["model_code"], item["version_code"], item["configuration_code"])

    catalog_configurations.sort(key=sort_key)
    model_min_prices: dict[str, float] = {}
    for item in catalog_configurations:
        price = item["catalog_price"]
        if price.get("state") != "recorded":
            continue
        model_code = item["model_code"]
        amount = float(price["amount"])
        current = model_min_prices.get(model_code)
        if current is None or amount < current:
            model_min_prices[model_code] = amount
    ordered_model_codes = sorted(
        active_model_codes,
        key=lambda code: (
            code not in model_min_prices,
            model_min_prices.get(code, float("inf")),
            models[code].get("name", ""),
            code,
        ),
    )
    active_versions = [versions[code] for code in sorted(active_version_codes)]
    equipment_facets = []
    for code in sorted(equipment_codes):
        attribute = attributes.get(code, {})
        counts = equipment_counts[code]
        equipment_facets.append(
            {
                "code": code,
                "name": attribute.get("name", code),
                "category": attribute.get("category", ""),
                "recorded_configurations": sum(counts.values()),
                "missing_configurations": len(catalog_configurations) - sum(counts.values()),
                "states": dict(sorted(counts.items())),
            }
        )

    comparison_value_facets = sorted(
        comparison_facets.values(),
        key=lambda item: (
            item.get("category", ""),
            item.get("label", ""),
            item.get("fuel_type_label", ""),
            item.get("key", ""),
        ),
    )
    return {
        "version": HTML_REPORT_VERSION,
        "as_of": as_of,
        "price_dimension": {
            "market": core.PRICE_MARKET,
            "price_type": core.PRICE_TYPE,
            "currency_code": core.PRICE_CURRENCY,
        },
        "initial_filters": core._filters_payload(criteria),
        "facets": {
            "models": [
                {
                    "code": code,
                    "name": models[code].get("name", ""),
                    "media": media.get(code, {}),
                    "minimum_catalog_price_pln": (
                        int(model_min_prices[code])
                        if code in model_min_prices
                        and model_min_prices[code].is_integer()
                        else model_min_prices.get(code)
                    ),
                }
                for code in ordered_model_codes
            ],
            "versions": [
                {"code": row["code"], "name": row.get("name", ""), "model_code": row.get("model_code", "")}
                for row in active_versions
            ],
            "transmissions": sorted({
                row.get("transmission_type", "") for row in configurations
                if row.get("transmission_type", "")
            }),
            "powertrains": sorted({
                row.get("powertrain_label", "") for row in configurations
                if row.get("powertrain_label", "")
            }),
            "seat_counts": sorted({
                int(state["value"])
                for state in (item["number_of_seats"] for item in catalog_configurations)
                if state.get("state") == "recorded"
            }),
            "comparison_values": comparison_value_facets,
            "equipment": equipment_facets,
        },
        "configurations": catalog_configurations,
    }

def render_html(catalog: Mapping[str, Any]) -> str:
    script_path = Path(__file__).with_name(
        "configuration_shortlist_browser.js"
    )
    try:
        script = script_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise core.ShortlistError(
            f"cannot read browser filter script: {exc}"
        ) from exc
    payload = _safe_json(catalog)
    return f"""<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="generator" content="Dacia Knowledge Base">
<title>Interaktywna shortlista konfiguracji Dacia</title>
<style>{_CSS}</style>
</head>
<body>
<header>
  <p class="eyebrow">Dacia Knowledge Base</p>
  <h1>Interaktywna shortlista konfiguracji</h1>
  <p class="lede">Snapshot źródłowy na dzień <strong>{catalog['as_of']}</strong>. Oficjalne zdjęcia modeli są osadzone z lokalnej pamięci podręcznej; przy braku sieci używany jest zapisany plik lub lokalna sylwetka zastępcza.</p>
</header>
<main>
  <section class="metrics" aria-label="Podsumowanie wyników">
    <div><span>Dopasowane</span><strong id="matched-count">0</strong></div>
    <div><span>Wykluczone</span><strong id="excluded-count">0</strong></div>
    <div><span>Brak ceny</span><strong id="missing-price-count">0</strong></div>
    <div><span>Brak liczby miejsc</span><strong id="missing-seats-count">0</strong></div>
  </section>
  <form id="filters" class="filters">
    <h2>Filtry</h2>
    <label>Modele
      <select id="models" multiple size="4"></select>
    </label>
    <label id="versions-field" hidden>Wersje
      <select id="versions" multiple size="5" disabled></select>
    </label>
    <label>Skrzynia
      <select id="transmissions"></select>
    </label>
    <label>Napędy
      <select id="powertrains" multiple size="5"></select>
    </label>
    <div class="price-range-row">
      <label>Cena minimalna PLN
        <input id="minimum-price" type="number" min="0" step="100">
      </label>
      <label>Cena maksymalna PLN
        <input id="maximum-price" type="number" min="0" step="100">
      </label>
    </div>
    <label>Liczba miejsc
      <select id="seats"></select>
    </label>
    <label class="full equipment-field">Wyposażenie
      <select id="required-equipment" multiple size="8"></select>
    </label>
    <div class="actions full">
      <button id="reset" type="button">Wyczyść wszystkie filtry</button>
    </div>
  </form>
  <section aria-labelledby="results-heading">
    <h2 id="results-heading">Konfiguracje</h2>
    <div id="results" class="results" aria-live="polite"></div>
  </section>
</main>
<footer>
  <p>Format interaktywnej shortlisty HTML v{HTML_REPORT_VERSION}. Brak stwierdzenia źródłowego pozostaje niewiadomą i nigdy nie jest zamieniany na wartość domyślną.</p>
</footer>
<script id="configuration-catalog" type="application/json">{payload}</script>
<script>{script}</script>
</body>
</html>
"""


_CSS = r""":root{color-scheme:light;--ink:#17211b;--muted:#5e6a63;--paper:#f5f7f4;--panel:#fff;--line:#d8ded9;--accent:#1f6f43;--soft:#e5f2e9;--config-bg:#151918;--config-panel:#202523;--config-line:#6e746e;--config-text:#f8f6ee;--warn:#8b500d;--warn-soft:#fff1d9;--danger:#9c3030;--danger-soft:#fde8e8}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.45}header,main,footer{width:min(1440px,calc(100% - 32px));margin-inline:auto}header{padding:48px 0 24px}h1{margin:0;font-size:clamp(2.2rem,5vw,4.5rem);letter-spacing:-.05em}h2{margin-top:36px}.eyebrow{margin:0 0 6px;color:var(--accent);font-size:.78rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase}.lede{max-width:800px;color:var(--muted);font-size:1.08rem}.metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}.metrics div{display:grid;gap:5px;padding:18px;background:var(--panel);border:1px solid var(--line);border-radius:14px}.metrics span{color:var(--muted)}.metrics strong{font-size:2rem}.filters{display:grid;grid-template-columns:1fr;gap:16px;padding:22px;margin-top:28px;background:var(--config-bg);color:var(--config-text);border:1px solid #2d3431;border-radius:4px}.filters h2{grid-column:1/-1;margin:0;color:var(--config-text);font-size:1.8rem}.filters label{display:grid;align-content:start;gap:7px;color:var(--config-text);font-size:.9rem;font-weight:800}.filters label[hidden]{display:none}.filters input,.filters select,.filters button{width:100%;min-height:44px;padding:9px 11px;border:1px solid var(--config-line);border-radius:4px;background:var(--config-panel);color:var(--config-text)}.filters select[multiple]{min-height:118px}.filters .wide,.filters .full{grid-column:1}.price-range-row{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:14px}.actions{display:flex;align-items:end}.filters button{cursor:pointer;font-weight:800}.filters button:hover{border-color:#b9c39d}.filters input:focus,.filters select:focus,.filters button:focus-visible{outline:3px solid rgba(191,205,154,.32);outline-offset:2px}.audit{padding:16px 18px;margin-top:18px;background:var(--warn-soft);border-left:4px solid var(--warn);border-radius:8px}.audit h2{margin:0 0 8px}.audit p{margin:5px 0;color:#5f421d}.results{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.result-card{display:grid;align-content:start;gap:10px;padding:18px;background:var(--panel);border:1px solid var(--line);border-radius:16px;box-shadow:0 10px 28px rgba(27,43,33,.06)}.result-card-hero{display:grid;grid-template-columns:minmax(180px,42%) minmax(0,1fr);align-items:center;gap:14px}.result-card-title{display:grid;gap:3px}.result-model-name{margin:0;color:var(--accent);font-size:.82rem;font-weight:850;letter-spacing:.06em;text-transform:uppercase}.result-card h3{margin:0;font-size:1.5rem}.result-variant-name{margin:0;color:var(--muted);font-size:.82rem;font-weight:650}.result-card h3 span{color:var(--muted);font-weight:500}.result-price{font-size:1.45rem;font-weight:850;color:var(--accent)}.configuration-code{display:none!important}.result-card dl{display:grid;gap:7px;margin:0}.result-card dl div{display:grid;grid-template-columns:90px 1fr;gap:8px}.result-card dt{color:var(--muted)}.result-card dd{margin:0;font-weight:650}.equipment-list{display:flex;flex-wrap:wrap;gap:6px}.equipment-state{padding:5px 8px;border-radius:999px;background:var(--soft);color:var(--accent);font-size:.72rem;font-weight:750}.equipment-missing,.equipment-not_available{background:var(--danger-soft);color:var(--danger)}.model-thumbnail-host{display:grid;place-items:center;min-height:120px}.model-thumbnail-host img,.model-thumbnail-host svg{display:block;width:100%;max-height:190px;object-fit:contain}details{color:var(--muted);font-size:.8rem}.empty{grid-column:1/-1;padding:28px;background:var(--panel);border:1px dashed var(--line);border-radius:14px;text-align:center}footer{padding:40px 0 56px;color:var(--muted)}@media(max-width:1050px){.results{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:680px){header,main,footer{width:min(100% - 20px,1440px)}.metrics,.results{grid-template-columns:1fr}.result-card-hero{grid-template-columns:1fr}.filters .wide,.filters .full{grid-column:1}}@media print{body{background:#fff}.filters{display:none}.results{grid-template-columns:repeat(2,minmax(0,1fr))}.result-card{break-inside:avoid;box-shadow:none}}"""
