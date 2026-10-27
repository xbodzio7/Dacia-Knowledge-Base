#!/usr/bin/env python3
"""Build or verify the authored Jogger page-19 ambiguity review."""
from __future__ import annotations
import argparse, csv, hashlib, json, sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

REVIEW_VERSION=1
REVIEW_KIND="jogger_technical_page19_ambiguity_review"
REVIEWED_ON="2026-07-28"
DEFAULT_PRIORITIZATION=Path("data/reporting/verified_pdf_candidate_residual_gap_prioritization.json")
DEFAULT_JSON=Path("data/reporting/jogger_technical_page19_ambiguity_review.json")
DEFAULT_MARKDOWN=Path("data/reporting/jogger_technical_page19_ambiguity_review.md")
PACKAGE_ID="residual_gap_002"
SOURCE_CODE="src_pl_jogger_brochure_20251217"
SOURCE_PAGE=19
SOURCE_PATH=Path("PDF/Broszury/DACIA JOGGER broszura 20251217.pdf")
SOURCE_SHA256="eb4d44436c314d7e38d018af68e7475f03122a27f1e3f30e768f60432d338dd6"
NEXT_PACKAGE="Duster Mini Technical Page 20 Ambiguity Review"
DECISION_STATUSES={"covered_by_selected_evidence","partially_covered","context_only_non_import","deferred_source_conflict","unresolved_signature_mismatch"}

class JoggerPage19ReviewError(RuntimeError): pass

def repository_root()->Path: return Path(__file__).resolve().parents[1]
def ensure(condition:bool,message:str)->None:
    if not condition: raise JoggerPage19ReviewError(message)
def canonical_json(payload:Mapping[str,Any])->str: return json.dumps(payload,ensure_ascii=False,indent=2)+"\n"
def write_atomic(path:Path,text:str)->None:
    path.parent.mkdir(parents=True,exist_ok=True); temporary=path.with_suffix(path.suffix+".tmp")
    temporary.write_text(text,encoding="utf-8",newline="\n"); temporary.replace(path)
def load_json_object(path:Path,label:str)->dict[str,Any]:
    try: value=json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc: raise JoggerPage19ReviewError(f"cannot read {label}: {exc}") from exc
    except json.JSONDecodeError as exc: raise JoggerPage19ReviewError(f"invalid JSON in {label}: {exc}") from exc
    ensure(isinstance(value,dict),f"{label} must be a JSON object"); return value
def sha256(path:Path)->str:
    digest=hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda:handle.read(1024*1024),b""): digest.update(chunk)
    except OSError as exc: raise JoggerPage19ReviewError(f"cannot read archived source: {exc}") from exc
    return digest.hexdigest()
def signature(attribute_code:str,value:str)->dict[str,str]:
    return {"attribute_code":attribute_code,"value":value,"fuel_type_code":"","gear_number":""}
def fact(attribute_code:str,values:Sequence[str],reason:str)->dict[str,Any]:
    return {"attribute_code":attribute_code,"source_values":list(values),"reason":reason}

