from __future__ import annotations

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
@media(max-width:760px){.selection-panel{position:static;grid-template-columns:1fr}.selection-actions{justify-content:flex-start}.selected-list{grid-column:auto}}
@media print{.selection-panel,.selection-toggle{display:none!important}}
'''


def render_html(catalog: Mapping[str, Any]) -> str:
    rendered = render_base_html(catalog)
    script_path = Path(__file__).with_name(
        "configuration_shortlist_selection.js"
    )
    try:
        script = script_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise core.ShortlistError(
            f"cannot read browser selection script: {exc}"
        ) from exc

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
        body_marker,
        f"<script>{script}</script>\n{body_marker}",
        1,
    )
    return rendered
