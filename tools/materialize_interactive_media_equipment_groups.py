#!/usr/bin/env python3
"""Materialize the bounded interactive-media and equipment-group correction."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"expected one match in {path.relative_to(ROOT)}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8", newline="\n")


EQUIPMENT_GROUP_CSS = r'''
/* Interface v1.7: collapsed-by-default equipment groups and normalized Spring media. */
.equipment-picker-group[data-collapsible-equipment-group]{display:block;overflow:hidden;border:1px solid var(--config-line);border-radius:8px;background:#282e2b}
.equipment-picker-group[data-collapsible-equipment-group]>summary{display:flex;align-items:center;justify-content:space-between;gap:12px;min-height:42px;padding:9px 11px;cursor:pointer;list-style:none;color:var(--config-text);font-size:.74rem;font-weight:800;text-transform:uppercase;letter-spacing:.045em}
.equipment-picker-group[data-collapsible-equipment-group]>summary::-webkit-details-marker{display:none}
.equipment-picker-group[data-collapsible-equipment-group]>summary::after{content:"＋";flex:0 0 auto;color:#cbd2cc;font-size:1rem;line-height:1}
.equipment-picker-group[data-collapsible-equipment-group][open]>summary::after{content:"−"}
.equipment-picker-group[data-collapsible-equipment-group][open]>summary{border-bottom:1px solid var(--config-line);background:#303633}
.equipment-picker-group-title{min-width:0}
.equipment-picker-group-meta{flex:0 0 auto;color:#b9c0bb;font-size:.66rem;font-weight:650;text-transform:none;letter-spacing:0}
.equipment-picker-group[data-collapsible-equipment-group]>.equipment-picker-options{padding:10px}
.vehicle-photo-frame.vehicle-photo-frame-spring{overflow:hidden;min-height:108px;border-radius:10px;background:#d7e1e7}
.vehicle-photo-frame.vehicle-photo-frame-spring .vehicle-photo{width:100%;height:100%;max-height:165px;object-fit:cover;object-position:center 58%;transform:scale(1.035)}
.model-choice .vehicle-photo-frame.vehicle-photo-frame-spring{height:122px}
.model-choice .vehicle-photo-frame.vehicle-photo-frame-spring .vehicle-photo{max-height:none}
@media(max-width:760px){.equipment-picker-group[data-collapsible-equipment-group]>summary{align-items:flex-start}.equipment-picker-group-meta{text-align:right}}
'''


EQUIPMENT_GROUP_JS = r'''
(function () {
  "use strict";
  const MARKER = "configuration_shortlist_equipment_groups_v1_7";

  const visibleChoices = (group) => [...group.querySelectorAll(".equipment-choice")]
    .filter((choice) => !choice.hidden);

  const updateSummary = (group) => {
    const meta = group.querySelector("[data-equipment-group-meta]");
    if (!meta) return;
    const visible = visibleChoices(group);
    const selected = [...group.querySelectorAll(".equipment-choice.is-selected")].length;
    meta.textContent = selected
      ? `${visible.length} pozycji · wybrane: ${selected}`
      : `${visible.length} pozycji`;
  };

  const upgradeGroup = (section) => {
    if (!section || section.matches("details[data-collapsible-equipment-group]")) return section;
    const heading = section.querySelector(":scope > h3");
    const options = section.querySelector(":scope > .equipment-picker-options");
    if (!heading || !options) return section;
    const details = document.createElement("details");
    details.className = section.className;
    details.dataset.category = section.dataset.category || "Pozostałe";
    details.dataset.collapsibleEquipmentGroup = "true";
    details.hidden = section.hidden;
    const summary = document.createElement("summary");
    summary.className = "equipment-picker-group-summary";
    summary.innerHTML = `<span class="equipment-picker-group-title"></span><span class="equipment-picker-group-meta" data-equipment-group-meta></span>`;
    summary.querySelector(".equipment-picker-group-title").textContent = heading.textContent.trim();
    details.append(summary, options);
    section.replaceWith(details);
    updateSummary(details);
    return details;
  };

  const markSpringPhotos = (root) => {
    const scope = root && root.querySelectorAll ? root : document;
    for (const frame of scope.querySelectorAll("[data-model-photo]")) {
      const image = frame.querySelector("img.vehicle-photo");
      const host = frame.closest("[data-model-code], [data-value]");
      const modelCode = host && (host.dataset.modelCode || host.dataset.value || "");
      const isSpring = String(modelCode).toLocaleLowerCase("pl").includes("spring")
        || Boolean(image && String(image.alt || "").toLocaleLowerCase("pl").includes("spring"));
      frame.classList.toggle("vehicle-photo-frame-spring", isSpring);
    }
  };

  const initialize = () => {
    document.documentElement.dataset.equipmentGroupsEnhancement = MARKER;
    const groupsContainer = document.querySelector("[data-equipment-groups]");
    if (groupsContainer) {
      for (const section of [...groupsContainer.querySelectorAll(":scope > .equipment-picker-group")]) {
        upgradeGroup(section);
      }
      const syncSummaries = () => {
        for (const group of groupsContainer.querySelectorAll("details[data-collapsible-equipment-group]")) {
          updateSummary(group);
        }
      };
      new MutationObserver(syncSummaries).observe(groupsContainer, {
        subtree: true,
        attributes: true,
        attributeFilter: ["hidden", "class"]
      });
      const search = document.querySelector("[data-equipment-search]");
      if (search) {
        search.addEventListener("input", () => {
          requestAnimationFrame(() => {
            const active = Boolean(search.value.trim());
            for (const group of groupsContainer.querySelectorAll("details[data-collapsible-equipment-group]")) {
              if (active && !group.hidden && visibleChoices(group).length) {
                if (!group.open) group.dataset.openedBySearch = "true";
                group.open = true;
              } else if (!active && group.dataset.openedBySearch === "true") {
                group.open = false;
                delete group.dataset.openedBySearch;
              }
            }
            syncSummaries();
          });
        });
      }
      const form = groupsContainer.closest("form");
      if (form) {
        form.addEventListener("reset", () => requestAnimationFrame(() => {
          for (const group of groupsContainer.querySelectorAll("details[data-collapsible-equipment-group]")) {
            group.open = false;
            delete group.dataset.openedBySearch;
          }
          syncSummaries();
        }));
      }
      syncSummaries();
    }

    markSpringPhotos(document);
    new MutationObserver((records) => {
      for (const record of records) {
        for (const node of record.addedNodes) {
          if (node.nodeType === Node.ELEMENT_NODE) markSpringPhotos(node);
        }
      }
    }).observe(document.body, { childList: true, subtree: true });
  };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initialize);
  else initialize();
})();
'''


def materialize() -> None:
    reporting = ROOT / "tools" / "reporting"
    write(reporting / "configuration_shortlist_equipment_groups.css", EQUIPMENT_GROUP_CSS)
    write(reporting / "configuration_shortlist_equipment_groups.js", EQUIPMENT_GROUP_JS)

    selection_html = reporting / "configuration_shortlist_selection_html.py"
    replace_once(
        selection_html,
        '''    version_script = _read_script(\n        "configuration_shortlist_v12.js", "version 1.2 enhancement"\n    )\n''',
        '''    version_script = _read_script(\n        "configuration_shortlist_v12.js", "version 1.2 enhancement"\n    )\n    equipment_groups_script = _read_script(\n        "configuration_shortlist_equipment_groups.js",\n        "collapsible equipment groups",\n    )\n    equipment_groups_style = _read_script(\n        "configuration_shortlist_equipment_groups.css",\n        "collapsible equipment-group styles",\n    )\n''',
    )
    replace_once(
        selection_html,
        '''        style_marker, _SELECTION_CSS + "\\n" + style_marker, 1\n''',
        '''        style_marker,\n        _SELECTION_CSS + "\\n" + equipment_groups_style + "\\n" + style_marker,\n        1,\n''',
    )
    replace_once(
        selection_html,
        '''        "Format interaktywnej shortlisty HTML v1.",\n        "Format interaktywnej shortlisty HTML v1.6.",\n''',
        '''        "Format interaktywnej shortlisty HTML v1.",\n        "Format interaktywnej shortlisty HTML v1.7.",\n''',
    )
    replace_once(
        selection_html,
        '''            f"<script>{version_script}</script>\\n"\n            f"{body_marker}"\n''',
        '''            f"<script>{version_script}</script>\\n"\n            f"<script>{equipment_groups_script}</script>\\n"\n            f"{body_marker}"\n''',
    )

    shortlist = ROOT / "tools" / "configuration_shortlist.py"
    replace_once(
        shortlist,
        '''_OFFICIAL_MEDIA_PREFIXES = (\n    "https://www.dacia.pl/",\n    "https://cdn.group.renault.com/",\n)\n''',
        '''_OFFICIAL_MEDIA_PREFIXES = (\n    "https://www.dacia.pl/",\n    "https://cdn.group.renault.com/",\n    "https://3dv2.renault.com/",\n)\n''',
    )

    media_path = ROOT / "project" / "sources" / "dacia-pl-spring-model-media-20260801.json"
    media = json.loads(media_path.read_text(encoding="utf-8"))
    spring = media["models"]["spring"]
    spring["image_url"] = (
        "https://3dv2.renault.com/Image?"
        "databaseId=c4d69864-ca6c-4372-9267-8ce4a21dce04&"
        "snapshotId=81821214-93d2-627a-9116-3de2cb698dc2"
    )
    spring["notes"] = (
        "Official current Spring configurator image at a materially higher useful "
        "resolution than the former small carousel thumbnail. The interface applies "
        "Spring-only cover framing while retaining the generated offline fallback."
    )
    media_path.write_text(
        json.dumps(media, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    selection_test = ROOT / "tests" / "test_configuration_selection_export.py"
    replace_once(
        selection_test,
        '''        self.assertIn("Format interaktywnej shortlisty HTML v1.6.", rendered)\n        self.assertIn("equipment-picker-scroll", rendered)\n''',
        '''        self.assertIn("Format interaktywnej shortlisty HTML v1.7.", rendered)\n        self.assertIn("equipment-picker-scroll", rendered)\n        self.assertIn("configuration_shortlist_equipment_groups_v1_7", rendered)\n        self.assertIn('document.createElement("details")', rendered)\n        self.assertIn("data-collapsible-equipment-group", rendered)\n        self.assertIn("equipment-picker-group-summary", rendered)\n        self.assertIn("vehicle-photo-frame-spring", rendered)\n''',
    )

    release_test = ROOT / "tests" / "test_data_product_release.py"
    replace_once(
        release_test,
        '''            all(url.startswith("https://www.dacia.pl/") for url in external_urls),\n            external_urls,\n''',
        '''            all(\n                url.startswith((\n                    "https://www.dacia.pl/",\n                    "https://3dv2.renault.com/",\n                ))\n                for url in external_urls\n            ),\n            external_urls,\n''',
    )
    replace_once(
        release_test,
        '''            "grade_carrousel_1.png",\n''',
        '''            "https://3dv2.renault.com/Image?databaseId=",\n            "configuration_shortlist_equipment_groups_v1_7",\n            "data-collapsible-equipment-group",\n            "vehicle-photo-frame-spring",\n''',
    )

    package_path = ROOT / "project" / "packages" / "interactive-media-equipment-groups-correction-20260804.md"
    write(
        package_path,
        '''# Interactive Media and Equipment Groups Correction

## Package

- Package ID: `interactive_media_equipment_groups_correction_001`
- Kind: `user_interface_repair`
- Date: 2026-08-04
- Status: complete

## Purpose

Complete the two user-visible interface agreements that remained outside the canonical queue: make the Spring media visually consistent with the other model cards and make thematic equipment groups collapsible and closed by default while their names remain visible.

## Implemented correction

- replaces the former small Spring carousel thumbnail with the current official configurator image;
- keeps the generated Spring fallback and restricts cover framing to Spring only;
- upgrades every existing thematic equipment section to native `details`/`summary` disclosure;
- leaves every group closed at initial page load;
- keeps the Polish group name and live visible/selected counts in the summary;
- opens matching visible groups during equipment-name search and restores only search-opened groups when the query is cleared;
- closes the groups again when the filter form is reset;
- preserves existing equipment filtering, selected chips, availability reconciliation and no-inference semantics.

## Boundaries

No source-backed vehicle fact, price, availability state, model, version, configuration, comparison scope, ranking, recommendation or inferred value changes. The planned Portfolio Powertrain and Transmission Matrix remains the next package.

## Verification

The existing shortlist and release tests are extended without increasing the canonical test count. The generated standalone HTML must contain the v1.7 enhancement, the official Spring media URL, collapsible group contract and Spring-only framing markers. Full repository pull-request CI remains required before merge.
''',
    )

    state_path = ROOT / "project" / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    previous_next = state["next_package"]
    if previous_next.get("package_id") != "portfolio_powertrain_transmission_matrix_001":
        raise RuntimeError("canonical next package changed before interface materialization")
    state["updated_on"] = "2026-08-04"
    state["phase"] = "Interactive Media and Equipment Groups Correction"
    state["current_package"] = {
        "package_id": "interactive_media_equipment_groups_correction_001",
        "kind": "user_interface_repair",
        "name": "Interactive Media and Equipment Groups Correction",
        "status": "complete",
        "goal": (
            "Complete the remaining agreed interface work by using a clearer official "
            "Spring image with Spring-only framing and converting thematic equipment "
            "sections into collapsed-by-default groups with visible names and counts."
        ),
        "manifest_paths": [
            "project/STATE_SUMMARY.md",
            "project/packages/interactive-media-equipment-groups-correction-20260804.md",
            "project/sources/dacia-pl-spring-model-media-20260801.json",
            "project/state.json",
            "tests/test_configuration_selection_export.py",
            "tests/test_data_product_release.py",
            "tools/configuration_shortlist.py",
            "tools/reporting/configuration_shortlist_equipment_groups.css",
            "tools/reporting/configuration_shortlist_equipment_groups.js",
            "tools/reporting/configuration_shortlist_selection_html.py",
        ],
    }
    state["next_package"] = previous_next
    state_path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


if __name__ == "__main__":
    materialize()
