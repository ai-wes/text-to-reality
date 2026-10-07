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
  {"part": "Seeed Studio XIAO ESP32S3 (pre-soldered headers)", "quantity": 1},
  {"part": "0.96 in SSD1306 I2C OLED, 4-pin header", "quantity": 1},
  {"part": "JIG_ connector, small, 7-pin", "quantity": 2, "jig_part": "jig-connector",
   "pins": 7, "size": "small", "unit": "assembly",
   "notes": "One per XIAO row; a row with no wires still gets one. Buy one 5 x 7-pin pack (3 spare)."},
  {"part": "JIG_ connector, small, 4-pin", "quantity": 1, "jig_part": "jig-connector",
   "pins": 4, "size": "small", "unit": "assembly", "notes": "Buy one 5 x 4-pin pack."},
  {"part": "Female-to-female jumper wires, 10 cm", "quantity": 4},
  {"part": "Printed body (body.stl)", "quantity": 1},
  {"part": "USB-C data cable", "quantity": 1}
]
```

`part` and a whole-number `quantity` are required. `jig_part` must be an id from
`find_jig_parts`. A JIG_ connector row also needs `pins` (the whole row), `size`
and `unit: "assembly"`; its quantity is the connectors the build uses. Put the
packs to buy in `notes`. Add `url`, `notes` or `owned` when useful.

## wiring.json

```json
{
  "boards": [{"board": "XIAO ESP32S3"}, {"board": "ssd1306-i2c"}],
  "connections": [
    {"from": "XIAO 3V3", "to": "OLED VCC", "color": "red", "function": "power",
     "voltage_v": 3.3, "expected_current_ma": 20, "wire_current_limit_ma": 1000,
     "contact_current_limit_ma": 3000},
    {"from": "XIAO GND", "to": "OLED GND", "color": "black", "function": "ground",
     "voltage_v": 0, "expected_current_ma": 20, "wire_current_limit_ma": 1000,
     "contact_current_limit_ma": 3000},
    {"from": "XIAO D4", "to": "OLED SDA", "color": "blue", "function": "signal", "voltage_v": 3.3},
    {"from": "XIAO D5", "to": "OLED SCL", "color": "yellow", "function": "signal", "voltage_v": 3.3}
  ],
  "connectors": [
    {"board": "XIAO ESP32S3", "pins": 7, "size": "small",
     "header": {"id": "left", "pin_count": 7, "pitch_mm": 2.54, "rows": 1,
                "gender": "male", "shrouded": false, "preinstalled": true},
     "orientation": {"pin_one": "D0, USB end",
                     "ordered_pin_ids": ["D0", "D1", "D2", "D3", "D4", "D5", "D6"]}},
    {"board": "XIAO ESP32S3", "pins": 7, "size": "small",
     "header": {"id": "right", "pin_count": 7, "pitch_mm": 2.54, "rows": 1,
                "gender": "male", "shrouded": false, "preinstalled": true},
     "orientation": {"pin_one": "5V, USB end",
                     "ordered_pin_ids": ["5V", "GND", "3V3", "D10", "D9", "D8", "D7"]}},
    {"board": "0.96-inch SSD1306 OLED (I2C)", "pins": 4, "size": "small",
     "header": {"id": "j1", "pin_count": 4, "pitch_mm": 2.54, "rows": 1,
                "gender": "male", "shrouded": false, "preinstalled": true},
     "orientation": {"pin_one": "GND",
                     "ordered_pin_ids": ["GND", "VCC", "SCL", "SDA"]}}
  ]
}
```

List every wire, with a color or label so the picture guide can say "the blue
wire", what it does (`signal`, `power` or `ground`) and its voltage. Power and
ground wires also need the expected current and what the wire and connector
contacts can carry.

List the boards each wire runs between under `boards` (names from
`board_headers`), and one connector for every row of every board, even a row with
no wires. For each connector give the `board`, the `header` row (with `gender`,
`rows`, `shrouded` and `preinstalled` as checked on the real board), `pins` for
the whole row, and `orientation`: where pin one is and `ordered_pin_ids` naming
every position in order. See [connector usage](connector-usage.md).

If nothing plugs onto a header, declare `connector_scope: {"kind":
"no_header_wiring", "reason": "..."}`. For a row that can't take a JIG_
connector, record a `connector_exceptions` entry with the exact board name,
`header_id`, `reason`, `alternative` and `evidence`.

## Firmware

Include the source, the exact board setting, how to load it (or that it comes
preloaded), any settings to change, and what the device shows when it's working.

## Testing

A short checklist, in order: what to look at, what a pass looks like, and what to
do if it fails. Mark tests that need the physical build as such.
