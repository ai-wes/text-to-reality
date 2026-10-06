"""JIG_ parts and board header data the agent can look up."""

from __future__ import annotations

import json
import math
from functools import cache
from importlib import resources
from typing import Any

STANDARD_PIN_COUNTS = (1, 2, 3, 4, 5, 6, 7, 8, 22)
MAX_PIN_COUNT = 22
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
        if needle in {entry["id"].lower(), entry["name"].lower(), *(a.lower() for a in entry["aliases"])}:
            return entry
    matches = find_boards(name_or_id)
    return matches[0] if len(matches) == 1 else None


def pack_for(pins: int) -> dict[str, Any]:
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
    for selection in selections:
        quantity = int(selection.get("quantity", 1))
        if quantity < 1:
            raise ValueError("quantity must be at least 1")
        if "rows" in selection:
            rows = [int(r) for r in selection["rows"]]
            label = selection.get("board", "custom board")
        else:
            entry = board(str(selection.get("board", "")))
            if entry is None:
                unknown.append(str(selection.get("board", "")))
                continue
            rows = [h["pin_count"] for h in entry["headers"]]
            label = entry["name"]
        resolved.append({"board": label, "quantity": quantity, "header_rows": rows})
        for pins in rows:
            totals[pins] = totals.get(pins, 0) + quantity
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
        connectors.append(item)
    return {
        "rule": "One connector per header row, sized to the whole row.",
        "boards": resolved,
        "connectors": connectors,
        "unknown_boards": unknown,
        "order_url": CONNECTOR_URL,
    }
