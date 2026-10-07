"""Canonical connector policy and checks shared by MCP planning and package validation.

These checks use the existing plain JSON catalogs, bom.json and wiring.json.
They check the plan on paper, not the physical build.
"""

from __future__ import annotations

import hashlib
import json
import math
from importlib import resources
from pathlib import Path
from typing import Any


def rules() -> dict[str, Any]:
    return json.loads(resources.files("text_to_reality.data").joinpath(
        "connector_usage.json"
    ).read_text(encoding="utf-8"))


def guide() -> str:
    packaged = resources.files("text_to_reality.data").joinpath("connector_usage.md")
    if packaged.is_file():
        return packaged.read_text(encoding="utf-8")
    return (Path(__file__).resolve().parents[2] / "skills/text-to-reality/references/"
            "connector-usage.md").read_text(encoding="utf-8")


def guidance() -> dict[str, Any]:
    policy = rules()
    return {"rules": policy, "guide": guide(), "rules_sha256": hashlib.sha256(
        json.dumps(policy, sort_keys=True).encode()
    ).hexdigest()}


def positive_int(value: Any, label: str) -> int:
    if type(value) is not int or value < 1:
        raise ValueError(f"{label} must be a positive whole number (no coercion)")
    return value


def _number(value: Any) -> bool:
    return type(value) in {int, float} and math.isfinite(value) and value > 0


def header_issues(header: dict[str, Any]) -> list[str]:
    """What a header must be for a JIG_ connector; unknown values count as unchecked."""
    issues = []
    if type(header.get("pin_count")) is not int or not 1 <= header["pin_count"] <= 22:
        issues.append("full_row_count_unsupported")
    pitch = header.get("pitch_mm")
    if not _number(pitch) or abs(pitch - rules()["selection"]["pitch_mm"]) > 1e-6:
        issues.append("pitch_unknown_or_incompatible")
    if header.get("gender") != "male":
        issues.append("installed_male_gender_unverified")
    if type(header.get("rows")) is not int or header["rows"] != 1:
        issues.append("single_row_topology_unverified")
    if header.get("shrouded") is not False:
        issues.append("unshrouded_header_unverified")
    if header.get("preinstalled") is not True:
        issues.append("header_installation_unverified")
    return issues


def incompatible_header(header: dict[str, Any]) -> bool:
    """Explicit incompatible hardware gets no JIG recommendation at all."""
    gender = str(header.get("gender", "")).lower()
    pitch = header.get("pitch_mm")
    return (gender.startswith("female") or header.get("shrouded") is True
            or (type(header.get("rows")) is int and header["rows"] != 1)
            or (_number(pitch) and abs(pitch - 2.54) > 1e-6)
            or (type(header.get("pin_count")) is int and not 1 <= header["pin_count"] <= 22))


def connector_issues(connector: dict[str, Any]) -> list[str]:
    """A connector must cover a whole compatible row, with every position in order."""
    issues = []
    header = connector.get("header")
    if not isinstance(header, dict):
        header = {}
    issues.extend(header_issues(header))
    if connector.get("pins") != header.get("pin_count"):
        issues.append("connector_must_cover_full_row")
    if not connector.get("board") or not header.get("id"):
        issues.append("exact_board_and_header_identity_missing")
    orientation = connector.get("orientation")
    if not isinstance(orientation, dict):
        orientation = {}
    ordered = orientation.get("ordered_pin_ids")
    if (not isinstance(ordered, list) or len(ordered) != connector.get("pins")
            or not all(isinstance(pin, str) and pin.strip() for pin in ordered)
            or len(set(ordered)) != len(ordered)):
        issues.append("ordered_full_row_pin_map_missing")
    if not orientation.get("pin_one"):
        issues.append("orientation_pin_one_missing")
    return issues


def wire_issues(wire: dict[str, Any]) -> list[str]:
    issues = []
    if wire.get("function") not in {"signal", "power", "ground"}:
        issues.append("wire_function_unknown")
    voltage = wire.get("voltage_v")
    if type(voltage) not in {int, float} or not math.isfinite(voltage) or voltage < 0:
        issues.append("wire_voltage_unknown")
    if wire.get("function") in {"power", "ground"}:
        current = wire.get("expected_current_ma")
        if not _number(current):
            issues.append("power_current_unknown")
        for key in ("wire_current_limit_ma", "contact_current_limit_ma"):
            limit = wire.get(key)
            if not _number(limit):
                issues.append(f"{key}_unknown")
            elif _number(current) and current > limit:
                issues.append(f"{key}_exceeded")
    return issues
