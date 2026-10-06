# Wave five: 13 Adafruit SKUs, with population distinctions

## Charter
Goal: 13 further exact-SKU records with complete physical header groups, pitch, population/gender and auxiliary connectors, then identify high-value uncertainty to resolve in existing records. Scope: JIG physical header research. Object: Metro, Grand Central, selected Feathers, ItsyBitsy and QT Py. Type: descriptive. Questions: counts of every physical position, pitch, contiguous rows vs separate connector groups, installed/bare state and exact provenance. Manufacturer CAD, manufacturer SKU pages and manufacturer photographs are primary evidence. No live integration or prior-wave edits.

## Canonical sources
Every SKU page was opened on 2026-10-06. Each record includes exact manufacturer Git commit, PCB SHA-256, local file and source URL. GitHub archive comments pin commits. Manufacturer photographs were inspected for Metro M4 AirLift, both Metro M7s, Grand Central, Metro 328 with/without headers, and FONA. The Metro 328 with-header photo was retrieved from its verified Adafruit CDN product-image path; other photographs came from manufacturer repositories.

## Findings ledger
findings-ledger.json has a source-backed geometry record per SKU. Pin centers and net labels are carried per header in the JSON.

- Metro M4 AirLift Lite 4000, Metro M7 microSD 5600, Metro M7 AirLift 4950 and Metro 328 with headers 2488: populated female main sockets of 6 + 10 + 8 + 8 positions, each 2.54 mm. Auxiliary SPI/ICSP and SWD remain separate dual-row connectors.
- Metro 328 without headers 2466: the same four footprint counts, but manufacturer product text and reference photo explicitly show bare main and ICSP footprints. This is a distinct exact SKU, not an inferred population variant.
- Grand Central M4 4064: six independent single-row female socket groups of 10 + 8 + 8 + 8 + 8 + 8, plus one female 2x18 socket at 2.54 mm. Its JSON pin_count is TOTAL 36 for that two-row group and pins_per_row is 18; never flatten into a 1x36 row.
- Metro Mini 328 V2 2590: two complete 14-position rows at 2.54 mm. Manufacturer CAD splits each row into 6- and 8-pin elements, but the transformed pad centers form a continuous 14-position grid. The V2 source is explicitly selected instead of older Mini Rev A/B.
- Feather M4 CAN 4759, Feather 32u4 FONA 3027 and WICED WiFi Feather 3056: complete 16 + 12 side rows at 2.54 mm.
- FONA additionally has two separate 1x2 microphone/speaker rows at 2.0 mm, physically bare in the manufacturer photo. They are auxiliary_audio_row, not 2.54 mm targets. Their row separation is not inferred to form a standard 2x2 connector.
- Feather M4 CAN has a separate 3-contact 3.5 mm screw terminal. Manufacturer revision history says the terminal block is pre-soldered from 2023-10-11; older boards can differ. Source: https://www.adafruit.com/product/4759
- ItsyBitsy ESP32 5889 PCB-antenna 8MB/2MB has two 14-position rows and no five-pin end row. The manufacturer explicitly notes the end pins were removed for the antenna. The optional bottom JST battery footprint is marked DNP in CAD.
- QT Py CH32V203 5996 and CH552 QT Py 5960 each have two 7-position rows at 2.54 mm. Castellated duplicates are excluded.

## Scope filter
No prior researched SKU was intentionally repeated. Counts include power/control/NC positions and omit connector shell/anchor pads. GPIO marketing totals are not used. Dedicated SIM, u.FL, audio, battery, USB, microSD, CAN terminal and debug interfaces are distinguished from main comb rows.

## Object filter
Legacy FONA and WICED records are retained for installed hardware but labeled no longer stocked; this is not advice to buy or operate old cellular hardware. Hardware revisions and population are exact-source scoped. Grand Central dual-row and female sockets must keep their gates. No identical-body or clearance inference is made between different Feathers; notably the M4 CAN 12-pin row coordinate is 21.6535 mm in this CAD, not the common 21.59 mm seen elsewhere.

## Conclusions
13 exact SKUs yield 43 physical header groups: 42 single-row groups plus one Grand Central 2x18 group. Forty single-row groups are 2.54 mm, the two FONA audio pairs are 2.0 mm, and Grand Central is a 2.54 mm dual-row socket. All retain fit_status unverified and automatic_fit_eligible false. Each geometric claim has pad-coordinate evidence and exact manufacturer CAD provenance.

## Next steps / Risks
- Preserve rows, pitch, role, population and gender in integration. Do not normalize Grand Central 36 total positions into a 36-pin comb or FONA audio into 2.54 mm.
- Main female sockets and bare holes remain excluded from direct automatic female-comb fit claims.
- Physical sample revision, installed header type, housing dimensions and component clearance still require verification.
- population-audit-candidates.json prioritizes existing-record unknowns. None of those proposed checks updates or qualifies a prior record.
- After these core families, targeted population and clearance checks have greater near-term value than more long-tail SKU expansion. Unresearched Metro ESP32-S2/S3 and specialized Feathers still have primary sources; exhaustive coverage is not claimed.
