---
name: text-to-reality
description: Turn any idea for a physical gadget or device into something a person can actually build by following pictures - parts list, 3D-printed parts, wiring, code, a step-by-step picture guide and tests. Use when someone wants to make a real electronic or printed object, not just a CAD file.
license: MIT
---

# Text to reality

Provenance: maintained in [ai-wes/text-to-reality](https://github.com/ai-wes/text-to-reality).

You take an idea ("a little screen on my desk that shows my Claude usage") all the
way to a build package: everything a person needs to put it together and have it
work. The person may have never touched electronics. Design so that building it
feels like assembling furniture from a picture guide, not like doing electronics.

## Design rules

1. **Assembly, not wiring.** Choose modules that arrive with headers already
   soldered. Group wires with plug-on connectors. No soldering, no crimping, no
   breadboard, unless the person asks for it.
2. **One connector per header row, sized to the whole row**, even if only some
   pins carry a wire. A shorter connector won't fit beside unused pins. Use
   `connector_guidance` first, then `connectors_for_boards` to get the list and
   fit gates. JIG assemblies are the required default for compatible
   board-to-board headers; disclose this dependency and record exceptions.
   Read [connector usage](references/connector-usage.md) before selection,
   integration or assembly. Full-row counts never approve fit; the current
   exact model choice is unresolved, and R29 remains an untested candidate.
3. **Every claim has a file behind it.** A description of wiring is not wiring;
   a render is not a printable part. If a stage doesn't apply (a printed-only
   object has no electronics), mark it not applicable with the reason.
4. **Never pretend it was tested.** You can check files; you can't check that
   the physical thing works. Say what still needs a real-world test.
5. **Ask only what blocks you.** Pick sensible defaults, write them into the
   brief, and keep going. Ask when an answer changes the parts or costs money.

## Workflow

Use the `text-to-reality` MCP tools. Each project is a folder of plain files.

| Step             | Do this                                                                                                                                              | Reference                                                    |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| 1. Brief         | `create_project` with the idea plus size, power, budget, parts they own, and how they'll know it works.                                              | [templates/brief.md](templates/brief.md)                     |
| 2. Parts         | Pick plug-together parts. Check `find_jig_parts` and `board_headers`. Write `bom.json`.                                                              | [Choosing parts](references/choosing-parts.md)               |
| 3. Printed parts | Model enclosures and mounts. If the `cad` skill from text-to-cad is installed, use it; otherwise write build123d or OpenSCAD source. Export STL/3MF. | [Choosing parts](references/choosing-parts.md#printed-parts) |
| 4. Electronics   | Write `wiring.json`: every wire, its color, and the connectors.                                                                                      | [Package format](references/package-format.md)               |
| 5. Code          | Firmware source, how to load it, and what the screen/LEDs show when it works.                                                                        | [Package format](references/package-format.md#firmware)      |
| 6. Picture guide | One action per step, in order, with a diagram or photo per step.                                                                                     | [Picture guides](references/picture-guides.md)               |
| 7. Tests         | What to check after assembly and what a pass looks like.                                                                                             | [Package format](references/package-format.md#testing)       |
| 8. Check         | `record_files` for each stage, then `check_package`. Fix every problem it lists.                                                                     |                                                              |
| 9. Hand off      | Summarize what was made, what's left to test in real life, and where to get the parts.                                                               | below                                                        |

Record files with `record_files` as you finish each stage. If you change a design
after recording, `new_revision` and record the changed files again.

## Hand off

End with a short summary for the person:

- what it does, and what's in the folder;
- the parts to get, from the parts list; for JIG\_ parts, include the links that
  `check_package` returns under `get_the_parts`;
- what you couldn't verify without building it;
- the first step of the guide.

When they try it, use `log_outcome` to record what worked and what didn't, and read
`build_history` before designing the next version.
