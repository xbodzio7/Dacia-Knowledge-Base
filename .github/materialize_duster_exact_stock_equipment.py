#!/usr/bin/env python3
"""Materialize the Duster exact-stock equipment expansion package."""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
DATE = "2026-07-25"
SOURCE_CODE = "src_pl_duster_exact_stock_equipment_20260725"
PRICE_SOURCE = "src_pl_duster_price_my26_20260703"
SNAPSHOT = ROOT / "project" / "sources" / "dacia-pl-duster-exact-stock-equipment-20260725.json"
IMPORTER = ROOT / "tools" / "import_duster_exact_stock_equipment_20260725.py"
TEST = ROOT / "tests" / "test_duster_exact_stock_equipment_20260725.py"


def e(attribute_code: str, source_label: str, status: str = "standard", section: str = "Wyposażenie podstawowe") -> dict[str, str]:
    return {
        "attribute_code": attribute_code,
        "availability_status": status,
        "source_section": section,
        "source_label": source_label,
    }


COMMON = [
    e("anti_lock_braking_system", "ABS z układem wspomagania nagłego hamowania (AFU)"),
    e("onboard_computer", "Komputer pokładowy z informacją o temperaturze zewnętrznej, licznikiem kilometrów, zużyciem paliwa, średnią prędkością i zasięgiem"),
    e("driver_front_airbag", "Poduszka powietrzna czołowa kierowcy"),
    e("passenger_front_airbag", "Poduszka powietrzna czołowa pasażera z możliwością dezaktywacji"),
    e("front_side_airbags", "Poduszki powietrzne boczne z przodu chroniące głowę i klatkę piersiową"),
    e("curtain_airbags", "Poduszki powietrzne kurtynowe"),
    e("electronic_stability_control", "System kontroli toru jazdy (ESC) + system wspomagania ruszania pod górę (HSA)"),
    e("hill_start_assist", "System kontroli toru jazdy (ESC) + system wspomagania ruszania pod górę (HSA)"),
    e("traction_control", "System kontroli trakcji (TCS)"),
    e("front_windows_power", "Szyby przednie regulowane elektrycznie z włącznikiem impulsowym"),
    e("rear_windows_power", "Szyby tylne regulowane elektrycznie z włącznikiem impulsowym"),
    e("one_touch_windows", "Szyby przednie i tylne regulowane elektrycznie z włącznikiem impulsowym"),
    e("rear_parking_sensors", "Czujniki parkowania z tyłu"),
    e("emergency_call_ecall", "eCall - połączenie alarmowe"),
    e("remote_firmware_updates", "FOTA (Firmware Over-The-Air)"),
    e("driver_seat_height_adjustment", "Fotel kierowcy z regulacją wysokości"),
    e("rear_usb_c_ports", "Gniazda USB-C 2x z tyłu w konsoli centralnej dla pasażerów drugiego rzędu"),
    e("rear_view_camera", "Kamera cofania"),
    e("eco_leather_steering_wheel", "Kierownica pokryta skórą ekologiczną"),
    e("steering_wheel_height_adjustment", "Kierownica z regulacją: wysokości/głębokości"),
    e("steering_wheel_reach_adjustment", "Kierownica z regulacją: wysokości/głębokości"),
    e("front_centre_armrest", "Konsola centralna z podłokietnikiem i schowkiem"),
    e("rear_seat_folding", "Oparcie tylnej kanapy składane 1/3 i 2/3"),
    e("connected_services", "Pakiet usług zdalnych na 8 lat: znajdź mój pojazd"),
    e("front_seat_belt_pretensioners", "Pasy bezpieczeństwa przednie i tylne z napinaczami pirotechnicznymi bez regulacji wysokości"),
    e("rear_seat_belt_pretensioners", "Pasy bezpieczeństwa przednie i tylne z napinaczami pirotechnicznymi bez regulacji wysokości"),
    e("driver_seat_belt_height_adjustment", "Pasy bezpieczeństwa przednie i tylne z napinaczami pirotechnicznymi bez regulacji wysokości", "not_available"),
    e("rear_three_point_seat_belts", "Pasy bezpieczeństwa z tyłu trzy, 3-punktowe"),
    e("my_safety_button", "Przycisk My Safety umożliwiający łatwe włączenie/wyłączanie wybranych systemów wspomagających kierowcę"),
    e("speed_limiter", "Regulator - ogranicznik prędkości"),
    e("cruise_control", "Regulator - ogranicznik prędkości"),
    e("rescue_code", "Rescue Code - kod QR na przedniej i tylnej szybie"),
    e("seat_belt_reminder", "Sygnalizacja dźwiękowa i wizualna niezapięcia pasów bezpieczeństwa"),
    e("door_open_warning", "Sygnalizacja niezamknięcia drzwi"),
    e("tyre_pressure_monitoring_system", "System kontroli ciśnienia w oponach, pośredni"),
    e("lane_departure_warning", "System kontroli pasa ruchu (LDWS)"),
    e("driver_attention_monitoring", "System kontroli zmęczenia kierowcy (DDAW)"),
    e("traffic_sign_recognition", "System rozpoznawania znaków drogowych z ostrzeganiem o nadmiernej prędkości (ISA)"),
    e("lane_keep_assist", "System utrzymania pasa ruchu (LKA)"),
    e("automatic_emergency_braking", "System wspomagania nagłego hamowania, aktywny, z funkcją wykrywania pieszych i rowerzystów (AEBS)"),
    e("led_daytime_running_lights", "Światła do jazdy dziennej LED w kształcie litery Y"),
    e("led_headlights", "Światła mijania LED"),
    e("automatic_headlights", "Światła mijania/wycieraczki włączane automatycznie"),
    e("rain_sensing_wipers", "Światła mijania/wycieraczki włączane automatycznie"),
    e("eco_mode", "Tryb ECO"),
    e("isofix_rear", "Uchwyty ISOFIX do instalacji fotelika dziecięcego z tyłu"),
    e("gear_shift_indicator", "Wskaźnik zmiany biegów"),
    e("instrument_cluster_colour_7", "Wyświetlacz zespołu wskaźników 7'' cyfrowy, kolorowy, konfigurowalny"),
    e("central_locking", "Zamek centralny, zdalnie sterowany falami radiowymi"),
]

