#!/usr/bin/env python3
"""Import and verify the official Jogger MY26 2026-10-01 commercial matrix."""
from __future__ import annotations
import argparse, csv, hashlib, os, tempfile
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MASTER=ROOT/"data"/"master"
IMPORTS=ROOT/"data"/"imports"
SOURCE="src_pl_jogger_price_my26_20261001"
SOURCE_DATE="2026-10-01"
SOURCE_URL="https://cdn.group.renault.com/dac/pl/pdf/cenniki/jogger-price.pdf.asset.pdf/f5cdbd7878.pdf"
SOURCE_PATH="owner_supplied/2026-10-01/f5cdbd7878.pdf"
SOURCE_SHA256="12e536c1e60e9e7f91228b27a9d962cecacb5a5287d585f419a14af3003e8b46"
ITEM_SPEC=IMPORTS/"jogger_commercial_items_20261001.csv"
MAP_SPEC=IMPORTS/"jogger_commercial_item_configurations_20261001.csv"
ITEM_FIELDS=("id","code","name","item_type","observation_date","source_code","status","notes")
MAP_FIELDS=("id","code","commercial_item_code","configuration_code","availability_status","amount","currency_code","price_date","source_code","notes")
ITEM_SPEC_FIELDS=ITEM_FIELDS[1:]
MAP_SPEC_FIELDS=("code","commercial_item_code","configuration_code","availability_status","amount","currency_code","price_date","source_code","source_page","source_label","notes")
EXPECTED_CONFIGS=["jogger_essential_5seat_ecog120_manual","jogger_essential_7seat_ecog120_manual","jogger_expression_5seat_ecog120_manual","jogger_expression_5seat_hybrid155_automatic","jogger_expression_7seat_ecog120_manual","jogger_expression_7seat_hybrid155_automatic","jogger_extreme_5seat_ecog120_manual","jogger_extreme_5seat_ecog120_automatic","jogger_extreme_5seat_hybrid155_automatic","jogger_extreme_7seat_ecog120_manual","jogger_extreme_7seat_ecog120_automatic","jogger_extreme_7seat_hybrid155_automatic"]
ESSENTIAL=["jogger_essential_5seat_ecog120_manual","jogger_essential_7seat_ecog120_manual"]
EXPRESSION=["jogger_expression_5seat_ecog120_manual","jogger_expression_5seat_hybrid155_automatic","jogger_expression_7seat_ecog120_manual","jogger_expression_7seat_hybrid155_automatic"]
EXTREME=["jogger_extreme_5seat_ecog120_manual","jogger_extreme_5seat_ecog120_automatic","jogger_extreme_5seat_hybrid155_automatic","jogger_extreme_7seat_ecog120_manual","jogger_extreme_7seat_ecog120_automatic","jogger_extreme_7seat_hybrid155_automatic"]
EXPECTED_COUNTS={"jogger_special_nonmetallic_paint_option":12,"jogger_media_nav_option":12,"jogger_heated_front_seats_option":6,"jogger_winter_package":12,"jogger_drive_package":12}
class ContractError(RuntimeError): pass
def read(path):
    with path.open(encoding="utf-8-sig",newline="") as handle:
        reader=csv.DictReader(handle)
        if reader.fieldnames is None: raise ContractError(f"missing CSV header: {path}")
        return list(reader)
def read_spec(path,fields):
    with path.open(encoding="utf-8-sig",newline="") as handle:
        reader=csv.DictReader(handle)
        if tuple(reader.fieldnames or ())!=fields: raise ContractError(f"CSV header mismatch: {path}")
        return list(reader)
def write(path,fields,rows):
    fd,tmp=tempfile.mkstemp(prefix=f".{path.name}.",dir=path.parent)
    try:
        with os.fdopen(fd,"w",encoding="utf-8",newline="") as handle:
            writer=csv.DictWriter(handle,fieldnames=fields,lineterminator="\n")
            writer.writeheader();writer.writerows(rows)
        os.replace(tmp,path)
    except Exception:
        try: os.unlink(tmp)
        except OSError: pass
        raise
def file_hash(path):
    digest=hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda:handle.read(1024*1024),b""):digest.update(block)
    return digest.hexdigest()
