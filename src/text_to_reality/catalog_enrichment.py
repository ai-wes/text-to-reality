"""Explicit source-bound descriptive enrichment of the existing boards catalog.

This operation never changes physical qualification or original provenance.
It is separate from insertion and requires exact record/field preconditions.
"""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from .catalog_import import (
    CatalogImportError,
    _normalization,
    _pointer,
    _reject_approval,
    digest,
    encoded,
    verify_sources,
)

_FIELDS = frozenset({"gender", "population"})
_SCOPE = ("id", "manufacturer", "sku", "revision", "assembly_variants")


def scope(record: dict[str, Any]) -> dict[str, Any]:
    """An explicit projection; nullable missing scope values do not establish fit."""
    return {field: (record.get(field) if record.get(field) is not None or field not in {"manufacturer", "sku"}
                    else record.get("original_record", {}).get(field)) for field in _SCOPE}


def _same(left: Any, right: Any) -> bool:
    return json.dumps(left, sort_keys=True, allow_nan=False) == json.dumps(right, sort_keys=True, allow_nan=False)


def _urls(value: Any) -> set[str]:
    if isinstance(value, str):
        return {value} if value.startswith("https://") else set()
    if isinstance(value, dict):
        return set().union(*(_urls(item) for item in value.values()))
    if isinstance(value, list):
        return set().union(*(_urls(item) for item in value))
    return set()


