"""Check that a build package is complete and that its pieces agree."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import catalog, connector_usage
from .store import MANIFEST, STAGES, STATUSES, sha256

ALWAYS_REQUIRED = ("requirements", "parts", "assembly")


def _load_json(path: Path, problems: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        problems.append(f"{path.name}: not valid JSON ({error})")
        return None


def check_bom(rows: Any, problems: list[str]) -> set[str]:
    """Return the JIG_ part ids used. Rows: [{"part", "quantity", "jig_part"?, "url"?, "notes"?}]."""
    used: set[str] = set()
    if isinstance(rows, dict):
        rows = rows.get("items")
    if not isinstance(rows, list) or not rows:
        problems.append("bom.json: must be a non-empty list of parts")
        return used
    known = {p["id"] for p in catalog.parts()}
    for index, row in enumerate(rows, 1):
        if not isinstance(row, dict) or not str(row.get("part", "")).strip():
            problems.append(f"bom.json row {index}: needs a 'part' name")
            continue
        quantity = row.get("quantity")
        if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity < 1:
            problems.append(f"bom.json row {index} ({row['part']}): quantity must be a whole number of at least 1")
        jig = row.get("jig_part")
        if jig is not None:
            if jig not in known:
                problems.append(f"bom.json row {index}: unknown jig_part {jig!r}")
            else:
                used.add(jig)
    return used


def check_wiring(wiring: Any, problems: list[str]) -> list[dict[str, Any]]:
    """wiring.json: {"connections": [{"from", "to", "color"?}], "connectors": [{"pins", "size", "plugs_onto"}]}."""
    if not isinstance(wiring, dict):
        problems.append("wiring.json: must be an object with 'connections'")
        return []
    connections = wiring.get("connections")
    if not isinstance(connections, list) or not connections:
        problems.append("wiring.json: 'connections' must list every wire")
    else:
        for index, wire in enumerate(connections, 1):
            if not isinstance(wire, dict) or not wire.get("from") or not wire.get("to"):
                problems.append(f"wiring.json connection {index}: needs 'from' and 'to'")
    connectors = wiring.get("connectors", [])
    if not isinstance(connectors, list):
        problems.append("wiring.json: 'connectors' must be a list")
        return []
    for index, connector in enumerate(connectors, 1):
        pins = connector.get("pins") if isinstance(connector, dict) else None
        if type(pins) is not int or not 1 <= pins <= catalog.MAX_PIN_COUNT:
            problems.append(f"wiring.json connector {index}: 'pins' must be 1-{catalog.MAX_PIN_COUNT} (the whole header row)")
        if isinstance(connector, dict) and connector.get("size") not in {"small", "large"}:
            problems.append(f"wiring.json connector {index}: 'size' must be small or large")
        if isinstance(connector, dict):
            for issue in connector_usage.connector_issues(connector):
                problems.append(f"wiring.json connector {index}: {issue}")
    selections = wiring.get("boards")
    if not selections:
        scope = wiring.get("connector_scope", {})
        if (not isinstance(scope, dict) or scope.get("kind") != "no_header_wiring"
                or not isinstance(scope.get("reason"), str) or not scope["reason"].strip()
                or connectors):
            problems.append("wiring.json: declare endpoint boards or an explicit no_header_wiring reason")
    elif not isinstance(selections, list):
        problems.append("wiring.json: boards must be a list of exact endpoint selections")
    else:
        try:
            plan = catalog.connectors_for(selections)
            if plan["unknown_boards"]:
                problems.append("wiring.json: unresolved endpoint board identity")
            expected = {item["pins"]: item["connectors"] for item in plan["connectors"]}
            actual: dict[int, int] = {}
            actual_rows: dict[tuple[str, str], int] = {}
            for connector in connectors:
                if not isinstance(connector, dict) or type(connector.get("pins")) is not int:
                    continue
                qty = connector.get("quantity", 1)
                if type(qty) is not int or qty < 1:
                    problems.append("wiring.json: connector quantity must be a positive whole number")
                    continue
                actual[connector["pins"]] = actual.get(connector["pins"], 0) + qty
                header = connector.get("header", {})
                if isinstance(header, dict) and isinstance(connector.get("board"), str) and isinstance(header.get("id"), str):
                    key = (connector["board"], header["id"])
                    actual_rows[key] = actual_rows.get(key, 0) + qty
            exceptions = wiring.get("connector_exceptions", [])
            valid_exceptions = set()
            if not isinstance(exceptions, list):
                problems.append("wiring.json: connector_exceptions must be a list")
            else:
                for exception in exceptions:
                    if (not isinstance(exception, dict) or not all(
                        isinstance(exception.get(k), str) and exception[k].strip()
                        for k in ("board", "header_id", "reason", "alternative", "evidence")
                    )):
                        problems.append("wiring.json: each exception needs exact board/header, reason, alternative and evidence")
                    else:
                        valid_exceptions.add((exception["board"], exception["header_id"]))
            for row in plan["boards"]:
                for header in row["headers"]:
                    key = (row["board"], header.get("id"))
                    if key in valid_exceptions and not connector_usage.incompatible_header(header):
                        pins = header["pin_count"]
                        expected[pins] = expected.get(pins, 0) - row["quantity"]
            expected_rows: dict[tuple[str, str], int] = {}
            known_rows = set()
            for row in plan["boards"]:
                for h in row["headers"]:
                    key = (row["board"], h.get("id"))
                    known_rows.add(key)
                    if not connector_usage.incompatible_header(h) and key not in valid_exceptions:
                        expected_rows[key] = expected_rows.get(key, 0) + row["quantity"]
            if not valid_exceptions <= known_rows:
                problems.append("wiring.json: exception references an unknown endpoint row")
            for row in plan["row_checks"]:
                if (row["board"], row["header_id"]) not in valid_exceptions and row["issues"]:
                    problems.append(f"wiring.json {row['board']}/{row['header_id']}: "
                                    + ", ".join(row["issues"]))
            if expected_rows != actual_rows:
                problems.append("wiring.json: connector board/header identities must cover each endpoint row exactly")
            if {k: v for k, v in expected.items() if v} != actual:
                problems.append("wiring.json: JIG assemblies must cover every full endpoint row or record an explicit exception")
        except (ValueError, TypeError) as error:
            problems.append(f"wiring.json boards: {error}")
    if connectors and isinstance(connections, list):
        for index, wire in enumerate(connections, 1):
            if isinstance(wire, dict):
                for issue in connector_usage.wire_issues(wire):
                    problems.append(f"wiring.json connection {index}: {issue}")
    return connectors


def validate(directory: Path) -> dict[str, Any]:
    directory = Path(directory).resolve()
    problems: list[str] = []
    warnings: list[str] = []
    manifest_path = directory / MANIFEST
    if not manifest_path.is_file():
        return {"complete": False, "problems": [f"no {MANIFEST} in {directory}"], "warnings": []}
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    stages = data.get("stages", {})
    files = data.get("files", {})

    for stage in STAGES:
        entry = stages.get(stage)
        if not isinstance(entry, dict) or entry.get("status") not in STATUSES:
            problems.append(f"{stage}: missing or invalid status")
            continue
        status = entry["status"]
        if status == "todo":
            problems.append(f"{stage}: not finished")
        elif status == "not_applicable":
            if stage in ALWAYS_REQUIRED:
                problems.append(f"{stage}: every build needs this stage")
            elif not (entry.get("reason") or "").strip():
                problems.append(f"{stage}: marked not applicable without a reason")
        elif not entry.get("files"):
            problems.append(f"{stage}: marked done but has no files")

    for relative, meta in files.items():
        path = (directory / relative).resolve()
        if directory not in path.parents:
            problems.append(f"{relative}: outside the project folder")
        elif not path.is_file():
            problems.append(f"{relative}: recorded but missing")
        elif sha256(path) != meta.get("sha256"):
            problems.append(f"{relative}: changed since it was recorded; record it again or start a new revision")
        elif meta.get("revision") != data.get("revision"):
            warnings.append(f"{relative}: recorded in revision {meta.get('revision')}, project is at {data.get('revision')}")

    used_jig: set[str] = set()
    bom_rows: Any = None
    bom_path = directory / "bom.json"
    if stages.get("parts", {}).get("status") == "done":
        if "bom.json" not in files:
            problems.append("parts: record a bom.json")
        elif bom_path.is_file():
            bom_rows = _load_json(bom_path, problems)
            used_jig = check_bom(bom_rows, problems)

    if stages.get("electronics", {}).get("status") == "done":
        wiring_path = directory / "wiring.json"
        if "wiring.json" not in files:
            problems.append("electronics: record a wiring.json")
        elif wiring_path.is_file():
            connectors = check_wiring(_load_json(wiring_path, problems), problems)
            if connectors and "jig-connector" not in used_jig:
                problems.append("wiring.json uses JIG_ connectors but bom.json has no row with jig_part 'jig-connector'")
            if connectors and "jig-connector" in used_jig:
                rows = bom_rows.get("items", []) if isinstance(bom_rows, dict) else bom_rows
                bom_counts: dict[tuple[Any, Any], int] = {}
                wire_counts: dict[tuple[Any, Any], int] = {}
                for row in rows:
                    if not isinstance(row, dict) or row.get("jig_part") != "jig-connector":
                        continue
                    if (row.get("unit") != "assembly" or type(row.get("pins")) is not int
                            or row.get("size") not in {"small", "large"} or not row.get("model_revision")):
                        problems.append("bom.json: JIG connector needs assembly unit, full-row pins, size and model_revision; store packs are separate")
                        continue
                    key = (row["pins"], row["size"])
                    if type(row.get("quantity")) is int:
                        bom_counts[key] = bom_counts.get(key, 0) + row["quantity"]
                for row in connectors:
                    if (not isinstance(row, dict) or type(row.get("pins")) is not int
                            or row.get("size") not in {"small", "large"}):
                        continue
                    key = (row["pins"], row["size"])
                    qty = row.get("quantity", 1)
                    if type(qty) is int and qty > 0:
                        wire_counts[key] = wire_counts.get(key, 0) + qty
                if bom_counts != wire_counts:
                    problems.append("bom.json: JIG assembly quantities must equal wiring.json, not rounded store pack quantities")

    if stages.get("assembly", {}).get("status") == "done":
        guides = [p for p in stages["assembly"].get("files", []) if p.lower().endswith((".md", ".html", ".pdf"))]
        if not guides:
            problems.append("assembly: needs a written guide (.md, .html or .pdf)")

    buy = [
        {"name": p["name"], "url": p["url"]} for p in catalog.parts() if p["id"] in used_jig
    ]
    return {
        "project": data.get("name"),
        "revision": data.get("revision"),
        "complete": not problems,
        "problems": problems,
        "warnings": warnings,
        "get_the_parts": buy,
    }
