(function (root, factory) {
  "use strict";
  const api = factory();
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  root.DkbConfigurationPricingV12 = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  let equipmentLabels = Object.freeze({});
  const commercialSelections = new Map();
  const summaryCatalogSnapshot = (() => {
    if (typeof document === "undefined") return { configurations: [] };
    const element = document.querySelector("#configuration-catalog");
    if (!element) return { configurations: [] };
    try {
      const payload = JSON.parse(element.textContent);
      return payload && typeof payload === "object" ? payload : { configurations: [] };
    } catch (_error) {
      return { configurations: [] };
    }
  })();
  const summaryConfigurationByCode = new Map(
    (summaryCatalogSnapshot.configurations || []).map((item) => [item.configuration_code, item])
  );
  const summaryObservationByCode = new Map();
  for (const configuration of summaryCatalogSnapshot.configurations || []) {
    const observations = (configuration.price_components || []).filter(
      (component) => component && component.kind === "configurator_observation"
    );
    if (observations.length === 1) {
      summaryObservationByCode.set(configuration.configuration_code, observations[0]);
    }
  }

  function setEquipmentLabels(labels) {
    equipmentLabels = Object.freeze({ ...(labels || {}) });
  }

  function unique(values) {
    return [...new Set((values || [])
      .filter((value) => value !== null && value !== undefined)
      .map(String).map((value) => value.trim()).filter(Boolean))];
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;").replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;").replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function equipmentLabel(code, fallback) {
    return equipmentLabels[code] || String(fallback || code);
  }

  function formatMoney(amount, currencyCode) {
    const number = Number(amount);
    if (!Number.isFinite(number)) return "brak danych";
    return new Intl.NumberFormat("pl-PL", {
      style: "currency", currency: currencyCode || "PLN",
      minimumFractionDigits: Number.isInteger(number) ? 0 : 2,
      maximumFractionDigits: 2
    }).format(number).replaceAll("\u00a0", " ");
  }

  function normalizeComponent(component, defaultCurrency) {
    const rawAmount = component.amount;
    const numeric = rawAmount === null || rawAmount === undefined || rawAmount === ""
      ? null : Number(rawAmount);
    const kind = String(component.kind || "option");
    return {
      code: String(component.code || ""),
      name: String(component.name || component.code || "Dopłata"),
      kind,
      availability_status: String(component.availability_status || ""),
      amount: Number.isFinite(numeric) ? numeric : null,
      currency_code: String(component.currency_code || defaultCurrency || "PLN"),
      price_date: String(component.price_date || ""),
      source_code: String(component.source_code || ""),
      equipment_codes: unique(component.equipment_codes || []),
      selected_state_observed: Boolean(component.selected_state_observed),
      selected_state_observation_date: String(component.selected_state_observation_date || ""),
      selected_state_source_code: String(component.selected_state_source_code || ""),
      review_state: String(component.review_state || ""),
      review_reason_code: String(component.review_reason_code || ""),
      reviewed_on: String(component.reviewed_on || ""),
      candidate_amount_pln: component.candidate_amount_pln === null
        || component.candidate_amount_pln === undefined
        || component.candidate_amount_pln === ""
        ? null
        : (Number.isFinite(Number(component.candidate_amount_pln))
          ? Number(component.candidate_amount_pln) : null),
      candidate_source_code: String(component.candidate_source_code || "")
    };
  }

  function compareSelections(left, right) {
    if (left.complete !== right.complete) return left.complete ? -1 : 1;
    if (left.coveredCount !== right.coveredCount) return right.coveredCount - left.coveredCount;
    if (left.unknownCount !== right.unknownCount) return left.unknownCount - right.unknownCount;
    if (left.total !== right.total) return left.total - right.total;
    if (left.components.length !== right.components.length) return left.components.length - right.components.length;
    return left.components.map((item) => item.code).join("|")
      .localeCompare(right.components.map((item) => item.code).join("|"));
  }

  function chooseComponents(components, requiredCodes) {
    const required = unique(requiredCodes);
    if (!required.length) return [];
    const requiredIndex = new Map(required.map((code, index) => [code, index]));
    const fullMask = (1n << BigInt(required.length)) - 1n;
    const candidates = components.map((component) => {
      let coverageMask = 0n;
      for (const code of component.equipment_codes) {
        const index = requiredIndex.get(code);
        if (index !== undefined) coverageMask |= 1n << BigInt(index);
      }
      return { component, coverageMask };
    }).filter((item) => item.coverageMask !== 0n);

    const empty = {
      components: [], total: 0, unknownCount: 0,
      coveredCount: 0, complete: false
    };
    let states = new Map([[0n, empty]]);
    for (const { component, coverageMask } of candidates) {
      const next = new Map(states);
      for (const [mask, state] of states) {
        const combinedMask = mask | coverageMask;
        const current = {
          components: [...state.components, component],
          total: state.total + (component.amount === null ? 0 : component.amount),
          unknownCount: state.unknownCount + (component.amount === null ? 1 : 0),
          coveredCount: combinedMask.toString(2).replaceAll("0", "").length,
          complete: combinedMask === fullMask
        };
        const previous = next.get(combinedMask);
        if (!previous || compareSelections(current, previous) < 0) {
          next.set(combinedMask, current);
        }
      }
      states = next;
    }

    let best = null;
    for (const [mask, state] of states) {
      if (mask === 0n) continue;
      if (best === null || compareSelections(state, best) < 0) best = state;
    }
    return best ? best.components : [];
  }

  function buildPriceBreakdown(configuration, requiredEquipment, requiredStandardEquipment) {
    const price = configuration.catalog_price || {};
    const baseAmount = price.state === "recorded" && Number.isFinite(Number(price.amount))
      ? Number(price.amount) : null;
    const currencyCode = String(price.currency_code || "PLN");
    const allComponents = (configuration.price_components || [])
      .map((component) => normalizeComponent(component, currencyCode));
    const selectedCodes = unique([...(requiredEquipment || []), ...(requiredStandardEquipment || [])]);
    const optionalCodes = [];
    const includedStandard = [];
    for (const code of selectedCodes) {
      const state = (configuration.equipment || {})[code];
      if (state && state.availability_status === "standard") {
        includedStandard.push({ code, name: equipmentLabel(code) });
      } else if (state && state.availability_status === "optional") {
        optionalCodes.push(code);
      }
    }
    const chosen = chooseComponents(allComponents, optionalCodes);
    const covered = new Set(chosen.flatMap((component) => component.equipment_codes));
    const knownComponents = chosen.filter((component) => component.amount !== null);
    const unknownComponents = chosen.filter((component) => component.amount === null);
    for (const code of optionalCodes) {
      if (!covered.has(code)) {
        unknownComponents.push({
          code: `unpriced:${code}`, name: equipmentLabel(code), kind: "option",
          amount: null, currency_code: currencyCode, price_date: "", source_code: "",
          equipment_codes: [code]
        });
      }
    }
    const selectedEquipment = selectedCodes.map((code) => {
      const state = (configuration.equipment || {})[code];
      const status = state ? state.availability_status : "missing";
      const coveringComponents = chosen.filter((component) =>
        component.equipment_codes.includes(code)
      );
      return {
        code,
        name: equipmentLabel(code),
        availability_status: status,
        components: coveringComponents.map((component) => ({
          code: component.code,
          name: component.name,
          kind: component.kind,
          amount: component.amount,
          review_state: component.review_state,
          review_reason_code: component.review_reason_code,
          reviewed_on: component.reviewed_on,
          candidate_amount_pln: component.candidate_amount_pln,
          candidate_source_code: component.candidate_source_code,
          source_code: component.source_code
        }))
      };
    });
    const knownSurcharge = knownComponents.reduce((sum, item) => sum + item.amount, 0);
    const totalAmount = baseAmount === null ? null : baseAmount + knownSurcharge;
    return {
      currency_code: currencyCode,
      standard_amount: baseAmount,
      known_components: knownComponents,
      unknown_components: unknownComponents,
      included_standard: includedStandard,
      selected_equipment: selectedEquipment,
      known_surcharge: knownSurcharge,
      total_amount: totalAmount,
      total_is_complete: totalAmount !== null && unknownComponents.length === 0
    };
  }

  function reviewedUnknownPriceStatus(component) {
    const state = String(component && component.review_state || "");
    const reason = String(component && component.review_reason_code || "");
    const rawCandidate = component && component.candidate_amount_pln;
    const candidate = rawCandidate === null || rawCandidate === undefined || rawCandidate === ""
      ? null : Number(rawCandidate);
    const hasCandidate = candidate !== null && Number.isFinite(candidate);
    const candidateText = hasCandidate ? formatMoney(candidate, component.currency_code || "PLN") : "";
    if (state === "source-conflict") {
      return "sprzeczne dane źródłowe — cena nie została doliczona";
    }
    if (state === "context-unmodeled") {
      if (reason === "stock-selection-and-standalone-price-are-separate-record-contexts") {
        return hasCandidate
          ? `wybrane w egzemplarzu; odrębna cena cennikowa ${candidateText} — nie doliczono`
          : "wybrane w egzemplarzu; odrębna cena nie została doliczona";
      }
      if (reason === "model-year-and-paint-price-class-not-modeled") {
        return hasCandidate
          ? `cena ${candidateText} dotyczy innego rocznika lub klasy lakieru — nie doliczono`
          : "cena zależy od rocznika lub klasy lakieru — nie doliczono";
      }
      if (reason === "model-year-stock-context-not-modeled") {
        return hasCandidate
          ? `cena ${candidateText} dotyczy zapasu MY25 — nie doliczono`
          : "cena dotyczy nieodwzorowanego zapasu modelowego — nie doliczono";
      }
      return "cena zależy od nieodwzorowanego kontekstu — nie doliczono";
    }
    if (state === "source-not-stated") return "cena niepodana w dokładnym źródle";
    return component && component.source_code
      ? "cena niepodana w źródle"
      : "brak powiązania z cennikiem";
  }

  function selectedEquipmentStatus(item) {
    if (item.availability_status === "standard") return "w standardzie — bez dopłaty";
    if (item.availability_status === "optional" && item.components.length) {
      const labels = item.components.map((component) => {
        const kind = component.kind === "package" ? "pakiet" : "opcja";
        const price = component.amount === null
          ? reviewedUnknownPriceStatus(component)
          : "dopłata ujęta powyżej";
        return `${kind}: ${component.name} (${price})`;
      });
      return labels.join("; ");
    }
    if (item.availability_status === "optional") return "opcjonalne — brak powiązania z cennikiem";
    if (item.availability_status === "not_available") return "niedostępne";
    if (item.availability_status === "unknown") return "status nieustalony";
    return "brak danych";
  }

  function selectedEquipmentMarkup(items) {
    if (!items.length) return "";
    const rows = items.map((item) =>
      `<li><span>${escapeHtml(item.name)}</span><strong>${escapeHtml(selectedEquipmentStatus(item))}</strong></li>`
    ).join("");
    return `<div class="configuration-price-equipment"><span>Wybrane wyposażenie</span><ul>${rows}</ul></div>`;
  }

  function priceBreakdownMarkup(breakdown) {
    const headline = breakdown.standard_amount === null
      ? "brak danych"
      : (breakdown.total_is_complete
        ? formatMoney(breakdown.total_amount, breakdown.currency_code)
        : `od ${formatMoney(breakdown.total_amount, breakdown.currency_code)}`);
    const rows = [
      ...breakdown.known_components.map((component) =>
        `<li><span>${escapeHtml(component.name)}</span><strong>+ ${escapeHtml(formatMoney(component.amount, component.currency_code))}</strong></li>`),
      ...breakdown.unknown_components.map((component) => {
        const status = reviewedUnknownPriceStatus(component);
        return `<li class="price-component-unknown"><span>${escapeHtml(component.name)}</span><strong>${escapeHtml(status)}</strong></li>`;
      })
    ].join("");
    const components = rows ? `<ul class="configuration-price-components">${rows}</ul>` : "";
    const warning = breakdown.unknown_components.length
      ? '<p class="configuration-price-warning">Niepełne dopłaty nie zostały doliczone do ceny.</p>' : "";
    const standard = breakdown.standard_amount === null
      ? ""
      : `<div class="configuration-price-standard">Cena standardowa: <strong>${escapeHtml(formatMoney(breakdown.standard_amount, breakdown.currency_code))}</strong></div>`;
    return `<div class="configuration-price-main"><span>Cena konfiguracji</span><strong>${escapeHtml(headline)}</strong></div>
      ${standard}${components}${warning}${selectedEquipmentMarkup(breakdown.selected_equipment || [])}`;
  }

  function commercialChoiceItems(configuration) {
    const currencyCode = String(configuration.catalog_price?.currency_code || "PLN");
    return (configuration.price_components || [])
      .map((component) => normalizeComponent(component, currencyCode))
      .filter((component) =>
        (component.kind === "package" || component.kind === "option")
        && component.availability_status === "optional"
      )
      .sort((left, right) => left.name.localeCompare(right.name, "pl") || left.code.localeCompare(right.code));
  }

  function buildCommercialSelectionPreview(configuration, selectedCodes) {
    const price = configuration.catalog_price || {};
    const baseAmount = price.state === "recorded" && Number.isFinite(Number(price.amount))
      ? Number(price.amount) : null;
    const currencyCode = String(price.currency_code || "PLN");
    const selected = new Set(unique(selectedCodes));
    const selectedItems = commercialChoiceItems(configuration)
      .filter((component) => selected.has(component.code));
    const knownItems = selectedItems.filter((component) => component.amount !== null);
    const unknownItems = selectedItems.filter((component) => component.amount === null);
    const knownSurcharge = knownItems.reduce((sum, component) => sum + component.amount, 0);
    const totalAmount = baseAmount === null ? null : baseAmount + knownSurcharge;
    return {
      currency_code: currencyCode,
      base_amount: baseAmount,
      selected_items: selectedItems,
      known_items: knownItems,
      unknown_items: unknownItems,
      known_surcharge: knownSurcharge,
      total_amount: totalAmount,
      total_is_complete: totalAmount !== null && unknownItems.length === 0,
      multi_choice_compatibility_unverified: selectedItems.length > 1,
      compatibility_inference_performed: false
    };
  }

  function commercialChoiceMarkup(configuration, selectedCodes) {
    const choices = commercialChoiceItems(configuration);
    if (!choices.length) return "";
    const selected = new Set(unique(selectedCodes));
    const preview = buildCommercialSelectionPreview(configuration, [...selected]);
    const rows = choices.map((component) => {
      const checked = selected.has(component.code) ? " checked" : "";
      const kind = component.kind === "package" ? "pakiet" : "opcja";
      const equipment = component.equipment_codes.map((code) => equipmentLabel(code)).join(", ");
      const observed = component.selected_state_observed
        ? " · zaobserwowano jako wybrane w zapisanej konfiguracji" : "";
      const price = component.amount === null
        ? "cena niepotwierdzona"
        : formatMoney(component.amount, component.currency_code);
      return `<li><label><input type="checkbox" data-commercial-choice="${escapeHtml(component.code)}"${checked}> <strong>${escapeHtml(component.name)}</strong><span>${escapeHtml(kind)}${escapeHtml(observed)}${equipment ? ` · ${escapeHtml(equipment)}` : ""}</span></label><b>${escapeHtml(price)}</b></li>`;
    }).join("");
    const total = preview.total_amount === null
      ? "brak ceny bazowej"
      : `${preview.total_is_complete ? "" : "od "}${formatMoney(preview.total_amount, preview.currency_code)}`;
    const unknownWarning = preview.unknown_items.length
      ? '<p class="configuration-price-warning">Co najmniej jedna zaznaczona pozycja nie ma potwierdzonej ceny i nie została doliczona.</p>'
      : "";
    const compatibilityWarning = preview.multi_choice_compatibility_unverified
      ? '<p class="configuration-price-warning">Suma wielu pozycji jest wyłącznie arytmetycznym podglądem. Źródła nie potwierdzają ich wzajemnej kompatybilności ani możliwości jednoczesnego zamówienia.</p>'
      : "";
    return `<summary>Pakiety i opcje (${choices.length})</summary><ul>${rows}</ul><p><strong>Podgląd ceny po wyborze:</strong> ${escapeHtml(total)}</p>${unknownWarning}${compatibilityWarning}<p class="commercial-choice-source-note">Wybór dotyczy wyłącznie ofert przypisanych w bazie do tej dokładnej konfiguracji. System nie wnioskuje zależności ani konfliktów między opcjami.</p>`;
  }

  function transmissionSummaryLabel(value) {
    if (value === "automatic") return "automatyczna";
    if (value === "manual") return "manualna";
    return String(value || "brak danych");
  }

  function observationValue(observation, key) {
    const value = observation && observation[key] && observation[key].value;
    return value ? String(value) : "brak w dokładnym zapisie";
  }

  function configuratorSummaryMarkup(configuration, observation, selectedCodes) {
    const preview = buildCommercialSelectionPreview(configuration, selectedCodes);
    const total = preview.total_amount === null
      ? "brak potwierdzonej ceny bazowej"
      : `${preview.total_is_complete ? "" : "od "}${formatMoney(preview.total_amount, preview.currency_code)}`;
    const selectedRows = preview.selected_items.length
      ? preview.selected_items.map((component) => {
        const price = component.amount === null
          ? "cena niepotwierdzona"
          : `+ ${formatMoney(component.amount, component.currency_code)}`;
        return `<li><span>${escapeHtml(component.name)}</span><strong>${escapeHtml(price)}</strong></li>`;
      }).join("")
      : '<li><span>Brak dodatkowych pakietów lub opcji zaznaczonych w kroku 7.</span></li>';
    const appearance = observation
      ? `<p><strong>Kolor:</strong> ${escapeHtml(observationValue(observation, "selected_colour"))}</p>
        <p><strong>Koła:</strong> ${escapeHtml(observationValue(observation, "selected_wheels"))}</p>
        <p><strong>Tapicerka:</strong> ${escapeHtml(observationValue(observation, "selected_upholstery"))}</p>
        <p class="commercial-choice-source-note">Wygląd pochodzi wyłącznie z dokładnej zapisanej obserwacji producenta${observation.observed_on ? ` z ${escapeHtml(observation.observed_on)}` : ""}. Nie jest to katalog innych dostępnych wyborów.</p>`
      : '<p class="commercial-choice-source-note">Brak dokładnej zapisanej obserwacji wyglądu dla tej konfiguracji. Kolor, koła i tapicerka nie są uzupełniane przez wnioskowanie.</p>';
    const unknownWarning = preview.unknown_items.length
      ? '<p class="configuration-price-warning">Co najmniej jedna wybrana pozycja nie ma potwierdzonej ceny i nie została doliczona.</p>'
      : "";
    const compatibilityWarning = preview.multi_choice_compatibility_unverified
      ? '<p class="configuration-price-warning">Łączna cena wielu pozycji jest tylko sumą arytmetyczną. Repozytorium nie potwierdza ich wzajemnej kompatybilności ani możliwości jednoczesnego zamówienia.</p>'
      : "";
    const basePrice = preview.base_amount === null
      ? "brak danych"
      : formatMoney(preview.base_amount, preview.currency_code);
    return `<p class="eyebrow">Krok 8</p>
      <h2 id="configurator-summary-heading">Podsumowanie konfiguracji</h2>
      <p><strong>${escapeHtml(configuration.model_name || configuration.model_code || "Dacia")} · ${escapeHtml(configuration.version_name || configuration.version_code || "")}</strong></p>
      <p>${escapeHtml(configuration.powertrain_label || "brak danych")} · skrzynia ${escapeHtml(transmissionSummaryLabel(configuration.transmission_type))}</p>
      <p><strong>Kod konfiguracji:</strong> <code>${escapeHtml(configuration.configuration_code || "")}</code></p>
      <div class="configuration-price-standard">Cena bazowa: <strong>${escapeHtml(basePrice)}</strong></div>
      <div class="configuration-price-main"><span>Cena z jawnie wybranymi pakietami i opcjami</span><strong>${escapeHtml(total)}</strong></div>
      <ul class="configuration-price-components">${selectedRows}</ul>
      ${unknownWarning}${compatibilityWarning}
      <h3>Wygląd — dokładna obserwacja</h3>
      ${appearance}
      <p class="commercial-choice-source-note">Podsumowanie handlowe obejmuje wyłącznie pozycje jawnie zaznaczone w kroku „Pakiety i opcje”. Filtry wyposażenia służą do zawężania shortlisty i nie są automatycznie traktowane jako dodatkowe zamówienie.</p>`;
  }

  function installConfiguratorSummary() {
    const results = document.querySelector("#results");
    if (!results) return;
    let panel = document.querySelector("#configurator-summary-panel");
    if (!panel) {
      panel = document.createElement("div");
      panel.id = "configurator-summary-panel";
      panel.className = "comparison-panel configurator-summary-panel";
      panel.setAttribute("aria-live", "polite");
      panel.setAttribute("aria-labelledby", "configurator-summary-heading");
      results.parentNode.insertBefore(panel, results);
    }
    let scheduled = false;
    const refresh = () => {
      if (scheduled) return;
      scheduled = true;
      setTimeout(() => {
        scheduled = false;
        const cards = [...results.querySelectorAll(".result-card")];
        if (!cards.length) {
          panel.innerHTML = '<p class="eyebrow">Krok 8</p><h2 id="configurator-summary-heading">Podsumowanie konfiguracji</h2><p>Brak konfiguracji spełniającej aktualne kryteria. Podsumowanie nie wybiera wariantu zastępczego.</p>';
          return;
        }
        if (cards.length !== 1) {
          panel.innerHTML = `<p class="eyebrow">Krok 8</p><h2 id="configurator-summary-heading">Podsumowanie konfiguracji</h2><p>Zawęź wybór do jednej konfiguracji. Aktualnie zgodnych wariantów: <strong>${cards.length}</strong>. System nie wybiera samochodu arbitralnie.</p>`;
          return;
        }
        const card = cards[0];
        const code = card.dataset.configurationCode
          || card.querySelector(".configuration-code")?.textContent.trim()
          || "";
        const configuration = summaryConfigurationByCode.get(code);
        if (!configuration) {
          panel.innerHTML = '<p class="eyebrow">Krok 8</p><h2 id="configurator-summary-heading">Podsumowanie konfiguracji</h2><p>Nie udało się powiązać widocznego wyniku z katalogiem. Dane nie są uzupełniane przez zgadywanie.</p>';
          return;
        }
        const selected = commercialSelections.get(code) || new Set();
        panel.innerHTML = configuratorSummaryMarkup(
          configuration,
          summaryObservationByCode.get(code) || null,
          [...selected]
        );
      }, 0);
    };
    results.addEventListener("dkb:results-rendered", refresh);
    document.addEventListener("change", (event) => {
      if (event.target.matches("[data-commercial-choice]")) refresh();
    });
    refresh();
  }

  function installCommercialChoiceSelector() {
    const catalogElement = document.querySelector("#configuration-catalog");
    const results = document.querySelector("#results");
    if (!catalogElement || !results) return;
    const catalog = JSON.parse(catalogElement.textContent);
    const byCode = new Map((catalog.configurations || []).map((item) => [item.configuration_code, item]));
    let scheduled = false;
    const refresh = () => {
      if (scheduled) return;
      scheduled = true;
      setTimeout(() => {
        scheduled = false;
        for (const card of results.querySelectorAll(".result-card")) {
          const code = card.dataset.configurationCode
            || card.querySelector(".configuration-code")?.textContent.trim()
            || "";
          const configuration = byCode.get(code);
          if (!configuration || !commercialChoiceItems(configuration).length) continue;
          const passive = card.querySelector(".commercial-offers:not(.commercial-choice-panel)");
          if (passive) passive.remove();
          let panel = card.querySelector(".commercial-choice-panel");
          if (!panel) {
            panel = document.createElement("details");
            panel.className = "commercial-offers commercial-choice-panel";
            panel.dataset.configurationCode = code;
            const provenance = card.querySelector("details");
            if (provenance) card.insertBefore(panel, provenance); else card.append(panel);
          }
          const selected = commercialSelections.get(code) || new Set();
          panel.innerHTML = commercialChoiceMarkup(configuration, [...selected]);
          if (panel.dataset.bound !== "true") {
            panel.dataset.bound = "true";
            panel.addEventListener("change", (event) => {
              const input = event.target.closest("[data-commercial-choice]");
              if (!input) return;
              const state = commercialSelections.get(code) || new Set();
              if (input.checked) state.add(input.dataset.commercialChoice);
              else state.delete(input.dataset.commercialChoice);
              commercialSelections.set(code, state);
              panel.innerHTML = commercialChoiceMarkup(configuration, [...state]);
            });
          }
        }
      }, 0);
    };
    results.addEventListener("dkb:results-rendered", refresh);
    refresh();
  }

  if (typeof document !== "undefined") {
    const installPricingUi = () => {
      installCommercialChoiceSelector();
      installConfiguratorSummary();
    };
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", installPricingUi);
    } else {
      installPricingUi();
    }
  }

  return {
    setEquipmentLabels, equipmentLabel, formatMoney,
    chooseComponents, buildPriceBreakdown, priceBreakdownMarkup,
    selectedEquipmentStatus, selectedEquipmentMarkup,
    reviewedUnknownPriceStatus, normalizeComponent,
    commercialChoiceItems, buildCommercialSelectionPreview,
    commercialChoiceMarkup, installCommercialChoiceSelector,
    configuratorSummaryMarkup, installConfiguratorSummary
  };
});

