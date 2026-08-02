from __future__ import annotations

import csv
import html
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

from reporting.cross_model_comparison_view import collect_view


SUMMARY_VERSION = 1


class PortfolioModelFamilySummaryError(ValueError):
    """Raised when a source-preserving model-family summary cannot be built."""


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read_csv(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames:
                raise PortfolioModelFamilySummaryError(
                    f"missing CSV header: {path}"
                )
            return list(reader)
    except OSError as exc:
        raise PortfolioModelFamilySummaryError(
            f"cannot read CSV file {path}: {exc}"
        ) from exc


def _string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) for item in value
    ):
        raise PortfolioModelFamilySummaryError(
            f"expected string list for {field}"
        )
    return list(value)


def _source_record(
    source: Mapping[str, str],
    configuration_codes: Sequence[str],
    relationship_values: Sequence[str],
) -> dict[str, Any]:
    return {
        "source_code": source["code"],
        "source_type": source["source_type"],
        "title": source["title"],
        "publisher": source["publisher"],
        "market": source["market"],
        "document_date": source["document_date"],
        "external_reference": source["external_reference"],
        "file_path": source["file_path"],
        "sha256": source["sha256"],
        "status": source["status"],
        "configuration_count": len(configuration_codes),
        "configuration_codes": list(configuration_codes),
        "relationships": list(relationship_values),
    }


