# Picture guides

The guide is the product. Write it for someone who has never built electronics.

## Rules

- **One action per step.** "Push the blue connector onto the left row of pins."
  Not "Connect the display."
- **Show, then say.** Every step gets a picture: a diagram, a render of the CAD
  model, or a photo. Make diagrams with SVG or a CAD render; name the files
  `step-01.svg`, `step-02.png` and so on, and record them under `assembly`.
- **Use what they can see.** Wire colors, shapes, labels printed on the board,
  "the side with the USB port". Not pin numbers alone, not jargon.
- **Say how to know it's right.** End steps with a check: "the connector sits flat
  and covers all seven pins".
- **Order matters.** Things that are hard to reach later go first. Power goes last.
- **Unplugged until the end.** Say when to unplug and when it's safe to plug in.

## Shape of the guide

1. What's in the box (picture of all parts, laid out and labeled).
2. The steps.
3. Turn it on: what they should see.
4. If something's wrong: the two or three most likely fixes.

Avoid: "simply", "just", "easy". Avoid unexplained terms like GPIO, SPI or I2C; if
one is unavoidable, say what it means in a few words.
