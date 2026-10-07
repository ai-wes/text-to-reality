"""JIG_ parts and board header data the agent can look up."""

from __future__ import annotations

import json
import math
from functools import cache
from importlib import resources
from typing import Any

from . import connector_usage

STANDARD_PIN_COUNTS = (1, 2, 3, 4, 5, 6, 7, 8, 22)
MAX_PIN_COUNT = 22
# Original broad family references: retained for explicit-ID compatibility.
LEGACY_FAMILY_IDS = frozenset({
    "seeed-xiao", "esp32-devkitc-v4", "esp32-devkit-v1-30", "esp32-s3-devkitc-1",
    "arduino-nano", "pro-micro", "wemos-d1-mini", "nodemcu-esp8266", "st7735s-128",
    "gmt020-02-8p", "ssd1306-i2c", "hc-sr04", "hc-sr501", "gy-521", "rc522",
    "max7219-matrix", "tm1637", "microsd-spi", "relay-1ch",
})
CONNECTOR_URL = "https://jig-robotics.com/support/dupont-housings"


@cache
def _load(name: str) -> dict[str, Any]:
    return json.loads(resources.files("text_to_reality.data").joinpath(name).read_text(encoding="utf-8"))


def parts() -> list[dict[str, Any]]:
    return _load("jig_parts.json")["parts"]


def boards() -> list[dict[str, Any]]:
    return _load("boards.json")["boards"]


def _matches(entry: dict[str, Any], needle: str, fields: tuple[str, ...]) -> bool:
    text = " ".join(str(entry.get(field, "")) for field in fields)
    text += " " + " ".join(entry.get("aliases", []))
    return needle in text.lower()


def find_parts(query: str = "") -> list[dict[str, Any]]:
    needle = query.strip().lower()
    if not needle:
        return parts()
    words = needle.split()
    return [p for p in parts() if any(_matches(p, w, ("id", "name", "summary", "use_when")) for w in words)]


def find_boards(query: str) -> list[dict[str, Any]]:
    needle = query.strip().lower()
    if not needle:
        return boards()
    return [b for b in boards() if _matches(b, needle, ("id", "name"))]


def board(name_or_id: str) -> dict[str, Any] | None:
    needle = name_or_id.strip().lower()
    for entry in boards():
        if needle == entry["id"].lower():
            return entry
    labels = [entry for entry in boards() if needle == entry["name"].strip().lower()
              or needle in {a.strip().lower() for a in entry["aliases"]}]
    researched = [entry for entry in labels if entry.get("source_record")
                  and needle not in {a.strip().lower() for a in entry.get("legacy_aliases", [])}]
    if researched:
        nonlegacy = [entry for entry in labels if entry["id"] not in LEGACY_FAMILY_IDS
                     and needle not in {a.strip().lower() for a in entry.get("legacy_aliases", [])}]
        return researched[0] if len(researched) == 1 and len(nonlegacy) == 1 else None
    if labels:
        return labels[0] if len(labels) == 1 else None
    matches = find_boards(name_or_id)
    return matches[0] if len(matches) == 1 else None


def pack_for(pins: int) -> dict[str, Any]:
    connector_usage.positive_int(pins, "pins")
    if pins > MAX_PIN_COUNT:
        raise ValueError("pins exceeds the supported 22-position range")
    if pins <= 8:
        return {"connectors_per_pack": 5, "pack": f"5 x {pins}-pin"}
    if pins == 22:
        return {"connectors_per_pack": 2, "pack": "2 x 22-pin"}
    return {"connectors_per_pack": 2, "pack": f"2 x {pins}-pin (printed to order)"}


