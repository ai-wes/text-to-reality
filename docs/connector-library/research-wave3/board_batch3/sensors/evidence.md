# Pololu sensor and driver geometry evidence

## Charter
Goal: 12 additional disjoint exact Pololu SKUs with full physical edge rows and separate auxiliary pads. Scope: sensor and motor-driver carriers. Object: connector geometry and shipped population. Subject: each exact SKU and the manufacturer drawing linked on its product page. Type: descriptive. Questions: physical row count, total contacts, pitch, population, auxiliary contacts and revision scope. Knowledge depth: working, based on prior breakout PCB research.

## Canonical sources
1. Pololu exact-SKU pages and their official dimension/pinout images.
2. Direct visual inspection of those manufacturer images. All images used are preserved with SHA-256 hashes in sensor_catalog.json.

## Findings ledger
- F1: Pololu 1182, A4988 Stepper Motor Driver Carrier: 8 + 8 main header contacts, every row 1xN at 2.54 mm. Auxiliary contacts: none identified. Source: https://www.pololu.com/product/1182; geometry image(s): https://a.pololu-files.com/picture/0J10061.1200.jpg?28dcebcb0b7b778f9af83cdb52c0ef8a
- F2: Pololu 2133, DRV8825 Stepper Motor Driver Carrier, High Current: 8 + 8 main header contacts, every row 1xN at 2.54 mm. Auxiliary contacts: none identified. Source: https://www.pololu.com/product/2133; geometry image(s): https://a.pololu-files.com/picture/0J4231.1200.jpg?a77bba8d3abd5c978e377eb505a9dfba
- F3: Pololu 2134, DRV8834 Low-Voltage Stepper Motor Driver Carrier: 8 + 8 main header contacts, every row 1xN at 2.54 mm. Auxiliary contacts: none identified. Source: https://www.pololu.com/product/2134; geometry image(s): https://a.pololu-files.com/picture/0J4347.1200.jpg?4d587f0a773969cc5c1d5316a4f91508
- F4: Pololu 2135, DRV8835 Dual Motor Driver Carrier: 7 + 7 main header contacts, every row 1xN at 2.54 mm. Auxiliary contacts: none identified. Source: https://www.pololu.com/product/2135; geometry image(s): https://a.pololu-files.com/picture/0J4055.1200.jpg?329b27f39fe705ef5e321d233ea3e7dc
- F5: Pololu 2990, DRV8838 Single Brushed DC Motor Driver Carrier: 5 + 5 main header contacts, every row 1xN at 2.54 mm. Auxiliary contacts: none identified. Source: https://www.pololu.com/product/2990; geometry image(s): https://a.pololu-files.com/picture/0J5751.1200.jpg?99af3fba112cbef297645d73c7b3d8b4
- F6: Pololu 4036, DRV8876 Single Brushed DC Motor Driver Carrier: 7 + 7 main header contacts, every row 1xN at 2.54 mm. Auxiliary contacts: none identified. Source: https://www.pololu.com/product/4036; geometry image(s): https://a.pololu-files.com/picture/0J11571.1200.jpg?61eab4d98030e2b46c79053588e773a2, https://a.pololu-files.com/picture/0J11574.1200.jpg?4590eb11b6cf255a83c6087d53c0aaf7
- F7: Pololu 4038, DRV8256E Single Brushed DC Motor Driver Carrier: 6 + 6 main header contacts, every row 1xN at 2.54 mm. Auxiliary contacts: none identified. Source: https://www.pololu.com/product/4038; geometry image(s): https://a.pololu-files.com/picture/0J11305.1200.jpg?398f0ed99ce2a61b4bed16d49b011efa, https://a.pololu-files.com/picture/0J11387.1200.jpg?f6d636536852d28c5c2f1a8b71a1e60f
- F8: Pololu 3415, VL53L1X Time-of-Flight Distance Sensor Carrier with Voltage Regulator, 400cm Max: 7 main header contacts, every row 1xN at 2.54 mm. Auxiliary contacts: none identified. Source: https://www.pololu.com/product/3415; geometry image(s): https://a.pololu-files.com/picture/0J7225.1200.jpg?4cd3973ce1cd37dbec8077396a14f803, https://a.pololu-files.com/picture/0J8679.1200.jpg?6de17a8834c6292052b284d216fae2bf
- F9: Pololu 2489, VL6180X Time-of-Flight Distance Sensor Carrier with Voltage Regulator, 60cm max: 7 main header contacts, every row 1xN at 2.54 mm. Auxiliary contacts: none identified. Source: https://www.pololu.com/product/2489; geometry image(s): https://a.pololu-files.com/picture/0J6785.1200.jpg?14550b59917a0ef70537b1d2d43c816e, https://a.pololu-files.com/picture/0J6786.1200.jpg?b64023d6f8b4b16894f49e99debbf8c9
- F10: Pololu 3418, VL53L7CX Time-of-Flight 8×8-Zone Wide FOV Distance Sensor Carrier with Voltage Regulator, 350cm Max: 7 main header contacts, every row 1xN at 2.54 mm. Auxiliary contacts: I2C_RST. Source: https://www.pololu.com/product/3418; geometry image(s): https://a.pololu-files.com/picture/0J11642.1200.jpg?6446cfa63e805229cbdb458a175a953a, https://a.pololu-files.com/picture/0J12241.1200.jpg?1e7474b4f01ad23fd85d6350bbc3bd15
- F11: Pololu 2739, AltIMU-10 v5 Gyro, Accelerometer, Compass, and Altimeter (LSM6DS33, LIS3MDL, and LPS25H Carrier): 5 main header contacts, every row 1xN at 2.54 mm. Auxiliary contacts: SA0. Source: https://www.pololu.com/product/2739; geometry image(s): https://a.pololu-files.com/picture/0J7061.1200.jpg?1a10de37745494f6aa3c28f2dd90d3d1, https://a.pololu-files.com/picture/0J7069.1200.jpg?503f83fc79faeb0b92c0c71b8157c480
- F12: Pololu 2490, VL53L0X Time-of-Flight Distance Sensor Carrier with Voltage Regulator, 200cm Max: 7 main header contacts, every row 1xN at 2.54 mm. Auxiliary contacts: none identified. Source: https://www.pololu.com/product/2490; geometry image(s): https://a.pololu-files.com/picture/0J7225.1200.jpg?4cd3973ce1cd37dbec8077396a14f803, https://a.pololu-files.com/picture/0J7226.1200.jpg?3489fa335a7cb10a1b78c158c1543192

