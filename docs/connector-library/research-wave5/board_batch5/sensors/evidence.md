# Communication, storage and RTC breakout evidence

## Charter
Goal: 12 disjoint exact manufacturer SKUs covering communication, storage and clock breakouts with full physical header groups, assembly state and separately classified auxiliary connectors. Type: descriptive. Scope: Adafruit interface/storage/clock breakouts; object: SKU-specific connector geometry; subject: manufacturer PCB pads and current product photographs. Questions: complete contact count, rows, pitch, population, revision and limits on fixture proposals. Knowledge depth: working after prior CAD batches.

## Canonical sources
1. Official Adafruit SKU pages and manufacturer GitHub repositories with exact commits.
2. Eagle XML geometry and direct inspection of official product photographs.
3. Manufacturer revision histories establish changes in pre-soldered auxiliary components.

## Findings ledger
- F1: SKU 746 Adafruit Ultimate GPS Breakout PA1616S: JP1=9 contacts, pitch 2.54 mm, role main_edge_row. Product https://www.adafruit.com/product/746; CAD https://github.com/adafruit/Adafruit-Ultimate-GPS/blob/70430c1240b49c1e054f1edee84ad0b5ec8ebe56/Adafruit%20Ultimate%20GPS.brd; image https://cdn-shop.adafruit.com/970x728/746-17.jpg
- F2: SKU 254 Adafruit MicroSD Card Breakout Board+: JP1=8 contacts, pitch 2.54 mm, role main_edge_row. Product https://www.adafruit.com/product/254; CAD https://github.com/adafruit/MicroSD-breakout-board/blob/ef4cb5171b78b6e17f12aa1fd1df41dc3f50418c/microsd.brd; image https://cdn-shop.adafruit.com/970x728/254-06.jpg
- F3: SKU 3013 Adafruit DS3231 Precision RTC Breakout: JP1=8 contacts, pitch 2.54 mm, role main_edge_row. Product https://www.adafruit.com/product/3013; CAD https://github.com/adafruit/Adafruit-DS3231-Precision-RTC-Breakout-PCB/blob/1d60495b54bd6ff8fa4d5acca7a6e1c1a317cfe1/Adafruit%20DS3231%20RTC%20Breakout.brd; image https://cdn-shop.adafruit.com/970x728/3013-06.jpg
- F4: SKU 3295 Adafruit PCF8523 Real Time Clock Assembled Breakout: JP2=5 contacts, pitch 2.54 mm, role main_edge_row. Product https://www.adafruit.com/product/3295; CAD https://github.com/adafruit/Adafruit-PCF8523-RTC-Breakout-PCB/blob/4ec7e14d667a2d075430da0980c35c4f049e860b/Adafruit%20PCF8523%20RTC%20HVSON.brd; image https://cdn-shop.adafruit.com/970x728/3295-10.jpg
- F5: SKU 3296 Adafruit DS1307 Real Time Clock Assembled Breakout: JP2=5 contacts, pitch 2.54 mm, role main_edge_row. Product https://www.adafruit.com/product/3296; CAD https://github.com/adafruit/DS1307-breakout-board/blob/22f84c8b77cacd22bf1296fa9f996f89bf646ae6/DS1307%20Rev%20B.brd; image https://cdn-shop.adafruit.com/970x728/3296-07.jpg
- F6: SKU 5188 Adafruit DS3231 Precision RTC STEMMA QT: JP1=8 contacts, pitch 2.54 mm, role main_edge_row. Product https://www.adafruit.com/product/5188; CAD https://github.com/adafruit/Adafruit-DS3231-Precision-RTC-Breakout-PCB/blob/1d60495b54bd6ff8fa4d5acca7a6e1c1a317cfe1/Adafruit%20DS3231%20STEMMA%20QT.brd; image https://cdn-shop.adafruit.com/970x728/5188-10.jpg
- F7: SKU 5708 Adafruit CAN Pal TJA1051T/3 CAN Bus Transceiver: JP2=7 contacts, pitch 2.54 mm, role main_edge_row. Product https://www.adafruit.com/product/5708; CAD https://github.com/adafruit/Adafruit-CAN-Pal-PCB/blob/56618b3a53162ce48872514be044eab033ed33ef/Adafruit%20CAN%20Pal%20Breakout.brd; image https://cdn-shop.adafruit.com/970x728/5708-06.jpg
- F8: SKU 4471 Adafruit MCP2221A USB to GPIO ADC I2C Breakout: JP1=6 contacts, pitch 2.54 mm, role main_edge_row, JP2=6 contacts, pitch 2.54 mm, role main_edge_row. Product https://www.adafruit.com/product/4471; CAD https://github.com/adafruit/Adafruit-MCP2221-PCB/blob/53e780f92007ff5cd0de8680872af6d316c64847/Adafruit%20MCP2221.brd; image https://cdn-shop.adafruit.com/970x728/4471-02.jpg
- F9: SKU 2264 Adafruit FT232H USB-C GPIO SPI I2C Breakout: JP1=11 contacts, pitch 2.54 mm, role main_edge_row, JP2=11 contacts, pitch 2.54 mm, role main_edge_row. Product https://www.adafruit.com/product/2264; CAD https://github.com/adafruit/Adafruit-FT232H-Breakout-PCB/blob/78919715d58046e883cc4fe47f90c6634582adf7/Adafruit%20FT232H.brd; image https://cdn-shop.adafruit.com/970x728/2264-16.jpg
- F10: SKU 364 Adafruit PN532 NFC RFID Controller Breakout v1.6: JP1=3 contacts, pitch 2.54 mm, role configuration_jumper, JP2=3 contacts, pitch 2.54 mm, role configuration_jumper, JP3=12 contacts, pitch 2.54 mm, role main_edge_row, CN1=6 contacts, pitch 2.54 mm, role main_edge_row, side_row_JP4_JP5=9 contacts, pitch None mm, role nonuniform_edge_row_requires_review. Product https://www.adafruit.com/product/364; CAD https://github.com/adafruit/Adafruit-PN532-RFID-NFC-Breakout/blob/d614276a3168bd402d0729daa7bd94c406de7beb/Adafruit%20PN532_Breakout_v1.6.brd; image https://cdn-shop.adafruit.com/970x728/364-08.jpg
- F11: SKU 3072 Adafruit RFM95W LoRa Radio Breakout 868/915 MHz: JP3=9 contacts, pitch 2.54 mm, role main_edge_row, JP1=5 contacts, pitch 2.54 mm, role main_edge_row. Product https://www.adafruit.com/product/3072; CAD https://github.com/adafruit/Adafruit-RFM-LoRa-Radio-Breakout-PCB/blob/3ad6bed6e1b407afa7119ae548b5c2f1b107c6b1/Adafruit%20RFM%2BLoRa%20Breakout.brd; image https://cdn-shop.adafruit.com/970x728/3072-08.jpg
- F12: SKU 3070 Adafruit RFM69HCW Radio Breakout 868/915 MHz: JP3=9 contacts, pitch 2.54 mm, role main_edge_row, JP1=5 contacts, pitch 2.54 mm, role main_edge_row. Product https://www.adafruit.com/product/3070; CAD https://github.com/adafruit/Adafruit-RFM-LoRa-Radio-Breakout-PCB/blob/3ad6bed6e1b407afa7119ae548b5c2f1b107c6b1/Adafruit%20RFM%2BLoRa%20Breakout.brd; image https://cdn-shop.adafruit.com/970x728/3070-08.jpg

