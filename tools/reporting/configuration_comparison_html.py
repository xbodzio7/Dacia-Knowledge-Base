from __future__ import annotations

from html import escape
from typing import Any, Mapping

HTML_REPORT_VERSION = 1
DOMAINS = (("prices", "Ceny"), ("technical", "Dane techniczne"), ("equipment", "Wyposażenie"))
LABELS = {"equal": "Równe", "different": "Różne", "not_comparable": "Nieporównywalne"}


def _h(value: Any) -> str:
    return escape(str(value), quote=True)


def _state_value(state: Mapping[str, Any], domain: str) -> str:
    kind = str(state.get("state", "")) or "missing"
    if kind != "recorded":
        return kind
    if domain == "prices":
        return str(state.get("amount", ""))
    if domain == "equipment":
        return str(state.get("availability_status", ""))
    if "minimum_value" in state:
        left = "[" if state.get("lower_inclusive") else "("
        right = "]" if state.get("upper_inclusive") else ")"
        value = f"{left}{state.get('minimum_value', '')}, {state.get('maximum_value', '')}{right}"
    else:
        value = str(state.get("value", ""))
    return f"{value} {state.get('unit', '')}".strip()


def _state_cell(state: Mapping[str, Any], domain: str) -> str:
    kind = str(state.get("state", "")) or "missing"
    details = [kind]
    for key in ("source_code", "price_date" if domain == "prices" else "observation_date", "reason_code"):
        value = str(state.get(key, ""))
        if value:
            details.append(value)
    pages = state.get("reviewed_pages")
    if isinstance(pages, list) and pages:
        details.append("strony " + ", ".join(str(page) for page in pages))
    return (
        f'<div class="state state-{_h(kind)}"><strong>{_h(_state_value(state, domain))}</strong>'
        f'<small>{_h(" · ".join(details))}</small></div>'
    )


def _item(item: Mapping[str, Any], domain: str) -> tuple[str, str]:
    if domain == "prices":
        label = f"{item.get('market', '')} / {item.get('price_type', '')} / {item.get('currency_code', '')}"
        delta = str(item.get("amount_delta_right_minus_left", ""))
        return label, f"różnica: {delta}" if delta else ""
    label = str(item.get("attribute_code", ""))
    if item.get("attribute_name"):
        label += f" — {item['attribute_name']}"
    context = [str(item.get("category", ""))]
    if domain == "technical" and item.get("fuel_type_code"):
        context.append(f"paliwo: {item['fuel_type_code']}")
    if item.get("range_relation"):
        context.append(f"relacja zakresu: {item['range_relation']}")
    return label, " · ".join(value for value in context if value)


def _configuration(configuration: Mapping[str, Any]) -> str:
    code = str(configuration.get("configuration_code", ""))
    details = " · ".join(
        str(configuration.get(key, ""))
        for key in ("version_code", "powertrain_label", "transmission_type")
        if configuration.get(key)
    )
    return f"{code} ({details})" if details else code


def _metric(label: str, value: Any, note: str = "") -> str:
    suffix = f"<small>{_h(note)}</small>" if note else ""
    return f'<div class="metric"><span>{_h(label)}</span><strong>{_h(value)}</strong>{suffix}</div>'


