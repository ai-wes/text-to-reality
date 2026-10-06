# Package format

A project is a folder created by `create_project`. Write files anywhere inside it,
then record them under a stage with `record_files`. `check_package` reads the
folder's `reality.json` and these files.

| Stage | Required |
| --- | --- |
| requirements | `brief.md` (created for you) |
| parts | `bom.json` |
| mechanical | CAD source and STL/STEP/3MF exports, or not applicable with a reason |
| electronics | `wiring.json`, or not applicable with a reason |
| firmware | source and setup notes, or not applicable with a reason |
| assembly | a guide: `.md`, `.html` or `.pdf` |
| testing | a checklist of what to test and what passing looks like |

## bom.json

A list of parts:

```json
[
  {"part": "Seeed Studio XIAO ESP32S3 (pre-soldered headers)", "quantity": 1, "owned": false},
  {"part": "1.44 in ST7735 SPI display, 8-pin header", "quantity": 1},
  {"part": "JIG_ wire connector, small, 7-pin", "quantity": 2, "jig_part": "jig-connector"},
  {"part": "Female-to-female jumper wires, 10 cm", "quantity": 8},
  {"part": "Printed body (body.stl)", "quantity": 1},
  {"part": "USB-C data cable", "quantity": 1}
]
```

`part` and a whole-number `quantity` are required. `jig_part` must be an id from
`find_jig_parts`. Add `url`, `notes` or `owned` when useful.

## wiring.json

```json
{
  "connections": [
    {"from": "XIAO D1", "to": "Display SDA", "color": "blue"},
    {"from": "XIAO 3V3", "to": "Display VCC", "color": "red"}
  ],
  "connectors": [
    {"pins": 7, "size": "small", "plugs_onto": "XIAO left header row (D0-D6)"}
  ]
}
```

List every wire. Give each a color so the picture guide can say "the blue wire".
Each connector's `pins` is the length of the whole header row it plugs onto. If you
use JIG_ connectors, `bom.json` needs a row with `"jig_part": "jig-connector"`.

Those short examples show the base format, not an accepted connector assembly.
Read [connector usage](connector-usage.md) before header wiring. Add exact
endpoint `boards` selections and each connector's `board`, `header`, full-row
`pins`, `quantity`, board/model revisions, measured housing/model envelope,
orientation/pin-one map, engagement, paired hashes, mount/clearance, print
conditions and approved illustrated retention protocol. The connector BOM
row also needs `pins`, `size`, `model_revision` and `unit: "assembly"`; its
quantity must equal functional assemblies, with rounded store packs separately.

For other wiring, declare `connector_scope: {"kind": "no_header_wiring",
"reason": "..."}`. For row-specific alternatives, record
`connector_exceptions` with exact resolved board name, `header_id`, `reason`,
`alternative` and `evidence`. A documented alternative does not approve a JIG
model or qualify a power path. The current unresolved connector model blocks
complete JIG assembly packages; planning files may still be recorded.

## Firmware

Include the source, the exact board setting, how to load it (or that it comes
preloaded), any settings to change, and what the device shows when it's working.

## Testing

A short checklist, in order: what to look at, what a pass looks like, and what to
do if it fails. Mark tests that need the physical build as such.
