# Wave three: 15 Adafruit controller boards

## Charter
Goal: 15 further exact SKUs with complete physical-row count, pitch, population/gender limitations, revision and auxiliary connector evidence. Scope: JIG physical header research. Object: disjoint Adafruit Feather, QT Py, original Trinket and Pro Trinket boards. Type: descriptive; manufacturer CAD establishes geometry, never mechanical fit. Questions: complete physical row counts, pitch, revision provenance and exclusions. Sources: manufacturer CAD first, exact manufacturer SKU pages second. No paid calls, user-computer edits or catalog deployment.

## Canonical sources
Each record links an opened Adafruit SKU page, a manufacturer GitHub PCB at exact commit, and the repository README. GitHub codeload ZIP comments give the source commits; individual PCB SHA-256 values are retained. Original files and ZIPs remain here for reproducibility. Product pages were checked on 2026-10-06.

## Findings ledger
findings-ledger.json gives one source-grounded claim per SKU. Every JSON header includes board-coordinate pin centers and net names.

- 3406 nRF52832 rev G, 4062 nRF52840 Express rev E, 4516 nRF52840 Sense rev C: complete Feather 16 + 12 rows. The FEATHERWING_NODIM CAD element contains both rows plus mechanical pads; only numbered pins 1–28 were included, split spatially into 16 and 12.
- 2995 Feather M0 Bluefruit LE, 2829 Feather 32u4 Bluefruit LE and 3010 Feather M0 WiFi WINC1500: 16 + 12 rows.
- 5395 QT Py ESP32 Pico 8MB Flash/2MB PSRAM and 5405 QT Py ESP32-C3: 7 + 7 rows. Castellated duplicate pads are excluded.
- 1500 Trinket 3.3V microUSB and 1501 Trinket 5V microUSB: complete 5 + 5 rows. Each consists of a 4-pad element plus a 1-pad element; transformed PCB coordinates show the fifth pad is on the same continuous 2.54 mm grid. This prevents a false 4 + 4 result.
- 2000 Pro Trinket 5V/16MHz and 2010 Pro Trinket 3V/12MHz: main 12 + 12 rows; separate 6-position FTDI row and interior 2-position A6/A7 row. These auxiliary rows are not merged with either main row.
- 3178 Feather M0 RFM95 900MHz and 3179 Feather M0 RFM96 433MHz: main 16 + 12; separate 3-position radio DIO row (DIO5, DIO3, DIO2), plus isolated antenna pad outside header rows.
- 3078 Feather 32u4 RFM95 868/915MHz: main 16 + 12; separate 2-position radio DIO row (DIO3, DIO2), plus isolated antenna pad.
- All 37 single-row header groups have CAD-measured 2.54 mm pitch.
- Nordic SWD connector geometry is separately represented as 2 rows of 5, 1.27 mm pitch, never 1x10. Product 3406 explicitly describes a separately soldered SWD header; product 4062 lists an SWD connector, so its actual gender/population is left unresolved here rather than assuming it is unpopulated.

## Scope filter
Excluded already researched SKUs, all RP2040/RP2350 records, GPIO-only totals, connector shield/anchor pads and castellated copies. Single antenna/NFC pads stay outside multi-position comb rows. Dedicated RF sockets, USB, JST, battery and debug footprints stay separate.

## Object filter
Selected exactly 15 SKUs; no separate record was created merely for different revisions of the same SKU. Radio 3178/3179 share the manufacturer PCB by explicit repository association but retain distinct RF module/SKU identity. Original Trinket records are microUSB revisions, excluding older miniUSB footprints. The nRF52840 Sense sensor revision can change component/clearance details even though these header coordinates are unchanged; no physical compatibility inference follows.

## Conclusions
All fifteen records have complete, reproducible physical row geometry backed by manufacturer PCB data (all ledger rows). They are proposals for bare-footprint geometry only. A header's gender of none identifies the scoped bare footprint, not an assertion about every retail package or user-installed header. automatic_fit_eligible is false throughout and fit_status is unverified.

## Next steps / Risks
- Confirm physical board revision, installed header gender and body dimensions before any JIG recommendation.
- Check housing/component clearance, including radio antenna, FTDI and the Pro Trinket interior analog pads.
- Preserve auxiliary_header_row roles; do not imply that fitting auxiliary rows proves an entire board fits.
- Auxiliary connector population/gender/pitch remains null or explicit unknown wherever not established. Keep these out of automatic comb matching.
- Pro Trinket is legacy hardware; manufacturer deprecation does not invalidate geometry but should prevent framing these as recommended new-board purchases.
- Next disjoint research candidates: Feather 32u4 RFM69 433/900 and RFM96 433, Feather M0 RFM69 433/900, Feather 32u4 FONA, Feather WICED, Feather M4 CAN, QT Py CH32V203/CH552 and ItsyBitsy ESP32. These are unvalidated candidates, not additions to this batch.
