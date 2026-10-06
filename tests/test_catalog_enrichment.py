import copy
from pathlib import Path

import pytest

from text_to_reality import catalog
from text_to_reality.catalog_enrichment import prepare_enrichment, scope
from text_to_reality.catalog_import import CatalogImportError, digest, encoded
from text_to_reality.cli import main


def setup(tmp_path):
    record = {"id": "sample", "name": "Sample", "aliases": [], "revision": "r1", "sku": "101", "manufacturer": "Maker",
              "assembly_variants": [], "headers": [{"id": "left", "gender": None, "population": None,
                  "rows": 1, "pin_count": 7, "pitch_mm": 2.54, "shrouded": False, "preinstalled": False,
                  "original_header": {"gender": None}}], "fit_status": "unverified",
              "original_record": {"old": "preserved"}, "source_record": {"file": "old.json", "json_pointer": "/boards/0"}}
    existing = {"schemaVersion": 1, "boards": [record]}
    source = {**scope(record), "headers": [{"id": "left", "gender": "male", "population": "factory fitted",
                    "rows": 1, "pin_count": 7, "pitch_mm": 2.54}], "source": "https://maker.example/101"}
    change = {"header_id": "left", "field": "gender", "before_present": True, "before": None, "after": "male",
              "source_record": {"file": "claim.json", "json_pointer": "/boards/0"},
              "source_field_pointer": "/headers/0/gender", "evidence_urls": [source["source"]]}
    patch = {"schemaVersion": 1, "updates": [{"board_id": "sample", "expected_record_sha256": digest(encoded(record)),
                                            "scope": scope(record), "changes": [change]}]}
    manifest = save_source(tmp_path, source)
    return existing, patch, source, manifest


def save_source(tmp_path, source):
    p = tmp_path / "claim.json"
    p.write_bytes(encoded({"boards": [source]}))
    return {"files": [{"path": p.name, "bytes": p.stat().st_size, "sha256": digest(p.read_bytes())}]}


def run(tmp_path, existing, patch, manifest):
    return prepare_enrichment(existing, patch, tmp_path, manifest, "gender-research-r1")


def test_enrichment_preserves_originals_qualification_and_replays(tmp_path, monkeypatch):
    existing, patch, source, manifest = setup(tmp_path)
    before = copy.deepcopy(existing)
    result, report = run(tmp_path, existing, patch, manifest)
    assert existing == before
    expected = copy.deepcopy(existing["boards"][0]);expected["headers"][0]["gender"] = "male"
    assert result["boards"][0] == expected
    assert report["updated_ids"] == ["sample"]
    replay, report = run(tmp_path, result, patch, manifest)
    assert encoded(replay) == encoded(result)
    assert report["status"] == "identical_replay"
    monkeypatch.setattr(catalog, "boards", lambda: result["boards"])
    plan = catalog.connectors_for([{"board": "sample"}])
    assert "header_installation_unverified" in plan["row_checks"][0]["issues"]
    assert plan["physical_validation"] is False
    assert not plan["connectors"][0]["fit_approved"]


@pytest.mark.parametrize("field,value", [("sku", "other"), ("revision", "r2"), ("id", "other"),
                                       ("manufacturer", "Other"), ("assembly_variants", ["header variant"])])
def test_wrong_source_scope_is_rejected(tmp_path, field, value):
    existing, patch, source, _ = setup(tmp_path)
    source[field] = value
    with pytest.raises(CatalogImportError, match="scope differs"):
        run(tmp_path, existing, patch, save_source(tmp_path, source))


@pytest.mark.parametrize("field", ["preinstalled", "fit_status", "pitch_mm", "rows", "pin_count", "confidence", "original_header", "shrouded"])
def test_forbidden_fields_are_rejected(tmp_path, field):
    existing, patch, source, manifest = setup(tmp_path)
    patch["updates"][0]["changes"][0]["field"] = field
    with pytest.raises(CatalogImportError):
        run(tmp_path, existing, patch, manifest)


@pytest.mark.parametrize("field,value", [("rows", 2), ("pin_count", 6), ("pitch_mm", 2.0), ("id", "right"), ("gender", "female")])
def test_wrong_source_header_or_claim_is_rejected(tmp_path, field, value):
    existing, patch, source, _ = setup(tmp_path)
    source["headers"][0][field] = value
    with pytest.raises(CatalogImportError):
        run(tmp_path, existing, patch, save_source(tmp_path, source))


