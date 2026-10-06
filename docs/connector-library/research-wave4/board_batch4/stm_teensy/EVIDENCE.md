# Modern ST board expansion
## Charter
Goal: continue disjoint growth with modern G0/G4 Nucleo and additional Discovery boards; finish only verified records, never inflate to a target count.
Scope / Object / Subject: development board fixtures / exact ST order codes outside previous batches / complete connector geometry and population.
Type: descriptive; prior family knowledge does not establish a new board's layout.
Canon: rank 1 ST exact board manuals, schematics and mechanical figures. Questions: counts, rows, pitch, gender/population, debug/auxiliary separation, revision limits.
## Findings ledger
F1. UM2591 Rev 2 (April 2026), pp.8–10,16–17: NUCLEO-G031K8 MB1455 has CN3/CN4 male 15-position rows; CN2 five-hole reserved footprint is visible in the top/bottom photographs. JP1 is separate. Row pitch is based on explicitly stated Arduino Nano V3 compatibility; inter-row separation 15.24 mm is dimensioned. No physical fixture inference is made.
F2. UM2397 Rev 2, pp.8–10,19–22: NUCLEO-G431KB MB1430 has male CN3/CN4 15-position rows. Page 9 explicitly identifies a 2.54 mm shunt across two existing CN4 positions; it is not another connector. CN2 has four visible holes arranged irregularly and is explicitly not fitted. This differs from MB1180/MB1455's five-hole reserved layout.
F3. UM2324 Rev 5, pp.1,7,12–16,30–34: NUCLEO-G070RB/G071RB/G0B1RE MB1360 order codes share the documented mechanical family. Main Arduino female connectors are 10/8/6/8; morpho male connectors are complete 2x19. Debug output is CN11 (six), debug-isolation row CN4 (four), with separate power and auxiliary footprints. Do not reuse MB1136 connector IDs.
F4. UM2505 Rev 7 (May 2026), pp.3,7,9–13,28–33: G431RB/G474RE/G491RE MB1367 have 10/8/6/8 female Arduino plus two 2x19 male morpho connectors. JP5 is a complete 2x4 power-selector block and JP8 a three-position reference selector. CN4 is described as MIPI10 but is shown with a 14-position STDC14-compatible SMT footprint: the catalog says footprint, null population/gender/pitch, never a confirmed fitted 14-pin header.
F5. UM1570 Rev 7, pp.14,17,23–33: STM32F3DISCOVERY MB1035 has two 50-position male 2x25 rows. Separate CN3 SWD=6 and CN4 isolation=4. Mechanical figure labels 2.54 mm row spacing and preserves complete headers.
F6. UM1775 Rev 6, pp.16,20–22,26–32: 32L0538DISCOVERY MB1143 has two male 25-position main rows (P2/P3), 60.96 mm over 24 intervals. CN1 NFC=2x4, CN5 SWD=6, CN4 debug isolation=4; JP2 and JP3 explicitly require soldering headers, so are unpopulated. JP4 is a three-position current selector. CN6 remains an auxiliary with unresolved population/pitch.
F7. UM1079 Rev 5, pp.6,12,14,17,19,27–31: exact STM32L152RC-based order code 32L152CDISCOVERY has two male 28-position expansion rows; 68.58 mm over 27 intervals. Separate six-position SWD and four-position isolation headers, three-position current and reference jumpers, and a DIP28 female LCD socket are represented. The obsolete RB-based STM32L-DISCOVERY was not silently merged.
F8. UM0919 Rev 2, pp.10,13–21: STM32VLDISCOVERY MB913 has two male 28-position rows and separate six-position P3. SWD CN2 is only four contacts, not the six used on later Discovery boards. Main pitch follows 68.58/27 and P3 follows 12.7/5 mm.
F9. Catalog validation: 12 distinct added models, 129 connector/footprint records, no overlapping IDs with prior ST/PJRC batches. These are completed source-backed records rather than padding to a larger target.

## Scope filter
Rejected older-Nucleo auxiliary maps for modern boards. Rejected GPIO totals as header counts. Known non-pin-header sockets and surface footprints are explicitly typed rather than promoted into straight male candidates.

## Object filter
Keep irregular reserved footprints, SMT debug footprints, female sockets and complete multi-row blocks intact. Generic Arduino compatibility supports stated pitch but does not prove jig fit. Exact supplied-unit board revisions remain null.

## Conclusions
Twelve further exact boards are cataloged (F1–F9). Modern board connector-ID and population differences are retained rather than hidden by family templates. All comb_qualified values remain false and physical fit remains unverified.

## Next steps / Risks
- Confirm exact unit revisions, header population, pin shape and fixture clearance
- Obtain exact-revision BOM for auxiliary gender/population nulls and verify CN4 physical connector population on MB1367
- Inspect any LCD removal/access requirements before treating its socket as a fixture target
- Next disjoint source candidates: NUCLEO-C031C6, NUCLEO-C051C8, NUCLEO-C071RB, NUCLEO-U031R8, NUCLEO-U083RC, STM32F401C-DISCO, STM32F429I-DISC1, NUCLEO-F429ZI, NUCLEO-F767ZI; no unverified connector counts are asserted

## Review result
Internal source/consistency review, not independent physical testing. Unknown auxiliary attributes remain null. Main model counts are supported by exact-manual connector tables or dimensioned manufacturer drawings. Descriptive research steps 1–6 complete.
