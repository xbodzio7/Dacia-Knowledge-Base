from __future__ import annotations

import csv
import hashlib
import json
import unittest
from pathlib import Path

from tools import import_configuration_value_ranges as range_importer

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SOURCE = "src_pl_bigster_brochure_20251210"
SOURCE_SHA = "76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74"
PDF = ROOT / "PDF" / "Broszury" / "DACIA BIGSTER broszura 20251210.pdf"

EXPECTED_BROCHURE_PAYLOAD = {
    "bigster_essential_mildhybridg140_4x2_manual": ("452", "521"),
    "bigster_expression_mildhybridg140_4x2_manual": ("452", "521"),
    "bigster_extreme_mildhybridg140_4x2_manual": ("452", "521"),
    "bigster_journey_mildhybridg140_4x2_manual": ("452", "521"),
}
EXPECTED_JULY_PAYLOAD = {
    "bigster_essential_mildhybrid140_4x2_manual": ("451", "540"),
    "bigster_expression_mildhybrid140_4x2_manual": ("451", "540"),
    "bigster_extreme_mildhybrid140_4x2_manual": ("451", "540"),
    "bigster_journey_mildhybrid140_4x2_manual": ("451", "540"),
    "bigster_essential_mildhybridg140_4x2_manual": ("451", "540"),
    "bigster_expression_mildhybridg140_4x2_manual": ("451", "540"),
    "bigster_extreme_mildhybridg140_4x2_manual": ("451", "540"),
    "bigster_journey_mildhybridg140_4x2_manual": ("451", "540"),
    "bigster_expression_hybridg150_4x4_automatic": ("462", "509"),
    "bigster_extreme_hybridg150_4x4_automatic": ("462", "509"),
    "bigster_journey_hybridg150_4x4_automatic": ("462", "509"),
    "bigster_expression_hybrid155_4x2_automatic": ("453", "521"),
    "bigster_extreme_hybrid155_4x2_automatic": ("453", "521"),
    "bigster_journey_hybrid155_4x2_automatic": ("453", "521"),
}
EXPECTED_BROCHURE_PRINTED_PAYLOAD = {
    "bigster_essential_mildhybridg140_4x2_manual": ("452", "521"),
    "bigster_expression_mildhybridg140_4x2_manual": ("452", "521"),
    "bigster_extreme_mildhybridg140_4x2_manual": ("452", "521"),
    "bigster_journey_mildhybridg140_4x2_manual": ("452", "521"),
    "bigster_essential_mildhybrid140_4x2_manual": ("451", "540"),
    "bigster_expression_mildhybrid140_4x2_manual": ("451", "540"),
    "bigster_extreme_mildhybrid140_4x2_manual": ("451", "540"),
    "bigster_journey_mildhybrid140_4x2_manual": ("451", "540"),
    "bigster_expression_hybridg150_4x4_automatic": ("462", "509"),
    "bigster_extreme_hybridg150_4x4_automatic": ("462", "509"),
    "bigster_journey_hybridg150_4x4_automatic": ("462", "509"),
    "bigster_expression_hybrid155_4x2_automatic": ("453", "521"),
    "bigster_extreme_hybrid155_4x2_automatic": ("453", "521"),
    "bigster_journey_hybrid155_4x2_automatic": ("453", "521"),
}
EXPECTED_COLOURS = {
    "bigster_colour_biel_alpejska": ("Biel Alpejska", "BIEL ALPEJSKA", "non_metallic", "present"),
    "bigster_colour_czarna_perla": ("Czarna Perła", "CZARNA PERŁA", "metallic", "not_printed"),
    "bigster_colour_szary_shiste": ("Szary Shiste", "SZARY SHISTE", "metallic", "present"),
    "bigster_colour_niebieski_indigo": ("Niebieski Indigo", "NIEBIESKI INDIGO", "metallic", "present"),
    "bigster_colour_zielony_cedar": ("Zielony Cedar", "ZIELONY CEDAR", "metallic", "present"),
    "bigster_colour_brazowy_terracotta": ("Brązowy Terracotta", "BRĄZOWY TERRACOTTA", "metallic", "present"),
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class BigsterBrochureFullAssimilationTests(unittest.TestCase):
    def test_full_brochure_reconciliation_and_exact_model_level_palette(self) -> None:
        self.assertEqual(hashlib.sha256(PDF.read_bytes()).hexdigest(), SOURCE_SHA)

        source_links = read_rows(MASTER / "source_configurations.csv")
        linked = {
            row["configuration_code"]
            for row in source_links
            if row["source_code"] == SOURCE
            and row["relationship"] == "brochure_technical_data_for"
        }
        self.assertEqual(len(linked), 14)

        ranges = read_rows(MASTER / "configuration_attribute_value_ranges.csv")
        brochure_payload = {
            row["configuration_code"]: (row["minimum_value"], row["maximum_value"])
            for row in ranges
            if row["source_code"] == SOURCE
            and row["attribute_code"] == "maximum_payload"
        }
        july_payload = {
            row["configuration_code"]: (row["minimum_value"], row["maximum_value"])
            for row in ranges
            if row["source_code"] == "src_pl_bigster_price_my26_20260703"
            and row["attribute_code"] == "maximum_payload"
        }
        self.assertEqual(brochure_payload, EXPECTED_BROCHURE_PAYLOAD)
        self.assertEqual(july_payload, EXPECTED_JULY_PAYLOAD)
        self.assertEqual(set(EXPECTED_BROCHURE_PRINTED_PAYLOAD), linked)
        self.assertEqual(set(EXPECTED_JULY_PAYLOAD), linked)
        self.assertEqual(len(set(EXPECTED_BROCHURE_PRINTED_PAYLOAD) - set(EXPECTED_BROCHURE_PAYLOAD)), 10)
        for configuration in set(EXPECTED_BROCHURE_PRINTED_PAYLOAD) - set(EXPECTED_BROCHURE_PAYLOAD):
            self.assertEqual(
                EXPECTED_BROCHURE_PRINTED_PAYLOAD[configuration],
                EXPECTED_JULY_PAYLOAD[configuration],
            )
        for configuration in EXPECTED_BROCHURE_PAYLOAD:
            self.assertNotEqual(
                EXPECTED_BROCHURE_PRINTED_PAYLOAD[configuration],
                EXPECTED_JULY_PAYLOAD[configuration],
            )
        self.assertEqual(
            len([
                row for row in ranges
                if row["source_code"] == SOURCE
            ]),
            34,
        )

        brochure_range_spec = range_importer.load_spec(
            ROOT / "data" / "imports" / "configuration_value_ranges"
            / "bigster-page20-mildhybridg140-maximum-payload-20251210.json"
        )
        verified = range_importer.verify_import(ROOT, brochure_range_spec)
        self.assertEqual(len(verified.missing_rows), 0)

        items = {
            row["code"]: row
            for row in read_rows(MASTER / "commercial_items.csv")
            if row["code"] in EXPECTED_COLOURS
        }
        self.assertEqual(set(items), set(EXPECTED_COLOURS))
        attributes = {
            row["commercial_item_code"]: row
            for row in read_rows(MASTER / "commercial_item_attributes.csv")
            if row["commercial_item_code"] in EXPECTED_COLOURS
        }
        self.assertEqual(set(attributes), set(EXPECTED_COLOURS))
        mappings = [
            row for row in read_rows(MASTER / "commercial_item_configurations.csv")
            if row["commercial_item_code"] in EXPECTED_COLOURS
        ]
        self.assertEqual(mappings, [])

        for code, (name, source_text, finish, two_tone) in EXPECTED_COLOURS.items():
            item = items[code]
            self.assertEqual(item["name"], name)
            self.assertEqual(item["item_type"], "option")
            self.assertEqual(item["observation_date"], "2025-12-10")
            self.assertEqual(item["source_code"], SOURCE)
            self.assertEqual(item["status"], "active")
            self.assertIn(f"finish={finish}", item["notes"])
            self.assertIn(f"two-tone marker={two_tone}", item["notes"])
            attribute = attributes[code]
            self.assertEqual(attribute["attribute_code"], "exterior_color")
            self.assertEqual(attribute["source_text"], source_text)

        compatibility = read_rows(
            ROOT / "data" / "reporting"
            / "official_bigster_accessory_catalog_compatibility_20260806.csv"
        )
        roof_rack = [row for row in compatibility if row["part_number"] == "7717277154"]
        self.assertEqual(len(roof_rack), 1)
        self.assertIn(
            "s. 19: niekompatybilny z panoramicznym szklanym dachem",
            roof_rack[0]["notes"],
        )

        sources = read_rows(MASTER / "sources.csv")
        source = next(row for row in sources if row["code"] == SOURCE)
        self.assertIn("fully_assimilated_with_deferrals", source["notes"])

        report = json.loads(
            (ROOT / "data" / "reporting"
             / "official_bigster_brochure_full_assimilation_20261125.json")
            .read_text(encoding="utf-8")
        )
        self.assertEqual(report["status"], "fully_assimilated_with_deferrals")
        self.assertEqual(len(report["pages"]), 24)
        self.assertEqual(
            report["master_reconciliation"]["source_observations"]
            ["configuration_attribute_availability"],
            557,
        )
        self.assertEqual(
            report["master_reconciliation"]["new_master_mutations"]
            ["commercial_items"],
            6,
        )

        ledger = json.loads(
            (ROOT / "project" / "sources"
             / "bigster_brochure_deferred_gaps_20251210.json")
            .read_text(encoding="utf-8")
        )
        self.assertTrue(all(item["status"] == "Do sprawdzenia" for item in ledger["items"]))
        self.assertEqual(
            {item["id"] for item in ledger["resolved_items"]},
            {"BIGSTER-BR-004", "BIGSTER-BR-006", "BIGSTER-BR-007", "BIGSTER-BR-008"},
        )

        state = json.loads((ROOT / "project" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["baseline"]["tests"], 2055)
        self.assertEqual(
            state["baseline"]["rows"],
            sum(
                1
                for path in MASTER.glob("*.csv")
                for _ in csv.DictReader(path.open(encoding="utf-8-sig", newline=""))
            ),
        )
        self.assertEqual(state["baseline"]["configuration_value_ranges"], 472)
        # The Spring closeout is complete; the portfolio review is the next planned package.
        self.assertEqual(state["next_package"]["status"], "planned")


if __name__ == "__main__":
    unittest.main()
