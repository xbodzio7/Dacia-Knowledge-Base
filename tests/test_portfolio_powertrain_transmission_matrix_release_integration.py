from __future__ import annotations
import json,sys,tempfile,unittest
from pathlib import Path
from zipfile import ZipFile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
from reporting.portfolio_powertrain_transmission_matrix_release_integration import FILES,HTML,create_release_assets
from reporting.data_product_release_model import verify_release_assets
class PowertrainMatrixReleaseIntegrationTests(unittest.TestCase):
 def test_archive_and_manifest(self):
  with tempfile.TemporaryDirectory() as d:
   out=Path(d);m=create_release_assets(ROOT,out,"1.16.0","1"*40);self.assertTrue(m["portfolio_powertrain_transmission_matrix_generated"]);self.assertEqual(m["portfolio_powertrain_transmission_matrix_directory"],"powertrains")
   with ZipFile(out/str(m["archive"]["path"])) as z:
    for n in FILES:self.assertEqual(z.read(f"powertrains/{n}"),(ROOT/"output"/"portfolio-powertrain-transmission-matrix"/n).read_bytes())
    matrix=json.loads(z.read(f"powertrains/{FILES[0]}").decode())
   self.assertEqual(matrix["summary"]["active_configuration_count"],84);self.assertEqual(verify_release_assets(out),m)
 def test_entry_point_contract(self):
  from reporting.data_product_release_download import OPTIONAL_ENTRY_POINTS
  from reporting.data_product_workspace_index import POWERTRAIN_MATRIX_HTML_MEMBER
  self.assertEqual(OPTIONAL_ENTRY_POINTS["powertrain_transmission_matrix_html"],HTML);self.assertEqual(POWERTRAIN_MATRIX_HTML_MEMBER,HTML)
