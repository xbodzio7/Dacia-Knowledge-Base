(function (root, factory) {
  "use strict";
  const pricing = root.DkbConfigurationPricingV11
    || (typeof require !== "undefined" ? require("./configuration_shortlist_v11_pricing.js") : null);
  const api = factory(pricing);
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  root.DkbConfigurationShortlistV11 = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function (pricing) {
  "use strict";

  const STATUS_LABELS = Object.freeze({
    standard: "w standardzie",
    optional: "opcjonalne",
    not_available: "niedostępne",
    unknown: "status nieustalony",
    missing: "brak danych"
  });

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function selectedValues(select) {
    return [...select.selectedOptions].map((option) => option.value);
  }

  function localizeEquipmentOptions(catalog) {
    const labels = new Map((catalog.facets && catalog.facets.equipment || []).map((item) => [
      item.code,
      pricing.equipmentLabel(item.code, item.name)
    ]));
    for (const select of [
      document.querySelector("#required-equipment"),
      document.querySelector("#required-standard-equipment")
    ]) {
      if (!select) continue;
      for (const option of select.options) {
        const label = labels.get(option.value) || pricing.equipmentLabel(option.value, option.textContent);
        option.textContent = label;
        option.title = option.value;
        option.dataset.displayLabel = label;
      }
    }
  }

  function renderSelectedSummary(select, summary) {
    const selected = [...select.selectedOptions];
    const count = summary.querySelector("[data-selected-count]");
    const list = summary.querySelector("[data-selected-list]");
    const clear = summary.querySelector("[data-clear-selected]");
    count.textContent = selected.length;
    clear.disabled = selected.length === 0;
    list.replaceChildren();
    if (!selected.length) {
      const empty = document.createElement("span");
      empty.className = "selected-filter-empty";
      empty.textContent = "Brak zaznaczonych pozycji";
      list.append(empty);
      return;
    }
    for (const option of selected) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "selected-filter-chip";
      button.dataset.removeValue = option.value;
      button.title = `Usuń: ${option.dataset.displayLabel || option.textContent}`;
      const close = document.createElement("span");
      close.textContent = "×";
      close.setAttribute("aria-hidden", "true");
      button.append(document.createTextNode(option.dataset.displayLabel || option.textContent), close);
      list.append(button);
    }
  }

  function createSelectedSummary(select, title) {
    if (!select || document.querySelector(`#${select.id}-selected-summary`)) return;
    const summary = document.createElement("div");
    summary.id = `${select.id}-selected-summary`;
    summary.className = "selected-filter-summary";
    summary.innerHTML = `<div class="selected-filter-summary-head"><span>${escapeHtml(title)}: <strong data-selected-count>0</strong></span><button type="button" data-clear-selected disabled>Wyczyść</button></div><div class="selected-filter-list" data-selected-list></div>`;
    select.parentNode.insertBefore(summary, select);
    const refresh = () => renderSelectedSummary(select, summary);
    select.addEventListener("input", refresh);
    select.addEventListener("change", refresh);
    summary.addEventListener("click", (event) => {
      const remove = event.target.closest("[data-remove-value]");
      if (remove) {
        const option = [...select.options].find((item) => item.value === remove.dataset.removeValue);
        if (option) option.selected = false;
        select.dispatchEvent(new Event("change", { bubbles: true }));
        return;
      }
      if (event.target.closest("[data-clear-selected]")) {
        for (const option of select.options) option.selected = false;
        select.dispatchEvent(new Event("change", { bubbles: true }));
      }
    });
    refresh();
  }

  function currentEquipmentCriteria() {
    const optional = document.querySelector("#required-equipment");
    const standard = document.querySelector("#required-standard-equipment");
    return {
      required_equipment: optional ? selectedValues(optional) : [],
      required_standard_equipment: standard ? selectedValues(standard) : []
    };
  }

  function localizeEquipmentBadges(card, configuration, criteria) {
    const codes = [
      ...criteria.required_equipment.map((code) => ({ code, standardOnly: false })),
      ...criteria.required_standard_equipment.map((code) => ({ code, standardOnly: true }))
    ];
    const badges = [...card.querySelectorAll(".equipment-state")];
    badges.forEach((badge, index) => {
      const item = codes[index];
      if (!item) return;
      const state = (configuration.equipment || {})[item.code];
      const status = state ? state.availability_status : "missing";
      const suffix = item.standardOnly ? " (wymagane seryjnie)" : "";
      const text = `${pricing.equipmentLabel(item.code)}: ${STATUS_LABELS[status] || status}${suffix}`;
      if (badge.textContent !== text) badge.textContent = text;
      badge.title = item.code;
    });
  }

  function enhanceCards(catalog, results) {
    const byCode = new Map(catalog.configurations.map((item) => [item.configuration_code, item]));
    const criteria = currentEquipmentCriteria();
    const signature = JSON.stringify(criteria);
    for (const card of results.querySelectorAll(".result-card")) {
      const codeElement = card.querySelector(".configuration-code");
      if (!codeElement) continue;
      const configuration = byCode.get(codeElement.textContent.trim());
      if (!configuration) continue;
      const price = card.querySelector(".result-price");
      const priceSignature = `${signature}|${JSON.stringify(configuration.price_components || [])}`;
      if (price && price.dataset.v11Signature !== priceSignature) {
        price.innerHTML = pricing.priceBreakdownMarkup(pricing.buildPriceBreakdown(
          configuration,
          criteria.required_equipment,
          criteria.required_standard_equipment
        ));
        price.dataset.v11Signature = priceSignature;
      }
      localizeEquipmentBadges(card, configuration, criteria);
      const toggle = card.querySelector(".configuration-select");
      const selected = Boolean(toggle && toggle.checked);
      card.classList.toggle("is-selected", selected);
      card.setAttribute("aria-selected", selected ? "true" : "false");
    }
  }

  function initialize() {
    const catalogElement = document.querySelector("#configuration-catalog");
    const results = document.querySelector("#results");
    if (!catalogElement || !results || !pricing) return;
    const catalog = JSON.parse(catalogElement.textContent);
    pricing.setEquipmentLabels(
      catalog.interface_labels && catalog.interface_labels.equipment_pl || {}
    );
    localizeEquipmentOptions(catalog);
    createSelectedSummary(document.querySelector("#required-equipment"), "Wybrane wyposażenie");
    createSelectedSummary(
      document.querySelector("#required-standard-equipment"),
      "Wybrane wyposażenie wymagane seryjnie"
    );

    let scheduled = false;
    const refresh = () => {
      if (scheduled) return;
      scheduled = true;
      queueMicrotask(() => {
        scheduled = false;
        enhanceCards(catalog, results);
      });
    };
    new MutationObserver(refresh).observe(results, { childList: true, subtree: true });
    document.addEventListener("change", (event) => {
      if (event.target.matches("#required-equipment, #required-standard-equipment, .configuration-select")) refresh();
    });
    document.addEventListener("input", (event) => {
      if (event.target.matches("#required-equipment, #required-standard-equipment")) refresh();
    });
    const reset = document.querySelector("#reset");
    if (reset) reset.addEventListener("click", () => setTimeout(refresh, 0));
    refresh();
  }

  if (typeof document !== "undefined") {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initialize);
    else initialize();
  }

  return { initialize, enhanceCards };
});
