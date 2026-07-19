# Jogger Equipment Matrix Intake Selection

## Status

`SELECTED`

The accepted Jogger MY26 price-list pages 4-5 define the first bounded equipment-availability import for all 22 active Jogger configurations. This review imports no data.

## Selected denominator

The implementation package will materialize 53 active boolean attributes for every active configuration, creating 1,166 dated availability records:

- 920 `standard`;
- 84 `optional`;
- 162 `not_available`.

The configuration denominator is 2 essential, 6 expression, 8 extreme and 6 journey combinations across five- and seven-seat bodies and the source-listed powertrains.

## Selected attributes

### Lighting, safety and driver assistance

`led_daytime_running_lights`, `led_headlights`, `automatic_headlights`, `fog_lights`, `high_beam_assist`, `anti_lock_braking_system`, `automatic_emergency_braking`, `electronic_stability_control`, `hill_start_assist`, `extended_grip`, `lane_departure_warning`, `lane_keep_assist`, `driver_attention_monitoring`, `traffic_sign_recognition`, `blind_spot_monitoring`, `emergency_call_ecall`, `driver_front_airbag`, `passenger_front_airbag`, `front_side_airbags`, `curtain_airbags`, `front_seat_belt_pretensioners`, `rear_seat_belt_pretensioners`, `isofix_rear`, `tyre_pressure_monitoring_system` and `tyre_repair_kit`.

### Visibility, controls and parking

`side_mirrors_electric_adjustment`, `side_mirrors_folding`, `side_mirrors_heated`, `onboard_computer`, `instrument_cluster_tft_3_5`, `instrument_cluster_colour_7`, `speed_limiter`, `cruise_control`, `rear_parking_sensors`, `front_parking_sensors`, `rear_view_camera`, `360_camera_system` and `electronic_parking_brake`.

### Comfort and multimedia

`front_windows_power`, `rear_windows_power`, `central_locking`, `keyless_entry`, `manual_air_conditioning`, `automatic_climate_control`, `front_centre_armrest`, `steering_wheel_height_adjustment`, `steering_wheel_reach_adjustment`, `driver_seat_height_adjustment`, `heated_front_seats`, `heated_steering_wheel`, `media_control_system`, `media_display_system` and `navigation_system`.

## Normalization contract

- `●` becomes `standard`;
- `P` and a printed option price become `optional`;
- `-` becomes `not_available`;
- trim-level cells are expanded only to source-backed configurations;
- five-/seven-seat and powertrain qualifications are preserved per configuration;
- notes retain the printed row, page and any package or incompatibility qualifier.

Important conditional mappings are explicit:

- the 7-inch colour cluster is standard for expression only with Hybrid 155, and for every extreme and journey configuration;
- the electronic parking brake is standard for expression Hybrid 155 and all extreme/journey configurations, optional for non-Hybrid expression through the KOMFORT package, and unavailable for essential;
- Multiview Camera is optional for extreme and standard for journey;
- heated steering wheel, heated/folding mirrors and high-beam assist are optional only through the extreme packages shown by the source.

## Exclusions

- `start_stop_system` is already a page-6 scalar observation and will not be duplicated as availability;
- `rain_sensing_wipers` remains deferred because the combined exterior row and the dedicated visibility row disagree for essential;
- colours, materials, wheel designs, upholstery variants and paint prices are value or price observations, not boolean availability;
- roof-rail variants, shark-fin antenna, dashboard inserts, aircraft tables, cargo cover, rubber mats, My Safety, E-Save, third-row opening windows, removable phone holder and spare-wheel compatibility lack a selected dedicated contract in this package;
- package prices themselves are not imported.

## Implementation contract

The next package will add versioned Jogger equipment matrices and a deterministic importer, append exactly 1,166 records without changing the existing 1,811 availability rows, add source/provenance and status-distribution tests, update the baseline to 2,977 availability records, and preserve every Sandero and Duster reporting scope.