def render_html(report: Mapping[str, Any]) -> str:
    scope, summary, evidence = report["scope"], report["summary"], report["evidence_summary"]
    parts = [
        "<!doctype html>", '<html lang="pl">', "<head>", '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<meta name="generator" content="Dacia Knowledge Base">',
        "<title>Porównanie konfiguracji Dacia</title>", "<style>", _CSS, "</style>",
        "</head>", "<body>", "<header>", '<p class="eyebrow">Dacia Knowledge Base</p>',
        "<h1>Porównanie konfiguracji</h1>",
        f'<p class="lede">Źródłowy snapshot na dzień <strong>{_h(report["as_of"])}</strong>. Raport działa offline.</p>',
        "</header>", "<main>", '<section aria-labelledby="summary-heading">',
        '<h2 id="summary-heading">Podsumowanie</h2>', '<div class="metrics">',
        _metric("Konfiguracje", scope["active_configurations"]),
        _metric("Pary", scope["pair_count"], f"z {scope['unfiltered_pair_count']} dostępnych"),
        _metric("Różnice", summary["total_differences"]), _metric("Decyzje dowodowe", evidence["total"]),
        "</div>", '<div class="table-wrap"><table><caption>Podsumowanie domen</caption>',
        "<thead><tr><th>Domena</th><th>Porównania</th><th>Równe</th><th>Różne</th><th>Nieporównywalne</th></tr></thead><tbody>",
    ]
    for domain, label in DOMAINS:
        item = summary[domain]
        parts.append(
            f"<tr><th>{_h(label)}</th><td>{item['comparisons']}</td><td>{item['equal']}</td>"
            f"<td>{item['different']}</td><td>{item['not_comparable']}</td></tr>"
        )
    parts += [
        "</tbody></table></div>",
        f'<p class="evidence">Stany dowodowe: not_stated={evidence["not_stated"]}, '
        f'out_of_scope={evidence["out_of_scope"]}, ambiguous={evidence["ambiguous"]}, found={evidence["found"]}. '
        "Tylko dwa zapisane stany mogą być równe lub różne.</p>", "</section>",
        '<section class="controls" aria-labelledby="controls-heading"><h2 id="controls-heading">Filtry</h2>',
        '<label>Wyszukaj<input id="search" type="search" placeholder="kod, nazwa, kategoria, wartość lub źródło"></label>',
        '<label>Domena<select id="domain"><option value="all">Wszystkie</option><option value="prices">Ceny</option><option value="technical">Dane techniczne</option><option value="equipment">Wyposażenie</option></select></label>',
        '<label>Wynik<select id="comparison"><option value="all">Wszystkie</option><option value="different">Różne</option><option value="equal">Równe</option><option value="not_comparable">Nieporównywalne</option></select></label>',
        '<label class="check"><input id="differences-only" type="checkbox" checked> Tylko różnice</label>',
        '<button id="reset" type="button">Wyczyść filtry</button><output id="result-count" aria-live="polite"></output></section>',
        '<section aria-labelledby="pairs-heading"><h2 id="pairs-heading">Pary konfiguracji</h2><div class="pair-index">',
    ]
    for index, pair in enumerate(report["pairs"], 1):
        parts.append(f'<a href="#pair-{index}">{_h(pair["pair_code"])}</a>')
    parts.append("</div>")
    for index, pair in enumerate(report["pairs"], 1):
        left, right = pair["left_configuration"], pair["right_configuration"]
        pair_search = " ".join((str(pair["pair_code"]), str(pair["pair_type"]), _configuration(left), _configuration(right))).lower()
        parts += [
            f'<article class="pair" id="pair-{index}" data-search="{_h(pair_search)}">',
            '<div class="pair-heading"><div>', f'<p class="eyebrow">{_h(pair["pair_type"])}</p>',
            f'<h3>{_h(pair["pair_code"])}</h3></div><a href="#pairs-heading">Powrót do listy</a></div>',
            '<div class="pair-configurations">', f'<div><span>Lewa</span><strong>{_h(_configuration(left))}</strong></div>',
            f'<div><span>Prawa</span><strong>{_h(_configuration(right))}</strong></div></div>',
        ]
        for domain, label in DOMAINS:
            left_label, right_label = _configuration(left), _configuration(right)
            parts += [
                f'<section class="domain" data-domain-section="{domain}"><h4>{_h(label)}</h4><div class="table-wrap"><table>',
                f'<thead><tr><th>Pozycja</th><th>Kontekst</th><th>{_h(left_label)}</th><th>{_h(right_label)}</th><th>Wynik</th></tr></thead><tbody>',
            ]
            for item in pair[domain]:
                result = str(item.get("comparison", ""))
                label_text, context = _item(item, domain)
                search_text = " ".join((pair_search, domain, result, label_text, context, _state_value(item["left"], domain), _state_value(item["right"], domain), str(item["left"].get("source_code", "")), str(item["right"].get("source_code", "")))).lower()
                parts.append(
                    f'<tr data-domain="{domain}" data-comparison="{_h(result)}" data-search="{_h(search_text)}">'
                    f'<th>{_h(label_text)}</th><td>{_h(context)}</td><td>{_state_cell(item["left"], domain)}</td>'
                    f'<td>{_state_cell(item["right"], domain)}</td><td><span class="badge badge-{_h(result)}">{_h(LABELS.get(result, result))}</span></td></tr>'
                )
            parts += ["</tbody></table></div></section>"]
        parts.append("</article>")
    parts += [
        "</section></main><footer>", f"<p>Format raportu HTML v{HTML_REPORT_VERSION}. Dane pochodzą z wersjonowanych źródeł DKB.</p>",
        "</footer><script>", _JS, "</script></body></html>", "",
    ]
    return "\n".join(parts)