DECISIONS=(
{"candidate_id":"91156aecc0c5e1c4f3c907a8d7bed4a6e48cc8ebd1b6c53a36b4ead6c5a737c3","line_start":12,"exact_text":"Maks. moc kW EWG (KM) przy                                                                                              105 (140)","decision":"deferred_source_conflict","selected":[],"rationale":"The row states 105 kW total Hybrid 155 output, every attached signature is max-power engine speed, and the later official MY26 source states 116 kW. The conflict remains non-importable.","source_facts":[fact("hybrid_system_power_total",["105"],"The older brochure value conflicts with the later official 116 kW observation and has no attached power signature.")]},
{"candidate_id":"af25bb2ab9eafa6499e0439b643700e4476f3b0e64ffc6c5bd86c6d038bd099f","line_start":51,"exact_text":"                                                           amortyzatorami hydraulicznymi i stabilizatorem","decision":"covered_by_selected_evidence","selected":[signature("front_suspension","Typu McPherson z dolnym wahaczem, sprężynami śrubowymi, teleskopowymi amortyzatorami hydraulicznymi i stabilizatorem")],"rationale":"The visual line is the continuation of the front-suspension row; the attached rear-suspension signature belongs to the next labelled row.","source_facts":[]},
{"candidate_id":"87f2256211644e68452882048c3c195bc6f8131db92038884e9f9aef4faf2281","line_start":61,"exact_text":"                    Wersja 5-miejscowa        10,5          10,9            11,9         10,4            11,4                8,9","decision":"partially_covered","selected":[signature("acceleration_0_100","8.9")],"rationale":"Only the attached 8.9-second signature belongs to this five-seat row; 9 seconds belongs to the seven-seat row.","source_facts":[fact("acceleration_0_100",["10.5","10.9","11.9","10.4","11.4"],"Visible five-seat values without signatures attached to this candidate.")]},
{"candidate_id":"dc6fdb0c6ad6ccde3275ec5df42e1cdaf1cbaa606b12d339b2234fff2417f238","line_start":62,"exact_text":"                    Wersja 7-miejscowa        11,2           11              12          10,7            11,7                 9","decision":"partially_covered","selected":[signature("acceleration_0_100","9")],"rationale":"Only the attached 9-second signature belongs to this seven-seat row; 8.9 seconds belongs to the five-seat row.","source_facts":[fact("acceleration_0_100",["11.2","11","12","10.7","11.7"],"Visible seven-seat values without signatures attached to this candidate.")]},
{"candidate_id":"a9cbecb27287715ea402b4ae8ba2754e10b0b994bea11d48e2eae3c2051d56e5","line_start":67,"exact_text":"                  Wersja 5-miejscowa          11,4          8,1             9,1          8,3             9,2                 6,4","decision":"unresolved_signature_mismatch","selected":[],"rationale":"The row is 80–120 km/h elasticity, but both attached signatures are 0–100 km/h acceleration.","source_facts":[fact("elasticity_80_120",["11.4","8.1","9.1","8.3","9.2","6.4"],"No matching elasticity signature is attached.")]},
{"candidate_id":"3e57e1eae5d0f58acf0756a50ff74047cc45c30cd1efe0729d8be2f920ae1315","line_start":68,"exact_text":"                  Wersja 7-miejscowa          12,3          8,2             9,2          8,7             9,5                 6,5","decision":"unresolved_signature_mismatch","selected":[],"rationale":"The row is 80–120 km/h elasticity, but both attached signatures are 0–100 km/h acceleration.","source_facts":[fact("elasticity_80_120",["12.3","8.2","9.2","8.7","9.5","6.5"],"No matching elasticity signature is attached.")]},
{"candidate_id":"123c5c41b995919ac7aa0157fc195514ecc93df2bf1b15268051b8e60a3504ac","line_start":82,"exact_text":"               Wersja 5-miejscowa             1193                   1292                         1326                       1359","decision":"unresolved_signature_mismatch","selected":[],"rationale":"The row is five-seat minimum kerb mass, but both attached signatures are acceleration.","source_facts":[fact("minimum_kerb_weight",["1193","1292","1326","1359"],"No matching mass signature is attached.")]},
{"candidate_id":"b9aeb4aed7119c4e5920f29463cdb73908d18d5f9b2fdc9afee2ddec407ecefe","line_start":83,"exact_text":"               Wersja 7-miejscowa             1221                   1321                         1354                       1388","decision":"unresolved_signature_mismatch","selected":[],"rationale":"The row is seven-seat minimum kerb mass, but both attached signatures are acceleration.","source_facts":[fact("minimum_kerb_weight",["1221","1321","1354","1388"],"No matching mass signature is attached.")]},
{"candidate_id":"72df9514c775a1e00171477bb61d20407e9c34a1b2bf2c4366e9f7e8e6211982","line_start":87,"exact_text":"                Wersja 5-miejscowa            1230                   1312                         1335                       1373","decision":"deferred_source_conflict","selected":[],"rationale":"The printed gross-train label conflicts with values below gross vehicle weight that follow a maximum-kerb-mass pattern; attached acceleration signatures are rejected.","source_facts":[fact("maximum_kerb_weight",["1230","1312","1335","1373"],"Likely five-seat maximum kerb masses, but the source label conflicts; no import meaning is approved.")]},
{"candidate_id":"f09c7f9f12583734f27b8282f460661317f2e04fead563099253d13097999b41","line_start":88,"exact_text":"                Wersja 7-miejscowa            1261                   1342                         1364                       1405","decision":"deferred_source_conflict","selected":[],"rationale":"The printed gross-train label conflicts with values below gross vehicle weight that follow a maximum-kerb-mass pattern; attached acceleration signatures are rejected.","source_facts":[fact("maximum_kerb_weight",["1261","1342","1364","1405"],"Likely seven-seat maximum kerb masses, but the source label conflicts; no import meaning is approved.")]},
{"candidate_id":"a97212de9458f15c537f77ea07a2c876fa82108c54cca5ab727d3f68c0030155","line_start":92,"exact_text":"               Wersja 5-miejscowa             2885                   2965                         2985                       2830","decision":"deferred_source_conflict","selected":[],"rationale":"The printed gross-vehicle label conflicts with values equal to gross vehicle plus braked trailer, the gross-train pattern; attached acceleration signatures are rejected.","source_facts":[fact("gross_train_weight",["2885","2965","2985","2830"],"Numerically five-seat gross train weights, but the printed label conflicts.")]},
{"candidate_id":"259cb9881353399e4f854a0ec9ec976c633835640dad94f92a36975ba3934a08","line_start":93,"exact_text":"               Wersja 7-miejscowa             3055                   3140                         3160                       3000","decision":"deferred_source_conflict","selected":[],"rationale":"The printed gross-vehicle label conflicts with values equal to gross vehicle plus braked trailer, the gross-train pattern; attached acceleration signatures are rejected.","source_facts":[fact("gross_train_weight",["3055","3140","3160","3000"],"Numerically seven-seat gross train weights, but the printed label conflicts.")]},
{"candidate_id":"4fac5cebdeae28892c2ee77ced0abb3bd59006918fef0462f69b1b8dd0e6999e","line_start":97,"exact_text":"               Wersja 5-miejscowa             1685                   1765                         1785                       1830","decision":"unresolved_signature_mismatch","selected":[],"rationale":"The row is five-seat gross vehicle weight, but both attached signatures are acceleration.","source_facts":[fact("gross_vehicle_weight",["1685","1765","1785","1830"],"No matching mass signature is attached.")]},
{"candidate_id":"a140b4a368f27e1b1b815bb6c70c80635bad3e0cbbcdaaa3442bde6450e0dd94","line_start":98,"exact_text":"               Wersja 7-miejscowa             1855                   1940                         1960                       2000","decision":"unresolved_signature_mismatch","selected":[],"rationale":"The row is seven-seat gross vehicle weight, but both attached signatures are acceleration.","source_facts":[fact("gross_vehicle_weight",["1855","1940","1960","2000"],"No matching mass signature is attached.")]},
{"candidate_id":"371081416255a70abb7008af66e06bd9284fa208d6d2f3bea1685203eaf2ecc0","line_start":102,"exact_text":"                Wersja 5-miejscowa            1200                   1200                         1200                       1200","decision":"deferred_source_conflict","selected":[],"rationale":"The older brochure assigns 1200 kg to Hybrid 155, while the later official source assigns 1000 kg; attached acceleration signatures are rejected.","source_facts":[fact("braked_trailer_weight",["1200","1200","1200","1200"],"The Hybrid 155 value conflicts with the later official 1000 kg observation.")]},
{"candidate_id":"6cf0cdad93218297dd60fd7d35499aa3c252987c7a867dbac1b9bbd2067904ed","line_start":103,"exact_text":"                Wersja 7-miejscowa            1200                   1200                         1200                       1200","decision":"deferred_source_conflict","selected":[],"rationale":"The older brochure assigns 1200 kg to Hybrid 155, while the later official source assigns 1000 kg; attached acceleration signatures are rejected.","source_facts":[fact("braked_trailer_weight",["1200","1200","1200","1200"],"The Hybrid 155 value conflicts with the later official 1000 kg observation.")]},
)

