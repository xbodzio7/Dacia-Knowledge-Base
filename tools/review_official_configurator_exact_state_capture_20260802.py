from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "project/sources/dacia-pl-official-configurator-exact-state-capture-20260802.json"
REPORT = ROOT / "data/reporting/official_configurator_exact_state_capture.json"
STATE = ROOT / "project/state.json"

EXPECTED_DEFAULTS = {
    "spring_essential_electric70_automatic",
    "sandero_iii_essential_tce100_manual",
    "sandero_stepway_iii_essential_tce110_manual",
    "jogger_essential_5seat_ecog120_manual",
    "jogger_essential_7seat_ecog120_manual",
    "duster_iii_essential_ecog120_4x2_manual",
    "bigster_essential_mildhybridg140_4x2_manual",
}


def read_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"expected JSON object: {path}")
    return payload


def verify(root: Path = ROOT) -> None:
    snapshot = read_json(root / SNAPSHOT.relative_to(ROOT))
    report = read_json(root / REPORT.relative_to(ROOT))
    state = read_json(root / STATE.relative_to(ROOT))

    captured = {
        row["configuration_code"]
        for row in snapshot["automatically_captured_default_states"]
    }
    if captured != EXPECTED_DEFAULTS:
        raise AssertionError("default exact-state capture set drifted")

    capability = snapshot["capture_capability"]
    if capability["ordinary_configurator_static_html"] != "supported":
        raise AssertionError("ordinary configurator capture must remain supported")
    if capability["saved_conf_wrapper"] != "not_resolved":
        raise AssertionError("saved conf wrapper boundary drifted")
    if capability["configurator_pdf_download"] != "requires_browser_or_user_export":
        raise AssertionError("PDF capture boundary drifted")

    queue = snapshot["minimal_manual_artifact_queue"]
    required_now = queue["required_now"]
    if len(required_now) != 1:
        raise AssertionError("exactly one artifact must block the architecture review")
    if required_now[0]["configuration_code"] != "spring_expression_electric70_automatic":
        raise AssertionError("unexpected immediate manual artifact")

    if report["automatically_captured_default_states"] != 7:
        raise AssertionError("unexpected automatic capture count")
    if report["manual_artifacts_required_now"] != 1:
        raise AssertionError("unexpected immediate manual count")
    if report["architecture_decision"] != "deferred":
        raise AssertionError("historical capture report must preserve its deferred decision")
    if any(report["master_data_delta"].values()):
        raise AssertionError("capture package must not mutate master data")

    # The completed package remains protected after canonical state advances.
    baseline = state["baseline"]
    if baseline["rows"] < 11715 or baseline["configuration_values"] < 3567:
        raise AssertionError("canonical baseline regressed below exact-state capture")
    if state["current_package"]["package_id"] == "official_configurator_exact_state_capture_001":
        if state["next_package"]["package_id"] != "spring_expression_saved_state_artifact_intake_001":
            raise AssertionError("unexpected next package")


if __name__ == "__main__":
    verify()
    print("Official configurator exact-state capture: PASS")
