#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOCUMENTS = [
  {"filename":"BIGSTER essential mild hybrid-G 140.pdf","sha256":"432c7c98ca09d6dc45ffea02d620ce01e7939f3da3ca41fec5be66fdf60b06b2","bytes":615910,"pages":9,"model_family":"bigster","grade":"essential","powertrain":"mild hybrid-G 140","fuel":"benzyna + LPG","transmission":"manualna 6 biegów","price_pln":101400,"configuration_code":"GGQ0LU"},
  {"filename":"BIGSTER expression mild hybrid-G 140.pdf","sha256":"44751171377226942306f0003b5b1f262da884d0d77a4fa5118f63759e233c1d","bytes":643032,"pages":9,"model_family":"bigster","grade":"expression","powertrain":"mild hybrid-G 140","fuel":"benzyna + LPG","transmission":"manualna 6 biegów","price_pln":110400,"configuration_code":"EFVBCJ"},
  {"filename":"BIGSTER extreme mild hybrid-G 140.pdf","sha256":"ec5b0fa0bf8c8d4baaf81a974e78a719c56b8fafca7de18f938d8c0f56bbbf2f","bytes":635339,"pages":9,"model_family":"bigster","grade":"extreme","powertrain":"mild hybrid-G 140","fuel":"benzyna + LPG","transmission":"manualna 6 biegów","price_pln":118900,"configuration_code":"XO3PYO"},
  {"filename":"BIGSTER journey mild hybrid 140.pdf","sha256":"6e5b02eac1aa4fd60d52e78ed0477b04b860f69d5af41db55ed3e15b84d4553c","bytes":655422,"pages":9,"model_family":"bigster","grade":"journey","powertrain":"mild hybrid 140","fuel":"benzyna mild hybrid","transmission":"manualna 6 biegów","price_pln":118500,"configuration_code":"OL7ODX"},
  {"filename":"DUSTER essential Eco-G 120.pdf","sha256":"edfefc62fbc5c1b956c23157e513fcd818bc5e8f6eb155c5710b4b780a255a5d","bytes":602233,"pages":9,"model_family":"duster","grade":"essential","powertrain":"Eco-G 120","fuel":"benzyna + LPG","transmission":"manualna","price_pln":82000,"configuration_code":"MEOHF3"},
  {"filename":"DUSTER expression Eco-G 120.pdf","sha256":"4cfc073ddfec4c3bc50643a5336e4358314f0767648c8f9b95145f0b5dd8cd2b","bytes":739646,"pages":9,"model_family":"duster","grade":"expression","powertrain":"Eco-G 120","fuel":"benzyna + LPG","transmission":"manualna","price_pln":90000,"configuration_code":"QWY7QR"},
  {"filename":"DUSTER extreme Eco-G 120.pdf","sha256":"cf063ed14e6c5747bfef5a0c941647b3838662b1100b26c9af65e35bc8efd354","bytes":727527,"pages":9,"model_family":"duster","grade":"extreme","powertrain":"Eco-G 120","fuel":"benzyna + LPG","transmission":"manualna","price_pln":96000,"configuration_code":"QVQDYV"},
  {"filename":"DUSTER journey Eco-G 120.pdf","sha256":"b8497ce040b6c705ce3e4041e002597ef2370aa7af0fc9d1385e0214012c559c","bytes":647907,"pages":9,"model_family":"duster","grade":"journey","powertrain":"Eco-G 120","fuel":"benzyna + LPG","transmission":"manualna","price_pln":96200,"configuration_code":"OQNKFK"},
  {"filename":"NOWY JOGGER essential Eco-G 120 5-miejsc.pdf","sha256":"3e75b149b85c549c94ce367ea7a18682411bce8c02085a213a66154e97e3e7ff","bytes":853947,"pages":10,"model_family":"jogger","phase":"nowy","seat_count":5,"grade":"essential","powertrain":"Eco-G 120","fuel":"benzyna + LPG","transmission":"manualna","price_pln":77900,"configuration_code":"I23FGG"},
  {"filename":"NOWY JOGGER expression Eco-G 120 5-miejsc.pdf","sha256":"9bdf6fb5fa558d5334dc5b20d5b80ca22275e1e5dbc6873840f4f041c7759532","bytes":855124,"pages":10,"model_family":"jogger","phase":"nowy","seat_count":5,"grade":"expression","powertrain":"Eco-G 120","fuel":"benzyna + LPG","transmission":"manualna","price_pln":82050,"configuration_code":"KJUY16"},
  {"filename":"NOWY JOGGER extreme Eco-G 120 5-miejsc.pdf","sha256":"e3ba1d4a44143eeac8de45dc5b4efadc213b92c0d124fcb0d9f9a3eddf008035","bytes":850712,"pages":10,"model_family":"jogger","phase":"nowy","seat_count":5,"grade":"extreme","powertrain":"Eco-G 120","fuel":"benzyna + LPG","transmission":"manualna","price_pln":89900,"configuration_code":"YHGCUZ"},
  {"filename":"NOWY JOGGER journey TCe 110 5-miejsc.pdf","sha256":"90ac33ab881fac38218c3536764b6fdab80991a28d95a26d3b20d3fca9e735a1","bytes":852447,"pages":10,"model_family":"jogger","phase":"nowy","seat_count":5,"grade":"journey","powertrain":"TCe 110","fuel":"benzyna","transmission":"manualna","price_pln":94050,"configuration_code":"ARKVJG"},
  {"filename":"NOWE SANDERO essential TCe 100 F.pdf","sha256":"a0ddd0844519f77e32cb5d0d0540a79ac2eb9c93f29d0589eb2c8b41636e13f0","bytes":616579,"pages":9,"model_family":"sandero","phase":"F.2","grade":"essential","powertrain":"TCe 100","fuel":"benzyna","transmission":"manualna","price_pln":63900,"configuration_code":"4TJTWN"},
  {"filename":"NOWE SANDERO expression TCe 100 f.pdf","sha256":"e7ea0de4e7260df147786513b03a87a8703f3944caa8b6864f74d3e7ab12c591","bytes":726178,"pages":9,"model_family":"sandero","phase":"F.2","grade":"expression","powertrain":"TCe 100","fuel":"benzyna","transmission":"manualna","price_pln":68000,"configuration_code":"FZXCXZ"},
  {"filename":"NOWE SANDERO journey TCe 100 f.pdf","sha256":"e119ba425e3e78d4bcb5403166257bc78455d262d20e16652435452212984915","bytes":725445,"pages":9,"model_family":"sandero","phase":"F.2","grade":"journey","powertrain":"TCe 100","fuel":"benzyna","transmission":"manualna","price_pln":73600,"configuration_code":"HJISLB"},
  {"filename":"NOWE SANDERO STEPWAY essential stepway TCe 110 f.pdf","sha256":"1611d4296103ea5883d19eea321d13dba2d40bd4a7ce5c6adbab9a5bfc10a1ef","bytes":843286,"pages":10,"model_family":"sandero_stepway","phase":"F.2","grade":"essential stepway","powertrain":"TCe 110","fuel":"benzyna","transmission":"manualna","price_pln":71700,"configuration_code":"9I1STI"},
  {"filename":"NOWE SANDERO STEPWAY expression stepway Eco-G 120 f(2).pdf","sha256":"e917125ffc38b76d367436cb68cb4d52f3f30f9f1784e6c70d387c721fee50ea","bytes":849291,"pages":10,"model_family":"sandero_stepway","phase":"F.2","grade":"expression stepway","powertrain":"Eco-G 120","fuel":"benzyna + LPG","transmission":"manualna","price_pln":76400,"configuration_code":"U56SQT"},
  {"filename":"NOWE SANDERO STEPWAY extreme stepway Eco-G 120 f(2).pdf","sha256":"2a45778be95778bab906492de831833b1a8b6abc0dbafd4b60bf6b447504a162","bytes":845833,"pages":10,"model_family":"sandero_stepway","phase":"F.2","grade":"extreme stepway","powertrain":"Eco-G 120","fuel":"benzyna + LPG","transmission":"manualna","price_pln":82500,"configuration_code":"5WZLHM"}
]


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    source = {
        "source_code": "src_pl_dacia_configurator_cross_model_pdf_bundle_20260804",
        "source_type": "official_configurator_pdf_bundle",
        "publisher": "Dacia Polska",
        "observed_on": "2026-08-04",
        "received_on": "2026-08-05",
        "document_count": len(DOCUMENTS),
        "model_families": sorted({d["model_family"] for d in DOCUMENTS}),
        "documents": DOCUMENTS,
        "evidence_boundary": {
            "exact_saved_configuration_only": True,
            "no_cross_grade_transfer": True,
            "no_cross_powertrain_transfer": True,
            "no_cross_phase_transfer": True,
            "no_unselected_option_inference": True,
            "binary_files_external_to_repository": True,
            "binary_identity_preserved_by_sha256": True
        }
    }
    write(ROOT / "project/sources/dacia-pl-configurator-cross-model-pdf-bundle-20260804.json", json.dumps(source, ensure_ascii=False, indent=2))
    write(ROOT / "data/reporting/cross_model_configurator_pdf_intake.json", json.dumps(source, ensure_ascii=False, indent=2))
    write(ROOT / "data/reporting/cross_model_configurator_pdf_intake.md", """# Cross-model Configurator PDF Intake

Observed: 2026-08-04

Registered 18 exact saved configurations across Bigster, Duster, new Jogger 5-seat, new Sandero F.2 and new Sandero Stepway F.2.

The intake preserves each PDF filename, SHA-256, byte size, page count, configuration code, exact grade, powertrain, transmission and displayed total price. No equipment, option, technical or price row is imported by this package.

The next reconciliation package must compare every exact PDF state with canonical configurations and must not transfer evidence across grade, powertrain, transmission, seat-count or phase boundaries.
""")
    write(ROOT / "project/packages/cross-model-configurator-pdf-intake-20260805.md", """# Cross-model Configurator PDF Intake

## Package

- Package ID: `cross_model_configurator_pdf_intake_001`
- Kind: `source_intake`
- Status: complete
- Source date: 2026-08-04

## Scope

Register the 18 user-supplied official Dacia configurator PDF exports for Bigster, Duster, new Jogger, new Sandero F.2 and new Sandero Stepway F.2 as exact saved-state evidence.

## Result

- 18 documents;
- five model families;
- exact SHA-256, byte size, page count and configuration code for every document;
- exact grade, powertrain, fuel, transmission and displayed total price;
- no master-data mutation;
- no propagation between phases or configurations.

## Next package

`cross_model_configurator_data_reconciliation_001` will parse all pages, compare the captured equipment, options, prices and technical values with canonical records, and produce bounded migration candidates and explicit conflicts.
""")
    write(ROOT / "tests/test_cross_model_configurator_pdf_intake_20260805.py", """import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'project/sources/dacia-pl-configurator-cross-model-pdf-bundle-20260804.json'

class CrossModelConfiguratorPdfIntakeTest(unittest.TestCase):
    def test_exact_intake_contract(self):
        data = json.loads(SOURCE.read_text(encoding='utf-8'))
        docs = data['documents']
        self.assertEqual(data['document_count'], 18)
        self.assertEqual(len(docs), 18)
        self.assertEqual(set(data['model_families']), {'bigster','duster','jogger','sandero','sandero_stepway'})
        self.assertEqual(len({d['sha256'] for d in docs}), 18)
        self.assertEqual(len({d['configuration_code'] for d in docs}), 18)
        self.assertTrue(all(len(d['sha256']) == 64 for d in docs))
        self.assertEqual(sum(d['price_pln'] for d in docs), 1626800)
        by_code = {d['configuration_code']: d for d in docs}
        self.assertEqual(by_code['GGQ0LU']['price_pln'], 101400)
        self.assertEqual(by_code['MEOHF3']['price_pln'], 82000)
        self.assertEqual(by_code['I23FGG']['seat_count'], 5)
        self.assertEqual(by_code['4TJTWN']['phase'], 'F.2')
        self.assertEqual(by_code['5WZLHM']['powertrain'], 'Eco-G 120')
        self.assertTrue(data['evidence_boundary']['no_cross_phase_transfer'])

if __name__ == '__main__':
    unittest.main()
""")
    state_path = ROOT / "project/state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["updated_on"] = "2026-08-05"
    state["phase"] = "Cross-model Configurator Data Assimilation"
    state["current_package"] = {
        "package_id": "cross_model_configurator_pdf_intake_001",
        "kind": "source_intake",
        "name": "Cross-model Configurator PDF Intake",
        "status": "complete",
        "goal": "Register 18 exact saved official configurator PDF states with immutable document identity and strict configuration boundaries.",
        "manifest_paths": [
            "data/reporting/cross_model_configurator_pdf_intake.json",
            "data/reporting/cross_model_configurator_pdf_intake.md",
            "project/STATE_SUMMARY.md",
            "project/packages/cross-model-configurator-pdf-intake-20260805.md",
            "project/sources/dacia-pl-configurator-cross-model-pdf-bundle-20260804.json",
            "project/state.json",
            "tests/test_cross_model_configurator_pdf_intake_20260805.py"
        ]
    }
    state["next_package"] = {
        "package_id": "cross_model_configurator_data_reconciliation_001",
        "kind": "source_reconciliation",
        "name": "Cross-model Configurator Data Reconciliation",
        "status": "planned",
        "goal": "Parse all 18 PDFs page by page, map exact states to canonical configurations, compare equipment, options, prices and technical values, and select only non-inferred migration candidates while preserving explicit conflicts and phase boundaries.",
        "manifest_paths": []
    }
    write(state_path, json.dumps(state, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
