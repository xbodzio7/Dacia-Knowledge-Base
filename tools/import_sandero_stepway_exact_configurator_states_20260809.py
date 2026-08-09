from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data/master"
CAPTURE = (
    ROOT
    / "project/sources/dacia-pl-sandero-stepway-exact-configurator-states-20260809.json"
)
SOURCE_CODE = "src_pl_sandero_stepway_exact_configurator_states_20260809"
DATE = "2026-08-09"

OPTION_ITEMS = {
    "NA487": "sandero_media_nav_live_option",
    "PCU20": "sandero_media_display_package",
    "PCU64": "sandero_media_nav_live_package",
    "PCU66": "sandero_winter_package",
    "PCU68": "sandero_easy_package",
    "PCV0Y": "sandero_comfort_auto_package",
    "PCV12": "sandero_thermo_package",
    "RRCAM": "sandero_rear_view_camera_option",
    "TOELEC": "sandero_glass_sunroof_option",
}

COLOUR_CODES = {
    "beżowy safari": "bezowy_safari",
    "biel alpejska": "biel_alpejska",
    "czarna perła": "czarna_perla",
    "niebieski iron": "niebieski_iron",
    "sandstone": "sandstone",
    "szary schiste": "szary_schiste",
    "szary urban": "szary_urban",
    "zielony cedar": "zielony_cedar",
    "żółty amber": "zolty_amber",
}


def read_csv(name: str) -> tuple[list[str], list[dict[str, str]]]:
    path = MASTER / name
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(name: str, fields: list[str], rows: list[dict[str, str]]) -> None:
    path = MASTER / name
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def next_id(rows: list[dict[str, str]]) -> int:
    return max((int(row["id"]) for row in rows), default=0) + 1


def append_unique(
    rows: list[dict[str, str]], row: dict[str, str], *, key: str = "code"
) -> None:
    if any(existing[key] == row[key] for existing in rows):
        raise RuntimeError(f"duplicate {key}: {row[key]}")
    rows.append(row)


def option_amount(text: str) -> int:
    return int(re.sub(r"\D", "", text))


def wheel_values(label: str) -> dict[str, str]:
    size = re.search(r'(\d+)"', label)
    if not size:
        raise RuntimeError(f"wheel size missing: {label}")
    material = "alloy" if "aluminiowe" in label.lower() else "steel"
    design = re.sub(r'^\d+"\s+felgi\s+(stalowe|aluminiowe)\s+', "", label).strip()
    return {
        "wheel_size": f'{size.group(1)}"',
        "wheel_material": material,
        "wheel_design": design,
    }


def upholstery_value(label: str) -> str:
    return re.sub(r"^tapicerka\s+", "", label, flags=re.IGNORECASE).strip()


