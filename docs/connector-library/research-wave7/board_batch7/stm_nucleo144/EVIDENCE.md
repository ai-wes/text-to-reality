# Nucleo-144 complete connector topology
## Charter
Goal: one bounded batch of twelve explicitly documented MB1137 order codes, with exact whole Zio/morpho connector topology and fitted socket faces.
Scope / Object / Subject: board fixture dictionary / STM32 Nucleo-144 MB1137 / exact UM1974 Rev 11 order codes and documented assembly variants.
Type: descriptive; never reuse Nucleo-64 header sizes or assume coverage of future marketed revisions.
Canon: originating ST UM1974 Rev 11 (August 2025), connector pin tables, mechanical drawings, population wording and board revision history. Manufacturer schematic/BOM where reachable for corroboration.
Questions: whole contact count, rows/pitch, top/bottom gender, default population, separate auxiliary/debug interfaces, bounded revision applicability.
## Findings ledger
F1. UM1974 Rev 11, pp.1,7,80 explicitly covers twelve order codes: F207ZG, F303ZE, F412ZG, F413ZH, F429ZI, F439ZI, F446ZE, F722ZE, F746ZG, F756ZG, F767ZI and H743ZI. Board history lists MB1137-<part>-B01 for each. Records are scoped to those assemblies, not all revisions sold under similar names.
F2. Section 7.14 p.37 explicitly states CN7/CN8/CN9/CN10 are female on top and male underneath. Inspected manufacturer p.1 and p.14 photographs corroborate fitted pass-through/socket topology. One connector is recorded once with two mating faces, never doubled by top/bottom contacts.
F3. Complete Zio counts are CN7=20 (2x10), CN8=16 (2x8), CN9=30 (2x15), CN10=34 (2x17). Exact-model pin tables: F207 pp.38–41; F303 pp.42–45; F412 pp.46–48; F413 pp.49–52; F429/F439 pp.53–56; F446/F722 pp.57–60; F746/F756/F767 pp.61–65; H743 pp.66–68. Arduino-designated subsets are signal assignments within these physical blocks, not separate headers.
F4. Section 7.15 p.69 calls CN11/CN12 male-header footprints OFF by default. Tables 21/22 pp.70–72 enumerate through pin 70 on each: complete 2x35 interfaces, unpopulated. The catalog does not pretend they ship as installed male headers. Intended male installation is retained separately from null actual gender.
F5. Mechanical figures pp.15–16 establish 2.54 mm/100 mil grid and separate full connector blocks. The main ST Zio and morpho geometry is source-backed; surrounding fixture clearance and tolerances are not tested.
F6. CN6 debug is six contacts (Table 5, p.20). CN4 has four contacts in one row with two shunts (layout and Table 4); JP3 is a complete 2x3 power-selector (Table 8, p.23). Small CN2/CN3/JP1/JP2/JP4 footprints are preserved with unresolved pitch/gender/population. Mechanical Figure 6 labels CN5 TX/RX and shows two separate contacts; pitch/population/gender remain unresolved. JP5 is separate two-contact current measurement.
F7. Manual p.80 explicitly distinguishes original NUCLEO-H743ZI/MB1137 from replacement NUCLEO-H743ZI2/MB1364. H743ZI2 is outside this batch. Packaging changes and MCU silicon revisions do not create additional board records.
F8. Twelve records, 192 separate connectors/footprints; IDs unique and disjoint from previously researched ST/PJRC and SBC model IDs. Known row sums validated. All comb_qualified false and fit_status unverified.

## Canonical source
https://www.st.com/resource/en/user_manual/dm00244518-stm32-nucleo-144-boards-mb1137-stmicroelectronics.pdf
UM1974 Rev 11, August 2025. Original PDF, extracted text and selected inspected page PNGs are preserved.
ST's current product listing independently links the same manual revision for NUCLEO-F429ZI: https://www.st.com/content/st_com/en/products/evaluation-tools/product-evaluation-tools/mcu-mpu-eval-tools/stm32-mcu-mpu-eval-tools/stm32-nucleo-boards/nucleo-f429zi.html

## Scope filter
Rejected Nucleo-64 38-contact morpho assumptions. Rejected separate Arduino-subset records, duplicated top/bottom contact counts and invented package/MCU-revision board variants. This batch is exactly the twelve documented order codes.

## Object filter
Scoped every record to MB1137 B01 as listed by the manual. Pass-through mixed gender is preserved; unpopulated outer footprints are not promoted to fitted headers. H743ZI2 is explicitly excluded. Unknown auxiliary pitch, population and gender remain null.

## Conclusions
Twelve exact MB1137 B01 assemblies are ready for dictionary discovery (F1–F8). Each has four fitted pass-through two-row Zio blocks (20/16/30/34) and two unpopulated two-row 70-position morpho footprints. None is a complete single-row-comb target. Actual unit revision matching and physical clearance remain necessary.

## Next steps / Risks
- Match actual board's MB1137 B01 marking; source does not guarantee every later marketed revision
- Resolve remaining auxiliary nulls from exact assembly BOM/CAD if needed for a fixture
- Preserve mixed mating faces and default unpopulated morpho state during normalization
- Verify underside access, contact cross-section, pin length and component clearance physically

## Review result
Source-backed and internally validated. No physical jig fit testing, no inferred future-revision coverage and no row-count inflation. Descriptive research steps 1–6 completed for this bounded batch.
