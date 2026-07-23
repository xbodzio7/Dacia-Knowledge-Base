(function (root, factory) {
  "use strict";
  const pricing = root.DkbConfigurationPricingV12
    || (typeof require !== "undefined" ? require("./configuration_shortlist_v12_pricing.js") : null);
  const api = factory(pricing);
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  root.DkbConfigurationShortlistV12 = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function (pricing) {
  "use strict";

  const CATEGORY_LABELS = Object.freeze({
    ADAS: "Systemy wspomagania kierowcy", Brakes: "Hamulce",
    Doors: "Drzwi i dostęp", "Driving Systems": "Prowadzenie i parkowanie",
    HVAC: "Ogrzewanie i klimatyzacja", Infotainment: "Multimedia",
    Lighting: "Oświetlenie", Mirrors: "Lusterka i parkowanie", Seats: "Fotele",
    Wheels: "Koła", Windows: "Szyby"
  });

  function escapeHtml(value) {
    return String(value).replaceAll("&", "&amp;").replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#39;");
  }

  function selectedValues(select) {
    return select ? [...select.selectedOptions].map((option) => option.value) : [];
  }

  function dispatchSelection(select) {
    select.dispatchEvent(new Event("change", { bubbles: true }));
  }

  function equipmentMap(catalog) {
    return new Map((catalog.facets && catalog.facets.equipment || []).map((item) => [item.code, item]));
  }

  function bodyProfile(modelCode) {
    const code = String(modelCode || "").toLowerCase();
    if (code.includes("jogger")) return "M12 60 L22 38 Q25 31 36 29 L69 28 Q78 29 84 38 L95 45 Q99 47 100 55 L100 60 Z";
    if (code.includes("bigster")) return "M10 60 L17 37 Q20 29 31 27 L72 26 Q82 27 88 38 L101 45 Q105 48 105 60 Z";
    if (code.includes("duster") || code.includes("stepway")) return "M12 60 L20 39 Q23 31 34 29 L70 29 Q79 30 85 40 L98 47 Q102 50 102 60 Z";
    if (code.includes("sandero") || code.includes("spring")) return "M14 60 L23 42 Q27 34 38 32 L67 32 Q77 34 84 43 L96 49 Q99 52 99 60 Z";
    return "M13 60 L22 40 Q26 32 37 30 L70 30 Q79 32 85 41 L98 48 Q101 51 101 60 Z";
  }

  function modelThumbnailSvg(modelCode, modelName) {
    const label = escapeHtml(modelName || modelCode || "Dacia");
    const profile = bodyProfile(modelCode);
    return `<svg viewBox="0 0 116 76" role="img" aria-label="${label}" focusable="false">
      <title>${label}</title>
      <path class="car-body" d="${profile}"/>
      <path class="car-window" d="M33 34 L42 30 L67 30 L77 39 L34 39 Z"/>
      <path class="car-line" d="M19 50 H99 M56 31 V59"/>
      <circle class="car-wheel" cx="32" cy="60" r="9"/><circle class="car-wheel" cx="84" cy="60" r="9"/>
      <circle class="car-hub" cx="32" cy="60" r="3"/><circle class="car-hub" cx="84" cy="60" r="3"/>
    </svg>`;
  }

  function createModelPicker(select, catalog) {
    if (!select || document.querySelector(`#${select.id}-picker`)) return null;
    const wrapper = document.createElement("div");
    wrapper.id = `${select.id}-picker`;
    wrapper.className = "model-picker";
    const models = new Map((catalog.facets.models || []).map((item) => [item.code, item]));
    for (const option of select.options) {
      const model = models.get(option.value) || { code: option.value, name: option.textContent };
      const button = document.createElement("button");
      button.type = "button";
      button.className = "model-choice";
      button.dataset.value = option.value;
      button.innerHTML = `<span class="model-choice-thumb">${modelThumbnailSvg(model.code, model.name)}</span><strong>${escapeHtml(model.name || option.textContent)}</strong><span class="model-choice-check" aria-hidden="true">✓</span>`;
      wrapper.append(button);
    }
    select.classList.add("native-model-select");
    select.hidden = true;
    select.parentNode.insertBefore(wrapper, select);

    const refresh = () => {
      const selected = new Set(selectedValues(select));
      for (const button of wrapper.querySelectorAll(".model-choice")) {
        const active = selected.has(button.dataset.value);
        button.classList.toggle("is-selected", active);
        button.setAttribute("aria-pressed", active ? "true" : "false");
      }
    };
    wrapper.addEventListener("click", (event) => {
      const button = event.target.closest(".model-choice");
      if (!button) return;
      const option = [...select.options].find((item) => item.value === button.dataset.value);
      if (option) option.selected = !option.selected;
      dispatchSelection(select);
    });
    select.addEventListener("change", refresh);
    refresh();
    return { refresh };
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
      <p class="equipment-availability-note" data-availability-note>Lista pokazuje tylko wyposażenie możliwe w aktualnie dopasowanych wariantach.</p>
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
      groups.get(category).push({ code: option.value, label });
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
    let availableCodes = null;
    let removedCodes = [];
    const refresh = () => {
      const selected = new Set(selectedValues(select));
      wrapper.querySelector("[data-selected-count]").textContent = selected.size;
      wrapper.querySelector("[data-clear-selected]").disabled = selected.size === 0;
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

      const note = wrapper.querySelector("[data-availability-note]");
      note.textContent = removedCodes.length
        ? `Usunięto ${removedCodes.length} pozycję/pozycje, których nie ma w aktualnych wariantach.`
        : "Lista pokazuje tylko wyposażenie możliwe w aktualnie dopasowanych wariantach.";
      note.classList.toggle("has-removal", removedCodes.length > 0);

      const query = wrapper.querySelector("[data-equipment-search]").value.trim().toLocaleLowerCase("pl");
      for (const button of wrapper.querySelectorAll(".equipment-choice")) {
        const active = selected.has(button.dataset.value);
        const available = availableCodes === null || availableCodes.has(button.dataset.value);
        button.classList.toggle("is-selected", active);
        button.setAttribute("aria-pressed", active ? "true" : "false");
        button.hidden = (!active && !available)
          || (showOnlySelected && !active)
          || Boolean(query && !button.dataset.searchText.includes(query));
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
    return {
      refresh,
      setAvailability(state) {
        const available = state && state.available_equipment;
        availableCodes = Array.isArray(available) ? new Set(available) : null;
        removedCodes = state && Array.isArray(state.removed_equipment) ? state.removed_equipment : [];
        refresh();
      }
    };
  }

  function currentCriteria() {
    const equipment = document.querySelector("#required-equipment");
    return { required_equipment: equipment ? selectedValues(equipment) : [], required_standard_equipment: [] };
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

  function enhanceCards(catalog, results) {
    const byCode = new Map(catalog.configurations.map((item) => [item.configuration_code, item]));
    const criteria = currentCriteria();
    const signature = JSON.stringify(criteria);
    for (const card of results.querySelectorAll(".result-card")) {
      const code = card.querySelector(".configuration-code")?.textContent.trim();
      const configuration = byCode.get(code);
      if (!configuration) continue;
      const thumbnail = card.querySelector(".model-thumbnail-host");
      if (thumbnail && thumbnail.dataset.renderedModel !== configuration.model_code) {
        thumbnail.innerHTML = modelThumbnailSvg(configuration.model_code, configuration.model_name);
        thumbnail.dataset.renderedModel = configuration.model_code;
      }
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
    const modelPicker = createModelPicker(document.querySelector("#models"), catalog);
    const equipmentPicker = createEquipmentPicker(
      document.querySelector("#required-equipment"), "Wybrane wyposażenie", catalog
    );
    let scheduled = false;
    let pendingAvailability = results.dkbLastDetail?.equipment_availability || null;
    const scheduleFrame = typeof requestAnimationFrame === "function"
      ? requestAnimationFrame
      : (callback) => setTimeout(callback, 0);
    const refresh = () => {
      if (scheduled) return;
      scheduled = true;
      scheduleFrame(() => {
        scheduled = false;
        if (equipmentPicker) equipmentPicker.setAvailability(pendingAvailability);
        if (modelPicker) modelPicker.refresh();
        enhanceCards(catalog, results);
      });
    };
    results.addEventListener("dkb:results-rendered", (event) => {
      pendingAvailability = event.detail && event.detail.equipment_availability || null;
      refresh();
    });
    document.addEventListener("change", (event) => {
      if (event.target.matches("#required-equipment, #models, .configuration-select")) refresh();
    });
    document.querySelector("#reset")?.addEventListener("click", () => setTimeout(refresh, 0));
    refresh();
  }

  if (typeof document !== "undefined") {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initialize);
    else initialize();
  }

  return {
    initialize, createEquipmentPicker, createModelPicker, enhanceCards, commercialOffersMarkup,
    dispatchSelection, currentCriteria, modelThumbnailSvg, bodyProfile
  };
});