EXPRESSION = COMMON + [
    e("manual_air_conditioning", "Klimatyzacja manualna"),
    e("side_mirrors_electric_adjustment", "Lusterka boczne zewnętrzne, regulowane elektrycznie i ogrzewane"),
    e("side_mirrors_heated", "Lusterka boczne zewnętrzne, regulowane elektrycznie i ogrzewane"),
    e("media_display_system", "System Media Display z ekranem dotykowym 10'', radiem, replikacją smartfona, Bluetooth, 4 głośnikami i pakietem usług zdalnych"),
    e("roof_rails", "Relingi dachowe czarne"),
]

EXTREME = COMMON + [
    e("automatic_climate_control", "Klimatyzacja automatyczna"),
    e("side_mirrors_electric_adjustment", "Lusterka boczne zewnętrzne, regulowane, podgrzewane i składane elektrycznie"),
    e("side_mirrors_heated", "Lusterka boczne zewnętrzne, regulowane, podgrzewane i składane elektrycznie"),
    e("side_mirrors_folding", "Lusterka boczne zewnętrzne, regulowane, podgrzewane i składane elektrycznie"),
    e("media_display_system", "System Media Display z ekranem dotykowym 10'', radiem, replikacją smartfona, Bluetooth, 4 głośnikami i pakietem usług zdalnych"),
    e("roof_rails", "Relingi dachowe, modułowe"),
    e("modular_roof_rails", "Relingi dachowe, modułowe"),
    e("fog_lights", "Światła przeciwmgielne"),
    e("high_beam_assist", "Funkcja automatycznej zmiany świateł drogowych na mijania (AHL)", section="Wyposażenie dodatkowe / widoczność i oświetlenie"),
    e("keyless_entry", "Karta Keyless Entry", section="Wyposażenie dodatkowe / komfort i wnętrze"),
    e("driver_seat_lumbar_adjustment", "Fotel kierowcy z regulacją lędźwi + fotel pasażera z regulacją wysokości", section="Wyposażenie dodatkowe / komfort i wnętrze"),
    e("passenger_seat_height_adjustment", "Fotel kierowcy z regulacją lędźwi + fotel pasażera z regulacją wysokości", section="Wyposażenie dodatkowe / komfort i wnętrze"),
    e("hill_descent_control", "ESP + system wspomagający ruszanie pod górę oraz kontroli zjazdu ze wzniesienia HSA/HDC", section="Wyposażenie dodatkowe / bezpieczeństwo"),
    e("boot_12v_socket", "Gniazdo 12V w bagażniku", section="Wyposażenie dodatkowe / multimedia"),
    e("tyre_repair_kit", "Zestaw do naprawy uszkodzenia opony", section="Wyposażenie dodatkowe / bezpieczeństwo"),
    e("privacy_glass", "Przyciemniane tylne szyby", section="Wyposażenie dodatkowe / widoczność i oświetlenie"),
    e("heated_front_seats", "Pakiet ZIMOWY PLUS: przednie fotele podgrzewane", section="Wyposażenie dodatkowe / Pakiet ZIMOWY PLUS"),
    e("heated_steering_wheel", "Pakiet ZIMOWY PLUS: kierownica podgrzewana", section="Wyposażenie dodatkowe / Pakiet ZIMOWY PLUS"),
    e("heated_windscreen", "Pakiet ZIMOWY PLUS: podgrzewana przednia szyba", section="Wyposażenie dodatkowe / Pakiet ZIMOWY PLUS"),
    e("youclip_phone_holder", "YouClip - uchwyt do smartfona"),
    e("safe_distance_warning", "System kontroli bezpiecznej odległości (DW)", section="Wyposażenie dodatkowe / bezpieczeństwo"),
    e("manual_day_night_rearview_mirror", "Lusterko wsteczne z ustawieniem dzień/noc", section="Wyposażenie dodatkowe / widoczność i oświetlenie"),
    e("one_touch_turn_signals", "Kierunkowskazy impulsowe", section="Wyposażenie dodatkowe / widoczność i oświetlenie"),
    e("adjustable_boot_floor", "Bez podłogi bagażnika ustawianej w dwóch płaszczyznach (góra i dół)", "not_available", "Wyposażenie skonfigurowanego pojazdu / komfort i wnętrze"),
    e("front_parking_sensors", "Pakiet PARKING: czujniki parkowania z przodu, z tyłu i z boku", section="Wyposażenie dodatkowe / Pakiet PARKING"),
    e("360_camera_system", "Pakiet PARKING: Multiview kamera", section="Wyposażenie dodatkowe / Pakiet PARKING"),
    e("blind_spot_monitoring", "Pakiet PARKING: system kontroli martwego pola (BSW)", section="Wyposażenie dodatkowe / Pakiet PARKING"),
]

