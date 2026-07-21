from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from reporting import configuration_shortlist as core
from reporting.configuration_shortlist_html import render_html as render_base_html


_SELECTION_PANEL = r'''  <section id="selection-panel" class="selection-panel" aria-labelledby="selection-heading">
    <div>
      <p class="eyebrow">Jawny wybór</p>
      <h2 id="selection-heading">Wybrane konfiguracje: <span id="selected-count">0</span></h2>
      <p>Zmiana filtrów nie usuwa zaznaczeń. Eksport JSON jest bezpośrednio zgodny z wejściem pakietu porównań.</p>
    </div>
    <div class="selection-actions">
      <button id="select-visible" type="button">Wybierz widoczne</button>
      <button id="clear-selection" type="button" disabled>Wyczyść wybór</button>
      <button id="download-selection-json" type="button" disabled>Pobierz JSON</button>
      <button id="download-selection-codes" type="button" disabled>Pobierz kody TXT</button>
    </div>
    <ul id="selected-list" class="selected-list"></ul>
  </section>
'''

_SELECTION_CSS = r'''
.selection-panel{position:sticky;top:10px;z-index:6;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:14px;padding:18px;margin-top:18px;background:rgba(255,255,255,.97);border:1px solid var(--line);border-radius:16px;box-shadow:0 12px 34px rgba(27,43,33,.1);backdrop-filter:blur(8px)}
.selection-panel h2{margin:0}.selection-panel p{margin:5px 0;color:var(--muted)}.selection-actions{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:8px;align-content:start}.selection-actions button,.remove-selection{min-height:38px;padding:7px 11px;border:1px solid #aeb8b0;border-radius:8px;background:#fff;color:var(--ink);cursor:pointer;font-weight:750}.selection-actions button:disabled{cursor:not-allowed;opacity:.45}.selected-list{grid-column:1/-1;display:flex;flex-wrap:wrap;gap:7px;margin:0;padding:0;list-style:none}.selected-list li{display:flex;align-items:center;gap:8px;padding:6px 8px 6px 10px;background:var(--soft);border-radius:999px;color:var(--accent);font-size:.76rem;font-weight:700}.remove-selection{min-height:28px;padding:3px 7px;border-color:transparent;background:rgba(255,255,255,.72);font-size:.7rem}.selection-toggle{display:flex;align-items:center;gap:6px;margin:-4px 0 2px;color:var(--accent);font-size:.78rem;font-weight:800}.selection-toggle input{width:18px;height:18px;accent-color:var(--accent)}
.selected-filter-summary{display:grid;gap:7px;min-height:76px;padding:9px;border:1px solid var(--line);border-radius:9px;background:var(--paper);color:var(--ink)}.selected-filter-summary-head{display:flex;align-items:center;justify-content:space-between;gap:8px;font-size:.75rem}.selected-filter-summary-head button{width:auto;min-height:30px;padding:4px 8px;background:#fff;font-size:.72rem}.selected-filter-summary-head button:disabled{cursor:not-allowed;opacity:.45}.selected-filter-list{display:flex;flex-wrap:wrap;gap:5px;align-content:start}.selected-filter-empty{color:var(--muted);font-size:.74rem;font-weight:500}.selected-filter-chip{display:inline-flex;align-items:center;gap:6px;width:auto!important;min-height:30px!important;padding:4px 7px 4px 9px!important;border-color:#b9d4c1!important;border-radius:999px!important;background:var(--soft)!important;color:var(--accent)!important;font-size:.7rem;font-weight:750!important;text-align:left}.selected-filter-chip span{font-size:1rem;line-height:1}.result-card.is-selected{border-color:var(--accent);box-shadow:0 0 0 3px rgba(31,111,67,.15),0 12px 32px rgba(27,43,33,.1)}.result-card.is-selected .selection-toggle{padding:5px 8px;margin:-6px -6px 2px;border-radius:8px;background:var(--soft)}.result-price{display:grid;gap:5px;font-size:inherit;font-weight:inherit;color:var(--ink)}.configuration-price-main{display:grid;gap:1px;color:var(--accent)}.configuration-price-main span{font-size:.72rem;font-weight:750;text-transform:uppercase;letter-spacing:.05em}.configuration-price-main strong{font-size:1.55rem;line-height:1.15}.configuration-price-standard{color:var(--muted);font-size:.78rem}.configuration-price-components{display:grid;gap:4px;margin:3px 0 0;padding:8px 0 0;border-top:1px solid var(--line);list-style:none}.configuration-price-components li{display:flex;justify-content:space-between;gap:10px;font-size:.74rem}.configuration-price-components strong{white-space:nowrap;color:var(--accent)}.configuration-price-components .price-component-unknown strong{color:var(--warn)}.configuration-price-warning{margin:0;color:var(--warn);font-size:.7rem;font-weight:700}.configuration-price-included{margin:0;color:var(--muted);font-size:.7rem}.equipment-state{overflow-wrap:anywhere}
@media(max-width:760px){.selection-panel{position:static;grid-template-columns:1fr}.selection-actions{justify-content:flex-start}.selected-list{grid-column:auto}}
@media print{.selection-panel,.selection-toggle,.selected-filter-summary{display:none!important}}
'''


def _read_script(name: str, label: str) -> str:
    script_path = Path(__file__).with_name(name)
    try:
        return script_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise core.ShortlistError(
            f"cannot read {label} script: {exc}"
        ) from exc


def _read_labels() -> dict[str, str]:
    labels_path = Path(__file__).with_name(
        "configuration_shortlist_labels_pl.json"
    )
    try:
        labels = json.loads(labels_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise core.ShortlistError(
            f"cannot read Polish equipment labels: {exc}"
        ) from exc
    if not isinstance(labels, dict) or not all(
        isinstance(code, str) and isinstance(label, str)
        for code, label in labels.items()
    ):
        raise core.ShortlistError("invalid Polish equipment label contract")
    return labels


def render_html(catalog: Mapping[str, Any]) -> str:
    enhanced_catalog = dict(catalog)
    enhanced_catalog["interface_labels"] = {
        "equipment_pl": _read_labels(),
    }
    rendered = render_base_html(enhanced_catalog)
    selection_script = _read_script(
        "configuration_shortlist_selection.js",
        "browser selection",
    )
    pricing_script = _read_script(
        "configuration_shortlist_v11_pricing.js",
        "version 1.1 pricing",
    )
    version_script = _read_script(
        "configuration_shortlist_v11.js",
        "version 1.1 enhancement",
    )

    style_marker = "</style>"
    results_marker = '  <section aria-labelledby="results-heading">'
    body_marker = "</body>"
    for marker, label in (
        (style_marker, "style"),
        (results_marker, "results"),
        (body_marker, "body"),
    ):
        if marker not in rendered:
            raise core.ShortlistError(
                f"cannot inject selection controls: missing {label} marker"
            )
    rendered = rendered.replace(
        style_marker,
        _SELECTION_CSS + "\n" + style_marker,
        1,
    )
    rendered = rendered.replace(
        results_marker,
        _SELECTION_PANEL + results_marker,
        1,
    )
    rendered = rendered.replace(
        "Format interaktywnej shortlisty HTML v1.",
        "Format interaktywnej shortlisty HTML v1.1.",
        1,
    )
    rendered = rendered.replace(
        body_marker,
        (
            f"<script>{selection_script}</script>\n"
            f"<script>{pricing_script}</script>\n"
            f"<script>{version_script}</script>\n"
            f"{body_marker}"
        ),
        1,
    )
    return rendered
