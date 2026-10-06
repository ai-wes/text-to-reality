# ST and PJRC disjoint third batch
## Charter
Goal: verify 16 further exact board records, disjoint from earlier 20 ST/PJRC records and original archive.
Scope / Object / Subject: development-board connectors / remaining MB1136 Nucleo-64 plus legacy Teensy / individually documented order codes and complete physical connectors.
Type: descriptive. Working knowledge established in previous batch; source-reuse allowed only for explicitly covered variants.
Questions: exact-model connector mapping; revision limits; legacy Teensy physical row and auxiliary counts.
## Canonical sources
Rank 1: ST UM1724 Rev 17 and PJRC exact product pages plus dimension drawings.
Rank 3: prior JSONs for duplicate checks only.
## Findings ledger
F1. UM1724 Rev 17, pp.1,7 names all fourteen added Nucleo order codes. Model-specific Arduino tables are at pp.38–43,46–47,50–52; morpho tables pp.54–58,60–61,63. Every connector is counted through its full numbered range: CN5=10, CN6=8, CN8=6, CN9=8; CN7 and CN10=38 each, 2x19. No electrical signal equivalence is asserted among models.
F2. The same manual pp.14–16,19–20 documents common physical geometry and auxiliary positions. Female Arduino and male morpho connector types are explicit in sections 7.13 and 7.14. Auxiliary footprint population/gender/pitch are retained as null where evidence is insufficient. Every connector remains discoverable independently.
F3. PJRC Teensy 2.0 product page explicitly distinguishes bare-board and installed-header variants. The linked mechanical drawing has two 12-position edge rows, one separate five-hole transverse row and two isolated inner holes. Pinout card identifies the isolated holes as PE6 and AREF. The holes total 31, not the product's 25 signal-I/O count.
F4. PJRC Teensy++ 2.0 bare-board product and mechanical drawing show two 20-position edges, three rear power/reset holes and eight interior Port A holes. The interior pattern is visibly irregular (4+3+1 horizontal hole counts in the dimension drawing), not a standard 2x4 socket footprint. The tiny crystal pads are excluded. Physical hole total is 51, not the 44 signal-I/O count.
F5. JSON has 16 unique boards and 219 separately represented connector/auxiliary-footprint records. IDs do not intersect the earlier 20-board ST/PJRC batch. All records remain fit-unverified; no row subsets of two-row morpho connectors are promoted to separate comb candidates.

## Scope filter
Excluded digital I/O totals as substitutes for physical hole counts. Shared MB1136 geometry is used only for exact models explicitly named and mapped in UM1724. Reused manufacturer evidence is not described as an independent new source.

## Object filter
Assembly revision remains unknown unless documented for a specific supplied unit. Nucleo female connectors and complete male 2x19 morpho connectors remain discoverable but unqualified. Bare Teensy footprints do not become installed male headers. Teensy++ Port A cluster is kept irregular rather than forced into a convenient 2x4 geometry.

## Conclusions
Sixteen further exact models are described without overlap with the prior ST/PJRC batch (F1–F5). Main header geometry is source-backed; small auxiliary population and exact-unit revisions remain explicitly unresolved (F2). Physical jig fit is not established (F5).

## Next steps / Risks
Match an actual unit's board revision and population before physical fixture selection. Confirm underside obstructions, pin cross-sections, insertion depth and clearances. The irregular Teensy++ interior group requires its own coordinate-aware fixture review.
Next candidate families for a separate research pass: STM32F3DISCOVERY, STM32L-DISCOVERY, 32L0538DISCOVERY, NUCLEO-G031K8, NUCLEO-G071RB, NUCLEO-G431KB, NUCLEO-G474RE, NUCLEO-U031R8. No counts for these unresearched candidates are asserted here.

## Review result
Source and internal-consistency review completed by the researcher; not an independent physical test. The structured catalog preserves all known uncertainty. Descriptive research steps 1–6 complete for this batch.