JOURNEY = COMMON + [
    e("automatic_climate_control", "Klimatyzacja automatyczna"),
    e("side_mirrors_electric_adjustment", "Lusterka boczne zewnętrzne, regulowane, podgrzewane i składane elektrycznie"),
    e("side_mirrors_heated", "Lusterka boczne zewnętrzne, regulowane, podgrzewane i składane elektrycznie"),
    e("side_mirrors_folding", "Lusterka boczne zewnętrzne, regulowane, podgrzewane i składane elektrycznie"),
    e("navigation_system", "System Media Nav Live"),
    e("roof_rails", "Relingi dachowe czarne"),
    e("fog_lights", "Światła przeciwmgielne"),
    e("high_beam_assist", "Funkcja automatycznej zmiany świateł drogowych na mijania (AHL)"),
    e("keyless_entry", "Keyless Entry - system bezkluczykowego dostępu i uruchamiania silnika"),
    e("driver_seat_lumbar_adjustment", "Fotel kierowcy z regulacją podparcia lędźwiowego"),
    e("passenger_seat_height_adjustment", "Pakiet ZIMOWY PLUS (Journey): fotel pasażera z regulacją wysokości", section="Pakiet ZIMOWY PLUS / skład według oficjalnego cennika MY26"),
    e("boot_12v_socket", "Gniazdo 12V w bagażniku"),
    e("tyre_repair_kit", "Zestaw do naprawy uszkodzenia opony"),
    e("privacy_glass", "Szyby tylne przyciemniane"),
    e("adjustable_boot_floor", "Podłoga bagażnika ustawiana w dwóch płaszczyznach (góra i dół)"),
    e("electronic_parking_brake", "Hamulec postojowy, automatyczny"),
    e("wireless_charging", "Ładowarka indukcyjna"),
    e("front_parking_sensors", "Pakiet PARKING: czujniki parkowania przód/tył", section="Dodatkowe wyposażenie prezentowanego egzemplarza / Pakiet PARKING"),
    e("360_camera_system", "Pakiet PARKING: kamera Multiview 360", section="Dodatkowe wyposażenie prezentowanego egzemplarza / Pakiet PARKING"),
    e("blind_spot_monitoring", "Pakiet PARKING: kontrola martwego pola", section="Dodatkowe wyposażenie prezentowanego egzemplarza / Pakiet PARKING"),
    e("heated_front_seats", "Pakiet ZIMOWY PLUS: podgrzewane fotele przednie", section="Dodatkowe wyposażenie prezentowanego egzemplarza / Pakiet ZIMOWY PLUS"),
    e("heated_steering_wheel", "Pakiet ZIMOWY PLUS: podgrzewana kierownica", section="Dodatkowe wyposażenie prezentowanego egzemplarza / Pakiet ZIMOWY PLUS"),
    e("heated_windscreen", "Pakiet ZIMOWY PLUS: podgrzewana szyba przednia", section="Dodatkowe wyposażenie prezentowanego egzemplarza / Pakiet ZIMOWY PLUS"),
    e("youclip_phone_holder", "YouClip - uchwyt do smartfona"),
    e("safe_distance_warning", "System kontroli bezpiecznej odległości", section="Wyposażenie wersji Journey"),
    e("adaptive_cruise_control", "Aktywny tempomat", section="Wyposażenie wersji Journey"),
]

CARDS = [
    {
        "configuration_code": "duster_iii_expression_ecog120_4x2_automatic",
        "version_code": "duster_iii_expression",
        "stock_id": "121553",
        "url": "https://kup.dacia.pl/wyszukiwarkaszczegoly/dacia/duster/2026/121553",
        "equipment": EXPRESSION,
        "selected_packages": [],
        "non_imports": [
            {"attribute_code": "side_mirrors_folding", "reason": "Conflicting official Expression descriptions remain unresolved."},
            {"attribute_code": "shark_fin_antenna", "reason": "The exact card does not state the factory antenna type."},
        ],
    },
    {
        "configuration_code": "duster_iii_extreme_ecog120_4x2_automatic",
        "version_code": "duster_iii_extreme",
        "stock_id": "121540",
        "url": "https://kup.dacia.pl/wyszukiwarkaszczegoly/dacia/duster/2026/121540",
        "supporting_current_url": "https://kup.dacia.pl/wyszukiwarkaszczegoly/dacia/duster/2026/127567",
        "equipment": EXTREME,
        "selected_packages": [
            {"commercial_item_code": "duster_parking_package", "name": "Pakiet PARKING", "catalogue_price": 2200, "source_label": "WYPOSAŻENIE DODATKOWE: Pakiet PARKING"},
            {"commercial_item_code": "duster_winter_plus_extreme_package", "name": "Pakiet ZIMOWY PLUS (Extreme)", "catalogue_price": 2300, "source_label": "WYPOSAŻENIE DODATKOWE: Pakiet ZIMOWY PLUS"},
        ],
        "non_imports": [
            {"attribute_code": "shark_fin_antenna", "reason": "The exact card does not state the factory antenna type."},
            {"concept": "newer_supporting_card_package_label", "reason": "Supporting card 127567 shortens one dealer-authored package heading to Pakiet ZIMOWY; the dated primary card 121540 explicitly names and itemizes Pakiet ZIMOWY PLUS and remains the evidence for this exact stock configuration."},
        ],
    },
    {
        "configuration_code": "duster_iii_journey_ecog120_4x2_automatic",
        "version_code": "duster_iii_journey",
        "stock_id": "121030",
        "url": "https://kup.dacia.pl/wyszukiwarkaszczegoly/dacia/duster/2026/121030",
        "equipment": JOURNEY,
        "selected_packages": [
            {"commercial_item_code": "duster_parking_package", "name": "Pakiet PARKING", "catalogue_price": 2200, "source_label": "Dodatkowe wyposażenie prezentowanego egzemplarza: Pakiet PARKING"},
            {"commercial_item_code": "duster_winter_plus_journey_package", "name": "Pakiet ZIMOWY PLUS (Journey)", "catalogue_price": 2300, "source_label": "Dodatkowe wyposażenie prezentowanego egzemplarza: Pakiet ZIMOWY PLUS"},
        ],
        "non_imports": [
            {"attribute_code": "shark_fin_antenna", "reason": "The exact card does not state the factory antenna type."},
        ],
    },
]


