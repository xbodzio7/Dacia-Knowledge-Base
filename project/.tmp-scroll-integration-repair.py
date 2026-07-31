from __future__ import annotations

import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "tools" / "configuration_shortlist.py"
text = path.read_text(encoding="utf-8")

replacements = {
    ".comparison-group-controls button{min-height:36px;padding:7px 11px;border:1px solid #aeb8b0;border-radius:8px;background:#fff;color:var(--ink);cursor:pointer;font-size:.76rem;font-weight:750}":
    ".comparison-group-controls button{min-height:36px;padding:7px 11px;border:1px solid var(--line);border-radius:8px;background:var(--config-panel);color:var(--config-text);cursor:pointer;font-size:.76rem;font-weight:750}",
    ".comparison-table .comparison-category-row .comparison-category-label{position:sticky;left:0;z-index:4;min-width:210px;padding:0;background:#dfe9e2}":
    ".comparison-table .comparison-category-row .comparison-category-label{position:sticky;left:0;z-index:7;width:var(--parameter-column,280px);min-width:var(--parameter-column,280px);max-width:var(--parameter-column,280px);padding:0;background:var(--soft)}",
    ".comparison-table .comparison-category-row .comparison-category-fill{background:#dfe9e2}":
    ".comparison-table .comparison-category-row .comparison-category-fill{background:var(--soft)}",
}
for old, new in replacements.items():
    assert old in text, old
    text = text.replace(old, new, 1)

old = '''  const updateStickyOffset = () => {
    if (offsetFrame) cancelAnimationFrame(offsetFrame);
    offsetFrame = requestAnimationFrame(() => {
      const sticky = getComputedStyle(selectionPanel).position === "sticky";
      const offset = sticky ? Math.ceil(selectionPanel.offsetHeight + 18) : 0;
      root.style.setProperty("--comparison-sticky-top", `${offset}px`);
      offsetFrame = 0;
    });
  };
'''
new = '''  const updateStickyOffset = () => {
    if (offsetFrame) cancelAnimationFrame(offsetFrame);
    offsetFrame = requestAnimationFrame(() => {
      const sticky = getComputedStyle(selectionPanel).position === "sticky";
      const scrollStyle = scroll ? getComputedStyle(scroll) : null;
      const innerScroll = Boolean(
        scrollStyle
        && ["auto", "scroll"].includes(scrollStyle.overflowY)
        && scrollStyle.maxHeight !== "none"
      );
      const offset = sticky && !innerScroll
        ? Math.ceil(selectionPanel.offsetHeight + 18)
        : 0;
      root.style.setProperty("--comparison-sticky-top", `${offset}px`);
      offsetFrame = 0;
    });
  };
'''
assert old in text
text = text.replace(old, new, 1)

