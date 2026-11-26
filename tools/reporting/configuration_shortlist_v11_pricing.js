(function (root, factory) {
  "use strict";
  const api = factory();
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  root.DkbConfigurationPricingV11 = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  let equipmentLabels = Object.freeze({});

  function setEquipmentLabels(labels) {
    equipmentLabels = Object.freeze({ ...(labels || {}) });
  }

  function unique(values) {
    return [...new Set((values || [])
      .filter((value) => value !== null && value !== undefined)
      .map(String)
      .map((value) => value.trim())
      .filter(Boolean))];
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function equipmentLabel(code, fallback) {
    return equipmentLabels[code] || String(fallback || code);
  }

  function formatMoney(amount, currencyCode) {
    const number = Number(amount);
    if (!Number.isFinite(number)) return "brak danych";
    return new Intl.NumberFormat("pl-PL", {
      style: "currency",
      currency: currencyCode || "PLN",
      minimumFractionDigits: Number.isInteger(number) ? 0 : 2,
      maximumFractionDigits: 2
    }).format(number).replaceAll("\u00a0", " ");
  }

  function normalizePriceComponent(component, defaultCurrency) {
    const rawAmount = component.amount;
    const amount = rawAmount === null || rawAmount === undefined || rawAmount === ""
      ? null
      : Number(rawAmount);
    const amountKnown = amount !== null && Number.isFinite(amount);
    return {
      code: String(component.code || ""),
      name: String(component.name || component.label || component.code || "Dopłata"),
      kind: component.kind === "package" ? "package" : "option",
      amount: amountKnown ? amount : null,
      currency_code: String(component.currency_code || defaultCurrency || "PLN"),
      equipment_codes: unique([
        component.equipment_code,
        ...(component.equipment_codes || [])
      ])
    };
  }

  function buildPriceBreakdown(configuration, requiredEquipment, requiredStandardEquipment) {
    const price = configuration.catalog_price || {};
    const baseAmount = price.state === "recorded" && Number.isFinite(Number(price.amount))
      ? Number(price.amount)
      : null;
    const currencyCode = String(price.currency_code || "PLN");
    const components = (configuration.price_components || [])
      .filter((component) => component && component.selected !== false)
      .map((component) => normalizePriceComponent(component, currencyCode));
    const knownComponents = components.filter((component) => component.amount !== null);
    const unknownComponents = components.filter((component) => component.amount === null);
    const coveredEquipment = new Set();
    for (const component of components) {
      if (component.code) coveredEquipment.add(component.code);
      for (const code of component.equipment_codes) coveredEquipment.add(code);
    }

    const selectedCodes = unique([
      ...(requiredEquipment || []),
      ...(requiredStandardEquipment || [])
    ]);
    const includedStandard = [];
    for (const code of selectedCodes) {
      const state = (configuration.equipment || {})[code];
      if (!state) continue;
      if (state.availability_status === "standard") {
        includedStandard.push({ code, name: equipmentLabel(code) });
      } else if (state.availability_status === "optional" && !coveredEquipment.has(code)) {
        unknownComponents.push({
          code,
          name: equipmentLabel(code),
          kind: "option",
          amount: null,
          currency_code: currencyCode,
          equipment_codes: [code]
        });
      }
    }

    const knownSurcharge = knownComponents.reduce((sum, component) => sum + component.amount, 0);
    const totalAmount = baseAmount === null ? null : baseAmount + knownSurcharge;
    return {
      currency_code: currencyCode,
      standard_amount: baseAmount,
      known_components: knownComponents,
      unknown_components: unknownComponents,
      included_standard: includedStandard,
      known_surcharge: knownSurcharge,
      total_amount: totalAmount,
      total_is_complete: totalAmount !== null && unknownComponents.length === 0
    };
  }

  function priceBreakdownMarkup(breakdown) {
    if (breakdown.standard_amount === null) {
      return '<div class="configuration-price-main"><span>Cena konfiguracji</span><strong>brak danych</strong></div>';
    }
    const totalText = formatMoney(breakdown.total_amount, breakdown.currency_code);
    const headline = breakdown.total_is_complete ? totalText : `od ${totalText}`;
    const items = [
      ...breakdown.known_components.map((component) => (
        `<li><span>${escapeHtml(component.name)}</span><strong>+ ${escapeHtml(formatMoney(component.amount, component.currency_code))}</strong></li>`
      )),
      ...breakdown.unknown_components.map((component) => (
        `<li class="price-component-unknown"><span>${escapeHtml(component.name)}</span><strong>cena nieustalona</strong></li>`
      ))
    ].join("");
    const components = items ? `<ul class="configuration-price-components">${items}</ul>` : "";
    const warning = breakdown.unknown_components.length
      ? '<p class="configuration-price-warning">Nieznane dopłaty nie zostały doliczone do ceny.</p>'
      : "";
    const included = breakdown.included_standard.length
      ? `<p class="configuration-price-included">Wybrane wyposażenie w cenie standardowej: ${breakdown.included_standard.length}</p>`
      : "";
    return `<div class="configuration-price-main"><span>Cena konfiguracji</span><strong>${escapeHtml(headline)}</strong></div>
      <div class="configuration-price-standard">Cena standardowa: <strong>${escapeHtml(formatMoney(breakdown.standard_amount, breakdown.currency_code))}</strong></div>
      ${components}${warning}${included}`;
  }

  return {
    setEquipmentLabels,
    equipmentLabel,
    formatMoney,
    buildPriceBreakdown,
    priceBreakdownMarkup
  };
});