def run(*args: str) -> None:
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="")


def snapshot_payload() -> dict:
    return {
        "version": 1,
        "source_code": SOURCE_CODE,
        "source_type": "web_snapshot",
        "publisher": "Dacia",
        "market": "PL",
        "observed_on": DATE,
        "volatility": "dynamic_official_stock_cards",
        "scope": {
            "model_code": "duster_iii",
            "powertrain_label": "Eco-G 120 4x2",
            "transmission_type": "automatic",
            "configurations": [card["configuration_code"] for card in CARDS],
        },
        "cards": CARDS,
        "price_list_evidence": {
            "source_code": PRICE_SOURCE,
            "document_date": "2026-07-03",
            "role": "Official name, component membership and catalogue gross price of each package. Exact stock cards prove selection for the specific configuration.",
        },
        "normalization_rules": [
            "Only explicit equipment statements from the exact stock card are normalized.",
            "A compound statement may support multiple existing boolean attributes only when every normalized capability is explicit.",
            "Named packages are mapped through existing commercial tables; price-list evidence and exact-card selection remain separate dated rows.",
            "A selected package row uses availability_status standard with an empty amount because the stock card proves inclusion but does not restate the standalone package price.",
            "Missing text is not interpreted as not_available.",
            "Wheel, upholstery, paint, warranty, dealer accessories and internal ordering criteria are not converted to equipment availability.",
            "Factory antenna type and the conflicting Expression folding-mirror state remain unimported.",
        ],
    }


