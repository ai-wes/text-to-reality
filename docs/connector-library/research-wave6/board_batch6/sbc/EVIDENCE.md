# Additional Beagle-family SBC headers
## Charter
Goal: prepare up to eight disjoint exact SBC models from originating manuals, without inferring a shared header map across generations.
Scope / Object / Subject: SBC header dictionary / BeagleBoard and Seeed board families / complete connectors and exact marketed model boundaries.
Type: descriptive. Working knowledge, verify each connector family and unusual geometry.
Canon: official BeagleBoard manuals and Seeed schematics, rank 1. Questions: main contact counts, rows/pitch/gender/population; auxiliary separation; PCB revision limits.
## Findings ledger
F1. BeagleBone AI-64 current official manual (2026-06-04) states P8=46 and P9=50; PDF p.38 embeds the CAD schematic showing P9 positions 1–46 plus E1–E4 and labels Header 2x25 2.54mm. Independent original Rev B1 CAD schematic and BOM retrieved from beagleboard/beaglebone-ai-64 confirm fitted female P8 2x23 and P9 2x25. BOM hash 263618c43200ccf7077c6e6ee3bd0c2b114d4d18; items 124/125. Rows are not cropped to Black's 46/46 pattern.
F2. AI-64 BOM items 122/123/131 and DNP-19 distinguish J1 fan four contacts/1.25 mm, J2/J3 UART three contacts/1.5 mm, J10 boxed 2x8/1.27 mm, and unpopulated J11 ten-contact TagConnect pads/1.27 mm. Shrouded female terminology follows manufacturer BOM, not a guessed universal contact-sex convention.
F3. BeagleBone AI current manual pp.8,17–18,42,57 and original BOM item 95 verify two fitted female 2x23 2.54 mm cape headers. J92 is a distinct three-position JST ZH serial connector at 1.5 mm. Do not copy Black's six-position UART or optional CTI connector to this board.
F4. BeagleBone Black Wireless originating board page and original BOM/schematic: P8/P9 are female 46-position dual-row 0.1-inch connectors; X1 is fitted six-position vertical 0.100-inch serial. Official product text names optional nominal 20-position JTAG, but exact omitted-contact/keying is unresolved and pin_count stays null. The downloaded guessed manual URL returned HTML, not a PDF; it is marked as a failed source, not evidence.
F5. Seeed Green Wireless exact wiki, V1.0 schematic and manufacturer PCBA mechanical drawing verify fitted female P8/P9 2x23, a separate six-position serial header, two four-position Grove connectors and a DNI CTI JTAG footprint. Exact pitch values are not dimensioned in the retrieved model-specific sources; they remain null rather than imported from Green/Black. This is an explicit source gap.
F6. Original PocketBeagle manual explicitly describes two unpopulated 36-position interfaces. Manufacturer KiCad file parsed independently: P1 and P2 each have 36 through-hole pads; two y coordinates +/-1.27 mm and x increments 2.54 mm establish complete 2x18 geometry and 2.54 mm row spacing. Reproducible extraction saved as pocket_cad_verified_headers.json. Seven underside JTAG test pads are not fabricated into a connector.
F7. PocketBeagle 2 current manual pp.7–8,32–33,36 and exact original schematic: two pre-soldered, bottom-mounted female 2x18 2.54 mm connectors, separate three-position 1 mm JST-SH UART and ten-contact TagConnect footprint. A0/A1 CPU revisions are not used to create duplicate model records.
F8. BeaglePlay current manual, inspected photo and original BOM verify complete J21 16-contact MIKROE-5210 female socket with two eight-contact sides; within-row pitch is 2.54 mm but the separation of sides is not asserted. Separate J6 male three-position UART at 2.54 mm; J7 four-position Grove at 2 mm; J18 four-position Qwiic at 1 mm. Two TagConnect pad groups are retained with unknown counts rather than guessed.
F9. BeagleV-Ahead current manual, exact CAD schematic and A11-design BOM verify two fitted female 2x23 2.54 mm cape connectors; J10 male 1x6 2.54 mm UART; J7 2x8 1.27 mm boxed mikroBUS-shuttle interface. TagConnect contacts are separately marked unresolved. BeagleV-Fire is a different model and not silently combined.
F10. Eight unique IDs added; 37 connector/footprint records. Consistent known contact/row sums verified. Prior wave files unchanged; source revision identities preserved without manufacturing individual revision variants.

