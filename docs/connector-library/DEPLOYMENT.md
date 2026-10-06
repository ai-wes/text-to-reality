# Connector library release path

The actual project is `/home/wes/PROJECTS/text-to-reality`, on local `main` at
baseline `db93bcd`. The checkout had no uncommitted changes and no configured
Git remote. README/plugin metadata identifies `https://github.com/ai-wes/text-to-reality`;
this does not establish remote contents or authorize publishing.

This change extends Claude's existing local MCP and plain JSON package formats.
It does not add a second server, AUTO_IOT backend, CAD or firmware. The original
AUTO_IOT attempt was preserved separately and removed from that working tree.

## What ships

- `src/text_to_reality/data/connector_usage.json`: canonical machine rules,
  full-row selection, pack rounding, dependency, exceptions and source-bound
  unresolved model choice. R29 is untested. Bus candidates common outputs and
  require soldering; they cannot replace signal combs or qualified power paths.
- `skills/text-to-reality/references/connector-usage.md`: readable canonical
  guide, also included as package data in the wheel. The skill routes to it.
- `connector_guidance` and three resources in the existing MCP:
  `text-to-reality://connectors/usage-rules`, `/agent-guide`, `/boards`.
- Existing `connectors_for_boards`: strict counts, full rows, per-row fit issues,
  excluded incompatible headers, functional BOM draft and row-diagram inputs.
  Packing is a separate procurement calculation. It never approves physical fit.
- Maintainer `enrich-boards` CLI: separate exact-record/field/source guards for
  descriptive gender/population updates; originals and all qualification gates
  preserved. See BATCH-IMPORT.md.
- Existing `check_package`: exact row coverage, topology/envelope/orientation,
  current limits, dependency exceptions, BOM quantity checks and unresolved
  model approval gates. Old counts-only JIG packages now fail deliberately.
- Existing `boards.json`: 320 entries. Wave eight adds 10 exact factory-populated SKUs, wave seven adds 12 exclusions, wave six adds eight exclusions, wave five adds 36, wave four adds 46, wave three adds 57, and wave two adds 76 research-only identities;
  see BATCH-IMPORT.md and pending-batches.json for the validated importer workflow.
  The first wave contained 75 entries. All 20 legacy IDs remain; 56 research
  records add 55 identities and enrich the existing Pico identity. Original
  records, source URLs, provisional data and excluded auxiliary groups remain.

`research-source-manifest.json` is the original research bundle manifest; all
41 listed files were verified before import. The source catalogs copied under
`research/` preserve raw research. The complete PDF/image bundle is a separate
release evidence archive, not runtime package data or physical qualification.

## Local activation after source integration

The existing `.venv` uses this repository's editable source. Test in a **new
process**; an already-running agent must restart its MCP to see new code.

```bash
cd /home/wes/PROJECTS/text-to-reality
.venv/bin/python -m text_to_reality.cli mcp --dir /absolute/path/to/private-builds
```

Register that command in the intended agent's local MCP settings only after
the installation scope is selected. A local configuration template is supplied
with the release. The existing Claude/Codex/Cursor manifests pin
`text-to-reality==0.1.0` through `uvx`; those commands continue to fetch that
published runtime and will not pick up source edits automatically.

## Wheel and portable installation

The wheel includes boards, JIG parts, machine policy and the exact canonical
Markdown guide. The source distribution also includes the skill. The root-only
`.gitignore` rule prevents generated project folders from being committed
without accidentally excluding the skill from source distributions.

For an isolated local runtime, create a virtual environment, install the wheel
and its declared `mcp>=2.3,<3` dependency, then register its Python command with
`-m text_to_reality.cli mcp --dir ...`. Install `skills/text-to-reality` in the
selected agent's skill directory, preserving any local changes. No account,
API token, provider credential or paid service is needed.

The build retains version `0.1.0` as a local review candidate. Its SHA-256 and
release manifest distinguish it from an older wheel. **Do not publish or
overwrite an existing 0.1.0 release.** A public release needs a selected new
version, synchronized plugin runtime pins, confirmed destination/repository
and explicit publication scope. No push, merge, PyPI upload, agent-settings
write or public deployment is included here. This MCP has stdio transport;
no hosted MCP endpoint is implemented by this change.

## Acceptance and remaining physical gates

Run `pytest tests` in the existing development environment. Checks include a
fresh stdio client retrieving canonical resources and the XIAO two-7-pin
mapping while fit issues remain enforced; candidate approval flags do not
bypass unresolved model selection. Validate installed-wheel resources in a
new process outside the source directory, and verify the release manifest.

Release-ready software is not a qualified physical connector lineup. Before
manufacturing directions can be delivered, the owner must bind the canonical
record to exact approved model/source hashes, base/retainer pairs, acceptance
envelopes, mount/clearance files and illustrated retention protocol. Physical
fit, engagement, insulation, retention, release, fatigue and electrical ratings
remain protocol/evidence requirements. No latch motion or approval was invented.

## Consolidated acceptance

Eight research waves supply 301 exact source records. The runtime has 320
identities: those records plus 19 original broad family references. Three
source-bound photo enrichments change only six normalized descriptive fields;
all prior originals remain intact. All supplied accepted records are integrated; none
are quarantined. Wave-eight held SKU 102010634 is not imported because its CAD
model mapping remains unresolved. Factory population is an assembly fact, never
connector-fit approval. The final regression suite and installed-wheel probe are
recorded in verification.json in the content-addressed release candidate.

Software is integrated and tested locally. Actual source activation uses the
editable interpreter command above; published uvx pins remain unchanged. A
public release still needs destination/version/scope, and physical deployment
still needs exact approved connector-model/hash binding and fit/electrical
evidence. No latch sequence, connector approval, R29 qualification, Git push,
agent-settings update or hosted endpoint is implied by catalog completeness.

## Compact runtime alongside full evidence

Build with `.venv/bin/python scripts/build_connector_candidate.py --output /tmp/new-candidate --compact-runtime`.
The full package retains its source distribution and research evidence; the
separate compact archive contains the identical tested wheel, complete skill,
deployment guidance, verification and source-snapshot identity. It omits full
research assets and editable source/tests. Each archive has its own SHA-256
manifest; the compact manifest binds the full release manifest and archive hash.
Use the compact package for local installation and the full package for source
review and evidence. Neither activates agent settings or publishes the runtime.

## Authorized source closeout — 2026-10-06

The owner subsequently authorized committing and pushing completed source work.
The existing `origin` is `https://github.com/ai-wes/text-to-reality.git`; its main
head matches local baseline `ca8e665ab44b4c479098104d43638b7d982fb479`.
The source closeout stays on `main` and retains all existing owner commits.
Fresh regression validation passes all 127 tests with 320 catalog identities.
The previously verified installed-wheel receipt is preserved in
`verification-2026-10-06.json`. This source push does not publish a package,
change agent settings, or activate a hosted service.

The saved installed-wheel receipt is historical. Its board catalog matches this
source checkout, but its connector rules precede the owner's current committed
rules. The fresh 127-test source run exercises the current rules. Rebuild an
installation candidate from the committed source before choosing local runtime
activation; existing candidate archives are retained unchanged.