## Scope filter
No power handling, signal integrity, radio-current, antenna-performance or physical JIG compatibility is inferred. Header strip lengths are never used to infer board contacts. Mechanical mounting holes, SMT chip legs, radio-module castellations, solder anchors and alternative connector footprints are excluded from pin-header rows.

## Object filter
Original DS3231 SKU 3013 and QT SKU 5188 are distinct products despite shared chip and 8-position row. PCF8523 SKU 3295 uses HVSON or SOIC-8 layouts: the HVSON file matches the saved current photograph, while both published files carry 1x5 headers. USB-C files used for current FT232H/MCP2221A rather than earlier USB versions.
Ultimate GPS sensor-package label in CAD uses an older module name; current photo PA1616S is recorded, and its nine physical header contacts match. Manufacturer states coin-cell holder is pre-soldered from 2023-11-22. CAN Pal terminal block is pre-soldered from 2024-03-20.
PN532 v1.6 has a physical 9-contact side row represented by 8+1 CAD elements. The added +5V contact is 2.572 mm from its nearest neighbor in the published file. This row has pitch=null, nominal_pitch_mm=2.54 and all adjacent intervals preserved; it is explicitly excluded from uniform-comb proposals. Two separate 1x3 selector groups are configuration jumpers.
RFM69/RFM95 share a manufacturer carrier file explicitly linked to both SKUs in its README. Their 9+5 rows are distinct from the singleton antenna pad and unpopulated alternate SMA/u.FL footprint.

## Conclusions
F1–F12 support 12 exact-SKU records with 20 physical header groups and 145 contacts. Of those contacts, six belong to PN532 selector jumpers and nine to the nonuniform PN532 side row. Every remaining multi-contact row has manufacturer CAD spacing of 2.54 mm.
All pin-header groups are bare/unpopulated in the official photos. Factory USB, card, coin-cell, QT, GPS RF and CAN-terminal connectors are separate; RF connector footprints on the two radio breakouts are unpopulated.

## Next steps / Risks
All actual fit/current/signal qualifications remain unknown. PN532 side row needs exact delivered-board measurement before comb design. USB-C and RF mating contact count/pitch are intentionally null where this research only establishes connector identity and population. These unknowns do not change the independently verified PTH rows.
Product photos represent manufacturer examples, not physical inspection of a delivered part. New revisions or alternate assembly may require revalidation. RS485 was not included in this completed batch; further exact-SKU primary research would be needed.

## Validation
Self-review checked the selected PTH packages and transformed pad positions against official product images. Source commits, CAD file paths, raw pads and photo SHA-256 hashes are saved. All 12 product IDs differ from prior researched sensor/IO records.
