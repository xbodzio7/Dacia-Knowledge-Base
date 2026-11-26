# Configuration Data Completeness

As of: `2026-10-01`

## Scope

| Metric | Value |
| --- | ---: |
| Configuration scope | `explicit_subset` |
| Reporting configurations | 7 |
| Repository configurations with selected status | 94 |
| Excluded configurations | 87 |
| Sources | 7 |
| Technical slots | 85 |
| Equipment attributes | 69 |

## Summary

| Domain | Applicable | Complete | Missing | Not applicable | Coverage |
| --- | ---: | ---: | ---: | ---: | ---: |
| Technical values | 595 | 537 | 58 | 0 | 90.25% |
| Equipment availability | 483 | 481 | 2 | 0 | 99.59% |

Equipment states: `standard=402`, `optional=7`, `not_available=72`, `unknown=0`.

## By configuration

| Configuration | Source | Technical | Equipment |
| --- | --- | ---: | ---: |
| `sandero_iii_expression_ecog120_manual` | `src_pl_sandero_expression_ecog120_mt_20260626` | 92.94% | 100.00% |
| `sandero_iii_journey_ecog120_manual` | `src_pl_sandero_journey_ecog120_mt_20260626` | 90.59% | 100.00% |
| `sandero_stepway_iii_essential_ecog120_manual` | `src_pl_sandero_stepway_essential_ecog120_mt_20260626` | 95.29% | 100.00% |
| `sandero_stepway_iii_expression_ecog120_automatic` | `src_pl_sandero_stepway_expression_ecog120_at_20260626` | 89.41% | 98.55% |
| `sandero_stepway_iii_expression_ecog120_manual` | `src_pl_sandero_stepway_expression_ecog120_mt_20260626` | 89.41% | 100.00% |
| `sandero_stepway_iii_extreme_ecog120_automatic` | `src_pl_sandero_stepway_extreme_ecog120_at_20260626` | 87.06% | 98.55% |
| `sandero_stepway_iii_extreme_ecog120_manual` | `src_pl_sandero_stepway_extreme_ecog120_mt_20260626` | 87.06% | 100.00% |

## By category

| Category | Technical | Equipment |
| --- | ---: | ---: |
| ADAS | 100.00% | 100.00% |
| Acoustics | 100.00% | 100.00% |
| Brakes | 100.00% | 100.00% |
| Capacities | 100.00% | 100.00% |
| Consumption | 100.00% | 100.00% |
| Dimensions | 89.29% | 100.00% |
| Doors | 78.57% | 100.00% |
| Drivetrain | 100.00% | 100.00% |
| Driving Systems | 100.00% | 96.43% |
| Emissions | 100.00% | 100.00% |
| Engine | 89.01% | 100.00% |
| Exterior | 100.00% | 100.00% |
| HVAC | 100.00% | 100.00% |
| Infotainment | 57.14% | 100.00% |
| Lighting | 100.00% | 100.00% |
| Mirrors | 14.29% | 100.00% |
| Performance | 95.71% | 100.00% |
| Powertrain | 100.00% | 100.00% |
| Safety | 100.00% | 100.00% |
| Seats | 71.43% | 100.00% |
| Steering | 14.29% | 100.00% |
| Suspension | 100.00% | 100.00% |
| Towing | 100.00% | 100.00% |
| Transmission | 100.00% | 100.00% |
| Weights | 100.00% | 100.00% |
| Wheels | 100.00% | 100.00% |
| Windows | 14.29% | 100.00% |

## Technical gaps

