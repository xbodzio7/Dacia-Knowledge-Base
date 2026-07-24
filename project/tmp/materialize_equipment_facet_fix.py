from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise SystemExit(f"expected one match in {path}, found {text.count(old)}")
    file.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_between(path: str, start: str, end: str, replacement: str) -> None:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    first = text.index(start)
    last = text.index(end, first)
    file.write_text(text[:first] + replacement + text[last:], encoding="utf-8")


core = "tools/reporting/configuration_shortlist_browser.js"
replace_between(
    core,
    "  function reconcileEquipmentSelection(catalog, rawCriteria) {",
    "  function selectedValues(element) {",
    '''  function reconcileEquipmentSelection(catalog, rawCriteria) {
    const criteria = normalizeCriteria(rawCriteria || {});
    const baseCriteria = criteriaWithoutEquipment(criteria);
    const baseResults = catalog.configurations
      .filter((configuration) => evaluate(configuration, baseCriteria).length === 0)
      .sort(sortConfigurations);
    const requested = criteria.required_equipment;
    const compatible = baseResults.filter((configuration) =>
      requested.every((code) => equipmentAvailable(configuration, code))
    );
    const selectionConflict = requested.length > 0 && compatible.length === 0;

    if (!baseResults.length || selectionConflict) {
      return {
        base_match_count: baseResults.length,
        compatible_match_count: compatible.length,
        selected_equipment: requested,
        removed_equipment: [],
        available_equipment: requested,
        addable_equipment: [],
        differentiating_equipment: [],
        facet_coverage: {},
        selection_conflict: selectionConflict,
        compatible_configurations: compatible
      };
    }

    const differentiating = differentiatingEquipmentCodes(compatible);
    const addable = differentiating.filter((code) => !requested.includes(code));
    const visible = new Set([...requested, ...addable]);
    const coverage = {};
    for (const code of visible) coverage[code] = equipmentCoverage(compatible, code);
    return {
      base_match_count: baseResults.length,
      compatible_match_count: compatible.length,
      selected_equipment: requested,
      removed_equipment: [],
      available_equipment: [...visible].sort(),
      addable_equipment: addable,
      differentiating_equipment: differentiating,
      facet_coverage: Object.fromEntries(Object.entries(coverage).sort()),
      selection_conflict: false,
      compatible_configurations: compatible
    };
  }

''',
)
replace_once(
    core,
    '''      const facetState = reconcileEquipmentSelection(catalog, rawCriteria);
      if (facetState.removed_equipment.length) {
        setSelected(equipment, facetState.selected_equipment);
        rawCriteria.required_equipment = facetState.selected_equipment;
      }
      const outcome = filterCatalog(catalog, rawCriteria);
''',
    '''      const facetState = reconcileEquipmentSelection(catalog, rawCriteria);
      const outcome = filterCatalog(catalog, rawCriteria);
''',
)