def test_stale_hash_duplicate_fields_and_incomplete_batch_fail_atomically(tmp_path):
    existing, patch, source, manifest = setup(tmp_path)
    unchanged = encoded(existing)
    patch["updates"][0]["expected_record_sha256"] = "0" * 64
    with pytest.raises(CatalogImportError, match="stale"):
        run(tmp_path, existing, patch, manifest)
    assert encoded(existing) == unchanged
    existing, patch, source, manifest = setup(tmp_path)
    patch["updates"][0]["changes"] *= 2
    with pytest.raises(CatalogImportError, match="Duplicate"):
        run(tmp_path, existing, patch, manifest)
    assert encoded(existing) == unchanged
    existing, patch, source, manifest = setup(tmp_path)
    patch["updates"].append({**copy.deepcopy(patch["updates"][0]), "board_id": "missing"})
    with pytest.raises(CatalogImportError):
        run(tmp_path, existing, patch, manifest)
    assert encoded(existing) == unchanged


def test_missing_null_and_boolean_preconditions_are_distinct(tmp_path):
    existing, patch, source, manifest = setup(tmp_path)
    change = patch["updates"][0]["changes"][0]
    change["before_present"] = False
    with pytest.raises(CatalogImportError, match="missing versus null"):
        run(tmp_path, existing, patch, manifest)
    existing["boards"][0]["headers"][0]["gender"] = False
    patch["updates"][0]["expected_record_sha256"] = digest(encoded(existing["boards"][0]))
    change.update(before_present=True, before=0)
    with pytest.raises(CatalogImportError):
        run(tmp_path, existing, patch, manifest)


def test_replay_rejects_drift_or_audit_tampering(tmp_path):
    existing, patch, source, manifest = setup(tmp_path)
    result, _ = run(tmp_path, existing, patch, manifest)
    result["boards"][0]["headers"][0]["preinstalled"] = True
    with pytest.raises(CatalogImportError, match="changed"):
        run(tmp_path, result, patch, manifest)
    result, _ = run(tmp_path, existing, patch, manifest)
    result["catalog_enrichments"][0]["records"] = []
    with pytest.raises(CatalogImportError, match="incomplete"):
        run(tmp_path, result, patch, manifest)
    result, _ = run(tmp_path, existing, patch, manifest)
    result["catalog_enrichments"][0]["records"][0]["changes"][0]["before"] = "tampered"
    with pytest.raises(CatalogImportError):
        run(tmp_path, result, patch, manifest)


def test_source_hash_and_source_url_membership(tmp_path):
    existing, patch, source, manifest = setup(tmp_path)
    (tmp_path / "claim.json").write_text("{}")
    with pytest.raises(CatalogImportError, match="mismatch"):
        run(tmp_path, existing, patch, manifest)
    existing, patch, source, manifest = setup(tmp_path)
    patch["updates"][0]["changes"][0]["evidence_urls"] = ["https://invented.example/proof"]
    with pytest.raises(CatalogImportError, match="absent"):
        run(tmp_path, existing, patch, manifest)


def test_population_remains_descriptive_and_cli_is_read_only(tmp_path, capsys):
    existing, patch, source, manifest = setup(tmp_path)
    change = patch["updates"][0]["changes"][0]
    change.update(field="population", after="factory fitted", source_field_pointer="/headers/0/population")
    result, _ = run(tmp_path, existing, patch, manifest)
    assert result["boards"][0]["headers"][0]["preinstalled"] is False
    paths = {}
    for name, value in [("catalog", existing), ("patch", patch), ("manifest", manifest)]:
        paths[name] = tmp_path / (name + ".json");paths[name].write_bytes(encoded(value))
    assert main(["enrich-boards", str(paths["patch"]), "--catalog", str(paths["catalog"]),
                 "--source-root", str(tmp_path), "--manifest", str(paths["manifest"]),
                 "--enrichment-id", "gender-research-r1"]) == 0
    assert paths["catalog"].read_bytes() == encoded(existing)
    capsys.readouterr()