IMPORTER_TEMPLATE = r'''#!/usr/bin/env python3
"""Import exact Duster Eco-G 120 automatic stock equipment and selected packages."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SNAPSHOT = ROOT / "project" / "sources" / "dacia-pl-duster-exact-stock-equipment-20260725.json"
SOURCE_CODE = "src_pl_duster_exact_stock_equipment_20260725"
PRICE_SOURCE = "src_pl_duster_price_my26_20260703"
DATE = "2026-07-25"
SNAPSHOT_SHA256 = "__SHA__"
CONFIGURATION_COUNTS = {
    "duster_iii_expression_ecog120_4x2_automatic": 54,
    "duster_iii_extreme_ecog120_4x2_automatic": 76,
    "duster_iii_journey_ecog120_4x2_automatic": 75,
}
TARGETS = {
    "sources.csv": ("id", "code", "source_type", "title", "publisher", "market", "document_date", "external_reference", "file_path", "sha256", "status", "notes"),
    "source_models.csv": ("id", "source_code", "model_code", "relationship", "notes"),
    "source_versions.csv": ("id", "source_code", "version_code", "relationship", "notes"),
    "source_configurations.csv": ("id", "source_code", "configuration_code", "relationship", "notes"),
    "configuration_attribute_availability.csv": ("id", "code", "configuration_code", "attribute_code", "availability_status", "observation_date", "source_code", "notes"),
    "commercial_item_configurations.csv": ("id", "code", "commercial_item_code", "configuration_code", "availability_status", "amount", "currency_code", "price_date", "source_code", "notes"),
}

class ContractError(RuntimeError):
    pass

def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ContractError(f"missing CSV header: {path}")
        return list(reader)

def require_header(path: Path, fields: Sequence[str]) -> None:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        header = next(csv.reader(handle), None)
    if header != list(fields):
        raise ContractError(f"unexpected header in {path}: {header!r}")

def write_rows(path: Path, fields: Sequence[str], rows: Iterable[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

def load_snapshot() -> dict:
    if file_sha256(SNAPSHOT) != SNAPSHOT_SHA256:
        raise ContractError("normalized snapshot SHA-256 mismatch")
    payload = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    if payload.get("source_code") != SOURCE_CODE or payload.get("observed_on") != DATE:
        raise ContractError("snapshot identity mismatch")
    return payload

def normalized_contract() -> dict[str, list[dict[str, str]]]:
    payload = load_snapshot()
    configurations = {row["code"]: row for row in read_rows(MASTER / "configurations.csv") if row.get("status") == "active"}
    attributes = {row["code"]: row for row in read_rows(MASTER / "attributes.csv") if row.get("status") == "active"}
    statuses = {row["code"] for row in read_rows(MASTER / "enums" / "equipment_availability_statuses.csv") if row.get("status") == "active"}
    items = {row["code"]: row for row in read_rows(MASTER / "commercial_items.csv") if row.get("status") == "active"}
    memberships: dict[str, set[str]] = {}
    for row in read_rows(MASTER / "commercial_item_attributes.csv"):
        memberships.setdefault(row["commercial_item_code"], set()).add(row["attribute_code"])
    source_codes = {row["code"] for row in read_rows(MASTER / "sources.csv") if row.get("status") == "active"}
    if PRICE_SOURCE not in source_codes:
        raise ContractError("official Duster MY26 price-list source is not active")

    availability: list[dict[str, str]] = []
    commercial: list[dict[str, str]] = []
    source_versions: list[dict[str, str]] = []
    source_configurations: list[dict[str, str]] = []
    seen_versions: set[str] = set()
    counts: Counter[str] = Counter()
    statuses_count: Counter[str] = Counter()

    cards = payload.get("cards", [])
    if len(cards) != 3:
        raise ContractError("expected three exact stock cards")
    if {card["configuration_code"] for card in cards} != set(CONFIGURATION_COUNTS):
        raise ContractError("exact configuration coverage mismatch")

    for card in cards:
        config = card["configuration_code"]
        version = card["version_code"]
        row = configurations.get(config)
        if row is None or row.get("version_code") != version or row.get("transmission_type") != "automatic":
            raise ContractError(f"active exact automatic configuration missing: {config}")
        if version not in seen_versions:
            seen_versions.add(version)
            source_versions.append({"source_code": SOURCE_CODE, "version_code": version, "relationship": "exact_stock_equipment_documents", "notes": f"Official exact stock equipment card observed {DATE}."})
        source_configurations.append({"source_code": SOURCE_CODE, "configuration_code": config, "relationship": "exact_stock_equipment_documents", "notes": f"Official Dacia Poland exact stock card {card['stock_id']} provides equipment and selected-package evidence."})

        seen_attributes: set[str] = set()
        card_status: dict[str, str] = {}
        for equipment in card.get("equipment", []):
            attribute = equipment["attribute_code"]
            status = equipment["availability_status"]
            if attribute in seen_attributes:
                raise ContractError(f"duplicate exact-card attribute: {config}/{attribute}")
            seen_attributes.add(attribute)
            definition = attributes.get(attribute)
            if definition is None or definition.get("data_type") != "boolean":
                raise ContractError(f"inactive or non-boolean equipment attribute: {attribute}")
            if status not in statuses:
                raise ContractError(f"invalid availability status: {status}")
            card_status[attribute] = status
            counts[config] += 1
            statuses_count[status] += 1
            availability.append({
                "code": f"{config}_{attribute}_exact_stock_20260725",
                "configuration_code": config,
                "attribute_code": attribute,
                "availability_status": status,
                "observation_date": DATE,
                "source_code": SOURCE_CODE,
                "notes": f"Official Dacia Poland exact stock card {card['stock_id']}, section {equipment['source_section']}: {equipment['source_label']}.",
            })

        for package in card.get("selected_packages", []):
            item = package["commercial_item_code"]
            if item not in items or not memberships.get(item):
                raise ContractError(f"active commercial package or membership missing: {item}")
            missing_components = sorted(attr for attr in memberships[item] if card_status.get(attr) != "standard")
            if missing_components:
                raise ContractError(f"selected package components are not exact-card standard for {config}/{item}: {missing_components}")
            amount = str(package["catalogue_price"])
            commercial.append({
                "code": f"{item}__{config}__exact_stock_offer_20260703",
                "commercial_item_code": item,
                "configuration_code": config,
                "availability_status": "optional",
                "amount": amount,
                "currency_code": "PLN",
                "price_date": "2026-07-03",
                "source_code": PRICE_SOURCE,
                "notes": f"Official Duster MY26 price list supplies package name, composition and {amount} PLN gross price; exact stock card {card['stock_id']} independently proves applicability to this automatic configuration.",
            })
            commercial.append({
                "code": f"{item}__{config}__selected_exact_stock_20260725",
                "commercial_item_code": item,
                "configuration_code": config,
                "availability_status": "standard",
                "amount": "",
                "currency_code": "PLN",
                "price_date": DATE,
                "source_code": SOURCE_CODE,
                "notes": f"Selected in exact stock vehicle {card['stock_id']}: {package['source_label']}. Empty amount preserves selection without claiming that the stock card restates the standalone package price.",
            })

    if dict(counts) != CONFIGURATION_COUNTS:
        raise ContractError(f"unexpected per-configuration equipment counts: {dict(counts)}")
    if len(availability) != 205 or dict(statuses_count) != {"standard": 201, "not_available": 4}:
        raise ContractError(f"unexpected exact equipment distribution: total={len(availability)}, statuses={dict(statuses_count)}")
    if len(commercial) != 8:
        raise ContractError("expected four optional offers and four exact-stock selections")
    if any(row["attribute_code"] == "shark_fin_antenna" for row in availability):
        raise ContractError("Duster antenna type must remain unimported")
    if any(row["configuration_code"].endswith("expression_ecog120_4x2_automatic") and row["attribute_code"] == "side_mirrors_folding" for row in availability):
        raise ContractError("Expression folding-mirror conflict must remain unimported")

    source_row = {
        "code": SOURCE_CODE,
        "source_type": "web_snapshot",
        "title": "Dacia Polska exact Duster Eco-G 120 automatic stock equipment cards",
        "publisher": "Dacia",
        "market": "PL",
        "document_date": DATE,
        "external_reference": "https://kup.dacia.pl/",
        "file_path": SNAPSHOT.relative_to(ROOT).as_posix(),
        "sha256": SNAPSHOT_SHA256,
        "status": "active",
        "notes": "Normalized snapshot of exact Expression, Extreme and Journey automatic stock equipment, selected packages, expired-card evidence and explicit non-import boundaries.",
    }
    return {
        "sources.csv": [source_row],
        "source_models.csv": [{"source_code": SOURCE_CODE, "model_code": "duster_iii", "relationship": "exact_stock_equipment_for", "notes": "Three official 2026 Eco-G 120 automatic exact-stock equipment cards."}],
        "source_versions.csv": sorted(source_versions, key=lambda row: row["version_code"]),
        "source_configurations.csv": sorted(source_configurations, key=lambda row: row["configuration_code"]),
        "configuration_attribute_availability.csv": sorted(availability, key=lambda row: row["code"]),
        "commercial_item_configurations.csv": sorted(commercial, key=lambda row: row["code"]),
    }

def owned(rows: list[dict[str, str]], name: str, generated: list[dict[str, str]]) -> list[dict[str, str]]:
    if name == "sources.csv":
        return [row for row in rows if row.get("code") == SOURCE_CODE]
    if name == "commercial_item_configurations.csv":
        codes = {row["code"] for row in generated}
        return [row for row in rows if row.get("code") in codes]
    return [row for row in rows if row.get("source_code") == SOURCE_CODE]

def semantic(rows: Iterable[dict[str, str]], fields: Sequence[str]) -> list[tuple[str, ...]]:
    payload_fields = [field for field in fields if field != "id"]
    return sorted(tuple(row.get(field, "") for field in payload_fields) for row in rows)

def check() -> None:
    contract = normalized_contract()
    for name, fields in TARGETS.items():
        path = MASTER / name
        require_header(path, fields)
        current = read_rows(path)
        if semantic(owned(current, name, contract[name]), fields) != semantic(contract[name], fields):
            raise ContractError(f"master data differs from normalized contract: {name}")

def apply() -> None:
    contract = normalized_contract()
    for name, fields in TARGETS.items():
        path = MASTER / name
        require_header(path, fields)
        rows = read_rows(path)
        current_owned = owned(rows, name, contract[name])
        retained = [row for row in rows if row not in current_owned]
        next_id = max((int(row["id"]) for row in retained), default=0) + 1
        generated = [{"id": str(next_id + index), **row} for index, row in enumerate(contract[name])]
        write_rows(path, fields, [*retained, *generated])
    check()

def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        apply() if args.apply else check()
    except (ContractError, OSError, csv.Error, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("PASS: Duster exact stock equipment contract")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
'''