def signature_key(value:Mapping[str,Any])->str: return json.dumps(dict(value),ensure_ascii=False,sort_keys=True,separators=(",",":"))
def read_source_row(repository:Path)->dict[str,str]:
    path=repository/"data/master/sources.csv"
    try:
        with path.open(encoding="utf-8",newline="") as handle:
            reader=csv.DictReader(handle); ensure(reader.fieldnames is not None,"sources.csv has no header")
            matches=[dict(row) for row in reader if row.get("code")==SOURCE_CODE]
    except OSError as exc: raise JoggerPage19ReviewError(f"cannot read sources.csv: {exc}") from exc
    ensure(len(matches)==1,"Jogger brochure source registry row differs"); return matches[0]
def validate_prioritization(payload:Mapping[str,Any])->dict[str,Any]:
    ensure(payload.get("version")==1,"prioritization version differs")
    ensure(payload.get("kind")=="verified_pdf_candidate_residual_gap_prioritization","prioritization kind differs")
    ensure(payload.get("status")=="complete","prioritization is not complete")
    policy=payload.get("policy"); ensure(isinstance(policy,Mapping),"prioritization policy is missing")
    ensure(policy.get("master_data_changes") is False,"prioritization changes master data")
    ensure(policy.get("approved_import_spec_generation") is False,"prioritization creates approved imports")
    packages=payload.get("packages"); ensure(isinstance(packages,list),"prioritization packages are missing")
    matches=[p for p in packages if isinstance(p,Mapping) and p.get("package_id")==PACKAGE_ID]
    ensure(len(matches)==1,"residual_gap_002 package differs"); package=dict(matches[0])
    ensure(package.get("source_code")==SOURCE_CODE,"package source differs")
    ensure(package.get("model_code")=="jogger","package model differs")
    ensure(package.get("domain")=="technical_tables","package domain differs")
    ensure(package.get("page")==SOURCE_PAGE,"package page differs")
    ensure(package.get("coverage_status")=="ambiguous","package status differs")
    ensure(package.get("candidate_count")==16,"package candidate count differs")
    candidates=package.get("candidates"); ensure(isinstance(candidates,list) and len(candidates)==16,"package candidates differ")
    return package
