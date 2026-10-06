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
- Existing `check_package`: exact row coverage, topology/envelope/orientation,
  current limits, dependency exceptions, BOM quantity checks and unresolved
  model approval gates. Old counts-only JIG packages now fail deliberately.
- Existing `boards.json`: 75 entries. All 20 legacy IDs remain; 56 research
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
