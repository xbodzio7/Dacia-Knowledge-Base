"use strict";

const assert = require("node:assert/strict");
const path = require("node:path");
const api = require(path.resolve(
  __dirname,
  "../../tools/reporting/configuration_shortlist_v11_pricing.js"
));
const labels = require(path.resolve(
  __dirname,
  "../../tools/reporting/configuration_shortlist_labels_pl.json"
));
api.setEquipmentLabels(labels);

assert.equal(api.equipmentLabel("rear_view_camera"), "Kamera cofania");
assert.equal(
  api.equipmentLabel("automatic_climate_control"),
  "Klimatyzacja automatyczna"
);

const configuration = {
  catalog_price: {
    state: "recorded",
    amount: "69900",
    currency_code: "PLN"
  },
  equipment: {
    rear_view_camera: { availability_status: "optional" },
    front_parking_sensors: { availability_status: "optional" },
    automatic_climate_control: { availability_status: "standard" }
  },
  price_components: [
    {
      code: "parking_plus",
      name: "Pakiet Parking Plus",
      kind: "package",
      amount: "1500",
      currency_code: "PLN",
      equipment_codes: ["rear_view_camera"]
    }
  ]
};

const breakdown = api.buildPriceBreakdown(
  configuration,
  ["rear_view_camera", "front_parking_sensors"],
  ["automatic_climate_control"]
);

assert.equal(breakdown.standard_amount, 69900);
assert.equal(breakdown.known_surcharge, 1500);
assert.equal(breakdown.total_amount, 71400);
assert.equal(breakdown.total_is_complete, false);
assert.deepEqual(
  breakdown.unknown_components.map((item) => item.code),
  ["front_parking_sensors"]
);
assert.deepEqual(
  breakdown.included_standard.map((item) => item.code),
  ["automatic_climate_control"]
);

const markup = api.priceBreakdownMarkup(breakdown);
for (const expected of [
  "Cena konfiguracji",
  "od 71 400",
  "Cena standardowa",
  "Pakiet Parking Plus",
  "cena nieustalona",
  "Nieznane dopłaty nie zostały doliczone"
]) {
  assert.ok(markup.includes(expected), `missing markup fragment: ${expected}`);
}

const complete = api.buildPriceBreakdown(
  {
    ...configuration,
    equipment: {
      rear_view_camera: { availability_status: "optional" },
      automatic_climate_control: { availability_status: "standard" }
    }
  },
  ["rear_view_camera"],
  ["automatic_climate_control"]
);
assert.equal(complete.total_is_complete, true);
assert.ok(!api.priceBreakdownMarkup(complete).includes("od 71 400"));

console.log("Configuration shortlist HTML v1.1 contract passed.");
