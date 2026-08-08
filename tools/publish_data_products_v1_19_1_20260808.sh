#!/usr/bin/env bash
set -euo pipefail

export GH_TOKEN="${GH_TOKEN:?}"
export PUBLICATION_SOURCE_SHA="${PUBLICATION_SOURCE_SHA:?}"
export SOURCE_SHA="${PUBLICATION_SOURCE_SHA}"
export RELEASE_DIR="${RUNNER_TEMP}/release-a"
export REPOSITORY_ROOT="${GITHUB_WORKSPACE}"

[[ "$(git rev-parse HEAD)" == "${PUBLICATION_SOURCE_SHA}" ]] || { echo "Wrong publication source" >&2; exit 1; }

python - <<'PY'
import json
from pathlib import Path
state=json.loads(Path('project/state.json').read_text(encoding='utf-8'))
assert state['next_package']['package_id']=='data_products_v1_19_1_publication_001'
assert state['execution_policy']['release_double_build_required'] is True
assert state['execution_policy']['release_exact_source_sha_required'] is True
PY

if gh release view data-products-v1.19.1 >/dev/null 2>&1; then echo "Release already exists." >&2; exit 1; fi
if git show-ref --tags --verify --quiet refs/tags/data-products-v1.19.1; then echo "Tag already exists." >&2; exit 1; fi
[[ "$(git rev-list -n1 data-products-v1.19.0)" == "c121e600de48576f2da53cba2eb42075b6632504" ]] || { echo "Previous immutable v1.19.0 tag moved" >&2; exit 1; }
[[ "$(git rev-list -n1 data-products-v1.18.0)" == "a13587ff0bf9d683d7a450f0fbb15aa610693f03" ]] || { echo "Previous immutable v1.18.0 tag moved" >&2; exit 1; }

python -m unittest -q \
  tests.test_data_product_release \
  tests.test_data_product_release_download \
  tests.test_configuration_selection_export \
  tests.test_configuration_comparison_bundle \
  tests.test_configuration_shortlist \
  tests.test_spring_commercial_packages
node tests/contracts/configuration_shortlist_v12_contract.js
python tools/dkb.py project-state --check

python - <<'PY'
import json
from pathlib import Path
root=Path('.')
closure=json.loads((root/'data/reporting/cross_model_configurator_conflict_closure.json').read_text(encoding='utf-8'))
assert len(closure['rows'])==18
assert len({row['canonical_configuration_code'] for row in closure['rows']})==18
assert len({row['configuration_code'] for row in closure['rows']})==18
standard=json.loads((root/'data/reporting/cross_model_configurator_standard_equipment.json').read_text(encoding='utf-8'))
documents=standard['documents']
assert len(documents)==18
assert sum(len(c['source_lines']) for d in documents for c in d['categories'])==1355
technical=json.loads((root/'data/reporting/cross_model_configurator_technical_data.json').read_text(encoding='utf-8'))
docs=technical['documents']
assert len(docs)==18
assert sum(len(d['categories']) for d in docs)==162
assert sum(len(c['source_lines']) for d in docs for c in d['categories'])==349
reconciliation=json.loads((root/'data/reporting/spring_type2_current_selector_reconciliation_20260808.json').read_text(encoding='utf-8'))
assert reconciliation['historical_mapping_rows_preserved']==3
assert reconciliation['exact_current_standard_rows_preserved']==3
assert reconciliation['selector_offer_rows_after']==164
assert reconciliation['priced_selector_offer_rows_after']==162
assert reconciliation['unpriced_selector_offer_rows_after']==2
assert reconciliation['spring_selector_offer_rows_after']==7
assert reconciliation['spring_priced_selector_offer_rows_after']==5
assert reconciliation['spring_unpriced_selector_offer_rows_after']==2
assert reconciliation['domestic_socket_charging_cable_selector_changed'] is False
assert reconciliation['duster_selected_state_semantics_changed'] is False
assert reconciliation['generic_commercial_precedence_rule_created'] is False
assert reconciliation['generic_dependency_conflict_orderability_model_created'] is False
assert reconciliation['historical_as_of_view_preserved'] is True
assert reconciliation['master_data_mutated'] is False
assert reconciliation['source_data_mutated'] is False
remaining={(item['configuration_code'],item['commercial_item_code']) for item in reconciliation['remaining_unpriced_current_questions']}
assert remaining=={
    ('spring_expression_electric70_automatic','spring_techno_package'),
    ('spring_expression_electric70_automatic','spring_dc40_charging_option'),
}
appearance=json.loads((root/'data/reporting/configurator_ui_grade_appearance_coverage_20260807.json').read_text(encoding='utf-8'))
appearance_coverage=appearance['coverage']
assert appearance_coverage['current_model_families']==6
assert appearance_coverage['current_grade_surfaces']==21
assert appearance_coverage['grade_surfaces_with_representative_exact_selected_appearance']==21
PY

for dir in release-a release-b; do
  python tools/dkb.py data-product-release --output-directory "${RUNNER_TEMP}/${dir}" --version 1.19.1 --commit-sha "${PUBLICATION_SOURCE_SHA}"
done
diff -qr "${RUNNER_TEMP}/release-a" "${RUNNER_TEMP}/release-b"
python tools/dkb.py data-product-release --output-directory "${RUNNER_TEMP}/release-a" --version 1.19.1 --commit-sha "${PUBLICATION_SOURCE_SHA}" --verify