ui = "tools/reporting/configuration_shortlist_v12.js"
replace_once(
    ui,
    '      <p class="equipment-availability-note" data-availability-note>Lista pokazuje wyłącznie źródłowo kompletne wyposażenie, które odróżnia aktualnie dopasowane warianty.</p>',
    '      <p class="equipment-availability-note" data-availability-note>Lista pokazuje tylko pozycje, które można teraz dodać bez utraty wszystkich wyników. Już wybrane pozycje pozostają zaznaczone.</p>',
)
replace_once(ui, "    let removedCodes = [];", "    let selectionConflict = false;")
replace_once(
    ui,
    '''      const note = wrapper.querySelector("[data-availability-note]");
      note.textContent = removedCodes.length
        ? `Usunięto ${removedCodes.length} pozycję/pozycje bez potwierdzonej dostępności w pozostałych wariantach.`
        : "Lista pokazuje tylko wyposażenie z kompletnym pokryciem źródłowym, dostępne w części, lecz nie we wszystkich aktualnie dopasowanych wariantach. Pozycje z brakami danych są ukrywane, aby nie przedstawiać braku rekordu jako niedostępności.";
      note.classList.toggle("has-removal", removedCodes.length > 0);
''',
    '''      const note = wrapper.querySelector("[data-availability-note]");
      note.textContent = selectionConflict
        ? "Wybrane pozycje nie występują razem w żadnej potwierdzonej konfiguracji. Usuń jedną z zaznaczonych pozycji; system nie odznacza filtrów automatycznie."
        : "Lista pokazuje tylko źródłowo kompletne pozycje, które można dodać do bieżącego wyboru i które nadal różnicują pozostałe konfiguracje. Alternatywy wykluczające się oraz pozycje z brakami danych są ukryte.";
      note.classList.toggle("has-removal", selectionConflict);
''',
)
replace_once(
    ui,
    '''        const available = state && state.available_equipment;
        availableCodes = Array.isArray(available) ? new Set(available) : null;
        removedCodes = state && Array.isArray(state.removed_equipment) ? state.removed_equipment : [];
        refresh();
''',
    '''        const available = state && state.available_equipment;
        availableCodes = Array.isArray(available) ? new Set(available) : null;
        selectionConflict = Boolean(state && state.selection_conflict);
        refresh();
''',
)

replace_once(
    "tools/reporting/configuration_shortlist_selection_html.py",
    ".equipment-choice{display:inline-flex;align-items:center;gap:6px;",
    ".equipment-choice[hidden]{display:none!important}.equipment-choice{display:inline-flex;align-items:center;gap:6px;",
)

tests = "tests/test_configuration_shortlist_html.py"
old_start = '''    @unittest.skipUnless(shutil.which("node"), "Node.js is required")
    def test_equipment_facets_remove_impossible_combination_before_zero_results'''
next_test = '''    @unittest.skipUnless(shutil.which("node"), "Node.js is required")
    def test_equipment_facets_require_complete_source_coverage_and_real_difference'''
replacement = '''    @unittest.skipUnless(shutil.which("node"), "Node.js is required")
    def test_equipment_facets_preserve_conflicting_selection_without_auto_removal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, catalog = self.catalog(Path(directory))
        script = REPOSITORY / "tools" / "reporting" / "configuration_shortlist_browser.js"
        program = r"""
const fs = require("fs");
const api = require(process.argv[1]);
const catalog = JSON.parse(fs.readFileSync(0, "utf8"));
const state = api.reconcileEquipmentSelection(catalog, {
  models: ["model_b"], versions: [], transmissions: [], powertrains: [],
  required_equipment: ["heated_steering_wheel", "navigation_system"],
  required_standard_equipment: []
});
process.stdout.write(JSON.stringify(state));
"""
        completed = subprocess.run(
            ["node", "-e", program, str(script)],
            input=json.dumps(catalog, ensure_ascii=False),
            text=True,
            capture_output=True,
            check=True,
        )
        state = json.loads(completed.stdout)
        self.assertGreater(state["base_match_count"], 0)
        self.assertEqual(state["compatible_match_count"], 0)
        self.assertEqual(
            state["selected_equipment"],
            ["heated_steering_wheel", "navigation_system"],
        )
        self.assertEqual(state["removed_equipment"], [])
        self.assertTrue(state["selection_conflict"])
        self.assertEqual(state["addable_equipment"], [])

'''
replace_between(tests, old_start, next_test, replacement)

