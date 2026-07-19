(function (root, factory) {
  "use strict";
  const api = factory();
  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  }
  root.DkbConfigurationSelection = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  function catalogOrder(catalog) {
    return new Map(
      catalog.configurations.map((item, index) => [item.configuration_code, index])
    );
  }

  function configurationMap(catalog) {
    return new Map(
      catalog.configurations.map((item) => [item.configuration_code, item])
    );
  }

  function normalizeSelection(catalog, codes) {
    const order = catalogOrder(catalog);
    return [...new Set((codes || []).map(String).map((code) => code.trim()).filter((code) => order.has(code)))]
      .sort((left, right) => order.get(left) - order.get(right));
  }

  function unionSelection(catalog, selectedCodes, addedCodes) {
    return normalizeSelection(catalog, [...(selectedCodes || []), ...(addedCodes || [])]);
  }

  function removeSelection(catalog, selectedCodes, removedCode) {
    return normalizeSelection(
      catalog,
      (selectedCodes || []).filter((code) => code !== removedCode)
    );
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

  function decorateCards(results, selected) {
    for (const card of results.querySelectorAll(".result-card")) {
      const codeElement = card.querySelector(".configuration-code");
      if (!codeElement) continue;
      const code = codeElement.textContent.trim();
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
        card.prepend(label);
      }
      toggle.checked = selected.has(code);
    }
  }

  function visibleCodes(results) {
    return [...results.querySelectorAll(".result-card[data-configuration-code]")]
      .map((card) => card.dataset.configurationCode)
      .filter(Boolean);
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
      text.textContent = `${configuration.model_name} ${configuration.version_name} — ${code}`;
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
  }

  function initialize() {
    const catalogElement = document.querySelector("#configuration-catalog");
    const results = document.querySelector("#results");
    const panel = document.querySelector("#selection-panel");
    if (!catalogElement || !results || !panel) return;

    const catalog = JSON.parse(catalogElement.textContent);
    const selected = new Set();
    const count = document.querySelector("#selected-count");
    const list = document.querySelector("#selected-list");
    const buttons = {
      selectVisible: document.querySelector("#select-visible"),
      clear: document.querySelector("#clear-selection"),
      json: document.querySelector("#download-selection-json"),
      codes: document.querySelector("#download-selection-codes")
    };

    const orderedSelection = () => normalizeSelection(catalog, selected);
    const sync = () => {
      decorateCards(results, selected);
      renderSelectionSummary(catalog, selected, list, count, buttons);
    };
    const observer = new MutationObserver(sync);
    observer.observe(results, { childList: true, subtree: true });
    sync();

    results.addEventListener("change", (event) => {
      const toggle = event.target.closest(".configuration-select");
      if (!toggle) return;
      if (toggle.checked) selected.add(toggle.value);
      else selected.delete(toggle.value);
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

    list.addEventListener("click", (event) => {
      const remove = event.target.closest(".remove-selection");
      if (!remove) return;
      selected.delete(remove.dataset.configurationCode);
      sync();
    });

    buttons.json.addEventListener("click", () => {
      const codes = orderedSelection();
      downloadText(
        exportFilename(catalog, codes, "json"),
        renderSelectionJson(catalog, codes),
        "application/json;charset=utf-8"
      );
    });

    buttons.codes.addEventListener("click", () => {
      const codes = orderedSelection();
      downloadText(
        exportFilename(catalog, codes, "txt"),
        renderCodeList(catalog, codes),
        "text/plain;charset=utf-8"
      );
    });
  }

  if (typeof document !== "undefined") {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initialize);
    else initialize();
  }

  return {
    normalizeSelection,
    unionSelection,
    removeSelection,
    selectedConfigurations,
    buildSelectionPayload,
    renderSelectionJson,
    renderCodeList,
    exportFilename
  };
});
