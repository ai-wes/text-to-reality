"""Check that a build package is complete and that its pieces agree."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import catalog
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
        if not isinstance(pins, int) or not 1 <= pins <= catalog.MAX_PIN_COUNT:
            problems.append(f"wiring.json connector {index}: 'pins' must be 1-{catalog.MAX_PIN_COUNT} (the whole header row)")
        if isinstance(connector, dict) and connector.get("size") not in {"small", "large"}:
            problems.append(f"wiring.json connector {index}: 'size' must be small or large")
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
    bom_path = directory / "bom.json"
    if stages.get("parts", {}).get("status") == "done":
        if "bom.json" not in files:
            problems.append("parts: record a bom.json")
        elif bom_path.is_file():
            used_jig = check_bom(_load_json(bom_path, problems), problems)

    if stages.get("electronics", {}).get("status") == "done":
        wiring_path = directory / "wiring.json"
        if "wiring.json" not in files:
            problems.append("electronics: record a wiring.json")
        elif wiring_path.is_file():
            connectors = check_wiring(_load_json(wiring_path, problems), problems)
            if connectors and "jig-connector" not in used_jig:
                problems.append("wiring.json uses JIG_ connectors but bom.json has no row with jig_part 'jig-connector'")

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