def build() -> dict[str, tuple[list[str], list[dict[str, str]]]]:
    capture = json.loads(CAPTURE.read_text(encoding="utf-8"))
    configurations = capture["configurations"]
    tables = {
        name: read_csv(name)
        for name in (
            "sources.csv",
            "source_configurations.csv",
            "commercial_items.csv",
            "commercial_item_attributes.csv",
            "commercial_item_configurations.csv",
            "configuration_attribute_values.csv",
        )
    }

    sources = tables["sources.csv"][1]
    if not any(row["code"] == SOURCE_CODE for row in sources):
        source_id = next_id(sources)
        append_unique(
            sources,
            {
            "id": str(source_id),
            "code": SOURCE_CODE,
            "source_type": "web_snapshot",
            "title": "Dacia Polska exact Sandero and Sandero Stepway configurator states",
            "publisher": "Dacia",
            "market": "PL",
            "document_date": DATE,
            "external_reference": ";".join(capture["entry_pages"]),
            "file_path": CAPTURE.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(CAPTURE.read_bytes()).hexdigest(),
            "status": "active",
            "notes": (
                "Interactive exact-state capture of all 15 current Sandero and "
                "Sandero Stepway grade and engine/transmission surfaces. Choices "
                "and priced factory options remain configuration-bounded."
            ),
            },
        )

    source_configurations = tables["source_configurations.csv"][1]
    source_configuration_id = next_id(source_configurations)
    for index, configuration in enumerate(configurations):
        code = configuration["configuration_code"]
        if any(
            row["source_code"] == SOURCE_CODE
            and row["configuration_code"] == code
            for row in source_configurations
        ):
            continue
        append_unique(
            source_configurations,
            {
                "id": str(source_configuration_id + index),
                "source_code": SOURCE_CODE,
                "configuration_code": code,
                "relationship": "documents",
                "notes": (
                    "Exact official configurator state selected interactively on "
                    f"{DATE}; stable conf URL preserved in the registered snapshot."
                ),
            },
            key="id",
        )

    commercial_items = tables["commercial_items.csv"][1]
    commercial_item_id = next_id(commercial_items)
    new_items: list[dict[str, str]] = []
    for colour, slug in COLOUR_CODES.items():
        new_items.append(
            {
                "code": f"sandero_stepway_colour_{slug}",
                "name": colour,
                "item_type": "option",
                "notes": (
                    "Exact current selectable exterior colour; applicability is "
                    "recorded per configuration without cross-grade projection."
                ),
            }
        )
    new_items.append(
        {
            "code": "sandero_media_display_package",
            "name": "Pakiet MEDIA DISPLAY",
            "item_type": "package",
            "notes": "Exact current Stepway Essential factory package (source code PCU20).",
        }
    )
    for offset, item in enumerate(new_items):
        if any(row["code"] == item["code"] for row in commercial_items):
            continue
        append_unique(
            commercial_items,
            {
                "id": str(commercial_item_id + offset),
                "code": item["code"],
                "name": item["name"],
                "item_type": item["item_type"],
                "observation_date": DATE,
                "source_code": SOURCE_CODE,
                "status": "active",
                "notes": item["notes"],
            },
        )

    commercial_attributes = tables["commercial_item_attributes.csv"][1]
    commercial_attribute_id = next_id(commercial_attributes)
    for offset, (colour, slug) in enumerate(COLOUR_CODES.items()):
        item_code = f"sandero_stepway_colour_{slug}"
        attribute_row_code = f"{item_code}__exterior_color"
        if any(row["code"] == attribute_row_code for row in commercial_attributes):
            continue
        append_unique(
            commercial_attributes,
            {
                "id": str(commercial_attribute_id + offset),
                "code": attribute_row_code,
                "commercial_item_code": item_code,
                "attribute_code": "exterior_color",
                "source_text": colour,
                "notes": (
                    "Selectable exterior-colour membership; this does not create "
                    "one scalar colour value for the configuration."
                ),
            },
        )

    mappings = tables["commercial_item_configurations.csv"][1]
    mapping_id = next_id(mappings)
    mapping_offset = 0
    for configuration in configurations:
        configuration_code = configuration["configuration_code"]
        for colour in configuration["colours"]:
            item_code = f"sandero_stepway_colour_{COLOUR_CODES[colour]}"
            is_selected = colour == configuration["selected_colour"]
            mapping_code = f"{item_code}__{configuration_code}_20260809"
            if any(row["code"] == mapping_code for row in mappings):
                continue
            append_unique(
                mappings,
                {
                    "id": str(mapping_id + mapping_offset),
                    "code": mapping_code,
                    "commercial_item_code": item_code,
                    "configuration_code": configuration_code,
                    "availability_status": "standard" if is_selected else "optional",
                    "amount": "0" if is_selected else "",
                    "currency_code": "PLN",
                    "price_date": DATE if is_selected else "",
                    "source_code": SOURCE_CODE,
                    "notes": (
                        "Exact current configurator palette membership. The selected "
                        "default is included at zero surcharge; unselected palette "
                        "entries are recorded without an inferred amount."
                    ),
                },
            )
            mapping_offset += 1
        for option in configuration["factory_options"]:
            amount = option_amount(option["price_text"])
            if amount == 0:
                continue
            item_code = OPTION_ITEMS[option["source_item_code"]]
            mapping_code = f"{item_code}__{configuration_code}_20260809"
            if any(row["code"] == mapping_code for row in mappings):
                continue
            append_unique(
                mappings,
                {
                    "id": str(mapping_id + mapping_offset),
                    "code": mapping_code,
                    "commercial_item_code": item_code,
                    "configuration_code": configuration_code,
                    "availability_status": "optional",
                    "amount": str(amount),
                    "currency_code": "PLN",
                    "price_date": DATE,
                    "source_code": SOURCE_CODE,
                    "notes": (
                        "Exact current official configurator option; literal source "
                        f"item code {option['source_item_code']}. Historical rows remain unchanged."
                    ),
                },
            )
            mapping_offset += 1

    values = tables["configuration_attribute_values.csv"][1]
    value_id = next_id(values)
    value_offset = 0
    for configuration in configurations:
        configuration_code = configuration["configuration_code"]
        current_values = wheel_values(configuration["selected_wheel"])
        current_values["upholstery_variant"] = upholstery_value(
            configuration["selected_upholstery"]
        )
        for attribute_code, value in current_values.items():
            value_code = (
                f"{configuration_code}_{attribute_code}_20260809_configurator"
            )
            if any(row["code"] == value_code for row in values):
                continue
            append_unique(
                values,
                {
                    "id": str(value_id + value_offset),
                    "code": value_code,
                    "configuration_code": configuration_code,
                    "attribute_code": attribute_code,
                    "fuel_type_code": "",
                    "gear_number": "",
                    "value": value,
                    "observation_date": DATE,
                    "source_code": SOURCE_CODE,
                    "notes": (
                        "Exact selected standard Design item in the current official "
                        "configurator; historical observations remain unchanged."
                    ),
                },
            )
            value_offset += 1

    return tables


def expected_counts() -> dict[str, int]:
    return {
        "sources.csv": 38,
        "source_configurations.csv": 269,
        "commercial_items.csv": 50,
        "commercial_item_attributes.csv": 103,
        "commercial_item_configurations.csv": 322,
        "configuration_attribute_values.csv": 3664,
    }


def verify_imported() -> None:
    for name, count in expected_counts().items():
        _, rows = read_csv(name)
        if len(rows) != count:
            raise RuntimeError(f"{name}: expected {count} rows, found {len(rows)}")
    _, sources = read_csv("sources.csv")
    source = next(row for row in sources if row["code"] == SOURCE_CODE)
    if source["sha256"] != hashlib.sha256(CAPTURE.read_bytes()).hexdigest():
        raise RuntimeError("registered capture SHA-256 differs")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.apply == args.verify:
        parser.error("choose exactly one of --apply or --verify")
    if args.verify:
        verify_imported()
        print("Sandero/Stepway exact configurator normalization: PASS")
        return 0
    tables = build()
    for name, (fields, rows) in tables.items():
        write_csv(name, fields, rows)
    verify_imported()
    print("Sandero/Stepway exact configurator normalization applied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
