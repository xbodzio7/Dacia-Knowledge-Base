from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from reporting import configuration_shortlist as core
from reporting.configuration_shortlist_html import render_html as render_base_html


_SELECTION_PANEL = r'''  <section id="selection-panel" class="selection-panel" aria-labelledby="selection-heading">
    <div>
      <p class="eyebrow">Wybór do porównania</p>
      <h2 id="selection-heading">Wybrane konfiguracje: <span id="selected-count">0</span></h2>
      <p>Zaznacz co najmniej dwa warianty. Porównanie działa bezpośrednio na tej stronie i obsługuje więcej niż dwie konfiguracje.</p>
    </div>
    <div class="selection-actions">
      <button id="select-visible" type="button">Wybierz widoczne</button>
      <button id="clear-selection" type="button" disabled>Wyczyść wybór</button>
      <button id="compare-selection" type="button" disabled>Porównaj wybrane</button>
      <button id="download-selection-json" type="button" disabled>Pobierz JSON</button>
      <button id="download-selection-codes" type="button" disabled>Pobierz kody TXT</button>
    </div>
    <ul id="selected-list" class="selected-list"></ul>
  </section>
  <section id="comparison-panel" class="comparison-panel" aria-labelledby="comparison-heading" hidden>
    <div class="comparison-heading-row">
      <div>
        <p class="eyebrow">Porównanie wielowariantowe</p>
        <h2 id="comparison-heading">Porównanie wybranych konfiguracji</h2>
      </div>
      <div class="comparison-heading-actions">
        <label class="difference-toggle"><input id="comparison-differences-only" type="checkbox"> Pokaż tylko różnice</label>
        <button id="close-comparison" type="button">Zamknij porównanie</button>
      </div>
    </div>
    <p>Porównanie obejmuje dane podstawowe oraz całe wyposażenie opisane w bazie. Kolor tła wskazuje różnice; tabela może być przewijana poziomo.</p>
    <div class="comparison-scroll"><table id="comparison-table" class="comparison-table"></table></div>
  </section>
'''

