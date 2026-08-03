#!/usr/bin/env bash
set -euo pipefail

export GH_TOKEN="${GH_TOKEN:?}"
export RELEASE_DIR="${RUNNER_TEMP}/release-a"
export PUBLICATION_SOURCE_SHA="${PUBLICATION_SOURCE_SHA:-${GITHUB_SHA}}"
export SOURCE_SHA="${PUBLICATION_SOURCE_SHA}"

python - <<'PY'
import json
from pathlib import Path
state = json.loads(Path('project/state.json').read_text(encoding='utf-8'))
assert state['next_package']['package_id'] == 'data_products_v1_12_1_publication_001'
assert state['execution_policy']['release_double_build_required'] is True
assert state['execution_policy']['release_exact_source_sha_required'] is True
PY

if gh release view data-products-v1.12.1 >/dev/null 2>&1; then
  echo 'Release already exists; refusing to rewrite it.' >&2
  exit 1
fi
if git rev-parse data-products-v1.12.1 >/dev/null 2>&1; then
  echo 'Tag already exists; refusing to rewrite it.' >&2
  exit 1
fi

python -m unittest -q \
  tests.test_data_products_v1_12_1_corrective_release \
  tests.test_portfolio_model_family_release_integration \
  tests.test_portfolio_model_family_workspace_entry_point \
  tests.test_data_product_release \
  tests.test_data_product_release_download
python tools/dkb.py project-state --check

python tools/dkb.py data-product-release --output-directory "${RUNNER_TEMP}/release-a" --version 1.12.1 --commit-sha "${PUBLICATION_SOURCE_SHA}"
python tools/dkb.py data-product-release --output-directory "${RUNNER_TEMP}/release-b" --version 1.12.1 --commit-sha "${PUBLICATION_SOURCE_SHA}"
diff -qr "${RUNNER_TEMP}/release-a" "${RUNNER_TEMP}/release-b"
python tools/dkb.py data-product-release --output-directory "${RUNNER_TEMP}/release-a" --verify

export RELEASE_ASSETS="${RUNNER_TEMP}/release-a"
export OFFLINE_WORKSPACE="${RUNNER_TEMP}/workspace"
PYTHONPATH=tools python - <<'PY'
import os
import shutil
from pathlib import Path
from reporting.data_product_release_download import ASSETS_DIRECTORY_NAME, CONTENTS_DIRECTORY_NAME, _extract_verified_contents
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
    'release_url': 'https://github.com/xbodzio7/Dacia-Knowledge-Base/releases/tag/' + manifest['release_tag'],
}
write_workspace_index(workspace, manifest, metadata)
assert entry_points['model_family_summary_html'] == 'contents/model-families/portfolio_model_family_summary.html'
assert (workspace / entry_points['model_family_summary_html']).is_file()
index = (workspace / 'index.html').read_text(encoding='utf-8')
assert 'Model family summary' in index
assert 'contents/model-families/portfolio_model_family_summary.html' in index
cross_model = (contents / 'cross-model' / 'cross-model-comparison-view.html').read_text(encoding='utf-8')
assert '../model-families/portfolio_model_family_summary.html' in cross_model
PY
python tools/dkb.py data-product-workspace-verify --workspace-directory "${RUNNER_TEMP}/workspace" --json
unzip -p "${RUNNER_TEMP}/release-a/dacia-knowledge-base-data-products-v1.12.1.zip" RELEASE_NOTES.md > "${RUNNER_TEMP}/release-notes.md"
grep -F 'v1.12.1 corrective workspace interface' "${RUNNER_TEMP}/release-notes.md"

gh release create data-products-v1.12.1 \
  "${RUNNER_TEMP}/release-a/dacia-knowledge-base-data-products-v1.12.1.zip" \
  "${RUNNER_TEMP}/release-a/data-product-release-manifest.json" \
  "${RUNNER_TEMP}/release-a/SHA256SUMS" \
  --target "${PUBLICATION_SOURCE_SHA}" \
  --title 'Dacia Knowledge Base Data Products v1.12.1' \
  --notes-file "${RUNNER_TEMP}/release-notes.md"
RELEASE_ID="$(gh release view data-products-v1.12.1 --json databaseId -q '.databaseId')"

mkdir "${RUNNER_TEMP}/public"
gh release download data-products-v1.12.1 --dir "${RUNNER_TEMP}/public"
diff -q "${RUNNER_TEMP}/release-a/dacia-knowledge-base-data-products-v1.12.1.zip" "${RUNNER_TEMP}/public/dacia-knowledge-base-data-products-v1.12.1.zip"
diff -q "${RUNNER_TEMP}/release-a/data-product-release-manifest.json" "${RUNNER_TEMP}/public/data-product-release-manifest.json"
diff -q "${RUNNER_TEMP}/release-a/SHA256SUMS" "${RUNNER_TEMP}/public/SHA256SUMS"
python tools/dkb.py data-product-release --output-directory "${RUNNER_TEMP}/public" --verify

export RELEASE_ID PUBLICATION_PR=497 PUBLICATION_RUN_ID="${GITHUB_RUN_ID}"
python tools/record_data_products_v1_12_1_publication_20260803.py
python tools/dkb.py project-state --apply
python tools/dkb.py documentation-baseline --apply
python tools/dkb.py project-state --check

python - <<'PY'
from pathlib import Path
path = Path('.github/workflows/data-product-release.yml')
marker = '  # BEGIN TEMPORARY DATA PRODUCTS V1.12.1 PUBLISHER\n'
text = path.read_text(encoding='utf-8')
path.write_text(text.split(marker, 1)[0].rstrip() + '\n', encoding='utf-8')
PY
rm tools/publish_data_products_v1_12_1_20260803.sh
rm tools/record_data_products_v1_12_1_publication_20260803.py
rm .github/workflows/temporary-publish-data-products-v1.12.1.yml
rm project/packages/data-products-v1.12.1-publication-trigger-20260803.md
rm project/packages/data-products-v1.12.1-quality-publisher-bridge-20260803.md

git config user.name 'github-actions[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
git add -A
git commit -m 'release(data-products): record v1.12.1 publication'
git push origin HEAD:main