def verify_source(repository:Path)->dict[str,Any]:
    row=read_source_row(repository)
    ensure(row.get("status")=="active","Jogger brochure source is not active")
    ensure(row.get("source_type")=="brochure_pdf","Jogger source type differs")
    ensure(row.get("document_date")=="2025-12-17","Jogger source date differs")
    ensure(row.get("file_path")==SOURCE_PATH.as_posix(),"Jogger source path differs")
    ensure(row.get("sha256")==SOURCE_SHA256,"Jogger source registry hash differs")
    archived=repository/SOURCE_PATH; ensure(archived.is_file(),"archived Jogger brochure is missing")
    ensure(sha256(archived)==SOURCE_SHA256,"archived Jogger brochure hash differs")
    return {"source_code":SOURCE_CODE,"file_path":SOURCE_PATH.as_posix(),"sha256":SOURCE_SHA256,"page":SOURCE_PAGE,"review_basis":"authored visual review of the archived page-19 technical table"}
def selected_signatures(candidate:Mapping[str,Any],expected:Sequence[Mapping[str,Any]])->list[dict[str,Any]]:
    available=candidate.get("evidence_signatures"); ensure(isinstance(available,list),"candidate evidence signatures are missing")
    by_key={}
    for item in available:
        ensure(isinstance(item,Mapping),"candidate evidence signature differs"); sig=item.get("signature")
        ensure(isinstance(sig,Mapping),"candidate signature payload is missing"); key=signature_key(sig)
        ensure(key not in by_key,"candidate evidence signature is duplicated"); by_key[key]=json.loads(json.dumps(dict(item),ensure_ascii=False))
    result=[]
    for wanted in expected:
        key=signature_key(wanted); ensure(key in by_key,f"selected signature is not attached to candidate: {key}"); result.append(by_key[key])
    return result
