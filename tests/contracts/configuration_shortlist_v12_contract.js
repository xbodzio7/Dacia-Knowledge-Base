"use strict";

const assert = require("assert/strict");
const api = require("../../tools/reporting/configuration_shortlist_v12_pricing.js");

api.setEquipmentLabels({
  automatic_climate_control: "Klimatyzacja automatyczna",
  heated_front_seats: "Podgrzewane fotele przednie",
  keyless_entry: "Dostęp bezkluczykowy"
});

const configuration = {
  catalog_price: { state: "recorded", amount: 80000, currency_code: "PLN" },
  equipment: {
    automatic_climate_control: { availability_status: "optional" },
    heated_front_seats: { availability_status: "optional" },
    keyless_entry: { availability_status: "standard" }
  },
  price_components: [
    { code: "climate_option", name: "Klimatyzacja", kind: "option", amount: 1500, currency_code: "PLN", equipment_codes: ["automatic_climate_control"] },
    { code: "heated_option", name: "Fotele", kind: "option", amount: 900, currency_code: "PLN", equipment_codes: ["heated_front_seats"] },
    { code: "thermo_package", name: "Pakiet THERMO", kind: "package", amount: 1900, currency_code: "PLN", equipment_codes: ["automatic_climate_control", "heated_front_seats"] }
  ]
};

let breakdown = api.buildPriceBreakdown(
  configuration,
  ["automatic_climate_control", "heated_front_seats"],
  ["keyless_entry"]
);
assert.equal(breakdown.known_surcharge, 1900);
assert.equal(breakdown.total_amount, 81900);
assert.deepEqual(breakdown.known_components.map((item) => item.code), ["thermo_package"]);
assert.deepEqual(breakdown.included_standard.map((item) => item.code), ["keyless_entry"]);
assert.equal(breakdown.total_is_complete, true);

breakdown = api.buildPriceBreakdown(configuration, ["automatic_climate_control"], []);
assert.deepEqual(breakdown.known_components.map((item) => item.code), ["climate_option"]);
assert.equal(breakdown.known_surcharge, 1500);

breakdown = api.buildPriceBreakdown(configuration, [], []);
assert.equal(breakdown.known_components.length, 0);
assert.equal(breakdown.total_amount, 80000);

const missing = api.buildPriceBreakdown({
  catalog_price: { state: "recorded", amount: 80000, currency_code: "PLN" },
  equipment: { heated_front_seats: { availability_status: "optional" } },
  price_components: []
}, ["heated_front_seats"], []);
assert.equal(missing.unknown_components.length, 1);
assert.equal(missing.total_is_complete, false);
assert.match(api.priceBreakdownMarkup(missing), /cena nieustalona/);

const manyAlternatives = Array.from({ length: 35 }, (_, index) => ({
  code: `alternative_${index}`,
  name: `Alternative ${index}`,
  kind: "option",
  amount: 2000 - index,
  currency_code: "PLN",
  equipment_codes: ["automatic_climate_control"]
}));
const selectedAlternative = api.chooseComponents(
  manyAlternatives,
  ["automatic_climate_control"]
);
assert.deepEqual(selectedAlternative.map((item) => item.code), ["alternative_34"]);

const ui = require("../../tools/reporting/configuration_shortlist_v12.js");
let textWrites = 0;
const badge = {
  _text: "",
  get textContent() { return this._text; },
  set textContent(value) { textWrites += 1; this._text = value; },
  title: ""
};
const card = { querySelectorAll: () => [badge] };
const criteria = { required_equipment: ["automatic_climate_control"], required_standard_equipment: [] };
ui.localizeBadges(card, configuration, criteria);
ui.localizeBadges(card, configuration, criteria);
assert.equal(textWrites, 1);

global.Event = class Event {
  constructor(type, options) { this.type = type; this.bubbles = Boolean(options && options.bubbles); }
};
const dispatched = [];
ui.dispatchSelection({ dispatchEvent: (event) => dispatched.push(event.type) });
assert.deepEqual(dispatched, ["change"]);

console.log("Configuration shortlist HTML v1.2 pricing contract passed.");
