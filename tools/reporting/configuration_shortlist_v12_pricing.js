(function (root, factory) {
  "use strict";
  const api = factory();
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  root.DkbConfigurationPricingV12 = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  let equipmentLabels = Object.freeze({});

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
    return {
      code: String(component.code || ""),
      name: String(component.name || component.code || "Dopłata"),
      kind: component.kind === "package" ? "package" : "option",
      amount: Number.isFinite(numeric) ? numeric : null,
      currency_code: String(component.currency_code || defaultCurrency || "PLN"),
      price_date: String(component.price_date || ""),
      source_code: String(component.source_code || ""),
      equipment_codes: unique(component.equipment_codes || []),
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

  return {
    setEquipmentLabels, equipmentLabel, formatMoney,
    chooseComponents, buildPriceBreakdown, priceBreakdownMarkup,
    selectedEquipmentStatus, selectedEquipmentMarkup,
    reviewedUnknownPriceStatus
  };
});
