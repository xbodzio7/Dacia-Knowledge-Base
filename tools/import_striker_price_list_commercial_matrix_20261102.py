#!/usr/bin/env python3
"""Verify and import the official Striker MY26 2026-11-02 option/package matrix."""
from __future__ import annotations
import argparse,csv,hashlib,json,os,tempfile
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];MASTER=ROOT/"data"/"master";IMPORTS=ROOT/"data"/"imports"
SOURCE="src_pl_striker_price_my26_20261102";SOURCE_DATE="2026-11-02";SOURCE_URL="https://cdn.group.renault.com/dac/pl/pdf/cenniki/striker-price.pdf.asset.pdf/1793603979544.pdf";SOURCE_PATH="PDF/Cenniki/striker-price.pdf";SOURCE_SHA256="d9e1e874ceaf2b65faf37650ad7be4b9a7c9710ee1d09cbdee5856c286e62d35";SOURCE_SIZE=1615585;SOURCE_PAGES=8
ITEM_SPEC=IMPORTS/"striker_commercial_items_20261102.csv";MAP_SPEC=IMPORTS/"striker_commercial_item_configurations_20261102.csv"
ITEM_FIELDS=("id","code","name","item_type","observation_date","source_code","status","notes")
MAP_FIELDS=("id","code","commercial_item_code","configuration_code","availability_status","amount","currency_code","price_date","source_code","notes")
ITEM_SPEC_FIELDS=ITEM_FIELDS[1:];MAP_SPEC_FIELDS=("code","commercial_item_code","configuration_code","availability_status","amount","currency_code","price_date","source_code","source_page","source_label","notes")
EXPECTED_CONFIGS={"striker_essential_mildhybridg140_4x2_manual":"essential","striker_expression_mildhybridg140_4x2_manual":"expression","striker_expression_mildhybridg140_4x2_automatic":"expression","striker_extreme_mildhybridg140_4x2_automatic":"extreme","striker_journey_mildhybridg140_4x2_automatic":"journey","striker_expression_hybrid155_4x2_automatic":"expression","striker_extreme_hybrid155_4x2_automatic":"extreme","striker_journey_hybrid155_4x2_automatic":"journey","striker_expression_hybrid150_4x4_automatic":"expression","striker_extreme_hybrid150_4x4_automatic":"extreme","striker_journey_hybrid150_4x4_automatic":"journey"}
EXPECTED_COUNTS={"optional":60,"standard":3,"not_available":51,"package":7}
class ContractError(RuntimeError):pass
def read(path):
 with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def read_spec(path,fields):
 with path.open(encoding="utf-8-sig",newline="") as f:
  r=csv.DictReader(f)
  if tuple(r.fieldnames or ())!=tuple(fields):raise ContractError(f"CSV header mismatch: {path}")
  return list(r)
def write(path,fields,rows):
 fd,tmp=tempfile.mkstemp(prefix=f".{path.name}.",dir=path.parent)
 try:
  with os.fdopen(fd,"w",encoding="utf-8",newline="") as f:
   w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(rows)
  os.replace(tmp,path)
 except Exception:
  try:os.unlink(tmp)
  except OSError:pass
  raise
