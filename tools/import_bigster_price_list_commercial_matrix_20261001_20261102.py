#!/usr/bin/env python3
"""Import the Bigster MY26 October/November 2026 commercial option matrix."""
from __future__ import annotations
import argparse, csv, hashlib, os, tempfile
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MASTER=ROOT/"data"/"master"
IMPORTS=ROOT/"data"/"imports"
OCT="src_pl_bigster_price_my26_20261001"
NOV="src_pl_bigster_price_my26_20261102"
DATES={OCT:"2026-10-01",NOV:"2026-11-02"}
NOV_URL="https://cdn.group.renault.com/dac/pl/pdf/cenniki/bigster-price.pdf.asset.pdf/2fe688def9.pdf"
OCT_SHA="0964b3a3311708698ef3cee6bd28244f76c1db36d0d9452e128e5113384dac97"
ITEM_SPEC=IMPORTS/"bigster_commercial_items_20261001.csv"
MAP_SPEC=IMPORTS/"bigster_commercial_item_configurations_20261001_20261102.csv"
ITEM_FIELDS=("id","code","name","item_type","observation_date","source_code","status","notes")
MAP_FIELDS=("id","code","commercial_item_code","configuration_code","availability_status","amount","currency_code","price_date","source_code","notes")
ITEM_SPEC_FIELDS=ITEM_FIELDS[1:]
MAP_SPEC_FIELDS=("code","commercial_item_code","configuration_code","availability_status","amount","currency_code","price_date","source_code","source_page","source_label","notes")
SPARE_NOTE="The July 2026 mappings are historical. October/November 2026 price-list rows preserve the printed powertrain qualifier; do not project the Hybrid 155 space-saver price to other powertrains. Unknown is used where the source does not establish applicability."
class ContractError(RuntimeError): pass

def read(path):
    with path.open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        if not reader.fieldnames: raise ContractError(f"missing header: {path}")
        return list(reader)

def write(path,fields,rows):
    fd,tmp=tempfile.mkstemp(prefix=f".{path.name}.",dir=path.parent)
    try:
        with os.fdopen(fd,"w",encoding="utf-8",newline="") as f:
            w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(rows)
        os.replace(tmp,path)
    except Exception:
        try: os.unlink(tmp)
        except OSError: pass
        raise

