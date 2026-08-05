#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def rep(path,old,new):
 p=ROOT/path;t=p.read_text(encoding='utf-8');n=t.count(old)
 if n!=1: raise RuntimeError(f'{path}: expected 1 match, got {n}')
 p.write_text(t.replace(old,new,1),encoding='utf-8',newline='\n')
def put(path,text):
 p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text.rstrip()+'\n',encoding='utf-8',newline='\n')

MODULE='''from __future__ import annotations
import json, shutil, tempfile
from pathlib import Path, PurePosixPath
from typing import Any
from zipfile import ZipFile
from reporting import portfolio_source_coverage_matrix_release_integration as previous
from reporting.data_product_release_model import CHECKSUMS_NAME, MANIFEST_NAME, ReleaseError, checksum_text, file_record, json_text, safe_member_name, sha256_file, verify_release_assets, write_deterministic_zip, write_text
DIRECTORY="powertrains"
FILES=("portfolio-powertrain-transmission-matrix.json","portfolio-powertrain-transmission-matrix.csv","portfolio-powertrain-transmission-matrix.html")
HTML=f"{DIRECTORY}/{FILES[2]}"
def repository_root(): return previous.repository_root()
def _record(path,root):
 r=file_record(path,root);return {k:r[k] for k in ("path","media_type","size_bytes","sha256")}
def _extract(out,payload):
 m=verify_release_assets(out);a=m.get("archive")
 if not isinstance(a,dict): raise ReleaseError("release archive record is missing")
 ap=out/str(a.get("path",""));safe_member_name(ap.name)
 with ZipFile(ap) as z:
  for i in z.infolist():
   name=safe_member_name(i.filename);target=payload.joinpath(*PurePosixPath(name).parts);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read(i.filename))
 return m
def _copy(repo,payload):
 src=repo/"output"/"portfolio-powertrain-transmission-matrix";dst=payload/DIRECTORY;dst.mkdir(parents=True,exist_ok=True)
 for name in FILES:
  if not (src/name).is_file(): raise ReleaseError(f"verified matrix missing: {src/name}")
  shutil.copyfile(src/name,dst/name)
 matrix=json.loads((dst/FILES[0]).read_text(encoding="utf-8"));summary=matrix.get("summary",{});records=matrix.get("records",[])
 codes=[c for row in records for c in row.get("configuration_codes",[])]
 if matrix.get("matrix_version")!=1 or summary.get("active_configuration_count")!=81 or len(codes)!=81 or len(set(codes))!=81: raise ReleaseError("powertrain matrix coverage differs")
 for key in ("ranking_generated","recommendations_generated","inferred_values_generated"):
  if summary.get(key) is not False: raise ReleaseError(f"matrix boundary differs: {key}")
def create_release_assets(repository:Path,output_directory:Path,version:str,commit_sha:str)->dict[str,Any]:
 previous.create_release_assets(repository,output_directory,version,commit_sha);root=Path(tempfile.mkdtemp(prefix=".powertrain-release-"));payload=root/"payload";payload.mkdir()
 try:
  m=_extract(output_directory,payload);_copy(repository,payload);a=m["archive"];ap=output_directory/str(a["path"]);m["files"]=write_deterministic_zip(payload,ap);m["portfolio_powertrain_transmission_matrix_generated"]=True;m["portfolio_powertrain_transmission_matrix_formats"]=["JSON","CSV","HTML"];m["portfolio_powertrain_transmission_matrix_directory"]=DIRECTORY;m["archive"]=_record(ap,output_directory);mp=output_directory/MANIFEST_NAME;write_text(mp,json_text(m));write_text(output_directory/CHECKSUMS_NAME,checksum_text({ap.name:sha256_file(ap),mp.name:sha256_file(mp)}));v=verify_release_assets(output_directory)
  if v!=m: raise ReleaseError("powertrain-integrated manifest changed after verification")
  return m
 finally: shutil.rmtree(root,ignore_errors=True)
'''
TEST='''from __future__ import annotations
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
   self.assertEqual(matrix["summary"]["active_configuration_count"],81);self.assertEqual(verify_release_assets(out),m)
 def test_entry_point_contract(self):
  from reporting.data_product_release_download import OPTIONAL_ENTRY_POINTS
  from reporting.data_product_workspace_index import POWERTRAIN_MATRIX_HTML_MEMBER
  self.assertEqual(OPTIONAL_ENTRY_POINTS["powertrain_transmission_matrix_html"],HTML);self.assertEqual(POWERTRAIN_MATRIX_HTML_MEMBER,HTML)
'''
put('tools/reporting/portfolio_powertrain_transmission_matrix_release_integration.py',MODULE)
put('tests/test_portfolio_powertrain_transmission_matrix_release_integration.py',TEST)
rep('tools/data_product_release.py','from reporting.portfolio_source_coverage_matrix_release_integration import (\n    create_release_assets,\n    repository_root,\n)','from reporting.portfolio_powertrain_transmission_matrix_release_integration import (\n    create_release_assets,\n    repository_root,\n)')
rep('tools/reporting/data_product_release_download.py','SOURCE_COVERAGE_HTML_MEMBER = (\n    "source-coverage/portfolio_source_coverage_matrix.html"\n)\n','SOURCE_COVERAGE_HTML_MEMBER = (\n    "source-coverage/portfolio_source_coverage_matrix.html"\n)\nPOWERTRAIN_MATRIX_HTML_MEMBER = (\n    "powertrains/portfolio-powertrain-transmission-matrix.html"\n)\n')
rep('tools/reporting/data_product_release_download.py','    "source_coverage_matrix_html": SOURCE_COVERAGE_HTML_MEMBER,\n}','    "source_coverage_matrix_html": SOURCE_COVERAGE_HTML_MEMBER,\n    "powertrain_transmission_matrix_html": POWERTRAIN_MATRIX_HTML_MEMBER,\n}')
rep('tools/data_product_release_download.py','        "source_coverage_matrix_html": "Source coverage matrix",\n','        "source_coverage_matrix_html": "Source coverage matrix",\n        "powertrain_transmission_matrix_html": "Powertrain and transmission matrix",\n')
rep('tools/data_product_release_download.py','    if "source_coverage_matrix_html" in raw_entry_points:\n        keys.append("source_coverage_matrix_html")\n','    if "source_coverage_matrix_html" in raw_entry_points:\n        keys.append("source_coverage_matrix_html")\n    if "powertrain_transmission_matrix_html" in raw_entry_points:\n        keys.append("powertrain_transmission_matrix_html")\n')
rep('tools/reporting/data_product_workspace_index.py','SOURCE_COVERAGE_MATRIX_HTML_MEMBER = (\n    "source-coverage/portfolio_source_coverage_matrix.html"\n)\n','SOURCE_COVERAGE_MATRIX_HTML_MEMBER = (\n    "source-coverage/portfolio_source_coverage_matrix.html"\n)\nPOWERTRAIN_MATRIX_HTML_MEMBER = (\n    "powertrains/portfolio-powertrain-transmission-matrix.html"\n)\n')
card='''\n\ndef _with_powertrain_matrix_card(content: str, workspace_root: Path, release_manifest: Any) -> str:\n    return _with_optional_card(content,workspace_root,release_manifest,member=POWERTRAIN_MATRIX_HTML_MEMBER,heading_id="powertrain-transmission-matrix-heading",title="Powertrain and transmission matrix",description="Browse exact recorded powertrain and transmission groups across all active configurations.",missing_label="portfolio powertrain and transmission matrix HTML")\n'''
rep('tools/reporting/data_product_workspace_index.py','\n\ndef render_workspace_index(\n',card+'\n\ndef render_workspace_index(\n')
rep('tools/reporting/data_product_workspace_index.py','    return _with_source_coverage_matrix_card(\n        content,\n        workspace_root,\n        release_manifest,\n    )\n','    content = _with_source_coverage_matrix_card(content, workspace_root, release_manifest)\n    return _with_powertrain_matrix_card(content, workspace_root, release_manifest)\n')
put('project/packages/portfolio-powertrain-transmission-matrix-release-integration-20260805.md','# Portfolio Powertrain and Transmission Matrix Release Integration\n\n- Package ID: `portfolio_powertrain_transmission_matrix_release_integration_001`\n- Status: complete\n\nThe verified JSON, CSV and standalone HTML matrix is copied byte for byte into `powertrains/`. The manifest, downloader, CLI and offline workspace expose the optional product while older releases remain valid. No master data, matrix semantics, ranking, recommendation or inferred value changes.')
s=ROOT/'project/state.json';state=json.loads(s.read_text(encoding='utf-8'));state['updated_on']='2026-08-05';state['phase']='Portfolio Powertrain and Transmission Matrix Release Integration';state['baseline']['tests']+=2;state['current_package']={'package_id':'portfolio_powertrain_transmission_matrix_release_integration_001','kind':'release_integration','name':'Portfolio Powertrain and Transmission Matrix Release Integration','status':'complete','goal':'Integrate the verified matrix into the versioned archive, manifest, download surface and offline workspace without changing semantics or master data.','manifest_paths':['project/STATE_SUMMARY.md','project/packages/portfolio-powertrain-transmission-matrix-release-integration-20260805.md','project/state.json','tests/test_portfolio_powertrain_transmission_matrix_release_integration.py','tools/data_product_release.py','tools/data_product_release_download.py','tools/reporting/data_product_release_download.py','tools/reporting/data_product_workspace_index.py','tools/reporting/portfolio_powertrain_transmission_matrix_release_integration.py']};state['next_package']={'package_id':'data_products_v1_16_0_release_preparation_001','kind':'release_preparation','name':'Data Products v1.16.0 Release Preparation','status':'planned','goal':'Prepare an immutable minor release from the verified powertrain-matrix integration state with exact-source double build and offline workspace verification.','manifest_paths':[]};s.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')