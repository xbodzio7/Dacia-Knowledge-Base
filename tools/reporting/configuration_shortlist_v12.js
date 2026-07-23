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
    ADAS: "Systemy wspomagania kierowcy",
    Acoustics: "Akustyka",
    Brakes: "Hamulce",
    Capacities: "Pojemności",
    Consumption: "Zużycie paliwa i energii",
    Dimensions: "Wymiary",
    Doors: "Drzwi i dostęp",
    Drivetrain: "Układ napędowy",
    "Driving Systems": "Prowadzenie i parkowanie",
    Efficiency: "Efektywność",
    "Electric System": "Instalacja elektryczna",
    Emissions: "Emisje",
    Engine: "Silnik",
    Exterior: "Nadwozie i wygląd zewnętrzny",
    HVAC: "Ogrzewanie, wentylacja i klimatyzacja",
    "Hybrid System": "Układ hybrydowy",
    Infotainment: "Multimedia",
    Lighting: "Widoczność i oświetlenie",
    Mirrors: "Lusterka",
    Performance: "Osiągi",
    Powertrain: "Zespół napędowy",
    Safety: "Bezpieczeństwo",
    Seats: "Fotele i kanapa",
    Steering: "Układ kierowniczy",
    Suspension: "Zawieszenie",
    Towing: "Holowanie",
    Transmission: "Skrzynia biegów",
    Weights: "Masy",
    Wheels: "Koła i opony",
    Windows: "Szyby",
    Comfort: "Komfort i wnętrze",
    Parking: "Parkowanie",
    Pozostałe: "Pozostałe"
  });

  function categoryLabel(category) {
    return CATEGORY_LABELS[category] || String(category || "Pozostałe");
  }

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

  function trimKey(versionName) {
    const value = String(versionName || "").toLocaleLowerCase("pl");
    if (value.includes("extreme")) return "extreme";
    if (value.includes("journey")) return "journey";
    if (value.includes("expression")) return "expression";
    return "essential";
  }

  function vehicleSpec(modelCode) {
    const code = String(modelCode || "").toLowerCase();
    if (code.includes("sandero_stepway")) return {
      key: "stepway", body: "M15 85 L24 66 Q29 49 50 43 L122 40 Q150 41 171 58 L214 67 Q234 71 242 85 L242 96 L15 96 Z",
      window: "M54 48 L119 44 Q141 45 158 58 L171 68 L48 68 Z", wheels: [62, 205], wheelY: 94,
      rails: true, cladding: true, doors: [108, 164]
    };
    if (code.includes("jogger")) return {
      key: "jogger", body: "M10 86 L18 66 Q23 49 44 43 L158 40 Q185 42 202 60 L232 69 Q246 74 250 87 L250 96 L10 96 Z",
      window: "M48 49 L153 45 Q176 47 193 61 L201 69 L42 69 Z", wheels: [58, 211], wheelY: 94,
      rails: true, cladding: true, doors: [93, 145, 195]
    };
    if (code.includes("bigster")) return {
      key: "bigster", body: "M8 87 L17 56 Q22 39 48 35 L169 33 Q198 35 215 58 L244 70 Q255 76 257 88 L257 99 L8 99 Z",
      window: "M53 42 L164 38 Q188 40 204 59 L211 69 L43 69 Z", wheels: [60, 218], wheelY: 97,
      rails: true, cladding: true, doors: [102, 158, 205]
    };
    if (code.includes("duster")) return {
      key: "duster", body: "M12 86 L20 60 Q25 43 47 39 L157 37 Q182 39 199 58 L232 69 Q246 75 248 87 L248 98 L12 98 Z",
      window: "M52 46 L153 42 Q174 44 190 59 L199 69 L44 69 Z", wheels: [61, 208], wheelY: 96,
      rails: true, cladding: true, doors: [105, 158, 201]
    };
    if (code.includes("spring")) return {
      key: "spring", body: "M24 87 L31 66 Q36 52 54 48 L120 45 Q144 46 160 61 L201 70 Q217 75 222 87 L222 95 L24 95 Z",
      window: "M60 53 L116 50 Q136 51 151 63 L160 69 L54 69 Z", wheels: [67, 184], wheelY: 93,
      rails: false, cladding: false, doors: [110, 158]
    };
    return {
      key: "sandero", body: "M18 86 L24 72 Q28 56 47 49 L118 45 Q144 46 164 61 L207 69 Q228 72 236 86 L236 94 L18 94 Z",
      window: "M54 54 L118 50 Q137 51 154 63 L166 70 L47 70 Z", wheels: [63, 197], wheelY: 92,
      rails: false, cladding: false, doors: [109, 161]
    };
  }

  function wheelMarkup(cx, cy, trim) {
    const spokes = trim === "essential" ? "" : [0, 60, 120].map((angle) => {
      const radians = angle * Math.PI / 180;
      const dx = Math.cos(radians) * 8;
      const dy = Math.sin(radians) * 8;
      return `<path class="car-wheel-spoke" d="M${cx - dx} ${cy - dy} L${cx + dx} ${cy + dy}"/>`;
    }).join("");
    return `<g class="car-wheel-group"><circle class="car-wheel" cx="${cx}" cy="${cy}" r="16"/><circle class="car-wheel-ring" cx="${cx}" cy="${cy}" r="10"/>${spokes}<circle class="car-hub" cx="${cx}" cy="${cy}" r="3.2"/></g>`;
  }

  function modelThumbnailSvg(modelCode, modelName, versionName) {
    const trim = trimKey(versionName);
    const spec = vehicleSpec(modelCode);
    const label = escapeHtml([modelName || modelCode || "Dacia", versionName || ""].filter(Boolean).join(" "));
    const doorLines = spec.doors.map((x) => `<path class="car-line" d="M${x} 69 V91"/>`).join("");
    const rails = spec.rails || trim === "extreme"
      ? '<path class="car-rail" d="M53 34 H150 M61 30 V39 M143 29 V38"/>' : "";
    const cladding = spec.cladding
      ? '<path class="car-cladding" d="M18 83 Q46 76 74 83 H184 Q214 76 240 84 L240 96 H18 Z"/>' : "";
    const accent = trim === "extreme"
      ? '<path class="car-accent car-accent-extreme" d="M31 76 H224"/>'
      : trim === "journey"
        ? '<path class="car-accent car-accent-journey" d="M48 71 H211"/>'
        : trim === "expression" ? '<path class="car-accent" d="M48 73 H210"/>' : "";
    const bumper = spec.key === "sandero" || spec.key === "spring" ? "M19 85 H42 M211 84 H235" : "M12 86 H42 M221 86 H246";
    return `<svg class="vehicle-artwork vehicle-artwork-${spec.key} trim-${trim}" viewBox="0 0 265 122" role="img" aria-label="${label}" focusable="false">
      <title>${label}</title>
      ${rails}
      <path class="car-body" d="${spec.body}"/>
      ${cladding}
      <path class="car-window" d="${spec.window}"/>
      <path class="car-window-divider" d="M105 45 V69 M158 45 V69"/>
      ${doorLines}
      <path class="car-line" d="M24 78 H238"/>
      <path class="car-bumper" d="${bumper}"/>
      <path class="car-light car-light-front" d="M226 70 L241 75 L235 80 L222 77 Z"/>
      <path class="car-light car-light-rear" d="M20 67 L31 64 L33 74 L21 76 Z"/>
      ${accent}
      ${wheelMarkup(spec.wheels[0], spec.wheelY, trim)}
      ${wheelMarkup(spec.wheels[1], spec.wheelY, trim)}
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
      button.innerHTML = `<span class="model-choice-thumb">${modelThumbnailSvg(model.code, model.name, "")}</span><strong>${escapeHtml(model.name || option.textContent)}</strong><span class="model-choice-check" aria-hidden="true">✓</span>`;
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
      categoryLabel(a[0]).localeCompare(categoryLabel(b[0]), "pl"))) {
      const section = document.createElement("section");
      section.className = "equipment-picker-group";
      section.dataset.category = category;
      section.innerHTML = `<h3>${escapeHtml(categoryLabel(category))}</h3><div class="equipment-picker-options"></div>`;
      const options = section.querySelector(".equipment-picker-options");
      for (const item of items.sort((a, b) => a.label.localeCompare(b.label, "pl"))) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "equipment-choice";
        button.dataset.value = item.code;
        button.dataset.searchText = `${item.label} ${item.code} ${categoryLabel(category)}`.toLocaleLowerCase("pl");
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
      if (thumbnail && thumbnail.dataset.renderedModel !== `${configuration.model_code}|${configuration.version_name}`) {
        thumbnail.innerHTML = modelThumbnailSvg(configuration.model_code, configuration.model_name, configuration.version_name);
        thumbnail.dataset.renderedModel = `${configuration.model_code}|${configuration.version_name}`;
      }
      const heading = card.querySelector("h3");
      if (heading && heading.dataset.v12Label !== configuration.version_name) {
        heading.textContent = configuration.version_name;
        heading.dataset.v12Label = configuration.version_name || "";
      }
      const modelName = card.querySelector(".result-model-name");
      if (modelName) modelName.textContent = configuration.model_name;
      const variantName = card.querySelector(".result-variant-name");
      if (variantName) {
        const transmission = configuration.transmission_type === "automatic" ? "automatyczna" : configuration.transmission_type === "manual" ? "manualna" : configuration.transmission_type;
        variantName.textContent = `${configuration.powertrain_label} · skrzynia ${transmission}`;
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
    dispatchSelection, currentCriteria, modelThumbnailSvg, vehicleSpec, trimKey, categoryLabel, CATEGORY_LABELS
  };
});