_SELECTION_CSS = r'''
.selection-panel{position:sticky;top:10px;z-index:6;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:14px;padding:18px;margin-top:18px;background:rgba(255,255,255,.97);border:1px solid var(--line);border-radius:16px;box-shadow:0 12px 34px rgba(27,43,33,.1);backdrop-filter:blur(8px)}
.selection-panel h2,.comparison-panel h2{margin:0}.selection-panel p,.comparison-panel p{margin:5px 0;color:var(--muted)}.selection-actions{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:8px;align-content:start}.selection-actions button,.remove-selection,.comparison-heading-row button{min-height:38px;padding:7px 11px;border:1px solid #aeb8b0;border-radius:8px;background:#fff;color:var(--ink);cursor:pointer;font-weight:750}.selection-actions button:disabled{cursor:not-allowed;opacity:.45}.selection-actions #compare-selection:not(:disabled){border-color:var(--accent);background:var(--accent);color:#fff}.selected-list{grid-column:1/-1;display:flex;flex-wrap:wrap;gap:7px;margin:0;padding:0;list-style:none}.selected-list li{display:flex;align-items:center;gap:8px;padding:6px 8px 6px 10px;background:var(--soft);border-radius:999px;color:var(--accent);font-size:.76rem;font-weight:700}.remove-selection{min-height:28px;padding:3px 7px;border-color:transparent;background:rgba(255,255,255,.72);font-size:.7rem}.selection-toggle{display:flex;align-items:center;gap:6px;margin:0;color:var(--accent);font-size:.78rem;font-weight:800}.selection-toggle input{width:18px;height:18px;accent-color:var(--accent)}
.comparison-panel{scroll-margin-top:18px;padding:18px;margin-top:18px;background:var(--panel);border:1px solid var(--line);border-radius:16px;box-shadow:0 10px 28px rgba(27,43,33,.06)}.comparison-heading-row{display:flex;align-items:start;justify-content:space-between;gap:16px}.comparison-heading-actions{display:flex;align-items:center;flex-wrap:wrap;justify-content:flex-end;gap:10px}.difference-toggle{display:inline-flex;align-items:center;gap:7px;min-height:38px;padding:7px 11px;border:1px solid #aeb8b0;border-radius:8px;background:#fff;color:var(--ink);font-size:.78rem;font-weight:750;cursor:pointer}.difference-toggle input{width:18px;height:18px;accent-color:var(--accent)}.comparison-scroll{max-width:100%;overflow:auto;margin-top:14px;border:1px solid var(--line);border-radius:12px}.comparison-table{width:max-content;min-width:100%;border-collapse:separate;border-spacing:0;background:#fff;font-size:.78rem}.comparison-table th,.comparison-table td{min-width:210px;padding:10px 12px;border-right:1px solid var(--line);border-bottom:1px solid var(--line);vertical-align:top}.comparison-table th:first-child{position:sticky;left:0;z-index:2;min-width:210px;background:var(--paper);text-align:left}.comparison-table thead th{position:sticky;top:0;z-index:1;background:var(--soft);text-align:left}.comparison-table thead th:first-child{z-index:3}.comparison-table thead strong{display:block;font-size:.94rem;color:var(--ink)}.comparison-table thead .comparison-version{display:block;margin-top:4px;color:var(--muted);font-size:.7rem;font-weight:600;line-height:1.35}.comparison-table .comparison-category-row th{position:sticky;left:0;z-index:2;padding:8px 12px;background:#dfe9e2;color:var(--accent);font-size:.74rem;text-transform:uppercase;letter-spacing:.05em}.comparison-table .is-different{background:var(--warn-soft)}.comparison-table tr[hidden]{display:none}.comparison-model-thumbnail{display:block;width:190px;max-width:100%;margin:0 auto 8px;color:#65736a}.comparison-model-thumbnail svg{display:block;width:100%;height:auto}
.selected-filter-summary{display:grid;gap:7px;min-height:76px;padding:9px;border:1px solid var(--line);border-radius:9px;background:var(--paper);color:var(--ink)}.selected-filter-summary-head{display:flex;align-items:center;justify-content:space-between;gap:8px;font-size:.75rem}.selected-filter-summary-head button{width:auto;min-height:30px;padding:4px 8px;background:#fff;font-size:.72rem}.selected-filter-summary-head button:disabled{cursor:not-allowed;opacity:.45}.selected-filter-list{display:flex;flex-wrap:wrap;gap:5px;align-content:start}.selected-filter-empty{color:var(--muted);font-size:.74rem;font-weight:500}.selected-filter-chip{display:inline-flex;align-items:center;gap:6px;width:auto!important;min-height:30px!important;padding:4px 7px 4px 9px!important;border-color:#b9d4c1!important;border-radius:999px!important;background:var(--soft)!important;color:var(--accent)!important;font-size:.7rem;font-weight:750!important;text-align:left}.selected-filter-chip span{font-size:1rem;line-height:1}.result-card.is-selected{border-color:var(--accent);box-shadow:0 0 0 3px rgba(31,111,67,.15),0 12px 32px rgba(27,43,33,.1)}.result-card.is-selected .selection-toggle{padding:5px 8px;border-radius:8px;background:var(--soft)}.result-price{display:grid;gap:5px;font-size:inherit;font-weight:inherit;color:var(--ink)}.configuration-price-main{display:grid;gap:1px;color:var(--accent)}.configuration-price-main span{font-size:.72rem;font-weight:750;text-transform:uppercase;letter-spacing:.05em}.configuration-price-main strong{font-size:1.55rem;line-height:1.15}.configuration-price-standard{color:var(--muted);font-size:.78rem}.configuration-price-components{display:grid;gap:4px;margin:3px 0 0;padding:8px 0 0;border-top:1px solid var(--line);list-style:none}.configuration-price-components li{display:flex;justify-content:space-between;gap:10px;font-size:.74rem}.configuration-price-components strong{white-space:nowrap;color:var(--accent)}.configuration-price-components .price-component-unknown strong{color:var(--warn)}.configuration-price-warning{margin:0;color:var(--warn);font-size:.7rem;font-weight:700}.configuration-price-equipment{display:grid;gap:5px;margin-top:5px;padding-top:8px;border-top:1px solid var(--line)}.configuration-price-equipment>span{color:var(--muted);font-size:.7rem;font-weight:800;text-transform:uppercase;letter-spacing:.04em}.configuration-price-equipment ul{display:grid;gap:5px;margin:0;padding:0;list-style:none}.configuration-price-equipment li{display:grid;gap:1px;padding:6px 7px;border-radius:7px;background:var(--paper);font-size:.72rem}.configuration-price-equipment li span{font-weight:750}.configuration-price-equipment li strong{color:var(--muted);font-size:.68rem;font-weight:650}
.native-model-select,.native-equipment-select{display:none!important}.model-picker{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:10px}.model-choice{position:relative;display:grid!important;grid-template-rows:118px auto;align-items:center;justify-items:center;gap:6px;min-height:160px!important;padding:10px!important;background:#fff!important;color:var(--ink)!important;text-align:center}.model-choice-thumb{display:block;width:190px;max-width:100%;color:#65736a}.model-choice svg,.model-thumbnail-host svg{display:block;width:100%;height:auto}.car-body{fill:#dfe6e1;stroke:currentColor;stroke-width:2}.car-window{fill:#aebbb3;stroke:currentColor;stroke-width:1.2}.car-window-divider,.car-line,.car-rail,.car-bumper,.car-wheel-spoke{fill:none;stroke:currentColor;stroke-width:1.2;stroke-linecap:round}.car-cladding{fill:#637069;opacity:.82}.car-accent{fill:none;stroke:#8b9a91;stroke-width:3}.car-accent-extreme{stroke:#b56f16}.car-accent-journey{stroke:#6a7f99}.car-light{fill:#f3c969;stroke:currentColor;stroke-width:.8}.car-wheel{fill:#27322c}.car-wheel-ring{fill:#aab6af;stroke:#27322c;stroke-width:1}.car-wheel-spoke{stroke:#39463f}.car-hub{fill:#e2e8e4}.model-choice-check{position:absolute;top:7px;right:8px;display:none;width:22px;height:22px;border-radius:999px;background:var(--accent);color:#fff;line-height:22px}.model-choice.is-selected{border-color:var(--accent)!important;background:var(--soft)!important;box-shadow:0 0 0 2px rgba(31,111,67,.12)}.model-choice.is-selected .model-choice-check{display:block}.model-thumbnail-host{width:100%;overflow:hidden;padding:4px 6px;color:#65736a;background:linear-gradient(180deg,var(--paper),transparent);border-radius:10px}.model-thumbnail-host svg{max-height:150px}.result-card-hero{grid-template-columns:minmax(210px,44%) minmax(0,1fr)}
.equipment-picker{display:grid;gap:9px;width:100%}.equipment-picker-search{display:grid;gap:5px}.equipment-picker-search input{min-height:38px}.equipment-availability-note{margin:0!important;color:var(--muted);font-size:.72rem;font-weight:600}.equipment-availability-note.has-removal{color:var(--warn)}.equipment-picker-scroll{display:grid;gap:10px;max-height:520px;overflow:auto;padding:10px;border:1px solid var(--line);border-radius:10px;background:#fff}.equipment-picker-group{display:grid;gap:6px}.equipment-picker-group h3{margin:0;color:var(--muted);font-size:.72rem;text-transform:uppercase;letter-spacing:.05em}.equipment-picker-options{display:flex;flex-wrap:wrap;gap:6px}.equipment-choice{display:inline-flex;align-items:center;gap:6px;width:auto!important;min-height:34px!important;padding:5px 9px!important;background:#fff!important;color:var(--ink)!important;font-size:.72rem;font-weight:700!important;text-align:left}.equipment-choice span{display:none}.equipment-choice.is-selected{border-color:var(--accent)!important;background:var(--soft)!important;color:var(--accent)!important;box-shadow:0 0 0 2px rgba(31,111,67,.10)}.equipment-choice.is-selected span{display:inline}.selected-filter-actions{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:5px}.selected-filter-actions button[aria-pressed="true"]{border-color:var(--accent);background:var(--soft);color:var(--accent)}.commercial-offers{padding:8px 0;border-top:1px solid var(--line)}.commercial-offers ul{display:grid;gap:7px;margin:8px 0 0;padding:0;list-style:none}.commercial-offers li{display:flex;justify-content:space-between;gap:10px;padding:7px;border-radius:8px;background:var(--paper)}.commercial-offers li div{display:grid;gap:2px}.commercial-offers li span{color:var(--muted);font-size:.7rem}.commercial-offers li b{white-space:nowrap;color:var(--accent)}
@media(max-width:760px){.selection-panel{position:static;grid-template-columns:1fr}.selection-actions{justify-content:flex-start}.selected-list{grid-column:auto}.comparison-heading-row,.comparison-heading-actions{display:grid;justify-content:stretch}.model-picker{grid-template-columns:1fr}.result-card-hero{grid-template-columns:1fr}.comparison-model-thumbnail{width:150px}}
@media print{.selection-panel,.selection-toggle,.selected-filter-summary,.comparison-heading-actions{display:none!important}.comparison-panel{box-shadow:none}}
'''



