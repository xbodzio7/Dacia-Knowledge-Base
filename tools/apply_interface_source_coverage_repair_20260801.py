#!/usr/bin/env python3
"""Apply the bounded interface and Sandero price-coverage repair."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"

SOURCE = "src_pl_sandero_stepway_price_my26_20260703"
PRICE_DATE = "2026-07-03"

MAPPINGS = (
    ("sandero_rear_view_camera_option", "sandero_iii_expression_tce100_manual", "700"),
    ("sandero_rear_view_camera_option", "sandero_iii_expression_ecog120_automatic", "700"),
    ("sandero_media_nav_live_option", "sandero_iii_expression_tce100_manual", "1600"),
    ("sandero_media_nav_live_option", "sandero_iii_expression_ecog120_automatic", "1600"),
    ("sandero_media_nav_live_option", "sandero_stepway_iii_expression_tce110_manual", "1600"),
    ("sandero_glass_sunroof_option", "sandero_stepway_iii_extreme_tce110_manual", "2200"),
    ("sandero_comfort_auto_package", "sandero_iii_expression_ecog120_automatic", "2000"),
    ("sandero_thermo_package", "sandero_iii_expression_tce100_manual", "1900"),
    ("sandero_thermo_package", "sandero_iii_expression_ecog120_automatic", "1900"),
    ("sandero_thermo_package", "sandero_stepway_iii_expression_tce110_manual", "1900"),
    ("sandero_winter_package", "sandero_iii_journey_tce100_manual", "1200"),
    ("sandero_winter_package", "sandero_iii_journey_ecog120_automatic", "1200"),
    ("sandero_winter_package", "sandero_stepway_iii_extreme_tce110_manual", "1200"),
    ("sandero_media_nav_live_package", "sandero_iii_journey_tce100_manual", "1600"),
    ("sandero_media_nav_live_package", "sandero_iii_journey_ecog120_automatic", "1600"),
    ("sandero_media_nav_live_package", "sandero_stepway_iii_extreme_tce110_manual", "1600"),
    ("sandero_easy_package", "sandero_iii_journey_tce100_manual", "1600"),
    ("sandero_easy_package", "sandero_iii_journey_ecog120_automatic", "1600"),
    ("sandero_easy_package", "sandero_stepway_iii_extreme_tce110_manual", "1600"),
)


def replace_once(text: str, old: str, new: str, *, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def append_commercial_mappings() -> None:
    path = MASTER / "commercial_item_configurations.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    expected = [
        "id", "code", "commercial_item_code", "configuration_code",
        "availability_status", "amount", "currency_code", "price_date",
        "source_code", "notes",
    ]
    if fieldnames != expected:
        raise RuntimeError("unexpected commercial mapping schema")
    existing_codes = {row["code"] for row in rows}
    next_id = max(int(row["id"]) for row in rows) + 1
    note = (
        "Exact trim-level applicability and gross amount from the official "
        "Polish Sandero/Sandero Stepway MY26 option matrix effective "
        "2026-07-03; no cross-configuration inference."
    )
    for item_code, configuration_code, amount in MAPPINGS:
        code = f"{item_code}__{configuration_code}"
        if code in existing_codes:
            continue
        rows.append(
            {
                "id": str(next_id),
                "code": code,
                "commercial_item_code": item_code,
                "configuration_code": configuration_code,
                "availability_status": "optional",
                "amount": amount,
                "currency_code": "PLN",
                "price_date": PRICE_DATE,
                "source_code": SOURCE,
                "notes": note,
            }
        )
        existing_codes.add(code)
        next_id += 1
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def patch_selection_module() -> None:
    path = ROOT / "tools/reporting/configuration_shortlist_selection.js"
    text = path.read_text(encoding="utf-8")
    text = replace_once(
        text,
        '    if (!state) return "brak danych";\n',
        '    if (!state) return "brak wpisu w bazie";\n',
        label="missing equipment state",
    )
    text = replace_once(
        text,
        '    if (status !== "optional") return "brak danych";\n',
        '    if (status !== "optional") return "brak wpisu w bazie";\n',
        label="unexpected equipment state",
    )
    text = replace_once(
        text,
        '    if (!selected || !selected.components.length) return "opcjonalne — cena nieustalona";\n',
        '    if (!selected || !selected.components.length) return "opcjonalne — brak powiązania z cennikiem";\n',
        label="unmapped optional equipment",
    )
    text = replace_once(
        text,
        '        ? "cena nieustalona"\n',
        '        ? "cena niepodana w źródle"\n',
        label="mapped blank price",
    )
    old_value = '''  function comparisonValueText(configuration, key) {
    const state = configuration && configuration.comparison_values && configuration.comparison_values[key];
    return state && state.display_value ? state.display_value : "brak danych";
  }
'''
    new_value = '''  function comparisonValueText(configuration, key) {
    const state = configuration && configuration.comparison_values && configuration.comparison_values[key];
    return state && state.display_value ? state.display_value : "brak wpisu w bazie";
  }

  function sourceTitle(state, missingLabel) {
    if (!state) return missingLabel;
    const source = String(state.source_code || "").trim();
    const date = String(state.observation_date || "").trim();
    const parts = [];
    if (source) parts.push(`Źródło: ${source}`);
    if (date) parts.push(`obserwacja: ${date}`);
    return parts.join("; ");
  }

  function comparisonValueTitle(configuration, key) {
    const state = configuration && configuration.comparison_values && configuration.comparison_values[key];
    return sourceTitle(
      state,
      "Brak rekordu w bazie nie oznacza, że parametr nie występuje w dokumencie źródłowym."
    );
  }

  function equipmentComparisonTitle(configuration, code) {
    const state = configuration && configuration.equipment && configuration.equipment[code];
    return sourceTitle(
      state,
      "Brak rekordu dostępności wyposażenia w bazie."
    );
  }
'''
    text = replace_once(text, old_value, new_value, label="comparison provenance helpers")
    text = replace_once(
        text,
        '''        values: configurations.map((item) => comparisonValueText(item, facet.key)),
        comparison_value_key: facet.key
''',
        '''        values: configurations.map((item) => comparisonValueText(item, facet.key)),
        titles: configurations.map((item) => comparisonValueTitle(item, facet.key)),
        comparison_value_key: facet.key
''',
        label="technical provenance titles",
    )
    text = replace_once(
        text,
        '''        values: configurations.map((item) => equipmentComparisonStatus(item, facet.code)),
        equipment_code: facet.code
''',
        '''        values: configurations.map((item) => equipmentComparisonStatus(item, facet.code)),
        titles: configurations.map((item) => equipmentComparisonTitle(item, facet.code)),
        equipment_code: facet.code
''',
        label="equipment provenance titles",
    )
    old_cells = '''      const values = row.values.map((value) => `<td${distinct ? ' class="is-different"' : ""}>${escapeHtml(value)}</td>`).join("");
'''
    new_cells = '''      const values = row.values.map((value, index) => {
        const title = row.titles && row.titles[index] ? String(row.titles[index]) : "";
        const note = title
          ? `<span class="comparison-source-note" tabindex="0" title="${escapeHtml(title)}" aria-label="${escapeHtml(title)}">i</span>`
          : "";
        return `<td${distinct ? ' class="is-different"' : ""}>${escapeHtml(value)}${note}</td>`;
      }).join("");
'''
    text = replace_once(text, old_cells, new_cells, label="comparison cell markup")
    text = replace_once(
        text,
        '''    comparisonRows, comparisonValueFacets, comparisonValueLabel, comparisonValueText, comparisonEquipmentFacets, equipmentComparisonStatus,
''',
        '''    comparisonRows, comparisonValueFacets, comparisonValueLabel, comparisonValueText, comparisonValueTitle, comparisonEquipmentFacets, equipmentComparisonStatus, equipmentComparisonTitle,
''',
        label="selection exports",
    )
    path.write_text(text, encoding="utf-8")


def patch_pricing_module() -> None:
    path = ROOT / "tools/reporting/configuration_shortlist_v12_pricing.js"
    text = path.read_text(encoding="utf-8")
    text = replace_once(
        text,
        '        const price = component.amount === null ? "cena nieustalona" : "dopłata ujęta powyżej";\n',
        '        const price = component.amount === null ? "cena niepodana w źródle" : "dopłata ujęta powyżej";\n',
        label="selected mapped blank price",
    )
    text = replace_once(
        text,
        '    if (item.availability_status === "optional") return "opcjonalne — cena nieustalona";\n',
        '    if (item.availability_status === "optional") return "opcjonalne — brak powiązania z cennikiem";\n',
        label="selected unmapped option",
    )
    old_unknown = '''      ...breakdown.unknown_components.map((component) =>
        `<li class="price-component-unknown"><span>${escapeHtml(component.name)}</span><strong>cena nieustalona</strong></li>`)
'''
    new_unknown = '''      ...breakdown.unknown_components.map((component) => {
        const status = component.source_code
          ? "cena niepodana w źródle"
          : "brak powiązania z cennikiem";
        return `<li class="price-component-unknown"><span>${escapeHtml(component.name)}</span><strong>${escapeHtml(status)}</strong></li>`;
      })
'''
    text = replace_once(text, old_unknown, new_unknown, label="unknown price breakdown")
    text = replace_once(
        text,
        '      ? \'<p class="configuration-price-warning">Nieznane dopłaty nie zostały doliczone do ceny.</p>\' : "";\n',
        '      ? \'<p class="configuration-price-warning">Niepełne dopłaty nie zostały doliczone do ceny.</p>\' : "";\n',
        label="price warning",
    )
    path.write_text(text, encoding="utf-8")


def patch_selection_test() -> None:
    path = ROOT / "tests/test_configuration_selection_export.py"
    text = path.read_text(encoding="utf-8")
    text = replace_once(
        text,
        '        self.assertEqual(power_row["values"], ["90 kW", "brak danych", "brak danych"])\n',
        '        self.assertEqual(power_row["values"], ["90 kW", "brak wpisu w bazie", "brak wpisu w bazie"])\n',
        label="comparison missing-state expectation",
    )
    path.write_text(text, encoding="utf-8")


def main() -> None:
    append_commercial_mappings()
    patch_selection_module()
    patch_pricing_module()
    patch_selection_test()


if __name__ == "__main__":
    main()
