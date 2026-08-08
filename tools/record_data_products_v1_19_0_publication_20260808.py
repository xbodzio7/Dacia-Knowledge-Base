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
TAG='data-products-v1.19.0'
PUBLISHED_ON='2026-08-08'


def sha256(path:Path)->str:
    digest=hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda:handle.read(1024*1024),b''):
            digest.update(chunk)
    return digest.hexdigest()


assets={}
for name in ('dacia-knowledge-base-data-products-v1.19.0.zip','data-product-release-manifest.json','SHA256SUMS'):
    path=RELEASE_DIR/name
    assets[name]={'size_bytes':path.stat().st_size,'sha256':sha256(path)}

receipt={
    'version':1,
    'kind':'data_products_v1_19_0_publication',
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
    'configuration_shortlist_v1_19':{
        'selected_configuration_count':81,
        'eight_step_configurator_navigation':True,
        'non_appearance_commercial_items':34,
        'selector_offer_rows':167,
        'selector_offer_rows_with_price':162,
        'selector_offer_rows_without_price':5,
        'commercial_selection_session_storage':True,
        'commercial_selection_json_export':True,
        'commercial_selection_comparison_bundle_metadata':True,
        'compatibility_inference_performed':False,
        'exact_configurator_saved_states':18,
        'exact_standard_equipment_source_lines':1355,
        'exact_technical_categories':162,
        'exact_technical_source_lines':349,
        'technical_semantic_coercion_performed':False,
    },
    'semantic_boundaries':{
        'source_data_changed':False,
        'master_data_changed':False,
        'ranking_generated':False,
        'recommendations_generated':False,
        'inferred_values_generated':False,
        'commercial_dependency_graph_generated':False,
        'commercial_orderability_inferred':False,
        'appearance_catalogue_inferred':False,
        'cross_phase_promotion':False,
        'cross_grade_transfer':False,
        'cross_powertrain_transfer':False,
    },
    'assets':assets,
    'public_v1_18_0_immutable':True,
}
(ROOT/'data/reporting/data_products_v1_19_0_publication.json').write_text(
    json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',
    encoding='utf-8',
)

state_path=ROOT/'project/state.json'
state=json.loads(state_path.read_text(encoding='utf-8'))
state['updated_on']=PUBLISHED_ON
state['phase']='Data Products v1.19.0 Publication'
state['reference_delivery']={
    'name':'Data Products v1.19.0 Publication',
    'pull_request':PUBLICATION_PR,
    'head_sha':SOURCE_SHA,
    'quality_run':PUBLICATION_RUN_ID,
}
state['current_package']={
    'package_id':'data_products_v1_19_0_publication_001',
    'kind':'data_product_release',
    'name':'Data Products v1.19.0 Publication',
    'status':'complete',
    'goal':'Publish immutable v1.19.0 assets from the exact source SHA after double-build, offline-workspace and public-download verification.',
    'manifest_paths':[
        'data/reporting/data_products_v1_19_0_publication.json',
        'project/STATE_SUMMARY.md',
        'project/packages/data-products-v1.19.0-publication-20260808.md',
        'project/state.json',
        'tools/data_product_release.py',
        'tools/reporting/configuration_shortlist_technical_observation_release_integration.py',
        'tools/reporting/configuration_shortlist_equipment_groups.js',
        'tools/reporting/configuration_shortlist_v12_pricing.js',
        'tools/reporting/configuration_shortlist_selection.js',
        'tools/reporting/configuration_comparison_bundle.py',
        'data/reporting/configurator_ui_commercial_choice_readiness_20260807.json',
        'data/reporting/configurator_ui_grade_appearance_coverage_20260807.json',
        'data/reporting/cross_model_configurator_commercial_data.json',
        'data/reporting/cross_model_configurator_standard_equipment.json',
        'data/reporting/cross_model_configurator_technical_data.json',
        'data/reporting/cross_model_configurator_conflict_closure.json',
    ],
}
state['next_package']={
    'package_id':'post_v1_19_0_release_priority_selection_review_001',
    'kind':'priority_selection_review',
    'name':'Post-v1.19.0 Release Priority Selection Review',
    'status':'planned',
    'goal':'Inspect canonical product, source, user-interface and roadmap evidence after v1.19.0 publication and select one bounded next package.',
    'manifest_paths':[],
}
state_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

(ROOT/'project/packages/data-products-v1.19.0-publication-20260808.md').write_text(f'''# Data Products v1.19.0 Publication

Date: {PUBLISHED_ON}

## Result

The immutable `data-products-v1.19.0` release was published from exact source commit `{SOURCE_SHA}` by activation PR #{PUBLICATION_PR} in workflow run `{PUBLICATION_RUN_ID}`.

The release publishes the completed post-v1.18.0 configurator interaction increment through the established offline data-product pipeline: eight-step navigation, exact configuration-mapped packages and options, deterministic single-configuration summary, browser-session commercial selection state, additive JSON `commercial_selection` export and source-specific comparison-bundle commercial metadata.

The commercial selector remains source-bounded: 34 non-appearance items produce 167 selectable exact-configuration offer rows, 162 with captured prices and 5 valid Spring offers with unknown prices. Unknown prices remain unknown, never zero. No generic dependency/conflict graph or simultaneous-orderability inference was created, and `compatibility_inference_performed` remains false.

Appearance remains evidence-bounded. Saved colour, wheel and upholstery states are exact observations only and are not promoted into a complete availability catalogue. The release also preserves all 18 exact saved configurator states, 1,355 standard-equipment source lines, 162 grouped technical categories and 349 technical source lines from v1.18.0.

Both independent builds were byte-identical, the complete offline workspace passed verification, and the publicly downloaded assets matched the verified build byte for byte. Public `data-products-v1.18.0` remains immutable.

## Assets

- `dacia-knowledge-base-data-products-v1.19.0.zip`;
- `data-product-release-manifest.json`;
- `SHA256SUMS`.

Exact sizes and SHA-256 values are stored in `data/reporting/data_products_v1_19_0_publication.json`.

## Evidence boundary

This release introduces no source-data or master-data mutation, ranking, recommendation, inferred commercial compatibility, inferred simultaneous orderability, appearance-catalogue inference, cross-phase promotion, cross-grade transfer or cross-powertrain transfer.

## Next package

`post_v1_19_0_release_priority_selection_review_001` selects one bounded next package from canonical repository evidence after the v1.19.0 publication checkpoint.
''',encoding='utf-8')