## Scope filter
Mechanical mounting holes, small vias, thermal vias and non-connector SMT pads excluded from header counts. Power capability and JIG fit not inferred. Header strips supplied in kits are used only for assembly/pitch evidence, not board-contact counts.

## Object filter
Related-product pinout pictures present in HTML were discarded when they depict another exact SKU (DRV8874, DRV8876 QFN, and VL53L0X when reading the VL53L1X page). Shared dimensional pictures retained only where manufacturer caption explicitly names the target sensor.
AltIMU-10 v5 and VL53L7CX each have a singleton auxiliary pad offset from the edge header. These remain in auxiliary_connectors, not the primary row. Driver VREF access vias are marked separately and not promoted to header groups.

## Conclusions
F1–F12 support 12 exact-SKU records, 19 main physical header rows and 131 main-row contacts at 2.54 mm. Two additional documented singleton auxiliary control pads are recorded separately. All main rows ship unpopulated; loose male strips are not fitted connector gender.

## Next steps / Risks
Actual fit/current/retention/clearance remain unknown. Single-pad auxiliary pitch is null because pitch cannot be assigned within one contact. Mechanical row separation was not dimensionally established from CAD and is intentionally not inferred from photo scaling. The DRV8256E small T pad function remains unqualified and excluded from main headers. Check exact delivered revision before modeling a solderless fixture.

## Validation
Self-review compared each retained image caption to its exact product, counted holes visually, and cross-checked header assembly documentation. Product HTML snapshots and selected geometry images are preserved. No CAD or physical testing is claimed.
