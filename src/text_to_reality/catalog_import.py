"""Validate research batches into the existing boards.json format, without fit promotion.

Source provenance is checked before merging. This module neither downloads nor
executes research files and never changes connector-model approval.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import re
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlsplit

MAX_FILE_BYTES = 32 * 1024 * 1024
MAX_BATCH_RECORDS = 500
_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
_SHA = re.compile(r"^[0-9a-f]{64}$")


class CatalogImportError(ValueError):
    """A research batch that cannot be safely merged."""


def encoded(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode()


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _no_symlinks(path: Path) -> None:
    for part in (path, *path.parents):
        if part.is_symlink():
            raise CatalogImportError("Symlinked paths are not accepted")


def _decode_json(content: bytes, label: str) -> Any:
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("Duplicate JSON object key")
            result[key] = value
        return result

    def constant(value):
        raise ValueError("Non-finite JSON number")

    try:
        return json.loads(content.decode("utf-8"), object_pairs_hook=pairs, parse_constant=constant,
                          parse_float=lambda value: float(value) if math.isfinite(float(value)) else constant(value))
    except (ValueError, UnicodeError) as error:
        raise CatalogImportError(f"Invalid JSON: {label}") from error


def read_json(path: Path) -> Any:
    _no_symlinks(path)
    if not path.is_file():
        raise CatalogImportError(f"Expected a regular JSON file: {path.name}")
    content = path.read_bytes()
    if len(content) > MAX_FILE_BYTES:
        raise CatalogImportError(f"JSON file exceeds byte budget: {path.name}")
    return _decode_json(content, path.name)


def _relative_file(root: Path, name: Any) -> Path:
    if not isinstance(name, str):
        raise CatalogImportError("Source paths must be relative POSIX strings")
    rel = PurePosixPath(name)
    if (rel.is_absolute() or ".." in rel.parts or "\\" in name or ":" in name
            or "\x00" in name or rel.as_posix() != name or name in {"", "."}):
        raise CatalogImportError("Unsafe source path")
    _no_symlinks(root)
    current = root
    for part in rel.parts:
        current = current / part
        if current.is_symlink():
            raise CatalogImportError("Symlinked research files are not accepted")
    if not current.is_file() or not current.resolve().is_relative_to(root.resolve()):
        raise CatalogImportError(f"Missing source file: {name}")
    if current.stat().st_size > MAX_FILE_BYTES:
        raise CatalogImportError(f"Source exceeds byte budget: {name}")
    return current


def verify_sources(root: Path, manifest: Any) -> dict[str, Any]:
    if not isinstance(manifest, dict) or not isinstance(manifest.get("files"), list):
        raise CatalogImportError("Source manifest needs a files list with path, bytes and sha256")
    if not 1 <= len(manifest["files"]) <= 2000:
        raise CatalogImportError("Source manifest file count is outside budget")
    source_json = {}
    seen = set()
    for file in manifest["files"]:
        if not isinstance(file, dict) or not isinstance(file.get("sha256"), str) or not _SHA.fullmatch(file["sha256"]):
            raise CatalogImportError("Manifest SHA-256 must be a lowercase hex digest")
        path = _relative_file(root, file.get("path"))
        if file["path"] in seen:
            raise CatalogImportError("Duplicate manifest source path")
        seen.add(file["path"])
        size = file.get("bytes", file.get("size_bytes"))
        if type(size) is not int or size < 0:
            raise CatalogImportError("Manifest byte size must be a non-negative integer")
        content = path.read_bytes()
        if len(content) != size or digest(content) != file["sha256"]:
            raise CatalogImportError(f"Research source hash/size mismatch: {file['path']}")
        if path.suffix == ".json":
            source_json[file["path"]] = _decode_json(content, file["path"])
    return source_json


def _pointer(value: Any, pointer: Any) -> Any:
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise CatalogImportError("source_record.json_pointer must be an absolute JSON pointer")
    try:
        for token in pointer[1:].split("/"):
            if re.search(r"~(?![01])", token):
                raise CatalogImportError("Malformed JSON pointer escape")
            token = token.replace("~1", "/").replace("~0", "~")
            if isinstance(value, list):
                if not re.fullmatch(r"0|[1-9][0-9]*", token):
                    raise CatalogImportError("JSON pointer array indices must be canonical integers")
                value = value[int(token)]
            elif isinstance(value, dict):
                value = value[token]
            else:
                raise CatalogImportError("JSON pointer does not resolve a record")
        return value
    except (KeyError, IndexError) as error:
        raise CatalogImportError("JSON pointer does not resolve a record") from error


def _manifest_records(manifest: dict[str, Any], sources: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    index = manifest.get("record_index")
    if index is None:
        return {}
    if not isinstance(index, list):
        raise CatalogImportError("Manifest record_index must be a list")
    records = {}
    for entry in index:
        if not isinstance(entry, dict) or entry.get("source_file") not in sources:
            raise CatalogImportError("Record index must reference verified JSON source")
        pointer = entry.get("json_pointer")
        _pointer(sources[entry["source_file"]], pointer)
        identity = (entry["source_file"], pointer)
        if identity in records:
            raise CatalogImportError("Duplicate manifest record identity")
        records[identity] = entry
    total = manifest.get("total_record_count", len(index))
    if type(total) is not int or total != len(index):
        raise CatalogImportError("Manifest total record count disagrees with index")
    if "batches" in manifest:
        batches = manifest["batches"]
        if not isinstance(batches, list):
            raise CatalogImportError("Manifest batches must be a list")
        expected = set()
        for batch in batches:
            if not isinstance(batch, dict) or batch.get("catalog_file") not in sources:
                raise CatalogImportError("Batch catalog must reference verified JSON")
            key = batch.get("records_key")
            entries = sources[batch["catalog_file"]].get(key)
            if not isinstance(entries, list) or type(batch.get("record_count")) is not int or len(entries) != batch["record_count"]:
                raise CatalogImportError("Batch record count disagrees with verified source")
            for i in range(len(entries)):
                expected.add((batch["catalog_file"], "/" + key.replace("~", "~0").replace("/", "~1") + "/" + str(i)))
        if expected != set(records):
            raise CatalogImportError("Manifest batches and record index differ")
    return records


def _reject_approval(value: Any) -> None:
    if isinstance(value, list):
        for item in value:
            _reject_approval(item)
    elif isinstance(value, dict):
        for key, item in value.items():
            if key in {"original_record", "original_header"}:
                continue  # Exact preserved source prose is evidence, never operational approval.
            normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", key).lower().replace("-", "_")
            if normalized in {"fit_approved", "physical_validation", "physically_validated", "physically_verified", "fit_verified", "physical_fit_verified", "automatic_fit_eligible", "direct_comb_fit", "comb_qualified", "revision_verified", "qualified", "approved"} and item is not False and item is not None:
                raise CatalogImportError("Research cannot approve physical fit or qualification")
            if normalized in {"fit_status", "mechanical_fit"} and item is not None and not isinstance(item, str):
                raise CatalogImportError("Normalized qualification states must be strings or null")
            if normalized in {"fit_status", "mechanical_fit"} and isinstance(item, str) and item.strip().lower() not in {
                "unknown", "unverified", "unresolved", "not_validated", "not validated", "not_certified",
                "unqualified", "candidate", "research_only", "planning_only_model_unresolved"
            }:
                raise CatalogImportError("Research cannot promote qualification state")
            if normalized in {"qualification", "state", "level"} and isinstance(item, str) and item.strip().lower() in {
                "approved", "qualified", "certified", "verified", "validated", "physical_verified", "physically_validated"
            }:
                raise CatalogImportError("Research cannot promote qualification state")
            if normalized in {"approved_model_revision", "retention_motion"} and item is not None:
                raise CatalogImportError("Research cannot select an approved connector model or latch motion")
            _reject_approval(item)


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CatalogImportError(f"{label} must be a non-empty string")
    return value


def _source_groups(original: dict[str, Any]) -> list[dict[str, Any]]:
    groups = original.get("header_groups", original.get("headers", []))
    if not isinstance(groups, list):
        raise CatalogImportError("Source physical header groups must be a list")
    for field in ("auxiliary_connectors", "other_connectors", "other_exposed_pads"):
        auxiliary = original.get(field, [])
        if not isinstance(auxiliary, list):
            raise CatalogImportError("Source auxiliary connectors must be a list")
        groups = groups + auxiliary
    return groups


def _normalization(header: dict[str, Any], original: dict[str, Any]) -> None:
    raw = header.get("original_header")
    groups = _source_groups(original)
    if not isinstance(raw, dict) or not isinstance(groups, list) or not any(encoded(raw) == encoded(group) for group in groups):
        raise CatalogImportError("Every normalized header must preserve one exact original header group")
    rows = raw.get("rows", raw.get("row_count"))
    pins = raw.get("pins_per_row", raw.get("positions", raw.get("pin_count")))
    if isinstance(pins, list) and rows == 1 and len(pins) == 1:
        pins = pins[0]
        if raw.get("pin_count", pins) != pins:
            raise CatalogImportError("Source pin count disagrees with physical row positions")
    if type(rows) is not int or rows < 1 or type(header.get("rows")) is not int or header["rows"] != rows:
        raise CatalogImportError("Header normalization changes or guesses row topology")
    if type(pins) is not int or type(header.get("pin_count")) is not int or header["pin_count"] < 1 or header["pin_count"] != pins:
        raise CatalogImportError("Header normalization changes full-row positions or flattens a multirow header")
    if raw.get("pitch_mm") is not None and type(raw["pitch_mm"]) not in {int, float}:
        raise CatalogImportError("Raw header pitch has invalid numeric type")
    pitch = header.get("pitch_mm")
    if pitch is not None and (type(pitch) not in {int, float} or not math.isfinite(pitch) or pitch <= 0):
        raise CatalogImportError("Header pitch must be a positive finite number or null")
    if pitch != raw.get("pitch_mm"):
        raise CatalogImportError("Header normalization promotes unknown or different pitch")
    gender = raw.get("gender", original.get("gender"))
    if header.get("gender") != gender:
        raise CatalogImportError("Header normalization changes descriptive mating gender")
    shrouded = raw.get("shrouded")
    if shrouded is not None and type(shrouded) is not bool or header.get("shrouded") is not None and type(header["shrouded"]) is not bool:
        raise CatalogImportError("Shroud state must be a boolean or null")
    if header.get("shrouded") != shrouded:
        raise CatalogImportError("Header normalization guesses shroud status")
    for field in ("confidence", "pitch_evidence"):
        expected = raw.get(field, original.get(field))
        if header.get(field) != expected:
            raise CatalogImportError(f"Header normalization changes source {field}")
    if header.get("preinstalled") is True and raw.get("preinstalled") is not True:
        raise CatalogImportError("Research normalization cannot approve installed-header state")


def _record(record: Any, sources: dict[str, Any]) -> None:
    if not isinstance(record, dict):
        raise CatalogImportError("Every board record must be an object")
    if not isinstance(record.get("id"), str) or not _ID.fullmatch(record["id"]):
        raise CatalogImportError("Board ID must be a stable lowercase exact-variant identifier")
    _text(record.get("name"), "Board name")
    if not isinstance(record.get("aliases"), list) or any(not isinstance(a, str) or not a.strip() for a in record["aliases"]):
        raise CatalogImportError("aliases must be a list of non-empty strings")
    if record.get("kind") not in {"board", "module"}:
        raise CatalogImportError("kind must be board or module")
    if "revision" not in record or record["revision"] is not None and not isinstance(record["revision"], str):
        raise CatalogImportError("revision must be an explicit string or null, never guessed")
    evidence = record.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        raise CatalogImportError("Every research record needs primary-source evidence URLs")
    for item in evidence:
        url = item.get("url") if isinstance(item, dict) else None
        if not isinstance(url, str) or urlsplit(url).scheme != "https" or not urlsplit(url).netloc or urlsplit(url).username is not None:
            raise CatalogImportError("Evidence URLs must be HTTPS URLs without credentials")
    provenance = record.get("source_record")
    if not isinstance(provenance, dict) or provenance.get("file") not in sources:
        raise CatalogImportError("source_record.file must reference a hash-verified JSON source")
    original = _pointer(sources[provenance["file"]], provenance.get("json_pointer"))
    if not isinstance(original, dict) or json.dumps(original, sort_keys=True, allow_nan=False) != json.dumps(record.get("original_record"), sort_keys=True, allow_nan=False):
        raise CatalogImportError("original_record differs from the preserved source record")
    if record.get("confidence") != original.get("confidence"):
        raise CatalogImportError("Board confidence must preserve the source qualification")
    original_unknowns = original.get("unknowns", original.get("unresolved"))
    if original_unknowns is not None and record.get("unresolved") != original_unknowns:
        raise CatalogImportError("Board unresolved qualifications must preserve source unknowns")
    source_revision = original.get("revision", original.get("revision_scope", original.get("board_revision")))
    if record["revision"] is not None and record["revision"] != source_revision:
        raise CatalogImportError("Research normalization cannot invent or replace board revision")
    def source_urls(value):
        if isinstance(value, str):
            return {value} if value.startswith("https://") else set()
        if isinstance(value, dict):
            return set().union(*(source_urls(item) for item in value.values()))
        if isinstance(value, list):
            return set().union(*(source_urls(item) for item in value))
        return set()

    if any(item["url"] not in source_urls(original) for item in evidence):
        raise CatalogImportError("Normalized evidence URL is absent from exact source record")
    if not isinstance(record.get("headers"), list):
        raise CatalogImportError("headers must preserve a list of separate physical groups")
    seen = set()
    for header in record["headers"]:
        if not isinstance(header, dict):
            raise CatalogImportError("Header must be an object")
        id = _text(header.get("id"), "Header ID")
        if id in seen:
            raise CatalogImportError("Duplicate physical header ID")
        seen.add(id)
        _normalization(header, original)
    excluded = record.get("excluded_headers", [])
    if not isinstance(excluded, list) or any(not isinstance(h, dict) or not isinstance(h.get("original_header"), dict)
                                            or not isinstance(h.get("reason"), str) or not h["reason"].strip() for h in excluded):
        raise CatalogImportError("Excluded groups require exact original_header and a reason")
    represented = [h["original_header"] for h in record["headers"]] + [h["original_header"] for h in excluded]
    groups = _source_groups(original)
    if not isinstance(groups, list) or sorted(encoded(h) for h in represented) != sorted(encoded(h) for h in groups):
        raise CatalogImportError("Normalized and excluded headers must cover every source group exactly once")
    _reject_approval(record)


def ambiguous_labels(records: list[dict[str, Any]]) -> dict[str, list[str]]:
    labels: dict[str, set[str]] = {}
    for record in records:
        for label in [record["name"], *record["aliases"]]:
            labels.setdefault(label.strip().lower(), set()).add(record["id"])
    return {label: sorted(ids) for label, ids in sorted(labels.items()) if len(ids) > 1}


def normalize_research_proposal(proposal: Any) -> tuple[Any, list[dict[str, Any]]]:
    """Bridge known research representations without guessing new facts.

    Exact originals remain untouched. This is optional and independently
    followed by every source/identity/qualification validation in prepare_import.
    """
    normalized = copy.deepcopy(proposal)
    if not isinstance(normalized, dict) or not isinstance(normalized.get("boards"), list):
        raise CatalogImportError("Proposal needs the existing boards list")
    adjustments = []
    for record in normalized["boards"]:
        if not isinstance(record, dict) or not isinstance(record.get("original_record"), dict):
            raise CatalogImportError("Normalization requires preserved source records")
        raw = record["original_record"]
        changes = []
        if record.get("kind") not in {"board", "module"}:
            record["kind"] = "board" if record.get("kind") == "development_board" else "module"
            changes.append("Map research category to board/module; raw kind preserved")
        if isinstance(record.get("revision"), dict):
            if record["revision"] != raw.get("revision"):
                raise CatalogImportError("Revision evidence differs from source")
            record["revision_evidence"] = record["revision"]
            record["revision"] = None
            changes.append("Preserve CAD revision object as evidence; actual board revision null")
        evidence = []
        for item in record.get("evidence", []):
            if isinstance(item, str):
                item = {"url": item}
                changes.append("Wrap exact source URL")
            elif isinstance(item, dict) and "url" not in item and isinstance(item.get("cad_url"), str):
                item = {**item, "url": item["cad_url"]}
                changes.append("Map exact cad_url evidence to url")
            elif (isinstance(item, dict) and "url" not in item and isinstance(item.get("image_sources"), list)
                  and item["image_sources"] and isinstance(raw.get("source"), str)):
                item = {**item, "url": raw["source"]}
                changes.append("Attach exact source product URL to preserved image evidence")
            evidence.append(item)
        record["evidence"] = evidence
        for header in record.get("headers", []):
            if not isinstance(header, dict) or not isinstance(header.get("original_header"), dict):
                raise CatalogImportError("Normalization requires exact original headers")
            for field in ("confidence", "pitch_evidence"):
                expected = header["original_header"].get(field, raw.get(field))
                if header.get(field) != expected:
                    header[field] = expected
                    changes.append(f"{header.get('id')}: preserve source {field}")
        if record.get("confidence") != raw.get("confidence"):
            record["confidence"] = raw.get("confidence")
            changes.append("Preserve source board confidence")
        unknowns = raw.get("unknowns", raw.get("unresolved"))
        if unknowns is not None and record.get("unresolved") != unknowns:
            record["unresolved"] = unknowns
            changes.append("Preserve source unresolved qualifications")
        if changes:
            adjustments.append({"id": record.get("id"), "changes": changes})
    return normalized, adjustments


def prepare_import(existing: Any, proposal: Any, source_root: Path, manifest: Any,
                   batch_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    if not _ID.fullmatch(batch_id):
        raise CatalogImportError("batch_id must be a stable lowercase identifier")
    for value, name in ((existing, "catalog"), (proposal, "proposal")):
        if not isinstance(value, dict) or type(value.get("schemaVersion")) is not int or value["schemaVersion"] != 1 or not isinstance(value.get("boards"), list):
            raise CatalogImportError(f"{name} must use the existing schemaVersion 1 boards format")
    if not 1 <= len(proposal["boards"]) <= MAX_BATCH_RECORDS:
        raise CatalogImportError("Research batch record count is outside budget")
    _reject_approval(proposal)
    sources = verify_sources(source_root, manifest)
    record_index = _manifest_records(manifest, sources)
    ids = [item.get("id") for item in existing["boards"] if isinstance(item, dict)]
    if len(ids) != len(existing["boards"]) or any(not isinstance(id, str) or not _ID.fullmatch(id) for id in ids) or len(set(ids)) != len(ids):
        raise CatalogImportError("Existing catalog contains duplicate or malformed identities")
    for item in existing["boards"]:
        if not isinstance(item.get("name"), str) or not isinstance(item.get("aliases"), list) or any(not isinstance(a, str) for a in item["aliases"]):
            raise CatalogImportError("Existing catalog contains malformed labels")
    merged = copy.deepcopy(existing)
    by_id = {record["id"]: record for record in merged["boards"]}
    source_identities = {(r["source_record"]["file"], r["source_record"]["json_pointer"]): r["id"]
                         for r in existing["boards"] if isinstance(r.get("source_record"), dict)}
    incoming = set()
    added, replayed = [], []
    for record in proposal["boards"]:
        _record(record, sources)
        id = record["id"]
        provenance = record["source_record"]
        source_identity = (provenance["file"], provenance["json_pointer"])
        if record_index and (source_identity not in record_index or record_index[source_identity].get("normalized_id", id) != id):
            raise CatalogImportError("Incoming record identity differs from source manifest index")
        if source_identity in source_identities and source_identities[source_identity] != id:
            raise CatalogImportError("One source record cannot invent multiple variant identities")
        source_identities[source_identity] = id
        if id in incoming:
            raise CatalogImportError("Research batch contains duplicate board IDs")
        incoming.add(id)
        if id in by_id:
            if by_id[id] != record:
                raise CatalogImportError(f"Existing ID {id} conflicts with research; preserve it and use an exact distinct variant/revision ID")
            replayed.append(id)
        else:
            merged["boards"].append(copy.deepcopy(record))
            by_id[id] = record
            added.append(id)
    audit = {"batch_id": batch_id, "proposal_sha256": digest(encoded(proposal)),
             "source_manifest_sha256": digest(encoded(manifest)), "hash_encoding": "canonical_indent2_utf8_json_with_newline", "records": len(incoming),
             "physical_validation": False}
    imports = merged.setdefault("catalog_imports", [])
    if not isinstance(imports, list):
        raise CatalogImportError("Existing catalog_imports must be a list")
    previous = next((item for item in imports if isinstance(item, dict) and item.get("batch_id") == batch_id), None)
    if previous is not None and previous != audit:
        raise CatalogImportError("Batch ID already identifies different source bytes")
    if previous is None:
        imports.append(audit)
    report = {"batch_id": batch_id, "added_ids": added, "identical_replay_ids": replayed,
              "existing_ids_preserved": len(existing["boards"]), "catalog_records": len(merged["boards"]),
              "verified_source_files": len(manifest["files"]), "ambiguous_labels": ambiguous_labels(merged["boards"]),
              "catalog_sha256": digest(encoded(merged)), "physical_validation": False,
              "model_approval_modified": False, "status": "validated_research_only"}
    return merged, report


def write_catalog(path: Path, content: bytes, *, expected_sha256: str | None = None) -> None:
    """Publish a candidate exclusively or update the exact user-selected catalog with a guard."""
    _no_symlinks(path)
    if path.exists():
        before = path.read_bytes()
        if before == content:
            return
        if expected_sha256 is None or digest(before) != expected_sha256:
            raise CatalogImportError("Output exists or changed; provide its exact expected SHA-256")
    elif expected_sha256 is not None:
        raise CatalogImportError("Expected catalog is absent")
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        stream.write(content)
        temporary = Path(stream.name)
    try:
        if path.exists():
            if expected_sha256 is None or digest(path.read_bytes()) != expected_sha256:
                raise CatalogImportError("Output changed before publication")
            os.chmod(temporary, path.stat().st_mode & 0o777)
            os.replace(temporary, path)
        else:
            os.chmod(temporary, 0o644)
            os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