def collect_summary(repository: Path) -> dict[str, Any]:
    master = repository / "data" / "master"
    view = collect_view(repository)
    view_summary = view.get("summary")
    raw_models = view.get("models")
    raw_scopes = view.get("scopes")
    if not isinstance(view_summary, Mapping):
        raise PortfolioModelFamilySummaryError("cross-model summary is missing")
    if not isinstance(raw_models, list) or not all(
        isinstance(item, Mapping) for item in raw_models
    ):
        raise PortfolioModelFamilySummaryError("cross-model families are missing")
    if not isinstance(raw_scopes, list) or not all(
        isinstance(item, Mapping) for item in raw_scopes
    ):
        raise PortfolioModelFamilySummaryError("cross-model scopes are missing")
    for flag in (
        "cross_scope_pairs_generated",
        "ranking_generated",
        "recommendations_generated",
        "inferred_values_generated",
    ):
        if view_summary.get(flag) is not False:
            raise PortfolioModelFamilySummaryError(
                f"cross-model view violates summary boundary: {flag}"
            )

    versions = {
        row["code"]: row for row in _read_csv(master / "versions.csv")
    }
    configurations = {
        row["code"]: row
        for row in _read_csv(master / "configurations.csv")
        if row.get("status") == "active"
    }
    source_rows = _read_csv(master / "sources.csv")
    sources = {row["code"]: row for row in source_rows}
    relationship_rows = _read_csv(master / "source_configurations.csv")

    configuration_model: dict[str, str] = {}
    model_configurations: dict[str, list[str]] = defaultdict(list)
    for code, configuration in configurations.items():
        version_code = configuration.get("version_code", "")
        version = versions.get(version_code)
        if version is None:
            raise PortfolioModelFamilySummaryError(
                f"configuration references unknown version: {code} -> {version_code}"
            )
        model_code = version.get("model_code", "")
        if not model_code:
            raise PortfolioModelFamilySummaryError(
                f"version has no model code: {version_code}"
            )
        configuration_model[code] = model_code
        model_configurations[model_code].append(code)

    scope_configuration_codes = [
        code
        for scope in raw_scopes
        for code in _string_list(
            scope.get("configuration_codes"),
            f"scope {scope.get('slug')} configuration_codes",
        )
    ]
    if len(scope_configuration_codes) != len(set(scope_configuration_codes)):
        raise PortfolioModelFamilySummaryError(
            "active configuration belongs to more than one reporting scope"
        )
    if set(scope_configuration_codes) != set(configurations):
        raise PortfolioModelFamilySummaryError(
            "reporting scopes do not cover every active configuration exactly once"
        )

    relations_by_model: dict[
        str, dict[str, list[dict[str, str]]]
    ] = defaultdict(lambda: defaultdict(list))
    relation_count = 0
    covered_configurations: set[str] = set()
    used_sources: set[str] = set()
    for relation in relationship_rows:
        configuration_code = relation.get("configuration_code", "")
        if configuration_code not in configurations:
            continue
        source_code = relation.get("source_code", "")
        if source_code not in sources:
            raise PortfolioModelFamilySummaryError(
                f"source relationship references unknown source: {source_code}"
            )
        model_code = configuration_model[configuration_code]
        relations_by_model[model_code][source_code].append(relation)
        relation_count += 1
        covered_configurations.add(configuration_code)
        used_sources.add(source_code)
    if covered_configurations != set(configurations):
        missing = sorted(set(configurations) - covered_configurations)
        raise PortfolioModelFamilySummaryError(
            f"active configurations without source provenance: {missing}"
        )

    scope_index = {
        str(scope.get("slug", "")): scope for scope in raw_scopes
    }
    family_records: list[dict[str, Any]] = []
    for model in raw_models:
        model_code = str(model.get("model_code", ""))
        configuration_codes = sorted(model_configurations[model_code])
        if int(model.get("configuration_count", -1)) != len(configuration_codes):
            raise PortfolioModelFamilySummaryError(
                f"model configuration count differs: {model_code}"
            )
        source_records: list[dict[str, Any]] = []
        model_relation_count = 0
        for source_code, relations in relations_by_model[model_code].items():
            relation_configuration_codes = sorted(
                {row["configuration_code"] for row in relations}
            )
            relationship_values = sorted(
                {row["relationship"] for row in relations if row["relationship"]}
            )
            source_records.append(
                _source_record(
                    sources[source_code],
                    relation_configuration_codes,
                    relationship_values,
                )
            )
            model_relation_count += len(relations)
        source_records.sort(
            key=lambda item: (
                str(item["document_date"]),
                str(item["source_code"]),
            )
        )
        source_type_counts = dict(
            sorted(Counter(item["source_type"] for item in source_records).items())
        )
        source_dates = [
            str(item["document_date"])
            for item in source_records
            if str(item["document_date"])
        ]
        scope_slugs = _string_list(
            model.get("scope_slugs"), f"model {model_code} scope_slugs"
        )
        scopes = [scope_index[slug] for slug in scope_slugs]
        shared_scope_slugs = sorted(
            str(scope["slug"]) for scope in scopes if scope.get("mixed_model") is True
        )
        exclusive_scope_slugs = sorted(
            str(scope["slug"]) for scope in scopes if scope.get("mixed_model") is False
        )
        price = model.get("catalog_price")
        if not isinstance(price, Mapping):
            raise PortfolioModelFamilySummaryError(
                f"model price summary is missing: {model_code}"
            )
        family_records.append(
            {
                "model_code": model_code,
                "model_name": model.get("model_name"),
                "generation": model.get("generation"),
                "body_type_code": model.get("body_type_code"),
                "segment_code": model.get("segment_code"),
                "configuration_count": len(configuration_codes),
                "configuration_codes": configuration_codes,
                "version_count": model.get("version_count"),
                "catalog_price": dict(price),
                "recorded_seat_values": list(
                    model.get("recorded_seat_values", [])
                ),
                "seat_summary_state": model.get("seat_summary_state"),
                "transmission_values": list(model.get("transmission_values", [])),
                "powertrain_labels": list(model.get("powertrain_labels", [])),
                "reporting_scope_count": len(scope_slugs),
                "exclusive_scope_count": len(exclusive_scope_slugs),
                "shared_scope_count": len(shared_scope_slugs),
                "scope_slugs": scope_slugs,
                "exclusive_scope_slugs": exclusive_scope_slugs,
                "shared_scope_slugs": shared_scope_slugs,
                "provenance": {
                    "source_count": len(source_records),
                    "relationship_count": model_relation_count,
                    "configuration_coverage_count": len(configuration_codes),
                    "missing_configuration_count": 0,
                    "earliest_document_date": min(source_dates),
                    "latest_document_date": max(source_dates),
                    "source_type_counts": source_type_counts,
                    "sources": source_records,
                },
            }
        )

    if len(family_records) != int(view_summary["model_family_count"]):
        raise PortfolioModelFamilySummaryError("model-family count differs")
    return {
        "version": SUMMARY_VERSION,
        "kind": "portfolio_model_family_summary",
        "as_of": view.get("as_of"),
        "summary": {
            "model_family_count": len(family_records),
            "reporting_scope_count": int(view_summary["reporting_scope_count"]),
            "single_model_scope_count": int(
                view_summary["single_model_scope_count"]
            ),
            "mixed_model_scope_count": int(
                view_summary["mixed_model_scope_count"]
            ),
            "active_configuration_count": len(configurations),
            "within_scope_pair_count": int(
                view_summary["within_scope_pair_count"]
            ),
            "provenance_source_count": len(used_sources),
            "source_configuration_relationship_count": relation_count,
            "configurations_with_provenance_count": len(covered_configurations),
            "configurations_without_provenance_count": 0,
            "cross_scope_pairs_generated": False,
            "ranking_generated": False,
            "recommendations_generated": False,
            "inferred_values_generated": False,
        },
        "methodology": {
            "family_boundary": (
                "Each family is the canonical model_code assigned through the "
                "active configuration's version."
            ),
            "scope_boundary": (
                "Reporting scopes are reused exactly from the existing comparison "
                "registry. Shared scopes are disclosed but never expanded into new pairs."
            ),
            "provenance_boundary": (
                "Only explicit source_configurations relationships are counted. "
                "Source metadata is copied from the canonical source registry."
            ),
            "unknown_handling": (
                "Unstated values remain not_stated and are never replaced with zero, "
                "false, unavailable or an inferred value."
            ),
        },
        "families": family_records,
    }