def verify_source():
    sources={r["code"]:r for r in read(MASTER/"sources.csv")}
    if SOURCE not in sources: raise ContractError("Jogger source is not registered")
    source=sources[SOURCE]
    if (source["document_date"]!=SOURCE_DATE or source["external_reference"]!=SOURCE_URL
        or source["file_path"]!=SOURCE_PATH or source["sha256"]!=SOURCE_SHA256):
        raise ContractError("registered source identity, URL, path or SHA-256 mismatch")
    source_file=ROOT/SOURCE_PATH
    if not source_file.is_file() or file_hash(source_file)!=SOURCE_SHA256:
        raise ContractError("archived source PDF is missing or its SHA-256 differs")
    links=[r for r in read(MASTER/"source_configurations.csv") if r["source_code"]==SOURCE]
    if len(links)!=12 or {r["configuration_code"] for r in links}!=set(EXPECTED_CONFIGS):
        raise ContractError("source must link exactly the 12 printed configurations")
    if any(r["relationship"]!="documents" for r in links): raise ContractError("unexpected source relationship type")
    grades=[r for r in read(MASTER/"source_versions.csv") if r["source_code"]==SOURCE]
    if len(grades)!=3 or {r["version_code"] for r in grades}!={"jogger_essential","jogger_expression","jogger_extreme"}:
        raise ContractError("source must link exactly three grade columns")
    prices=[r for r in read(MASTER/"configuration_prices.csv") if r["source_code"]==SOURCE and r["price_date"]==SOURCE_DATE]
    if len(prices)!=11 or len({r["configuration_code"] for r in prices})!=11:
        raise ContractError("source price matrix must retain exactly 11 priced cells")
    if "jogger_essential_7seat_ecog120_manual" in {r["configuration_code"] for r in prices}:
        raise ContractError("7-seat Essential Eco-G 120 dash must not have a price row")
    return set(EXPECTED_CONFIGS)
def expected_matrix():
    rows=[]
    def add(item,configs,status,amount,page,label,note):
        for config in sorted(configs):
            rows.append({"code":f"{item}__{config}__20261001","commercial_item_code":item,
                "configuration_code":config,"availability_status":status,"amount":amount if status=="optional" else "",
                "currency_code":"PLN","price_date":SOURCE_DATE,"source_code":SOURCE,
                "source_page":str(page),"source_label":label,"notes":note})
    all_configs=set(EXPECTED_CONFIGS);essential=set(ESSENTIAL);expression=set(EXPRESSION);extreme=set(EXTREME)
    add("jogger_special_nonmetallic_paint_option",all_configs,"optional","2800",3,
        "Lakier niemetalizowany / niemetalizowany specjalny","The 2,800 PLN cell is the special non-metallic finish; no named colour is inferred.")
    add("jogger_media_nav_option",essential,"not_available","",4,"Nowy Media Nav","The printed cell is a dash (-), explicitly unavailable for this configuration.")
    add("jogger_media_nav_option",expression|extreme,"optional","1600",4,"Nowy Media Nav","Optional equipment at the printed 1,600 PLN price.")
    add("jogger_heated_front_seats_option",essential,"not_available","",4,"Przednie fotele podgrzewane","The printed cell is a dash (-), explicitly unavailable for this configuration.")
    add("jogger_heated_front_seats_option",expression,"optional","700",4,"Przednie fotele podgrzewane","Optional equipment at the printed 700 PLN price.")
    add("jogger_winter_package",essential|expression,"not_available","",4,"Pakiet ZIMOWY","The printed cell is a dash (-), explicitly unavailable for this configuration.")
    add("jogger_winter_package",extreme,"optional","1200",4,"Pakiet ZIMOWY","Optional package at the printed 1,200 PLN price.")
    add("jogger_drive_package",essential|expression,"not_available","",4,"Pakiet DRIVE","The printed cell is a dash (-), explicitly unavailable for this configuration.")
    add("jogger_drive_package",extreme,"optional","1400",4,"Pakiet DRIVE","Optional package at the printed 1,400 PLN price.")
    return rows
def load_specs(configurations):
    items=read_spec(ITEM_SPEC,ITEM_SPEC_FIELDS)
    expected_item={"code":"jogger_special_nonmetallic_paint_option","name":"Lakier niemetalizowany specjalny",
        "item_type":"option","observation_date":SOURCE_DATE,"source_code":SOURCE,"status":"active",
        "notes":"Official Polish Jogger MY26 cennik, printed page 3; special non-metallic paint is priced at 2,800 PLN. The source does not assign named colours."}
    if items!=[expected_item]: raise ContractError("new commercial item differs from reviewed source contract")
    rows=read_spec(MAP_SPEC,MAP_SPEC_FIELDS)
    if len(rows)!=54 or len({r["code"] for r in rows})!=54: raise ContractError("expected 54 unique mapping specification rows")
    if sorted(rows,key=lambda r:r["code"])!=sorted(expected_matrix(),key=lambda r:r["code"]):
        raise ContractError("mapping specification differs from exact reviewed matrix")
    if {r["configuration_code"] for r in rows}-configurations: raise ContractError("mapping references configuration outside source")
    if dict(Counter(r["commercial_item_code"] for r in rows))!=EXPECTED_COUNTS:
        raise ContractError("commercial item distribution differs from reviewed matrix")
    if Counter(r["availability_status"] for r in rows)!=Counter({"optional":38,"not_available":16}):
        raise ContractError("expected 38 optional and 16 not_available cells")
    return items,rows
