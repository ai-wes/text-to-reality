# Repeatable board batch integration

The sole runtime catalog is `src/text_to_reality/data/boards.json`; its existing
`schemaVersion: 1` and `boards` list remain canonical. Research proposals are
source evidence until validated and merged. This CLI is a maintainer workflow;
it does not add remote MCP writes or change any agent settings.

Supply stable exact variant IDs; name/aliases; board/module kind; explicit
revision string or null; primary HTTPS evidence objects with `url`; separate
physical headers with ID, full-row pin_count, rows, nullable pitch/gender/shroud;
and excluded_header groups with a reason. Every group preserves original_header.
Every board preserves original_record plus source_record.file and an absolute
JSON pointer into a manifest-verified JSON file. Preserve source confidence,
pitch evidence and unresolved qualifications. Include all source headers and
auxiliary/other connectors and exposed pads, either normalized or explicitly excluded.

The manifest uses `files: [{path, bytes, sha256}]` relative to source-root.
If supplied, record_index, batches, and total_record_count must agree exactly
with verified source catalogs. Reject symlinks, traversal, duplicate JSON keys,
non-finite numbers, hash mismatches and source identity reuse. Source files are
never executed. Hashes in catalog_imports use indent-2 UTF-8 JSON plus a newline;
manifest file hashes refer to original byte buffers.

```bash
.venv/bin/python -m text_to_reality.cli import-boards research/headerBoards.proposed.json \
  --catalog src/text_to_reality/data/boards.json --source-root research \
  --manifest research/manifest.json --batch-id wave3-2026-10-06 \
  --normalize-source-format
```

Without `--output`, this prints validation/audit results and writes nothing.
Optional `--normalize-source-format` bridges source URL strings/cad_url objects,
source confidence and unknowns, research categories, and CAD revision objects.
Each adjustment is reported; exact original records remain untouched. A CAD
revision object stays evidence and actual board revision becomes null. This
never guesses pitch, population, gender, shroud, topology or qualification.

Prepare a candidate with `--output /tmp/boards.candidate.json`. To update the
canonical catalog, supply its exact current SHA-256 using
`--expected-output-sha256` and `--output src/text_to_reality/data/boards.json`.
An identical replay produces identical catalog bytes. Same-ID conflicts fail:
retain the old identity and resolve the source variant/revision before import.
All validation finishes before any write. Failed records must be recorded in a
quarantine report and corrected from source evidence, then retried. A partial
approved subset must retain each source pointer; the full manifest remains.

Ambiguous researched names/aliases return no selected board. Exact IDs are
explicit selectors. The original 19 broad family reference IDs have a named
legacy scope in catalog.py so unique sourced variants can supersede their broad
aliases; newly imported research cannot gain that scope. Source revision text
never verifies the actual sample revision. Fit gates and unresolved JIG model
choice still apply to every imported board. R29 and bus candidates gain no status.

After every accepted batch:

1. Save import report and raw research manifest/catalogs under docs/connector-library.
2. Run `.venv/bin/python -m pytest -q tests` including fresh stdio MCP checks.
3. Build a frozen candidate: `.venv/bin/python scripts/build_connector_candidate.py --output /tmp/new-candidate`.
4. Verify its manifest and installed-wheel resources outside the checkout.
5. Distribute the new content-addressed candidate; keep older candidates immutable.

Wave two: 76 accepted, zero quarantined, 151 total identities. The compact source
bundle is preserved under research-wave2, including original and normalized
proposals and adjustment report. Full evidence is referenced by Library ID and
its original hashes; large PDF/CAD sources are not claimed as locally retrieved.
Wave three: 57 accepted, zero quarantined, 208 total identities; research-wave3
preserves its compact sources and exact normalization/replay. Pololu image evidence
retains the exact original product URL; VREF/thermal access pads stay excluded.
Wave four: 46 accepted, zero quarantined, 254 total identities; research-wave4
preserves 80 main-row proposals and 206 excluded groups. Eight records have no
main-row proposal. Wave five: 36 accepted, zero quarantined, 290 total identities; 11 SBC records
retain multirow exclusions. PN532 retains its nonuniform nine-contact side row as
excluded with pitch null. Three photo-scoped SparkFun display descriptions were
enriched; two inconclusive display records stay unknown. Wave six adds eight SBC records, all excluded from single-row comb selection,
retaining 37 connector groups; 298 total identities. Wave seven adds 12 MB1137 B01 Nucleo-144 model records with zero main-row comb
proposals and 192 excluded groups, preserving mixed mating faces and 70-position
morpho connectors. Wave eight adds 10 exact factory-populated SKUs with 20 single male 2.54 mm rows
and 168 positions. Population remains a source-supported assembly fact; actual
fit, housing clearance and model approval stay gated. Held SKU 102010634 is absent.
All eight prepared accepted batches are integrated: 320 total identities,
301 research records plus 19 legacy family references. Future daily batches use
the same guarded workflow; see pending-batches.json. Package 0.1.0 remains a local
review version; content hashes distinguish batches. Public release requires a
new selected version and synchronized runtime pins as described in DEPLOYMENT.md.

## Separate descriptive enrichment

`enrich-boards` updates only existing normalized header gender/population strings.
It checks exact current-runtime record SHA, old field presence/value, unchanged
board/revision/SKU/assembly scope, row topology and literal hash-verified source
claims. Original record/header/provenance, installation flags, confidence,
qualification, model choice and aliases remain untouched. All changes validate
before the shared guarded atomic writer runs. No existing ID is reinserted.

The generic runtime patch is schemaVersion 1 with `updates`, each containing
board_id, expected_record_sha256, explicit scope and changes. A change contains
header_id, field (gender/population), before_present, before, after, source_record,
source_field_pointer and evidence_urls. The source field must be the exact
literal string on the same scope and row topology. A record hash uses indent-2
UTF-8 JSON plus newline; it is distinct from source canonical hashes.

The supplied photograph format can be used directly:

```bash
.venv/bin/python -m text_to_reality.cli enrich-boards \
  docs/connector-library/research-wave5/headerBoards.enrichment.proposed.json \
  --catalog src/text_to_reality/data/boards.json \
  --source-root docs/connector-library/research-wave5 \
  --manifest docs/connector-library/research-wave5/enrichment-source-manifest.json \
  --enrichment-id wave5-display-population-2026-10-06 --photo-source-format
```

This command is read-only without --output. Photo preparation computes each
runtime guard; it never substitutes a source record hash. Validation checks the
original file/record/header hashes, sealed wave-four proposal, literal update
pointers, unchanged scope, exact old values, primary URLs and unique hashed
image. The supplemental manifest includes the original wave-five files and
preserved old-source guards without altering either sealed original manifest.

Root catalog_enrichments events preserve old presence/values, new source update,
original source records, image metadata, before/after hashes and request hashes.
Identical enrichment replay requires the exact current postimage, intact audit
and reconstruction of the preimage; audit edits and target drift reject. An
earlier enrichment replay after a later change to that board rejects; rebuild
from the pre-enrichment state and replay ordered requests. Raw insertion replay
after enrichment deliberately retains same-ID conflict rejection. Rebuild by
importing all source batches into the seed catalog, then apply enrichments in
order. No audit is treated as permission to bypass the insertion validator.
