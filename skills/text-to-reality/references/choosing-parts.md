# Choosing parts

The goal is a build with no soldering, no crimping and no breadboard. Most of that
is decided here.

## Boards and modules

- Prefer modules sold **with headers already soldered** (often listed as "pre-soldered"
  or with an "H" suffix, like Raspberry Pi Pico H).
- Prefer boards with USB-C and built-in USB programming (ESP32-S3, ESP32-C3, RP2040,
  Seeed Studio XIAO).
- For sensors and displays, prefer breakouts with standard 2.54 mm (0.1 in) header
  pins. Grove/STEMMA QT/Qwiic cables are also solder-free; use one system per build.
- Check voltage: most modern modules are 3.3 V. Note any 5 V module and how it's
  powered.
- Use `board_headers` to see how many header rows a board has and how many pins
  are in each.

## Wires and connectors

Jumper wires work, but loose ones fall off and get swapped. JIG_ connectors
group the wires going to one header row into a single plug:

- **One connector per header row, with the same pin count as the whole row.**
  A 7-pin row needs a 7-pin connector even if three pins are used.
- Two sizes: small (for jumper wire plugs about 12 x 2 x 2 mm) and large (about
  14 x 2.5 x 2.5 mm). Match the person's jumper wires.
- `connectors_for_boards` returns the connectors and packs for a list of boards.
  Put them in `bom.json` with `"jig_part": "jig-connector"`.

Get them at [jig-robotics.com](https://jig-robotics.com/support/dupont-housings), which also has a
finder for a board's connectors. Use `find_jig_parts` for the full list.

Call `connector_guidance` and read [connector usage](connector-usage.md) before
planning header wiring. The XIAO battery adapter and bus blocks are still being
tested; don't use them as a build's power path.

## Power

- USB power from a computer or phone charger is simplest; say which.
- For batteries, name the exact cell, connector and how it charges. Don't invent
  battery life; give a calculation with its assumptions or say it needs testing.

## Printed parts

- Model the enclosure around the real module dimensions; write the dimensions you
  assumed into the brief so they can be checked.
- Leave room for the connectors and wires, and an opening for USB.
- Avoid features under about 1 mm; they print poorly. Prefer snap fits or screws
  that need no glue.
- If text-to-cad's `cad` skill is installed, use it to model and export. Record the
  source file and the exports (STL or 3MF) under `mechanical`.

## The parts list

Every part goes in `bom.json` with its quantity: boards, modules, connectors, wires,
screws, printed parts and the USB cable. Note parts the person already owns. See
[package format](package-format.md#bomjson).