def build_review(prioritization:Mapping[str,Any],repository:Path)->dict[str,Any]:
    package=validate_prioritization(prioritization); source_receipt=verify_source(repository); candidates=package["candidates"]
    candidate_by_id={str(c.get("candidate_id")):c for c in candidates if isinstance(c,Mapping)}
    ensure(len(candidate_by_id)==16,"package candidate IDs are not unique")
    manifest_ids=[d["candidate_id"] for d in DECISIONS]
    ensure(len(manifest_ids)==len(set(manifest_ids))==16,"authored decision candidate IDs differ")
    ensure(set(manifest_ids)==set(candidate_by_id),"authored decision partition differs")
    decisions=[]; counts=Counter(); selected_count=selected_records=0
    for authored in DECISIONS:
        candidate=candidate_by_id[authored["candidate_id"]]
        ensure(candidate.get("line_start")==authored["line_start"] and candidate.get("line_end")==authored["line_start"],f"candidate line differs: {authored['candidate_id']}")
        ensure(candidate.get("exact_text")==authored["exact_text"],f"candidate exact text differs: {authored['candidate_id']}")
        ensure(candidate.get("source_code")==SOURCE_CODE and candidate.get("page")==SOURCE_PAGE,"candidate source boundary differs")
        ensure(candidate.get("coverage_status")=="ambiguous","candidate input status differs")
        decision=str(authored["decision"]); ensure(decision in DECISION_STATUSES,f"unknown authored decision: {decision}")
        selected=selected_signatures(candidate,authored["selected"])
        for item in selected:
            records=item.get("records"); ensure(isinstance(records,list) and item.get("record_count")==len(records),"selected evidence record count differs")
            for record in records:
                ensure(record.get("source_code")==SOURCE_CODE and record.get("source_page")==SOURCE_PAGE,"selected evidence boundary differs")
            selected_records+=len(records)
        selected_count+=len(selected); counts[decision]+=1
        decisions.append({"candidate_id":authored["candidate_id"],"source_code":SOURCE_CODE,"page":SOURCE_PAGE,"line_start":authored["line_start"],"line_end":authored["line_start"],"exact_text":authored["exact_text"],"input_coverage_status":"ambiguous","authored_decision":decision,"rationale":authored["rationale"],"selected_evidence_signature_count":len(selected),"selected_evidence_record_count":sum(int(x["record_count"]) for x in selected),"selected_evidence_signatures":selected,"source_facts":authored["source_facts"]})
    expected=Counter({"covered_by_selected_evidence":1,"partially_covered":2,"context_only_non_import":0,"deferred_source_conflict":7,"unresolved_signature_mismatch":6})
    ensure(counts==expected,"authored decision distribution differs")
    return {"version":REVIEW_VERSION,"kind":REVIEW_KIND,"reviewed_on":REVIEWED_ON,"status":"complete","source_prioritization":DEFAULT_PRIORITIZATION.as_posix(),"package_id":PACKAGE_ID,"source_receipt":source_receipt,"scope":{"candidate_count":16,"source_code":SOURCE_CODE,"model_code":"jogger","domain":"technical_tables","page":SOURCE_PAGE,"input_coverage_status":"ambiguous"},"policy":{"candidate_id_and_exact_text_cited":True,"selected_evidence_copied_without_reinterpretation":True,"source_page_layout_used_for_row_disambiguation":True,"adjacent_line_evidence_not_silently_attached":True,"master_data_changes":False,"approved_import_spec_generation":False,"automatic_promotion":False},"summary":{"candidate_count":16,"decision_counts":{s:counts.get(s,0) for s in sorted(DECISION_STATUSES)},"selected_evidence_signature_count":selected_count,"selected_evidence_record_count":selected_records,"candidates_with_selected_evidence":sum(x["selected_evidence_signature_count"]>0 for x in decisions),"candidates_without_selected_evidence":sum(x["selected_evidence_signature_count"]==0 for x in decisions)},"decisions":decisions,"semantic_boundaries":{"review_is_not_import_approval":True,"source_conflict_deferral_is_preserved":True,"signature_mismatch_does_not_authorize_cross_attribute_substitution":True,"no_configuration_projection_is_created":True},"next_package":{"name":NEXT_PACKAGE,"status":"planned","goal":"Review the 5 ambiguous technical candidates from the Duster mini-brochure page 20 against their 26 preserved evidence signatures without creating master-data rows or approved import specifications."}}
