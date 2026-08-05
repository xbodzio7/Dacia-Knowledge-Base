
(function () {
  "use strict";
  const MARKER = "configuration_shortlist_equipment_groups_v1_8";
  const OBSERVATION_KIND = "configurator_observation";
  const STORAGE_KEY = "dkb-configurator-observation-filters-v1";

  const escapeHtml = (value) => String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");

  const catalogElement = typeof document !== "undefined"
    ? document.querySelector("#configuration-catalog")
    : null;
  const observationByConfiguration = new Map();
  const configurationByCode = new Map();

  if (catalogElement) {
    const catalog = JSON.parse(catalogElement.textContent);
    for (const configuration of catalog.configurations || []) {
      const components = Array.isArray(configuration.price_components)
        ? configuration.price_components
        : [];
      const observations = components.filter((item) => item && item.kind === OBSERVATION_KIND);
      if (observations.length > 1) {
        throw new Error(`multiple configurator observations for ${configuration.configuration_code}`);
      }
      if (observations.length === 1) {
        observationByConfiguration.set(configuration.configuration_code, observations[0]);
      }
      configuration.price_components = components.filter(
        (item) => !item || item.kind !== OBSERVATION_KIND
      );
      configurationByCode.set(configuration.configuration_code, configuration);
    }
    catalogElement.textContent = JSON.stringify(catalog);
  }

  const visibleChoices = (group) => [...group.querySelectorAll(".equipment-choice")]
    .filter((choice) => !choice.hidden);

  const updateSummary = (group) => {
    const meta = group.querySelector("[data-equipment-group-meta]");
    if (!meta) return;
    const visible = visibleChoices(group);
    const selected = [...group.querySelectorAll(".equipment-choice.is-selected")].length;
    meta.textContent = selected
      ? `${visible.length} pozycji · wybrane: ${selected}`
      : `${visible.length} pozycji`;
  };

  const upgradeGroup = (section) => {
    if (!section || section.matches("details[data-collapsible-equipment-group]")) return section;
    const heading = section.querySelector(":scope > h3");
    const options = section.querySelector(":scope > .equipment-picker-options");
    if (!heading || !options) return section;
    const details = document.createElement("details");
    details.className = section.className;
    details.dataset.category = section.dataset.category || "Pozostałe";
    details.dataset.collapsibleEquipmentGroup = "true";
    details.hidden = section.hidden;
    const summary = document.createElement("summary");
    summary.className = "equipment-picker-group-summary";
    summary.innerHTML = '<span class="equipment-picker-group-title"></span><span class="equipment-picker-group-meta" data-equipment-group-meta></span>';
    summary.querySelector(".equipment-picker-group-title").textContent = heading.textContent.trim();
    details.append(summary, options);
    section.replaceWith(details);
    updateSummary(details);
    return details;
  };

  const uniqueSorted = (values) => [...new Set(values.filter(Boolean))]
    .sort((left, right) => left.localeCompare(right, "pl"));

  const selectedValues = (selector) => {
    const select = document.querySelector(selector);
    return select ? [...select.selectedOptions].map((option) => option.value) : [];
  };

  const fillSelect = (selector, values) => {
    const select = document.querySelector(selector);
    if (!select) return;
    select.replaceChildren(...values.map((value) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = value;
      return option;
    }));
  };

  const readCriteria = () => ({
    confirmed_only: Boolean(document.querySelector("#configurator-confirmed-only")?.checked),
    colours: selectedValues("#configurator-selected-colours"),
    wheels: selectedValues("#configurator-selected-wheels"),
    upholsteries: selectedValues("#configurator-selected-upholsteries"),
    standard_equipment: selectedValues("#configurator-standard-equipment"),
  });

  const activeCriteria = (criteria) => criteria.confirmed_only
    || criteria.colours.length > 0
    || criteria.wheels.length > 0
    || criteria.upholsteries.length > 0
    || criteria.standard_equipment.length > 0;

  const observationMatches = (observation, criteria) => {
    if (!activeCriteria(criteria)) return true;
    if (!observation) return false;
    const colour = observation.selected_colour?.value || "";
    const wheels = observation.selected_wheels?.value || "";
    const upholstery = observation.selected_upholstery?.value || "";
    const sourceLines = new Set(observation.standard_equipment_source_lines || []);
    return (!criteria.colours.length || criteria.colours.includes(colour))
      && (!criteria.wheels.length || criteria.wheels.includes(wheels))
      && (!criteria.upholsteries.length || criteria.upholsteries.includes(upholstery))
      && criteria.standard_equipment.every((line) => sourceLines.has(line));
  };

  const restoreCriteria = () => {
    let stored = {};
    try {
      stored = JSON.parse(sessionStorage.getItem(STORAGE_KEY) || "{}");
    } catch (_error) {
      stored = {};
    }
    const checkbox = document.querySelector("#configurator-confirmed-only");
    if (checkbox) checkbox.checked = Boolean(stored.confirmed_only);
    for (const [selector, values] of [
      ["#configurator-selected-colours", stored.colours],
      ["#configurator-selected-wheels", stored.wheels],
      ["#configurator-selected-upholsteries", stored.upholsteries],
      ["#configurator-standard-equipment", stored.standard_equipment],
    ]) {
      const wanted = new Set(Array.isArray(values) ? values : []);
      const select = document.querySelector(selector);
      if (!select) continue;
      for (const option of select.options) option.selected = wanted.has(option.value);
    }
  };

  const persistCriteria = () => {
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(readCriteria()));
    } catch (_error) {
      // The report remains fully usable when storage is unavailable.
    }
  };

  const clearCriteria = () => {
    const checkbox = document.querySelector("#configurator-confirmed-only");
    if (checkbox) checkbox.checked = false;
    for (const selector of [
      "#configurator-selected-colours",
      "#configurator-selected-wheels",
      "#configurator-selected-upholsteries",
      "#configurator-standard-equipment",
    ]) {
      const select = document.querySelector(selector);
      if (!select) continue;
      for (const option of select.options) option.selected = false;
    }
    const search = document.querySelector("#configurator-standard-equipment-search");
    if (search) search.value = "";
    try {
      sessionStorage.removeItem(STORAGE_KEY);
    } catch (_error) {
      // No-op.
    }
  };

  const evidenceMarkup = (observation) => {
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
  };

  const appendEvidence = (card, observation) => {
    if (!observation || card.querySelector(".configurator-observation-evidence")) return;
    card.insertAdjacentHTML("beforeend", evidenceMarkup(observation));
  };

  const setMetric = (selector, value) => {
    const element = document.querySelector(selector);
    if (element) element.textContent = String(value);
  };

  const applyObservationFilters = (detail, notify) => {
    const results = document.querySelector("#results");
    if (!results) return;
    const criteria = readCriteria();
    const cards = [...results.querySelectorAll(".result-card")];
    let visible = 0;
    const visibleCodes = [];
    for (const card of cards) {
      const code = card.dataset.configurationCode || "";
      const observation = observationByConfiguration.get(code);
      appendEvidence(card, observation);
      if (!observationMatches(observation, criteria)) {
        card.remove();
        continue;
      }
      visible += 1;
      visibleCodes.push(code);
    }

    const baseSummary = detail?.outcome?.summary || results.dkbLastDetail?.outcome?.summary || {};
    const baseMatched = Number(baseSummary.matched_configurations ?? cards.length);
    const totalConfigurations = configurationByCode.size;
    setMetric("#matched-count", visible);
    setMetric("#excluded-count", Math.max(0, totalConfigurations - visible));

    const visibleConfigurations = visibleCodes
      .map((code) => configurationByCode.get(code))
      .filter(Boolean);
    setMetric(
      "#missing-price-count",
      visibleConfigurations.filter((item) => item.catalog_price?.state !== "recorded").length
    );
    setMetric(
      "#missing-seats-count",
      visibleConfigurations.filter((item) => item.number_of_seats?.state !== "recorded").length
    );

    if (baseMatched > 0 && visible === 0) {
      results.innerHTML = '<p class="empty">Żadna konfiguracja nie spełnia wszystkich kryteriów, w tym dokładnych filtrów danych producenta.</p>';
    }
    results.dataset.configuratorObservationMatchCount = String(visible);
    if (notify) {
      results.dispatchEvent(new CustomEvent("dkb:results-rendered", {
        detail: {
          ...(detail || results.dkbLastDetail || {}),
          configurator_observation_filtered: true,
          visible_configuration_codes: visibleCodes,
        }
      }));
    }
  };

  const requestBaseRender = () => {
    const trigger = document.querySelector("#minimum-price");
    if (trigger) {
      trigger.dispatchEvent(new Event("input", { bubbles: true }));
    } else {
      applyObservationFilters(null, true);
    }
  };

  const buildObservationPanel = () => {
    const form = document.querySelector("#filters");
    if (!form || !observationByConfiguration.size) return;
    const observations = [...observationByConfiguration.values()];
    const panel = document.createElement("details");
    panel.id = "configurator-observation-filters";
    panel.className = "configurator-observation-filters full";
    panel.innerHTML = `<summary>
        <span>Dane potwierdzone konfiguracją producenta</span>
        <small>${observations.length} dokładnych zapisów</small>
      </summary>
      <div class="configurator-observation-filter-grid">
        <label class="configurator-confirmed-toggle">
          <input id="configurator-confirmed-only" type="checkbox">
          Tylko konfiguracje potwierdzone dokładnym zapisem producenta
        </label>
        <label>Wybrany kolor zapisanej konfiguracji
          <select id="configurator-selected-colours" multiple size="4"></select>
        </label>
        <label>Wybrane koła zapisanej konfiguracji
          <select id="configurator-selected-wheels" multiple size="6"></select>
        </label>
        <label>Wybrana tapicerka zapisanej konfiguracji
          <select id="configurator-selected-upholsteries" multiple size="6"></select>
        </label>
        <label class="configurator-standard-equipment-filter">Dokładne wiersze wyposażenia standardowego
          <input id="configurator-standard-equipment-search" type="search" placeholder="Szukaj w dokładnych wierszach źródłowych">
          <select id="configurator-standard-equipment" multiple size="10"></select>
        </label>
        <p class="configurator-observation-note">Filtry odnoszą się wyłącznie do zapisanych konfiguracji z eksportów producenta. Nie oznaczają dostępności innych kolorów, kół, tapicerek ani elementów wyposażenia.</p>
      </div>`;
    const actions = form.querySelector(".actions");
    if (actions) form.insertBefore(panel, actions);
    else form.append(panel);

    fillSelect(
      "#configurator-selected-colours",
      uniqueSorted(observations.map((item) => item.selected_colour?.value || ""))
    );
    fillSelect(
      "#configurator-selected-wheels",
      uniqueSorted(observations.map((item) => item.selected_wheels?.value || ""))
    );
    fillSelect(
      "#configurator-selected-upholsteries",
      uniqueSorted(observations.map((item) => item.selected_upholstery?.value || ""))
    );
    fillSelect(
      "#configurator-standard-equipment",
      uniqueSorted(observations.flatMap((item) => item.standard_equipment_source_lines || []))
    );
    restoreCriteria();

    for (const control of panel.querySelectorAll("input:not([type=search]), select")) {
      control.addEventListener("change", () => {
        persistCriteria();
        requestBaseRender();
      });
    }
    const search = panel.querySelector("#configurator-standard-equipment-search");
    if (search) {
      search.addEventListener("input", () => {
        const query = search.value.trim().toLocaleLowerCase("pl");
        const select = panel.querySelector("#configurator-standard-equipment");
        for (const option of select.options) {
          option.hidden = Boolean(query) && !option.textContent.toLocaleLowerCase("pl").includes(query);
        }
      });
    }
    const reset = document.querySelector("#reset");
    if (reset) {
      reset.addEventListener("click", clearCriteria, { capture: true });
    }
  };

  const initializeEquipmentGroups = () => {
    const groupsContainer = document.querySelector("[data-equipment-groups]");
    if (!groupsContainer) return;
    for (const section of [...groupsContainer.querySelectorAll(":scope > .equipment-picker-group")]) {
      upgradeGroup(section);
    }
    const syncSummaries = () => {
      for (const group of groupsContainer.querySelectorAll("details[data-collapsible-equipment-group]")) {
        updateSummary(group);
      }
    };
    new MutationObserver(syncSummaries).observe(groupsContainer, {
      subtree: true,
      attributes: true,
      attributeFilter: ["hidden", "class"]
    });
    const search = document.querySelector("[data-equipment-search]");
    if (search) {
      search.addEventListener("input", () => {
        requestAnimationFrame(() => {
          const active = Boolean(search.value.trim());
          for (const group of groupsContainer.querySelectorAll("details[data-collapsible-equipment-group]")) {
            if (active && !group.hidden && visibleChoices(group).length) {
              if (!group.open) group.dataset.openedBySearch = "true";
              group.open = true;
            } else if (!active && group.dataset.openedBySearch === "true") {
              group.open = false;
              delete group.dataset.openedBySearch;
            }
          }
          syncSummaries();
        });
      });
    }
    const form = groupsContainer.closest("form");
    if (form) {
      form.addEventListener("reset", () => requestAnimationFrame(() => {
        for (const group of groupsContainer.querySelectorAll("details[data-collapsible-equipment-group]")) {
          group.open = false;
          delete group.dataset.openedBySearch;
        }
        syncSummaries();
      }));
    }
    syncSummaries();
  };

  const initialize = () => {
    document.documentElement.dataset.equipmentGroupsEnhancement = MARKER;
    initializeEquipmentGroups();
    buildObservationPanel();
    const results = document.querySelector("#results");
    if (results) {
      results.addEventListener("dkb:results-rendered", (event) => {
        if (event.detail?.configurator_observation_filtered) return;
        applyObservationFilters(event.detail, false);
      }, { capture: true });
      applyObservationFilters(results.dkbLastDetail, true);
    }
  };

  const api = {
    activeCriteria,
    observationMatches,
    observation_count: observationByConfiguration.size,
  };
  if (typeof globalThis !== "undefined") {
    globalThis.DkbConfiguratorObservationFilters = api;
  }

  if (typeof document !== "undefined") {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initialize);
    else initialize();
  }
})();
