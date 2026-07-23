from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

from reporting import configuration_shortlist as core
from reporting.commercial_offers import collect_commercial_components

HTML_REPORT_VERSION = 1


def _safe_json(value: Mapping[str, Any]) -> str:
    return (
        json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def collect_browser_catalog(
    repository: Path,
    criteria: core.ShortlistCriteria,
) -> dict[str, Any]:
    criteria = core.normalize_criteria(criteria)
    master = repository / "data" / "master"
    models = {
        row["code"]: row for row in core.read_csv(master / "models.csv")
    }
    versions = {
        row["code"]: row for row in core.read_csv(master / "versions.csv")
    }
    attributes = {
        row["code"]: row for row in core.read_csv(master / "attributes.csv")
    }
    configurations = [
        row
        for row in core.read_csv(master / "configurations.csv")
        if row.get("status") == "active"
    ]
    if not configurations:
        raise core.ShortlistError("no active configurations found")
    configuration_codes = {row["code"] for row in configurations}

    for configuration in configurations:
        version_code = configuration.get("version_code", "")
        if version_code not in versions:
            raise core.ShortlistError(
                f"configuration references unknown version: {version_code!r}"
            )
        model_code = versions[version_code].get("model_code", "")
        if model_code not in models:
            raise core.ShortlistError(
                f"version references unknown model: {model_code!r}"
            )

    price_rows = [
        row
        for row in core.read_csv(master / "configuration_prices.csv")
        if row.get("configuration_code") in configuration_codes
        and row.get("market") == core.PRICE_MARKET
        and row.get("price_type") == core.PRICE_TYPE
        and row.get("currency_code") == core.PRICE_CURRENCY
    ]
    seat_rows = [
        row
        for row in core.read_csv(
            master / "configuration_attribute_values.csv"
        )
        if row.get("configuration_code") in configuration_codes
        and row.get("attribute_code") == "number_of_seats"
        and row.get("fuel_type_code", "") == ""
    ]
    availability_rows = [
        row
        for row in core.read_csv(
            master / "configuration_attribute_availability.csv"
        )
        if row.get("configuration_code") in configuration_codes
    ]
    as_of = core._effective_as_of(
        criteria.as_of,
        price_rows,
        seat_rows,
        availability_rows,
    )
    prices = core._latest(
        price_rows,
        ("configuration_code",),
        "price_date",
        as_of,
    )
    seats = core._latest(
        seat_rows,
        ("configuration_code",),
        "observation_date",
        as_of,
    )
    availability = core._latest(
        availability_rows,
        ("configuration_code", "attribute_code"),
        "observation_date",
        as_of,
    )
    commercial_components = collect_commercial_components(
        repository, configuration_codes, as_of
    )

    active_model_codes = {
        versions[row["version_code"]]["model_code"]
        for row in configurations
    }
    active_version_codes = {row["version_code"] for row in configurations}
    equipment_codes = {
        key[1] for key in availability if key[1]
    }
    core._validate_codes("model", criteria.models, active_model_codes)
    core._validate_codes("version", criteria.versions, active_version_codes)
    core._validate_codes(
        "equipment attribute",
        (
            *criteria.required_equipment,
            *criteria.required_standard_equipment,
        ),
        equipment_codes,
    )

    catalog_configurations: list[dict[str, Any]] = []
    equipment_counts: dict[str, Counter[str]] = {
        code: Counter() for code in sorted(equipment_codes)
    }
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
        transmission_label = {
            "manual": "manualna",
            "automatic": "automatyczna",
        }.get(transmission, transmission)
        catalog_configurations.append(
            {
                "configuration_code": code,
                "model_code": model["code"],
                "model_name": model.get("name", ""),
                "version_code": version["code"],
                "version_name": version.get("name", ""),
                "display_name": (
                    f"{model.get('name', '')} — {version.get('name', '')} · "
                    f"{configuration.get('powertrain_label', '')} · "
                    f"skrzynia {transmission_label}"
                ),
                "powertrain_label": configuration.get(
                    "powertrain_label", ""
                ),
                "transmission_type": transmission,
                "catalog_price": core._price_state(prices.get((code,))),
                "number_of_seats": core._seat_state(seats.get((code,))),
                "equipment": equipment,
                "price_components": commercial_components.get(code, []),
            }
        )

    def sort_key(item: Mapping[str, Any]) -> tuple[Any, ...]:
        price = item["catalog_price"]
        missing = price.get("state") != "recorded"
        amount = (
            float(price["amount"])
            if not missing
            else float("inf")
        )
        return (
            missing,
            amount,
            item["model_code"],
            item["version_code"],
            item["configuration_code"],
        )

    catalog_configurations.sort(key=sort_key)
    active_versions = [
        versions[code] for code in sorted(active_version_codes)
    ]
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
                "missing_configurations": (
                    len(catalog_configurations) - sum(counts.values())
                ),
                "states": dict(sorted(counts.items())),
            }
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
                }
                for code in sorted(active_model_codes)
            ],
            "versions": [
                {
                    "code": row["code"],
                    "name": row.get("name", ""),
                    "model_code": row.get("model_code", ""),
                }
                for row in active_versions
            ],
            "transmissions": sorted(
                {
                    row.get("transmission_type", "")
                    for row in configurations
                    if row.get("transmission_type", "")
                }
            ),
            "powertrains": sorted(
                {
                    row.get("powertrain_label", "")
                    for row in configurations
                    if row.get("powertrain_label", "")
                }
            ),
            "seat_counts": sorted(
                {
                    int(state["value"])
                    for state in (
                        item["number_of_seats"]
                        for item in catalog_configurations
                    )
                    if state.get("state") == "recorded"
                }
            ),
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
  <p class="lede">Snapshot źródłowy na dzień <strong>{catalog['as_of']}</strong>. Plik działa offline i nie pobiera zewnętrznych zasobów.</p>
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
    <label>Cena minimalna PLN
      <input id="minimum-price" type="number" min="0" step="100">
    </label>
    <label>Cena maksymalna PLN
      <input id="maximum-price" type="number" min="0" step="100">
    </label>
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