def render_markdown(payload:Mapping[str,Any])->str:
    s=payload["summary"]; c=s["decision_counts"]
    lines=["# Jogger Technical Page 19 Ambiguity Review","","Authored review of `residual_gap_002`. Decisions preserve the source page and do not approve imports.","","## Summary","","| Measure | Value |","| --- | ---: |",f"| Reviewed candidates | {s['candidate_count']} |",f"| Covered by selected evidence | {c['covered_by_selected_evidence']} |",f"| Partially covered | {c['partially_covered']} |",f"| Context-only non-import | {c['context_only_non_import']} |",f"| Deferred source conflict | {c['deferred_source_conflict']} |",f"| Unresolved signature mismatch | {c['unresolved_signature_mismatch']} |",f"| Selected evidence signatures | {s['selected_evidence_signature_count']} |",f"| Selected evidence records | {s['selected_evidence_record_count']} |","","## Candidate decisions","","| Line | Candidate | Decision | Selected signatures | Exact text |","| ---: | --- | --- | ---: | --- |"]
    for item in payload["decisions"]:
        exact=str(item["exact_text"]).replace("|","\\|"); lines.append(f"| {item['line_start']} | `{item['candidate_id']}` | `{item['authored_decision']}` | {item['selected_evidence_signature_count']} | {exact} |")
    lines.extend(["","## Residual authored findings",""])
    for item in payload["decisions"]:
        if item["authored_decision"] not in {"partially_covered","deferred_source_conflict","unresolved_signature_mismatch"}: continue
        lines.extend([f"### Line {item['line_start']} — `{item['candidate_id']}`","",item["rationale"]])
        for f in item["source_facts"]:
            values=", ".join(f"`{v}`" for v in f["source_values"]); lines.append(f"- `{f['attribute_code']}`: {values} — {f['reason']}")
        lines.append("")
    lines.extend(["## Safety boundary","","- no file under `data/master` is changed;","- no approved import specification is created or changed;","- no mismatched signature is substituted across attributes;","- contradictory Jogger mass labels and superseded Hybrid 155 values remain explicitly deferred.","","## Next package","",f"**{payload['next_package']['name']}** — {payload['next_package']['goal']}",""])
    return "\n".join(lines)
def ensure_safe_output(repository:Path,path:Path)->Path:
    resolved=(path if path.is_absolute() else repository/path).resolve()
    for restricted in (repository/"data/master",repository/"data/imports"):
        try: resolved.relative_to(restricted.resolve())
        except ValueError: continue
        raise JoggerPage19ReviewError(f"output path is restricted: {path}")
    return resolved
def verify_output(path:Path,expected:str,label:str)->None:
    try: actual=path.read_text(encoding="utf-8")
    except OSError as exc: raise JoggerPage19ReviewError(f"cannot read {label}: {exc}") from exc
    ensure(actual==expected,f"{label} differs from deterministic output")
def build_from_path(repository:Path,prioritization_path:Path)->tuple[dict[str,Any],str]:
    resolved=prioritization_path if prioritization_path.is_absolute() else repository/prioritization_path
    payload=build_review(load_json_object(resolved,"residual-gap prioritization"),repository); return payload,render_markdown(payload)
def parser()->argparse.ArgumentParser:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--prioritization",type=Path,default=DEFAULT_PRIORITIZATION); p.add_argument("--json",type=Path,default=DEFAULT_JSON); p.add_argument("--markdown",type=Path,default=DEFAULT_MARKDOWN); p.add_argument("--verify",action="store_true"); return p
def main(argv:Sequence[str]|None=None)->int:
    a=parser().parse_args(argv); repository=repository_root()
    try:
        payload,markdown=build_from_path(repository,a.prioritization); jp=ensure_safe_output(repository,a.json); mp=ensure_safe_output(repository,a.markdown); jt=canonical_json(payload)
        if a.verify:
            verify_output(jp,jt,"Jogger page-19 review JSON"); verify_output(mp,markdown,"Jogger page-19 review Markdown"); print("Jogger technical page-19 ambiguity review: PASS")
        else: write_atomic(jp,jt); write_atomic(mp,markdown); print(f"JSON report written to {jp}"); print(f"Markdown report written to {mp}")
        print(f"Candidates reviewed: {payload['summary']['candidate_count']}"); print(f"Selected evidence signatures: {payload['summary']['selected_evidence_signature_count']}"); print(f"Selected evidence records: {payload['summary']['selected_evidence_record_count']}"); return 0
    except JoggerPage19ReviewError as exc: print(f"ERROR: {exc}",file=sys.stderr); return 1
if __name__=="__main__": raise SystemExit(main())