def expected_master_rows(item_spec,map_spec):
    items=[{"id":"64",**r} for r in item_spec]
    maps=[]
    for i,r in enumerate(sorted(map_spec,key=lambda x:x["code"]),start=841):
        maps.append({"id":str(i),"code":r["code"],"commercial_item_code":r["commercial_item_code"],
            "configuration_code":r["configuration_code"],"availability_status":r["availability_status"],
            "amount":r["amount"],"currency_code":r["currency_code"],"price_date":r["price_date"],
            "source_code":r["source_code"],
            "notes":f"Printed page {r['source_page']}; source row: {r['source_label']}. {r['notes']}"})
    return items,maps
def check():
    configurations=verify_source();item_spec,map_spec=load_specs(configurations)
    expected_items,expected_maps=expected_master_rows(item_spec,map_spec)
    items=read(MASTER/"commercial_items.csv");maps=read(MASTER/"commercial_item_configurations.csv")
    if len(items)!=64: raise ContractError("master commercial item count must equal 64")
    if len({r["id"] for r in items})!=len(items) or {r["id"] for r in items}!={str(i) for i in range(1,65)}:
        raise ContractError("master commercial item IDs must be unique and contiguous 1–64")
    if [r for r in items if r["code"]=="jogger_special_nonmetallic_paint_option"] != expected_items:
        raise ContractError("new commercial item differs from import specification")
    if [r for r in maps if r["source_code"]==SOURCE]!=expected_maps:
        raise ContractError("Jogger source mappings differ from import specification")
    if len(maps)!=894: raise ContractError("master commercial mapping count must equal 894")
    if len({r["id"] for r in maps})!=len(maps) or {r["id"] for r in maps}!={str(i) for i in range(1,895)}:
        raise ContractError("master commercial mapping IDs must be unique and contiguous 1–894")
    if len({r["code"] for r in maps})!=len(maps): raise ContractError("duplicate commercial mapping code")
    source_keys=[(r["commercial_item_code"],r["configuration_code"],r["source_code"],r["price_date"]) for r in source_rows]
    if len(set(source_keys))!=len(source_keys): raise ContractError("duplicate Jogger source mapping natural key")
    historical=[r for r in maps if r["source_code"]=="src_pl_jogger_price_my26_20260703"]
    if len(historical)!=48: raise ContractError("July Jogger historical mappings changed")
    return {"new_items":1,"new_mappings":54,"optional":38,"not_available":16}
def apply():
    configurations=verify_source();item_spec,map_spec=load_specs(configurations)
    ip=MASTER/"commercial_items.csv";mp=MASTER/"commercial_item_configurations.csv"
    items=read(ip);maps=read(mp)
    if len(items)!=63 or len(maps)!=840: raise ContractError("apply requires exact pre-import baseline: 63 items and 840 mappings")
    if {r["id"] for r in items}!={str(i) for i in range(1,64)} or {r["id"] for r in maps}!={str(i) for i in range(1,841)}:
        raise ContractError("apply requires contiguous, unique pre-import IDs")
    if any(r["code"]=="jogger_special_nonmetallic_paint_option" for r in items): raise ContractError("new item already exists")
    if any(r["source_code"]==SOURCE for r in maps): raise ContractError("source mappings already exist")
    new_items,new_maps=expected_master_rows(item_spec,map_spec)
    if len({r["code"] for r in maps+new_maps})!=len(maps)+len(new_maps): raise ContractError("mapping code collision")
    old={(r["commercial_item_code"],r["configuration_code"],r["source_code"]) for r in maps}
    new={(r["commercial_item_code"],r["configuration_code"],r["source_code"]) for r in new_maps}
    if old&new: raise ContractError("mapping natural-key collision")
    write(ip,ITEM_FIELDS,items+new_items);write(mp,MAP_FIELDS,maps+new_maps)
    return check()
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group();mode.add_argument("--apply",action="store_true");mode.add_argument("--check",action="store_true")
    args=parser.parse_args()
    try: result=apply() if args.apply else check()
    except (ContractError,OSError,KeyError) as exc: parser.error(str(exc))
    print("Jogger commercial matrix OK: 1 item, 54 mappings, 38 optional, 16 not_available")
    print(result)
if __name__=="__main__": raise SystemExit(main())
