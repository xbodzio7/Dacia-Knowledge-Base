#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ACCELERATED_DOC = '# Accelerated Milestone Closure Mode\n\n**Project:** Dacia Knowledge Base (DKB)  \n**Status:** Active  \n**Effective date:** 2026-08-01\n\n## Purpose\n\nThis mode shortens the path from an already bounded backlog to a verified milestone or release without weakening evidence rules, final validation, or repository traceability.\n\nIt is used when the remaining work is known, logically related and small enough that repeated full-matrix runs and repeated Pull Request setup would add more overhead than safety.\n\n## Activation\n\nThe mode is active when `project/state.json` contains:\n\n```json\n"execution_policy": {\n  "mode": "accelerated_milestone_closure"\n}\n```\n\nThe canonical state may activate or deactivate the mode. Conversation history alone never activates it.\n\n## Operating rules\n\n1. Resolve the exact current package and remaining bounded backlog from repository state and generated analysis.\n2. Combine multiple source reviews only when they form one logical closure package and preserve exact source, configuration, date, fuel, transmission and model-year boundaries.\n3. Stabilize the branch before opening the Pull Request whenever repository tooling permits safe branch-only work.\n4. During implementation run focused tests for the changed paths and contracts.\n5. Batch mechanical repairs such as generated snapshots, counters and deterministic manifests before the final quality run.\n6. Run the complete required quality matrix once against the final Pull Request head SHA.\n7. Merge only when the current head is green, mergeable and review-clean.\n8. For a release, build twice from the exact release source commit, prove byte identity, verify the offline workspace and publish immutable assets.\n9. Record the publication result and restore the next bounded package in canonical state.\n10. Do not create temporary automation whose implementation and maintenance cost exceeds the remaining backlog.\n\n## Non-negotiable boundaries\n\nAcceleration never permits:\n\n- skipping the final complete quality gate;\n- publishing from an unverified or stale SHA;\n- combining unrelated domains into one Pull Request;\n- inferring missing source facts;\n- transferring values between configurations, fuels, transmissions, grades, model years or sources;\n- replacing missing evidence with `not_available`, zero or a guessed value;\n- rewriting an existing public release;\n- bypassing an `ACTION_REQUIRED` boundary.\n\n## Pull Request rule\n\nOne logical package still maps to one Pull Request.\n\nA closure package may contain several closely related sources or the release preparation and publication automation when they serve one explicit milestone and share one acceptance contract. Unrelated work remains separate.\n\n## Validation cadence\n\nDuring development:\n\n- run focused unit and contract tests;\n- regenerate only affected deterministic outputs;\n- avoid repeated full-matrix runs after each mechanical correction.\n\nAt the final head:\n\n- run all required Linux, Windows and supported-Python checks;\n- run the complete repository quality gate;\n- verify canonical project state;\n- verify release assets when a release is in scope.\n\n## Release cadence\n\nAn accelerated release may use one Pull Request plus a post-merge publication workflow when all of the following are true:\n\n- the workflow targets the exact merge SHA;\n- assets are built twice and compared byte for byte;\n- the tag and release are absent before publication;\n- public assets are verified after upload;\n- the workflow records the publication and removes itself;\n- a later commit cannot silently change the already published assets.\n\n## End of document\n'
PACKAGE_DOC = '# Data Products v1.10.0 Accelerated Release Preparation\n\nDate: 2026-08-01\n\n## Purpose\n\nPrepare one accelerated minor release that publishes the current repository data products and the already merged interactive shortlist repairs.\n\nThe public `data-products-v1.9.0` remains immutable.\n\n## User-facing interface delta\n\nThe release includes the interface repair merged in Pull Request #427:\n\n- one forced dark theme across the interactive shortlist;\n- grouped duplicate commercial grade labels while retaining exact version codes;\n- model headers that remain visible during vertical scrolling;\n- parameter and category labels that remain visible during horizontal scrolling;\n- deterministic parameter and configuration column widths;\n- a sticky category label cell instead of an oversized category colspan cell.\n\nThe release also retains the existing pair-type filter and multi-configuration comparison behavior.\n\n## Data delta\n\nThe release uses the current source-backed repository state after v1.9.0, including the Spring catalogue foundation and subsequent exact technical and equipment observations.\n\nNo cross-scope pair, ranking, recommendation or inferred value is introduced.\n\n## Execution policy\n\nThis package activates `accelerated_milestone_closure`:\n\n- focused tests during implementation;\n- batched deterministic repairs;\n- one final complete Pull Request quality matrix;\n- exact-commit, double-build publication after merge;\n- immutable release assets;\n- publication receipt and workflow self-removal.\n\n## Target\n\n- version: `1.10.0`;\n- tag: `data-products-v1.10.0`;\n- archive: `dacia-knowledge-base-data-products-v1.10.0.zip`;\n- public assets: archive, manifest and SHA256SUMS.\n\n## Acceptance criteria\n\n- project documentation describes the accelerated mode and its safety boundaries;\n- release notes describe the interface repair and current source-backed portfolio;\n- focused interface and release tests pass;\n- the final Pull Request head passes the complete repository quality matrix;\n- post-merge publication builds twice from the exact merge SHA and proves byte identity;\n- the offline workspace verifies successfully;\n- the public release is created only once and is then recorded in canonical state.\n'
DECISION = '## D-ACC-001 — Accelerated milestone closure mode\n\nStatus: Accepted\n\nDate: 2026-08-01\n\n### Decision\n\nThe project may use `accelerated_milestone_closure` for a bounded milestone or release when the remaining backlog is known and logically related.\n\nThe mode uses focused tests during implementation, batches mechanical snapshot and counter repairs, opens the Pull Request after branch stabilization when practical, and runs the complete required quality matrix once on the final Pull Request head.\n\nClosely related sources may be combined only into one explicit closure package. Exact evidence boundaries remain unchanged.\n\nFor releases, publication may be completed by one post-merge workflow that builds twice from the exact merge SHA, verifies byte identity and the offline workspace, publishes immutable assets, records the result and removes itself.\n\n### Rationale\n\nRepeated full-matrix runs and repeated Pull Request setup after every small deterministic correction consumed substantial time without adding proportional safety. The repository already provides focused contracts, deterministic generators, a final cross-platform matrix and exact release verification.\n\n### Consequences\n\n- one logical package still maps to one Pull Request;\n- final complete quality is mandatory;\n- stale or unverified SHAs cannot be merged or published;\n- evidence may not be inferred or transferred across scope boundaries;\n- public releases remain immutable;\n- the canonical execution policy is stored in `project/state.json`;\n- detailed rules are stored in `project/ACCELERATED_MILESTONE_CLOSURE.md`.\n'
TEST_CONTENT = 'from __future__ import annotations\n\nimport json\nimport unittest\nfrom pathlib import Path\n\n\nROOT = Path(__file__).resolve().parents[1]\n\n\nclass DataProductsV110AcceleratedReleaseContractTest(unittest.TestCase):\n    def test_accelerated_policy_is_canonical_and_documented(self) -> None:\n        state = json.loads((ROOT / "project/state.json").read_text(encoding="utf-8"))\n        policy = state["execution_policy"]\n        self.assertEqual(policy["mode"], "accelerated_milestone_closure")\n        self.assertTrue(policy["focused_tests_during_development"])\n        self.assertTrue(policy["full_quality_on_final_head"])\n        self.assertTrue(policy["batch_mechanical_repairs"])\n        self.assertTrue(policy["open_pr_after_package_stabilization"])\n        self.assertEqual(\n            policy["allow_multi_source_package"],\n            "only_for_one_logical_closure_scope",\n        )\n\n        start_here = (ROOT / "project/START_HERE.md").read_text(encoding="utf-8")\n        self.assertIn("ACCELERATED_MILESTONE_CLOSURE.md", start_here)\n\n        maintainer = (\n            ROOT / "project/AUTONOMOUS_MAINTAINER.md"\n        ).read_text(encoding="utf-8")\n        self.assertIn("## Accelerated milestone closure mode", maintainer)\n\n        decision = (ROOT / "project/DECISIONS.md").read_text(encoding="utf-8")\n        self.assertIn("## D-ACC-001 — Accelerated milestone closure mode", decision)\n\n    def test_release_notes_include_interface_repairs(self) -> None:\n        release_source = (\n            ROOT / "tools/reporting/data_product_release.py"\n        ).read_text(encoding="utf-8")\n        self.assertIn(\'elif version == "1.10.0":\', release_source)\n        self.assertIn("forced dark theme", release_source)\n        self.assertIn("two-axis sticky comparison grid", release_source)\n        self.assertIn("grouped commercial grade choices", release_source)\n\n    def test_current_interface_repair_contract_remains_present(self) -> None:\n        selection_html = (\n            ROOT / "tools/reporting/configuration_shortlist_selection_html.py"\n        ).read_text(encoding="utf-8")\n        self.assertIn("Interface repair v1.6", selection_html)\n        self.assertIn("position:sticky;top:0", selection_html)\n        self.assertIn("position:sticky;left:0", selection_html)\n        self.assertIn("--parameter-column:280px", selection_html)\n        self.assertIn("--data-column:260px", selection_html)\n\n\nif __name__ == "__main__":\n    unittest.main()\n'
RECORD_SCRIPT = '#!/usr/bin/env python3\nfrom __future__ import annotations\n\nimport hashlib\nimport json\nimport os\nfrom pathlib import Path\n\n\nROOT = Path(__file__).resolve().parents[1]\nRELEASE_DIR = Path(os.environ["RELEASE_DIR"])\nSOURCE_SHA = os.environ["SOURCE_SHA"]\nRELEASE_ID = os.environ.get("RELEASE_ID", "")\nTAG = "data-products-v1.10.0"\n\n\ndef sha256(path: Path) -> str:\n    digest = hashlib.sha256()\n    with path.open("rb") as handle:\n        for chunk in iter(lambda: handle.read(1024 * 1024), b""):\n            digest.update(chunk)\n    return digest.hexdigest()\n\n\nassets = {}\nfor name in (\n    "dacia-knowledge-base-data-products-v1.10.0.zip",\n    "data-product-release-manifest.json",\n    "SHA256SUMS",\n):\n    path = RELEASE_DIR / name\n    assets[name] = {\n        "size_bytes": path.stat().st_size,\n        "sha256": sha256(path),\n    }\n\nreceipt = {\n    "version": 1,\n    "kind": "data_products_v1_10_0_publication",\n    "published_on": "2026-08-01",\n    "status": "complete",\n    "tag": TAG,\n    "release_id": int(RELEASE_ID) if RELEASE_ID else None,\n    "source_commit": SOURCE_SHA,\n    "double_build_byte_identity": True,\n    "offline_workspace_verification": "PASS",\n    "interface_repairs": {\n        "forced_dark_theme": True,\n        "grouped_commercial_grade_choices": True,\n        "two_axis_sticky_comparison_grid": True,\n        "deterministic_column_widths": True,\n    },\n    "assets": assets,\n    "public_v1_9_0_immutable": True,\n}\n(ROOT / "data/reporting/data_products_v1_10_0_publication.json").write_text(\n    json.dumps(receipt, ensure_ascii=False, indent=2) + "\\n",\n    encoding="utf-8",\n)\n\nstate_path = ROOT / "project/state.json"\nstate = json.loads(state_path.read_text(encoding="utf-8"))\nstate["updated_on"] = "2026-08-01"\nstate["phase"] = "Data Products v1.10.0 Publication"\nstate["current_package"] = {\n    "package_id": "data_products_v1_10_0_publication_001",\n    "kind": "data_product_release",\n    "name": "Data Products v1.10.0 Publication",\n    "status": "complete",\n    "goal": (\n        "Publish the current source-backed data products and the interactive "\n        "shortlist interface repairs from the exact verified merge commit."\n    ),\n    "manifest_paths": [\n        "data/reporting/data_products_v1_10_0_publication.json",\n        "project/STATE_SUMMARY.md",\n        "project/packages/data-products-v1.10.0-publication-20260801.md",\n        "project/state.json",\n        "tools/reporting/data_product_release.py",\n    ],\n}\nstate["next_package"] = {\n    "package_id": "sandero_residual_source_closure_006",\n    "kind": "source_backed_completeness_import",\n    "name": "Sandero Residual Source Closure",\n    "status": "planned",\n    "goal": (\n        "Close the three remaining eligible Sandero source candidates as one "\n        "logical evidence-bounded package, without cross-configuration or "\n        "cross-powertrain inference."\n    ),\n    "manifest_paths": [],\n}\nstate_path.write_text(\n    json.dumps(state, ensure_ascii=False, indent=2) + "\\n",\n    encoding="utf-8",\n)\n\npublication_doc = f"""# Data Products v1.10.0 Publication\n\nDate: 2026-08-01\n\n## Result\n\nThe immutable `data-products-v1.10.0` release was published from exact source commit `{SOURCE_SHA}`.\n\nThe release contains the current source-backed portfolio and the interactive shortlist repairs introduced by Pull Request #427:\n\n- forced dark theme;\n- grouped commercial grade choices with exact version codes retained;\n- two-axis sticky comparison grid;\n- deterministic comparison-column widths.\n\nThe assets were built twice and were byte-identical. The extracted offline workspace passed verification. Public `data-products-v1.9.0` remains immutable.\n\n## Assets\n\n- `dacia-knowledge-base-data-products-v1.10.0.zip`;\n- `data-product-release-manifest.json`;\n- `SHA256SUMS`.\n\nExact sizes and SHA-256 values are stored in `data/reporting/data_products_v1_10_0_publication.json`.\n\n## Next package\n\nThe next package is `sandero_residual_source_closure_006`, combining only the three remaining eligible Sandero source candidates into one evidence-bounded closure package.\n"""\n(ROOT / "project/packages/data-products-v1.10.0-publication-20260801.md").write_text(\n    publication_doc,\n    encoding="utf-8",\n)\n'
PUBLISH_WORKFLOW = 'name: Temporary Publish Data Products v1.10.0\n\non:\n  push:\n    branches:\n      - main\n    paths:\n      - "project/packages/data-products-v1.10.0-accelerated-release-preparation-20260801.md"\n\npermissions:\n  contents: write\n\nconcurrency:\n  group: publish-data-products-v1-10-0\n  cancel-in-progress: false\n\njobs:\n  publish:\n    runs-on: ubuntu-latest\n    steps:\n      - name: Check out exact merge commit\n        uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1\n        with:\n          fetch-depth: 0\n          persist-credentials: true\n\n      - name: Set up Python\n        uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97\n        with:\n          python-version: "3.14"\n\n      - name: Verify release is absent\n        env:\n          GH_TOKEN: ${{ github.token }}\n        run: |\n          if gh release view data-products-v1.10.0 >/dev/null 2>&1; then\n            echo "Release already exists; refusing to rewrite it."\n            exit 1\n          fi\n          if git rev-parse data-products-v1.10.0 >/dev/null 2>&1; then\n            echo "Tag already exists; refusing to rewrite it."\n            exit 1\n          fi\n\n      - name: Run focused release and interface contracts\n        run: |\n          python -m unittest -q \\\n            tests.test_data_products_v1_10_0_release_contract \\\n            tests.test_configuration_comparison_sticky_offset \\\n            tests.test_configuration_selection_export \\\n            tests.test_configuration_shortlist_html \\\n            tests.test_data_product_release\n          python tools/dkb.py project-state --check\n\n      - name: Build exact assets twice\n        run: |\n          python tools/dkb.py data-product-release \\\n            --output-directory "${RUNNER_TEMP}/release-a" \\\n            --version 1.10.0 \\\n            --commit-sha "${GITHUB_SHA}"\n          python tools/dkb.py data-product-release \\\n            --output-directory "${RUNNER_TEMP}/release-b" \\\n            --version 1.10.0 \\\n            --commit-sha "${GITHUB_SHA}"\n          diff -qr "${RUNNER_TEMP}/release-a" "${RUNNER_TEMP}/release-b"\n\n      - name: Verify assets and offline workspace\n        run: |\n          python tools/dkb.py data-product-release \\\n            --output-directory "${RUNNER_TEMP}/release-a" \\\n            --verify\n          mkdir "${RUNNER_TEMP}/workspace"\n          unzip -q \\\n            "${RUNNER_TEMP}/release-a/dacia-knowledge-base-data-products-v1.10.0.zip" \\\n            -d "${RUNNER_TEMP}/workspace"\n          python tools/dkb.py data-product-workspace-verify \\\n            --workspace-directory "${RUNNER_TEMP}/workspace" \\\n            --json\n          unzip -p \\\n            "${RUNNER_TEMP}/release-a/dacia-knowledge-base-data-products-v1.10.0.zip" \\\n            RELEASE_NOTES.md > "${RUNNER_TEMP}/release-notes.md"\n\n      - name: Publish immutable release\n        env:\n          GH_TOKEN: ${{ github.token }}\n        run: |\n          gh release create data-products-v1.10.0 \\\n            "${RUNNER_TEMP}/release-a/dacia-knowledge-base-data-products-v1.10.0.zip" \\\n            "${RUNNER_TEMP}/release-a/data-product-release-manifest.json" \\\n            "${RUNNER_TEMP}/release-a/SHA256SUMS" \\\n            --target "${GITHUB_SHA}" \\\n            --title "Dacia Knowledge Base Data Products v1.10.0" \\\n            --notes-file "${RUNNER_TEMP}/release-notes.md"\n          gh release view data-products-v1.10.0 --json databaseId -q \'.databaseId\' \\\n            > "${RUNNER_TEMP}/release-id.txt"\n\n      - name: Verify public assets\n        env:\n          GH_TOKEN: ${{ github.token }}\n        run: |\n          mkdir "${RUNNER_TEMP}/public"\n          gh release download data-products-v1.10.0 \\\n            --dir "${RUNNER_TEMP}/public"\n          diff -q \\\n            "${RUNNER_TEMP}/release-a/dacia-knowledge-base-data-products-v1.10.0.zip" \\\n            "${RUNNER_TEMP}/public/dacia-knowledge-base-data-products-v1.10.0.zip"\n          diff -q \\\n            "${RUNNER_TEMP}/release-a/data-product-release-manifest.json" \\\n            "${RUNNER_TEMP}/public/data-product-release-manifest.json"\n          diff -q \\\n            "${RUNNER_TEMP}/release-a/SHA256SUMS" \\\n            "${RUNNER_TEMP}/public/SHA256SUMS"\n\n      - name: Record publication and remove temporary automation\n        env:\n          RELEASE_DIR: ${{ runner.temp }}/release-a\n          RELEASE_ID_FILE: ${{ runner.temp }}/release-id.txt\n          SOURCE_SHA: ${{ github.sha }}\n        run: |\n          export RELEASE_ID="$(cat "${RELEASE_ID_FILE}")"\n          python tools/record_data_products_v1_10_0_publication_20260801.py\n          python tools/dkb.py project-state --apply\n          rm .github/workflows/temporary-publish-data-products-v1.10.0.yml\n          rm tools/record_data_products_v1_10_0_publication_20260801.py\n          git config user.name "github-actions[bot]"\n          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"\n          git add \\\n            data/reporting/data_products_v1_10_0_publication.json \\\n            project/STATE_SUMMARY.md \\\n            project/packages/data-products-v1.10.0-publication-20260801.md \\\n            project/state.json \\\n            .github/workflows/temporary-publish-data-products-v1.10.0.yml \\\n            tools/record_data_products_v1_10_0_publication_20260801.py\n          git commit -m "release(data-products): record v1.10.0 publication"\n          git push origin HEAD:main\n'


