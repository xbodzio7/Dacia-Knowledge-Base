#!/usr/bin/env python3
"""Import and verify the Jogger MY26 2026-11-02 special non-metallic paint mappings."""
from __future__ import annotations
import argparse, csv, hashlib, json, os, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MASTER=ROOT/"data"/"master"
IMPORTS=ROOT/"data"/"imports"
SOURCE="src_pl_jogger_price_my26_20261102"
SOURCE_DATE="2026-11-02"
SOURCE_URL="https://cdn.group.renault.com/dac/pl/pdf/cenniki/jogger-price.pdf.asset.pdf/d0a86dff46.pdf"
SOURCE_PATH="PDF/Cenniki/DACIA JOGGER cennik MY26 20261102.pdf"
SOURCE_SHA256="94324e97d00e825ed537b525052dacfc436b57984880585e087852411b65a5da"
MANIFEST_PATH=ROOT/"data"/"source_intake"/"jogger_my26_20261102_capture.json"
MAP_SPEC=IMPORTS/"jogger_commercial_item_configurations_20261102.csv"
FIELDS=("id","code","commercial_item_code","configuration_code","availability_status","amount","currency_code","price_date","source_code","notes")
SPEC_FIELDS=("code","commercial_item_code","configuration_code","availability_status","amount","currency_code","price_date","source_code","source_page","source_label","notes")
CONFIGURATIONS=["jogger_essential_5seat_ecog120_manual","jogger_essential_7seat_ecog120_manual","jogger_expression_5seat_ecog120_manual","jogger_expression_5seat_hybrid155_automatic","jogger_expression_7seat_ecog120_manual","jogger_expression_7seat_hybrid155_automatic","jogger_extreme_5seat_ecog120_manual","jogger_extreme_5seat_ecog120_automatic","jogger_extreme_5seat_hybrid155_automatic","jogger_extreme_7seat_ecog120_manual","jogger_extreme_7seat_ecog120_automatic","jogger_extreme_7seat_hybrid155_automatic"]
ITEM="jogger_special_nonmetallic_paint_option"
class ContractError(RuntimeError): pass
def read_csv(path:Path)->list[dict[str,str]]:
    with path.open("r",encoding="utf-8-sig",newline="") as h:return list(csv.DictReader(h))
def read_spec()->list[dict[str,str]]:
    with MAP_SPEC.open("r",encoding="utf-8-sig",newline="") as h:
        r=csv.DictReader(h)
        if tuple(r.fieldnames or ())!=SPEC_FIELDS:raise ContractError("commercial mapping specification header mismatch")
        return list(r)
def write_csv(path:Path,fields:tuple[str,...],rows:list[dict[str,str]])->None:
    fd,tmp=tempfile.mkstemp(prefix=f".{path.name}.",dir=path.parent)
    try:
        with os.fdopen(fd,"w",encoding="utf-8",newline="") as h:
            w=csv.DictWriter(h,fieldnames=fields,lineterminator="\\n");w.writeheader();w.writerows(rows)
        os.replace(tmp,path)
    except Exception:
        try:os.unlink(tmp)
        except OSError:pass
        raise
def sha256(path:Path)->str:
    d=hashlib.sha256()
    with path.open("rb") as h:
        for block in iter(lambda:h.read(1024*1024),b""):d.update(block)
    return d.hexdigest()
def expected_spec()->list[dict[str,str]]:
    return [{"code":f"{ITEM}__{c}__20261102","commercial_item_code":ITEM,"configuration_code":c,"availability_status":"optional","amount":"2800","currency_code":"PLN","price_date":SOURCE_DATE,"source_code":SOURCE,"source_page":"3","source_label":"Lakier niemetalizowany / niemetalizowany specjalny","notes":"The 2,800 PLN cell is the special non-metallic finish; no named colour is inferred."} for c in sorted(CONFIGURATIONS)]
