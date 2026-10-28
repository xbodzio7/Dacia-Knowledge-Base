#!/usr/bin/env python3
"""Import exact Bigster brochure page-21 states for rear tinted glazing and both roof-rail types."""
from __future__ import annotations
import argparse,csv,hashlib,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; MASTER=ROOT/"data"/"master"
SOURCE=ROOT/"PDF"/"Broszury"/"DACIA BIGSTER broszura 20251210.pdf"
SOURCE_SHA256="76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74"
SOURCE_CODE="src_pl_bigster_brochure_20251210"; DATE="2025-12-10"
SPEC=ROOT/"data"/"imports"/"bigster_brochure_page21_availability_20251210.csv"
OUTPUT=MASTER/"configuration_attribute_availability.csv"
FIELDS=("id","code","configuration_code","attribute_code","availability_status","observation_date","source_code","notes")
SPEC_FIELDS=("configuration_code","attribute_code","availability_status","source_page","source_label","normalization_notes")
CONFIGS={"bigster_essential_mildhybrid140_4x2_manual":"essential","bigster_expression_mildhybrid140_4x2_manual":"expression","bigster_extreme_mildhybrid140_4x2_manual":"extreme","bigster_journey_mildhybrid140_4x2_manual":"journey","bigster_essential_mildhybridg140_4x2_manual":"essential","bigster_expression_mildhybridg140_4x2_manual":"expression","bigster_extreme_mildhybridg140_4x2_manual":"extreme","bigster_journey_mildhybridg140_4x2_manual":"journey","bigster_expression_hybrid155_4x2_automatic":"expression","bigster_extreme_hybrid155_4x2_automatic":"extreme","bigster_journey_hybrid155_4x2_automatic":"journey","bigster_expression_hybridg150_4x4_automatic":"expression","bigster_extreme_hybridg150_4x4_automatic":"extreme","bigster_journey_hybridg150_4x4_automatic":"journey"}
STATES={"privacy_glass":{"essential":"not_available","expression":"not_available","journey":"standard","extreme":"standard"},"roof_rails":{"essential":"standard","expression":"standard","journey":"standard","extreme":"not_available"},"modular_roof_rails":{"essential":"not_available","expression":"not_available","journey":"not_available","extreme":"standard"}}
class ContractError(RuntimeError): pass
def read_csv(path):
 with path.open(encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
def sha256(path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
 return h.hexdigest()
def generated_rows():
 if sha256(SOURCE)!=SOURCE_SHA256: raise ContractError("brochure source SHA-256 mismatch")
 with SPEC.open(encoding="utf-8-sig",newline="") as f:
  reader=csv.DictReader(f)
  if reader.fieldnames!=list(SPEC_FIELDS): raise ContractError("unexpected import spec header")
  spec=list(reader)
 expected={(c,a,STATES[a][g]) for c,g in CONFIGS.items() for a in STATES}
 actual={(r["configuration_code"],r["attribute_code"],r["availability_status"]) for r in spec}
 if actual!=expected or len(spec)!=len(expected): raise ContractError("spec differs from reviewed page-21 grade matrix")
 if any(r["source_page"]!="21" or not r["source_label"].strip() for r in spec): raise ContractError("invalid source page/label")
 configs={r["code"]:r for r in read_csv(MASTER/"configurations.csv")}
 if any(c not in configs or configs[c]["status"]!="active" for c in CONFIGS): raise ContractError("expected Bigster configs missing/inactive")
 attrs={r["code"]:r for r in read_csv(MASTER/"attributes.csv")}
 for a in STATES:
  if a not in attrs or attrs[a]["status"]!="active" or attrs[a]["data_type"]!="boolean": raise ContractError(f"attribute {a} missing/inactive/not boolean")
 links={(r["source_code"],r["configuration_code"]) for r in read_csv(MASTER/"source_configurations.csv")}
 if any((SOURCE_CODE,c) not in links for c in CONFIGS): raise ContractError("brochure source-to-configuration link missing")
 result=[]
 for r in spec:
  c=r["configuration_code"]; g=CONFIGS[c]
  note=f"Official Bigster brochure dated 2025-12-10, printed page 21; {r['source_label']}; exact {g} grade column. "+r["normalization_notes"].strip()
  result.append({"code":f"{c}_{r['attribute_code']}_20251210","configuration_code":c,"attribute_code":r["attribute_code"],"availability_status":r["availability_status"],"observation_date":DATE,"source_code":SOURCE_CODE,"notes":note})
 return result
def semantic(rows): return sorted(tuple(r.get(f,"") for f in FIELDS[1:]) for r in rows)
def main():
 p=argparse.ArgumentParser(description=__doc__); m=p.add_mutually_exclusive_group(required=True); m.add_argument("--check",action="store_true"); m.add_argument("--apply",action="store_true"); a=p.parse_args()
 current=read_csv(OUTPUT); expected=generated_rows()
 actual=[r for r in current if r.get("source_code")==SOURCE_CODE and r.get("observation_date")==DATE and r.get("attribute_code") in STATES]
 if a.check:
  if len(actual)!=len(expected) or semantic(actual)!=semantic(expected): raise ContractError("page-21 observations differ from import contract")
  print("Bigster brochure page-21 availability: PASS (42 direct observations)"); return 0
 if actual:
  if len(actual)!=len(expected) or semantic(actual)!=semantic(expected): raise ContractError("partial/conflicting page-21 observations already exist")
  print("Bigster page-21 observations already match contract."); return 0
 maximum=max((int(r["id"]) for r in current),default=0)
 additions=[{"id":str(maximum+i),**r} for i,r in enumerate(expected,1)]
 tmp=OUTPUT.with_name(f".{OUTPUT.name}.tmp-{os.getpid()}")
 try:
  with tmp.open("w",encoding="utf-8",newline="") as f:
   w=csv.DictWriter(f,fieldnames=FIELDS,lineterminator="\n"); w.writeheader(); w.writerows(current+additions)
  tmp.replace(OUTPUT)
 finally: tmp.unlink(missing_ok=True)
 print(f"Imported {len(additions)} direct Bigster brochure page-21 observations."); return 0
if __name__=="__main__":
 try: raise SystemExit(main())
 except (ContractError,OSError,ValueError,KeyError) as exc: raise SystemExit(f"Bigster page-21 import failed: {exc}")
