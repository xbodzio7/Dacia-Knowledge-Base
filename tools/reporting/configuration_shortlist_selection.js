(function (root, factory) {
  "use strict";
  const pricing = root.DkbConfigurationPricingV12
    || (typeof require !== "undefined" ? require("./configuration_shortlist_v12_pricing.js") : null);
  const api = factory(pricing);
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  root.DkbConfigurationSelection = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function (pricing) {
  "use strict";


  const CATEGORY_LABELS = Object.freeze({
    ADAS: "Systemy wspomagania kierowcy", Acoustics: "Akustyka",
    Brakes: "Hamulce", Capacities: "Pojemności",
    Consumption: "Zużycie paliwa i energii", Dimensions: "Wymiary",
    Doors: "Drzwi i dostęp", Drivetrain: "Układ napędowy",
    "Driving Systems": "Prowadzenie i parkowanie", Efficiency: "Efektywność",
    "Electric System": "Instalacja elektryczna", Emissions: "Emisje",
    Engine: "Silnik", Exterior: "Nadwozie i wygląd zewnętrzny",
    HVAC: "Ogrzewanie, wentylacja i klimatyzacja", "Hybrid System": "Układ hybrydowy",
    Infotainment: "Multimedia", Lighting: "Widoczność i oświetlenie",
    Mirrors: "Lusterka", Performance: "Osiągi", Powertrain: "Zespół napędowy",
    Safety: "Bezpieczeństwo", Seats: "Fotele i kanapa", Steering: "Układ kierowniczy",
    Suspension: "Zawieszenie", Towing: "Holowanie", Transmission: "Skrzynia biegów",
    Weights: "Masy", Wheels: "Koła i opony", Windows: "Szyby",
    Comfort: "Komfort i wnętrze", Parking: "Parkowanie", Pozostałe: "Pozostałe"
  });

  function categoryLabel(category) {
    const artworkApi = typeof globalThis !== "undefined" ? globalThis.DkbConfigurationShortlistV12 : null;
    if (artworkApi && typeof artworkApi.categoryLabel === "function") return artworkApi.categoryLabel(category);
    return CATEGORY_LABELS[category] || String(category || "Pozostałe");
  }
  function catalogOrder(catalog) {
    return new Map(catalog.configurations.map((item, index) => [item.configuration_code, index]));
  }

  function configurationMap(catalog) {
    return new Map(catalog.configurations.map((item) => [item.configuration_code, item]));
  }

  function normalizeSelection(catalog, codes) {
    const order = catalogOrder(catalog);
    const values = codes == null ? [] : Array.from(codes);
    return [...new Set(values.map(String).map((code) => code.trim()).filter((code) => order.has(code)))]
      .sort((left, right) => order.get(left) - order.get(right));
  }

  function unionSelection(catalog, selectedCodes, addedCodes) {
    return normalizeSelection(catalog, [...(selectedCodes || []), ...(addedCodes || [])]);
  }

  function removeSelection(catalog, selectedCodes, removedCode) {
    return normalizeSelection(catalog, Array.from(selectedCodes || []).filter((code) => code !== removedCode));
  }

  function selectedConfigurations(catalog, selectedCodes) {
    const byCode = configurationMap(catalog);
    return normalizeSelection(catalog, selectedCodes).map((code) => byCode.get(code));
  }

  function exportResult(configuration) {
    return {
      configuration_code: configuration.configuration_code,
      model_code: configuration.model_code,
      model_name: configuration.model_name,
      version_code: configuration.version_code,
      version_name: configuration.version_name,
      powertrain_label: configuration.powertrain_label,
      transmission_type: configuration.transmission_type,
      catalog_price: configuration.catalog_price,
      number_of_seats: configuration.number_of_seats
    };
  }

  function buildSelectionPayload(catalog, selectedCodes) {
    const results = selectedConfigurations(catalog, selectedCodes).map(exportResult);
    return {
      version: 1,
      export_type: "interactive_configuration_selection",
      as_of: catalog.as_of,
      selection_summary: {
        selected_configuration_count: results.length,
        catalog_configuration_count: catalog.configurations.length
      },
      results
    };
  }

  function renderSelectionJson(catalog, selectedCodes) {
    return `${JSON.stringify(buildSelectionPayload(catalog, selectedCodes), null, 2)}\n`;
  }

  function renderCodeList(catalog, selectedCodes) {
    const codes = normalizeSelection(catalog, selectedCodes);
    return codes.length ? `${codes.join("\n")}\n` : "";
  }

  function exportFilename(catalog, selectedCodes, extension) {
    const count = normalizeSelection(catalog, selectedCodes).length;
    const safeDate = String(catalog.as_of || "snapshot").replace(/[^0-9A-Za-z_-]/g, "-");
    return `dacia-configuration-selection-${safeDate}-${count}.${extension}`;
  }

  function formatCatalogPrice(configuration) {
    const price = configuration.catalog_price || {};
    if (price.state !== "recorded") return "brak danych";
    if (pricing) return pricing.formatMoney(price.amount, price.currency_code || "PLN");
    return `${Number(price.amount).toLocaleString("pl-PL")} ${price.currency_code || "PLN"}`;
  }

  function formatSeats(configuration) {
    const seats = configuration.number_of_seats || {};
    return seats.state === "recorded" ? String(seats.value) : "brak danych";
  }

  function equipmentComparisonStatus(configuration, code) {
    const state = configuration && configuration.equipment && configuration.equipment[code];
    if (!state) return "brak danych";
    const status = state.availability_status;
    if (status === "standard") return "seryjne";
    if (status === "not_available") return "niedostępne";
    if (status === "unknown") return "status nieustalony";
    if (status !== "optional") return "brak danych";
    if (!pricing) return "opcjonalne";
    const breakdown = pricing.buildPriceBreakdown(configuration, [code], []);
    const selected = breakdown.selected_equipment && breakdown.selected_equipment[0];
    if (!selected || !selected.components.length) return "opcjonalne — cena nieustalona";
    return selected.components.map((component) => {
      const kind = component.kind === "package" ? "pakiet" : "opcja";
      const price = component.amount === null
        ? "cena nieustalona"
        : `+ ${pricing.formatMoney(component.amount, breakdown.currency_code)}`;
      return `${kind}: ${component.name} (${price})`;
    }).join("; ");
  }

  function comparisonEquipmentFacets(catalog, configurations) {
    const facets = (catalog.facets && catalog.facets.equipment || []).filter((facet) =>
      configurations.some((configuration) => Object.prototype.hasOwnProperty.call(configuration.equipment || {}, facet.code))
    );
    return facets.slice().sort((left, right) =>
      categoryLabel(left.category).localeCompare(categoryLabel(right.category), "pl")
      || (pricing ? pricing.equipmentLabel(left.code, left.name) : String(left.name || left.code))
        .localeCompare(pricing ? pricing.equipmentLabel(right.code, right.name) : String(right.name || right.code), "pl")
      || String(left.code).localeCompare(String(right.code))
    );
  }

  function comparisonRows(catalog, selectedCodes, equipmentCodes) {
    const configurations = selectedConfigurations(catalog, selectedCodes);
    const equipment = [...new Set((equipmentCodes || []).map(String).filter(Boolean))];
    const rows = [
      { key: "model", category: "Dane podstawowe", label: "Model", values: configurations.map((item) => item.model_name) },
      { key: "version", category: "Dane podstawowe", label: "Wersja", values: configurations.map((item) => item.version_name) },
      { key: "powertrain", category: "Dane podstawowe", label: "Napęd", values: configurations.map((item) => item.powertrain_label) },
      { key: "transmission", category: "Dane podstawowe", label: "Skrzynia", values: configurations.map((item) => item.transmission_type === "automatic" ? "automatyczna" : item.transmission_type === "manual" ? "manualna" : item.transmission_type) },
      { key: "catalog_price", category: "Dane podstawowe", label: "Cena katalogowa", values: configurations.map(formatCatalogPrice) },
      { key: "seats", category: "Dane podstawowe", label: "Liczba miejsc", values: configurations.map(formatSeats) }
    ];

    if (equipment.length && pricing) {
      rows.push({
        key: "configured_price", category: "Dane podstawowe", label: "Cena z wybranym wyposażeniem",
        values: configurations.map((item) => {
          const breakdown = pricing.buildPriceBreakdown(item, equipment, []);
          if (breakdown.total_amount === null) return "brak danych";
          const amount = pricing.formatMoney(breakdown.total_amount, breakdown.currency_code);
          return breakdown.total_is_complete ? amount : `od ${amount}`;
        })
      });
    }

    for (const facet of comparisonEquipmentFacets(catalog, configurations)) {
      rows.push({
        key: `equipment:${facet.code}`,
        category: categoryLabel(facet.category),
        label: pricing ? pricing.equipmentLabel(facet.code, facet.name) : String(facet.name || facet.code),
        values: configurations.map((item) => equipmentComparisonStatus(item, facet.code)),
        equipment_code: facet.code
      });
    }
    return { configurations, rows };
  }

  function escapeHtml(value) {
    return String(value).replaceAll("&", "&amp;").replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#39;");
  }

  function comparisonThumbnail(configuration) {
    const thumbnailApi = typeof globalThis !== "undefined"
      ? globalThis.DkbConfigurationShortlistV12
      : null;
    if (!thumbnailApi || typeof thumbnailApi.modelThumbnailSvg !== "function") return "";
    return `<span class="comparison-model-thumbnail">${thumbnailApi.modelThumbnailSvg(
      configuration.model_code, configuration.model_name, configuration.version_name
    )}</span>`;
  }

  function rowIsDifferent(values) {
    return new Set(values.map((value) => String(value).trim())).size > 1;
  }

  function applyDifferenceFilter(table, onlyDifferences) {
    if (!table) return;
    const dataRows = [...table.querySelectorAll("tr.comparison-data-row")];
    for (const row of dataRows) {
      row.hidden = Boolean(onlyDifferences && row.dataset.different !== "true");
    }
    for (const heading of table.querySelectorAll("tr.comparison-category-row")) {
      const category = heading.dataset.category;
      heading.hidden = !dataRows.some((row) => row.dataset.category === category && !row.hidden);
    }
    table.classList.toggle("differences-only", Boolean(onlyDifferences));
  }

  function renderComparison(catalog, selectedCodes, equipmentCodes, table, options) {
    const comparison = comparisonRows(catalog, selectedCodes, equipmentCodes);
    if (comparison.configurations.length < 2) {
      table.innerHTML = "";
      return comparison;
    }
    const header = comparison.configurations.map((configuration) => {
      const transmission = configuration.transmission_type === "automatic" ? "automatyczna" : configuration.transmission_type === "manual" ? "manualna" : configuration.transmission_type;
      return `<th scope="col">${comparisonThumbnail(configuration)}<strong>${escapeHtml(configuration.model_name)}</strong><span class="comparison-version">${escapeHtml(configuration.version_name)} · ${escapeHtml(configuration.powertrain_label)} · ${escapeHtml(transmission)}</span></th>`;
    }).join("");
    const body = [];
    let currentCategory = null;
    for (const row of comparison.rows) {
      if (row.category !== currentCategory) {
        currentCategory = row.category;
        body.push(`<tr class="comparison-category-row" data-category="${escapeHtml(currentCategory)}"><th colspan="${comparison.configurations.length + 1}">${escapeHtml(currentCategory)}</th></tr>`);
      }
      const distinct = rowIsDifferent(row.values);
      const values = row.values.map((value) => `<td${distinct ? ' class="is-different"' : ""}>${escapeHtml(value)}</td>`).join("");
      body.push(`<tr class="comparison-data-row" data-category="${escapeHtml(currentCategory)}" data-different="${distinct ? "true" : "false"}"><th scope="row">${escapeHtml(row.label)}</th>${values}</tr>`);
    }
    table.innerHTML = `<thead><tr><th scope="col">Parametr</th>${header}</tr></thead><tbody>${body.join("")}</tbody>`;
    applyDifferenceFilter(table, options && options.onlyDifferences);
    return comparison;
  }

  function decorateCards(results, selected) {
    for (const card of results.querySelectorAll(".result-card")) {
      const codeElement = card.querySelector(".configuration-code");
      const code = card.dataset.configurationCode || (codeElement ? codeElement.textContent.trim() : "");
      if (!code) continue;
      card.dataset.configurationCode = code;
      let toggle = card.querySelector(".configuration-select");
      if (!toggle) {
        const label = document.createElement("label");
        label.className = "selection-toggle";
        toggle = document.createElement("input");
        toggle.className = "configuration-select";
        toggle.type = "checkbox";
        toggle.value = code;
        toggle.setAttribute("aria-label", `Wybierz konfigurację ${code}`);
        label.append(toggle, document.createTextNode(" Wybierz do porównania"));
        const hero = card.querySelector(".result-card-hero");
        if (hero && hero.nextSibling) card.insertBefore(label, hero.nextSibling);
        else if (hero) card.append(label);
        else card.prepend(label);
      }
      toggle.checked = selected.has(code);
    }
  }

  function visibleCodes(results) {
    return [...results.querySelectorAll(".result-card[data-configuration-code]")]
      .map((card) => card.dataset.configurationCode).filter(Boolean);
  }

  function downloadText(filename, content, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.append(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  function renderSelectionSummary(catalog, selected, list, count, buttons) {
    const ordered = normalizeSelection(catalog, selected);
    count.textContent = ordered.length;
    list.replaceChildren();
    const byCode = configurationMap(catalog);
    for (const code of ordered) {
      const configuration = byCode.get(code);
      const item = document.createElement("li");
      const text = document.createElement("span");
      text.textContent = `${configuration.model_name} ${configuration.version_name} · ${configuration.powertrain_label}`;
      const remove = document.createElement("button");
      remove.type = "button";
      remove.className = "remove-selection";
      remove.dataset.configurationCode = code;
      remove.textContent = "Usuń";
      item.append(text, remove);
      list.append(item);
    }
    const disabled = ordered.length === 0;
    buttons.clear.disabled = disabled;
    buttons.json.disabled = disabled;
    buttons.codes.disabled = disabled;
    buttons.compare.disabled = ordered.length < 2;
    buttons.compare.textContent = ordered.length >= 2 ? `Porównaj wybrane (${ordered.length})` : "Porównaj wybrane";
  }

  function initialize() {
    const catalogElement = document.querySelector("#configuration-catalog");
    const results = document.querySelector("#results");
    const panel = document.querySelector("#selection-panel");
    if (!catalogElement || !results || !panel) return;

    const catalog = JSON.parse(catalogElement.textContent);
    if (pricing) pricing.setEquipmentLabels(catalog.interface_labels?.equipment_pl || {});
    const selected = new Set();
    const count = document.querySelector("#selected-count");
    const list = document.querySelector("#selected-list");
    const comparisonPanel = document.querySelector("#comparison-panel");
    const comparisonTable = document.querySelector("#comparison-table");
    const differencesOnly = document.querySelector("#comparison-differences-only");
    const buttons = {
      selectVisible: document.querySelector("#select-visible"),
      clear: document.querySelector("#clear-selection"),
      compare: document.querySelector("#compare-selection"),
      closeComparison: document.querySelector("#close-comparison"),
      json: document.querySelector("#download-selection-json"),
      codes: document.querySelector("#download-selection-codes")
    };

    const orderedSelection = () => normalizeSelection(catalog, selected);
    const selectedEquipment = () => [...(document.querySelector("#required-equipment")?.selectedOptions || [])].map((option) => option.value);
    const refreshComparison = () => {
      if (!comparisonPanel || comparisonPanel.hidden) return;
      renderComparison(catalog, selected, selectedEquipment(), comparisonTable, { onlyDifferences: Boolean(differencesOnly && differencesOnly.checked) });
    };
    const sync = () => {
      decorateCards(results, selected);
      renderSelectionSummary(catalog, selected, list, count, buttons);
      if (orderedSelection().length < 2 && comparisonPanel) comparisonPanel.hidden = true;
      refreshComparison();
    };
    results.addEventListener("dkb:results-rendered", sync);
    sync();

    results.addEventListener("change", (event) => {
      const toggle = event.target.closest(".configuration-select");
      if (!toggle) return;
      if (toggle.checked) selected.add(toggle.value); else selected.delete(toggle.value);
      sync();
    });

    buttons.selectVisible.addEventListener("click", () => {
      const combined = unionSelection(catalog, selected, visibleCodes(results));
      selected.clear();
      for (const code of combined) selected.add(code);
      sync();
    });
    buttons.clear.addEventListener("click", () => {
      selected.clear();
      sync();
    });
    buttons.compare.addEventListener("click", () => {
      if (orderedSelection().length < 2) return;
      comparisonPanel.hidden = false;
      renderComparison(catalog, selected, selectedEquipment(), comparisonTable, { onlyDifferences: Boolean(differencesOnly && differencesOnly.checked) });
      comparisonPanel.scrollIntoView({ behavior: "smooth", block: "start" });
    });
    buttons.closeComparison.addEventListener("click", () => { comparisonPanel.hidden = true; });

    list.addEventListener("click", (event) => {
      const remove = event.target.closest(".remove-selection");
      if (!remove) return;
      selected.delete(remove.dataset.configurationCode);
      sync();
    });
    document.addEventListener("change", (event) => {
      if (event.target.matches("#required-equipment, #comparison-differences-only")) refreshComparison();
    });

    buttons.json.addEventListener("click", () => {
      const codes = orderedSelection();
      downloadText(exportFilename(catalog, codes, "json"), renderSelectionJson(catalog, codes), "application/json;charset=utf-8");
    });
    buttons.codes.addEventListener("click", () => {
      const codes = orderedSelection();
      downloadText(exportFilename(catalog, codes, "txt"), renderCodeList(catalog, codes), "text/plain;charset=utf-8");
    });
  }

  if (typeof document !== "undefined") {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initialize);
    else initialize();
  }

  return {
    normalizeSelection, unionSelection, removeSelection, selectedConfigurations,
    buildSelectionPayload, renderSelectionJson, renderCodeList, exportFilename,
    comparisonRows, comparisonEquipmentFacets, equipmentComparisonStatus,
    renderComparison, comparisonThumbnail, applyDifferenceFilter, rowIsDifferent, categoryLabel
  };
});
