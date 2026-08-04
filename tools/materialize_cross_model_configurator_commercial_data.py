#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ROWS = [
  {"configuration_code":"GGQ0LU","model_family":"bigster","phase":"current","grade":"essential","powertrain":"mild hybrid-G 140","seat_count":5,"price_pln":101400,"colour":"biel alpejska","colour_price_pln":0,"wheels":"aluminiowe obręcze kół 17\" 215 TERGAN","wheels_price_pln":0,"upholstery":"tapicerka materiałowa essential","upholstery_price_pln":0,"source_page":2},
  {"configuration_code":"EFVBCJ","model_family":"bigster","phase":"current","grade":"expression","powertrain":"mild hybrid-G 140","seat_count":5,"price_pln":110400,"colour":"biel alpejska","colour_price_pln":0,"wheels":"aluminiowe obręcze kół 17\" 215 TERGAN diamentowane","wheels_price_pln":0,"upholstery":"tapicerka materiałowa \"Denim\" z odblaskowym logo","upholstery_price_pln":0,"source_page":2},
  {"configuration_code":"XO3PYO","model_family":"bigster","phase":"current","grade":"extreme","powertrain":"mild hybrid-G 140","seat_count":5,"price_pln":118900,"colour":"biel alpejska","colour_price_pln":0,"wheels":"aluminiowe obręcze kół 18\" 215 TAGASAN pół diamentowane","wheels_price_pln":0,"upholstery":"tapicerka \"MicroCloud\" z odblaskowym logo","upholstery_price_pln":0,"source_page":2},
  {"configuration_code":"OL7ODX","model_family":"bigster","phase":"current","grade":"journey","powertrain":"mild hybrid 140","seat_count":5,"price_pln":118500,"colour":"biel alpejska","colour_price_pln":0,"wheels":"aluminiowe obręcze kół 18\" 215 TAGASAN diamentowane","wheels_price_pln":0,"upholstery":"tapicerka materiałowa journey łączona z MicroCloud","upholstery_price_pln":0,"source_page":2},
  {"configuration_code":"MEOHF3","model_family":"duster","phase":"current","grade":"essential","powertrain":"Eco-G 120","seat_count":5,"price_pln":82000,"colour":"biel alpejska","colour_price_pln":0,"wheels":"16\" felgi stalowe w kolorze czarnym","wheels_price_pln":0,"upholstery":"tapicerka materiałowa essential","upholstery_price_pln":0,"source_page":2},
  {"configuration_code":"QWY7QR","model_family":"duster","phase":"current","grade":"expression","powertrain":"Eco-G 120","seat_count":5,"price_pln":90000,"colour":"biel alpejska","colour_price_pln":0,"wheels":"17\" felgi aluminiowe, TERGAN 215","wheels_price_pln":0,"upholstery":"tapicerka materiałowa \"Denim\" z odblaskowym logo","upholstery_price_pln":0,"source_page":2},
  {"configuration_code":"QVQDYV","model_family":"duster","phase":"current","grade":"extreme","powertrain":"Eco-G 120","seat_count":5,"price_pln":96000,"colour":"biel alpejska","colour_price_pln":0,"wheels":"17\" felgi aluminiowe TERGAN BLACK 215","wheels_price_pln":0,"upholstery":"tapicerka \"MicroCloud\" z odblaskowym logo","upholstery_price_pln":0,"source_page":2},
  {"configuration_code":"OQNKFK","model_family":"duster","phase":"current","grade":"journey","powertrain":"Eco-G 120","seat_count":5,"price_pln":96200,"colour":"biel alpejska","colour_price_pln":0,"wheels":"18\" felgi aluminiowe, TAGASAN 215 diamentowane","wheels_price_pln":0,"upholstery":"tapicerka materiałowa journey","upholstery_price_pln":0,"source_page":2},
  {"configuration_code":"I23FGG","model_family":"jogger","phase":"new","grade":"essential","powertrain":"Eco-G 120","seat_count":5,"price_pln":77900,"colour":"biel alpejska","colour_price_pln":0,"wheels":"16\" felgi stalowe","wheels_price_pln":0,"upholstery":"tapicerka materiałowa w kolorze czarnym i wstawkami denim","upholstery_price_pln":0,"source_page":2},
  {"configuration_code":"KJUY16","model_family":"jogger","phase":"new","grade":"expression","powertrain":"Eco-G 120","seat_count":5,"price_pln":82050,"colour":"biel alpejska","colour_price_pln":0,"wheels":"16\" felgi stalowe","wheels_price_pln":0,"upholstery":"tapicerka materiałowa w kolorze czarnym i wstawkami denim","upholstery_price_pln":0,"source_page":2},
  {"configuration_code":"YHGCUZ","model_family":"jogger","phase":"new","grade":"extreme","powertrain":"Eco-G 120","seat_count":5,"price_pln":89900,"colour":"biel alpejska","colour_price_pln":0,"wheels":"16\" felgi aluminiowe czarne","wheels_price_pln":0,"upholstery":"tapicerka microclud extreme","upholstery_price_pln":0,"source_page":2},
  {"configuration_code":"ARKVJG","model_family":"jogger","phase":"new","grade":"journey","powertrain":"TCe 110","seat_count":5,"price_pln":94050,"colour":"biel alpejska","colour_price_pln":0,"wheels":"16\" felgi aluminiowe","wheels_price_pln":0,"upholstery":"tapicerka materiałowa w kolorze denim i czarnymi wstawkami","upholstery_price_pln":0,"source_page":2},
  {"configuration_code":"4TJTWN","model_family":"sandero","phase":"F.2","grade":"essential","powertrain":"TCe 100","seat_count":5,"price_pln":63900,"colour":"biel alpejska","colour_price_pln":0,"wheels":"15\" felgi stalowe ELMA","wheels_price_pln":0,"upholstery":"tapicerka materiałowa w kolorze czarnym i wstawkami denim","upholstery_price_pln":0,"source_page":2},
  {"configuration_code":"FZXCXZ","model_family":"sandero","phase":"F.2","grade":"expression","powertrain":"TCe 100","seat_count":5,"price_pln":68000,"colour":"biel alpejska","colour_price_pln":0,"wheels":"16\" felgi stalowe ATARA","wheels_price_pln":0,"upholstery":"tapicerka materiałowa w kolorze czarnym i wstawkami denim","upholstery_price_pln":0,"source_page":2},
  {"configuration_code":"HJISLB","model_family":"sandero","phase":"F.2","grade":"journey","powertrain":"TCe 100","seat_count":5,"price_pln":73600,"colour":"biel alpejska","colour_price_pln":0,"wheels":"16\" felgi aluminiowe TAMIA","wheels_price_pln":0,"upholstery":"tapicerka materiałowa w kolorze denim i czarnymi wstawkami","upholstery_price_pln":0,"source_page":2},
  {"configuration_code":"9I1STI","model_family":"sandero_stepway","phase":"F.2","grade":"stepway essential","powertrain":"TCe 110","seat_count":5,"price_pln":71700,"colour":"biel alpejska","colour_price_pln":0,"wheels":"16\" felgi stalowe ERALIA","wheels_price_pln":0,"upholstery":"tapicerka materiałowa stepway","upholstery_price_pln":0,"source_page":2},
  {"configuration_code":"U56SQT","model_family":"sandero_stepway","phase":"F.2","grade":"stepway expression","powertrain":"Eco-G 120","seat_count":5,"price_pln":76400,"colour":"biel alpejska","colour_price_pln":0,"wheels":"16\" felgi stalowe ATARA","wheels_price_pln":0,"upholstery":"tapicerka materiałowa stepway","upholstery_price_pln":0,"source_page":2},
  {"configuration_code":"5WZLHM","model_family":"sandero_stepway","phase":"F.2","grade":"stepway extreme","powertrain":"Eco-G 120","seat_count":5,"price_pln":82500,"colour":"biel alpejska","colour_price_pln":0,"wheels":"16\" felgi aluminiowe TAMIA BLACK","wheels_price_pln":0,"upholstery":"tapicerka microclud extreme","upholstery_price_pln":0,"source_page":2}
]


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    payload = {
        "product_code": "cross_model_configurator_commercial_data_20260804",
        "observed_on": "2026-08-04",
        "source_code": "src_pl_dacia_configurator_cross_model_pdf_bundle_20260804",
        "record_count": len(ROWS),
        "commercial_fields": ["price_pln", "colour", "colour_price_pln", "wheels", "wheels_price_pln", "upholstery", "upholstery_price_pln"],
        "identity_key": ["configuration_code"],
        "rows": ROWS,
        "migration_boundary": {
            "exact_saved_configuration_only": True,
            "master_data_mutated": False,
            "reason": "New phase/model identities are not yet canonical for every record; exact commercial observations are persisted without unsafe cross-phase promotion.",
            "no_cross_grade_transfer": True,
            "no_cross_powertrain_transfer": True,
            "no_cross_phase_transfer": True
        }
    }
    write(ROOT / "data/reporting/cross_model_configurator_commercial_data.json", json.dumps(payload, ensure_ascii=False, indent=2))
    lines = [
        "# Cross-model Configurator Commercial Data",
        "",
        "Observed: 2026-08-04",
        "",
        "Exact page-2 commercial observations for 18 saved configurator states.",
        "",
        "| Code | Model | Phase | Grade | Powertrain | Price PLN | Colour | Wheels | Upholstery |",
        "|---|---|---|---|---|---:|---|---|---|",
    ]
    for row in ROWS:
        lines.append(f"| {row['configuration_code']} | {row['model_family']} | {row['phase']} | {row['grade']} | {row['powertrain']} | {row['price_pln']} | {row['colour']} | {row['wheels']} | {row['upholstery']} |")
    write(ROOT / "data/reporting/cross_model_configurator_commercial_data.md", "\n".join(lines))
    write(ROOT / "project/packages/cross-model-configurator-commercial-data-migration-20260805.md", """# Cross-model Configurator Commercial Data Migration

## Package

- Package ID: `cross_model_configurator_commercial_data_migration_001`
- Kind: `source_backed_commercial_observation_migration`
- Status: complete
- Source date: 2026-08-04

## Result

Persisted exact page-2 commercial observations for all 18 saved configurator states: displayed catalogue price, base colour and its price, wheel designation and its price, upholstery designation and its price.

Every record is keyed by the configurator code. All selected colour, wheel and upholstery prices are zero in the supplied saved states.

## Boundary

The package does not promote the observations into canonical master rows because Sandero F.2, Sandero Stepway F.2 and the new Jogger require explicit canonical entity creation or mapping. The exact observations are retained without propagation across grade, powertrain, transmission, seat-count or phase boundaries.

## Next package

`cross_model_configurator_standard_equipment_migration_001` will migrate the exact standard-equipment lists from the dedicated equipment pages while preserving the same identity boundaries.
""")
    write(ROOT / "tests/test_cross_model_configurator_commercial_data_20260805.py", """import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / 'data/reporting/cross_model_configurator_commercial_data.json'

class CrossModelConfiguratorCommercialDataTest(unittest.TestCase):
    def test_exact_commercial_contract(self):
        data = json.loads(PATH.read_text(encoding='utf-8'))
        rows = data['rows']
        self.assertEqual(data['record_count'], 18)
        self.assertEqual(len(rows), 18)
        self.assertEqual(len({r['configuration_code'] for r in rows}), 18)
        self.assertEqual(sum(r['price_pln'] for r in rows), 1593400)
        self.assertTrue(all(r['colour'] == 'biel alpejska' for r in rows))
        self.assertTrue(all(r['colour_price_pln'] == 0 for r in rows))
        self.assertTrue(all(r['wheels_price_pln'] == 0 for r in rows))
        self.assertTrue(all(r['upholstery_price_pln'] == 0 for r in rows))
        by_code = {r['configuration_code']: r for r in rows}
        self.assertEqual(by_code['GGQ0LU']['wheels'], 'aluminiowe obręcze kół 17" 215 TERGAN')
        self.assertEqual(by_code['MEOHF3']['price_pln'], 82000)
        self.assertEqual(by_code['I23FGG']['phase'], 'new')
        self.assertEqual(by_code['4TJTWN']['phase'], 'F.2')
        self.assertEqual(by_code['5WZLHM']['wheels'], '16" felgi aluminiowe TAMIA BLACK')
        self.assertFalse(data['migration_boundary']['master_data_mutated'])

if __name__ == '__main__':
    unittest.main()
""")
    state_path = ROOT / "project/state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    expected = "cross_model_configurator_commercial_data_migration_001"
    if state.get("next_package", {}).get("package_id") != expected:
        raise RuntimeError(f"expected next package {expected}")
    state["updated_on"] = "2026-08-05"
    state["phase"] = "Cross-model Configurator Data Assimilation"
    state["current_package"] = {
        "package_id": expected,
        "kind": "source_backed_commercial_observation_migration",
        "name": "Cross-model Configurator Commercial Data Migration",
        "status": "complete",
        "goal": "Persist exact page-2 price, colour, wheel and upholstery observations for all 18 saved configurator states without cross-identity promotion.",
        "manifest_paths": [
            "data/reporting/cross_model_configurator_commercial_data.json",
            "data/reporting/cross_model_configurator_commercial_data.md",
            "project/STATE_SUMMARY.md",
            "project/packages/cross-model-configurator-commercial-data-migration-20260805.md",
            "project/state.json",
            "tests/test_cross_model_configurator_commercial_data_20260805.py"
        ]
    }
    state["next_package"] = {
        "package_id": "cross_model_configurator_standard_equipment_migration_001",
        "kind": "source_backed_equipment_migration",
        "name": "Cross-model Configurator Standard Equipment Migration",
        "status": "planned",
        "goal": "Extract and persist exact standard-equipment lists from all 18 saved configurator PDFs while preserving configuration, phase, powertrain and seat-count boundaries.",
        "manifest_paths": []
    }
    write(state_path, json.dumps(state, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
