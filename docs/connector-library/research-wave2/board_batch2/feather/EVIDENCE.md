# Adafruit / Seeed second-wave physical header research

## Charter
Goal: 19 disjoint exact-board records describing complete physical header rows, not advertised GPIO totals. Scope: JIG header catalog. Object: Adafruit Feather, ItsyBitsy, Trinket M0 and QT Py plus standard Seeed XIAO SAMD21/nRF52840 boards. Type: descriptive, based on manufacturer geometry. Questions: physical row counts, pitch, header population/gender, CAD revision and auxiliary interfaces. No mechanical fit certification or live-store changes.

## Canonical sources
1. Manufacturer Adafruit GitHub Eagle PCB files, pinned tree commit where available, otherwise downloaded master with SHA-256. Source URL and local file appear per record.
2. Manufacturer Seeed PCB archives linked from https://wiki.seeedstudio.com/XIAO_BLE/ and https://wiki.seeedstudio.com/Seeeduino-XIAO/. Exact archive URL, file revision and SHA-256 appear per record.
3. Adafruit exact product pages linked per record; manufacturer README snapshots identify products and confirm loose-header options where explicitly stated.
All sources retrieved 2026-10-06. The Adafruit product pages were readable through web retrieval; direct HTTP downloads returned 403 and were not used as evidence. No access restriction was bypassed.

## Findings ledger
Machine-readable ledger: findings-ledger.json. Coordinate evidence: every JSON header includes numbered pin coordinates and CAD signal/net names. cad-inspection.txt and seeed-cad-inspection.txt preserve extraction details; original PCB files remain beside the result.

- Seven Feather models: independent 16-position and 12-position rows, 2.54 mm pitch, all positions counted including power/reset/enable.
- ItsyBitsy 32u4 3V/5V, M0 Express, M4 Express: two 14-position rows AND one separate 5-position end row, all 2.54 mm. End-row grouping stays separate; do not merge it into either long row.
- ItsyBitsy nRF52840 Express: two 14-position rows; no 5-position end header present in inspected CAD.
- Trinket M0: two 5-position rows, 2.54 mm.
- QT Py SAMD21 / ESP32-S2 / ESP32-S3 8MB-no-PSRAM: two 7-position rows, 2.54 mm. CAD includes an additional castellated duplicate of each hole; it is NOT a second independent pin row.
- XIAO SAMD21 v1.0 / nRF52840 v1.2 / nRF52840 Sense v1.1: two 7-position rows, 2.54 mm. Interior through-holes establish the header geometry; castellated duplicates excluded.

Population evidence: Adafruit M0 Express, M4 Express, Feather 328P, Feather 32u4 Adalogger, ItsyBitsy M0 and ItsyBitsy nRF52840 manufacturer text explicitly describes headers supplied for user soldering. Other records are scoped to the bare-footprint configuration in manufacturer CAD rather than asserting the population of all shipped variants. Bare holes have gender 'none'; never interpret this as male. Actual installed hardware must be checked.

## Scope filter
Excluded RP2040/RP2350 records already covered in wave one. Excluded generic GPIO totals, castellated duplicates, USB shell pins and SMD anchor pads from full-row counts. Auxiliary USB, JST, battery, NFC and debug/test-pad interfaces remain separate. No equivalence to a standard adjacent dual-row connector is inferred from two opposing board edges.

## Object filter
Revision is explicit: Seeed SAMD21 is the original v1.0 CAD, not the currently linked v2.1 or Plus. nRF52840 and Sense use their individually linked PCB archives. Adafruit files with master references have a content hash but an unpinned branch; physical retail revision remains unverified. Exact product 5426 is the ESP32-S3 8MB/no-PSRAM version. Similar-looking products are not aliases.

## Conclusions
All 19 records have CAD-backed complete physical header-row counts and 2.54 mm pitch, with individual coordinates permitting independent verification (all ledger rows). The record is a geometry proposal, not a ready-to-plug fit or gender claim. Actual body clearance, nearby sockets/components, tolerances, installed header gender, board revision and JIG availability require checks before recommending a fit.

## Next steps / Risks
- Integration must retain gender, population, roles and fit_status gates. Do not treat bare-footprint records as verified male-header matches.
- Auxiliary connector population/gender/pitch is intentionally unknown when not independently confirmed; CAD alone does not establish assembled retail population. Do not promote these to comb candidates.
- Check exact sample revision and installed header pins, then measure JIG housing/component clearances.
- Next disjoint candidates: Feather nRF52832 Bluefruit LE, Feather nRF52840 Express, Feather nRF52840 Sense, Feather M0 Bluefruit LE, Feather 32u4 Bluefruit LE, Feather M0 RFM69HCW 433/868-915, Feather M0 RFM95 433/868-915, Feather 32u4 RFM69HCW 433/868-915, Feather 32u4 RFM95 433/868-915, Feather M0 WiFi WINC1500, QT Py ESP32-C3, QT Py ESP32 Pico, original Trinket 3.3V/5V, Pro Trinket 3V/5V. These are candidates only; not counted or yet verified here.