def write(path: str, content: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.rstrip() + "\n", encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"cannot find replacement marker in {path}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


def append_once(path: str, marker: str, block: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if marker in text:
        return
    target.write_text(text.rstrip() + "\n\n" + block.rstrip() + "\n", encoding="utf-8")


def main() -> None:
    write("project/ACCELERATED_MILESTONE_CLOSURE.md", ACCELERATED_DOC)

    old_order = """1. `state.json`
2. `STATE_SUMMARY.md`
3. `AUTONOMOUS_MAINTAINER.md`
4. `AI_WORKING_AGREEMENT.md`
5. `AI_CONTEXT.md`
6. `DOCUMENTATION_STANDARD.md`
7. `DOCUMENT_TYPES.md`
8. `GLOSSARY.md`
9. `DECISIONS.md`
10. `SESSION_STATE.md`
11. `ROADMAP.md`"""
    new_order = """1. `state.json`
2. `STATE_SUMMARY.md`
3. `AUTONOMOUS_MAINTAINER.md`
4. `ACCELERATED_MILESTONE_CLOSURE.md`
5. `AI_WORKING_AGREEMENT.md`
6. `AI_CONTEXT.md`
7. `DOCUMENTATION_STANDARD.md`
8. `DOCUMENT_TYPES.md`
9. `GLOSSARY.md`
10. `DECISIONS.md`
11. `SESSION_STATE.md`
12. `ROADMAP.md`"""
    replace_once("project/START_HERE.md", old_order, new_order)

    maintainer_marker = "## Standing authorization"
    maintainer_block = """## Accelerated milestone closure mode

When `project/state.json` selects `accelerated_milestone_closure`, the maintainer follows `project/ACCELERATED_MILESTONE_CLOSURE.md`.

The mode changes execution cadence, not correctness:

- focused tests are used during branch stabilization;
- deterministic snapshot and counter repairs are batched;
- the Pull Request is opened after stabilization when practical;
- the complete required quality matrix runs on the final head SHA;
- closely related sources may be combined only into one explicit closure scope;
- releases are built twice from the exact source commit and remain immutable.

The mode never permits evidence inference, stale-SHA publication, skipped final quality, unrelated scope mixing or bypassing an `ACTION_REQUIRED` boundary.

"""
    target = ROOT / "project/AUTONOMOUS_MAINTAINER.md"
    text = target.read_text(encoding="utf-8")
    if "## Accelerated milestone closure mode" not in text:
        if maintainer_marker not in text:
            raise RuntimeError("AUTONOMOUS_MAINTAINER marker not found")
        target.write_text(
            text.replace(maintainer_marker, maintainer_block + maintainer_marker, 1),
            encoding="utf-8",
        )

    append_once(
        "project/DECISIONS.md",
        "## D-ACC-001 — Accelerated milestone closure mode",
        DECISION,
    )

    release_path = ROOT / "tools/reporting/data_product_release.py"
    release_text = release_path.read_text(encoding="utf-8")
    if 'elif version == "1.10.0":' not in release_text:
        marker = """    lines.extend(
        [
            "No ranking, recommendations or inferred values are generated.","""
        block = """    elif version == "1.10.0":
        lines.extend(
            [
                "This minor release publishes the current source-backed portfolio, "
                "including the Spring catalogue foundation and all later exact "
                "technical and equipment observations.",
                "",
                "The interactive shortlist includes the repaired user interface: "
                "one forced dark theme, grouped commercial grade choices with exact "
                "version codes retained, and a two-axis sticky comparison grid with "
                "deterministic parameter and configuration column widths.",
                "",
                "The release preserves the existing pair-type filter and multi-"
                "configuration comparison behavior. No cross-scope pairs, ranking, "
                "recommendations or inferred values are introduced, and the public "
                "v1.9.0 remains immutable.",
                "",
            ]
        )
"""
        if marker not in release_text:
            raise RuntimeError("release notes insertion marker not found")
        release_path.write_text(
            release_text.replace(marker, block + marker, 1),
            encoding="utf-8",
        )

    write(
        "project/packages/data-products-v1.10.0-accelerated-release-preparation-20260801.md",
        PACKAGE_DOC,
    )

    state_path = ROOT / "project/state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    previous_next = state.get("next_package")
    state["updated_on"] = "2026-08-01"
    state["phase"] = "Data Products v1.10.0 Accelerated Release Preparation"
    state["execution_policy"] = {
        "mode": "accelerated_milestone_closure",
        "focused_tests_during_development": True,
        "full_quality_on_final_head": True,
        "batch_mechanical_repairs": True,
        "open_pr_after_package_stabilization": True,
        "allow_multi_source_package": "only_for_one_logical_closure_scope",
        "release_double_build_required": True,
        "release_exact_source_sha_required": True,
    }
    state["current_package"] = {
        "package_id": "data_products_v1_10_0_accelerated_release_preparation_001",
        "kind": "data_product_release_preparation",
        "name": "Data Products v1.10.0 Accelerated Release Preparation",
        "status": "complete",
        "goal": (
            "Document the accelerated closure policy and prepare exact post-merge "
            "publication of the current data products and interactive shortlist repairs."
        ),
        "manifest_paths": [
            ".github/workflows/temporary-publish-data-products-v1.10.0.yml",
            "project/ACCELERATED_MILESTONE_CLOSURE.md",
            "project/AUTONOMOUS_MAINTAINER.md",
            "project/DECISIONS.md",
            "project/START_HERE.md",
            "project/STATE_SUMMARY.md",
            "project/packages/data-products-v1.10.0-accelerated-release-preparation-20260801.md",
            "project/state.json",
            "tests/test_data_products_v1_10_0_release_contract.py",
            "tools/record_data_products_v1_10_0_publication_20260801.py",
            "tools/reporting/data_product_release.py",
        ],
    }
    state["next_package"] = {
        "package_id": "data_products_v1_10_0_publication_001",
        "kind": "data_product_release",
        "name": "Data Products v1.10.0 Publication",
        "status": "planned",
        "goal": (
            "Build the assets twice from the exact squash-merged preparation commit, "
            "verify byte identity and the offline workspace, publish immutable assets "
            "and record the result."
        ),
        "manifest_paths": [],
        "resume_after_publication": previous_next,
    }
    state_path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    write("tests/test_data_products_v1_10_0_release_contract.py", TEST_CONTENT)
    write(
        "tools/record_data_products_v1_10_0_publication_20260801.py",
        RECORD_SCRIPT,
    )
    write(
        ".github/workflows/temporary-publish-data-products-v1.10.0.yml",
        PUBLISH_WORKFLOW,
    )


if __name__ == "__main__":
    main()
