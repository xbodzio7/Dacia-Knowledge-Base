from __future__ import annotations
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
