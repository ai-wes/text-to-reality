# SBC header catalog
## Charter
Goal: 8–12 exact widely used SBC models missing from preceding batches. Main multi-row GPIO headers remain discoverable without being single-row-comb qualified.
Scope / Object / Subject: SBC physical header dictionary / Raspberry Pi, BeagleBone, Orange Pi / whole connector counts, pitch, row count, gender, population and separate auxiliary/debug headers.
Type: descriptive. Working knowledge of families; require originating documentation and board drawings for exact models.
Canon: Raspberry Pi official hardware documentation/product briefs/mechanical drawings; BeagleBoard system reference manuals; Orange Pi official manuals (all rank 1). Prior catalogs rank 3 for deduplication only.
Questions: exact model coverage; full physical geometry and population; separate auxiliary connectors and revision limits.
## Findings ledger
F1. Raspberry Pi current hardware documentation, model tables and GPIO section: nine exact selected models (Zero, Zero W, Zero 2 W, 1 Model B+, 2 Model B, 3 Model B, 3 Model B+, 4 Model B, 5) have complete 40-contact GPIO connectors/footprints with 2.54 mm pitch. Explicit source wording distinguishes bare Zero variants from pre-soldered variants. Reduced schematics enumerate odd/even positions through 40. No model is duplicated by RAM size or PCB revision.
F2. Reduced schematics RP-008340-DS (3B), RP-008339-DS (3B+) and RP-008327-DS (2B) identify J2 as a two-way RUN header. Population and auxiliary pitch remain null. Pi 4 schematic RP-008345-DS identifies a separate three-position J2 RUN/GLOBAL_EN and four-contact J14 PoE. Pi 3B+ J14 is independently a four-contact PoE header. None is merged into GPIO.
F3. Official Raspberry Pi Press articles https://magazine.raspberrypi.com/articles/rca-pi-zero and https://magazine.raspberrypi.com/articles/pi-zero-w identify separate unpopulated RUN/composite interfaces. The TV pair has two positions; unresolved RUN geometry/count is null rather than guessed. Zero 2 W RUN/TV are listed in official hardware docs as underside test pads, not assumed two-pin header rows.
F4. Raspberry Pi 5 originating announcement https://www.raspberrypi.com/news/introducing-raspberry-pi-5/ names four PoE pins, two RTC-battery pins, three UART/debug pins and four fan pins. Hardware docs specify fan JST-SH pitch 1 mm. Linked debug standard RP-008189-DS (internal RP-003139-SP Rev 4), p.3 specifies three-position JST-SH at 1 mm. Contact gender in shrouded connectors stays null where not independently established.
F5. BeagleBoard official BeagleBone Black manual (June 4 2026), PDF pp.26–27,32,34,70–73,77,81,91–92: P8/P9 are two complete 46-position cape interfaces. Expansion/mating definition is 2x23 at 2.54 x 2.54 mm. Inspected official photo shows fitted female sockets and male 1x6 serial debug. Small serial pitch left null rather than borrowed from main connectors.
F6. That manual specifies optional JTAG connector FTR-110-03-G-D-06. Samtec's originating https://www.samtec.com/products/ftr-110-03-g-d-06 explicitly omits pin 6 in the nominal 20-position 2-row part, with 1.27 mm within-row and 2.54 mm between-row pitch. Catalog uses 19 actual connector contacts, nominal_positions 20, missing_positions [6], and unpopulated assembly. Footprint pad count is not asserted. This is a keyed optional connector, never a full 2x10 comb.
F7. Seeed official Green wiki identifies two 46-position cape connectors, two Grove ports, exact Green identity. Linked schematic REV1.2 dated 2024-08-16 (with legacy internal title/revision strings) explicitly labels P8/P9 2x23 2.54 mm, J1 1x6 2.54 mm, P2 Header 2x10P DNI, and Grove four-position 2 mm right-angle connectors. Inspected official cover photo confirms female cape sockets and fitted serial/Grove connectors. Do not apply Black's keyed-JTAG count to Green without its exact BOM.
F8. Deduplication against initial archive found none of the selected SBC families. JSON validation has 11 exact models and 33 separately represented interfaces; every full row-count sum matches known pin_count and all fit flags remain unverified.

## Scope filter
Excluded SoC pin totals and GPIO signal totals. Full 2x20/2x23 structures remain complete, not split into fabricated single-row-compatible subheaders. Memory-size and PCB-revision variants do not inflate model counts. USB, video, Ethernet, storage, FFC and production test pads are not counted as generic pin headers.

## Object filter
Explicitly retain unknown auxiliary population, pitch and RUN details; a main-header-verified board is not presented as a complete mechanical fixture drawing. BeagleBone Black optional nominal-20 JTAG keying does not transfer to Green. Zero 2 W test pads do not inherit Zero's TV/RUN holes. Raspberry Pi mechanical drawings are reference-only and contain manufacturer tolerance disclaimers.

## Conclusions
Eleven disjoint exact SBC models are ready for dictionary inclusion (F1–F8). Main SBC GPIO/cape interfaces are multi-row; none is a compatible complete target for a single-row comb. Verified smaller/debug connectors remain separate, with physical jig fit unverified. No Orange Pi record is fabricated from secondary mirrors.

## Next steps / Risks
- Verify actual board revision, installed population, clearance, pin cross-section and connector orientation before physical fixture design
- Resolve null auxiliary attributes and incomplete RUN details from exact-revision BOM/CAD or actual unit inspection
- Raspberry Pi PIP PDFs and hardware documentation were successfully retrieved through web tools, but direct filesystem PDF downloads returned HTTP 403; source URLs and the verified findings are preserved instead of claiming local binaries. BeagleBoard PDF, Seeed schematic PDF and inspected BeagleBoard/Seeed imagery are locally preserved
- Orange Pi official wiki/product URLs repeatedly timed out; reseller manuals were deliberately not substituted. Orange Pi 5 remains a lead, not a counted record
- The partially opened Nucleo-144 lead directory outside this SBC folder is not part of this completed wave

## Review result
Primary-source and internal consistency review complete; no independent physical test. Main geometry is source-backed, remaining auxiliary uncertainties are explicit, and no fabricated revision variants or compatibility claims are present.
