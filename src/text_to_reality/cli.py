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
    batch = commands.add_parser("import-boards", help="validate research into the existing boards catalog")
    batch.add_argument("proposal", type=Path, help="schemaVersion 1 boards proposal")
    batch.add_argument("--catalog", type=Path, required=True, help="existing boards.json")
    batch.add_argument("--source-root", type=Path, required=True, help="unpacked preserved source bundle")
    batch.add_argument("--manifest", type=Path, required=True, help="source SHA-256 manifest")
    batch.add_argument("--batch-id", required=True, help="unique stable research batch identity")
    batch.add_argument("--output", type=Path, help="optional candidate or exact catalog path; omission is read-only")
    batch.add_argument("--normalize-source-format", action="store_true", help="bridge known research representations, preserving raw source and unknowns")
    batch.add_argument("--expected-output-sha256", help="required to replace different existing output bytes")
    enrich = commands.add_parser("enrich-boards", help="validate source-bound descriptive header enrichment")
    enrich.add_argument("patch", type=Path)
    enrich.add_argument("--catalog", type=Path, required=True)
    enrich.add_argument("--source-root", type=Path, required=True)
    enrich.add_argument("--manifest", type=Path, required=True)
    enrich.add_argument("--enrichment-id", required=True)
    enrich.add_argument("--photo-source-format", action="store_true", help="bind guarded photo proposal to exact runtime record hashes")
    enrich.add_argument("--output", type=Path, help="omission is read-only")
    enrich.add_argument("--expected-output-sha256", help="exact guard required to replace output")
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
    if args.command == "import-boards":
        from .catalog_import import (
            CatalogImportError,
            digest,
            encoded,
            normalize_research_proposal,
            prepare_import,
            read_json,
            write_catalog,
        )
        try:
            proposal = read_json(args.proposal)
            original_proposal_sha = digest(encoded(proposal))
            adjustments = []
            if args.normalize_source_format:
                proposal, adjustments = normalize_research_proposal(proposal)
            merged, report = prepare_import(read_json(args.catalog), proposal,
                                           args.source_root, read_json(args.manifest), args.batch_id)
            report["original_proposal_canonical_sha256"] = original_proposal_sha
            report["normalization_adjustments"] = adjustments
            if args.output:
                write_catalog(args.output, encoded(merged), expected_sha256=args.expected_output_sha256)
                report["output"] = str(args.output.resolve())
            print(json.dumps(report, indent=2))
            return 0
        except (CatalogImportError, OSError) as error:
            print(json.dumps({"error": str(error), "catalog_modified": False}))
            return 1
    if args.command == "enrich-boards":
        from .catalog_enrichment import normalize_photo_patch, prepare_enrichment
        from .catalog_import import (
            CatalogImportError,
            encoded,
            read_json,
            write_catalog,
        )
        try:
            existing = read_json(args.catalog)
            patch = read_json(args.patch)
            if args.photo_source_format:
                try:
                    relative = args.patch.resolve().relative_to(args.source_root.resolve()).as_posix()
                except ValueError as error:
                    raise CatalogImportError("Photo proposal must be under source-root") from error
                patch = normalize_photo_patch(existing, patch, relative, args.enrichment_id)
            merged, report = prepare_enrichment(existing, patch, args.source_root,
                                               read_json(args.manifest), args.enrichment_id)
            if args.output:
                write_catalog(args.output, encoded(merged), expected_sha256=args.expected_output_sha256)
                report["output"] = str(args.output.resolve())
            print(json.dumps(report, indent=2))
            return 0
        except (CatalogImportError, OSError) as error:
            print(json.dumps({"error": str(error), "catalog_modified": False}))
            return 1
    print(json.dumps(catalog.find_boards(args.query), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
