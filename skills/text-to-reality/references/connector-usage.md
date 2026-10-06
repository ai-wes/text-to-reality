# JIG connector usage

Retrieve `connector_guidance` before any board-to-board header wiring. The same
canonical content is available at `text-to-reality://connectors/usage-rules`
and `text-to-reality://connectors/agent-guide`. `board_headers` reads the
existing board catalog; research evidence and family aliases are row references,
never approval for fit or a pin map.

Disclose JIG in the brief and BOM. JIG retention assemblies are the required
default for compatible board-to-board header wiring. Record the exact row,
reason, evidence and alternative for exceptions. Never force a comb onto a
female, bare, shrouded, multirow, wrong-pitch or incompatible header. A printed
retainer does not qualify contacts, wire ratings or a power path. A bare board
is an installation task, not a solder-free mating connector.

## Select the whole row

One installed 1×7 row needs one 7-pin assembly, even when only three pins carry
wires. A XIAO ESP32 with two installed 1×7 rows needs **two 7-pin assemblies**.
Repeat at each board endpoint. Leave unwired positions electrically empty.
Never count only GPIOs, omit ground/power/NC positions, or shorten the comb.
Separate opposite edge rows are not a contiguous multirow header.

Require exact board variant/revision, installed male gender, single-row
topology, unshrouded body and 2.54 mm pitch. `connectors_for_boards` preserves
full-row counts but returns `row_checks`, `model_choice` and a planning-only
status. These gates matter even when it returns pack quantities. Text or null
metadata remains unresolved. An alias can find a board, but cannot resolve an
ambiguous revision or approve housing fit.

One assembly is one matched base plus its matching retainer. Count one base
and one retainer per assembly after selecting an exact model. The existing
store categories are five assemblies per pack for 1–8 pins and two per pack
for 9–22 pins. Round up separately by pin count, housing profile and model:
`ceil(assembly units / pack units)`. Two 7-pin assemblies need one 5-pack and
leave three spares; six need two 5-packs. Functional BOM quantities remain
assembly units, and packs/spares are a separate procurement calculation.
The 9–21 categories are printed to order, not live stock or approved CAD.
Verify the current SKU and pack size before purchase.

## Exact design remains unresolved

The AUTO_IOT universal adapter README describes a production strip alongside
older clasp instructions and new clip test candidates; local strip meshes
are archived. The machine record snapshots exact source hashes and sets
`approved_model_revision` and `retention_motion` to null. No exact current
approved lineup and protocol was found. Do not choose a strip, clasp, clip,
historical Agent Meter lock, or mix their latch motions. Do not manufacture
operator or physical approval from a caller's `approved` field. Stop
model-specific assembly until the canonical record binds an exact approved
version, paired file hashes, housing envelope and retention protocol.

The XIAO battery adapter **R29 is an untested candidate**, not a qualified
power path. New `bus_small`/`bus_large` blocks are separate commoned rails:
one input to multiple electrically common outputs, assembled with soldered
loose pins and copper wire. They are test-print candidates, not independent
signal combs, not solder-free assemblies and not qualified current paths.
Never substitute one automatically for independent signals or qualified power.

## Retrieve CAD and verify fit

`find_jig_parts` returns catalog references and missing asset status. This
standalone MCP does not bundle or download CAD. Obtain the exact approved
source/manufacturing pair, SHA-256, license, board pin map, mount, clearance
volume, assembly view and illustrated retention protocol from the owner or
provider. Missing mount/clearance models remain unresolved. Preserve datums,
fixed fitting dimensions and exact revisions. Never globally scale a comb to
hide a mismatch. Check neighboring pins, row ends, USB, enclosure, wire route,
engagement, strain relief and release access.

Use the existing `bom.json` and `wiring.json` formats. Extend each connector
with `header` (catalog row fields, including `preinstalled`), `board_revision`,
`model_revision`, `housing` and `model_envelope` measurements, `orientation`,
`contact_engagement_evidence`, `paired_model_hashes`, `mount_source`,
`clearance_geometry`, `retention_protocol` and `print_conditions`. Housing
measurements use `width_mm`, `length_mm`, `height_mm`, `wire_diameter_mm`.
Orientation names `pin_one`, `board_side`, `mating_direction` and ordered
`ordered_pin_ids` for every physical position. Record file paths and hashes;
opaque strings alone do not establish physical qualification.

Each wire needs exact `from`/`to` pin/GPIO labels, color/label, voltage and
function. Power/ground paths need expected current, conductor/contact current
limits, polarity and protection evidence. Keep wire lengths and routing in the
diagram/guide. Do not infer a net from wire color, rated current from nominal
pitch, or electrical isolation from a printable mesh.

## Retention sequence and outputs

1. Disconnect all power. Verify exact endpoint revisions, board side, pin one,
   net map, crimp contacts and installed header solder joints.
2. Measure housings, wire insulation and contact engagement against the exact
   model envelope; check mount, clearance, insertion and release access.
3. Retrieve the approved model's illustrated loading/retention/release
   protocol. **Stop here while model choice remains unresolved.**
4. After resolution, follow that protocol's loading order before mating to
   headers. Retain housings, leave unused positions electrically empty, label
   wires, mate in the permitted direction and provide strain relief.
5. Record unpowered continuity, isolation, polarity and physical retention
   results. Apply power only after applicable electrical qualification.

Deliver functional BOM quantities, exact ordered full-row diagrams for both
endpoints, and model-bound picture instructions. Show board side/pin one,
endpoint revisions, GPIO/net labels, empty positions, voltage/polarity, wire
labels/lengths, orientation, mounts and clearance views. Include housings,
contacts, wires and installed headers as well as base/retainer assemblies.
Record JIG dependency, exceptions, model revision, pack rounding and spares.
Catalog counts alone cannot supply those outputs.

`check_package` shares the canonical connector checks with the finder and
will report missing full-row coverage, housing/orientation evidence, current
limits, BOM assembly quantities and unresolved model approval. It validates
software records, not physical operation. Record the actual physical protocol
for insertion, retention, release, fatigue, insulation and continuity. Any
change to board/header/housing/wire/model/mount/pin map requires `new_revision`
and updated BOM, CAD, diagrams, instructions and tests.
