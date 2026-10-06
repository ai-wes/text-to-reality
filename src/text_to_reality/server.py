"""Local MCP server. Everything is stored in plain folders on the user's machine."""

from __future__ import annotations

from typing import Any

from mcp.server.mcpserver import MCPServer

from . import __version__, catalog, package
from .store import ProjectError, Store

INSTRUCTIONS = (
    "text-to-reality turns an idea into a device someone can build by following pictures: "
    "parts list, printed parts, wiring, code, an assembly guide and tests. Start with create_project, "
    "write each stage's files into the project folder, record them with record_files, and finish with "
    "check_package. Prefer parts that plug together (pre-soldered headers, JIG_ connectors) so the "
    "builder never solders, crimps or uses a breadboard."
)


def _safe(call):
    try:
        return call()
    except ProjectError as error:
        return {"error": str(error)}


def create_server(store: Store | None = None) -> MCPServer:
    store = store or Store()
    server = MCPServer(
        "text-to-reality",
        instructions=INSTRUCTIONS,
        version=__version__,
        website_url="https://github.com/ai-wes/text-to-reality",
    )

    @server.tool()
    def create_project(name: str, brief: str) -> dict[str, Any]:
        """Start a build. `brief` is the idea in plain words plus anything known: size, power, budget,
        parts the person already owns, and how they'll know it works. Creates a folder with brief.md."""
        return _safe(lambda: store.create(name, brief))

    @server.tool()
    def list_projects() -> list[dict[str, Any]]:
        """List builds in the projects folder."""
        return store.list()

    @server.tool()
    def project_status(project: str) -> dict[str, Any]:
        """Show each stage, its files, what to do next, and files edited since they were recorded."""
        return _safe(lambda: store.status(project))

    @server.tool()
    def record_files(project: str, stage: str, paths: list[str]) -> dict[str, Any]:
        """Record files you've written (paths relative to the project folder) under a stage:
        requirements, parts, mechanical, electronics, firmware, assembly or testing.
        Recording fingerprints each file so later edits are caught."""
        return _safe(lambda: store.record(project, stage, paths))

    @server.tool()
    def set_stage(project: str, stage: str, status: str, reason: str | None = None) -> dict[str, Any]:
        """Set a stage to todo, done or not_applicable. not_applicable needs a reason
        (for example, a printed-only object has no electronics)."""
        return _safe(lambda: store.set_stage(project, stage, status, reason))

    @server.tool()
    def check_package(project: str) -> dict[str, Any]:
        """Check the build is complete and consistent: every stage finished, files unchanged since
        recorded, bom.json and wiring.json valid, JIG_ connectors in the parts list, an assembly guide
        present. Returns problems to fix and links to get the JIG_ parts the build uses."""
        return _safe(lambda: package.validate(store.load(project)[0]))

    @server.tool()
    def new_revision(project: str, note: str) -> dict[str, Any]:
        """Start a new revision after a design change. Re-record files you change in it."""
        return _safe(lambda: store.new_revision(project, note))

    @server.tool()
    def log_outcome(project: str, result: str, note: str) -> dict[str, Any]:
        """Record what happened when the build was tried: worked, partly_worked or failed, with what
        was learned. Read it back with build_history before designing the next one."""
        return _safe(lambda: store.outcome(project, result, note))

    @server.tool()
    def build_history(project: str) -> list[dict[str, Any]] | dict[str, Any]:
        """Everything that happened to a build: files recorded, revisions, outcomes."""
        return _safe(lambda: store.history(project))

    @server.tool()
    def find_jig_parts(query: str = "") -> list[dict[str, Any]]:
        """Look up JIG_ parts that remove soldering, crimping and breadboards: wire connectors,
        a XIAO battery adapter, and complete kits. Empty query lists everything."""
        return catalog.find_parts(query)

    @server.tool()
    def board_headers(query: str) -> list[dict[str, Any]]:
        """Header rows (pins per row) for common boards and modules: XIAO, Pico, ESP32 DevKit,
        Arduino Nano, SSD1306 OLED and more."""
        return catalog.find_boards(query)

    @server.tool()
    def connectors_for_boards(boards: list[dict[str, Any]], size: str = "small") -> dict[str, Any]:
        """Which JIG_ wire connectors a build needs: one per header row, sized to the whole row.
        `boards` is a list of {"board": name, "quantity": n}, or {"board": label, "rows": [pins, ...],
        "quantity": n} for a board that isn't in the catalog. `size` is small or large, matching the
        jumper wire housings."""
        try:
            return catalog.connectors_for(boards, size)
        except ValueError as error:
            return {"error": str(error)}

    return server
