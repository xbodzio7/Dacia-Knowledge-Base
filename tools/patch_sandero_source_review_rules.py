from pathlib import Path

path = Path("tools/import_sandero_residual_source_closure_20260801.py")
text = path.read_text(encoding="utf-8")
old = '''    source_review["review_triage_keys"] = [item for item in triage if not targeted_triage_key(item)]
    write_json(SOURCE_REVIEW_INDEX, source_review)
'''
new = '''    source_review["review_triage_keys"] = [item for item in triage if not targeted_triage_key(item)]
    rules = source_review.get("rules")
    if not isinstance(rules, list):
        raise ClosureError("unexpected configuration source-review rules payload")
    resolved_rule_attributes = {attribute for _domain, _source, _configuration, attribute in TARGET_DECISIONS}
    source_review["rules"] = [
        rule
        for rule in rules
        if not isinstance(rule, Mapping)
        or str(rule.get("attribute_code", "")) not in resolved_rule_attributes
    ]
    write_json(SOURCE_REVIEW_INDEX, source_review)
'''
if old in text:
    text = text.replace(old, new, 1)
elif new not in text:
    raise SystemExit("source-review update block not found")

old_check = '''    analysis_payload = missing_analysis.collect(ROOT)
    stored_analysis = read_json(REPORTING / "existing_configuration_missing_data_analysis.json")
'''
new_check = '''    source_review = read_json(SOURCE_REVIEW_INDEX)
    rules = source_review.get("rules")
    if not isinstance(rules, list):
        raise ClosureError("unexpected configuration source-review rules payload")
    resolved_rule_attributes = {attribute for _domain, _source, _configuration, attribute in TARGET_DECISIONS}
    stale_rules = [
        rule
        for rule in rules
        if isinstance(rule, Mapping)
        and str(rule.get("attribute_code", "")) in resolved_rule_attributes
    ]
    if stale_rules:
        raise ClosureError(f"resolved source-review rules remain: {stale_rules}")
    analysis_payload = missing_analysis.collect(ROOT)
    stored_analysis = read_json(REPORTING / "existing_configuration_missing_data_analysis.json")
'''
if old_check in text:
    text = text.replace(old_check, new_check, 1)
elif new_check not in text:
    raise SystemExit("package check insertion point not found")

path.write_text(text, encoding="utf-8", newline="\n")
