#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

ROOT=Path(os.environ.get('REPOSITORY_ROOT',Path.cwd())).resolve()
RELEASE_DIR=Path(os.environ['RELEASE_DIR'])
SOURCE_SHA=os.environ['SOURCE_SHA']
RELEASE_ID=os.environ.get('RELEASE_ID','')
PUBLICATION_PR=int(os.environ['PUBLICATION_PR'])
PUBLICATION_RUN_ID=int(os.environ['PUBLICATION_RUN_ID'])
TAG='data-products-v1.19.1'
PUBLISHED_ON='2026-08-08'


def sha256(path:Path)->str:
    digest=hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda:handle.read(1024*1024),b''):
            digest.update(chunk)
    return digest.hexdigest()


assets={}
for name in ('dacia-knowledge-base-data-products-v1.19.1.zip','data-product-release-manifest.json','SHA256SUMS'):
    path=RELEASE_DIR/name
    assets[name]={'size_bytes':path.stat().st_size,'sha256':sha256(path)}

receipt={
    'version':1,
    'kind':'data_products_v1_19_1_publication',
    'published_on':PUBLISHED_ON,
    'status':'complete',
    'tag':TAG,
    'release_id':int(RELEASE_ID) if RELEASE_ID else None,
    'source_commit':SOURCE_SHA,
    'activation_pull_request':PUBLICATION_PR,
    'publication_workflow_run':PUBLICATION_RUN_ID,
    'double_build_byte_identity':True,
    'offline_workspace_verification':'PASS',
    'public_download_byte_identity':True,
    'configuration_shortlist_v1_19_1':{
        'selected_configuration_count':81,
        'eight_step_configurator_navigation':True,
        'non_appearance_commercial_items':34,
        'selector_offer_rows':164,
        'selector_offer_rows_with_price':162,
        'selector_offer_rows_without_price':2,
        'commercial_selection_session_storage':True,
        'commercial_selection_json_export':True,
        'commercial_selection_comparison_bundle_metadata':True,
        'compatibility_inference_performed':False,
        'exact_configurator_saved_states':18,
        'exact_standard_equipment_source_lines':1355,
        'exact_technical_categories':162,
        'exact_technical_source_lines':349,
        'technical_semantic_coercion_performed':False,
        'spring_type2_historical_option_rows_preserved':3,
        'spring_type2_exact_current_standard_rows_preserved':3,
        'spring_type2_current_selector_rows_suppressed':3,
        'spring_current_selector_offer_rows':7,
        'spring_current_selector_priced_rows':5,
        'spring_current_selector_unpriced_rows':2,
        'spring_remaining_unpriced_items':[
            'spring_techno_package',
            'spring_dc40_charging_option',
        ],
        'historical_as_of_view_preserved':True,
        'domestic_socket_flexicharger_selector_preserved':True,
        'duster_offer_selected_state_semantics_preserved':True,
    },
    'semantic_boundaries':{
        'source_data_changed':False,
        'master_data_changed':False,
        'ranking_generated':False,
        'recommendations_generated':False,
        'inferred_values_generated':False,
        'commercial_dependency_graph_generated':False,
        'commercial_orderability_inferred':False,
        'generic_commercial_precedence_rule_generated':False,
        'appearance_catalogue_inferred':False,
        'cross_phase_promotion':False,
        'cross_grade_transfer':False,
        'cross_powertrain_transfer':False,
    },
    'assets':assets,
    'public_v1_19_0_immutable':True,
    'public_v1_18_0_immutable':True,
}
(ROOT/'data/reporting/data_products_v1_19_1_publication.json').write_text(
    json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',
    encoding='utf-8',
)