export RELEASE_ASSETS="${RUNNER_TEMP}/release-a"
export OFFLINE_WORKSPACE="${RUNNER_TEMP}/workspace"
PYTHONPATH=tools python - <<'PY'
import os, shutil
from pathlib import Path
from zipfile import ZipFile
from reporting.data_product_release_download import ASSETS_DIRECTORY_NAME, CONTENTS_DIRECTORY_NAME, _extract_verified_contents
from reporting.data_product_release_model import verify_release_assets
from reporting.data_product_workspace_index import write_workspace_index
release=Path(os.environ['RELEASE_ASSETS']); workspace=Path(os.environ['OFFLINE_WORKSPACE'])
assets=workspace/ASSETS_DIRECTORY_NAME; contents=workspace/CONTENTS_DIRECTORY_NAME
shutil.copytree(release, assets)
manifest=verify_release_assets(assets)
assert manifest['release_version']=='1.19.1'
assert manifest['selected_configuration_count']==81
assert manifest['configuration_shortlist_spring_media_normalized'] is True
assert manifest['configuration_shortlist_configurator_observation_filters'] is True
assert manifest['configuration_shortlist_exact_technical_observation_filters'] is True
assert manifest['configurator_saved_state_count']==18
assert manifest['configurator_standard_equipment_source_line_count']==1355
assert manifest['configurator_technical_category_count']==162
assert manifest['configurator_technical_source_line_count']==349
assert manifest['configurator_technical_semantic_coercion_performed'] is False
entry=_extract_verified_contents(assets, contents, manifest)
write_workspace_index(workspace, manifest, {'release_version':manifest['release_version'],'release_tag':manifest['release_tag'],'repository_commit':manifest['repository_commit'],'release_url':'https://github.com/xbodzio7/Dacia-Knowledge-Base/releases/tag/'+manifest['release_tag']})
for key in ('model_family_summary_html','model_family_comparison_matrix_html','model_version_comparison_matrix_html','source_coverage_matrix_html','powertrain_transmission_matrix_html'):
    assert (workspace/entry[key]).is_file()
archive=release/'dacia-knowledge-base-data-products-v1.19.1.zip'
with ZipFile(archive) as z: shortlist=z.read('shortlist/configuration-shortlist.html').decode('utf-8')
for marker in (
    'configurator_step_navigation_v1',
    'Pakiety i opcje',
    'Podsumowanie',
    'commercial_selection',
    'compatibility_inference_performed',
    'dkb-commercial-selections-v1',
    'Dokładne wiersze wyposażenia standardowego',
    'Dokładne wiersze danych technicznych',
    'Wybrany kolor zapisanej konfiguracji',
):
    assert marker in shortlist, marker
assert 'https://3dv2.renault.com/' not in shortlist
PY
python tools/dkb.py data-product-workspace-verify --workspace-directory "${RUNNER_TEMP}/workspace" --json

unzip -p "${RUNNER_TEMP}/release-a/dacia-knowledge-base-data-products-v1.19.1.zip" RELEASE_NOTES.md > "${RUNNER_TEMP}/release-notes.md"
grep -F "v1.19.1" "${RUNNER_TEMP}/release-notes.md"

REMOTE_MAIN="$(git ls-remote origin refs/heads/main | awk '{print $1}')"
[[ "${REMOTE_MAIN}" == "${PUBLICATION_SOURCE_SHA}" ]] || { echo "main moved before publication" >&2; exit 1; }
if gh release view data-products-v1.19.1 >/dev/null 2>&1; then echo "Release appeared during verification." >&2; exit 1; fi

gh release create data-products-v1.19.1 \
  "${RUNNER_TEMP}/release-a/dacia-knowledge-base-data-products-v1.19.1.zip" \
  "${RUNNER_TEMP}/release-a/data-product-release-manifest.json" \
  "${RUNNER_TEMP}/release-a/SHA256SUMS" \
  --target "${PUBLICATION_SOURCE_SHA}" --title "Dacia Knowledge Base Data Products v1.19.1" --notes-file "${RUNNER_TEMP}/release-notes.md"

RELEASE_ID="$(gh release view data-products-v1.19.1 --json databaseId -q '.databaseId')"
mkdir "${RUNNER_TEMP}/public"
gh release download data-products-v1.19.1 --dir "${RUNNER_TEMP}/public"
for name in dacia-knowledge-base-data-products-v1.19.1.zip data-product-release-manifest.json SHA256SUMS; do diff -q "${RUNNER_TEMP}/release-a/${name}" "${RUNNER_TEMP}/public/${name}"; done
python tools/dkb.py data-product-release --output-directory "${RUNNER_TEMP}/public" --version 1.19.1 --commit-sha "${PUBLICATION_SOURCE_SHA}" --verify
[[ "$(git rev-list -n1 data-products-v1.19.0)" == "c121e600de48576f2da53cba2eb42075b6632504" ]] || { echo "Previous immutable v1.19.0 tag moved during publication" >&2; exit 1; }
[[ "$(git rev-list -n1 data-products-v1.18.0)" == "a13587ff0bf9d683d7a450f0fbb15aa610693f03" ]] || { echo "Previous immutable v1.18.0 tag moved during publication" >&2; exit 1; }

export RELEASE_ID PUBLICATION_PR="${PUBLICATION_PR:?}" PUBLICATION_RUN_ID="${GITHUB_RUN_ID}"
python tools/record_data_products_v1_19_1_publication_20260808.py
python tools/dkb.py project-state --apply
python tools/dkb.py documentation-baseline --apply
python tools/dkb.py project-state --check
rm -f tools/publish_data_products_v1_19_1_20260808.sh tools/record_data_products_v1_19_1_publication_20260808.py

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git add -A
git commit -m "release(data-products): record v1.19.1 publication"
git push origin HEAD:main
