# Spring Non-conflicting Technical Observations Review

**Status:** complete  
**Date:** 2026-08-02  
**Master-data mutations:** 0

## Result

The fully assimilated Spring brochure and MY2025 stock price list were compared with current master data across battery, charging, performance, dimensions and luggage evidence.

Exactly **12** canonical attributes and **36** dated observations are approved for a bounded follow-up migration:

- LFP traction-battery chemistry;
- permanent-magnet synchronous traction-motor technology;
- electric power steering;
- nine common body dimensions from the rendered page-21 diagram.

All approved values come from `src_pl_spring_brochure_20260219`, apply identically to Electric 70 and Electric 100, and are not qualified by grade, wheel size or model year. The migration needs controlled enum representation for `traction_battery_type` and `electric_motor_type`, but no new canonical attribute.

## Deliberate non-migrations

- **204 kg battery mass** and **354 V nominal voltage** remain deferred because their only source is the MY2025 stock price list; they are not projected into current Spring configurations.
- **24.3 kWh** remains deferred because the source does not identify gross versus net capacity.
- Charging times, range and maximum speed are not migrated.
- The **146 mm** ground-clearance value remains deferred because it is explicitly limited to 15-inch wheels.
- Existing 308 L and 1004 L ISO 3832 luggage observations remain unchanged.

## Next package

`spring_nonconflicting_common_technical_observations_migration_001` will materialize only the **36** approved brochure observations and the minimum controlled enum-domain support required by the existing attributes.
