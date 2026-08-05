from __future__ import annotations

from pathlib import Path

PATH = Path("tools/reporting/configuration_shortlist_equipment_groups.js")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def main() -> None:
    text = PATH.read_text(encoding="utf-8")
    text = replace_once(
        text,
        'const MARKER = "configuration_shortlist_equipment_groups_v1_8";\n  const OBSERVATION_KIND = "configurator_observation";\n  const STORAGE_KEY = "dkb-configurator-observation-filters-v1";',
        'const MARKER = "configuration_shortlist_equipment_groups_v1_9";\n  const OBSERVATION_KIND = "configurator_observation";\n  const STORAGE_KEY = "dkb-configurator-observation-filters-v2";',
        "version marker",
    )
    text = replace_once(
        text,
        '''    upholsteries: selectedValues("#configurator-selected-upholsteries"),
    standard_equipment: selectedValues("#configurator-standard-equipment"),
  });''',
        '''    upholsteries: selectedValues("#configurator-selected-upholsteries"),
    standard_equipment: selectedValues("#configurator-standard-equipment"),
    technical_data: selectedValues("#configurator-technical-data"),
  });''',
        "criteria reader",
    )
    text = replace_once(
        text,
        '''    || criteria.upholsteries.length > 0
    || criteria.standard_equipment.length > 0;''',
        '''    || criteria.upholsteries.length > 0
    || criteria.standard_equipment.length > 0
    || (criteria.technical_data || []).length > 0;''',
        "active criteria",
    )
    text = replace_once(
        text,
        '''    const sourceLines = new Set(observation.standard_equipment_source_lines || []);
    return (!criteria.colours.length || criteria.colours.includes(colour))
      && (!criteria.wheels.length || criteria.wheels.includes(wheels))
      && (!criteria.upholsteries.length || criteria.upholsteries.includes(upholstery))
      && criteria.standard_equipment.every((line) => sourceLines.has(line));''',
        '''    const equipmentLines = new Set(observation.standard_equipment_source_lines || []);
    const technicalLines = new Set(observation.technical_data_source_lines || []);
    return (!criteria.colours.length || criteria.colours.includes(colour))
      && (!criteria.wheels.length || criteria.wheels.includes(wheels))
      && (!criteria.upholsteries.length || criteria.upholsteries.includes(upholstery))
      && criteria.standard_equipment.every((line) => equipmentLines.has(line))
      && (criteria.technical_data || []).every((line) => technicalLines.has(line));''',
        "observation matcher",
    )
    text = replace_once(
        text,
        '''      ["#configurator-selected-upholsteries", stored.upholsteries],
      ["#configurator-standard-equipment", stored.standard_equipment],''',
        '''      ["#configurator-selected-upholsteries", stored.upholsteries],
      ["#configurator-standard-equipment", stored.standard_equipment],
      ["#configurator-technical-data", stored.technical_data],''',
        "criteria restore",
    )
    text = replace_once(
        text,
        '''      "#configurator-selected-upholsteries",
      "#configurator-standard-equipment",
    ]) {''',
        '''      "#configurator-selected-upholsteries",
      "#configurator-standard-equipment",
      "#configurator-technical-data",
    ]) {''',
        "criteria clear",
    )
    text = replace_once(
        text,
        '''    const search = document.querySelector("#configurator-standard-equipment-search");
    if (search) search.value = "";''',
        '''    for (const selector of [
      "#configurator-standard-equipment-search",
      "#configurator-technical-data-search",
    ]) {
      const search = document.querySelector(selector);
      if (search) search.value = "";
    }''',
        "search clear",
    )
    old_evidence = '''  const evidenceMarkup = (observation) => {
    const categories = (observation.standard_equipment_categories || []).map((category) =>
      `<section><h5>${escapeHtml(category.category || "Pozostałe")}</h5><ul>${
        (category.source_lines || []).map((line) => `<li>${escapeHtml(line)}</li>`).join("")
      }</ul></section>`
    ).join("");
    return `<details class="configurator-observation-evidence">
      <summary>Dane potwierdzone konfiguracją producenta</summary>
      <div class="configurator-observation-summary">
        <p><strong>Kod zapisanej konfiguracji:</strong> ${escapeHtml(observation.exact_configuration_code)}</p>
        <p><strong>Data obserwacji:</strong> ${escapeHtml(observation.observed_on)}</p>
        <p><strong>Faza źródłowa:</strong> ${escapeHtml(observation.source_phase || "current")}</p>
        <p><strong>Wybrany kolor:</strong> ${escapeHtml(observation.selected_colour?.value || "brak")}</p>
        <p><strong>Wybrane koła:</strong> ${escapeHtml(observation.selected_wheels?.value || "brak")}</p>
        <p><strong>Wybrana tapicerka:</strong> ${escapeHtml(observation.selected_upholstery?.value || "brak")}</p>
        <p><strong>Plik źródłowy:</strong> ${escapeHtml(observation.filename || observation.source_code)}</p>
      </div>
      <details class="configurator-standard-equipment-evidence">
        <summary>Dokładne wiersze wyposażenia standardowego</summary>
        ${categories}
      </details>
    </details>`;
  };'''
    new_evidence = '''  const categoryMarkup = (categories) => (categories || []).map((category) =>
    `<section><h5>${escapeHtml(category.category || "Pozostałe")}</h5><ul>${
      (category.source_lines || []).map((line) => `<li>${escapeHtml(line)}</li>`).join("")
    }</ul></section>`
  ).join("");

  const evidenceMarkup = (observation) => {
    const equipmentCategories = categoryMarkup(observation.standard_equipment_categories);
    const technicalCategories = categoryMarkup(observation.technical_data_categories);
    return `<details class="configurator-observation-evidence">
      <summary>Dane potwierdzone konfiguracją producenta</summary>
      <div class="configurator-observation-summary">
        <p><strong>Kod zapisanej konfiguracji:</strong> ${escapeHtml(observation.exact_configuration_code)}</p>
        <p><strong>Data obserwacji:</strong> ${escapeHtml(observation.observed_on)}</p>
        <p><strong>Faza źródłowa:</strong> ${escapeHtml(observation.source_phase || "current")}</p>
        <p><strong>Wybrany kolor:</strong> ${escapeHtml(observation.selected_colour?.value || "brak")}</p>
        <p><strong>Wybrane koła:</strong> ${escapeHtml(observation.selected_wheels?.value || "brak")}</p>
        <p><strong>Wybrana tapicerka:</strong> ${escapeHtml(observation.selected_upholstery?.value || "brak")}</p>
        <p><strong>Plik źródłowy:</strong> ${escapeHtml(observation.filename || observation.source_code)}</p>
      </div>
      <details class="configurator-standard-equipment-evidence">
        <summary>Dokładne wiersze wyposażenia standardowego</summary>
        ${equipmentCategories}
      </details>
      <details class="configurator-technical-data-evidence">
        <summary>Dokładne wiersze danych technicznych</summary>
        <p>Dane techniczne dotyczą wyłącznie dokładnie zapisanej konfiguracji i nie są przenoszone między wariantami.</p>
        ${technicalCategories}
      </details>
    </details>`;
  };'''
    text = replace_once(text, old_evidence, new_evidence, "evidence markup")
    text = replace_once(
        text,
        '''        <label class="configurator-standard-equipment-filter">Dokładne wiersze wyposażenia standardowego
          <input id="configurator-standard-equipment-search" type="search" placeholder="Szukaj w dokładnych wierszach źródłowych">
          <select id="configurator-standard-equipment" multiple size="10"></select>
        </label>
        <p class="configurator-observation-note">Filtry odnoszą się wyłącznie do zapisanych konfiguracji z eksportów producenta. Nie oznaczają dostępności innych kolorów, kół, tapicerek ani elementów wyposażenia.</p>''',
        '''        <label class="configurator-standard-equipment-filter">Dokładne wiersze wyposażenia standardowego
          <input id="configurator-standard-equipment-search" type="search" placeholder="Szukaj w dokładnych wierszach źródłowych">
          <select id="configurator-standard-equipment" multiple size="10"></select>
        </label>
        <label class="configurator-standard-equipment-filter">Dokładne wiersze danych technicznych
          <input id="configurator-technical-data-search" type="search" placeholder="Szukaj w dokładnych wierszach danych technicznych">
          <select id="configurator-technical-data" multiple size="10"></select>
        </label>
        <p class="configurator-observation-note">Filtry odnoszą się wyłącznie do zapisanych konfiguracji z eksportów producenta. Nie oznaczają katalogowej dostępności innych kolorów, kół, tapicerek, elementów wyposażenia ani parametrów technicznych.</p>''',
        "technical filter panel",
    )
    text = replace_once(
        text,
        '''    fillSelect(
      "#configurator-standard-equipment",
      uniqueSorted(observations.flatMap((item) => item.standard_equipment_source_lines || []))
    );
    restoreCriteria();''',
        '''    fillSelect(
      "#configurator-standard-equipment",
      uniqueSorted(observations.flatMap((item) => item.standard_equipment_source_lines || []))
    );
    fillSelect(
      "#configurator-technical-data",
      uniqueSorted(observations.flatMap((item) => item.technical_data_source_lines || []))
    );
    restoreCriteria();''',
        "technical filter values",
    )
    text = replace_once(
        text,
        '''    const search = panel.querySelector("#configurator-standard-equipment-search");
    if (search) {
      search.addEventListener("input", () => {
        const query = search.value.trim().toLocaleLowerCase("pl");
        const select = panel.querySelector("#configurator-standard-equipment");
        for (const option of select.options) {
          option.hidden = Boolean(query) && !option.textContent.toLocaleLowerCase("pl").includes(query);
        }
      });
    }''',
        '''    for (const [searchSelector, selectSelector] of [
      ["#configurator-standard-equipment-search", "#configurator-standard-equipment"],
      ["#configurator-technical-data-search", "#configurator-technical-data"],
    ]) {
      const search = panel.querySelector(searchSelector);
      const select = panel.querySelector(selectSelector);
      if (!search || !select) continue;
      search.addEventListener("input", () => {
        const query = search.value.trim().toLocaleLowerCase("pl");
        for (const option of select.options) {
          option.hidden = Boolean(query) && !option.textContent.toLocaleLowerCase("pl").includes(query);
        }
      });
    }''',
        "source-line search handlers",
    )
    PATH.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
