# Releasing text-to-reality

## What ships

The PyPI package (`text-to-reality`) contains the local MCP server, the CLI, and
its data:

- `boards.json`: header rows for 320 boards and modules.
- `jig_parts.json`: JIG_ parts with links to jig-robotics.com.
- `connector_usage.json` and `connector_usage.md`: the connector rules. The
  Markdown copy is `skills/text-to-reality/references/connector-usage.md`.

The source package adds the skill. The research files under
`docs/connector-library/` stay in the repo only; they are the evidence behind
`boards.json` (see BATCH-IMPORT.md) and are not shipped.

The Claude Code, Codex and Cursor plugins install the skill from this repo and
run the server with `uvx --from text-to-reality==<version>`.

## Release steps

1. Run the tests: `uv run pytest`.
2. Set the same version in `pyproject.toml`, `src/text_to_reality/__init__.py`,
   all three `*-plugin/plugin.json` files, `.claude-plugin/marketplace.json`,
   the three `*.mcp.json` files and the Claude Desktop snippet in README.md.
3. Build: `rm -rf dist && uv build`.
4. Check the wheel in a clean environment outside the repo:
   `uvx --from dist/text_to_reality-<version>-py3-none-any.whl text-to-reality boards xiao`.
5. Publish with your own PyPI token: `uv publish`.
6. Commit, tag `v<version>` and push to `main`. Plugin installs pick it up from
   the repo; the pinned version makes them fetch the new package.

A published version can't be replaced, so bump the version for any fix.

## Still open

- The XIAO battery adapter (R29) and bus blocks are untested.
- The server runs over stdio only; there is no hosted endpoint.