def _read_script(name: str, label: str) -> str:
    script_path = Path(__file__).with_name(name)
    try:
        return script_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise core.ShortlistError(f"cannot read {label} script: {exc}") from exc


def _read_labels() -> dict[str, str]:
    labels_path = Path(__file__).with_name("configuration_shortlist_labels_pl.json")
    try:
        labels = json.loads(labels_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise core.ShortlistError(f"cannot read Polish equipment labels: {exc}") from exc
    if not isinstance(labels, dict) or not all(
        isinstance(code, str) and isinstance(label, str)
        for code, label in labels.items()
    ):
        raise core.ShortlistError("invalid Polish equipment label contract")
    return labels


def render_html(catalog: Mapping[str, Any]) -> str:
    enhanced_catalog = dict(catalog)
    enhanced_catalog["interface_labels"] = {"equipment_pl": _read_labels()}
    rendered = render_base_html(enhanced_catalog)
    selection_script = _read_script(
        "configuration_shortlist_selection.js", "browser selection"
    )
    pricing_script = _read_script(
        "configuration_shortlist_v12_pricing.js", "version 1.2 pricing"
    )
    version_script = _read_script(
        "configuration_shortlist_v12.js", "version 1.2 enhancement"
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
        style_marker, _SELECTION_CSS + "\n" + style_marker, 1
    )
    rendered = rendered.replace(
        results_marker, _SELECTION_PANEL + results_marker, 1
    )
    rendered = rendered.replace(
        "Format interaktywnej shortlisty HTML v1.",
        "Format interaktywnej shortlisty HTML v1.4.",
        1,
    )
    rendered = rendered.replace(
        body_marker,
        (
            f"<script>{pricing_script}</script>\n"
            f"<script>{selection_script}</script>\n"
            f"<script>{version_script}</script>\n"
            f"{body_marker}"
        ),
        1,
    )
    return rendered
