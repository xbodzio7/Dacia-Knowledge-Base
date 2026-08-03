#!/usr/bin/env bash
set -euo pipefail

export GH_TOKEN="${GH_TOKEN:?}"
export PUBLICATION_SOURCE_SHA="${PUBLICATION_SOURCE_SHA:?}"
export SOURCE_SHA="${PUBLICATION_SOURCE_SHA}"
export RELEASE_DIR="${RUNNER_TEMP}/release-a"
export REPOSITORY_ROOT="${GITHUB_WORKSPACE}"

actual_sha="$(git rev-parse HEAD)"
if [[ "${actual_sha}" != "${PUBLICATION_SOURCE_SHA}" ]]; then
  echo "Checked-out source ${actual_sha} differs from required ${PUBLICATION_SOURCE_SHA}." >&2
  exit 1
fi

python - <<'PY'
import json
from pathlib import Path
state = json.loads(Path('project/state.json').read_text(encoding='utf-8'))
assert state['next_package']['package_id'] == 'data_products_v1_13_0_publication_001'
assert state['execution_policy']['release_double_build_required'] is True
assert state['execution_policy']['release_exact_source_sha_required'] is True
PY

if gh release view data-products-v1.13.0 >/dev/null 2>&1; then
  echo 'Release already exists; refusing to rewrite it.' >&2
  exit 1
fi
if git show-ref --tags --verify --quiet refs/tags/data-products-v1.13.0; then
  echo 'Tag already exists; refusing to rewrite it.' >&2
  exit 1
fi

python -m unittest -q \
  tests.test_portfolio_model_family_release_integration \
  tests.test_data_product_release \
  tests.test_data_product_release_download
python tools/dkb.py project-state --check

python tools/dkb.py data-product-release \
  --output-directory "${RUNNER_TEMP}/release-a" \
  --version 1.13.0 \
  --commit-sha "${PUBLICATION_SOURCE_SHA}"
python tools/dkb.py data-product-release \
  --output-directory "${RUNNER_TEMP}/release-b" \
  --version 1.13.0 \
  --commit-sha "${PUBLICATION_SOURCE_SHA}"
diff -qr "${RUNNER_TEMP}/release-a" "${RUNNER_TEMP}/release-b"
python tools/dkb.py data-product-release \
  --output-directory "${RUNNER_TEMP}/release-a" \
  --version 1.13.0 \
  --commit-sha "${PUBLICATION_SOURCE_SHA}" \
  --verify

export RELEASE_ASSETS="${RUNNER_TEMP}/release-a"
export OFFLINE_WORKSPACE="${RUNNER_TEMP}/workspace"
PYTHONPATH=tools python - <<'PY'
import os
import shutil
from pathlib import Path
from reporting.data_product_release_download import (
    ASSETS_DIRECTORY_NAME,
    CONTENTS_DIRECTORY_NAME,
    _extract_verified_contents,
)
from reporting.data_product_release_model import verify_release_assets
from reporting.data_product_workspace_index import write_workspace_index

release_assets = Path(os.environ['RELEASE_ASSETS'])
workspace = Path(os.environ['OFFLINE_WORKSPACE'])
assets = workspace / ASSETS_DIRECTORY_NAME
contents = workspace / CONTENTS_DIRECTORY_NAME
shutil.copytree(release_assets, assets)
manifest = verify_release_assets(assets)
entry_points = _extract_verified_contents(assets, contents, manifest)
metadata = {
    'release_version': manifest['release_version'],
    'release_tag': manifest['release_tag'],
    'repository_commit': manifest['repository_commit'],
    'release_url': (
        'https://github.com/xbodzio7/Dacia-Knowledge-Base/releases/tag/'
        + manifest['release_tag']
    ),
}
write_workspace_index(workspace, manifest, metadata)
expected = {
    'model_family_summary_html': (
        'contents/model-families/portfolio_model_family_summary.html'
    ),
    'model_family_comparison_matrix_html': (
        'contents/model-families/portfolio_model_family_comparison_matrix.html'
    ),
}
for key, relative_path in expected.items():
    assert entry_points[key] == relative_path
    assert (workspace / relative_path).is_file()
index = (workspace / 'index.html').read_text(encoding='utf-8')
assert 'Model family summary' in index
assert 'Model family comparison matrix' in index
assert expected['model_family_summary_html'] in index
assert expected['model_family_comparison_matrix_html'] in index
matrix = (
    workspace / expected['model_family_comparison_matrix_html']
).read_text(encoding='utf-8')
assert matrix.startswith('<!doctype html>')
assert 'creates no configuration pair' in matrix
assert 'data-state="not_stated"' in matrix
PY
python tools/dkb.py data-product-workspace-verify \
  --workspace-directory "${RUNNER_TEMP}/workspace" \
  --json

unzip -p \
  "${RUNNER_TEMP}/release-a/dacia-knowledge-base-data-products-v1.13.0.zip" \
  RELEASE_NOTES.md > "${RUNNER_TEMP}/release-notes.md"
if [[ "$(grep -c '^## v1.13.0 portfolio model-family comparison matrix$' "${RUNNER_TEMP}/release-notes.md")" != "1" ]]; then
  echo 'Expected exactly one v1.13.0 release-notes section.' >&2
  exit 1
fi
grep -F 'model_family_comparison_matrix_html' "${RUNNER_TEMP}/release-notes.md"
grep -F 'Public `data-products-v1.12.1` remains immutable' "${RUNNER_TEMP}/release-notes.md"

gh release create data-products-v1.13.0 \
  "${RUNNER_TEMP}/release-a/dacia-knowledge-base-data-products-v1.13.0.zip" \
  "${RUNNER_TEMP}/release-a/data-product-release-manifest.json" \
  "${RUNNER_TEMP}/release-a/SHA256SUMS" \
  --target "${PUBLICATION_SOURCE_SHA}" \
  --title 'Dacia Knowledge Base Data Products v1.13.0' \
  --notes-file "${RUNNER_TEMP}/release-notes.md"
RELEASE_ID="$(gh release view data-products-v1.13.0 --json databaseId -q '.databaseId')"

mkdir "${RUNNER_TEMP}/public"
gh release download data-products-v1.13.0 --dir "${RUNNER_TEMP}/public"
diff -q \
  "${RUNNER_TEMP}/release-a/dacia-knowledge-base-data-products-v1.13.0.zip" \
  "${RUNNER_TEMP}/public/dacia-knowledge-base-data-products-v1.13.0.zip"
diff -q \
  "${RUNNER_TEMP}/release-a/data-product-release-manifest.json" \
  "${RUNNER_TEMP}/public/data-product-release-manifest.json"
diff -q \
  "${RUNNER_TEMP}/release-a/SHA256SUMS" \
  "${RUNNER_TEMP}/public/SHA256SUMS"
python tools/dkb.py data-product-release \
  --output-directory "${RUNNER_TEMP}/public" \
  --version 1.13.0 \
  --commit-sha "${PUBLICATION_SOURCE_SHA}" \
  --verify

export RELEASE_ID
export PUBLICATION_PR="${PUBLICATION_PR:?}"
export PUBLICATION_RUN_ID="${GITHUB_RUN_ID}"
python tools/record_data_products_v1_13_0_publication_20260803.py
python tools/dkb.py project-state --apply
python tools/dkb.py documentation-baseline --apply
python tools/dkb.py project-state --check

rm -f tools/publish_data_products_v1_13_0_20260803.sh
rm -f tools/record_data_products_v1_13_0_publication_20260803.py

git config user.name 'github-actions[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
git add -A
git commit -m 'release(data-products): record v1.13.0 publication'
git push origin HEAD:main
