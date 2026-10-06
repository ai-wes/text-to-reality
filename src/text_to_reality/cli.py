"""Command line: `text-to-reality mcp | check PATH | parts [QUERY] | boards QUERY`."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__, catalog, package


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="text-to-reality", description="Turn an idea into a buildable device package.")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    serve = commands.add_parser("mcp", help="run the local MCP server over stdio")
    serve.add_argument("--dir", type=Path, help="projects folder (default: ./text-to-reality or $TEXT_TO_REALITY_DIR)")
    check = commands.add_parser("check", help="check a project folder")
    check.add_argument("path", type=Path)
    parts = commands.add_parser("parts", help="list JIG_ parts")
    parts.add_argument("query", nargs="?", default="")
    boards = commands.add_parser("boards", help="show header rows for a board")
    boards.add_argument("query")
    args = parser.parse_args(argv)

    if args.command == "mcp":
        from .server import create_server
        from .store import Store

        create_server(Store(args.dir)).run()
        return 0
    if args.command == "check":
        report = package.validate(args.path)
        print(json.dumps(report, indent=2))
        return 0 if report["complete"] else 1
    if args.command == "parts":
        print(json.dumps(catalog.find_parts(args.query), indent=2))
        return 0
    print(json.dumps(catalog.find_boards(args.query), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