def _claim(change: dict[str, Any], record: dict[str, Any], sources: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    provenance = change.get("source_record")
    if not isinstance(provenance, dict) or provenance.get("file") not in sources:
        raise CatalogImportError("Enrichment needs hash-verified source_record")
    original = _pointer(sources[provenance["file"]], provenance.get("json_pointer"))
    if isinstance(original, dict) and "source_guard" in original and "original_update" in original:
        return _photo_claim(change, record, original, sources, manifest)
    if not isinstance(original, dict) or not _same(scope(original), scope(record)):
        raise CatalogImportError("Enrichment source variant/revision/SKU/assembly scope differs")
    pointer = change.get("source_field_pointer")
    if not isinstance(pointer, str) or not pointer.endswith("/" + change["field"]):
        raise CatalogImportError("Enrichment source field pointer must name the exact changed field")
    source_header = _pointer(original, pointer.rsplit("/", 1)[0])
    if not isinstance(source_header, dict) or source_header.get("id") != change["header_id"]:
        raise CatalogImportError("Enrichment source header identity differs")
    value = _pointer(original, pointer)
    if not _same(value, change["after"]):
        raise CatalogImportError("Enrichment value differs from the literal source claim")
    target = next(header for header in record["headers"] if header["id"] == change["header_id"])
    for field in ("rows", "pin_count", "pitch_mm"):
        if field not in source_header or not _same(source_header[field], target.get(field)):
            raise CatalogImportError("Enrichment source changes or lacks physical topology")
    evidence = change.get("evidence_urls")
    if not isinstance(evidence, list) or not evidence:
        raise CatalogImportError("Enrichment requires primary evidence URLs")
    for url in evidence:
        try:
            parsed = urlsplit(url) if isinstance(url, str) else None
        except ValueError as error:
            raise CatalogImportError("Invalid enrichment evidence URL") from error
        if parsed is None or parsed.scheme != "https" or not parsed.netloc or parsed.username is not None or url not in _urls(original):
            raise CatalogImportError("Enrichment evidence URL is absent from exact source")
    return {"source_record": copy.deepcopy(provenance), "source_field_pointer": pointer,
            "source_original_record": copy.deepcopy(original), "evidence_urls": copy.deepcopy(evidence)}


def _canonical_source_sha(value: Any) -> str:
    return digest(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode())


def _photo_claim(change: dict[str, Any], record: dict[str, Any], proposal: dict[str, Any],
                 sources: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    """Validate the supplied guarded photograph patch against preserved old sources."""
    _reject_approval(proposal)
    files = {item["path"]: item for item in manifest["files"]}
    guard = proposal.get("source_guard", {})
    file = guard.get("file")
    if file not in sources or files[file]["sha256"] != guard.get("file_sha256"):
        raise CatalogImportError("Photograph enrichment original source-file guard differs")
    old = _pointer(sources[file], guard.get("json_pointer"))
    if (not _same(old, record.get("original_record")) or _canonical_source_sha(old) != guard.get("record_canonical_sha256")
            or record.get("source_record") != {"file": file, "json_pointer": guard.get("json_pointer")}):
        raise CatalogImportError("Photograph enrichment original record or provenance guard differs")
    if (proposal.get("record_id") != record["id"] or proposal.get("sku") != scope(record)["sku"]
            or proposal.get("revision_scope") != record.get("revision")):
        raise CatalogImportError("Photograph enrichment variant/revision/SKU scope differs")
    provenance = proposal.get("source_update", {})
    if provenance.get("file") not in sources:
        raise CatalogImportError("Photograph enrichment update source is not verified")
    update = _pointer(sources[provenance["file"]], provenance.get("json_pointer"))
    if not _same(update, proposal.get("original_update")) or update.get("record_id") != record["id"] or update.get("sku") != scope(record)["sku"]:
        raise CatalogImportError("Photograph enrichment exact update or SKU differs")
    for field in ("revision", "revision_scope", "manufacturer", "assembly_variants"):
        expected = record.get("revision") if field in {"revision", "revision_scope"} else scope(record)[field]
        if field in update and not _same(update[field], expected):
            raise CatalogImportError("Photograph enrichment raw update scope contradicts the target")
    match = re.fullmatch(r"/changes/(0|[1-9][0-9]*)/fields/(gender|population)", change.get("source_field_pointer", ""))
    if match is None or match[2] != change["field"]:
        raise CatalogImportError("Photograph enrichment pointer must select the literal field")
    i = int(match[1])
    try:
        proposed = proposal["changes"][i]
        literal = update["changes"][i]
    except (IndexError, KeyError, TypeError) as error:
        raise CatalogImportError("Photograph enrichment change is absent") from error
    target = next(h for h in record["headers"] if h["id"] == change["header_id"])
    if (proposed.get("selector") != {"header_id": change["header_id"]} or literal.get("selector") != proposed["selector"]
            or _canonical_source_sha(target.get("original_header")) != proposed.get("original_header_canonical_sha256")
            or not _same(proposed.get("fields"), literal.get("fields"))
            or not _same(proposed["fields"].get(change["field"]), change["after"])
            or not _same(proposed.get("expected_old_fields", {}).get(change["field"]), change["before"])):
        raise CatalogImportError("Photograph enrichment header, literal value or precondition differs")
    if set(proposed["fields"]) - _FIELDS or change["field"] not in proposed.get("expected_old_fields", {}):
        raise CatalogImportError("Photograph enrichment changes fields outside allowlist")
    check_header = copy.deepcopy(target)
    check_header["gender"] = target["original_header"].get("gender", old.get("gender"))
    _normalization(check_header, old)
    seal = proposal.get("expected_wave4_normalized_source", {})
    sealed_file = "wave4-source/" + str(seal.get("file", ""))
    if sealed_file not in sources or files[sealed_file]["sha256"] != seal.get("file_sha256"):
        raise CatalogImportError("Photograph enrichment sealed proposal file guard differs")
    sealed = [entry for entry in sources[sealed_file].get("boards", []) if entry.get("id") == record["id"]]
    if len(sealed) != 1 or _canonical_source_sha(sealed[0]) != seal.get("record_canonical_sha256"):
        raise CatalogImportError("Photograph enrichment sealed proposal record guard differs")
    if proposal.get("source_record") != provenance:
        raise CatalogImportError("Photograph enrichment update source pointers differ")
    evidence = proposal.get("evidence")
    if not isinstance(evidence, dict) or not _same(evidence, update.get("evidence")):
        raise CatalogImportError("Photograph enrichment evidence differs from source")
    urls = [evidence.get("product_url"), evidence.get("image_url")]
    if not _same(change.get("evidence_urls"), urls):
        raise CatalogImportError("Photograph enrichment primary URLs differ")
    for url in urls:
        try:
            parsed = urlsplit(url) if isinstance(url, str) else None
        except ValueError as error:
            raise CatalogImportError("Invalid photograph evidence URL") from error
        if parsed is None or parsed.scheme != "https" or not parsed.netloc or parsed.username is not None:
            raise CatalogImportError("Invalid photograph primary URL")
    image_name = Path(evidence.get("image_local", "")).name
    images = [item for item in manifest["files"] if Path(item["path"]).name == image_name and item["sha256"] == evidence.get("image_sha256")]
    if len(images) != 1:
        raise CatalogImportError("Photograph enrichment exact image is absent or ambiguous")
    return {"source_record": copy.deepcopy(change["source_record"]), "source_field_pointer": change["source_field_pointer"],
            "source_original_record": copy.deepcopy(proposal), "source_original_update": copy.deepcopy(update),
            "original_source_record": copy.deepcopy(old), "image_source": copy.deepcopy(images[0]), "evidence_urls": urls}


def normalize_photo_patch(existing: Any, proposal: Any, proposal_file: str, enrichment_id: str) -> dict[str, Any]:
    """Bind the sealed photo proposal to this runtime, never to a source-record hash.

    prepare_enrichment validates all resulting guards and proof before a write.
    Existing audited preimages are reused solely to prepare an identical replay.
    """
    if (not isinstance(existing, dict) or not isinstance(existing.get("boards"), list)
            or not isinstance(proposal, dict) or type(proposal.get("schemaVersion")) is not int
            or proposal["schemaVersion"] != 1 or not isinstance(proposal.get("patches"), list)):
        raise CatalogImportError("Photo preparation requires the canonical catalog and guarded proposal")
    records = {record["id"]: record for record in existing["boards"]}
    previous = next((audit for audit in existing.get("catalog_enrichments", [])
                     if isinstance(audit, dict) and audit.get("enrichment_id") == enrichment_id), None)
    updates = []
    for i, item in enumerate(proposal["patches"]):
        if not isinstance(item, dict) or item.get("record_id") not in records:
            raise CatalogImportError("Photo preparation requires an existing exact board ID")
        record = records[item["record_id"]]
        audit_record = next((entry for entry in previous.get("records", []) if entry.get("board_id") == record["id"]), None) if previous else None
        changes = []
        for j, item_change in enumerate(item.get("changes", [])):
            id = item_change.get("selector", {}).get("header_id")
            header = next((h for h in record.get("headers", []) if h.get("id") == id), None)
            if header is None or not isinstance(item_change.get("fields"), dict):
                raise CatalogImportError("Photo preparation requires an existing exact header")
            for field, value in item_change["fields"].items():
                if field not in _FIELDS or field not in item_change.get("expected_old_fields", {}):
                    raise CatalogImportError("Photo preparation permits only guarded gender/population")
                logged = next((entry for entry in audit_record.get("changes", [])
                               if entry.get("header_id") == id and entry.get("field") == field), None) if audit_record else None
                changes.append({"header_id": id, "field": field, "before_present": logged["before_present"] if logged else field in header,
                                "before": item_change["expected_old_fields"][field], "after": value,
                                "source_record": {"file": proposal_file, "json_pointer": f"/patches/{i}"},
                                "source_field_pointer": f"/changes/{j}/fields/{field}",
                                "evidence_urls": [item.get("evidence", {}).get("product_url"), item.get("evidence", {}).get("image_url")]})
        updates.append({"board_id": record["id"], "scope": scope(record),
                        "expected_record_sha256": audit_record["before_sha256"] if audit_record else digest(encoded(record)), "changes": changes})
    return {"schemaVersion": 1, "updates": updates}


def prepare_enrichment(existing: Any, patch: Any, source_root: Path, manifest: Any,
                       enrichment_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    if not isinstance(enrichment_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,127}", enrichment_id):
        raise CatalogImportError("Enrichment ID must be stable lowercase identity")
    if not isinstance(existing, dict) or type(existing.get("schemaVersion")) is not int or existing["schemaVersion"] != 1 or not isinstance(existing.get("boards"), list):
        raise CatalogImportError("Enrichment requires the existing schemaVersion 1 catalog")
    if (not isinstance(patch, dict) or type(patch.get("schemaVersion")) is not int or patch["schemaVersion"] != 1
            or not isinstance(patch.get("updates"), list) or not 1 <= len(patch["updates"]) <= 100):
        raise CatalogImportError("Enrichment requires one to 100 explicit updates")
    _reject_approval(patch)
    sources = verify_sources(source_root, manifest)
    merged = copy.deepcopy(existing)
    by_id = {}
    for record in merged["boards"]:
        if not isinstance(record, dict) or not isinstance(record.get("id"), str) or record["id"] in by_id:
            raise CatalogImportError("Existing catalog identities are malformed or duplicated")
        by_id[record["id"]] = record
    audits = merged.setdefault("catalog_enrichments", [])
    if not isinstance(audits, list):
        raise CatalogImportError("Existing enrichment audit must be a list")
    fingerprint = {"enrichment_id": enrichment_id, "patch_sha256": digest(encoded(patch)),
                   "source_manifest_sha256": digest(encoded(manifest)), "physical_validation": False}
    previous = [audit for audit in audits if isinstance(audit, dict) and audit.get("enrichment_id") == enrichment_id]
    if len(previous) > 1:
        raise CatalogImportError("Duplicate enrichment audit identity")
    if previous:
        audit = previous[0]
        if set(audit) != {*fingerprint, "records", "hash_encoding"} or audit.get("hash_encoding") != "canonical_indent2_utf8_json_with_newline":
            raise CatalogImportError("Enrichment replay audit shape or hash encoding changed")
        if any(not _same(audit.get(field), value) for field, value in fingerprint.items()):
            raise CatalogImportError("Enrichment ID identifies a different request or source")
        items = audit.get("records")
        if not isinstance(items, list) or len(items) != len(patch["updates"]):
            raise CatalogImportError("Enrichment replay audit is incomplete")
        for item, update in zip(items, patch["updates"]):
            if (not isinstance(item, dict) or not isinstance(update, dict)
                    or item.get("board_id") != update.get("board_id") or item.get("board_id") not in by_id
                    or item.get("before_sha256") != update.get("expected_record_sha256")):
                raise CatalogImportError("Enrichment replay identities or preimages differ")
            record = by_id[item["board_id"]]
            if set(item) != {"board_id", "before_sha256", "after_sha256", "scope", "changes"} or not _same(item.get("scope"), scope(record)):
                raise CatalogImportError("Enrichment replay audited scope or shape changed")
            if digest(encoded(record)) != item.get("after_sha256"):
                raise CatalogImportError("Enriched record changed after this request; replay requires the exact postimage")
            if not _same(update.get("scope"), scope(record)):
                raise CatalogImportError("Enrichment replay scope changed")
            restored = copy.deepcopy(record)
            changes = update.get("changes")
            if not isinstance(changes, list) or not isinstance(item.get("changes"), list) or len(changes) != len(item["changes"]):
                raise CatalogImportError("Enrichment replay field audit is incomplete")
            for claim, logged in zip(changes, item["changes"]):
                if not isinstance(claim, dict) or not isinstance(logged, dict):
                    raise CatalogImportError("Enrichment replay field audit is malformed")
                if claim.get("field") not in _FIELDS:
                    raise CatalogImportError("Enrichment replay field is outside allowlist")
                actual = next((h for h in record["headers"] if h["id"] == claim.get("header_id")), None)
                if actual is None or claim["field"] not in actual or not _same(actual[claim["field"]], claim.get("after")):
                    raise CatalogImportError("Enrichment replay target differs from the claimed postimage")
                proof = _claim(claim, record, sources, manifest)
                expected = {"header_id": claim["header_id"], "field": claim["field"],
                            "before_present": claim["before_present"], "before": claim["before"],
                            "after": claim["after"], **proof}
                if not _same(logged, expected):
                    raise CatalogImportError("Enrichment replay source or field audit differs")
                target = next(h for h in restored["headers"] if h["id"] == claim["header_id"])
                if claim["before_present"] is True:
                    target[claim["field"]] = claim["before"]
                elif claim["before_present"] is False:
                    target.pop(claim["field"], None)
                else:
                    raise CatalogImportError("Enrichment replay presence marker is invalid")
            if digest(encoded(restored)) != item["before_sha256"]:
                raise CatalogImportError("Enrichment replay changes do not reconstruct the original record")
        return merged, {"enrichment_id": enrichment_id, "status": "identical_replay", "updated_ids": [],
                        "physical_validation": False, "catalog_sha256": digest(encoded(merged))}
    affected = set()
    records = []
    for update in patch["updates"]:
        if not isinstance(update, dict) or set(update) != {"board_id", "expected_record_sha256", "scope", "changes"}:
            raise CatalogImportError("Enrichment update fields are explicit and restricted")
        id = update["board_id"]
        if not isinstance(id, str) or id not in by_id or id in affected:
            raise CatalogImportError("Enrichment requires separate existing unique board IDs")
        affected.add(id)
        record = by_id[id]
        before = digest(encoded(record))
        if update["expected_record_sha256"] != before:
            raise CatalogImportError("Enrichment target record hash is stale")
        if not _same(update["scope"], scope(record)):
            raise CatalogImportError("Enrichment declared variant/revision/SKU scope differs")
        changes = update["changes"]
        if not isinstance(changes, list) or not 1 <= len(changes) <= 100:
            raise CatalogImportError("Enrichment needs explicit field changes")
        headers = record.get("headers")
        if not isinstance(headers, list) or any(not isinstance(h, dict) for h in headers):
            raise CatalogImportError("Enrichment requires existing physical headers")
        headers_by_id = {h.get("id"): h for h in headers}
        if len(headers_by_id) != len(headers):
            raise CatalogImportError("Existing physical header IDs are duplicated")
        seen = set()
        evidence_log = []
        for change in changes:
            if not isinstance(change, dict) or set(change) != {"header_id", "field", "before_present", "before", "after", "source_record", "source_field_pointer", "evidence_urls"}:
                raise CatalogImportError("Enrichment field changes have an exact restricted shape")
            field = change["field"]
            header_id = change["header_id"]
            if not isinstance(field, str) or field not in _FIELDS or not isinstance(header_id, str) or header_id not in headers_by_id:
                raise CatalogImportError("Only existing header gender/population can be enriched")
            identity = (header_id, field)
            if identity in seen:
                raise CatalogImportError("Duplicate enrichment field")
            seen.add(identity)
            target = headers_by_id[header_id]
            if type(change["before_present"]) is not bool or change["before_present"] != (field in target) or not _same(change["before"], target.get(field)):
                raise CatalogImportError("Enrichment field precondition differs, including missing versus null")
            value = change["after"]
            if not isinstance(value, str) or not value.strip() or _same(value, target.get(field)):
                raise CatalogImportError("Enrichment needs a changed descriptive source string")
            evidence = _claim(change, record, sources, manifest)
            evidence_log.append({"header_id": header_id, "field": field, "before_present": change["before_present"],
                                 "before": copy.deepcopy(change["before"]), "after": value, **evidence})
            target[field] = value
        _reject_approval(record)
        records.append({"board_id": id, "before_sha256": before, "after_sha256": digest(encoded(record)),
                        "scope": scope(record), "changes": evidence_log})
    audits.append({**fingerprint, "records": records, "hash_encoding": "canonical_indent2_utf8_json_with_newline"})
    return merged, {"enrichment_id": enrichment_id, "updated_ids": sorted(affected), "status": "descriptive_research_only",
                    "physical_validation": False, "model_approval_modified": False, "catalog_sha256": digest(encoded(merged))}