TEST_TEXT = r'''from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
MASTER = REPOSITORY / "data" / "master"
SOURCE_CODE = "src_pl_duster_exact_stock_equipment_20260725"
PRICE_SOURCE = "src_pl_duster_price_my26_20260703"
DATE = "2026-07-25"
CONFIGURATION_COUNTS = {
    "duster_iii_expression_ecog120_4x2_automatic": 54,
    "duster_iii_extreme_ecog120_4x2_automatic": 76,
    "duster_iii_journey_ecog120_4x2_automatic": 75,
}

def rows(name: str) -> list[dict[str, str]]:
    with (MASTER / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))

class DusterExactStockEquipment20260725Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sources = rows("sources.csv")
        cls.availability = [row for row in rows("configuration_attribute_availability.csv") if row["source_code"] == SOURCE_CODE]
        cls.commercial = rows("commercial_item_configurations.csv")
        cls.snapshot_path = REPOSITORY / "project" / "sources" / "dacia-pl-duster-exact-stock-equipment-20260725.json"
        cls.snapshot = json.loads(cls.snapshot_path.read_text(encoding="utf-8"))

    def test_snapshot_hash_matches_registered_source(self) -> None:
        source = next(row for row in self.sources if row["code"] == SOURCE_CODE)
        self.assertEqual(hashlib.sha256(self.snapshot_path.read_bytes()).hexdigest(), source["sha256"])
        self.assertEqual(source["document_date"], DATE)

    def test_exact_equipment_counts_and_statuses(self) -> None:
        self.assertEqual(len(self.availability), 205)
        self.assertEqual(Counter(row["availability_status"] for row in self.availability), {"standard": 201, "not_available": 4})
        self.assertEqual(Counter(row["configuration_code"] for row in self.availability), Counter(CONFIGURATION_COUNTS))

    def test_non_inference_boundaries_remain_absent(self) -> None:
        keys = {(row["configuration_code"], row["attribute_code"]) for row in self.availability}
        self.assertFalse(any(attribute == "shark_fin_antenna" for _, attribute in keys))
        self.assertNotIn(("duster_iii_expression_ecog120_4x2_automatic", "side_mirrors_folding"), keys)

    def test_explicit_negative_states_are_preserved(self) -> None:
        negative = {(row["configuration_code"], row["attribute_code"]) for row in self.availability if row["availability_status"] == "not_available"}
        self.assertEqual(negative, {
            ("duster_iii_expression_ecog120_4x2_automatic", "driver_seat_belt_height_adjustment"),
            ("duster_iii_extreme_ecog120_4x2_automatic", "driver_seat_belt_height_adjustment"),
            ("duster_iii_extreme_ecog120_4x2_automatic", "adjustable_boot_floor"),
            ("duster_iii_journey_ecog120_4x2_automatic", "driver_seat_belt_height_adjustment"),
        })

    def test_four_package_offers_and_four_selected_states(self) -> None:
        scoped = [row for row in self.commercial if row["code"].endswith("exact_stock_offer_20260703") or row["source_code"] == SOURCE_CODE]
        self.assertEqual(len(scoped), 8)
        self.assertEqual(Counter(row["availability_status"] for row in scoped), {"optional": 4, "standard": 4})
        selected = [row for row in scoped if row["source_code"] == SOURCE_CODE]
        self.assertTrue(all(row["amount"] == "" for row in selected))
        self.assertEqual({row["price_date"] for row in selected}, {DATE})
        offers = [row for row in scoped if row["source_code"] == PRICE_SOURCE]
        self.assertEqual(sorted(int(row["amount"]) for row in offers), [2200, 2200, 2300, 2300])

    def test_selected_package_components_are_standard(self) -> None:
        standard = {(row["configuration_code"], row["attribute_code"]) for row in self.availability if row["availability_status"] == "standard"}
        for config in ("duster_iii_extreme_ecog120_4x2_automatic", "duster_iii_journey_ecog120_4x2_automatic"):
            for attribute in ("front_parking_sensors", "rear_parking_sensors", "360_camera_system", "blind_spot_monitoring", "heated_front_seats", "heated_steering_wheel", "heated_windscreen"):
                self.assertIn((config, attribute), standard)

    def test_snapshot_preserves_primary_and_supporting_extreme_cards(self) -> None:
        extreme = next(card for card in self.snapshot["cards"] if card["stock_id"] == "121540")
        self.assertEqual(extreme["supporting_current_url"].rsplit("/", 1)[-1], "127567")
        self.assertEqual({row["commercial_item_code"] for row in extreme["selected_packages"]}, {"duster_parking_package", "duster_winter_plus_extreme_package"})

    def test_importer_check_is_green(self) -> None:
        completed = subprocess.run([sys.executable, "tools/import_duster_exact_stock_equipment_20260725.py", "--check"], cwd=REPOSITORY, text=True, capture_output=True)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

if __name__ == "__main__":
    unittest.main()
'''