(function (root) {
  "use strict";
  const MARKER = "configurator_navigation_state_integration_v1";

  function summaryStatus(matchCount) {
    const count = Math.max(0, Number(matchCount) || 0);
    if (count === 1) return "gotowe";
    if (count > 1) return `zawęź: ${count} wariantów`;
    return "brak wyników";
  }

  function commercialStatus(selectedCount, choiceCount, matchCount) {
    const selected = Math.max(0, Number(selectedCount) || 0);
    const choices = Math.max(0, Number(choiceCount) || 0);
    const matches = Math.max(0, Number(matchCount) || 0);
    if (selected) return `wybrano: ${selected}`;
    if (matches > 1) return "najpierw 1 wariant";
    if (matches === 0) return "brak wyniku";
    if (choices) return `oferty: ${choices}`;
    return "brak potwierdzonych ofert";
  }

  function markCurrent(shell, stepId) {
    for (const button of shell.querySelectorAll("[data-configurator-step]")) {
      if (button.dataset.configuratorStep === stepId) button.setAttribute("aria-current", "step");
      else button.removeAttribute("aria-current");
    }
  }

  function focusTarget(target) {
    if (!target) return;
    target.scrollIntoView({ behavior: "smooth", block: "center" });
    const focusable = target.matches("button,input,select,a[href],summary")
      ? target
      : target.querySelector("button:not([disabled]),input:not([disabled]),select:not([disabled]),a[href],summary");
    if (focusable) focusable.focus({ preventScroll: true });
  }

  function flowTarget(stepId, results) {
    if (stepId === "summary") {
      return document.querySelector("#configurator-summary-panel, #results-heading");
    }
    if (stepId === "commercial") {
      const cards = [...results.querySelectorAll(".result-card")];
      if (cards.length === 1) {
        return cards[0].querySelector(".commercial-choice-panel, .commercial-offers") || cards[0];
      }
      return results;
    }
    return null;
  }

  function install() {
    let attempts = 0;
    const bind = () => {
      const shell = document.querySelector(".configurator-step-shell");
      const results = document.querySelector("#results");
      if (!shell || !results) {
        attempts += 1;
        if (attempts < 8) setTimeout(bind, 0);
        return;
      }
      if (shell.dataset.navigationStateIntegrated === "true") return;
      shell.dataset.navigationStateIntegrated = "true";

      const statusElement = (stepId) => shell.querySelector(
        `[data-configurator-step="${stepId}"] [data-configurator-step-status]`
      );
      let scheduled = false;
      const refresh = () => {
        if (scheduled) return;
        scheduled = true;
        setTimeout(() => {
          scheduled = false;
          const matches = results.querySelectorAll(".result-card").length;
          const choices = results.querySelectorAll(
            ".commercial-choice-panel [data-commercial-choice]"
          ).length;
          const selected = results.querySelectorAll(
            ".commercial-choice-panel [data-commercial-choice]:checked"
          ).length;
          const commercial = statusElement("commercial");
          const summary = statusElement("summary");
          if (commercial) commercial.textContent = commercialStatus(selected, choices, matches);
          if (summary) summary.textContent = summaryStatus(matches);
        }, 0);
      };

      shell.addEventListener("click", (event) => {
        const button = event.target.closest("[data-configurator-step]");
        if (!button || button.disabled) return;
        const stepId = button.dataset.configuratorStep;
        if (stepId !== "commercial" && stepId !== "summary") return;
        event.preventDefault();
        event.stopImmediatePropagation();
        markCurrent(shell, stepId);
        focusTarget(flowTarget(stepId, results));
      }, true);
      results.addEventListener("dkb:results-rendered", refresh);
      document.addEventListener("change", (event) => {
        if (event.target.matches("[data-commercial-choice]")) refresh();
      });
      refresh();
    };
    setTimeout(bind, 0);
  }

  const api = { MARKER, summaryStatus, commercialStatus, install };
  root.DkbConfiguratorNavigationState = api;
  if (typeof document !== "undefined") {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", install);
    else install();
  }
})(typeof globalThis !== "undefined" ? globalThis : this);