_CSS = r""":root{color-scheme:light;--ink:#17211b;--muted:#5e6a63;--paper:#f6f7f4;--panel:#fff;--line:#d9ded9;--accent:#1f6f43;--accent-soft:#dff1e5;--warn:#8a4b08;--warn-soft:#fff0d6;--danger:#9d2b2b;--danger-soft:#fde5e5}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:var(--ink);background:var(--paper);line-height:1.45}header,main,footer{width:min(1500px,calc(100% - 32px));margin-inline:auto}header{padding:48px 0 28px}h1{margin:0;font-size:clamp(2rem,4vw,4rem);letter-spacing:-.045em}h2{margin-top:42px}h3,h4{margin:0}.lede{max-width:760px;color:var(--muted);font-size:1.08rem}.eyebrow{margin:0 0 6px;color:var(--accent);font-size:.78rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase}.metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}.metric{display:grid;gap:5px;padding:18px;background:var(--panel);border:1px solid var(--line);border-radius:14px}.metric span,.metric small{color:var(--muted)}.metric strong{font-size:1.8rem}.table-wrap{overflow-x:auto}table{width:100%;border-collapse:collapse;background:var(--panel)}caption{padding:18px 0 10px;text-align:left;font-weight:700}th,td{padding:11px 12px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}thead th{position:sticky;top:0;z-index:1;background:#edf1ed;font-size:.82rem}tbody tr:hover{background:#fafcf9}.evidence{padding:14px 16px;background:var(--warn-soft);border-left:4px solid var(--warn)}.controls{position:sticky;top:0;z-index:5;display:grid;grid-template-columns:minmax(240px,2fr) repeat(2,minmax(150px,1fr)) auto auto;gap:10px;align-items:end;padding:14px;margin-top:32px;background:rgba(246,247,244,.96);border:1px solid var(--line);border-radius:14px;backdrop-filter:blur(8px)}.controls h2{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}.controls label{display:grid;gap:5px;color:var(--muted);font-size:.82rem;font-weight:700}.controls input[type=search],.controls select,.controls button{min-height:42px;padding:8px 10px;border:1px solid #b9c1bb;border-radius:8px;background:var(--panel);color:var(--ink)}.controls button{cursor:pointer;font-weight:700}.controls .check{display:flex;align-items:center;min-height:42px;color:var(--ink)}.controls output{grid-column:1/-1;color:var(--muted)}.pair-index{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:20px}.pair-index a{padding:7px 10px;border:1px solid var(--line);border-radius:999px;background:var(--panel);color:var(--accent);text-decoration:none;font-size:.78rem}.pair{margin:20px 0 40px;padding:20px;background:var(--panel);border:1px solid var(--line);border-radius:16px;box-shadow:0 10px 28px rgba(30,45,35,.06)}.pair[hidden],tr[hidden],.domain[hidden]{display:none!important}.pair-heading{display:flex;justify-content:space-between;gap:20px;align-items:start}.pair-heading a{color:var(--accent)}.pair-configurations{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:18px 0}.pair-configurations div{display:grid;gap:4px;padding:12px;background:var(--paper);border-radius:10px}.pair-configurations span{color:var(--muted);font-size:.78rem;text-transform:uppercase}.domain{margin-top:22px}.domain h4{margin-bottom:8px}.state{display:grid;gap:3px;min-width:150px}.state small{color:var(--muted);font-size:.72rem}.badge{display:inline-flex;padding:4px 8px;border-radius:999px;font-size:.75rem;font-weight:800;white-space:nowrap}.badge-equal{background:var(--accent-soft);color:var(--accent)}.badge-different{background:var(--danger-soft);color:var(--danger)}.badge-not_comparable{background:var(--warn-soft);color:var(--warn)}footer{padding:30px 0 50px;color:var(--muted)}@media(max-width:900px){.metrics{grid-template-columns:repeat(2,minmax(0,1fr))}.controls{position:static;grid-template-columns:1fr 1fr}.controls label:first-of-type{grid-column:1/-1}.pair-configurations{grid-template-columns:1fr}}@media(max-width:560px){header,main,footer{width:min(100% - 20px,1500px)}.metrics,.controls{grid-template-columns:1fr}.controls label:first-of-type{grid-column:auto}.pair{padding:12px}}@media print{body{background:#fff}.controls,.pair-index,.pair-heading a{display:none!important}.pair{break-inside:avoid;box-shadow:none}thead th{position:static}}"""

_JS = r"""(()=>{const search=document.querySelector('#search'),domain=document.querySelector('#domain'),comparison=document.querySelector('#comparison'),only=document.querySelector('#differences-only'),reset=document.querySelector('#reset'),count=document.querySelector('#result-count'),rows=[...document.querySelectorAll('tbody tr[data-domain]')],pairs=[...document.querySelectorAll('article.pair')];function apply(){const query=search.value.trim().toLocaleLowerCase('pl');let visible=0;for(const row of rows){const show=(domain.value==='all'||row.dataset.domain===domain.value)&&(comparison.value==='all'||row.dataset.comparison===comparison.value)&&(!only.checked||row.dataset.comparison==='different')&&(!query||row.dataset.search.includes(query));row.hidden=!show;if(show)visible++}for(const section of document.querySelectorAll('[data-domain-section]'))section.hidden=!section.querySelector('tbody tr:not([hidden])');for(const pair of pairs)pair.hidden=!pair.querySelector('tbody tr:not([hidden])');count.value=`Widoczne wiersze: ${visible}; pary: ${pairs.filter(pair=>!pair.hidden).length}.`}for(const control of[search,domain,comparison,only]){control.addEventListener('input',apply);control.addEventListener('change',apply)}reset.addEventListener('click',()=>{search.value='';domain.value='all';comparison.value='all';only.checked=true;apply();search.focus()});apply()})();"""