PACKAGE_DOC = '''# Duster Exact Stock Equipment Expansion — 2026-07-25

Status: complete

## Goal

Expand the three exact 2026 Duster Eco-G 120 automatic stock configurations with source-backed equipment and selected-package evidence without projecting manual-version data or converting missing text into negative availability.

## Exact equipment

The package adds 205 dated configuration-level equipment observations:

- Expression automatic — 54 records;
- Extreme automatic — 76 records;
- Journey automatic — 75 records.

The distribution is 201 `standard` and four explicit `not_available` states. The negative states are limited to source wording that explicitly removes driver seat-belt height adjustment from all three cards and the configured Extreme card's explicit absence of the two-level boot floor.

Compound source statements are decomposed only where every capability is explicit, for example ESC/HSA, automatic lights/rain-sensing wipers, electric/heated/folding mirrors and front/rear pyrotechnic pretensioners.

## Commercial packages

The existing commercial model is reused without schema changes. The official Duster MY26 price list supplies package names, component membership and gross prices, while exact stock cards prove applicability and selection.

Four optional offer mappings are added:

- Extreme — Pakiet PARKING, 2,200 PLN;
- Extreme — Pakiet ZIMOWY PLUS, 2,300 PLN;
- Journey — Pakiet PARKING, 2,200 PLN;
- Journey — Pakiet ZIMOWY PLUS, 2,300 PLN.

Four later `standard` rows record that those packages are selected in the exact stock vehicles. Their amount is deliberately empty: the stock card proves inclusion but does not restate a standalone package price. The earlier optional price-list row remains the price observation.

## Source lifecycle

Stock card 121540 expired after the first observation. Its normalized snapshot preserves the explicit Extreme PARKING and ZIMOWY PLUS descriptions. Current card 127567 is retained as supporting evidence but does not replace the dated primary card; its shortened dealer-authored `Pakiet ZIMOWY` heading is documented rather than allowed to erase the original exact-card evidence.

## Boundaries

- no equipment is copied from manual configurations;
- Expression power-folding mirrors remain unresolved;
- factory antenna type remains unimported for all three configurations;
- wheel, upholstery and paint wording is not converted into boolean equipment;
- rubber mats, luggage-compartment liners, warranty and dealer accessories remain outside factory-configuration equipment;
- missing rows are not interpreted as `not_available`.

## Determinism

`tools/import_duster_exact_stock_equipment_20260725.py` verifies the snapshot SHA-256, exact configuration coverage, active boolean attributes, 205-row distribution, four package offers, four selected-package states and non-inference boundaries. `--apply` replaces only records owned by this source and the exact generated commercial mapping codes; `--check` reproduces the contract without mutation.
'''

REVIEW_DOC = '''# Duster Exact Stock Equipment Review — 2026-07-25

## Accepted evidence

- official Dacia Poland exact stock cards 121553, 121540 and 121030;
- official Duster MY26 price list effective 3 July 2026 for package names, membership and prices;
- indexed primary-card content retained in the normalized snapshot when dynamic stock URLs expire;
- current Extreme card 127567 as supporting lifecycle evidence only.

## Accepted normalization

- explicit basic and configured equipment mapped to existing boolean attributes;
- explicit package components mapped as present in the exact stock vehicle;
- exact negative wording retained only for seat-belt height adjustment and the Extreme two-level boot floor;
- package availability/price and selected-in-stock state stored as separate dated commercial rows.

## Rejected inferences

- no manual-to-automatic trim projection;
- no antenna classification;
- no Expression folding-mirror decision;
- no negative status from omitted text;
- no conversion of wheel, upholstery, paint, warranty or dealer accessories into boolean equipment.

## Result

Accepted for import:

- 205 exact equipment observations;
- four optional package-price mappings;
- four selected-package states;
- one model, three version and three configuration source relationships.

Deferred:

- automatic-specific homologation values;
- factory antenna type;
- Expression folding-mirror resolution;
- dealer-accessory and financing information.
'''

README_PARAGRAPH = """Najnowsze rozszerzenie dokładnych konfiguracji Dustera zapisuje 205 datowanych obserwacji wyposażenia dla automatów Expression, Extreme i Journey bez kopiowania danych z wersji manualnych. Cztery pozycje są jawnym `not_available`, a pozostałe 201 stanowią wyposażenie obecne w konkretnych kartach. Pakiety PARKING i ZIMOWY PLUS dla Extreme i Journey mają osobne rekordy dostępności/ceny z oficjalnego cennika oraz późniejsze rekordy potwierdzające wybór w konkretnych egzemplarzach. Antena i składane lusterka Expression pozostają nierozstrzygnięte. Szczegóły zawiera `project/packages/duster-exact-stock-equipment-expansion-20260725.md`."""