def test_combined_postimage_and_audit_tampering_is_rejected(tmp_path):
    existing, patch, source, manifest = setup(tmp_path)
    result, _ = run(tmp_path, existing, patch, manifest)
    result["boards"][0]["headers"][0]["gender"] = "female"
    result["catalog_enrichments"][0]["records"][0]["after_sha256"] = digest(encoded(result["boards"][0]))
    with pytest.raises(CatalogImportError, match="claimed postimage"):
        run(tmp_path, result, patch, manifest)


@pytest.mark.parametrize("target", ["scope", "hash_encoding"])
def test_complete_audit_metadata_is_guarded(tmp_path, target):
    existing, patch, source, manifest = setup(tmp_path)
    result, _ = run(tmp_path, existing, patch, manifest)
    if target == "scope":
        result["catalog_enrichments"][0]["records"][0]["scope"]["revision"] = "r2"
    else:
        result["catalog_enrichments"][0]["hash_encoding"] = "other"
    with pytest.raises(CatalogImportError):
        run(tmp_path, result, patch, manifest)


def test_source_scope_preserves_known_original_maker_and_sku():
    record = {"id": "old", "sku": None, "original_record": {"sku": "known", "manufacturer": "Maker"}, "revision": None}
    assert scope(record)["sku"] == "known"
    assert scope(record)["manufacturer"] == "Maker"
    assert scope(record)["revision"] is None


def photo_setup(tmp_path):
    import shutil

    from text_to_reality.catalog_import import read_json
    root = Path(__file__).resolve().parents[1] / "docs/connector-library/research-wave5"
    shutil.copytree(root, tmp_path / "sources")
    copied = tmp_path / "sources"
    current = read_json(Path(__file__).resolve().parents[1] / "src/text_to_reality/data/boards.json")
    patch = read_json(copied / "headerBoards.enrichment.runtime-guarded.json")
    patch["updates"] = patch["updates"][:1]
    id = patch["updates"][0]["board_id"]
    record = copy.deepcopy(next(r for r in current["boards"] if r["id"] == id))
    for change in patch["updates"][0]["changes"]:
        header = next(h for h in record["headers"] if h["id"] == change["header_id"])
        if change["before_present"]:
            header[change["field"]] = change["before"]
        else:
            header.pop(change["field"], None)
    assert digest(encoded(record)) == patch["updates"][0]["expected_record_sha256"]
    return copied, {"schemaVersion": 1, "boards": [record]}, patch, read_json(copied / "enrichment-source-manifest.json")


def update_manifest(root, manifest, path):
    file = next(f for f in manifest["files"] if f["path"] == path)
    content = (root / path).read_bytes()
    file.update(bytes=len(content), sha256=digest(content))


def test_actual_three_photo_enrichments_replay_and_preserve_gates():
    from text_to_reality.catalog_import import read_json
    root = Path(__file__).resolve().parents[1] / "docs/connector-library/research-wave5"
    existing = read_json(Path(__file__).resolve().parents[1] / "src/text_to_reality/data/boards.json")
    patch = read_json(root / "headerBoards.enrichment.runtime-guarded.json")
    result, report = prepare_enrichment(existing, patch, root, read_json(root / "enrichment-source-manifest.json"),
                                      "wave5-display-population-2026-10-06")
    assert encoded(result) == encoded(existing)
    assert report["status"] == "identical_replay"
    for update in patch["updates"]:
        record = next(r for r in result["boards"] if r["id"] == update["board_id"])
        for change in update["changes"]:
            header = next(h for h in record["headers"] if h["id"] == change["header_id"])
            assert header["gender"] == "none"
            assert header.get("preinstalled") is not True
        assert record["physical_fit_verified"] is False


@pytest.mark.parametrize("target", ["file_hash", "record_hash", "header_hash", "sealed_record_hash", "pointer", "sku", "revision"])
def test_photo_guard_mismatches_are_rejected(tmp_path, target):
    from text_to_reality.catalog_import import read_json
    root, existing, patch, manifest = photo_setup(tmp_path)
    path = "headerBoards.enrichment.proposed.json"
    envelope = read_json(root / path)
    photo = envelope["patches"][0]
    if target == "file_hash":
        photo["source_guard"]["file_sha256"] = "0" * 64
    elif target == "record_hash":
        photo["source_guard"]["record_canonical_sha256"] = "0" * 64
    elif target == "header_hash":
        photo["changes"][0]["original_header_canonical_sha256"] = "0" * 64
    elif target == "sealed_record_hash":
        photo["expected_wave4_normalized_source"]["record_canonical_sha256"] = "0" * 64
    elif target == "pointer":
        photo["source_guard"]["json_pointer"] = "/records/1"
    elif target == "sku":
        photo["sku"] = "OTHER"
    else:
        photo["revision_scope"] = "r2"
    (root / path).write_bytes(encoded(envelope));update_manifest(root, manifest, path)
    with pytest.raises(CatalogImportError):
        run(root, existing, patch, manifest)