anchor = "    def test_historical_catalog_uses_only_records_available_as_of_date(self) -> None:\n"
extra = '''    @unittest.skipUnless(shutil.which("node"), "Node.js is required")
    def test_selected_equipment_hides_incompatible_alternatives(self) -> None:
        script = REPOSITORY / "tools" / "reporting" / "configuration_shortlist_browser.js"
        program = r"""
const api = require(process.argv[1]);
const catalog = {configurations: [
  {configuration_code: "a", model_code: "m", version_code: "v", transmission_type: "manual", powertrain_label: "p", catalog_price: {state: "missing"}, number_of_seats: {state: "missing"}, equipment: {cluster_10: {availability_status: "standard"}, cluster_3: {availability_status: "not_available"}, cabin_led: {availability_status: "standard"}, boot_light: {availability_status: "not_available"}, camera: {availability_status: "standard"}}},
  {configuration_code: "b", model_code: "m", version_code: "v", transmission_type: "manual", powertrain_label: "p", catalog_price: {state: "missing"}, number_of_seats: {state: "missing"}, equipment: {cluster_10: {availability_status: "optional"}, cluster_3: {availability_status: "not_available"}, cabin_led: {availability_status: "standard"}, boot_light: {availability_status: "not_available"}, camera: {availability_status: "not_available"}}},
  {configuration_code: "c", model_code: "m", version_code: "v", transmission_type: "manual", powertrain_label: "p", catalog_price: {state: "missing"}, number_of_seats: {state: "missing"}, equipment: {cluster_10: {availability_status: "not_available"}, cluster_3: {availability_status: "standard"}, cabin_led: {availability_status: "not_available"}, boot_light: {availability_status: "standard"}, camera: {availability_status: "standard"}}}
]};
const state = api.reconcileEquipmentSelection(catalog, {required_equipment: ["cluster_10"], required_standard_equipment: []});
process.stdout.write(JSON.stringify(state));
"""
        completed = subprocess.run(
            ["node", "-e", program, str(script)],
            text=True,
            capture_output=True,
            check=True,
        )
        state = json.loads(completed.stdout)
        self.assertEqual(state["compatible_match_count"], 2)
        self.assertIn("cluster_10", state["available_equipment"])
        self.assertIn("camera", state["addable_equipment"])
        self.assertNotIn("cluster_3", state["available_equipment"])
        self.assertNotIn("boot_light", state["available_equipment"])

    def test_equipment_search_hidden_contract_overrides_button_display(self) -> None:
        css = (REPOSITORY / "tools" / "reporting" / "configuration_shortlist_selection_html.py").read_text(encoding="utf-8")
        ui = (REPOSITORY / "tools" / "reporting" / "configuration_shortlist_v12.js").read_text(encoding="utf-8")
        self.assertIn(".equipment-choice[hidden]{display:none!important}", css)
        self.assertIn("system nie odznacza filtrów automatycznie", ui)

'''
replace_once(tests, anchor, extra + anchor)

changelog = Path("CHANGELOG.md")
text = changelog.read_text(encoding="utf-8")
bullet = "* Fixed equipment-facet interaction: list search now visibly filters entries, selected equipment is never removed automatically, and only source-complete compatible additions remain selectable.\n"
if bullet not in text:
    start = text.index("* Published and independently re-verified minor release `data-products-v1.6.0`")
    end = text.index("\n", start) + 1
    text = text[:end] + bullet + text[end:]
changelog.write_text(text, encoding="utf-8")

Path("project/packages/equipment-facet-interaction-fix.md").write_text(
    """# Equipment Facet Interaction Fix

Status: complete

## Goal

Make equipment filtering predictable without changing source-backed availability data.

## Behaviour

- text search visibly hides non-matching equipment entries;
- selected equipment remains selected until the user removes it;
- the system never resolves a conflict by silently unchecking an earlier choice;
- the list exposes only source-complete features that can be added while retaining at least one configuration;
- mutually exclusive alternatives disappear while the conflicting choice is active;
- incomplete cross-model option data remains hidden rather than being interpreted as confirmed unavailability.

## Non-goal

This package does not infer or import options for any model. Cross-model source intake remains a separate planned package.

## Verification

- conflicting selections remain selected and are reported clearly;
- mutually exclusive instrument-cluster and lighting alternatives are hidden;
- equipment-list search obeys the HTML `hidden` contract;
- full repository test suite and project-state check.
""",
    encoding="utf-8",
)
