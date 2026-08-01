from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise RuntimeError(f"expected one corrective anchor in {path}: {text.count(old)}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


shortlist = ROOT / "tools/configuration_shortlist.py"
replace_once(
    shortlist,
    '''        configuration = by_code.get(review["configuration_code"])
        facet = facet_by_key.get(review["comparison_key"])
        if configuration is None or facet is None:
            raise ShortlistError(
                "reviewed technical gap does not match the browser catalog: "
                f"{review['configuration_code']} / {review['comparison_key']}"
            )
''',
    '''        configuration = by_code.get(review["configuration_code"])
        facet = facet_by_key.get(review["comparison_key"])
        if configuration is None:
            raise ShortlistError(
                "reviewed technical gap references an unknown configuration: "
                f"{review['configuration_code']}"
            )
        if facet is None:
            if review["comparison_key"] != "gear_shift_indicator::all":
                raise ShortlistError(
                    "reviewed technical gap does not match the browser catalog: "
                    f"{review['configuration_code']} / {review['comparison_key']}"
                )
            facet = {
                "key": "gear_shift_indicator::all",
                "attribute_code": "gear_shift_indicator",
                "label": "Wskaźnik zmiany biegów",
                "category": "Transmission",
                "data_type": "boolean",
                "unit": "",
                "fuel_type_code": "",
                "fuel_type_label": "",
                "gear_number": "",
                "cargo_context": None,
                "cargo_context_signature": "",
                "cargo_context_label": "",
                "context": "",
            }
            comparison_facets.append(facet)
            facet_by_key[review["comparison_key"]] = facet
''',
)

pricing = ROOT / "tools/reporting/configuration_shortlist_v12_pricing.js"
replace_once(
    pricing,
    '''      candidate_amount_pln: Number.isFinite(Number(component.candidate_amount_pln))
        ? Number(component.candidate_amount_pln) : null,
''',
    '''      candidate_amount_pln: component.candidate_amount_pln === null
        || component.candidate_amount_pln === undefined
        || component.candidate_amount_pln === ""
        ? null
        : (Number.isFinite(Number(component.candidate_amount_pln))
          ? Number(component.candidate_amount_pln) : null),
''',
)
replace_once(
    pricing,
    '''    const candidate = Number(component && component.candidate_amount_pln);
    const hasCandidate = Number.isFinite(candidate);
''',
    '''    const rawCandidate = component && component.candidate_amount_pln;
    const candidate = rawCandidate === null || rawCandidate === undefined || rawCandidate === ""
      ? null : Number(rawCandidate);
    const hasCandidate = candidate !== null && Number.isFinite(candidate);
''',
)