def file_hash(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()

def verify_sources():
    sources={r["code"]:r for r in read(MASTER/"sources.csv")}
    oct=sources[OCT];nov=sources[NOV]
    if oct["document_date"]!="2026-10-01" or oct["sha256"]!=OCT_SHA: raise ContractError("October source receipt mismatch")
    if file_hash(ROOT/oct["file_path"])!=OCT_SHA: raise ContractError("October source PDF hash mismatch")
    if nov["document_date"]!="2026-11-02" or nov["external_reference"]!=NOV_URL: raise ContractError("November source receipt mismatch")
    if nov["file_path"] or nov["sha256"] or "no repository SHA-256 is asserted" not in nov["notes"]: raise ContractError("November Library/hash boundary mismatch")
    links=read(MASTER/"source_configurations.csv")
    oct_links={r["configuration_code"] for r in links if r["source_code"]==OCT and r["relationship"]=="documents"}
    nov_links=[r for r in links if r["source_code"]==NOV]
    prices=read(MASTER/"configuration_prices.csv")
    sets={}
    for source,date in DATES.items():
        rows=[r for r in prices if r["source_code"]==source and r["price_date"]==date]
        sets[source]={r["configuration_code"] for r in rows}
        if len(rows)!=13 or len(sets[source])!=13: raise ContractError(f"{source} price matrix must cover 13 configurations")
    if sets[OCT]!=sets[NOV] or sets[OCT]!=oct_links or len(oct_links)!=13 or nov_links:
        raise ContractError("source/configuration boundary mismatch")
    return sets

def load_specs(configs):
    with ITEM_SPEC.open(encoding="utf-8-sig",newline="") as f:
        if next(csv.reader(f),None)!=list(ITEM_SPEC_FIELDS): raise ContractError("paint item spec header mismatch")
    items=read(ITEM_SPEC)
    if len(items)!=2 or {r["code"] for r in items}!={"bigster_metallic_paint_option","bigster_two_tone_body_option"}: raise ContractError("expected two paint options")
    if any(r["source_code"]!=OCT or r["observation_date"]!="2026-10-01" or r["item_type"]!="option" for r in items): raise ContractError("paint item provenance mismatch")
    with MAP_SPEC.open(encoding="utf-8-sig",newline="") as f:
        if next(csv.reader(f),None)!=list(MAP_SPEC_FIELDS): raise ContractError("mapping spec header mismatch")
    rows=read(MAP_SPEC)
    if len(rows)!=172 or len({r["code"] for r in rows})!=172: raise ContractError("expected 172 unique mapping spec rows")
    keys={(r["commercial_item_code"],r["configuration_code"],r["source_code"]) for r in rows}
    if len(keys)!=172: raise ContractError("duplicate mapping natural key")
    expected={"bigster_metallic_paint_option":13,"bigster_two_tone_body_option":8,"bigster_19inch_wheel_option":4,"bigster_panoramic_roof_option":4,"bigster_power_tailgate_option":4,"bigster_media_nav_live_option":4,"bigster_easy_package":4,"bigster_parking_package":8,"bigster_winter_package":12,"bigster_winter_plus_package":12,"bigster_spare_wheel_option":13}
    for source,date in DATES.items():
        subset=[r for r in rows if r["source_code"]==source]
        if len(subset)!=86 or {r["configuration_code"] for r in subset}-configs[source]: raise ContractError(f"invalid configuration scope for {source}")
        if dict(Counter(r["commercial_item_code"] for r in subset))!=expected: raise ContractError(f"invalid item distribution for {source}")
        spare=[r for r in subset if r["commercial_item_code"]=="bigster_spare_wheel_option"]
        if Counter(r["availability_status"] for r in spare)!={"unknown":10,"optional":3}: raise ContractError("spare-wheel scope must be 3 priced and 10 unknown")
        for r in subset:
            if r["price_date"]!=date or r["currency_code"]!="PLN" or r["source_page"] not in {"4","5"} or not r["source_label"]: raise ContractError(f"invalid provenance for {r['code']}")
            if r["availability_status"]=="unknown":
                if r["commercial_item_code"]!="bigster_spare_wheel_option" or r["amount"] or "_hybrid155_" in r["configuration_code"]: raise ContractError("invalid unknown spare-wheel row")
            elif r["availability_status"]=="optional":
                if not r["amount"].isdigit() or int(r["amount"])<=0: raise ContractError("optional mapping requires a price")
            else: raise ContractError("unsupported availability status")
    return items,rows

def expected_rows(item_spec,map_spec):
    items=[{"id":str(57+i),**r} for i,r in enumerate(item_spec)]
    maps=[]
    for i,r in enumerate(map_spec):
        maps.append({"id":str(396+i),"code":r["code"],"commercial_item_code":r["commercial_item_code"],"configuration_code":r["configuration_code"],"availability_status":r["availability_status"],"amount":r["amount"],"currency_code":r["currency_code"],"price_date":r["price_date"],"source_code":r["source_code"],"notes":f"Printed page {r['source_page']}; source row: {r['source_label']}. {r['notes']}"})
    return items,maps

def check():
    configs=verify_sources(); item_spec,map_spec=load_specs(configs); exp_items,exp_maps=expected_rows(item_spec,map_spec)
    items=read(MASTER/"commercial_items.csv"); maps=read(MASTER/"commercial_item_configurations.csv")
    got_items=[r for r in items if r["code"] in {x["code"] for x in exp_items}]
    got_maps=[r for r in maps if r["source_code"] in DATES]
    if len(items)!=58 or len(maps)!=567 or got_items!=exp_items or got_maps!=exp_maps: raise ContractError("master rows differ from import spec")
    if len({r["code"] for r in maps})!=len(maps): raise ContractError("duplicate mapping code")
    new_keys={(r["commercial_item_code"],r["configuration_code"],r["source_code"]) for r in got_maps}
    if len(new_keys)!=len(got_maps): raise ContractError("duplicate natural key in imported rows")
    existing_keys={(r["commercial_item_code"],r["configuration_code"],r["source_code"]) for r in maps if r["source_code"] not in DATES}
    if new_keys & existing_keys: raise ContractError("new mapping natural key already exists in historical master rows")
    if sum(r["source_code"]=="src_pl_bigster_price_my26_20260703" for r in maps)!=66: raise ContractError("July history changed")
    if next(r for r in items if r["code"]=="bigster_spare_wheel_option")["notes"]!=SPARE_NOTE: raise ContractError("spare-wheel note mismatch")
    return {"new_items":2,"new_mappings":172,"rows_2026_10_01":86,"rows_2026_11_02":86}

def apply():
    configs=verify_sources(); item_spec,map_spec=load_specs(configs); new_items,new_maps=expected_rows(item_spec,map_spec)
    ip=MASTER/"commercial_items.csv";mp=MASTER/"commercial_item_configurations.csv"
    items=read(ip);maps=read(mp)
    if len(items)!=56 or len(maps)!=395: raise ContractError("apply requires exact pre-import baseline")
    spare=next(r for r in items if r["code"]=="bigster_spare_wheel_option");spare["notes"]=SPARE_NOTE
    items.extend(new_items);maps.extend(new_maps);write(ip,ITEM_FIELDS,items);write(mp,MAP_FIELDS,maps)
    return check()

def main():
    parser=argparse.ArgumentParser(description=__doc__);g=parser.add_mutually_exclusive_group();g.add_argument("--apply",action="store_true");g.add_argument("--check",action="store_true");args=parser.parse_args()
    try: result=apply() if args.apply else check()
    except (ContractError,OSError,KeyError) as exc: parser.error(str(exc))
    print(f"Bigster commercial matrix OK: {result['new_items']} items, {result['new_mappings']} mappings (86 per source date)")
if __name__=="__main__": main()