def render_json(summary: Mapping[str, Any]) -> str:
    return json.dumps(summary, ensure_ascii=False, indent=2) + "\n"


def _format_price(value: Any) -> str:
    if value is None:
        return "nie podano"
    return f"{int(value):,}".replace(",", " ") + " PLN"


def _join(values: Any, empty: str = "nie podano") -> str:
    if not isinstance(values, list) or not values:
        return empty
    return " / ".join(str(item) for item in values)


def render_markdown(summary: Mapping[str, Any]) -> str:
    totals = summary["summary"]
    families = summary["families"]
    assert isinstance(totals, Mapping)
    assert isinstance(families, list)
    lines = [
        "# Portfolio Model Family Summary",
        "",
        f"Snapshot: `{summary.get('as_of')}`",
        "",
        "This report groups the current active configurations by canonical model "
        "family. It reuses existing reporting scopes and explicit source links; it "
        "does not create cross-scope pairs, rankings, recommendations or inferred values.",
        "",
        "## Portfolio",
        "",
        f"- model families: {totals['model_family_count']};",
        f"- active configurations: {totals['active_configuration_count']};",
        f"- reporting scopes: {totals['reporting_scope_count']};",
        f"- within-scope pairs: {totals['within_scope_pair_count']};",
        f"- provenance sources: {totals['provenance_source_count']};",
        f"- source-to-configuration relationships: {totals['source_configuration_relationship_count']};",
        "- configurations without provenance: 0.",
        "",
        "## Family overview",
        "",
        "| Family | Configurations | Versions | Scopes | Price range | Sources | Source dates |",
        "|---|---:|---:|---:|---|---:|---|",
    ]
    for family in families:
        price = family["catalog_price"]
        provenance = family["provenance"]
        lines.append(
            "| {name} | {configs} | {versions} | {scopes} | {minimum}–{maximum} | "
            "{sources} | {earliest}–{latest} |".format(
                name=family["model_name"],
                configs=family["configuration_count"],
                versions=family["version_count"],
                scopes=family["reporting_scope_count"],
                minimum=_format_price(price["minimum"]),
                maximum=_format_price(price["maximum"]),
                sources=provenance["source_count"],
                earliest=provenance["earliest_document_date"],
                latest=provenance["latest_document_date"],
            )
        )
    for family in families:
        provenance = family["provenance"]
        lines.extend(
            [
                "",
                f"## {family['model_name']}",
                "",
                f"- model code: `{family['model_code']}`;",
                f"- configurations: {family['configuration_count']};",
                f"- versions: {family['version_count']};",
                f"- powertrains: {_join(family['powertrain_labels'])};",
                f"- transmissions: {_join(family['transmission_values'])};",
                f"- recorded seat values: {_join(family['recorded_seat_values'])};",
                f"- reporting scopes: {family['reporting_scope_count']} "
                f"({family['exclusive_scope_count']} exclusive, "
                f"{family['shared_scope_count']} shared);",
                f"- explicit provenance: {provenance['source_count']} sources and "
                f"{provenance['relationship_count']} source-configuration relationships.",
                "",
                "### Sources",
                "",
            ]
        )
        for source in provenance["sources"]:
            lines.append(
                "- `{code}` — {date}, `{kind}`, {covered} configurations, "
                "SHA-256 `{digest}` — {title}.".format(
                    code=source["source_code"],
                    date=source["document_date"],
                    kind=source["source_type"],
                    covered=source["configuration_count"],
                    digest=source["sha256"],
                    title=source["title"],
                )
            )
    lines.extend(
        [
            "",
            "## Safety boundary",
            "",
            "- existing independent scopes are preserved;",
            "- no cross-scope pair is generated;",
            "- no ranking or recommendation is generated;",
            "- no missing value is inferred or reclassified;",
            "- every provenance entry is an explicit canonical relationship.",
        ]
    )
    return "\n".join(lines) + "\n"


