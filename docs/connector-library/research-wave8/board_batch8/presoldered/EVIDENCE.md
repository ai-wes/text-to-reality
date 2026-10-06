# Factory pre-soldered variants, checked 2026-10-06

## Charter
Goal: add exact factory-soldered male-header variants of bare boards already in the JIG research catalog, with useful whole-row connector-selection geometry. Scope: official Seeed XIAO, Adafruit assembled Feather and SparkFun variants; object: exact retail population variants; subject: SKU, main row count, pitch, gender and relationship to the bare parent. Descriptive research; working knowledge from existing catalog. Q1 exact variant/parent identity; Q2 installed header count/gender; Q3 pitch; Q4 duplicates and fit limits.

## Canonical sources
1. Official exact-SKU product listing and its photos: identity, population, gender and visual count
2. Manufacturer CAD, exact-model dimensional data and official header specification: nominal pitch and complete physical positions
3. Existing catalogs and research ZIPs: prior IDs and previously extracted manufacturer CAD; not independent evidence of factory population

Full source URLs and local snapshots are in each record and findings-ledger.json. sources.json records Seeed photo URLs. Parent CAD used for geometry is included. Photographs were visually inspected individually. Readable exact-SKU text establishes installed configuration, rather than interpreting a generic 'assembled PCB' statement as soldered headers.

## Findings ledger
See findings-ledger.json, F1–F10, one row per admitted variant. Every record combines its new exact assembled SKU evidence with independently scoped parent geometry. No bare board has been relabeled or modified.

| Ledger | New SKU | Bare parent | Main headers |
|---|---|---|---|
| F1 | Seeed 102010388 | XIAO SAMD21 | 7 + 7 |
| F2 | Seeed 102010630 | XIAO RP2040 | 7 + 7 |
| F3 | Seeed 102010631 | XIAO nRF52840 | 7 + 7 |
| F4 | Seeed 102010632 | XIAO nRF52840 Sense | 7 + 7 |
| F5 | Seeed 102010633 | XIAO ESP32-C3 | 7 + 7 |
| F6 | Seeed 102010635 | XIAO ESP32-S3 Sense | 7 + 7 |
| F7 | Seeed 102010636 | XIAO ESP32-C6 | 7 + 7 |
| F8 | Seeed 102010637 | XIAO RP2350 | 7 + 7 |
| F9 | Adafruit 3046 | Feather HUZZAH ESP8266 2821 | 16 + 12 |
| F10 | Adafruit 3591 | HUZZAH32 ESP32 Feather 3405 | 16 + 12 |

All main headers are straight, unshrouded, single-row, male, factory installed, nominal 2.54 mm. These are whole-row candidates for female mating connectors. Total: 10 boards, 20 rows, 168 positions.

## Scope filter
Excluded already cataloged Raspberry Pi Pico H, WH, Pico 2 with headers and Pico 2 W with headers. Excluded stacking header SKUs: a female upper face and male lower face should not be collapsed into this plain male configuration. SparkFun Pro Micro RP2040 guide instructs the user to solder headers; no exact new factory-populated SKU was verified. No market popularity ranking was inferred. Newer XIAO families without a cataloged bare parent were outside this bounded pass.

## Object filter
Withheld Seeed 102010634, XIAO ESP32-S3 non-Sense. Its exact SKU and 7+7 male factory population are established, but the official wiki's non-Sense KiCad download URL returns the identical Sense v1.5 archive. The downloaded non-Sense DXF did not yield a verified pin-pitch measurement in this pass. A Sense filename is not silently used as non-Sense CAD evidence. This candidate is in unresolved-candidates.json.

For C6, S3 Sense and RP2350, extracted CAD edge footprint pads have 14 distinct numbered positions and longitudinal coordinates −7.62, −5.08, −2.54, 0, 2.54, 5.08, 7.62 mm. Duplicate castellated/through-hole primitives are not extra positions. Some inner end-hole coordinates differ laterally on S3 Sense: no whole-board row-spacing or fit inference is made from those values. For RP2040 and ESP32-C3, the official Seeed design guide names those models and explicitly specifies two seven-position 2.54 mm male headers. SAMD21 and nRF52840 variants use prior exact-model manufacturer CAD. SKU photo and parent identity support only nominal main-row transfer, not retail PCB revision equivalence.

## Conclusions
F1–F10 support ten new exact assembled records, suitable for nominal row-count/pitch/gender filtering. They do not certify any particular JIG connector fit. Bare parent records must remain distinct. This is a qualified self-review, not an independent audit.

## Next steps / Risks
- Keep physical_fit_verified, automatic_fit_eligible and comb_qualified false everywhere
- Header height, mating depth, pin cross-section tolerances, housing envelope and collision clearance need physical or exact connector-specific dimensional validation
- Preserve exact SKU selection; included loose headers are not factory population
- Retail PCB revision is not locked to downloaded CAD. This matters especially where old SAMD21 CAD is retained; only main-row nominal geometry is proposed
- USB, camera/expansion connectors, battery/debug and underside pads remain outside the main header counts
- To admit the non-Sense S3 candidate, obtain corrected exact-model CAD or independently read its exact dimension drawing
- Regenerate using build_catalog.py then finalize.py; validation is in VALIDATION.txt. Duplicate audit includes available catalog JSON and research/integration ZIP entries
