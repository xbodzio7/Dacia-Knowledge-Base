#!/usr/bin/env python3
"""Build or verify the authored Duster mini-brochure page-23 equipment ambiguity review."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

REVIEW_VERSION = 1
REVIEW_KIND = "duster_mini_equipment_page23_ambiguity_review"
REVIEWED_ON = "2026-07-28"
DEFAULT_PRIORITIZATION = Path("data/reporting/verified_pdf_candidate_residual_gap_prioritization.json")
DEFAULT_JSON = Path("data/reporting/duster_mini_equipment_page23_ambiguity_review.json")
DEFAULT_MARKDOWN = Path("data/reporting/duster_mini_equipment_page23_ambiguity_review.md")
PACKAGE_ID = "residual_gap_007"
SOURCE_CODE = "src_pl_duster_mini_brochure_20251020"
SOURCE_PAGE = 23
SOURCE_PATH = Path("PDF/Broszury/DACIA DUSTER mini broszura 20251020.pdf")
SOURCE_SHA256 = "84040b64bd67391cce4a99ada3021b0ad1a493f9430a666783e4632dd6ce85e8"
NEXT_PACKAGE = "Duster Mini Equipment Page 22 Ambiguity Review"
DECISION_STATUSES = {"covered", "partially_covered"}
TRIMS = ("essential", "expression", "journey", "extreme")

class DusterMiniEquipmentPage23ReviewError(RuntimeError):
    pass

def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]

def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise DusterMiniEquipmentPage23ReviewError(message)

def canonical_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"

def write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    temporary.replace(path)

def load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise DusterMiniEquipmentPage23ReviewError(f"cannot read {label}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise DusterMiniEquipmentPage23ReviewError(f"invalid JSON in {label}: {exc}") from exc
    ensure(isinstance(value, dict), f"{label} must be a JSON object")
    return value

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise DusterMiniEquipmentPage23ReviewError(f"cannot read archived source: {exc}") from exc
    return digest.hexdigest()

def availability_signature(attribute_code: str, availability_status: str) -> dict[str, str]:
    return {"attribute_code": attribute_code, "availability_status": availability_status}

DECISIONS = ({'candidate_id': 'e7d77061bf613db664b2fac2c5948d11965c94de2f6d042724801933fd1b4c2a',
  'line_start': 5,
  'line_end': 5,
  'exact_text': 'Światła przeciwmgłowe                                      -                   -                  '
                '•                   •',
  'decision': 'covered',
  'selected': [{'attribute_code': 'fog_lights', 'availability_status': 'not_available'},
               {'attribute_code': 'fog_lights', 'availability_status': 'standard'}],
  'row_context': 'complete fog-lights row',
  'source_availability': {'essential': 'not_available',
                          'expression': 'not_available',
                          'journey': 'standard',
                          'extreme': 'standard'},
  'rationale': 'This candidate is the complete fog-lights row. The selected signatures are limited to fog_lights:not_available, '
               'fog_lights:standard and preserve the printed trim-state boundary. No signature for a different attribute or '
               'availability state is substituted.'},
 {'candidate_id': '67bfa6143925d078ab4d6b98e4a909c748fe7efdb6042ceeacafcf92dc7fd942',
  'line_start': 15,
  'line_end': 15,
  'exact_text': 'Klimatyzacja manualna                                      •                   •                  '
                '-                   -',
  'decision': 'covered',
  'selected': [{'attribute_code': 'manual_air_conditioning', 'availability_status': 'not_available'},
               {'attribute_code': 'manual_air_conditioning', 'availability_status': 'standard'}],
  'row_context': 'complete manual-air-conditioning row',
  'source_availability': {'essential': 'standard',
                          'expression': 'standard',
                          'journey': 'not_available',
                          'extreme': 'not_available'},
  'rationale': 'This candidate is the complete manual-air-conditioning row. The selected signatures are limited to '
               'manual_air_conditioning:not_available, manual_air_conditioning:standard and preserve the printed trim-state '
               'boundary. No signature for a different attribute or availability state is substituted.'},
 {'candidate_id': '914b8682491d97e10cb74de3869f161013139e0194852eefccfd22170de44d4b',
  'line_start': 17,
  'line_end': 17,
  'exact_text': 'Klimatyzacja automatyczna                                  -                   -                  '
                '•                   •',
  'decision': 'covered',
  'selected': [{'attribute_code': 'automatic_climate_control', 'availability_status': 'not_available'},
               {'attribute_code': 'automatic_climate_control', 'availability_status': 'standard'}],
  'row_context': 'complete automatic-climate-control row',
  'source_availability': {'essential': 'not_available',
                          'expression': 'not_available',
                          'journey': 'standard',
                          'extreme': 'standard'},
  'rationale': 'This candidate is the complete automatic-climate-control row. The selected signatures are limited to '
               'automatic_climate_control:not_available, automatic_climate_control:standard and preserve the printed trim-state '
               'boundary. No signature for a different attribute or availability state is substituted.'},
 {'candidate_id': '8455b0e3b71fd819c06db3d30c2411f082e500e10d56ab4e173079b08e03bbb4',
  'line_start': 25,
  'line_end': 25,
  'exact_text': 'Keyless Entry - system',
  'decision': 'partially_covered',
  'selected': [{'attribute_code': 'keyless_entry', 'availability_status': 'not_available'},
               {'attribute_code': 'keyless_entry', 'availability_status': 'standard'}],
  'row_context': 'first line of the Keyless Entry row',
  'source_availability': {'essential': 'not_available',
                          'expression': 'not_available',
                          'journey': 'standard',
                          'extreme': 'standard'},
  'rationale': 'This candidate is the first line of the Keyless Entry row. The selected signatures are limited to '
               'keyless_entry:not_available, keyless_entry:standard and preserve the printed trim-state boundary. No signature '
               'for a different attribute or availability state is substituted.'},
 {'candidate_id': '3d09f4062abab6c0cfc00f6e4ff77b42d3b70a4aec702cd357128705538246e5',
  'line_start': 26,
  'line_end': 26,
  'exact_text': 'bezkluczykowego dostępu                                    -                   -                  '
                '•                   •',
  'decision': 'partially_covered',
  'selected': [{'attribute_code': 'keyless_entry', 'availability_status': 'not_available'},
               {'attribute_code': 'keyless_entry', 'availability_status': 'standard'}],
  'row_context': 'availability-bearing middle line of the Keyless Entry row',
  'source_availability': {'essential': 'not_available',
                          'expression': 'not_available',
                          'journey': 'standard',
                          'extreme': 'standard'},
  'rationale': 'This candidate is the availability-bearing middle line of the Keyless Entry row. The selected signatures are '
               'limited to keyless_entry:not_available, keyless_entry:standard and preserve the printed trim-state boundary. No '
               'signature for a different attribute or availability state is substituted.'},
 {'candidate_id': 'e0a3dae3be152c1898a485b2d685aae35a35863cb0b2e1add5bb5fb036504a08',
  'line_start': 27,
  'line_end': 27,
  'exact_text': 'i uruchamiania silnika',
  'decision': 'partially_covered',
  'selected': [{'attribute_code': 'keyless_entry', 'availability_status': 'not_available'},
               {'attribute_code': 'keyless_entry', 'availability_status': 'standard'}],
  'row_context': 'final line of the Keyless Entry row',
  'source_availability': {'essential': 'not_available',
                          'expression': 'not_available',
                          'journey': 'standard',
                          'extreme': 'standard'},
  'rationale': 'This candidate is the final line of the Keyless Entry row. The selected signatures are limited to '
               'keyless_entry:not_available, keyless_entry:standard and preserve the printed trim-state boundary. No signature '
               'for a different attribute or availability state is substituted.'},
 {'candidate_id': '1e3cb273c9aea5a8b30be82184f7f0f06219ed2a4b6d599e350cffb4e84d39da',
  'line_start': 28,
  'line_end': 28,
  'exact_text': 'Szyby przednie regulowane elektrycznie                     •                   •                  '
                '•                   •',
  'decision': 'covered',
  'selected': [{'attribute_code': 'front_windows_power', 'availability_status': 'standard'}],
  'row_context': 'complete front power-window row',
  'source_availability': {'essential': 'standard', 'expression': 'standard', 'journey': 'standard', 'extreme': 'standard'},
  'rationale': 'This candidate is the complete front power-window row. The selected signatures are limited to '
               'front_windows_power:standard and preserve the printed trim-state boundary. The attached one-touch-window '
               'signature is a different feature and is rejected.'},
 {'candidate_id': '1dbb3d92a96f57ace3ffcf707250f8907622d553496ce01706d6bd607aeb42fb',
  'line_start': 30,
  'line_end': 30,
  'exact_text': 'Szyby tylne regulowane elektrycznie                        -                   •                  '
                '•                   •',
  'decision': 'covered',
  'selected': [{'attribute_code': 'rear_windows_power', 'availability_status': 'not_available'},
               {'attribute_code': 'rear_windows_power', 'availability_status': 'standard'}],
  'row_context': 'complete rear power-window row',
  'source_availability': {'essential': 'not_available', 'expression': 'standard', 'journey': 'standard', 'extreme': 'standard'},
  'rationale': 'This candidate is the complete rear power-window row. The selected signatures are limited to '
               'rear_windows_power:not_available, rear_windows_power:standard and preserve the printed trim-state boundary. The '
               'attached one-touch-window signature is a different feature and is rejected.'},
 {'candidate_id': '738ff58cdf0084291a7f7361a7909a42d073083f6c0a71a20fa27a143f6abaad',
  'line_start': 32,
  'line_end': 32,
  'exact_text': 'Kierownica z regulacją: wysokości /',
  'decision': 'partially_covered',
  'selected': [{'attribute_code': 'steering_wheel_height_adjustment', 'availability_status': 'standard'},
               {'attribute_code': 'steering_wheel_reach_adjustment', 'availability_status': 'standard'}],
  'row_context': 'first line of the height/reach steering-wheel adjustment row',
  'source_availability': {'essential': 'standard', 'expression': 'standard', 'journey': 'standard', 'extreme': 'standard'},
  'rationale': 'This candidate is the first line of the height/reach steering-wheel adjustment row. The selected signatures are '
               'limited to steering_wheel_height_adjustment:standard, steering_wheel_reach_adjustment:standard and preserve the '
               'printed trim-state boundary. No signature for a different attribute or availability state is substituted.'},
 {'candidate_id': 'f537be0e005d196dd821e69637a80e99ba8d78eb2e3d9b5029750bbefd33acf0',
  'line_start': 35,
  'line_end': 35,
  'exact_text': 'Fotel kierowcy z regulacją wysokości                       •                   •                  '
                '•                   •',
  'decision': 'covered',
  'selected': [{'attribute_code': 'driver_seat_height_adjustment', 'availability_status': 'standard'}],
  'row_context': 'complete driver-seat height row',
  'source_availability': {'essential': 'standard', 'expression': 'standard', 'journey': 'standard', 'extreme': 'standard'},
  'rationale': 'This candidate is the complete driver-seat height row. The selected signatures are limited to '
               'driver_seat_height_adjustment:standard and preserve the printed trim-state boundary. Lumbar and passenger-seat '
               'signatures belong to other rows and are rejected.'},
 {'candidate_id': '367e8c3a0d6f267fe39768d09a019cd8115b46bda563fb17fa21a7a7d665db27',
  'line_start': 42,
  'line_end': 42,
  'exact_text': 'Fotel pasażera z regulacją wysokości                       -',
  'decision': 'partially_covered',
  'selected': [{'attribute_code': 'passenger_seat_adjustment', 'availability_status': 'optional'},
               {'attribute_code': 'passenger_seat_height_adjustment', 'availability_status': 'standard'}],
  'row_context': 'passenger-seat height row split across option and standard markers',
  'source_availability': {'essential': 'not_available',
                          'expression': 'optional_package',
                          'journey': 'optional_package',
                          'extreme': 'standard'},
  'rationale': 'This candidate is the passenger-seat height row split across option and standard markers. The selected '
               'signatures are limited to passenger_seat_adjustment:optional, passenger_seat_height_adjustment:standard and '
               'preserve the printed trim-state boundary. The driver-lumbar signature belongs to the preceding row and is '
               'rejected.'},
 {'candidate_id': '77639618810b66ccd2c25ff8e667a62c04164c452fc6022bb77c021dacc1ca60',
  'line_start': 46,
  'line_end': 46,
  'exact_text': 'Konsola centralna z podłokietnikiem',
  'decision': 'partially_covered',
  'selected': [{'attribute_code': 'front_centre_armrest', 'availability_status': 'not_available'},
               {'attribute_code': 'front_centre_armrest', 'availability_status': 'standard'}],
  'row_context': 'first line of the centre-console armrest row',
  'source_availability': {'essential': 'not_available', 'expression': 'standard', 'journey': 'standard', 'extreme': 'standard'},
  'rationale': 'This candidate is the first line of the centre-console armrest row. The selected signatures are limited to '
               'front_centre_armrest:not_available, front_centre_armrest:standard and preserve the printed trim-state boundary. '
               'No signature for a different attribute or availability state is substituted.'},
 {'candidate_id': '3263a784dc65a5239a862c149f7924e52044eae648e2f8c84ba0b8a7f3d47367',
  'line_start': 62,
  'line_end': 62,
  'exact_text': 'Ładowarka indukcyjna                                       -                   -                  •',
  'decision': 'partially_covered',
  'selected': [{'attribute_code': 'wireless_charging', 'availability_status': 'not_available'},
               {'attribute_code': 'wireless_charging', 'availability_status': 'optional'},
               {'attribute_code': 'wireless_charging', 'availability_status': 'standard'}],
  'row_context': 'wireless-charging row with the Extreme package marker on the following line',
  'source_availability': {'essential': 'not_available',
                          'expression': 'not_available',
                          'journey': 'standard',
                          'extreme': 'optional_package'},
  'rationale': 'This candidate is the wireless-charging row with the Extreme package marker on the following line. The selected '
               'signatures are limited to wireless_charging:not_available, wireless_charging:optional, '
               'wireless_charging:standard and preserve the printed trim-state boundary. All three availability states are '
               'retained; the Extreme option marker is printed on the following line.'},
 {'candidate_id': '05639266337f85a97239e31563d67a576b753d9d1d0fce6fb9529e2563aa18e3',
  'line_start': 66,
  'line_end': 66,
  'exact_text': 'System multimedialny Media Control:',
  'decision': 'partially_covered',
  'selected': [{'attribute_code': 'media_control_system', 'availability_status': 'not_available'},
               {'attribute_code': 'media_control_system', 'availability_status': 'standard'}],
  'row_context': 'first line of the Media Control row',
  'source_availability': {'essential': 'standard',
                          'expression': 'not_available',
                          'journey': 'not_available',
                          'extreme': 'not_available'},
  'rationale': 'This candidate is the first line of the Media Control row. The selected signatures are limited to '
               'media_control_system:not_available, media_control_system:standard and preserve the printed trim-state boundary. '
               'No signature for a different attribute or availability state is substituted.'},
 {'candidate_id': '80fed6910e8c25629cfe124425a23d30797138b0c37e44e4cf5d601540ca7525',
  'line_start': 73,
  'line_end': 73,
  'exact_text': 'System Media Display: system',
  'decision': 'partially_covered',
  'selected': [{'attribute_code': 'media_display_system', 'availability_status': 'not_available'},
               {'attribute_code': 'media_display_system', 'availability_status': 'standard'}],
  'row_context': 'first line of the Media Display row',
  'source_availability': {'essential': 'not_available',
                          'expression': 'standard',
                          'journey': 'not_available',
                          'extreme': 'standard'},
  'rationale': 'This candidate is the first line of the Media Display row. The selected signatures are limited to '
               'media_display_system:not_available, media_display_system:standard and preserve the printed trim-state boundary. '
               'No signature for a different attribute or availability state is substituted.'},
 {'candidate_id': 'b6fd6517ac2abb8ee8522cf8792137206c79698c0628c2e62542d4598f5a8500',
  'line_start': 92,
  'line_end': 92,
  'exact_text': 'i pakiet usług zdalnych',
  'decision': 'partially_covered',
  'selected': [{'attribute_code': 'connected_services', 'availability_status': 'not_available'},
               {'attribute_code': 'connected_services', 'availability_status': 'standard'}],
  'row_context': 'final line of the Media Nav Live description',
  'source_availability': {'essential': 'not_available',
                          'expression': 'optional',
                          'journey': 'standard',
                          'extreme': 'optional_package'},
  'rationale': 'This candidate is the final line of the Media Nav Live description. The selected signatures are limited to '
               'connected_services:not_available, connected_services:standard and preserve the printed trim-state boundary. '
               'Optional Media Nav Live states are visible in the brochure but no optional connected-services signature is '
               'attached, so the fragment remains partial.'},
 {'candidate_id': 'bdc78d82c8d5108072cba2be1839185b56804cb85b1bcf3d7d69c3fb705a41bb',
  'line_start': 94,
  'line_end': 94,
  'exact_text': 'Pakiet usług zdalnych (za',
  'decision': 'partially_covered',
  'selected': [{'attribute_code': 'connected_services', 'availability_status': 'not_available'},
               {'attribute_code': 'connected_services', 'availability_status': 'standard'}],
  'row_context': 'first line of the separate remote-services row',
  'source_availability': {'essential': 'not_available', 'expression': 'standard', 'journey': 'standard', 'extreme': 'standard'},
  'rationale': 'This candidate is the first line of the separate remote-services row. The selected signatures are limited to '
               'connected_services:not_available, connected_services:standard and preserve the printed trim-state boundary. No '
               'signature for a different attribute or availability state is substituted.'},
 {'candidate_id': 'c695d1a46a9ec4ab42c9b6f9a9ce88ee896a96f0fd085f8f12aba502a2072648',
  'line_start': 95,
  'line_end': 95,
  'exact_text': 'pośrednictwem aplikacji MY Dacia)',
  'decision': 'partially_covered',
  'selected': [{'attribute_code': 'connected_services', 'availability_status': 'not_available'},
               {'attribute_code': 'connected_services', 'availability_status': 'standard'}],
  'row_context': 'second line of the separate remote-services row',
  'source_availability': {'essential': 'not_available', 'expression': 'standard', 'journey': 'standard', 'extreme': 'standard'},
  'rationale': 'This candidate is the second line of the separate remote-services row. The selected signatures are limited to '
               'connected_services:not_available, connected_services:standard and preserve the printed trim-state boundary. No '
               'signature for a different attribute or availability state is substituted.'},
 {'candidate_id': '62ec88f4925dacadd5c0a7a925b0094be661a8f392df50ef403e4f4b05b560f9',
  'line_start': 107,
  'line_end': 107,
  'exact_text': 'Pakiet PARKING: czujniki parkowania',
  'decision': 'partially_covered',
  'selected': [{'attribute_code': 'front_parking_sensors', 'availability_status': 'optional'}],
  'row_context': 'first line of the Parking package row',
  'source_availability': {'essential': 'not_available',
                          'expression': 'not_available',
                          'journey': 'optional_package',
                          'extreme': 'optional_package'},
  'rationale': 'This candidate is the first line of the Parking package row. The selected signatures are limited to '
               'front_parking_sensors:optional and preserve the printed trim-state boundary. Only optional front-sensor evidence '
               'matches the package marker; standard evidence is not substituted for the optional package row.'},
 {'candidate_id': '919be17ffe35a31d89cb1baaee4d785b2907ff6888a7ae1aa13eb345f5e43a2b',
  'line_start': 112,
  'line_end': 112,
  'exact_text': 'Pakiet ZIMOWY: przednie fotele',
  'decision': 'partially_covered',
  'selected': [{'attribute_code': 'heated_front_seats', 'availability_status': 'optional'}],
  'row_context': 'first line of the Extreme Winter package row',
  'source_availability': {'essential': 'not_available',
                          'expression': 'not_available',
                          'journey': 'not_available',
                          'extreme': 'optional_package'},
  'rationale': 'This candidate is the first line of the Extreme Winter package row. The selected signatures are limited to '
               'heated_front_seats:optional and preserve the printed trim-state boundary. Only optional heated-seat evidence '
               'matches this package row; standard evidence is rejected.'},
 {'candidate_id': 'c67dfca1a468cd90ffa06827413282fab38239d3383113e552ada097c0efb734',
  'line_start': 115,
  'line_end': 115,
  'exact_text': 'Pakiet ZIMOWY PLUS: podgrzewana',
  'decision': 'partially_covered',
  'selected': [{'attribute_code': 'heated_windscreen', 'availability_status': 'optional'}],
  'row_context': 'first line of the Extreme Winter Plus package row',
  'source_availability': {'essential': 'not_available',
                          'expression': 'not_available',
                          'journey': 'not_available',
                          'extreme': 'optional_package'},
  'rationale': 'This candidate is the first line of the Extreme Winter Plus package row. The selected signatures are limited to '
               'heated_windscreen:optional and preserve the printed trim-state boundary. Only optional heated-windscreen '
               'evidence matches this package row; heated-steering-wheel and standard-windscreen evidence are rejected.'},
 {'candidate_id': '9f45140013402ce3253e430ea41b9b164e66a905ff7135db1590a11edb2f869d',
  'line_start': 118,
  'line_end': 118,
  'exact_text': 'Pakiet ZIMOWY: przednie fotele',
  'decision': 'partially_covered',
  'selected': [{'attribute_code': 'heated_front_seats', 'availability_status': 'optional'}],
  'row_context': 'first line of the Expression/Journey Winter package row',
  'source_availability': {'essential': 'not_available',
                          'expression': 'optional_package',
                          'journey': 'optional_package',
                          'extreme': 'not_available'},
  'rationale': 'This candidate is the first line of the Expression/Journey Winter package row. The selected signatures are '
               'limited to heated_front_seats:optional and preserve the printed trim-state boundary. Only optional heated-seat '
               'evidence matches this package row; standard evidence is rejected.'},
 {'candidate_id': '3bab9be222e4b913a6f0eafaa24622d42a4d885641310ccc3024addfb8473f4f',
  'line_start': 122,
  'line_end': 122,
  'exact_text': 'fotel pasażera z regulacją wysokosci',
  'decision': 'partially_covered',
  'selected': [{'attribute_code': 'passenger_seat_adjustment', 'availability_status': 'optional'}],
  'row_context': 'passenger-seat tail of the Expression/Journey Winter package row',
  'source_availability': {'essential': 'not_available',
                          'expression': 'optional_package',
                          'journey': 'optional_package',
                          'extreme': 'not_available'},
  'rationale': 'This candidate is the passenger-seat tail of the Expression/Journey Winter package row. The selected signatures '
               'are limited to passenger_seat_adjustment:optional and preserve the printed trim-state boundary. Only optional '
               'passenger-seat adjustment evidence matches the package row; driver lumbar and standard passenger-height evidence '
               'are rejected.'},
 {'candidate_id': '0ce47af75f3921094b15d89c07fb35e222ffc406fb52eae78431baba77a19b2b',
  'line_start': 123,
  'line_end': 123,
  'exact_text': 'Pakiet ZIMOWY PLUS: podgrzewana',
  'decision': 'partially_covered',
  'selected': [{'attribute_code': 'heated_windscreen', 'availability_status': 'optional'}],
  'row_context': 'first line of the Journey Winter Plus package row',
  'source_availability': {'essential': 'not_available',
                          'expression': 'not_available',
                          'journey': 'optional_package',
                          'extreme': 'not_available'},
  'rationale': 'This candidate is the first line of the Journey Winter Plus package row. The selected signatures are limited to '
               'heated_windscreen:optional and preserve the printed trim-state boundary. Only optional heated-windscreen '
               'evidence matches this package row; heated-steering-wheel and standard-windscreen evidence are rejected.'},
 {'candidate_id': '37fdef3bf18768861841e0b7473313fa3a0ffb394c810f7ce9816ce503cdb4a3',
  'line_start': 127,
  'line_end': 127,
  'exact_text': 'fotel pasażera z regulacją wysokosci',
  'decision': 'partially_covered',
  'selected': [{'attribute_code': 'passenger_seat_adjustment', 'availability_status': 'optional'}],
  'row_context': 'passenger-seat tail of the Journey Winter Plus package row',
  'source_availability': {'essential': 'not_available',
                          'expression': 'not_available',
                          'journey': 'optional_package',
                          'extreme': 'not_available'},
  'rationale': 'This candidate is the passenger-seat tail of the Journey Winter Plus package row. The selected signatures are '
               'limited to passenger_seat_adjustment:optional and preserve the printed trim-state boundary. Only optional '
               'passenger-seat adjustment evidence matches the package row; driver lumbar and standard passenger-height evidence '
               'are rejected.'},
 {'candidate_id': '6f657acc5e7861d31dd69553fbd01682f82350547a9efde67677eaba1b1d4535',
  'line_start': 142,
  'line_end': 142,
  'exact_text': 'regulator prędkości',
  'decision': 'partially_covered',
  'selected': [{'attribute_code': 'adaptive_cruise_control', 'availability_status': 'optional'}],
  'row_context': 'final line of the Hybrid-G 150 4x4 Techno package row',
  'source_availability': {'essential': 'not_available',
                          'expression': 'not_available',
                          'journey': 'not_available',
                          'extreme': 'optional_package'},
  'rationale': 'This candidate is the final line of the Hybrid-G 150 4x4 Techno package row. The selected signatures are limited '
               'to adaptive_cruise_control:optional and preserve the printed trim-state boundary. The page context says adaptive '
               'cruise control. Ordinary cruise-control and speed-limiter signatures are rejected.'})

def signature_key(value: Mapping[str, Any]) -> str:
    return json.dumps(dict(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def read_source_row(repository: Path) -> dict[str, str]:
    path = repository / "data/master/sources.csv"
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            ensure(reader.fieldnames is not None, "sources.csv has no header")
            matches = [dict(row) for row in reader if row.get("code") == SOURCE_CODE]
    except OSError as exc:
        raise DusterMiniEquipmentPage23ReviewError(f"cannot read sources.csv: {exc}") from exc
    ensure(len(matches) == 1, "Duster mini-brochure source registry row differs")
    return matches[0]

def validate_prioritization(payload: Mapping[str, Any]) -> dict[str, Any]:
    ensure(payload.get("version") == 1, "prioritization version differs")
    ensure(payload.get("kind") == "verified_pdf_candidate_residual_gap_prioritization", "prioritization kind differs")
    ensure(payload.get("status") == "complete", "prioritization is not complete")
    policy = payload.get("policy")
    ensure(isinstance(policy, Mapping), "prioritization policy is missing")
    ensure(policy.get("master_data_changes") is False, "prioritization changes master data")
    ensure(policy.get("approved_import_spec_generation") is False, "prioritization creates approved imports")
    packages = payload.get("packages")
    ensure(isinstance(packages, list), "prioritization packages are missing")
    matches = [item for item in packages if isinstance(item, Mapping) and item.get("package_id") == PACKAGE_ID]
    ensure(len(matches) == 1, "residual_gap_007 package differs")
    package = dict(matches[0])
    ensure(package.get("source_code") == SOURCE_CODE, "package source differs")
    ensure(package.get("model_code") == "duster_iii", "package model differs")
    ensure(package.get("domain") == "equipment_matrix", "package domain differs")
    ensure(package.get("page") == SOURCE_PAGE, "package page differs")
    ensure(package.get("coverage_status") == "ambiguous", "package status differs")
    ensure(package.get("candidate_count") == 26, "package candidate count differs")
    ensure(package.get("evidence_signature_count") == 61, "package evidence signature count differs")
    ensure(package.get("evidence_record_count") == 623, "package evidence record count differs")
    candidates = package.get("candidates")
    ensure(isinstance(candidates, list) and len(candidates) == 26, "package candidates differ")
    return package

def verify_source(repository: Path) -> dict[str, Any]:
    row = read_source_row(repository)
    ensure(row.get("status") == "active", "Duster mini-brochure source is not active")
    ensure(row.get("source_type") == "brochure_pdf", "Duster source type differs")
    ensure(row.get("document_date") == "2025-10-20", "Duster source date differs")
    ensure(row.get("file_path") == SOURCE_PATH.as_posix(), "Duster source path differs")
    ensure(row.get("sha256") == SOURCE_SHA256, "Duster source registry hash differs")
    archived = repository / SOURCE_PATH
    ensure(archived.is_file(), "archived Duster mini-brochure is missing")
    ensure(sha256(archived) == SOURCE_SHA256, "archived Duster mini-brochure hash differs")
    return {"source_code": SOURCE_CODE, "file_path": SOURCE_PATH.as_posix(), "sha256": SOURCE_SHA256, "page": SOURCE_PAGE,
            "review_basis": "authored visual review of the archived page-23 equipment matrix"}

def selected_signatures(candidate: Mapping[str, Any], expected: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    available = candidate.get("evidence_signatures")
    ensure(isinstance(available, list), "candidate evidence signatures are missing")
    by_key: dict[str, dict[str, Any]] = {}
    for item in available:
        ensure(isinstance(item, Mapping), "candidate evidence signature differs")
        payload = item.get("signature")
        ensure(isinstance(payload, Mapping), "candidate signature payload is missing")
        key = signature_key(payload)
        ensure(key not in by_key, "candidate evidence signature is duplicated")
        by_key[key] = json.loads(json.dumps(dict(item), ensure_ascii=False))
    result = []
    for wanted in expected:
        key = signature_key(wanted)
        ensure(key in by_key, f"selected signature is not attached to candidate: {key}")
        result.append(by_key[key])
    return result

def build_review(prioritization: Mapping[str, Any], repository: Path) -> dict[str, Any]:
    package = validate_prioritization(prioritization)
    source_receipt = verify_source(repository)
    candidates = package["candidates"]
    ensure(len(DECISIONS) == len(candidates), "authored decision count differs")
    by_id = {str(item["candidate_id"]): item for item in candidates}
    ensure(len(by_id) == len(candidates), "candidate IDs are not unique")
    decisions = []
    for authored in DECISIONS:
        candidate = by_id.get(str(authored["candidate_id"]))
        ensure(candidate is not None, "authored decision candidate is missing")
        ensure(candidate.get("line_start") == authored["line_start"] and candidate.get("line_end") == authored["line_end"], "candidate line differs")
        ensure(candidate.get("exact_text") == authored["exact_text"], "candidate exact text differs")
        ensure(candidate.get("source_code") == SOURCE_CODE and candidate.get("page") == SOURCE_PAGE, "candidate source boundary differs")
        ensure(candidate.get("coverage_status") == "ambiguous", "candidate input status differs")
        decision = str(authored["decision"])
        ensure(decision in DECISION_STATUSES, f"unknown authored decision: {decision}")
        selected = selected_signatures(candidate, authored["selected"])
        selected_records = 0
        for item in selected:
            records = item.get("records")
            ensure(isinstance(records, list) and item.get("record_count") == len(records), "selected evidence record count differs")
            for record in records:
                ensure(record.get("table") == "configuration_attribute_availability", "selected evidence table differs")
                ensure(str(record.get("configuration_code", "")).startswith("duster_iii_"), "selected evidence model boundary differs")
            selected_records += len(records)
        visual = authored["source_availability"]
        ensure(tuple(visual) == TRIMS, "source availability trim keys differ")
        decisions.append({
            "candidate_id": authored["candidate_id"], "source_code": SOURCE_CODE, "page": SOURCE_PAGE,
            "line_start": authored["line_start"], "line_end": authored["line_end"], "exact_text": authored["exact_text"],
            "input_coverage_status": "ambiguous", "authored_decision": decision, "row_context": authored["row_context"],
            "source_availability": visual, "rationale": authored["rationale"],
            "selected_evidence_signature_count": len(selected), "selected_evidence_record_count": selected_records,
            "selected_evidence_signatures": selected,
            "rejected_attached_signature_count": len(candidate["evidence_signatures"]) - len(selected),
        })
    decision_ids = [item["candidate_id"] for item in decisions]
    ensure(len(decision_ids) == len(set(decision_ids)) == 26, "authored candidate assignment differs")
    counts = Counter(item["authored_decision"] for item in decisions)
    ensure(counts == Counter({"partially_covered": 20, "covered": 6}), "authored decision distribution differs")
    selected_signature_count = sum(item["selected_evidence_signature_count"] for item in decisions)
    selected_record_count = sum(item["selected_evidence_record_count"] for item in decisions)
    ensure((selected_signature_count, selected_record_count) == (43, 518), "selected evidence totals differ")
    return {
        "version": REVIEW_VERSION, "kind": REVIEW_KIND, "reviewed_on": REVIEWED_ON, "status": "complete",
        "source_prioritization": DEFAULT_PRIORITIZATION.as_posix(), "package_id": PACKAGE_ID, "source_receipt": source_receipt,
        "scope": {"candidate_count": 26, "source_code": SOURCE_CODE, "model_code": "duster_iii", "domain": "equipment_matrix", "page": SOURCE_PAGE, "input_coverage_status": "ambiguous"},
        "policy": {"candidate_id_and_exact_text_cited": True, "selected_evidence_copied_without_reinterpretation": True,
                   "source_page_layout_used_for_row_disambiguation": True, "multi_line_rows_preserved": True,
                   "package_markers_not_rewritten_as_standard": True, "cross_attribute_evidence_not_silently_substituted": True,
                   "configuration_states_not_projected_between_trims": True, "master_data_changes": False,
                   "approved_import_spec_generation": False, "automatic_promotion": False},
        "summary": {"candidate_count": 26, "decision_counts": {"covered": 6, "partially_covered": 20},
                    "selected_evidence_signature_count": selected_signature_count, "selected_evidence_record_count": selected_record_count,
                    "rejected_attached_signature_count": 61-selected_signature_count, "rejected_attached_record_count": 623-selected_record_count,
                    "candidates_with_selected_evidence": 26, "candidates_without_selected_evidence": 0},
        "decisions": decisions,
        "semantic_boundaries": {"review_is_not_import_approval": True, "bullet_option_and_dash_symbols_remain_distinct": True,
                                 "row_fragments_are_not_promoted_to_new_attributes": True, "one_touch_windows_are_distinct_from_power_windows": True,
                                 "seat_lumbar_and_height_attributes_remain_distinct": True, "package_components_do_not_inherit_standard_status": True,
                                 "ordinary_and_adaptive_cruise_control_remain_distinct": True, "no_configuration_projection_is_created": True},
        "next_package": {"name": NEXT_PACKAGE, "status": "planned",
                         "goal": "Review the 11 ambiguous equipment candidates from Duster mini-brochure page 22 against their 27 preserved evidence signatures without creating master-data rows or approved import specifications."},
    }

def render_markdown(payload: Mapping[str, Any]) -> str:
    summary = payload["summary"]
    lines = ["# Duster Mini Equipment Page 23 Ambiguity Review", "",
             "Authored review of `residual_gap_007`. Symbols and multi-line row boundaries are preserved; the review does not approve imports.", "",
             "## Summary", "", "| Measure | Value |", "| --- | ---: |",
             f"| Reviewed candidates | {summary['candidate_count']} |", f"| Covered | {summary['decision_counts']['covered']} |",
             f"| Partially covered | {summary['decision_counts']['partially_covered']} |",
             f"| Selected evidence signatures | {summary['selected_evidence_signature_count']} |",
             f"| Selected evidence records | {summary['selected_evidence_record_count']} |",
             f"| Rejected attached signatures | {summary['rejected_attached_signature_count']} |",
             "", "## Candidate decisions", "", "| Line | Candidate | Decision | Signatures | Records | Row context |", "| ---: | --- | --- | ---: | ---: | --- |"]
    for item in payload["decisions"]:
        context = str(item["row_context"]).replace("|", "\\|")
        lines.append(f"| {item['line_start']} | `{item['candidate_id']}` | `{item['authored_decision']}` | {item['selected_evidence_signature_count']} | {item['selected_evidence_record_count']} | {context} |")
    lines.extend(["", "## Safety boundary", "", "- no file under `data/master` is changed;", "- no approved import specification is created or changed;",
                  "- `•`, `¤` and `-` remain standard, optional and unavailable respectively;", "- multi-line labels are reviewed as one visual row without inventing new attributes;",
                  "- package components do not inherit standard status from records outside the printed package row;", "- evidence for adjacent attributes is rejected rather than substituted;",
                  "", "## Next package", "", f"**{payload['next_package']['name']}** — {payload['next_package']['goal']}", ""])
    return "\n".join(lines)

def ensure_safe_output(repository: Path, path: Path) -> Path:
    resolved = (path if path.is_absolute() else repository / path).resolve()
    for restricted in (repository / "data/master", repository / "data/imports"):
        try:
            resolved.relative_to(restricted.resolve())
        except ValueError:
            continue
        raise DusterMiniEquipmentPage23ReviewError(f"output path is restricted: {path}")
    return resolved

def verify_output(path: Path, expected: str, label: str) -> None:
    try:
        actual = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise DusterMiniEquipmentPage23ReviewError(f"cannot read {label}: {exc}") from exc
    ensure(actual == expected, f"{label} differs from deterministic output")

def build_from_path(repository: Path, prioritization_path: Path) -> tuple[dict[str, Any], str]:
    resolved = prioritization_path if prioritization_path.is_absolute() else repository / prioritization_path
    payload = build_review(load_json_object(resolved, "residual-gap prioritization"), repository)
    return payload, render_markdown(payload)

def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--prioritization", type=Path, default=DEFAULT_PRIORITIZATION)
    result.add_argument("--json", type=Path, default=DEFAULT_JSON)
    result.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    result.add_argument("--verify", action="store_true")
    return result

def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    repository = repository_root()
    try:
        payload, markdown = build_from_path(repository, args.prioritization)
        json_path = ensure_safe_output(repository, args.json)
        markdown_path = ensure_safe_output(repository, args.markdown)
        expected_json = canonical_json(payload)
        if args.verify:
            verify_output(json_path, expected_json, "JSON report")
            verify_output(markdown_path, markdown, "Markdown report")
            print("Duster mini equipment page-23 ambiguity review: PASS")
        else:
            write_atomic(json_path, expected_json)
            write_atomic(markdown_path, markdown)
            print(f"JSON report written to {json_path}")
            print(f"Markdown report written to {markdown_path}")
        print("Candidates reviewed: 26")
        print("Selected evidence signatures: 43")
        print("Selected evidence records: 518")
        return 0
    except DusterMiniEquipmentPage23ReviewError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