def _family_card(family: Mapping[str, Any]) -> str:
    price = family["catalog_price"]
    provenance = family["provenance"]
    assert isinstance(price, Mapping)
    assert isinstance(provenance, Mapping)
    source_items = []
    for source in provenance["sources"]:
        source_items.append(
            "<li><div><code>{code}</code><strong>{title}</strong></div>"
            "<p>{date} · {kind} · {count} konfiguracji</p>"
            "<p class=\"hash\">SHA-256 {digest}</p></li>".format(
                code=html.escape(str(source["source_code"])),
                title=html.escape(str(source["title"])),
                date=html.escape(str(source["document_date"])),
                kind=html.escape(str(source["source_type"])),
                count=source["configuration_count"],
                digest=html.escape(str(source["sha256"])),
            )
        )
    return """<article class="family" id="family-{code}">
<header><p class="eyebrow">{segment} · {body}</p><h2>{name}</h2><code>{code}</code></header>
<div class="metrics">
<div><span>Konfiguracje</span><strong>{configs}</strong></div>
<div><span>Wersje</span><strong>{versions}</strong></div>
<div><span>Zakresy</span><strong>{scopes}</strong></div>
<div><span>Źródła</span><strong>{sources}</strong></div>
</div>
<dl>
<div><dt>Ceny katalogowe</dt><dd>{minimum}–{maximum}</dd></div>
<div><dt>Napędy</dt><dd>{powertrains}</dd></div>
<div><dt>Skrzynie</dt><dd>{transmissions}</dd></div>
<div><dt>Zapisane liczby miejsc</dt><dd data-state="{seat_state}">{seats}</dd></div>
<div><dt>Zakresy własne / wspólne</dt><dd>{exclusive} / {shared}</dd></div>
<div><dt>Daty źródeł</dt><dd>{earliest}–{latest}</dd></div>
</dl>
<details><summary>Dokładna proweniencja ({sources} źródeł, {relations} relacji)</summary><ul class="sources">{source_items}</ul></details>
</article>""".format(
        code=html.escape(str(family["model_code"])),
        segment=html.escape(str(family["segment_code"])),
        body=html.escape(str(family["body_type_code"])),
        name=html.escape(str(family["model_name"])),
        configs=family["configuration_count"],
        versions=family["version_count"],
        scopes=family["reporting_scope_count"],
        sources=provenance["source_count"],
        minimum=html.escape(_format_price(price["minimum"])),
        maximum=html.escape(_format_price(price["maximum"])),
        powertrains=html.escape(_join(family["powertrain_labels"])),
        transmissions=html.escape(_join(family["transmission_values"])),
        seat_state=html.escape(str(family["seat_summary_state"])),
        seats=html.escape(_join(family["recorded_seat_values"])),
        exclusive=family["exclusive_scope_count"],
        shared=family["shared_scope_count"],
        earliest=html.escape(str(provenance["earliest_document_date"])),
        latest=html.escape(str(provenance["latest_document_date"])),
        relations=provenance["relationship_count"],
        source_items="".join(source_items),
    )


