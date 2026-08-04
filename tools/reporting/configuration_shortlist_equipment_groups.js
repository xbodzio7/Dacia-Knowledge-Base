
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
