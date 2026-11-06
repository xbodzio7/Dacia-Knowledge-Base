from __future__ import annotations
import argparse, csv, json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SPECS = ROOT / "data" / "imports"
SOURCE = "src_pl_duster_price_my26_20261102"
URL = "https://cdn.group.renault.com/dac/pl/pdf/cenniki/duster-price.pdf.asset.pdf/f07ca0a87f.pdf"
PREVIOUS = "src_pl_duster_price_my26_20260901"
CONFIGS = (
"duster_iii_essential_ecog120_4x2_manual","duster_iii_expression_ecog120_4x2_manual","duster_iii_extreme_ecog120_4x2_manual","duster_iii_journey_ecog120_4x2_manual",
"duster_iii_expression_ecog120_4x2_automatic","duster_iii_extreme_ecog120_4x2_automatic","duster_iii_journey_ecog120_4x2_automatic",
"duster_iii_expression_mildhybrid140_4x2_manual","duster_iii_extreme_mildhybrid140_4x2_manual","duster_iii_journey_mildhybrid140_4x2_manual",
"duster_iii_expression_hybrid155_4x2_automatic","duster_iii_extreme_hybrid155_4x2_automatic","duster_iii_journey_hybrid155_4x2_automatic",
"duster_iii_expression_hybridg150_4x4_automatic","duster_iii_extreme_hybridg150_4x4_automatic","duster_iii_journey_hybridg150_4x4_automatic")
VERSIONS = ("duster_iii_essential","duster_iii_expression","duster_iii_extreme","duster_iii_journey")
WHEEL = {"duster_iii_expression_mildhybrid140_4x2_manual","duster_iii_extreme_mildhybrid140_4x2_manual","duster_iii_journey_mildhybrid140_4x2_manual","duster_iii_expression_hybrid155_4x2_automatic","duster_iii_extreme_hybrid155_4x2_automatic","duster_iii_journey_hybrid155_4x2_automatic"}
TECHNO = {"duster_iii_extreme_ecog120_4x2_automatic","duster_iii_extreme_hybrid155_4x2_automatic","duster_iii_extreme_hybridg150_4x4_automatic"}
PRICES = {
"duster_iii_essential_ecog120_4x2_manual":"82000","duster_iii_expression_ecog120_4x2_manual":"90000","duster_iii_extreme_ecog120_4x2_manual":"96000","duster_iii_journey_ecog120_4x2_manual":"96200",
"duster_iii_expression_ecog120_4x2_automatic":"96900","duster_iii_extreme_ecog120_4x2_automatic":"102900","duster_iii_journey_ecog120_4x2_automatic":"103100",
"duster_iii_expression_mildhybrid140_4x2_manual":"97600","duster_iii_extreme_mildhybrid140_4x2_manual":"103600","duster_iii_journey_mildhybrid140_4x2_manual":"103800",
"duster_iii_expression_hybrid155_4x2_automatic":"112100","duster_iii_extreme_hybrid155_4x2_automatic":"118100","duster_iii_journey_hybrid155_4x2_automatic":"118300",
"duster_iii_expression_hybridg150_4x4_automatic":"119900","duster_iii_extreme_hybridg150_4x4_automatic":"125900","duster_iii_journey_hybridg150_4x4_automatic":"126100"}
ITEM_NOTES = {
"duster_spare_wheel_option":"Space saver 135/80 R17; July 2026 historical price 800 PLN. The 2026-11-02 official cennik sets 900 PLN for Expression/Extreme/Journey and explicitly excludes all LPG configurations; see dated mappings.",
"duster_techno_1_package":"The 2026-11-02 official cennik shows 2,900 PLN only for Extreme; the package includes ACC, which is available only with automatic transmission. Current dated mappings therefore allow only the three automatic Extreme configurations and mark the other 13 unavailable."}

def read(name):
    with (MASTER / name).open(encoding="utf-8", newline="") as f: return list(csv.DictReader(f))
def read_spec(name):
    with (SPECS / name).open(encoding="utf-8", newline="") as f: return list(csv.DictReader(f))
def write(name, rows):
    with (MASTER / name).open("w", encoding="utf-8", newline="") as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows)
def unique(rows, key="code"):
    result={r[key]:r for r in rows}
    assert len(result)==len(rows), f"duplicate {key}"
    return result
def expected_mapping(r):
    return {"code":r["code"],"commercial_item_code":r["commercial_item_code"],"configuration_code":r["configuration_code"],"availability_status":r["availability_status"],"amount":r["amount"],"currency_code":r["currency_code"],"price_date":r["price_date"],"source_code":r["source_code"],"notes":f"Printed page {r['source_page']}; source row: {r['source_label']}. {r['notes']}"}