def test_photo_source_revision_and_primary_url_validation(tmp_path):
    from text_to_reality.catalog_import import read_json
    root, existing, patch, manifest = photo_setup(tmp_path)
    source = "board_batch5/display_enrichment/enrichment.json"
    wrapper = "headerBoards.enrichment.proposed.json"
    original = read_json(root / source);envelope = read_json(root / wrapper)
    original["updates"][0]["revision_scope"] = "r2"
    envelope["patches"][0]["original_update"] = original["updates"][0]
    (root / source).write_bytes(encoded(original));(root / wrapper).write_bytes(encoded(envelope))
    update_manifest(root, manifest, source);update_manifest(root, manifest, wrapper)
    with pytest.raises(CatalogImportError, match="scope contradicts"):
        run(root, existing, patch, manifest)
    original["updates"][0].pop("revision_scope")
    original["updates"][0]["evidence"]["product_url"] = "https://"
    envelope["patches"][0]["original_update"] = original["updates"][0]
    envelope["patches"][0]["evidence"] = original["updates"][0]["evidence"]
    for change in patch["updates"][0]["changes"]:
        change["evidence_urls"][0] = "https://"
    (root / source).write_bytes(encoded(original));(root / wrapper).write_bytes(encoded(envelope))
    update_manifest(root, manifest, source);update_manifest(root, manifest, wrapper)
    with pytest.raises(CatalogImportError, match="primary URL"):
        run(root, existing, patch, manifest)


def test_photo_requires_exact_image_and_unchanged_topology(tmp_path):
    from text_to_reality.catalog_import import read_json
    root, existing, patch, manifest = photo_setup(tmp_path)
    photo = read_json(root / "headerBoards.enrichment.proposed.json")["patches"][0]
    image_name = Path(photo["evidence"]["image_local"]).name
    filtered = copy.deepcopy(manifest)
    filtered["files"] = [f for f in filtered["files"] if Path(f["path"]).name != image_name]
    with pytest.raises(CatalogImportError, match="image"):
        run(root, existing, patch, filtered)
    header = existing["boards"][0]["headers"][0]
    header["pin_count"] += 1
    patch["updates"][0]["expected_record_sha256"] = digest(encoded(existing["boards"][0]))
    with pytest.raises(CatalogImportError, match="positions"):
        run(root, existing, patch, manifest)


def test_photo_normalization_computes_runtime_hash_and_replays(tmp_path):
    from text_to_reality.catalog_enrichment import normalize_photo_patch
    from text_to_reality.catalog_import import read_json
    root = Path(__file__).resolve().parents[1] / "docs/connector-library/research-wave5"
    catalog_path = Path(__file__).resolve().parents[1] / "src/text_to_reality/data/boards.json"
    existing = read_json(catalog_path)
    proposal = read_json(root / "headerBoards.enrichment.proposed.json")
    normalized = normalize_photo_patch(existing, proposal, "headerBoards.enrichment.proposed.json", "wave5-display-population-2026-10-06")
    assert normalized == read_json(root / "headerBoards.enrichment.runtime-guarded.json")
    output = tmp_path / "catalog.json";output.write_bytes(encoded(existing))
    assert main(["enrich-boards", str(root / "headerBoards.enrichment.proposed.json"), "--catalog", str(output),
                 "--source-root", str(root), "--manifest", str(root / "enrichment-source-manifest.json"),
                 "--enrichment-id", "wave5-display-population-2026-10-06", "--photo-source-format"]) == 0
    assert output.read_bytes() == encoded(existing)


def test_empty_username_with_password_is_still_a_credential(tmp_path):
    existing, patch, source, _ = setup(tmp_path)
    source["source"] = "https://:secret@maker.example/101"
    patch["updates"][0]["changes"][0]["evidence_urls"] = [source["source"]]
    with pytest.raises(CatalogImportError, match="evidence URL"):
        run(tmp_path, existing, patch, save_source(tmp_path, source))