state_path=ROOT/'project/state.json'
state=json.loads(state_path.read_text(encoding='utf-8'))
state['updated_on']=PUBLISHED_ON
state['phase']='Data Products v1.19.1 Publication'
state['reference_delivery']={
    'name':'Data Products v1.19.1 Publication',
    'pull_request':PUBLICATION_PR,
    'head_sha':SOURCE_SHA,
    'quality_run':PUBLICATION_RUN_ID,
}
state['current_package']={
    'package_id':'data_products_v1_19_1_publication_001',
    'kind':'data_product_release',
    'name':'Data Products v1.19.1 Publication',
    'status':'complete',
    'goal':'Publish immutable v1.19.1 assets from the exact source SHA after double-build, offline-workspace and public-download verification.',
    'manifest_paths':[
        'data/reporting/data_products_v1_19_1_publication.json',
        'data/reporting/spring_type2_current_selector_reconciliation_20260808.json',
        'project/STATE_SUMMARY.md',
        'project/packages/data-products-v1.19.1-publication-20260808.md',
        'project/state.json',
        'tools/data_product_release.py',
        'tools/reporting/commercial_offers.py',
        'tools/reporting/configuration_shortlist_technical_observation_release_integration.py',
        'tools/reporting/configuration_shortlist_equipment_groups.js',
        'tools/reporting/configuration_shortlist_v12_pricing.js',
        'tools/reporting/configuration_shortlist_selection.js',
        'tools/reporting/configuration_comparison_bundle.py',
        'data/reporting/configurator_ui_grade_appearance_coverage_20260807.json',
        'data/reporting/cross_model_configurator_commercial_data.json',
        'data/reporting/cross_model_configurator_standard_equipment.json',
        'data/reporting/cross_model_configurator_technical_data.json',
        'data/reporting/cross_model_configurator_conflict_closure.json',
    ],
}
state['next_package']={
    'package_id':'sandero_stepway_configurator_data_completion_001',
    'kind':'configurator_data_completion',
    'name':'Sandero and Sandero Stepway Configurator Data Completion',
    'status':'planned',
    'goal':'Complete source-backed current configurator data for Sandero and Sandero Stepway, prioritizing the exact Design choices available for each relevant configuration before generating the next configurator-choice interface version.',
    'manifest_paths':[],
}
state_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

(ROOT/'project/packages/data-products-v1.19.1-publication-20260808.md').write_text(f'''# Data Products v1.19.1 Publication

Date: {PUBLISHED_ON}

## Result

The immutable `data-products-v1.19.1` release was published from exact source commit `{SOURCE_SHA}` by activation PR #{PUBLICATION_PR} in workflow run `{PUBLICATION_RUN_ID}`.

This patch release publishes the bounded Spring Type 2 current-selector reconciliation completed in PR #617 without changing historical source records or canonical master evidence. The three February brochure-backed Type 2 optional mappings remain preserved, as do the three later exact-current observations that the supplied Type 2 cable is standard for Spring Essential electric 70, Expression electric 70 and Extreme electric 100.

The current commercial selector now exposes 164 offer rows: 162 priced and 2 legitimately unpriced. Spring contributes 7 current selector offers, 5 priced and 2 unpriced. The only remaining unpriced current Spring questions are `spring_techno_package` and `spring_dc40_charging_option` for Spring Expression electric 70. Historical `as_of` visibility, the separate domestic-socket/FlexiCharger option and the existing Duster offer-plus-selected-state semantics remain unchanged.

The release preserves all established v1.19.0 interface behavior: eight-step configurator navigation, deterministic single-configuration summary, browser-session commercial selection state, additive JSON export and comparison-bundle metadata. `compatibility_inference_performed` remains false. It also preserves all 18 exact saved configurator states, 1,355 standard-equipment source lines, 162 grouped technical categories and 349 technical source lines.

Both independent builds were byte-identical, the complete offline workspace passed verification, and the publicly downloaded assets matched the verified build byte for byte. Public `data-products-v1.19.0` and `data-products-v1.18.0` remain unchanged.

## Assets

- `dacia-knowledge-base-data-products-v1.19.1.zip`;
- `data-product-release-manifest.json`;
- `SHA256SUMS`.

Exact sizes and SHA-256 values are stored in `data/reporting/data_products_v1_19_1_publication.json`.

## Evidence boundary

This release introduces no source-data or master-data mutation, generic commercial precedence rule, dependency/conflict graph, simultaneous-orderability inference, ranking, recommendation, inferred values, appearance-catalogue inference, cross-phase promotion, cross-grade transfer or cross-powertrain transfer.

## Next package

`sandero_stepway_configurator_data_completion_001` completes the source-backed current configurator data for Sandero and Sandero Stepway, with priority on exact Design choices for the relevant configurations. The next interface version follows only after that data-completion package.
''',encoding='utf-8')