def check():
    sources=read("sources.csv"); versions=read("source_versions.csv"); links=read("source_configurations.csv")
    items=read("commercial_items.csv"); members=read("commercial_item_attributes.csv"); mappings=read("commercial_item_configurations.csv")
    prices=read("configuration_prices.csv"); values=read("configuration_attribute_values.csv")
    ranges=read("configuration_attribute_value_ranges.csv"); availability=read("configuration_attribute_availability.csv")
    source=unique(sources)["src_pl_duster_price_my26_20261102"]
    assert source["source_type"]=="configuration_pdf" and source["document_date"]=="2026-11-02"
    assert source["external_reference"]==URL and not source["file_path"] and not source["sha256"]
    sv=[r for r in versions if r["source_code"]==SOURCE]; sl=[r for r in links if r["source_code"]==SOURCE]
    assert {r["version_code"] for r in sv}==set(VERSIONS) and len(sv)==4
    assert {r["configuration_code"] for r in sl}==set(CONFIGS) and len(sl)==16
    item_spec=read_spec("duster_price_list_20261102_items.csv")
    member_spec=read_spec("duster_price_list_20261102_memberships.csv")
    mapping_spec=read_spec("duster_price_list_20261102_mappings.csv")
    assert (len(item_spec),len(member_spec),len(mapping_spec))==(2,2,64)
    ii=unique(items); mi=unique(members); ci=unique(mappings)
    for r in item_spec: assert {k:ii[r["code"]][k] for k in r}==r
    for r in member_spec: assert {k:mi[r["code"]][k] for k in r}==r
    for r in mapping_spec:
        e=expected_mapping(r); a=ci[r["code"]]; assert {k:a[k] for k in e}==e
    assert (len(items),len(members),len(mappings))==(60,105,631)
    new=[r for r in mappings if r["source_code"]==SOURCE]
    assert len(new)==64
    assert Counter(r["commercial_item_code"] for r in new)=={"duster_colour_biel_alpejska":16,"duster_colour_khaki_lichen":16,"duster_spare_wheel_option":16,"duster_techno_1_package":16}
    wheel=[r for r in new if r["commercial_item_code"]=="duster_spare_wheel_option"]
    techno=[r for r in new if r["commercial_item_code"]=="duster_techno_1_package"]
    assert {r["configuration_code"] for r in wheel if r["availability_status"]=="optional"}==WHEEL
    assert all(r["amount"]=="900" for r in wheel if r["availability_status"]=="optional")
    assert len([r for r in wheel if r["availability_status"]=="not_available" and not r["amount"]])==10
    assert {r["configuration_code"] for r in techno if r["availability_status"]=="optional"}==TECHNO
    assert all(r["amount"]=="2900" for r in techno if r["availability_status"]=="optional")
    assert len([r for r in techno if r["availability_status"]=="not_available" and not r["amount"]])==13
    old_prices=[r for r in prices if r["source_code"]==PREVIOUS]
    assert len(old_prices)==16 and {r["configuration_code"]:r["amount"] for r in old_prices}==PRICES
    assert not [r for r in prices if r["source_code"]==SOURCE]
    assert len([r for r in values if r["source_code"]==PREVIOUS])==391
    assert len([r for r in ranges if r["source_code"]==PREVIOUS])==16
    assert len([r for r in availability if r["source_code"]==PREVIOUS])==1152
    assert not [r for r in values+ranges+availability if r["source_code"]==SOURCE]
    for code,note in ITEM_NOTES.items(): assert ii[code]["notes"]==note
    return {"source_code":SOURCE,"configurations":16,"versions":4,"new_items":2,"new_memberships":2,"dated_commercial_mappings":64,"catalogue_price_rows_reused":16,"technical_scalar_observations_reused":391,"technical_ranges_reused":16,"equipment_availability_observations_reused":1152}

def apply():
    items=read("commercial_items.csv"); members=read("commercial_item_attributes.csv"); mappings=read("commercial_item_configurations.csv")
    if (len(items),len(members),len(mappings))!=(58,103,567): raise AssertionError("Unexpected pre-import baseline")
    if SOURCE not in {r["code"] for r in read("sources.csv")}: raise AssertionError("Register the source first")
    item_spec=read_spec("duster_price_list_20261102_items.csv"); member_spec=read_spec("duster_price_list_20261102_memberships.csv"); mapping_spec=read_spec("duster_price_list_20261102_mappings.csv")
    for r in items:
        if r["code"] in ITEM_NOTES: r["notes"]=ITEM_NOTES[r["code"]]
    ni=max(int(r["id"]) for r in items)+1
    for r in item_spec: items.append({"id":str(ni),**r}); ni+=1
    nm=max(int(r["id"]) for r in members)+1
    for r in member_spec: members.append({"id":str(nm),**r}); nm+=1
    nc=max(int(r["id"]) for r in mappings)+1
    for r in mapping_spec: mappings.append({"id":str(nc),**expected_mapping(r)}); nc+=1
    write("commercial_items.csv",items); write("commercial_item_attributes.csv",members); write("commercial_item_configurations.csv",mappings)
    return check()

def main():
    p=argparse.ArgumentParser(description="Duster MY26 2026-11-02 official price-list import")
    p.add_argument("--apply",action="store_true")
    a=p.parse_args()
    print(json.dumps(apply() if a.apply else check(),ensure_ascii=False,indent=2))
if __name__=="__main__": main()