## Canonical source URLs
- https://docs.beagleboard.org/beaglebone-ai-64.pdf
- https://github.com/beagleboard/beaglebone-ai-64/blob/main/hw/BeagleBone_AI-64_Rev_B1_BOM_220602.csv
- https://github.com/beagleboard/beaglebone-ai-64/blob/main/hw/BeagleBone_AI-64_Rev_B1_SCH_220602.pdf
- https://docs.beagleboard.org/beaglebone-ai.pdf
- https://github.com/beagleboard/beaglebone-ai/blob/master/BeagleBone-AI_bom.csv
- https://github.com/beagleboard/beaglebone-ai/blob/master/BeagleBone-AI_RevA2_sch.pdf
- https://www.beagleboard.org/boards/beaglebone-black-wireless
- https://github.com/beagleboard/beaglebone-black-wireless/blob/master/BeagleBone_Black_Wireless_BOM.csv
- https://github.com/beagleboard/beaglebone-black-wireless/blob/master/BeagleBone_Black_Wireless_SCH.pdf
- https://wiki.seeedstudio.com/BeagleBone_Green_Wireless/
- https://github.com/SeeedDocument/BeagleBone_Green_Wireless/blob/master/resources/BeagleBone_Green%20Wireless_V1.0_SCH_20160314.pdf
- https://files.seeedstudio.com/wiki/BeagleBone_Green_Wireless/resources/BBGW-PCBA.pdf
- https://docs.beagleboard.org/pocketbeagle.pdf
- https://github.com/beagleboard/pocketbeagle/blob/master/KiCAD/PocketBeagle.kicad_pcb
- https://docs.beagleboard.org/pocketbeagle-2.pdf
- https://github.com/beagleboard/pocketbeagle-2/blob/main/pocketbeagle2_sch.pdf
- https://docs.beagleboard.org/beagleplay.pdf
- https://github.com/beagleboard/beagleplay/blob/main/BeaglePlay_bom.csv
- https://docs.beagleboard.org/beaglev-ahead.pdf
- https://github.com/beagleboard/beaglev-ahead/blob/main/design/202003615_PCBA_BeagleVAhead_A11_Design-BOM.csv
- https://github.com/beagleboard/beaglev-ahead/blob/main/BeagleV-Ahead_SCH.pdf

## Scope filter
Rejected generic BeagleBone geometry propagation across families. No cropped single-row subheaders, RAM variants, GPIO totals or artificial revisions inflate the catalog. Distinct complete sockets and pad groups remain separate.

## Object filter
AI-64's full 50-position P9 verified in manual, original CAD and BOM; the extra four contacts belong to the connector. Shrouded/boxed and female connectors remain non-comb-qualified. Unpopulated TagConnect footprints are not installed male pins. Pitch/keying gaps for Green Wireless and some auxiliary pads stay null.

## Conclusions
Eight additional exact SBC models are source-backed dictionary entries (F1–F10). Geometry varies enough that copying Black's layout would produce wrong counts and pitches on several models. Every physical fit remains unverified and every comb_qualified flag remains false.

## Next steps / Risks
- Resolve Green Wireless pitch and optional CTI keying via an exact-revision dimensioned CAD/BOM, not compatibility marketing
- Resolve null TagConnect pad counts from exact revision CAD if those pads are a future fixture target
- Confirm actual unit revisions, fitted population, underside clearance and contact cross-sections before fixture design
- Broad row geometry is not an electrical compatibility claim; some cape positions are internally tied on these boards
- Source files include several large complete manuals. Selected rendered pages and CAD/BOM extracts are also preserved for lightweight review

## Review result
Source and internal-consistency review complete. No independent physical test, no compatible-fit assertion, no invented keying or missing dimensions. Descriptive steps 1–6 complete for this bounded batch.