old = '''  const decorateCategoryRows = () => {
    const columnCount = Math.max(1, table.querySelectorAll("thead th").length);
    for (const row of categoryRows()) {
      const category = row.dataset.category || "Pozostałe";
      let labelCell = [...row.children].find((child) => child.tagName === "TH");
      if (!labelCell) continue;
      let toggle = labelCell.querySelector(".comparison-category-toggle");
      if (!toggle) {
        const label = labelCell.textContent.trim() || category;
        labelCell.removeAttribute("colspan");
        labelCell.classList.add("comparison-category-label");
        labelCell.setAttribute("scope", "rowgroup");
        toggle = document.createElement("button");
        toggle.type = "button";
        toggle.className = "comparison-category-toggle";
        toggle.dataset.category = category;
        toggle.textContent = label;
        labelCell.replaceChildren(toggle);
        const fill = document.createElement("td");
        fill.className = "comparison-category-fill";
        fill.setAttribute("aria-hidden", "true");
        fill.colSpan = Math.max(1, columnCount - 1);
        row.append(fill);
      } else {
        const fill = row.querySelector(".comparison-category-fill");
        if (fill) fill.colSpan = Math.max(1, columnCount - 1);
      }
      applyCollapsedState(category);
    }
    updateControlState();
  };
'''
new = '''  const decorateCategoryRows = () => {
    const columnCount = Math.max(1, table.querySelectorAll("thead th").length);
    for (const row of categoryRows()) {
      const category = row.dataset.category || "Pozostałe";
      const labelCell = [...row.children].find((child) => child.tagName === "TH");
      if (!labelCell) continue;
      let fill = row.querySelector(".comparison-category-fill")
        || [...row.children].find((child) => child.tagName === "TD");
      let toggle = labelCell.querySelector(".comparison-category-toggle");
      if (!toggle) {
        const label = labelCell.textContent.trim() || category;
        labelCell.removeAttribute("colspan");
        labelCell.classList.add("comparison-category-label");
        labelCell.setAttribute("scope", "rowgroup");
        toggle = document.createElement("button");
        toggle.type = "button";
        toggle.className = "comparison-category-toggle";
        toggle.dataset.category = category;
        toggle.textContent = label;
        labelCell.replaceChildren(toggle);
      }
      if (!fill) {
        fill = document.createElement("td");
        row.append(fill);
      }
      fill.classList.add("comparison-category-fill");
      fill.setAttribute("aria-hidden", "true");
      fill.colSpan = Math.max(1, columnCount - 1);
      applyCollapsedState(category);
    }
    updateControlState();
  };
'''
assert old in text
text = text.replace(old, new, 1)

old = '''    decorateFrame = requestAnimationFrame(() => {
      decorateCategoryRows();
      decorateFrame = 0;
    });
'''
new = '''    decorateFrame = requestAnimationFrame(() => {
      decorateCategoryRows();
      updateStickyOffset();
      decorateFrame = 0;
    });
'''
assert old in text
text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8")

path = root / "tests" / "test_configuration_comparison_sticky_offset.py"
text = path.read_text(encoding="utf-8")
anchor = '        "selectionPanel.offsetHeight + 18",\n'
assert anchor in text
text = text.replace(
    anchor,
    anchor
    + '        "innerScroll",\n'
    + '        \'scrollStyle.maxHeight !== "none"\',\n'
    + '        \'row.querySelector(".comparison-category-fill")\',\n',
    1,
)
anchor = '    assert "new MutationObserver(scheduleDecoration).observe(table" in rendered\n'
assert anchor in text
text = text.replace(
    anchor,
    anchor
    + '    assert \'scrollStyle.maxHeight !== "none"\' in rendered\n'
    + '    assert \'row.querySelector(".comparison-category-fill")\' in rendered\n',
    1,
)
path.write_text(text, encoding="utf-8")

package = root / "project" / "packages" / "interactive-shortlist-interface-repair-20260731.md"
package_text = package.read_text(encoding="utf-8")
addition = '''
## Visual verification

The generated final HTML was opened in headless Chromium. The audit confirmed a dark outer canvas and filter panel, five unique commercial grade choices across all six models, visible Duster and Bigster comparison columns, a fixed-width parameter column and an internally scrollable comparison table. The legacy page-level sticky offset and duplicate category filler discovered during that audit are repaired in this package.
'''
if "## Visual verification" not in package_text:
    package.write_text(package_text.rstrip() + "\n" + addition, encoding="utf-8")

state_path = root / "project" / "state.json"
state = json.loads(state_path.read_text(encoding="utf-8"))
state["current_package"]["manifest_paths"] = [
    "project/STATE_SUMMARY.md",
    "project/packages/interactive-shortlist-interface-repair-20260731.md",
    "project/state.json",
    "tests/test_configuration_comparison_sticky_offset.py",
    "tests/test_configuration_selection_export.py",
    "tests/test_configuration_shortlist_html.py",
    "tools/configuration_shortlist.py",
    "tools/reporting/configuration_shortlist_browser.js",
    "tools/reporting/configuration_shortlist_html.py",
    "tools/reporting/configuration_shortlist_selection.js",
    "tools/reporting/configuration_shortlist_selection_html.py",
]
state_path.write_text(
    json.dumps(state, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
