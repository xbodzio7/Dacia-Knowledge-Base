from __future__ import annotations

import csv
import html
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

from reporting.configuration_comparison_bundle import discover_scopes
from reporting.configuration_shortlist import ShortlistCriteria
from reporting.configuration_shortlist_html import collect_browser_catalog

VIEW_VERSION = 1
_MODEL_ORDER = {
    "sandero_iii": 10,
    "sandero_stepway_iii": 20,
    "jogger": 30,
    "duster_iii": 40,
    "bigster": 50,
    "spring": 60,
}
_TRANSMISSION_LABELS = {
    "manual": "manualna",
    "automatic": "automatyczna",
}


class CrossModelViewError(ValueError):
    """Raised when a scope-preserving cross-model view cannot be built."""


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read_csv(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames:
                raise CrossModelViewError(f"missing CSV header: {path}")
            return list(reader)
    except OSError as exc:
        raise CrossModelViewError(f"cannot read CSV file {path}: {exc}") from exc


def _price_amount(item: Mapping[str, Any]) -> int | None:
    price = item.get("catalog_price")
    if not isinstance(price, Mapping) or price.get("state") != "recorded":
        return None
    raw = price.get("amount")
    try:
        return int(str(raw))
    except (TypeError, ValueError) as exc:
        raise CrossModelViewError(
            f"invalid catalogue price for {item.get('configuration_code')}: {raw!r}"
        ) from exc


def _seat_value(item: Mapping[str, Any]) -> int | None:
    state = item.get("number_of_seats")
    if not isinstance(state, Mapping) or state.get("state") != "recorded":
        return None
    raw = state.get("value")
    try:
        return int(str(raw))
    except (TypeError, ValueError) as exc:
        raise CrossModelViewError(
            f"invalid seat value for {item.get('configuration_code')}: {raw!r}"
        ) from exc


def _model_sort_key(item: Mapping[str, Any]) -> tuple[int, str]:
    code = str(item.get("model_code", ""))
    return (_MODEL_ORDER.get(code, 999), str(item.get("model_name", code)))


def _scope_sort_key(item: Mapping[str, Any]) -> tuple[int, str, str]:
    model_codes = item.get("model_codes", [])
    first = str(model_codes[0]) if isinstance(model_codes, list) and model_codes else ""
    return (
        _MODEL_ORDER.get(first, 999),
        str(item.get("label", "")),
        str(item.get("slug", "")),
    )


def _scope_label(
    model_names: Sequence[str],
    configurations: Sequence[Mapping[str, Any]],
) -> str:
    powertrains = sorted(
        {
            str(item.get("powertrain_label", "")).strip()
            for item in configurations
            if str(item.get("powertrain_label", "")).strip()
        }
    )
    transmissions = sorted(
        {
            _TRANSMISSION_LABELS.get(
                str(item.get("transmission_type", "")),
                str(item.get("transmission_type", "")),
            )
            for item in configurations
            if str(item.get("transmission_type", "")).strip()
        }
    )
    seats = sorted(
        {
            value
            for item in configurations
            if (value := _seat_value(item)) is not None
        }
    )
    parts = [" / ".join(model_names)]
    if powertrains:
        parts.append(" / ".join(powertrains))
    if transmissions:
        parts.append(" / ".join(transmissions))
    if seats:
        suffix = "miejsce" if seats == [1] else "miejsc"
        parts.append(f"{' / '.join(str(value) for value in seats)} {suffix}")
    return " · ".join(parts)


def collect_view(repository: Path) -> dict[str, Any]:
    master = repository / "data" / "master"
    models = {row["code"]: row for row in _read_csv(master / "models.csv")}
    versions = {row["code"]: row for row in _read_csv(master / "versions.csv")}
    configurations = {
        row["code"]: row
        for row in _read_csv(master / "configurations.csv")
        if row.get("status") == "active"
    }
    catalog = collect_browser_catalog(repository, ShortlistCriteria())
    raw_catalog = catalog.get("configurations")
    if not isinstance(raw_catalog, list):
        raise CrossModelViewError("browser catalog configurations are missing")
    catalog_index = {
        str(item.get("configuration_code", "")): item
        for item in raw_catalog
        if isinstance(item, Mapping)
    }
    if set(catalog_index) != set(configurations):
        raise CrossModelViewError(
            "browser catalog does not cover every active configuration exactly once"
        )

    configuration_model: dict[str, str] = {}
    for code, configuration in configurations.items():
        version_code = configuration.get("version_code", "")
        version = versions.get(version_code)
        if version is None:
            raise CrossModelViewError(
                f"configuration references unknown version: {code} -> {version_code}"
            )
        model_code = version.get("model_code", "")
        if model_code not in models:
            raise CrossModelViewError(
                f"version references unknown model: {version_code} -> {model_code}"
            )
        configuration_model[code] = model_code

    scopes = discover_scopes(repository)
    mapped_codes: list[str] = []
    scope_records: list[dict[str, Any]] = []
    model_scope_slugs: dict[str, list[str]] = defaultdict(list)
    model_shared_scope_count: dict[str, int] = defaultdict(int)
    model_exclusive_scope_count: dict[str, int] = defaultdict(int)

    for scope in scopes:
        codes = list(scope.configuration_codes)
        mapped_codes.extend(codes)
        try:
            items = [catalog_index[code] for code in codes]
        except KeyError as exc:
            raise CrossModelViewError(
                f"scope references unknown active configuration: {scope.slug}"
            ) from exc
        model_codes = sorted(
            {configuration_model[code] for code in codes},
            key=lambda code: (_MODEL_ORDER.get(code, 999), code),
        )
        model_names = [models[code].get("name", code) for code in model_codes]
        mixed_model = len(model_codes) > 1
        for model_code in model_codes:
            model_scope_slugs[model_code].append(scope.slug)
            if mixed_model:
                model_shared_scope_count[model_code] += 1
            else:
                model_exclusive_scope_count[model_code] += 1
        pair_count = len(codes) * (len(codes) - 1) // 2
        scope_records.append(
            {
                "slug": scope.slug,
                "label": _scope_label(model_names, items),
                "model_codes": model_codes,
                "model_names": model_names,
                "mixed_model": mixed_model,
                "configuration_count": len(codes),
                "pair_count": pair_count,
                "technical_slot_count": len(
                    scope.completeness_spec.get("technical_slots", [])
                ),
                "equipment_slot_count": len(
                    scope.completeness_spec.get("equipment_slots", [])
                ),
                "configuration_codes": codes,
                "configuration_labels": [
                    str(item.get("display_name", item.get("configuration_code", "")))
                    for item in items
                ],
                "comparison_paths": {
                    "html": (
                        "../comparison-bundle/"
                        f"{scope.slug}.comparison.html"
                    ),
                    "json": (
                        "../comparison-bundle/"
                        f"{scope.slug}.comparison.json"
                    ),
                    "markdown": (
                        "../comparison-bundle/"
                        f"{scope.slug}.comparison.md"
                    ),
                    "differences_csv": (
                        "../comparison-bundle/"
                        f"{scope.slug}.differences.csv"
                    ),
                },
            }
        )

    if len(mapped_codes) != len(set(mapped_codes)):
        raise CrossModelViewError(
            "an active configuration belongs to more than one reporting scope"
        )
    if set(mapped_codes) != set(configurations):
        raise CrossModelViewError(
            "reporting scopes do not cover every active configuration exactly once"
        )

    model_records: list[dict[str, Any]] = []
    for model_code in sorted(
        set(configuration_model.values()),
        key=lambda code: (_MODEL_ORDER.get(code, 999), code),
    ):
        codes = sorted(
            code
            for code, assigned_model in configuration_model.items()
            if assigned_model == model_code
        )
        items = [catalog_index[code] for code in codes]
        prices = [
            amount
            for item in items
            if (amount := _price_amount(item)) is not None
        ]
        seats = sorted(
            {
                value
                for item in items
                if (value := _seat_value(item)) is not None
            }
        )
        media = next(
            (
                dict(item["model_media"])
                for item in items
                if isinstance(item.get("model_media"), Mapping)
            ),
            {},
        )
        model = models[model_code]
        model_records.append(
            {
                "model_code": model_code,
                "model_name": model.get("name", model_code),
                "generation": model.get("generation", ""),
                "body_type_code": model.get("body_type_code", ""),
                "segment_code": model.get("segment_code", ""),
                "configuration_count": len(codes),
                "version_count": len(
                    {configurations[code]["version_code"] for code in codes}
                ),
                "catalog_price": {
                    "state": "recorded" if prices else "not_stated",
                    "currency": "PLN" if prices else "",
                    "minimum": min(prices) if prices else None,
                    "maximum": max(prices) if prices else None,
                    "recorded_count": len(prices),
                    "missing_count": len(codes) - len(prices),
                },
                "recorded_seat_values": seats,
                "seat_summary_state": "recorded" if seats else "not_stated",
                "transmission_values": sorted(
                    {
                        str(item.get("transmission_type", ""))
                        for item in items
                        if str(item.get("transmission_type", ""))
                    }
                ),
                "powertrain_labels": sorted(
                    {
                        str(item.get("powertrain_label", ""))
                        for item in items
                        if str(item.get("powertrain_label", ""))
                    }
                ),
                "exclusive_scope_count": model_exclusive_scope_count[model_code],
                "shared_scope_count": model_shared_scope_count[model_code],
                "scope_slugs": sorted(model_scope_slugs[model_code]),
                "model_media": media,
            }
        )

    scope_records.sort(key=_scope_sort_key)
    model_records.sort(key=_model_sort_key)
    mixed_scopes = [item for item in scope_records if item["mixed_model"]]
    total_pairs = sum(int(item["pair_count"]) for item in scope_records)
    price_count = sum(
        int(item["catalog_price"]["recorded_count"])
        for item in model_records
    )
    return {
        "version": VIEW_VERSION,
        "kind": "scope_preserving_cross_model_comparison_view",
        "as_of": catalog.get("as_of"),
        "summary": {
            "model_family_count": len(model_records),
            "reporting_scope_count": len(scope_records),
            "single_model_scope_count": len(scope_records) - len(mixed_scopes),
            "mixed_model_scope_count": len(mixed_scopes),
            "active_configuration_count": len(configurations),
            "within_scope_pair_count": total_pairs,
            "catalog_price_recorded_count": price_count,
            "cross_scope_pairs_generated": False,
            "ranking_generated": False,
            "recommendations_generated": False,
            "inferred_values_generated": False,
        },
        "navigation": {
            "shortlist_html": "../shortlist/configuration-shortlist.html",
            "comparison_bundle_manifest": (
                "../comparison-bundle/comparison-bundle-manifest.json"
            ),
            "pair_generation_rule": (
                "Links open only existing scope reports. Model cards never "
                "generate a configuration pair."
            ),
            "unknown_handling": (
                "Missing model-level facts remain not stated and are never "
                "converted to zero, false or an assumed value."
            ),
        },
        "models": model_records,
        "scopes": scope_records,
    }


def render_json(view: Mapping[str, Any]) -> str:
    return json.dumps(view, ensure_ascii=False, indent=2) + "\n"


def _format_price(value: int | None) -> str:
    if value is None:
        return "nie podano"
    return f"{value:,}".replace(",", " ") + " PLN"


def _seat_summary(model: Mapping[str, Any]) -> str:
    values = model.get("recorded_seat_values")
    if not isinstance(values, list) or not values:
        return "nie podano"
    return " / ".join(str(value) for value in values)


def _model_card(model: Mapping[str, Any]) -> str:
    name = html.escape(str(model.get("model_name", "")))
    code = html.escape(str(model.get("model_code", "")))
    price = model.get("catalog_price")
    assert isinstance(price, Mapping)
    minimum = _format_price(price.get("minimum"))
    maximum = _format_price(price.get("maximum"))
    scope_links = "".join(
        f'<a href="#scope-{html.escape(str(slug))}">'
        f'{html.escape(str(slug))}</a>'
        for slug in model.get("scope_slugs", [])
    )
    media = model.get("model_media")
    source_link = ""
    if isinstance(media, Mapping) and media.get("source_page_url"):
        source_link = (
            '<a class="source" href="'
            + html.escape(str(media["source_page_url"]), quote=True)
            + '">oficjalna strona modelu</a>'
        )
    return f'''<article class="model-card" id="model-{code}">
  <div class="model-mark" aria-hidden="true">{name[:2].upper()}</div>
  <div>
    <p class="eyebrow">{html.escape(str(model.get("segment_code", "")))} · {html.escape(str(model.get("body_type_code", "")))}</p>
    <h2>{name}</h2>
    <p>Generacja {html.escape(str(model.get("generation", "")))}</p>
    <dl>
      <div><dt>Konfiguracje</dt><dd>{model.get("configuration_count")}</dd></div>
      <div><dt>Wersje</dt><dd>{model.get("version_count")}</dd></div>
      <div><dt>Ceny katalogowe</dt><dd>{minimum}–{maximum}</dd></div>
      <div><dt>Pokrycie cen</dt><dd>{price.get("recorded_count")}/{model.get("configuration_count")}</dd></div>
      <div><dt>Zapisane wartości miejsc</dt><dd data-state="{html.escape(str(model.get("seat_summary_state", "")))}">{html.escape(_seat_summary(model))}</dd></div>
      <div><dt>Zakresy</dt><dd>{model.get("exclusive_scope_count")} własnych, {model.get("shared_scope_count")} wspólnych</dd></div>
    </dl>
    <nav class="scope-links">{scope_links}</nav>
    {source_link}
  </div>
</article>'''


def _scope_card(scope: Mapping[str, Any]) -> str:
    slug = html.escape(str(scope.get("slug", "")))
    label = html.escape(str(scope.get("label", "")))
    mixed = bool(scope.get("mixed_model"))
    badge = '<span class="badge mixed">wspólny zakres modeli</span>' if mixed else '<span class="badge">zakres jednego modelu</span>'
    paths = scope.get("comparison_paths")
    assert isinstance(paths, Mapping)
    configurations = "".join(
        f"<li>{html.escape(str(label_value))}</li>"
        for label_value in scope.get("configuration_labels", [])
    )
    return f'''<article class="scope-card" id="scope-{slug}">
  <div class="scope-heading"><div><p class="eyebrow">{slug}</p><h3>{label}</h3></div>{badge}</div>
  <dl class="scope-stats">
    <div><dt>Konfiguracje</dt><dd>{scope.get("configuration_count")}</dd></div>
    <div><dt>Istniejące pary</dt><dd>{scope.get("pair_count")}</dd></div>
    <div><dt>Sloty techniczne</dt><dd>{scope.get("technical_slot_count")}</dd></div>
  </dl>
  <details><summary>Pokaż konfiguracje</summary><ul>{configurations}</ul></details>
  <p class="actions">
    <a class="primary" href="{html.escape(str(paths.get("html", "")), quote=True)}">Otwórz istniejące porównanie</a>
    <a href="{html.escape(str(paths.get("json", "")), quote=True)}">JSON</a>
    <a href="{html.escape(str(paths.get("differences_csv", "")), quote=True)}">CSV różnic</a>
  </p>
</article>'''


def render_html(view: Mapping[str, Any]) -> str:
    models = view.get("models")
    scopes = view.get("scopes")
    summary = view.get("summary")
    navigation = view.get("navigation")
    if not isinstance(models, list) or not isinstance(scopes, list):
        raise CrossModelViewError("view models and scopes must be lists")
    if not isinstance(summary, Mapping) or not isinstance(navigation, Mapping):
        raise CrossModelViewError("view summary and navigation are missing")
    model_cards = "\n".join(_model_card(item) for item in models)
    scope_cards = "\n".join(_scope_card(item) for item in scopes)
    return f'''<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Przegląd modeli i bezpiecznych zakresów porównań</title>
<style>
:root{{--bg:#f4f5f7;--surface:#fff;--ink:#202124;--muted:#666b73;--line:#d9dde3;--accent:#1d5f47;--soft:#e7f2ed;--warn:#8a4b08;--warn-bg:#fff2df}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}}a{{color:var(--accent)}}header,main,footer{{max-width:1180px;margin:auto;padding:24px}}header{{padding-top:48px}}h1{{font-size:clamp(2rem,4vw,3.7rem);line-height:1.05;margin:.2em 0}}h2,h3{{margin:.15em 0}}.lead{{max-width:800px;font-size:1.15rem;color:var(--muted)}}.summary{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:28px 0}}.summary div,.notice{{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:16px}}.summary strong{{display:block;font-size:1.7rem}}.notice{{border-left:5px solid var(--accent)}}.models,.scopes{{display:grid;gap:16px}}.models{{grid-template-columns:repeat(auto-fit,minmax(320px,1fr))}}.scopes{{grid-template-columns:repeat(auto-fit,minmax(340px,1fr))}}.model-card,.scope-card{{background:var(--surface);border:1px solid var(--line);border-radius:18px;padding:20px;box-shadow:0 8px 28px rgba(20,30,40,.05)}}.model-card{{display:grid;grid-template-columns:64px 1fr;gap:16px}}.model-mark{{width:64px;height:64px;border-radius:16px;background:var(--soft);display:grid;place-items:center;font-weight:800;font-size:1.25rem;color:var(--accent)}}.eyebrow{{margin:0;color:var(--muted);font-size:.78rem;text-transform:uppercase;letter-spacing:.08em}}dl{{margin:14px 0}}dl div{{display:flex;justify-content:space-between;gap:16px;border-top:1px solid var(--line);padding:7px 0}}dt{{color:var(--muted)}}dd{{margin:0;text-align:right;font-weight:650}}dd[data-state="not_stated"]{{font-weight:500;color:var(--muted)}}.scope-links{{display:flex;flex-wrap:wrap;gap:7px;margin:12px 0}}.scope-links a,.badge{{background:var(--soft);border-radius:999px;padding:4px 9px;font-size:.76rem;text-decoration:none}}.source{{font-size:.84rem}}section{{margin-top:48px}}.scope-heading{{display:flex;justify-content:space-between;gap:14px;align-items:start}}.badge{{white-space:nowrap}}.badge.mixed{{color:var(--warn);background:var(--warn-bg)}}.scope-stats{{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}}.scope-stats div{{display:block;border:0;background:var(--bg);border-radius:10px;padding:8px}}.scope-stats dd{{text-align:left;font-size:1.2rem}}summary{{cursor:pointer;font-weight:650}}details ul{{padding-left:20px}}.actions{{display:flex;flex-wrap:wrap;gap:10px;align-items:center}}.actions a{{padding:8px 11px;border:1px solid var(--line);border-radius:10px;text-decoration:none}}.actions .primary{{background:var(--accent);color:white;border-color:var(--accent)}}footer{{color:var(--muted);font-size:.88rem}}@media(max-width:600px){{header,main,footer{{padding:18px}}.model-card{{grid-template-columns:1fr}}.scope-heading{{display:block}}.badge{{display:inline-block;margin-top:8px}}}}
</style>
</head>
<body>
<header>
<p class="eyebrow">Dacia Knowledge Base · stan {html.escape(str(view.get("as_of", "")))}</p>
<h1>Modele i bezpieczne zakresy porównań</h1>
<p class="lead">Ten widok porządkuje pięć rodzin modeli i prowadzi do istniejących raportów. Nie tworzy par między niezależnymi zakresami, rankingu ani rekomendacji.</p>
<div class="summary">
<div><strong>{summary.get("model_family_count")}</strong>rodzin modeli</div>
<div><strong>{summary.get("reporting_scope_count")}</strong>zakresów</div>
<div><strong>{summary.get("active_configuration_count")}</strong>konfiguracje</div>
<div><strong>{summary.get("within_scope_pair_count")}</strong>istniejących par</div>
</div>
<div class="notice"><strong>Granica porównywalności:</strong> {html.escape(str(navigation.get("pair_generation_rule", "")))} Brak danych pozostaje oznaczony jako „nie podano”.</div>
</header>
<main>
<section><h2>Rodziny modeli</h2><div class="models">{model_cards}</div></section>
<section><h2>Istniejące zakresy raportowe</h2><p class="lead">Wspólny zakres Sandero i Sandero Stepway pozostaje jawnie oznaczony. Pozostałe zakresy dotyczą jednej rodziny modeli.</p><div class="scopes">{scope_cards}</div></section>
</main>
<footer><p>Źródło: zarejestrowane dane Dacia Knowledge Base. Ceny są najnowszymi zapisanymi cenami katalogowymi z pełnym pokryciem konfiguracji, nie oceną opłacalności.</p></footer>
</body>
</html>
'''