def render_html(summary: Mapping[str, Any]) -> str:
    totals = summary["summary"]
    families = summary["families"]
    assert isinstance(totals, Mapping)
    assert isinstance(families, list)
    cards = "".join(_family_card(family) for family in families)
    return f"""<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dacia Knowledge Base — rodziny modeli</title>
<style>
:root{{--bg:#11151b;--panel:#1a2029;--soft:#252d38;--text:#f2f5f8;--muted:#aeb8c5;--line:#394452;--accent:#d7ff38}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.55 system-ui,sans-serif}}main{{max-width:1180px;margin:auto;padding:40px 22px 72px}}h1{{font-size:clamp(2rem,5vw,4.2rem);line-height:1;margin:.2em 0}}h2{{margin:.15em 0;font-size:1.65rem}}code{{font-family:ui-monospace,monospace;overflow-wrap:anywhere}}.lead{{max-width:78ch;color:var(--muted)}}.portfolio{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:28px 0 36px}}.portfolio div,.metrics div{{background:var(--soft);border:1px solid var(--line);border-radius:12px;padding:14px}}.portfolio span,.metrics span,dt,.eyebrow{{display:block;color:var(--muted);font-size:.78rem;text-transform:uppercase;letter-spacing:.08em}}.portfolio strong,.metrics strong{{font-size:1.55rem}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px}}.family{{background:var(--panel);border:1px solid var(--line);border-radius:18px;padding:20px}}.family header{{border-bottom:1px solid var(--line);padding-bottom:14px}}.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:16px 0}}dl{{margin:0}}dl div{{display:grid;grid-template-columns:1fr 1.6fr;gap:12px;padding:8px 0;border-bottom:1px solid var(--line)}}dd{{margin:0;text-align:right}}details{{margin-top:18px}}summary{{cursor:pointer;color:var(--accent);font-weight:700}}.sources{{list-style:none;padding:0;margin:14px 0 0}}.sources li{{border-top:1px solid var(--line);padding:12px 0}}.sources li div{{display:flex;gap:10px;flex-wrap:wrap;justify-content:space-between}}.sources p{{margin:.25em 0;color:var(--muted)}}.hash{{font-size:.72rem;overflow-wrap:anywhere}}footer{{margin-top:30px;padding-top:20px;border-top:1px solid var(--line);color:var(--muted)}}@media(max-width:580px){{.metrics{{grid-template-columns:repeat(2,1fr)}}dl div{{grid-template-columns:1fr}}dd{{text-align:left}}}}
</style>
</head>
<body><main>
<p class="eyebrow">Dacia Knowledge Base · snapshot {html.escape(str(summary.get('as_of')))}</p>
<h1>Rodziny modeli</h1>
<p class="lead">Samodzielne, deterministyczne podsumowanie aktualnego portfela. Zachowuje istniejące zakresy raportowe i dokładne relacje źródłowe; nie tworzy par między zakresami, rankingów, rekomendacji ani wartości domyślnych.</p>
<section class="portfolio" aria-label="Podsumowanie portfela">
<div><span>Rodziny</span><strong>{totals['model_family_count']}</strong></div>
<div><span>Konfiguracje</span><strong>{totals['active_configuration_count']}</strong></div>
<div><span>Zakresy</span><strong>{totals['reporting_scope_count']}</strong></div>
<div><span>Źródła</span><strong>{totals['provenance_source_count']}</strong></div>
<div><span>Relacje źródłowe</span><strong>{totals['source_configuration_relationship_count']}</strong></div>
<div><span>Brak proweniencji</span><strong>0</strong></div>
</section>
<section class="grid" aria-label="Rodziny modeli">{cards}</section>
<footer>Zakres bezpieczeństwa: wyłącznie aktywne konfiguracje i jawne relacje kanoniczne. Brak nowych par porównawczych, rankingów, rekomendacji i inferencji.</footer>
</main></body></html>
"""
