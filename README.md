<div align="center">

# text-to-reality

**Give your agent the power to build real things.**

text-to-cad makes a part. text-to-reality makes the working device.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/text-to-reality?style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.org/project/text-to-reality/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](pyproject.toml)

</div>

Describe something you want to exist. Your agent turns it into a build package
anyone can put together by following pictures:

- **a parts list** you can order, using parts that plug together
- **3D-printable parts** for the case and mounts
- **the wiring**, every wire and which connector it goes in
- **the code**, ready to load
- **a step-by-step picture guide** written for someone who has never built electronics
- **tests**, so you know it works

No soldering, no breadboard, no electronics experience required. It runs on your
machine: no account, no API key, and your projects are plain folders you own.

## Example: Agent Meter

> *"Build me a little desk character that shows what my coding agent is doing and
> how much of my Claude allowance is left."*

<p align="center"><img src="docs/media/agent-meter.png" alt="Agent Meter, a small printed robot character with a screen in its head (concept render)" width="420"></p>

Agent Meter was built with this workflow: a Seeed Studio XIAO ESP32-S3 and a small
screen inside a printed character, wired with plug-on connectors, with firmware and
a picture guide. Its face shows when your agent is working, finished or waiting on
you, plus your remaining allowance.

**[Get the Agent Meter kit →](https://jig-robotics.com/projects/agent-meter)**

## Install

### Ask your agent

```text
Install text-to-reality from https://github.com/ai-wes/text-to-reality
```

Or install it yourself. text-to-reality runs through [uv](https://docs.astral.sh/uv/):
check it's installed with `uv --version`, or use
[uv's installer](https://docs.astral.sh/uv/getting-started/installation/). Then run the
commands for your agent and restart it.

### Claude Code

```bash
claude plugin marketplace add ai-wes/text-to-reality
claude plugin install text-to-reality@ai-wes
```

To update: `claude plugin marketplace update ai-wes`, then
`claude plugin update text-to-reality@ai-wes`.

### Codex

```bash
codex plugin marketplace add ai-wes/text-to-reality
codex plugin add text-to-reality@ai-wes
```

### Cursor

Cursor also loads the Claude Code plugin; if that's installed, skip this.

```bash
git clone --depth 1 https://github.com/ai-wes/text-to-reality ~/.cursor/plugins/local/text-to-reality
```

### Claude Desktop

Add the server to Claude Desktop's config (Settings > Developer > Edit Config), then
restart. If it can't find `uvx`, use its full path (`which uvx`).

```json
{
  "mcpServers": {
    "text-to-reality": {
      "command": "uvx",
      "args": ["--no-config", "--managed-python", "--python", "3.13", "--from", "text-to-reality==0.1.0", "text-to-reality", "mcp"]
    }
  }
}
```

Projects are saved in `text-to-reality/` in the folder the app starts in; set
`TEXT_TO_REALITY_DIR` in `env` to choose another folder.

### Other agents

```bash
npx skills add ai-wes/text-to-reality
```

Then add the MCP server above to your agent's MCP config.

## Works with text-to-cad

text-to-reality plans the whole device; [text-to-cad](https://github.com/earthtojake/text-to-cad)
is great at the printed parts. Install both, and the agent uses text-to-cad for the
printed parts when it's available.

## How it works

Each build is a folder. The agent fills in seven stages and checks them:

| Stage | What's in it |
| --- | --- |
| Requirements | `brief.md`: what it does, size, power, budget, how you'll know it works |
| Parts | `bom.json`: every part and quantity |
| Printed parts | CAD source and STL/3MF files |
| Electronics | `wiring.json`: every wire, its color, and its connector |
| Code | firmware source and how to load it |
| Assembly | the picture guide |
| Testing | what to check, and what a pass looks like |

The local MCP server gives the agent tools to create projects, record files, catch
files edited after they were checked, validate the package, keep a build history, and
look up board header layouts and plug-on parts.

You can also check a folder yourself:

```bash
uvx text-to-reality check ./text-to-reality/my-build
```

## Parts that plug together

Loose jumper wires fall off and get swapped. [JIG_](https://jig-robotics.com) makes
parts that turn wiring into plugging things in: connectors that make a group of wires
one plug, and a battery adapter that adds a battery to a XIAO board without soldering.
The agent can look them up and will tell you which ones your build needs; you can use
any parts you like.

## License

MIT
