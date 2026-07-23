(function (root, factory) {
  "use strict";
  const api = factory();
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  root.DkbConfigurationShortlist = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const AVAILABLE = new Set(["standard", "optional"]);

  function unique(values) {
    return [...new Set((values || []).map(String).map((value) => value.trim()).filter(Boolean))].sort();
  }

  function normalizeCriteria(criteria) {
    const standard = unique(criteria && criteria.required_standard_equipment);
    const standardSet = new Set(standard);
    const seatsValue = criteria && criteria.seats;
    const seats = seatsValue === null || seatsValue === undefined || seatsValue === ""
      ? null
      : Number(seatsValue);
    const minimum = criteria && criteria.minimum_price_pln;
    const maximum = criteria && criteria.maximum_price_pln;
    return {
      models: unique(criteria && criteria.models),
      versions: unique(criteria && criteria.versions),
      transmissions: unique(criteria && criteria.transmissions),
      powertrains: unique(criteria && criteria.powertrains),
      minimum_price_pln: minimum === null || minimum === undefined || minimum === "" ? null : Number(minimum),
      maximum_price_pln: maximum === null || maximum === undefined || maximum === "" ? null : Number(maximum),
      seats,
      required_equipment: unique(criteria && criteria.required_equipment).filter((code) => !standardSet.has(code)),
      required_standard_equipment: standard,
      search: String(criteria && criteria.search || "").trim().toLocaleLowerCase("pl")
    };
  }

  function configurationSearchText(configuration) {
    return [
      configuration.configuration_code,
      configuration.display_name,
      configuration.model_code,
      configuration.model_name,
      configuration.version_code,
      configuration.version_name,
      configuration.powertrain_label,
      configuration.transmission_type
    ].join(" ").toLocaleLowerCase("pl");
  }

  function equipmentAvailable(configuration, code) {
    const state = configuration && configuration.equipment && configuration.equipment[code];
    return Boolean(state && AVAILABLE.has(state.availability_status));
  }

  function evaluate(configuration, rawCriteria) {
    const criteria = normalizeCriteria(rawCriteria || {});
    const reasons = new Set();
    if (criteria.models.length && !criteria.models.includes(configuration.model_code)) reasons.add("model");
    if (criteria.versions.length && !criteria.versions.includes(configuration.version_code)) reasons.add("version");
    if (criteria.transmissions.length && !criteria.transmissions.includes(configuration.transmission_type)) reasons.add("transmission");
    if (criteria.powertrains.length && !criteria.powertrains.some((phrase) =>
      configuration.powertrain_label.toLocaleLowerCase("pl").includes(phrase.toLocaleLowerCase("pl")))) {
      reasons.add("powertrain");
    }
    if (criteria.search && !configurationSearchText(configuration).includes(criteria.search)) reasons.add("search");

    const price = configuration.catalog_price;
    const amount = price.state === "recorded" ? Number(price.amount) : null;
    if (criteria.minimum_price_pln !== null) {
      if (amount === null) reasons.add("price_missing");
      else if (amount < criteria.minimum_price_pln) reasons.add("price_below_minimum");
    }
    if (criteria.maximum_price_pln !== null) {
      if (amount === null) reasons.add("price_missing");
      else if (amount > criteria.maximum_price_pln) reasons.add("price_above_maximum");
    }

    const seats = configuration.number_of_seats;
    if (criteria.seats !== null) {
      if (seats.state !== "recorded") reasons.add("number_of_seats_missing");
      else if (Number(seats.value) !== criteria.seats) reasons.add("number_of_seats");
    }

    for (const code of criteria.required_equipment) {
      const state = configuration.equipment[code];
      if (!state) reasons.add(`equipment_missing:${code}`);
      else if (!AVAILABLE.has(state.availability_status)) reasons.add(`equipment_not_available:${code}`);
    }
    for (const code of criteria.required_standard_equipment) {
      const state = configuration.equipment[code];
      if (!state) reasons.add(`equipment_missing:${code}`);
      else if (state.availability_status !== "standard") reasons.add(`equipment_not_standard:${code}`);
    }
    return [...reasons].sort();
  }

  function sortConfigurations(left, right) {
    const leftMissing = left.catalog_price.state !== "recorded";
    const rightMissing = right.catalog_price.state !== "recorded";
    if (leftMissing !== rightMissing) return leftMissing ? 1 : -1;
    if (!leftMissing) {
      const delta = Number(left.catalog_price.amount) - Number(right.catalog_price.amount);
      if (delta) return delta;
    }
    return left.model_code.localeCompare(right.model_code)
      || left.version_code.localeCompare(right.version_code)
      || left.configuration_code.localeCompare(right.configuration_code);
  }

  function filterCatalog(catalog, rawCriteria) {
    const criteria = normalizeCriteria(rawCriteria || {});
    const exclusionReasonCounts = {};
    const requiredEquipmentMissing = {};
    let catalogPriceMissing = 0;
    let numberOfSeatsMissing = 0;
    const results = [];

    for (const configuration of catalog.configurations) {
      if (configuration.catalog_price.state !== "recorded") catalogPriceMissing += 1;
      if (configuration.number_of_seats.state !== "recorded") numberOfSeatsMissing += 1;
      for (const code of [...criteria.required_equipment, ...criteria.required_standard_equipment]) {
        if (!configuration.equipment[code]) {
          requiredEquipmentMissing[code] = (requiredEquipmentMissing[code] || 0) + 1;
        }
      }
      const reasons = evaluate(configuration, criteria);
      for (const reason of reasons) exclusionReasonCounts[reason] = (exclusionReasonCounts[reason] || 0) + 1;
      if (!reasons.length) results.push(configuration);
    }
    results.sort(sortConfigurations);
    return {
      criteria,
      results,
      summary: {
        active_configurations: catalog.configurations.length,
        matched_configurations: results.length,
        excluded_configurations: catalog.configurations.length - results.length,
        exclusion_reason_counts: Object.fromEntries(Object.entries(exclusionReasonCounts).sort()),
        data_unknowns: {
          catalog_price_missing: catalogPriceMissing,
          number_of_seats_missing: numberOfSeatsMissing,
          required_equipment_missing: Object.fromEntries(Object.entries(requiredEquipmentMissing).sort())
        }
      }
    };
  }

  function criteriaWithoutEquipment(rawCriteria) {
    const criteria = normalizeCriteria(rawCriteria || {});
    return { ...criteria, required_equipment: [], required_standard_equipment: [] };
  }

  function availableEquipmentCodes(configurations) {
    const codes = new Set();
    for (const configuration of configurations || []) {
      for (const [code, state] of Object.entries(configuration.equipment || {})) {
        if (state && AVAILABLE.has(state.availability_status)) codes.add(code);
      }
    }
    return [...codes].sort();
  }

  function reconcileEquipmentSelection(catalog, rawCriteria) {
    const criteria = normalizeCriteria(rawCriteria || {});
    const baseCriteria = criteriaWithoutEquipment(criteria);
    const baseResults = catalog.configurations
      .filter((configuration) => evaluate(configuration, baseCriteria).length === 0)
      .sort(sortConfigurations);
    const requested = criteria.required_equipment;

    if (!baseResults.length) {
      return {
        base_match_count: 0,
        selected_equipment: requested,
        removed_equipment: [],
        available_equipment: requested,
        compatible_configurations: []
      };
    }

    const accepted = [];
    const removed = [];
    let compatible = baseResults;
    for (const code of requested) {
      const next = compatible.filter((configuration) => equipmentAvailable(configuration, code));
      if (next.length) {
        accepted.push(code);
        compatible = next;
      } else {
        removed.push(code);
      }
    }

    const available = new Set(availableEquipmentCodes(compatible));
    for (const code of accepted) available.add(code);
    return {
      base_match_count: baseResults.length,
      selected_equipment: accepted,
      removed_equipment: removed,
      available_equipment: [...available].sort(),
      compatible_configurations: compatible
    };
  }

  function selectedValues(element) {
    return element ? [...element.selectedOptions].map((option) => option.value) : [];
  }

  function setSelected(element, values) {
    if (!element) return;
    const wanted = new Set(values || []);
    for (const option of element.options) option.selected = wanted.has(option.value);
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function optionMarkup(items, valueKey, label) {
    return items.map((item) => {
      const value = typeof item === "string" ? item : item[valueKey];
      const text = typeof item === "string" ? item : label(item);
      return `<option value="${escapeHtml(value)}">${escapeHtml(text)}</option>`;
    }).join("");
  }

  function priceText(price) {
    if (price.state !== "recorded") return "Cena: brak danych";
    return `${Number(price.amount).toLocaleString("pl-PL")} ${price.currency_code}`;
  }

  function seatsText(seats) {
    return seats.state === "recorded" ? `${seats.value} miejsc` : "Liczba miejsc: brak danych";
  }

  function renderResults(container, outcome) {
    if (!outcome.results.length) {
      container.innerHTML = '<p class="empty">Żadna konfiguracja nie spełnia wszystkich kryteriów.</p>';
      return;
    }
    container.innerHTML = outcome.results.map((item) => {
      const price = item.catalog_price;
      const seats = item.number_of_seats;
      const priceSource = price.state === "recorded"
        ? `${price.price_date} · ${price.source_code}` : "brak źródłowego rekordu ceny";
      const seatsSource = seats.state === "recorded"
        ? `${seats.observation_date} · ${seats.source_code}` : "brak źródłowego rekordu liczby miejsc";
      return `<article class="result-card">
        <div class="model-thumbnail-host" data-model-code="${escapeHtml(item.model_code)}" data-model-name="${escapeHtml(item.model_name)}"></div>
        <div class="result-price">${escapeHtml(priceText(price))}</div>
        <h3>${escapeHtml(item.display_name || `${item.model_name} ${item.version_name}`)}</h3>
        <p class="configuration-code">${escapeHtml(item.configuration_code)}</p>
        <dl>
          <div><dt>Napęd</dt><dd>${escapeHtml(item.powertrain_label)}</dd></div>
          <div><dt>Skrzynia</dt><dd>${escapeHtml(item.transmission_type)}</dd></div>
          <div><dt>Miejsca</dt><dd>${escapeHtml(seatsText(seats))}</dd></div>
        </dl>
        <details><summary>Proweniencja</summary>
          <p>Cena: ${escapeHtml(priceSource)}</p>
          <p>Miejsca: ${escapeHtml(seatsSource)}</p>
        </details>
      </article>`;
    }).join("");
  }

  function setText(selector, value) {
    const element = document.querySelector(selector);
    if (element) element.textContent = value;
  }

  function renderSummary(outcome) {
    const summary = outcome.summary;
    setText("#matched-count", summary.matched_configurations);
    setText("#excluded-count", summary.excluded_configurations);
    setText("#missing-price-count", summary.data_unknowns.catalog_price_missing);
    setText("#missing-seats-count", summary.data_unknowns.number_of_seats_missing);
  }

  function modelOptionLabel(item) {
    return String(item.name || item.code || "");
  }

  function versionOptionLabel(item) {
    return String(item.name || item.code || "");
  }

  function versionsForModels(versions, modelCodes) {
    const wanted = new Set(modelCodes || []);
    if (!wanted.size) return [];
    return (versions || []).filter((item) => wanted.has(item.model_code));
  }

  function populateVersions(catalog, modelCodes, selectedVersions) {
    const select = document.querySelector("#versions");
    const field = document.querySelector("#versions-field");
    const items = versionsForModels(catalog.facets.versions, modelCodes);
    select.innerHTML = optionMarkup(items, "code", versionOptionLabel);
    select.disabled = items.length === 0;
    if (field) field.hidden = items.length === 0;
    setSelected(select, selectedVersions || []);
  }

  function populateControls(catalog) {
    document.querySelector("#models").innerHTML = optionMarkup(catalog.facets.models, "code", modelOptionLabel);
    populateVersions(catalog, [], []);
    document.querySelector("#transmissions").innerHTML = '<option value="">Dowolna</option>'
      + optionMarkup(catalog.facets.transmissions, "", (item) => item);
    document.querySelector("#powertrains").innerHTML = optionMarkup(catalog.facets.powertrains, "", (item) => item);
    document.querySelector("#seats").innerHTML = '<option value="">Dowolna / także brak danych</option>'
      + optionMarkup(catalog.facets.seat_counts.map(String), "", (item) => `${item} miejsc`);
    document.querySelector("#required-equipment").innerHTML = optionMarkup(
      catalog.facets.equipment, "code", (item) => `${item.name} (${item.code})`
    );
  }

  function criteriaFromControls() {
    const transmission = document.querySelector("#transmissions").value;
    const search = document.querySelector("#search");
    return {
      models: selectedValues(document.querySelector("#models")),
      versions: selectedValues(document.querySelector("#versions")),
      transmissions: transmission ? [transmission] : [],
      powertrains: selectedValues(document.querySelector("#powertrains")),
      minimum_price_pln: document.querySelector("#minimum-price").value,
      maximum_price_pln: document.querySelector("#maximum-price").value,
      seats: document.querySelector("#seats").value,
      required_equipment: selectedValues(document.querySelector("#required-equipment")),
      required_standard_equipment: [],
      search: search ? search.value : ""
    };
  }

  function applyInitialFilters(catalog, filters) {
    const selectedVersions = filters.versions || [];
    const inferredModels = new Set(filters.models || []);
    if (!inferredModels.size && selectedVersions.length) {
      for (const item of catalog.facets.versions) {
        if (selectedVersions.includes(item.code)) inferredModels.add(item.model_code);
      }
    }
    const modelCodes = [...inferredModels];
    setSelected(document.querySelector("#models"), modelCodes);
    populateVersions(catalog, modelCodes, selectedVersions);
    document.querySelector("#transmissions").value = (filters.transmissions || [])[0] || "";
    setSelected(document.querySelector("#powertrains"), filters.powertrains || []);
    document.querySelector("#minimum-price").value = filters.minimum_price_pln || "";
    document.querySelector("#maximum-price").value = filters.maximum_price_pln || "";
    document.querySelector("#seats").value = filters.seats || "";
    setSelected(document.querySelector("#required-equipment"), unique([
      ...(filters.required_equipment || []),
      ...(filters.required_standard_equipment || [])
    ]));
  }

  function initialize() {
    const catalogElement = document.querySelector("#configuration-catalog");
    if (!catalogElement) return;
    const catalog = JSON.parse(catalogElement.textContent);
    populateControls(catalog);
    applyInitialFilters(catalog, catalog.initial_filters || {});
    const results = document.querySelector("#results");
    const equipment = document.querySelector("#required-equipment");

    const update = () => {
      const rawCriteria = criteriaFromControls();
      const facetState = reconcileEquipmentSelection(catalog, rawCriteria);
      if (facetState.removed_equipment.length) {
        setSelected(equipment, facetState.selected_equipment);
        rawCriteria.required_equipment = facetState.selected_equipment;
      }
      const outcome = filterCatalog(catalog, rawCriteria);
      renderSummary(outcome);
      renderResults(results, outcome);
      const detail = { outcome, equipment_availability: facetState };
      results.dkbLastDetail = detail;
      results.dispatchEvent(new CustomEvent("dkb:results-rendered", { detail }));
    };

    const models = document.querySelector("#models");
    models.addEventListener("change", () => {
      const selectedVersions = selectedValues(document.querySelector("#versions"));
      populateVersions(catalog, selectedValues(models), selectedVersions);
      update();
    });
    for (const element of document.querySelectorAll("#filters input, #filters select")) {
      if (element === models) continue;
      element.addEventListener(element.tagName === "SELECT" ? "change" : "input", update);
    }
    document.querySelector("#reset").addEventListener("click", () => {
      const filters = document.querySelector("#filters");
      HTMLFormElement.prototype.reset.call(filters);
      for (const element of document.querySelectorAll("#filters select[multiple]")) setSelected(element, []);
      populateVersions(catalog, [], []);
      update();
    });
    update();
  }

  if (typeof document !== "undefined") {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initialize);
    else initialize();
  }

  return {
    normalizeCriteria,
    evaluate,
    filterCatalog,
    sortConfigurations,
    modelOptionLabel,
    versionOptionLabel,
    versionsForModels,
    equipmentAvailable,
    availableEquipmentCodes,
    reconcileEquipmentSelection,
    criteriaWithoutEquipment
  };
});
