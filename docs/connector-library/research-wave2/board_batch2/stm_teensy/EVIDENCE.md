# STM32 and Teensy header expansion
## Charter
Goal: 15–20 exact boards absent from the prior archive, with physical headers individually represented and no asserted jig fit. Knowledge depth: working; family layouts require revision-specific manufacturer verification.
Scope / Object / Subject: development-board connectors / ST Nucleo and Discovery plus PJRC Teensy / individual ordered board variants and each complete connector.
Type: descriptive because the required schema and physical-header questions are already defined.
Q1: Which exact models and revisions share documented layouts? Q2: What are connector pin count, row count, pitch, population and gender? Q3: Which auxiliary connectors must be separated and which claims remain unknown?
## Canonical sources
1. ST official user manuals, schematics and product pages: originating source for exact board assemblies and connector tables.
1. PJRC official product pages, dimension drawings, pinout cards and schematics: originating source for Teensy layouts.
3. Supplied prior catalog: deduplication only, never independent physical evidence.
## Research progress
- [x] 1 Canon ranked
- [x] 2 Charter recorded
- [x] 3 Descriptive type read; ledger maintained below
- [x] 4 Scope filter
- [x] 5 Object filter
- [x] 6 Conclusions and risks

## Findings ledger
F1. UM1956 Rev 6 (March 2025), pp. 1, 22–30, 38: eight exact MB1180 order codes are covered. Each CN3/CN4 pin table has positions 1–15. Figure 5, p.14, gives 2.54 mm pitch. MB1180 schematic C.1 labels both connectors Header 15X1_male; p.1 photograph shows bottom-mounted populated rows. Current manual assembly history is retained individually; the older schematic supports type only, not current assembly equivalence.
F2. UM1956 pp.12–14 and MB1180 schematic sheet 3: CN2 reserved SWD is a five-contact footprint on a keyed two-row arrangement, not six contacts. Pitch is deliberately null. JP1 is a solderable current link rather than an assumed installed header and is excluded.
F3. UM1724 Rev 17 (September 2025), pp.38,44–45,48–49,53–63: F401RE, F411RE, F446RE and L476RG use CN5 10, CN6 8, CN8 6, CN9 8 female contacts and CN7/CN10 complete 38-contact male 2x19 connectors. Mechanical drawing p.16 establishes the 2.54 mm grid. Individual assembly revisions remain null; MB1136 is not itself a revision.
F4. UM1724 pp.14–16,19–20: debug CN4 is a separate six-contact row. CN2 is a 1x4 row with two shunts, not 2x2. Small auxiliary footprints are preserved independently with unknown population/gender/pitch where the manual illustration alone does not establish those facts.
F5. UM1525 Rev 2 pp.20,36–38: STM32F0DISCOVERY MB1034 B-00 has two male 33-contact single rows; 81.28 mm over 32 intervals gives 2.54 mm. The schematic explicitly identifies B-00 as the 33-position variant. Earlier A-00 is not merged. CN3 SWD, CN2 debug links, JP1 UART and JP2 current-measurement positions are separate. Note: ST's downloaded URL has a misleading stm32f3discovery filename; the actual PDF title and pages explicitly say UM1525/STM32F0DISCOVERY.
F6. UM1472 Rev 9 pp.7,15,19,25–31: STM32F407G-DISC1 is the exact order code; P1 and P2 each have 50 contacts in 2x25 rows. 60.96 mm over 24 intervals gives 2.54 mm. Male designation is explicit. Revision-dependent component changes exist; PCB assembly revision stays null. The older STM32F4DISCOVERY name is retained only as a search alias identifying the product lineage.
F7. PJRC official product pages and linked mechanical drawings: Teensy LC/3.2/4.0 have two separate 14-position edge rows; 3.5/3.6/4.1 have two 24-position edge rows. Each also has a separate transverse five-hole row and isolated VUSB hole. The 2.54 mm pitch is drawn directly. These records use bare-board products, so the holes are unpopulated and gender is null; these are not automatically male headers.
F8. PJRC drawings: LC/3.2/3.5/3.6 have a separate inner three-hole group. 3.5/3.6/4.1 have an additional five-hole row (USB-host location; the 3.5 electrical use differs). 4.1 has a separate 2x3 Ethernet footprint at 2 mm. No underside SMT pads, test points, USB sockets or microSD socket contacts are converted into headers.
F9. The earlier 56-board research archive contains no exact board names in this batch. JSON validation confirmed 20 unique board IDs, positive contact counts and consistent row sums; no jig-fit assertion is made.

## Scope filter
GPIO, processor package pin counts, and total digital-I/O counts were discarded as connector evidence. Populated and bare-board variants remain distinct. All pin counts represent complete physical connectors or clearly identified separate footprints.

## Object filter
Discarded automatic comb qualification for male single rows: surrounding-component clearance, insertion depth, pin cross-section, assembly orientation and physical fit were not measured. Multi-row, female and 2 mm structures stay discoverable with comb_qualified false. Restrict STM32F0DISCOVERY to B-00; do not propagate its 33-contact count to revision A. The 4.x component revision history does not establish the physical revision of an arbitrary user's board.

## Conclusions
- 20 exact boards and 127 separately modeled header/auxiliary footprint records are present in stm_teensy_headers.json (F1–F9)
- Primary source PDFs, extracted text, PJRC HTML and inspected mechanical drawings are preserved alongside the catalog (F1–F8)
- Every record retains fit_status unverified and comb_qualified false; no fabrication tolerance or tested-fit claim is implied (F9, object filter)

## Next steps / Risks
- Match the actual board's assembly markings and installed headers before jig selection
- Auxiliary footprint gender/population/pitch nulls require exact-revision BOM or direct board inspection; they are not silently inferred from the main headers
- Female headers and 2x19/2x25 connectors need a distinct fixture strategy
- Next disjoint candidates: NUCLEO-F030R8, F070RB, F072RB, F091RC, F103RB, F302R8, F303RE, F334R8, F410RB, L010RB, L053R8, L073RZ, L152RE, L452RE; Teensy 2.0 and Teensy++ 2.0. These are candidates, not yet verified records

## Review result
Source-backed descriptive geometry with explicit qualification limits. This was a source and internal-consistency review by the author, not an independent physical validation. Research progress steps 1–6 are complete for this bounded batch.
