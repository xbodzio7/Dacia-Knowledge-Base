(function (root, factory) {
  "use strict";
  const api = factory();
  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  }
  root.DkbConfigurationShortlist = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const AVAILABLE = new Set(["standard", "optional"]);

  function unique(values) {
    return [...new Set((values || []).map(String).map((value) => value.trim()).filter(Boolean))].sort();
  }

  function normalizeCriteria(criteria) {
    const standard = unique(criteria.required_standard_equipment);
    const standardSet = new Set(standard);
    const seatsValue = criteria.seats;
    const seats = seatsValue === null || seatsValue === undefined || seatsValue === ""
      ? null
      : Number(seatsValue);
    const minimum = criteria.minimum_price_pln;
    const maximum = criteria.maximum_price_pln;
    return {
      models: unique(criteria.models),
      versions: unique(criteria.versions),
      transmissions: unique(criteria.transmissions),
      powertrains: unique(criteria.powertrains),
      minimum_price_pln: minimum === null || minimum === undefined || minimum === "" ? null : Number(minimum),
      maximum_price_pln: maximum === null || maximum === undefined || maximum === "" ? null : Number(maximum),
      seats,
      required_equipment: unique(criteria.required_equipment).filter((code) => !standardSet.has(code)),
      required_standard_equipment: standard,
      search: String(criteria.search || "").trim().toLocaleLowerCase("pl")
    };
  }

  function configurationSearchText(configuration) {
    return [
      configuration.configuration_code,
      configuration.model_code,
      configuration.model_name,
      configuration.version_code,
      configuration.version_name,
      configuration.powertrain_label,
      configuration.transmission_type
    ].join(" ").toLocaleLowerCase("pl");
  }

  function evaluate(configuration, rawCriteria) {
    const criteria = normalizeCriteria(rawCriteria);
    const reasons = new Set();
    if (criteria.models.length && !criteria.models.includes(configuration.model_code)) {
      reasons.add("model");
    }
    if (criteria.versions.length && !criteria.versions.includes(configuration.version_code)) {
      reasons.add("version");
    }
    if (criteria.transmissions.length && !criteria.transmissions.includes(configuration.transmission_type)) {
      reasons.add("transmission");
    }
    if (criteria.powertrains.length && !criteria.powertrains.some((phrase) =>
      configuration.powertrain_label.toLocaleLowerCase("pl").includes(phrase.toLocaleLowerCase("pl")))) {
      reasons.add("powertrain");
    }
    if (criteria.search && !configurationSearchText(configuration).includes(criteria.search)) {
      reasons.add("search");
    }

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
    const criteria = normalizeCriteria(rawCriteria);
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
      for (const reason of reasons) {
        exclusionReasonCounts[reason] = (exclusionReasonCounts[reason] || 0) + 1;
      }
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

  function selectedValues(element) {
    return [...element.selectedOptions].map((option) => option.value);
  }

  function setSelected(element, values) {
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

  function stateBadge(code, state, standardOnly) {
    const status = state ? state.availability_status : "missing";
    const label = standardOnly ? `${code}: ${status} (wymagane seryjnie)` : `${code}: ${status}`;
    return `<span class="equipment-state equipment-${escapeHtml(status)}">${escapeHtml(label)}</span>`;
  }

  function renderResults(container, outcome) {
    const required = outcome.criteria.required_equipment;
    const standard = outcome.criteria.required_standard_equipment;
    if (!outcome.results.length) {
      container.innerHTML = '<p class="empty">Żadna konfiguracja nie spełnia wszystkich kryteriów.</p>';
      return;
    }
    container.innerHTML = outcome.results.map((item) => {
      const price = item.catalog_price;
      const seats = item.number_of_seats;
      const equipment = [
        ...required.map((code) => stateBadge(code, item.equipment[code], false)),
        ...standard.map((code) => stateBadge(code, item.equipment[code], true))
      ].join("");
      const priceSource = price.state === "recorded"
        ? `${price.price_date} · ${price.source_code}` : "brak źródłowego rekordu ceny";
      const seatsSource = seats.state === "recorded"
        ? `${seats.observation_date} · ${seats.source_code}` : "brak źródłowego rekordu liczby miejsc";
      return `<article class="result-card">
        <div class="result-price">${escapeHtml(priceText(price))}</div>
        <h3>${escapeHtml(item.model_name)} <span>${escapeHtml(item.version_name)}</span></h3>
        <p class="configuration-code">${escapeHtml(item.configuration_code)}</p>
        <dl>
          <div><dt>Napęd</dt><dd>${escapeHtml(item.powertrain_label)}</dd></div>
          <div><dt>Skrzynia</dt><dd>${escapeHtml(item.transmission_type)}</dd></div>
          <div><dt>Miejsca</dt><dd>${escapeHtml(seatsText(seats))}</dd></div>
        </dl>
        ${equipment ? `<div class="equipment-list">${equipment}</div>` : ""}
        <details><summary>Proweniencja</summary>
          <p>Cena: ${escapeHtml(priceSource)}</p>
          <p>Miejsca: ${escapeHtml(seatsSource)}</p>
        </details>
      </article>`;
    }).join("");
  }

  function renderSummary(outcome) {
    const summary = outcome.summary;
    document.querySelector("#matched-count").textContent = summary.matched_configurations;
    document.querySelector("#excluded-count").textContent = summary.excluded_configurations;
    document.querySelector("#missing-price-count").textContent = summary.data_unknowns.catalog_price_missing;
    document.querySelector("#missing-seats-count").textContent = summary.data_unknowns.number_of_seats_missing;
    const missingEquipment = Object.entries(summary.data_unknowns.required_equipment_missing);
    document.querySelector("#missing-equipment").textContent = missingEquipment.length
      ? missingEquipment.map(([code, count]) => `${code}: ${count}`).join(" · ")
      : "Brak wymaganych atrybutów z nieznanym stanem.";
    const reasons = Object.entries(summary.exclusion_reason_counts);
    document.querySelector("#exclusion-reasons").textContent = reasons.length
      ? reasons.map(([reason, count]) => `${reason}: ${count}`).join(" · ")
      : "Brak wykluczeń.";
  }

  function populateControls(catalog) {
    document.querySelector("#models").innerHTML = optionMarkup(catalog.facets.models, "code", (item) => `${item.name} (${item.code})`);
    document.querySelector("#versions").innerHTML = optionMarkup(catalog.facets.versions, "code", (item) => `${item.name} (${item.code})`);
    document.querySelector("#transmissions").innerHTML = optionMarkup(catalog.facets.transmissions, "", (item) => item);
    document.querySelector("#seats").innerHTML = '<option value="">Dowolna / także brak danych</option>'
      + optionMarkup(catalog.facets.seat_counts.map(String), "", (item) => `${item} miejsc`);
    const equipment = optionMarkup(catalog.facets.equipment, "code", (item) => `${item.name} (${item.code})`);
    document.querySelector("#required-equipment").innerHTML = equipment;
    document.querySelector("#required-standard-equipment").innerHTML = equipment;
  }

  function criteriaFromControls() {
    const splitPowertrain = document.querySelector("#powertrains").value
      .split(",").map((value) => value.trim()).filter(Boolean);
    return {
      models: selectedValues(document.querySelector("#models")),
      versions: selectedValues(document.querySelector("#versions")),
      transmissions: selectedValues(document.querySelector("#transmissions")),
      powertrains: splitPowertrain,
      minimum_price_pln: document.querySelector("#minimum-price").value,
      maximum_price_pln: document.querySelector("#maximum-price").value,
      seats: document.querySelector("#seats").value,
      required_equipment: selectedValues(document.querySelector("#required-equipment")),
      required_standard_equipment: selectedValues(document.querySelector("#required-standard-equipment")),
      search: document.querySelector("#search").value
    };
  }

  function applyInitialFilters(filters) {
    setSelected(document.querySelector("#models"), filters.models);
    setSelected(document.querySelector("#versions"), filters.versions);
    setSelected(document.querySelector("#transmissions"), filters.transmissions);
    document.querySelector("#powertrains").value = (filters.powertrains || []).join(", ");
    document.querySelector("#minimum-price").value = filters.minimum_price_pln || "";
    document.querySelector("#maximum-price").value = filters.maximum_price_pln || "";
    document.querySelector("#seats").value = filters.seats || "";
    setSelected(document.querySelector("#required-equipment"), filters.required_equipment);
    setSelected(document.querySelector("#required-standard-equipment"), filters.required_standard_equipment);
  }

  function initialize() {
    const catalogElement = document.querySelector("#configuration-catalog");
    if (!catalogElement) return;
    const catalog = JSON.parse(catalogElement.textContent);
    populateControls(catalog);
    applyInitialFilters(catalog.initial_filters || {});
    const results = document.querySelector("#results");
    const update = () => {
      const outcome = filterCatalog(catalog, criteriaFromControls());
      renderSummary(outcome);
      renderResults(results, outcome);
    };
    for (const element of document.querySelectorAll("#filters input, #filters select")) {
      element.addEventListener("input", update);
      element.addEventListener("change", update);
    }
    document.querySelector("#reset").addEventListener("click", () => {
      document.querySelector("#filters").reset();
      for (const element of document.querySelectorAll("#filters select[multiple]")) {
        setSelected(element, []);
      }
      update();
      document.querySelector("#search").focus();
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
    sortConfigurations
  };
});