def connectors_for(selections: list[dict[str, Any]], size: str = "small") -> dict[str, Any]:
    """One connector per full header row; returns connectors, packs and unknown boards.

    Each selection is {"board": name-or-id, "quantity": n} or {"rows": [pin counts], "quantity": n}
    for a board that isn't in the catalog.
    """
    if size not in {"small", "large"}:
        raise ValueError("size must be 'small' or 'large'")
    totals: dict[int, int] = {}
    unknown: list[str] = []
    resolved: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    for selection in selections:
        if not isinstance(selection, dict):
            raise ValueError("each board selection must be an object")
        quantity = connector_usage.positive_int(selection.get("quantity", 1), "quantity")
        revision = selection.get("revision")
        if "headers" in selection:
            headers = selection["headers"]
            label = selection.get("board", "custom board")
        if "rows" in selection and "headers" in selection:
            raise ValueError("supply rows or headers, not both")
        if "rows" in selection:
            if not isinstance(selection["rows"], list):
                raise ValueError("rows must be a list of full physical row counts")
            headers = [{"id": f"row-{i + 1}", "pin_count": connector_usage.positive_int(r, "row pins")}
                       for i, r in enumerate(selection["rows"])]
            label = selection.get("board", "custom board")
        elif "headers" not in selection:
            entry = board(str(selection.get("board", "")))
            if entry is None:
                unknown.append(str(selection.get("board", "")))
                continue
            headers = entry["headers"]
            label = entry["name"]
            revision = revision or (entry.get("revision") if entry.get("revision_verified") is True else None)
        if not isinstance(headers, list) or any(not isinstance(h, dict) for h in headers):
            raise ValueError("headers must be a list of header objects")
        if any(not isinstance(h.get("id"), str) or not h["id"].strip() for h in headers):
            raise ValueError("every header needs an exact non-empty row ID")
        if len({h.get("id") for h in headers}) != len(headers):
            raise ValueError("header IDs must identify separate physical rows uniquely")
        if not headers:
            issues.append({"board": label, "header_id": None,
                           "issues": ["no_compatible_single_row_headers"], "excluded": True})
        rows = []
        for header in headers:
            pins = connector_usage.positive_int(header.get("pin_count"), "full row pins")
            issues.append({"board": label, "header_id": header.get("id"),
                           "issues": connector_usage.header_issues(header),
                           "excluded": connector_usage.incompatible_header(header)})
            if connector_usage.incompatible_header(header):
                continue
            rows.append(pins)
            totals[pins] = totals.get(pins, 0) + quantity
        resolved.append({"board": label, "quantity": quantity, "header_rows": rows,
                         "revision": revision, "headers": headers})
    connectors = []
    for pins in sorted(totals):
        count = totals[pins]
        item: dict[str, Any] = {"size": size, "pins": pins, "connectors": count}
        if pins < 1 or pins > MAX_PIN_COUNT:
            item["note"] = "Longer than 22 pins: no standard JIG_ connector."
        else:
            pack = pack_for(pins)
            item["pack"] = pack["pack"]
            item["packs_to_order"] = math.ceil(count / pack["connectors_per_pack"])
            item["printed_to_order"] = pins not in STANDARD_PIN_COUNTS
            item["assembly_units_per_pack"] = pack["connectors_per_pack"]
            item["spare_assemblies"] = item["packs_to_order"] * pack["connectors_per_pack"] - count
            item["base_units"] = count
            item["cover_units"] = count
        connectors.append(item)
    return {
        "rule": "One connector per header row, sized to the whole row.",
        "boards": resolved,
        "connectors": connectors,
        "unknown_boards": unknown,
        "order_url": CONNECTOR_URL,
        "usage_revision": connector_usage.rules()["revision"],
        "dependency": connector_usage.rules()["dependency"],
        "design": connector_usage.rules()["design"],
        "row_checks": issues,
        "bom_draft": [{"part": f"JIG_ {c['pins']}-pin {size} connector", "quantity": c["connectors"],
                       "unit": "assembly", "pins": c["pins"], "size": size, "jig_part": "jig-connector"}
                      for c in connectors],
        "row_diagrams": [{"board": b["board"], "revision": b["revision"],
                          "header_id": h.get("id"), "full_row_positions": h["pin_count"],
                          "ordered_pin_ids": h.get("pin_ids"), "orientation": h.get("orientation")}
                         for b in resolved for h in b["headers"]],
        "note": "row_checks lists what to confirm on the real board (male, single row, unshrouded, already installed).",
    }
