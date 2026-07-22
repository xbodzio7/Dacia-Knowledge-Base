(function (root, factory) {
  "use strict";
  const pricing = root.DkbConfigurationPricingV12
    || (typeof require !== "undefined" ? require("./configuration_shortlist_v12_pricing.js") : null);
  const api = factory(pricing);
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  root.DkbConfigurationShortlistV12 = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function (pricing) {
  "use strict";

  const STATUS_LABELS = Object.freeze({
    standard: "w standardzie", optional: "dostępne opcjonalnie",
    not_available: "niedostępne", unknown: "status nieustalony", missing: "brak danych"
  });
  const CATEGORY_LABELS = Object.freeze({
    ADAS: "Systemy wspomagania kierowcy", Brakes: "Hamulce",
    Doors: "Drzwi i dostęp", "Driving Systems": "Prowadzenie i parkowanie",
    HVAC: "Ogrzewanie i klimatyzacja", Infotainment: "Multimedia",
    Lighting: "Oświetlenie", Mirrors: "Lusterka i parkowanie", Seats: "Fotele"
  });

  function escapeHtml(value) {
    return String(value).replaceAll("&", "&amp;").replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#39;");
  }

  function selectedValues(select) {
    return [...select.selectedOptions].map((option) => option.value);
  }

  function dispatchSelection(select) {
    select.dispatchEvent(new Event("change", { bubbles: true }));
  }

  function equipmentMap(catalog) {
    return new Map((catalog.facets && catalog.facets.equipment || []).map((item) => [item.code, item]));
  }

  function createEquipmentPicker(select, title, catalog) {
    if (!select || document.querySelector(`#${select.id}-picker`)) return null;
    const facets = equipmentMap(catalog);
    const wrapper = document.createElement("div");
    wrapper.id = `${select.id}-picker`;
    wrapper.className = "equipment-picker";
    wrapper.innerHTML = `
      <div class="selected-filter-summary">
        <div class="selected-filter-summary-head">
          <span>${escapeHtml(title)}: <strong data-selected-count>0</strong></span>
          <span class="selected-filter-actions">
            <button type="button" data-show-selected aria-pressed="false">Pokaż tylko wybrane</button>
            <button type="button" data-clear-selected disabled>Wyczyść</button>
          </span>
        </div>
        <div class="selected-filter-list" data-selected-list></div>
      </div>
      <label class="equipment-picker-search">Szukaj wyposażenia
        <input type="search" data-equipment-search placeholder="np. kamera, fotele, nawigacja">
      </label>
      <div class="equipment-picker-scroll" data-equipment-groups></div>`;
    select.classList.add("native-equipment-select");
    select.hidden = true;
    select.parentNode.insertBefore(wrapper, select);

    const groups = new Map();
    for (const option of select.options) {
      const facet = facets.get(option.value) || {};
      const category = facet.category || "Pozostałe";
      const label = pricing.equipmentLabel(option.value, facet.name || option.textContent);
      option.textContent = label;
      option.dataset.displayLabel = label;
      if (!groups.has(category)) groups.set(category, []);
      groups.get(category).push({ code: option.value, label, option });
    }
    const groupsContainer = wrapper.querySelector("[data-equipment-groups]");
    for (const [category, items] of [...groups.entries()].sort((a, b) =>
      (CATEGORY_LABELS[a[0]] || a[0]).localeCompare(CATEGORY_LABELS[b[0]] || b[0], "pl"))) {
      const section = document.createElement("section");
      section.className = "equipment-picker-group";
      section.dataset.category = category;
      section.innerHTML = `<h3>${escapeHtml(CATEGORY_LABELS[category] || category)}</h3><div class="equipment-picker-options"></div>`;
      const options = section.querySelector(".equipment-picker-options");
      for (const item of items.sort((a, b) => a.label.localeCompare(b.label, "pl"))) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "equipment-choice";
        button.dataset.value = item.code;
        button.dataset.searchText = `${item.label} ${item.code} ${CATEGORY_LABELS[category] || category}`.toLocaleLowerCase("pl");
        button.title = item.code;
        button.innerHTML = `<span aria-hidden="true">✓</span>${escapeHtml(item.label)}`;
        options.append(button);
      }
      groupsContainer.append(section);
    }

    let showOnlySelected = false;
    const refresh = () => {
      const selected = new Set(selectedValues(select));
      wrapper.querySelector("[data-selected-count]").textContent = selected.size;
      const clear = wrapper.querySelector("[data-clear-selected]");
      clear.disabled = selected.size === 0;
      const list = wrapper.querySelector("[data-selected-list]");
      list.replaceChildren();
      if (!selected.size) {
        const empty = document.createElement("span");
        empty.className = "selected-filter-empty";
        empty.textContent = "Brak zaznaczonych pozycji";
        list.append(empty);
      } else {
        for (const option of [...select.options].filter((item) => item.selected)) {
          const chip = document.createElement("button");
          chip.type = "button";
          chip.className = "selected-filter-chip";
          chip.dataset.removeValue = option.value;
          chip.innerHTML = `${escapeHtml(option.dataset.displayLabel || option.textContent)} <span aria-hidden="true">×</span>`;
          list.append(chip);
        }
      }
      const query = wrapper.querySelector("[data-equipment-search]").value.trim().toLocaleLowerCase("pl");
      for (const button of wrapper.querySelectorAll(".equipment-choice")) {
        const active = selected.has(button.dataset.value);
        button.classList.toggle("is-selected", active);
        button.setAttribute("aria-pressed", active ? "true" : "false");
        button.hidden = (showOnlySelected && !active) || (query && !button.dataset.searchText.includes(query));
      }
      for (const section of wrapper.querySelectorAll(".equipment-picker-group")) {
        section.hidden = !section.querySelector(".equipment-choice:not([hidden])");
      }
    };

    wrapper.addEventListener("click", (event) => {
      const choice = event.target.closest(".equipment-choice");
      if (choice) {
        const option = [...select.options].find((item) => item.value === choice.dataset.value);
        if (option) option.selected = !option.selected;
        dispatchSelection(select);
        return;
      }
      const remove = event.target.closest("[data-remove-value]");
      if (remove) {
        const option = [...select.options].find((item) => item.value === remove.dataset.removeValue);
        if (option) option.selected = false;
        dispatchSelection(select);
        return;
      }
      if (event.target.closest("[data-clear-selected]")) {
        for (const option of select.options) option.selected = false;
        dispatchSelection(select);
        return;
      }
      const show = event.target.closest("[data-show-selected]");
      if (show) {
        showOnlySelected = !showOnlySelected;
        show.setAttribute("aria-pressed", showOnlySelected ? "true" : "false");
        show.textContent = showOnlySelected ? "Pokaż wszystkie" : "Pokaż tylko wybrane";
        refresh();
      }
    });
    wrapper.querySelector("[data-equipment-search]").addEventListener("input", refresh);
    refresh();
    return { refresh };
  }

  function currentCriteria() {
    const available = document.querySelector("#required-equipment");
    const standard = document.querySelector("#required-standard-equipment");
    return {
      required_equipment: available ? selectedValues(available) : [],
      required_standard_equipment: standard ? selectedValues(standard) : []
    };
  }

  function commercialOffersMarkup(configuration) {
    const components = configuration.price_components || [];
    if (!components.length) return "";
    const rows = components.map((item) => {
      const equipment = (item.equipment_codes || []).map((code) => pricing.equipmentLabel(code)).join(", ");
      const kind = item.kind === "package" ? "pakiet" : "opcja";
      return `<li><div><strong>${escapeHtml(item.name)}</strong><span>${escapeHtml(kind)} · ${escapeHtml(equipment || "bez przypisanego filtra wyposażenia")}</span></div><b>${escapeHtml(pricing.formatMoney(item.amount, item.currency_code))}</b></li>`;
    }).join("");
    return `<details class="commercial-offers"><summary>Dostępne pakiety i opcje (${components.length})</summary><ul>${rows}</ul></details>`;
  }

  function localizeBadges(card, configuration, criteria) {
    const selected = [
      ...criteria.required_equipment.map((code) => ({ code, standardOnly: false })),
      ...criteria.required_standard_equipment.map((code) => ({ code, standardOnly: true }))
    ];
    [...card.querySelectorAll(".equipment-state")].forEach((badge, index) => {
      const item = selected[index];
      if (!item) return;
      const state = (configuration.equipment || {})[item.code];
      const status = state ? state.availability_status : "missing";
      const nextText = `${pricing.equipmentLabel(item.code)}: ${STATUS_LABELS[status] || status}${item.standardOnly ? " (wymagane seryjnie)" : ""}`;
      if (badge.textContent !== nextText) badge.textContent = nextText;
      if (badge.title !== item.code) badge.title = item.code;
    });
  }

  function enhanceCards(catalog, results) {
    const byCode = new Map(catalog.configurations.map((item) => [item.configuration_code, item]));
    const criteria = currentCriteria();
    const signature = JSON.stringify(criteria);
    for (const card of results.querySelectorAll(".result-card")) {
      const code = card.querySelector(".configuration-code")?.textContent.trim();
      const configuration = byCode.get(code);
      if (!configuration) continue;
      const heading = card.querySelector("h3");
      if (heading && heading.dataset.v12Label !== configuration.display_name) {
        heading.textContent = configuration.display_name || `${configuration.model_name} ${configuration.version_name}`;
        heading.dataset.v12Label = configuration.display_name || "";
      }
      const price = card.querySelector(".result-price");
      const priceSignature = `${signature}|${JSON.stringify(configuration.price_components || [])}`;
      if (price && price.dataset.v12Signature !== priceSignature) {
        price.innerHTML = pricing.priceBreakdownMarkup(pricing.buildPriceBreakdown(
          configuration, criteria.required_equipment, criteria.required_standard_equipment
        ));
        price.dataset.v12Signature = priceSignature;
      }
      localizeBadges(card, configuration, criteria);
      let offers = card.querySelector(".commercial-offers");
      if (!offers && configuration.price_components?.length) {
        const provenance = card.querySelector("details");
        const holder = document.createElement("div");
        holder.innerHTML = commercialOffersMarkup(configuration);
        offers = holder.firstElementChild;
        if (provenance) card.insertBefore(offers, provenance); else card.append(offers);
      }
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
    pricing.setEquipmentLabels(catalog.interface_labels?.equipment_pl || {});
    const pickers = [
      createEquipmentPicker(document.querySelector("#required-equipment"), "Wybrane wyposażenie", catalog),
      createEquipmentPicker(document.querySelector("#required-standard-equipment"), "Wymagane w standardzie", catalog)
    ].filter(Boolean);
    let scheduled = false;
    const scheduleFrame = typeof requestAnimationFrame === "function"
      ? requestAnimationFrame
      : (callback) => setTimeout(callback, 0);
    const refresh = () => {
      if (scheduled) return;
      scheduled = true;
      scheduleFrame(() => {
        scheduled = false;
        pickers.forEach((picker) => picker.refresh());
        enhanceCards(catalog, results);
      });
    };
    results.addEventListener("dkb:results-rendered", refresh);
    document.addEventListener("change", (event) => {
      if (event.target.matches("#required-equipment, #required-standard-equipment, .configuration-select")) refresh();
    });
    document.querySelector("#reset")?.addEventListener("click", () => setTimeout(refresh, 0));
    refresh();
  }

  if (typeof document !== "undefined") {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initialize);
    else initialize();
  }

  return {
    initialize, createEquipmentPicker, enhanceCards, commercialOffersMarkup,
    dispatchSelection, localizeBadges
  };
});