def verify_source()->None:
    sources={r["code"]:r for r in read_csv(MASTER/"sources.csv")}
    s=sources.get(SOURCE)
    expected={"document_date":SOURCE_DATE,"external_reference":SOURCE_URL,"file_path":SOURCE_PATH,"sha256":SOURCE_SHA256,"status":"active"}
    if s is None or any(s.get(k)!=v for k,v in expected.items()):raise ContractError("registered Jogger source identity mismatch")
    f=ROOT/SOURCE_PATH
    if not f.is_file() or sha256(f)!=SOURCE_SHA256:raise ContractError("archived Jogger PDF missing or SHA-256 mismatch")
    m=json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    expected_m={"source_code":SOURCE,"document_date":SOURCE_DATE,"source_url":SOURCE_URL,"file_path":SOURCE_PATH,"sha256":SOURCE_SHA256,"expected_sha256":SOURCE_SHA256,"file_size_bytes":2119710,"expected_file_size_bytes":2119710,"page_count":9,"expected_page_count":9,"verification_status":"verified_my26"}
    if any(m.get(k)!=v for k,v in expected_m.items()) or m.get("missing_markers")!=[]:raise ContractError("capture manifest/source registry mismatch")
    links=[r for r in read_csv(MASTER/"source_configurations.csv") if r["source_code"]==SOURCE]
    if len(links)!=12 or {r["configuration_code"] for r in links}!=set(CONFIGURATIONS) or any(r["relationship"]!="documents" for r in links):raise ContractError("new source must link exactly 12 configurations")
    grades=[r for r in read_csv(MASTER/"source_versions.csv") if r["source_code"]==SOURCE]
    if len(grades)!=3 or {r["version_code"] for r in grades}!={"jogger_essential","jogger_expression","jogger_extreme"}:raise ContractError("new source must link exactly three grades")
    if [r for r in read_csv(MASTER/"configuration_prices.csv") if r["source_code"]==SOURCE]:raise ContractError("unchanged catalogue prices must not be duplicated")
def check()->dict[str,int]:
    verify_source()
    spec=read_spec();expected=expected_spec()
    if sorted(spec,key=lambda r:r["code"])!=sorted(expected,key=lambda r:r["code"]) or len(spec)!=12:raise ContractError("2026-11-02 commercial spec differs from page-3 evidence")
    rows=read_csv(MASTER/"commercial_item_configurations.csv")
    actual=[r for r in rows if r["source_code"]==SOURCE]
    want=[{"id":str(905+i),"code":r["code"],"commercial_item_code":r["commercial_item_code"],"configuration_code":r["configuration_code"],"availability_status":r["availability_status"],"amount":r["amount"],"currency_code":r["currency_code"],"price_date":r["price_date"],"source_code":r["source_code"],"notes":f"Printed page 3; source row: {r['source_label']}. {r['notes']}"} for i,r in enumerate(sorted(expected,key=lambda x:x["code"]))]
    if actual!=want:raise ContractError("2026-11-02 master mappings differ from import specification")
    old=[r for r in rows if r["source_code"]=="src_pl_jogger_price_my26_20261001"]
    oldpaint=[r for r in old if r["commercial_item_code"]==ITEM]
    if len(old)!=54 or len(oldpaint)!=12 or {r["amount"] for r in oldpaint}!={"2700"}:raise ContractError("historical 2026-10-01 special non-metallic paint mappings must match the visually reverified 2,700 PLN source row")
    if len([r for r in read_csv(MASTER/"commercial_items.csv") if r["code"]==ITEM])!=1:raise ContractError("existing special non-metallic item must be reused")
    if any(r["code"]=="jogger_metallic_paint_option" for r in read_csv(MASTER/"commercial_items.csv")):raise ContractError("do not create an unsupported metallic-paint item")
    if len({r["id"] for r in rows})!=len(rows) or len({r["code"] for r in rows})!=len(rows):raise ContractError("commercial mapping IDs/codes must be unique")
    return {"new_mappings":12,"optional":12,"not_available":0,"catalogue_price_rows":0}
def apply()->dict[str,int]:
    verify_source();spec=read_spec();path=MASTER/"commercial_item_configurations.csv";rows=read_csv(path)
    if any(r["source_code"]==SOURCE for r in rows):raise ContractError("2026-11-02 mappings already exist")
    if max(int(r["id"]) for r in rows)!=904:raise ContractError("expected pre-import mapping baseline ending at ID 904")
    new=[{"id":str(905+i),"code":r["code"],"commercial_item_code":r["commercial_item_code"],"configuration_code":r["configuration_code"],"availability_status":r["availability_status"],"amount":r["amount"],"currency_code":r["currency_code"],"price_date":r["price_date"],"source_code":r["source_code"],"notes":f"Printed page 3; source row: {r['source_label']}. {r['notes']}"} for i,r in enumerate(sorted(spec,key=lambda x:x["code"]))]
    write_csv(path,FIELDS,rows+new);return check()
def main()->int:
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group();g.add_argument("--apply",action="store_true");g.add_argument("--check",action="store_true");a=p.parse_args()
    try:result=apply() if a.apply else check()
    except (ContractError,OSError,KeyError,ValueError) as e:p.error(str(e))
    print("Jogger MY26 2026-11-02 paint mapping OK:",result);return 0
if __name__=="__main__":raise SystemExit(main())
