# Wave four: ESP Feathers and Metro boards

## Charter
Goal: complete 12 disjoint exact-SKU records with physical row geometry, population/gender, revision provenance and auxiliary ports. Scope: JIG header catalog research. Object: Adafruit ESP32-S2/S3 display variants, other ESP Feathers and Metro M0/M4. Type: descriptive. Questions: full row counts, pitch, installed-vs-bare configuration, exact revision and auxiliary exclusions. Manufacturer CAD is rank 1; manufacturer product pages and photographs establish SKU and connector population. No fit certification or deployment.

## Canonical sources
The 12 manufacturer product URLs are linked in the JSON and were opened on 2026-10-06. Every record includes an exact manufacturer Git commit, PCB SHA-256, source URL and local CAD filename. Commit IDs were recovered from the GitHub codeload archive comment. Repository README snapshots identify the specific SKU. Metro manufacturer photographs were extracted from the same source archives and visually inspected; they are linked per record.

## Findings ledger
findings-ledger.json gives one source-backed geometry claim per SKU. Every single-row group includes transformed board-coordinate pin centers and signals; auxiliary SPI/SWD connector pad coordinates also remain in JSON.

- Products 5000, 5300, 5345, 5323, 5483, 5691, 5400, 3405, 2821 and 5933 each have separate complete 16-position and 12-position Feather rows at CAD-measured 2.54 mm pitch.
- Exact S2/S3 memory, display and antenna SKU distinctions are in the names. Product 5323 is 8MB/no-PSRAM; no equivalence is implied for 5477 or 5885. Product 5000 is the PCB-antenna board, not the BME280 or external-antenna versions.
- Products 3505 Metro M0 Express and 3382 Metro M4 Express each have four complete main socket groups: AD 6, IOH 10, IOL 8 and POWER 8, each at 2.54 mm pitch. Main sockets are visibly female and populated in the manufacturer reference photos. Metro M0 product text independently states fully assembled headers. Neither Metro is eligible as a direct female-jumper-comb target.
- Metro SPI/ICSP is a separate populated male 2x3 group at 2.54 mm; SWD is a separate shrouded male 2x5 group at 1.27 mm, visible in the photographs and backed by CAD pad coordinates. Neither is flattened into a single row.
- JST-PH battery, STEMMA QT, USB and TFT display-flex footprints stay auxiliary. Display assemblies and the actual housing/component envelope have not been fit tested.

## Scope filter
All already researched RP2040/RP2350, Seeed, Arduino and prior Adafruit SKUs were excluded. Counts use every physical header position, including power/control/NC, rather than GPIO marketing totals. Connector mounting/anchor pads and display-flex pads are excluded from the comb rows.

## Object filter
Selected exact CAD revision files (including S2 rev C and ESP8266 rev G), not interchangeable seller variants. The TFT models retain their mirrored/oriented CAD placements; no display-side clearance assumption is made. Metro socket groups stay separate across the Arduino-format spacing gaps. Manufacturer reference photos establish population for the depicted models but do not certify every hardware revision or altered user board.

## Conclusions
Twelve new exact SKUs contribute 28 CAD-backed single-row groups, all 2.54 mm (all ledger records). Twenty Feather rows describe the bare-footprint configuration; eight Metro rows are populated female sockets in the reference configuration. All have fit_status unverified and automatic_fit_eligible false. Counts are research facts, not mating/clearance guarantees.

## Next steps / Risks
- Verify the physical board revision and header assembly before suggesting a comb size.
- Preserve gender and population gates, especially female Metro sockets and separately shrouded SWD headers.
- Measure display, USB, battery and STEMMA socket interference on actual hardware; the shared 16+12 count does not settle these constraints.
- Leave auxiliary mating pitch/gender unknown where the evidence only establishes a PCB footprint.
- New primary-source coverage remains for Metro M4 AirLift, Metro M7, Grand Central M4 and selected specialized Feathers. They are not counted here; this bounded batch ends at 12 rather than extrapolating more SKUs from shared geometry.