def file_hash(path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
 return h.hexdigest()
def verify_source():
 ss=[r for r in read(MASTER/"sources.csv") if r["code"]==SOURCE]
 if len(ss)!=1:raise ContractError("source registry must contain exactly one Striker source")
 s=ss[0]
 if (s["document_date"],s["market"],s["external_reference"],s["file_path"],s["sha256"],s["status"])!=(SOURCE_DATE,"PL",SOURCE_URL,SOURCE_PATH,SOURCE_SHA256,"active"):raise ContractError("registered source identity mismatch")
 manifest=json.loads((ROOT/"data/source_intake/striker_my26_20261102_capture.json").read_text(encoding="utf-8"))
 expected={"source_code":SOURCE,"source_url":SOURCE_URL,"file_path":SOURCE_PATH,"sha256":SOURCE_SHA256,"expected_sha256":SOURCE_SHA256,"file_size_bytes":SOURCE_SIZE,"expected_file_size_bytes":SOURCE_SIZE,"page_count":SOURCE_PAGES,"expected_page_count":SOURCE_PAGES,"verification_status":"verified_my26","missing_markers":[]}
 if any(manifest.get(k)!=v for k,v in expected.items()):raise ContractError("capture manifest mismatch")
 side=(ROOT/"data/source_intake/striker_my26_20261102.sha256").read_text(encoding="utf-8").strip().split(maxsplit=1)
 if side!=[SOURCE_SHA256,SOURCE_PATH]:raise ContractError("SHA-256 sidecar mismatch")
 rel=Path(SOURCE_PATH)
 if rel.is_absolute() or ".." in rel.parts:raise ContractError("unsafe source path")
 archive=(ROOT/rel).resolve()
 try:archive.relative_to(ROOT.resolve())
 except ValueError as e:raise ContractError("source archive escapes repository") from e
 if rel.is_symlink() or not archive.is_file():raise ContractError("archived PDF missing or symlink")
 if archive.stat().st_size!=SOURCE_SIZE or file_hash(archive)!=SOURCE_SHA256:raise ContractError("archived PDF size/hash mismatch")
 links=[r for r in read(MASTER/"source_configurations.csv") if r["source_code"]==SOURCE]
 if len(links)!=11 or {r["configuration_code"] for r in links}!=set(EXPECTED_CONFIGS) or any(r["relationship"]!="documents" for r in links):raise ContractError("source configuration links mismatch")
 grades=[r for r in read(MASTER/"source_versions.csv") if r["source_code"]==SOURCE]
 if len(grades)!=4 or {r["version_code"] for r in grades}!={"striker_essential","striker_expression","striker_extreme","striker_journey"}:raise ContractError("source grade links mismatch")
 prices=[r for r in read(MASTER/"configuration_prices.csv") if r["source_code"]==SOURCE and r["price_date"]==SOURCE_DATE]
 if len(prices)!=11 or {r["configuration_code"] for r in prices}!=set(EXPECTED_CONFIGS):raise ContractError("catalogue price scope mismatch")
def load_specs():
 items=read_spec(ITEM_SPEC,ITEM_SPEC_FIELDS);maps=read_spec(MAP_SPEC,MAP_SPEC_FIELDS)
 if len(items)!=11 or len({r["code"] for r in items})!=11:raise ContractError("expected 11 commercial items")
 if len(maps)!=121 or len({r["code"] for r in maps})!=121:raise ContractError("expected 121 mappings")
 if {r["code"] for r in items}!={r["commercial_item_code"] for r in maps}:raise ContractError("item/mapping specs differ")
 if {r["configuration_code"] for r in maps}!=set(EXPECTED_CONFIGS):raise ContractError("configuration scope mismatch")
 if Counter(r["availability_status"] for r in maps)!=Counter(EXPECTED_COUNTS):raise ContractError("status distribution mismatch")
 if any(r["source_code"]!=SOURCE or r["observation_date"]!=SOURCE_DATE or r["item_type"] not in {"option","package"} or r["status"]!="active" for r in items):raise ContractError("item provenance mismatch")
 if any(r["source_code"]!=SOURCE or r["price_date"]!=SOURCE_DATE or r["source_page"]!="5" or r["currency_code"]!="PLN" or not r["source_label"] for r in maps):raise ContractError("mapping provenance mismatch")
 for r in maps:
  if r["availability_status"]=="optional" and (not r["amount"].isdigit() or int(r["amount"])<=0):raise ContractError("optional mapping needs positive price")
  if r["availability_status"]!="optional" and r["amount"]:raise ContractError("non-optional mapping must not carry amount")
  if r["availability_status"]=="package" and "literal marker P" not in r["notes"]:raise ContractError("package mapping must preserve P")
 return items,maps
def expected_rows(si,sm):
 ni=[{"id":str(65+i),**r} for i,r in enumerate(si)]
 nm=[{"id":str(917+i),"code":r["code"],"commercial_item_code":r["commercial_item_code"],"configuration_code":r["configuration_code"],"availability_status":r["availability_status"],"amount":r["amount"],"currency_code":r["currency_code"],"price_date":r["price_date"],"source_code":r["source_code"],"notes":f"Printed page {r['source_page']}; source row: {r['source_label']}. {r['notes']}"} for i,r in enumerate(sm)]
 return ni,nm
def check():
 verify_source();si,sm=load_specs();ei,em=expected_rows(si,sm);items=read(MASTER/"commercial_items.csv");maps=read(MASTER/"commercial_item_configurations.csv")
 item_ids=[int(r["id"]) for r in items];mapping_ids=[int(r["id"]) for r in maps]
 if len(item_ids)!=len(set(item_ids)) or any(v<1 for v in item_ids):raise ContractError("commercial item IDs must be unique positive integers")
 if len(mapping_ids)!=len(set(mapping_ids)) or any(v<1 for v in mapping_ids):raise ContractError("commercial mapping IDs must be unique positive integers")
 if len({r["code"] for r in items})!=len(items):raise ContractError("duplicate commercial item code")
 if [r for r in items if r["code"] in {x["code"] for x in ei}]!=ei:raise ContractError("Striker items differ from spec")
 sr=[r for r in maps if r["source_code"]==SOURCE]
 if sr!=em:raise ContractError("Striker mappings differ from spec")
 if len({r["code"] for r in maps})!=len(maps):raise ContractError("duplicate mapping code")
 source_keys=[(r["commercial_item_code"],r["configuration_code"],r["source_code"],r["price_date"]) for r in sr]
 if len(set(source_keys))!=len(source_keys):raise ContractError("duplicate Striker source natural key")
 return {"new_items":11,"new_mappings":121,**EXPECTED_COUNTS}
def apply():
 verify_source();si,sm=load_specs();ip=MASTER/"commercial_items.csv";mp=MASTER/"commercial_item_configurations.csv";items=read(ip);maps=read(mp)
 if len(items)!=64 or len(maps)!=916:raise ContractError("apply requires exact pre-import baseline: 64 items/916 mappings")
 if {r["id"] for r in items}!={str(i) for i in range(1,65)} or {r["id"] for r in maps}!={str(i) for i in range(1,917)}:raise ContractError("pre-import IDs must be contiguous")
 ni,nm=expected_rows(si,sm)
 if {r["code"] for r in items}&{r["code"] for r in ni} or {r["code"] for r in maps}&{r["code"] for r in nm}:raise ContractError("new item/mapping already exists")
 write(ip,ITEM_FIELDS,items+ni);write(mp,MAP_FIELDS,maps+nm);return check()
def main():
 p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group();g.add_argument("--apply",action="store_true");g.add_argument("--check",action="store_true");a=p.parse_args()
 try:r=apply() if a.apply else check()
 except (ContractError,OSError,KeyError,ValueError) as e:p.error(str(e))
 print("Striker MY26 commercial matrix OK: "+", ".join(f"{k}={v}" for k,v in r.items()))
if __name__=="__main__":main()