_CSS = r""":root{color-scheme:light;--ink:#17211b;--muted:#5e6a63;--paper:#f5f7f4;--panel:#fff;--line:#d8ded9;--accent:#1f6f43;--soft:#e5f2e9;--warn:#8b500d;--warn-soft:#fff1d9;--danger:#9c3030;--danger-soft:#fde8e8}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.45}header,main,footer{width:min(1440px,calc(100% - 32px));margin-inline:auto}header{padding:48px 0 24px}h1{margin:0;font-size:clamp(2.2rem,5vw,4.5rem);letter-spacing:-.05em}h2{margin-top:36px}.eyebrow{margin:0 0 6px;color:var(--accent);font-size:.78rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase}.lede{max-width:800px;color:var(--muted);font-size:1.08rem}.metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}.metrics div{display:grid;gap:5px;padding:18px;background:var(--panel);border:1px solid var(--line);border-radius:14px}.metrics span{color:var(--muted)}.metrics strong{font-size:2rem}.filters{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;padding:18px;margin-top:28px;background:var(--panel);border:1px solid var(--line);border-radius:16px}.filters h2{grid-column:1/-1;margin:0}.filters label{display:grid;align-content:start;gap:6px;color:var(--muted);font-size:.82rem;font-weight:700}.filters label[hidden]{display:none}.filters input,.filters select,.filters button{width:100%;min-height:42px;padding:8px 10px;border:1px solid #b9c3bb;border-radius:8px;background:#fff;color:var(--ink)}.filters select[multiple]{min-height:118px}.filters .wide{grid-column:span 2}.filters .full{grid-column:1/-1}.actions{display:flex;align-items:end}.filters button{cursor:pointer;font-weight:800}.audit{padding:16px 18px;margin-top:18px;background:var(--warn-soft);border-left:4px solid var(--warn);border-radius:8px}.audit h2{margin:0 0 8px}.audit p{margin:5px 0;color:#5f421d}.results{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.result-card{display:grid;align-content:start;gap:10px;padding:18px;background:var(--panel);border:1px solid var(--line);border-radius:16px;box-shadow:0 10px 28px rgba(27,43,33,.06)}.result-card h3{margin:0;font-size:1.35rem}.result-card h3 span{color:var(--muted);font-weight:500}.result-price{font-size:1.45rem;font-weight:850;color:var(--accent)}.configuration-code{margin:0;color:var(--muted);font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.76rem;overflow-wrap:anywhere}.result-card dl{display:grid;gap:7px;margin:0}.result-card dl div{display:grid;grid-template-columns:90px 1fr;gap:8px}.result-card dt{color:var(--muted)}.result-card dd{margin:0;font-weight:650}.equipment-list{display:flex;flex-wrap:wrap;gap:6px}.equipment-state{padding:5px 8px;border-radius:999px;background:var(--soft);color:var(--accent);font-size:.72rem;font-weight:750}.equipment-missing,.equipment-not_available{background:var(--danger-soft);color:var(--danger)}details{color:var(--muted);font-size:.8rem}.empty{grid-column:1/-1;padding:28px;background:var(--panel);border:1px dashed var(--line);border-radius:14px;text-align:center}footer{padding:40px 0 56px;color:var(--muted)}@media(max-width:1050px){.filters{grid-template-columns:repeat(2,minmax(0,1fr))}.results{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:680px){header,main,footer{width:min(100% - 20px,1440px)}.metrics,.filters,.results{grid-template-columns:1fr}.filters .wide,.filters .full{grid-column:auto}}@media print{body{background:#fff}.filters{display:none}.results{grid-template-columns:repeat(2,minmax(0,1fr))}.result-card{break-inside:avoid;box-shadow:none}}"""