def update_existing_docs() -> None:
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    anchor = "Najnowszy import Dustera dodaje trzy dokładne konfiguracje Eco-G 120 z automatyczną skrzynią: Expression, Extreme i Journey."
    pos = text.find(anchor)
    if pos < 0:
        raise RuntimeError("README Duster stock anchor missing")
    paragraph_end = text.find("\n\n", pos)
    if README_PARAGRAPH not in text:
        text = text[:paragraph_end + 2] + README_PARAGRAPH + "\n\n" + text[paragraph_end + 2:]
    write(readme, text)

    changelog = ROOT / "CHANGELOG.md"
    text = changelog.read_text(encoding="utf-8")
    bullet = "* Expanded the three exact Duster Eco-G 120 automatic stock configurations with 205 dated equipment observations, four source-priced package mappings and four separately dated selected-package states while preserving antenna and Expression mirror unknowns."
    anchor = "* Added three exact 2026 Duster Eco-G 120 automatic configurations"
    pos = text.find(anchor)
    if pos < 0:
        raise RuntimeError("CHANGELOG Duster anchor missing")
    line_end = text.find("\n", pos)
    if bullet not in text:
        text = text[:line_end + 1] + bullet + "\n" + text[line_end + 1:]
    write(changelog, text)

    roadmap = ROOT / "project" / "ROADMAP.md"
    text = roadmap.read_text(encoding="utf-8")
    bullet = "- dokładne wyposażenie trzech automatów Duster Eco-G 120 z 205 obserwacjami, czterema źródłowo wycenionymi pakietami i odrębnymi stanami pakietów wybranych w konkretnych egzemplarzach,"
    anchor = "- trzy dokładne konfiguracje Duster Eco-G 120 automatic"
    pos = text.find(anchor)
    if pos < 0:
        raise RuntimeError("ROADMAP Duster anchor missing")
    line_end = text.find("\n", pos)
    if bullet not in text:
        text = text[:line_end + 1] + bullet + "\n" + text[line_end + 1:]
    write(roadmap, text)


def update_commercial_test() -> None:
    path = ROOT / "tests" / "test_commercial_items_20260703.py"
    text = path.read_text(encoding="utf-8")
    if 'STOCK_DATE = "2026-07-25"' not in text:
        text = text.replace('DATE = "2026-07-03"\n', 'DATE = "2026-07-03"\nSTOCK_DATE = "2026-07-25"\n')
    text = text.replace("self.assertEqual(len(self.mappings), 134)", "self.assertEqual(len(self.mappings), 142)")
    text = text.replace('self.assertEqual({row["price_date"] for row in self.mappings}, {DATE})', 'self.assertEqual({row["price_date"] for row in self.mappings}, {DATE, STOCK_DATE})')
    text = text.replace('self.assertEqual({row["availability_status"] for row in self.mappings}, {"optional"})', 'self.assertEqual({row["availability_status"] for row in self.mappings}, {"optional", "standard"})')
    write(path, text)


def update_state() -> None:
    baseline_path = ROOT / ".tmp-duster-baseline.json"
    run("tools/dkb.py", "documentation-baseline", "--json", str(baseline_path))
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    baseline_path.unlink()
    path = ROOT / "project" / "state.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    state["updated_on"] = DATE
    state["phase"] = "Duster Exact Stock Equipment Expansion"
    state["current_package"] = {
        "name": "Duster Exact Stock Equipment Expansion",
        "status": "complete",
        "goal": "Expand the exact 2026 Duster Eco-G 120 automatic Expression, Extreme and Journey configurations with source-backed basic/configured equipment and separately preserved optional-price and selected-package evidence.",
    }
    state["next_package"] = {
        "name": "Duster Eco-G 120 Automatic Homologation Evidence Review",
        "status": "planned",
        "goal": "Locate and classify automatic-specific towing, cargo, WLTP, performance and mass evidence without inheriting manual homologation values or weakening current unknown states.",
    }
    state["baseline"] = {
        "tests": baseline["tests"],
        "csv_files": baseline["master"]["csv_files"],
        "rows": baseline["master"]["rows"],
        "configuration_values": baseline["configuration"]["values"],
        "configuration_import_specs": baseline["configuration"]["import_specs"],
        "configuration_value_ranges": baseline["configuration"]["value_ranges"],
        "configuration_range_import_specs": baseline["configuration"]["range_import_specs"],
        "availability_records": baseline["configuration"]["availability"]["total"],
        "attributes": baseline["catalogue"]["attributes"],
        "attribute_categories": baseline["catalogue"]["attribute_categories"],
    }
    write(path, json.dumps(state, ensure_ascii=False, indent=2) + "\n")
    run("tools/dkb.py", "project-state", "--apply")
    run("tools/dkb.py", "documentation-baseline", "--apply")


def main() -> None:
    payload = snapshot_payload()
    snapshot_text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    write(SNAPSHOT, snapshot_text)
    sha = hashlib.sha256(snapshot_text.encode("utf-8")).hexdigest()
    write(IMPORTER, IMPORTER_TEMPLATE.replace("__SHA__", sha))
    write(TEST, TEST_TEXT)
    write(ROOT / "project" / "packages" / "duster-exact-stock-equipment-expansion-20260725.md", PACKAGE_DOC)
    write(ROOT / "project" / "reviews" / "duster-exact-stock-equipment-review-2026-07-25.md", REVIEW_DOC)
    update_existing_docs()
    update_commercial_test()
    run("tools/import_duster_exact_stock_equipment_20260725.py", "--apply")
    update_state()
    run("tools/import_duster_exact_stock_equipment_20260725.py", "--check")
    run("tools/dkb.py", "project-state", "--check")
    run("tools/dkb.py", "documentation-baseline", "--check")
    print("PASS: materialized Duster exact stock equipment expansion")


if __name__ == "__main__":
    main()