| Configuration | Source | Category | Attribute | Fuel context |
| --- | --- | --- | --- | --- |
| `sandero_iii_expression_ecog120_manual` | `src_pl_sandero_expression_ecog120_mt_20260626` | Seats | `centre_console_variant` | `none` |
| `sandero_iii_expression_ecog120_manual` | `src_pl_sandero_expression_ecog120_mt_20260626` | Windows | `rear_windows_power` | `none` |
| `sandero_iii_expression_ecog120_manual` | `src_pl_sandero_expression_ecog120_mt_20260626` | Dimensions | `roof_height_with_rails` | `none` |
| `sandero_iii_expression_ecog120_manual` | `src_pl_sandero_expression_ecog120_mt_20260626` | Mirrors | `side_mirrors_electric_adjustment` | `none` |
| `sandero_iii_expression_ecog120_manual` | `src_pl_sandero_expression_ecog120_mt_20260626` | Infotainment | `speaker_count` | `none` |
| `sandero_iii_expression_ecog120_manual` | `src_pl_sandero_expression_ecog120_mt_20260626` | Steering | `steering_wheel_material` | `none` |
| `sandero_iii_journey_ecog120_manual` | `src_pl_sandero_journey_ecog120_mt_20260626` | Seats | `centre_console_variant` | `none` |
| `sandero_iii_journey_ecog120_manual` | `src_pl_sandero_journey_ecog120_mt_20260626` | Performance | `factory_speed_limit` | `none` |
| `sandero_iii_journey_ecog120_manual` | `src_pl_sandero_journey_ecog120_mt_20260626` | Doors | `key_count` | `none` |
| `sandero_iii_journey_ecog120_manual` | `src_pl_sandero_journey_ecog120_mt_20260626` | Windows | `rear_windows_power` | `none` |
| `sandero_iii_journey_ecog120_manual` | `src_pl_sandero_journey_ecog120_mt_20260626` | Dimensions | `roof_height_with_rails` | `none` |
| `sandero_iii_journey_ecog120_manual` | `src_pl_sandero_journey_ecog120_mt_20260626` | Mirrors | `side_mirrors_electric_adjustment` | `none` |
| `sandero_iii_journey_ecog120_manual` | `src_pl_sandero_journey_ecog120_mt_20260626` | Infotainment | `speaker_count` | `none` |
| `sandero_iii_journey_ecog120_manual` | `src_pl_sandero_journey_ecog120_mt_20260626` | Steering | `steering_wheel_material` | `none` |
| `sandero_stepway_iii_essential_ecog120_manual` | `src_pl_sandero_stepway_essential_ecog120_mt_20260626` | Dimensions | `front_track` | `none` |
| `sandero_stepway_iii_essential_ecog120_manual` | `src_pl_sandero_stepway_essential_ecog120_mt_20260626` | Engine | `max_power_rpm` | `lpg` |
| `sandero_stepway_iii_essential_ecog120_manual` | `src_pl_sandero_stepway_essential_ecog120_mt_20260626` | Engine | `max_power_rpm` | `petrol` |
| `sandero_stepway_iii_essential_ecog120_manual` | `src_pl_sandero_stepway_essential_ecog120_mt_20260626` | Dimensions | `rear_track` | `none` |
| `sandero_stepway_iii_expression_ecog120_automatic` | `src_pl_sandero_stepway_expression_ecog120_at_20260626` | Seats | `centre_console_variant` | `none` |
| `sandero_stepway_iii_expression_ecog120_automatic` | `src_pl_sandero_stepway_expression_ecog120_at_20260626` | Dimensions | `front_track` | `none` |
| `sandero_stepway_iii_expression_ecog120_automatic` | `src_pl_sandero_stepway_expression_ecog120_at_20260626` | Engine | `max_power_rpm` | `lpg` |
| `sandero_stepway_iii_expression_ecog120_automatic` | `src_pl_sandero_stepway_expression_ecog120_at_20260626` | Engine | `max_power_rpm` | `petrol` |
| `sandero_stepway_iii_expression_ecog120_automatic` | `src_pl_sandero_stepway_expression_ecog120_at_20260626` | Dimensions | `rear_track` | `none` |
| `sandero_stepway_iii_expression_ecog120_automatic` | `src_pl_sandero_stepway_expression_ecog120_at_20260626` | Windows | `rear_windows_power` | `none` |
| `sandero_stepway_iii_expression_ecog120_automatic` | `src_pl_sandero_stepway_expression_ecog120_at_20260626` | Mirrors | `side_mirrors_electric_adjustment` | `none` |
| `sandero_stepway_iii_expression_ecog120_automatic` | `src_pl_sandero_stepway_expression_ecog120_at_20260626` | Infotainment | `speaker_count` | `none` |
| `sandero_stepway_iii_expression_ecog120_automatic` | `src_pl_sandero_stepway_expression_ecog120_at_20260626` | Steering | `steering_wheel_material` | `none` |
| `sandero_stepway_iii_expression_ecog120_manual` | `src_pl_sandero_stepway_expression_ecog120_mt_20260626` | Seats | `centre_console_variant` | `none` |
| `sandero_stepway_iii_expression_ecog120_manual` | `src_pl_sandero_stepway_expression_ecog120_mt_20260626` | Dimensions | `front_track` | `none` |
| `sandero_stepway_iii_expression_ecog120_manual` | `src_pl_sandero_stepway_expression_ecog120_mt_20260626` | Engine | `max_power_rpm` | `lpg` |
| `sandero_stepway_iii_expression_ecog120_manual` | `src_pl_sandero_stepway_expression_ecog120_mt_20260626` | Engine | `max_power_rpm` | `petrol` |
| `sandero_stepway_iii_expression_ecog120_manual` | `src_pl_sandero_stepway_expression_ecog120_mt_20260626` | Dimensions | `rear_track` | `none` |
| `sandero_stepway_iii_expression_ecog120_manual` | `src_pl_sandero_stepway_expression_ecog120_mt_20260626` | Windows | `rear_windows_power` | `none` |
| `sandero_stepway_iii_expression_ecog120_manual` | `src_pl_sandero_stepway_expression_ecog120_mt_20260626` | Mirrors | `side_mirrors_electric_adjustment` | `none` |
| `sandero_stepway_iii_expression_ecog120_manual` | `src_pl_sandero_stepway_expression_ecog120_mt_20260626` | Infotainment | `speaker_count` | `none` |
| `sandero_stepway_iii_expression_ecog120_manual` | `src_pl_sandero_stepway_expression_ecog120_mt_20260626` | Steering | `steering_wheel_material` | `none` |
| `sandero_stepway_iii_extreme_ecog120_automatic` | `src_pl_sandero_stepway_extreme_ecog120_at_20260626` | Seats | `centre_console_variant` | `none` |
| `sandero_stepway_iii_extreme_ecog120_automatic` | `src_pl_sandero_stepway_extreme_ecog120_at_20260626` | Performance | `factory_speed_limit` | `none` |
| `sandero_stepway_iii_extreme_ecog120_automatic` | `src_pl_sandero_stepway_extreme_ecog120_at_20260626` | Dimensions | `front_track` | `none` |
| `sandero_stepway_iii_extreme_ecog120_automatic` | `src_pl_sandero_stepway_extreme_ecog120_at_20260626` | Doors | `key_count` | `none` |
| `sandero_stepway_iii_extreme_ecog120_automatic` | `src_pl_sandero_stepway_extreme_ecog120_at_20260626` | Engine | `max_power_rpm` | `lpg` |
| `sandero_stepway_iii_extreme_ecog120_automatic` | `src_pl_sandero_stepway_extreme_ecog120_at_20260626` | Engine | `max_power_rpm` | `petrol` |
| `sandero_stepway_iii_extreme_ecog120_automatic` | `src_pl_sandero_stepway_extreme_ecog120_at_20260626` | Dimensions | `rear_track` | `none` |
| `sandero_stepway_iii_extreme_ecog120_automatic` | `src_pl_sandero_stepway_extreme_ecog120_at_20260626` | Windows | `rear_windows_power` | `none` |
| `sandero_stepway_iii_extreme_ecog120_automatic` | `src_pl_sandero_stepway_extreme_ecog120_at_20260626` | Mirrors | `side_mirrors_electric_adjustment` | `none` |
| `sandero_stepway_iii_extreme_ecog120_automatic` | `src_pl_sandero_stepway_extreme_ecog120_at_20260626` | Infotainment | `speaker_count` | `none` |
| `sandero_stepway_iii_extreme_ecog120_automatic` | `src_pl_sandero_stepway_extreme_ecog120_at_20260626` | Steering | `steering_wheel_material` | `none` |
| `sandero_stepway_iii_extreme_ecog120_manual` | `src_pl_sandero_stepway_extreme_ecog120_mt_20260626` | Seats | `centre_console_variant` | `none` |
| `sandero_stepway_iii_extreme_ecog120_manual` | `src_pl_sandero_stepway_extreme_ecog120_mt_20260626` | Performance | `factory_speed_limit` | `none` |
| `sandero_stepway_iii_extreme_ecog120_manual` | `src_pl_sandero_stepway_extreme_ecog120_mt_20260626` | Dimensions | `front_track` | `none` |
| `sandero_stepway_iii_extreme_ecog120_manual` | `src_pl_sandero_stepway_extreme_ecog120_mt_20260626` | Doors | `key_count` | `none` |
| `sandero_stepway_iii_extreme_ecog120_manual` | `src_pl_sandero_stepway_extreme_ecog120_mt_20260626` | Engine | `max_power_rpm` | `lpg` |
| `sandero_stepway_iii_extreme_ecog120_manual` | `src_pl_sandero_stepway_extreme_ecog120_mt_20260626` | Engine | `max_power_rpm` | `petrol` |
| `sandero_stepway_iii_extreme_ecog120_manual` | `src_pl_sandero_stepway_extreme_ecog120_mt_20260626` | Dimensions | `rear_track` | `none` |
| `sandero_stepway_iii_extreme_ecog120_manual` | `src_pl_sandero_stepway_extreme_ecog120_mt_20260626` | Windows | `rear_windows_power` | `none` |
| `sandero_stepway_iii_extreme_ecog120_manual` | `src_pl_sandero_stepway_extreme_ecog120_mt_20260626` | Mirrors | `side_mirrors_electric_adjustment` | `none` |
| `sandero_stepway_iii_extreme_ecog120_manual` | `src_pl_sandero_stepway_extreme_ecog120_mt_20260626` | Infotainment | `speaker_count` | `none` |
| `sandero_stepway_iii_extreme_ecog120_manual` | `src_pl_sandero_stepway_extreme_ecog120_mt_20260626` | Steering | `steering_wheel_material` | `none` |

## Equipment gaps

| Configuration | Source | Category | Attribute |
| --- | --- | --- | --- |
| `sandero_stepway_iii_expression_ecog120_automatic` | `src_pl_sandero_stepway_expression_ecog120_at_20260626` | Driving Systems | `gear_shift_indicator` |
| `sandero_stepway_iii_extreme_ecog120_automatic` | `src_pl_sandero_stepway_extreme_ecog120_at_20260626` | Driving Systems | `gear_shift_indicator` |