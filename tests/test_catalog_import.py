import copy
import json
from pathlib import Path

import pytest

from text_to_reality import catalog
from text_to_reality.catalog_import import (
    CatalogImportError,
    digest,
    encoded,
    prepare_import,
    read_json,
    write_catalog,
)
from text_to_reality.cli import main


def batch(tmp_path):
    raw_header = {"group_id": "left", "rows": 1, "pins_per_row": 7, "pitch_mm": 2.54,
                  "gender": "male", "shrouded": False, "confidence": {"mechanical_fit": "not_validated"}}
    raw = {"name": "Sample board", "source": "https://manufacturer.example/board", "revision": "unresolved", "header_groups": [raw_header]}
    source = {"records": [raw]}
    path = tmp_path / "source.json"
    path.write_bytes(encoded(source))
    record = {"id": "sample-board", "name": "Sample board", "aliases": ["Sample"], "kind": "board",
              "revision": "unresolved", "evidence": [{"url": "https://manufacturer.example/board"}],
              "source_record": {"file": "source.json", "json_pointer": "/records/0"},
              "original_record": raw,
              "headers": [{"id": "left", "rows": 1, "pin_count": 7, "pitch_mm": 2.54,
                           "gender": "male", "shrouded": False, "confidence": raw_header["confidence"],
                           "fit_status": "unverified", "original_header": raw_header}]}
    proposal = {"schemaVersion": 1, "boards": [record]}
    manifest = {"files": [{"path": path.name, "bytes": path.stat().st_size,
                           "sha256": digest(path.read_bytes())}]}
    return {"schemaVersion": 1, "boards": []}, proposal, manifest


def run(tmp_path, existing, proposal, manifest):
    return prepare_import(existing, proposal, tmp_path, manifest, "second-wave-sample")


def test_merge_preserves_source_ids_and_replays_identically(tmp_path):
    existing, proposal, manifest = batch(tmp_path)
    existing["boards"] = [{"id": "legacy", "name": "Legacy", "aliases": [], "headers": []}]
    snapshot = copy.deepcopy(existing)
    merged, report = run(tmp_path, existing, proposal, manifest)
    assert existing == snapshot
    assert merged["boards"][0] == existing["boards"][0]
    assert merged["boards"][1] == proposal["boards"][0]
    replay, replay_report = run(tmp_path, merged, proposal, manifest)
    assert replay == merged
    assert replay_report["identical_replay_ids"] == ["sample-board"]
    assert report["physical_validation"] is False
    assert report["model_approval_modified"] is False


@pytest.mark.parametrize("update", [
    {"revision": "Rev A verified"}, {"fit_status": "verified"}, {"fitApproved": True},
    {"approved_model_revision": "new-clasp"}, {"retention_motion": "slide then click"},
    {"mechanical_fit": "physical fit approved"}, {"qualified": True},
    {"REVISION_VERIFIED": True}, {"FIT_APPROVED": True}, {"Fit_Approved": True},
    {"fit_status": True}, {"mechanical_fit": 1}, {"confidence": {"pitch": "high"}},
    {"physical_fit_verified": True}, {"automatic_fit_eligible": True}, {"comb_qualified": True},
])
def test_rejects_unsupported_revision_and_qualification(tmp_path, update):
    existing, proposal, manifest = batch(tmp_path)
    proposal["boards"][0].update(update)
    with pytest.raises(CatalogImportError):
        run(tmp_path, existing, proposal, manifest)


@pytest.mark.parametrize("field,value", [
    ("rows", 2), ("rows", True), ("pin_count", 14), ("pin_count", True),
    ("pitch_mm", 2.0), ("pitch_mm", float("nan")), ("pitch_mm", True),
    ("shrouded", True), ("gender", "female"), ("preinstalled", True),
    ("confidence", {"mechanical_fit": "high"}), ("pitch_evidence", "verified manually"),
])
def test_rejects_topology_and_unknown_promotions(tmp_path, field, value):
    existing, proposal, manifest = batch(tmp_path)
    proposal["boards"][0]["headers"][0][field] = value
    with pytest.raises(CatalogImportError):
        run(tmp_path, existing, proposal, manifest)


def test_boolean_raw_dimensions_fail_even_when_normalized_matches(tmp_path):
    existing, proposal, manifest = batch(tmp_path)
    proposal["boards"][0]["original_record"]["header_groups"][0]["rows"] = True
    proposal["boards"][0]["headers"][0]["rows"] = 1
    source = tmp_path / "source.json"
    source.write_bytes(encoded({"records": [proposal["boards"][0]["original_record"]]}))
    manifest["files"][0].update(bytes=source.stat().st_size, sha256=digest(source.read_bytes()))
    with pytest.raises(CatalogImportError, match="topology"):
        run(tmp_path, existing, proposal, manifest)


def test_all_raw_groups_must_be_represented_once(tmp_path):
    existing, proposal, manifest = batch(tmp_path)
    proposal["boards"][0]["headers"] = []
    with pytest.raises(CatalogImportError, match="every source group"):
        run(tmp_path, existing, proposal, manifest)
    proposal["boards"][0]["excluded_headers"] = [{"reason": "unknown topology",
        "original_header": proposal["boards"][0]["original_record"]["header_groups"][0]}]
    merged, _ = run(tmp_path, existing, proposal, manifest)
    assert not merged["boards"][0]["headers"]


def test_source_hash_and_original_pointer_are_checked(tmp_path):
    existing, proposal, manifest = batch(tmp_path)
    (tmp_path / "source.json").write_text("{}")
    with pytest.raises(CatalogImportError, match="mismatch"):
        run(tmp_path, existing, proposal, manifest)
    existing, proposal, manifest = batch(tmp_path)
    proposal["boards"][0]["source_record"]["json_pointer"] = "/records/00"
    with pytest.raises(CatalogImportError):
        run(tmp_path, existing, proposal, manifest)
    proposal["boards"][0]["source_record"]["json_pointer"] = "/records/~2"
    with pytest.raises(CatalogImportError):
        run(tmp_path, existing, proposal, manifest)


def test_same_id_conflict_and_invented_source_variant_fail(tmp_path):
    existing, proposal, manifest = batch(tmp_path)
    merged, _ = run(tmp_path, existing, proposal, manifest)
    proposal["boards"][0]["name"] = "Different layout"
    with pytest.raises(CatalogImportError, match="conflicts"):
        run(tmp_path, merged, proposal, manifest)
    proposal["boards"][0]["id"] = "invented-variant"
    with pytest.raises(CatalogImportError, match="multiple variant"):
        run(tmp_path, merged, proposal, manifest)


@pytest.mark.parametrize("content", [b'{"id":1,"id":2}', b'{"pitch":NaN}', b'{"pitch":Infinity}', b'{"pitch":1e999}'])
def test_json_rejects_duplicate_keys_and_nonfinite_values(tmp_path, content):
    path = tmp_path / "input.json"
    path.write_bytes(content)
    with pytest.raises(CatalogImportError):
        read_json(path)


def test_symlinks_and_traversal_fail_before_write(tmp_path):
    existing, proposal, manifest = batch(tmp_path)
    manifest["files"][0]["path"] = "../source.json"
    with pytest.raises(CatalogImportError):
        run(tmp_path, existing, proposal, manifest)
    link = tmp_path / "linked"
    link.symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(CatalogImportError):
        read_json(link / "source.json")
    with pytest.raises(CatalogImportError):
        write_catalog(link / "result.json", b"{}")
    assert not (tmp_path / "result.json").exists()


def test_writes_need_expected_hash_and_cli_default_is_read_only(tmp_path, capsys):
    existing, proposal, manifest = batch(tmp_path)
    paths = {}
    for name, value in (("catalog", existing), ("proposal", proposal), ("manifest", manifest)):
        paths[name] = tmp_path / (name + ".json")
        paths[name].write_bytes(encoded(value))
    before = paths["catalog"].read_bytes()
    args = ["import-boards", str(paths["proposal"]), "--catalog", str(paths["catalog"]),
            "--source-root", str(tmp_path), "--manifest", str(paths["manifest"]), "--batch-id", "second-wave-sample"]
    assert main(args) == 0
    assert paths["catalog"].read_bytes() == before
    assert json.loads(capsys.readouterr().out)["added_ids"] == ["sample-board"]
    assert main(args + ["--output", str(paths["catalog"])]) == 1
    assert paths["catalog"].read_bytes() == before
    capsys.readouterr()
    assert main(args + ["--output", str(paths["catalog"]), "--expected-output-sha256", digest(before)]) == 0
    result = json.loads(paths["catalog"].read_text())
    assert len(result["boards"]) == 1


def test_researched_name_alias_collision_is_ambiguous(monkeypatch):
    a = {"id": "a", "name": "Shared", "aliases": [], "source_record": {"file": "a"}}
    b = {"id": "b", "name": "B", "aliases": ["Shared"], "source_record": {"file": "b"}}
    monkeypatch.setattr(catalog, "boards", lambda: [a, b])
    assert catalog.board("shared") is None
    assert catalog.board("a") == a
    assert catalog.board("b") == b


def test_unresolved_source_qualifications_cannot_be_dropped(tmp_path):
    existing, proposal, manifest = batch(tmp_path)
    raw = proposal["boards"][0]["original_record"]
    raw["unknowns"] = ["revision unresolved"]
    proposal["boards"][0]["unresolved"] = []
    source = tmp_path / "source.json"
    source.write_bytes(encoded({"records": [raw]}))
    manifest["files"][0].update(bytes=source.stat().st_size, sha256=digest(source.read_bytes()))
    with pytest.raises(CatalogImportError, match="unresolved"):
        run(tmp_path, existing, proposal, manifest)


def test_manifest_index_counts_are_checked(tmp_path):
    existing, proposal, manifest = batch(tmp_path)
    manifest["record_index"] = [{"source_file": "source.json", "json_pointer": "/records/0",
                                 "normalized_id": "sample-board"}]
    manifest["total_record_count"] = 2
    with pytest.raises(CatalogImportError, match="record count"):
        run(tmp_path, existing, proposal, manifest)
    manifest["total_record_count"] = 1
    manifest["record_index"][0]["normalized_id"] = "invented"
    with pytest.raises(CatalogImportError, match="identity"):
        run(tmp_path, existing, proposal, manifest)


def test_mixed_ordinary_legacy_and_research_labels_are_ambiguous(monkeypatch):
    a = {"id": "legacy-custom", "name": "Shared", "aliases": []}
    b = {"id": "b", "name": "B", "aliases": ["Shared"], "source_record": {"file": "b"}}
    monkeypatch.setattr(catalog, "boards", lambda: [a, b])
    assert catalog.board("shared") is None


def test_preserved_original_boolean_is_not_equal_to_zero(tmp_path):
    existing, proposal, manifest = batch(tmp_path)
    raw = proposal["boards"][0]["original_record"]
    raw["unknown_field"] = False
    source = tmp_path / "source.json"
    source.write_bytes(encoded({"records": [raw]}))
    manifest["files"][0].update(bytes=source.stat().st_size, sha256=digest(source.read_bytes()))
    raw["unknown_field"] = 0
    with pytest.raises(CatalogImportError, match="original_record"):
        run(tmp_path, existing, proposal, manifest)


def test_wave2_sources_replay_and_normalization_are_exact():
    from text_to_reality.catalog_import import normalize_research_proposal
    root = Path(__file__).resolve().parents[1] / "docs/connector-library/research-wave2"
    current = {"schemaVersion": 1, "boards": catalog.boards()}
    normalized, adjustments = normalize_research_proposal(read_json(root / "headerBoards.proposed.json"))
    assert normalized == read_json(root / "headerBoards.validated-normalization.json")
    assert adjustments
    merged, report = prepare_import(current, normalized, root, read_json(root / "manifest.json"), "wave2-2026-10-06")
    assert report["added_ids"] == []
    assert len(report["identical_replay_ids"]) == 76
    assert len(merged["boards"]) == len(current["boards"])
    assert all(not b.get("revision_verified") for b in normalized["boards"])


def test_wave3_sources_replay_and_normalization_are_exact():
    from text_to_reality.catalog_import import normalize_research_proposal
    root = Path(__file__).resolve().parents[1] / "docs/connector-library/research-wave3"
    current = {"schemaVersion": 1, "boards": catalog.boards()}
    normalized, _ = normalize_research_proposal(read_json(root / "headerBoards.proposed.json"))
    assert normalized == read_json(root / "headerBoards.validated-normalization.json")
    merged, report = prepare_import(current, normalized, root, read_json(root / "manifest.json"), "wave3-2026-10-06")
    assert report["added_ids"] == []
    assert len(report["identical_replay_ids"]) == 57
    assert len(merged["boards"]) == len(current["boards"])
    pololu = catalog.board("pololu-1182")
    assert len(pololu["headers"]) == 2
    assert any(h["original_header"].get("id") == "VREF_access" for h in pololu["excluded_headers"])
    plan = catalog.connectors_for([{"board": "pololu-1182"}])
    assert plan["physical_validation"] is False
    assert all(not c["fit_approved"] for c in plan["connectors"])
    assert all("installed_male_gender_unverified" in row["issues"] for row in plan["row_checks"])


def test_normalized_evidence_cannot_invent_source_urls(tmp_path):
    existing, proposal, manifest = batch(tmp_path)
    proposal["boards"][0]["evidence"][0]["url"] = "https://fabricated.example/qualification"
    with pytest.raises(CatalogImportError, match="absent from exact source"):
        run(tmp_path, existing, proposal, manifest)


def test_wave4_preserves_exclusions_and_replays_exactly():
    from text_to_reality.catalog_import import normalize_research_proposal
    root = Path(__file__).resolve().parents[1] / "docs/connector-library/research-wave4"
    current = {"schemaVersion": 1, "boards": copy.deepcopy(catalog.boards())}
    enriched_ids = {"sparkfun-lcd-23453", "sparkfun-lcd-15143", "sparkfun-lcd-29530"}
    normalized, _ = normalize_research_proposal(read_json(root / "headerBoards.proposed.json"))
    assert normalized == read_json(root / "headerBoards.validated-normalization.json")
    for record in current["boards"]:
        if record["id"] in enriched_ids:
            source = next(r for r in normalized["boards"] if r["id"] == record["id"])
            record["headers"] = copy.deepcopy(source["headers"])
    merged, report = prepare_import(current, normalized, root, read_json(root / "manifest.json"), "wave4-2026-10-06")
    assert report["added_ids"] == []
    assert len(report["identical_replay_ids"]) == 46
    assert len(merged["boards"]) == len(current["boards"])
    assert sum(not r["headers"] for r in normalized["boards"]) == 8
    assert sum(len(r["headers"]) for r in normalized["boards"]) == 80
    assert all(h["rows"] == 1 for r in normalized["boards"] for h in r["headers"])
    for r in normalized["boards"]:
        plan = catalog.connectors_for([{"board": r["id"]}])
        assert plan["physical_validation"] is False
        assert all(c["fit_approved"] is False for c in plan["connectors"])
        assert plan["model_choice"]["approved_model_revision"] is None


def test_wave5_new_records_preserve_multirow_and_nonuniform_exclusions():
    from text_to_reality.catalog_import import normalize_research_proposal
    root = Path(__file__).resolve().parents[1] / "docs/connector-library/research-wave5"
    current = {"schemaVersion": 1, "boards": catalog.boards()}
    normalized, _ = normalize_research_proposal(read_json(root / "headerBoards.proposed.json"))
    assert normalized == read_json(root / "headerBoards.validated-normalization.json")
    merged, report = prepare_import(current, normalized, root, read_json(root / "manifest.json"), "wave5-2026-10-06")
    assert report["added_ids"] == []
    assert len(report["identical_replay_ids"]) == 36
    assert sum(not r["headers"] for r in normalized["boards"]) == 11
    assert all(h["rows"] == 1 for r in normalized["boards"] for h in r["headers"])
    pn532 = next(r for r in normalized["boards"] if "pn532" in r["name"].lower())
    assert any(h["original_header"].get("pin_count") == 9 and h["original_header"].get("pitch_mm") is None
               for h in pn532["excluded_headers"])
    assert len(merged["boards"]) == len(current["boards"])


def test_old_insert_replay_after_enrichment_keeps_conflict_guard():
    from text_to_reality.catalog_import import normalize_research_proposal
    root = Path(__file__).resolve().parents[1] / "docs/connector-library/research-wave4"
    normalized, _ = normalize_research_proposal(read_json(root / "headerBoards.proposed.json"))
    with pytest.raises(CatalogImportError, match="conflicts"):
        prepare_import({"schemaVersion": 1, "boards": catalog.boards()}, normalized, root,
                       read_json(root / "manifest.json"), "wave4-2026-10-06")


def test_wave6_sbc_headers_are_discoverable_without_comb_proposals():
    from text_to_reality.catalog_import import normalize_research_proposal
    root = Path(__file__).resolve().parents[1] / "docs/connector-library/research-wave6"
    normalized, _ = normalize_research_proposal(read_json(root / "headerBoards.proposed.json"))
    assert normalized == read_json(root / "headerBoards.validated-normalization.json")
    merged, report = prepare_import({"schemaVersion": 1, "boards": catalog.boards()}, normalized,
                                   root, read_json(root / "manifest.json"), "wave6-sbc-2026-10-06")
    assert report["added_ids"] == [] and len(report["identical_replay_ids"]) == 8
    assert all(not r["headers"] for r in normalized["boards"])
    assert sum(len(r["excluded_headers"]) for r in normalized["boards"]) == 37
    for r in normalized["boards"]:
        plan = catalog.connectors_for([{"board": r["id"]}])
        assert plan["connectors"] == []
        assert plan["physical_validation"] is False
    assert len(merged["boards"]) == len(catalog.boards())


def test_wave7_nucleo144_mixed_faces_and_morpho_remain_excluded():
    from text_to_reality.catalog_import import normalize_research_proposal
    root = Path(__file__).resolve().parents[1] / "docs/connector-library/research-wave7"
    normalized, _ = normalize_research_proposal(read_json(root / "headerBoards.proposed.json"))
    assert normalized == read_json(root / "headerBoards.validated-normalization.json")
    merged, report = prepare_import({"schemaVersion": 1, "boards": catalog.boards()}, normalized,
                                   root, read_json(root / "manifest.json"), "wave7-nucleo144-2026-10-06")
    assert report["added_ids"] == [] and len(report["identical_replay_ids"]) == 12
    assert all(not r["headers"] for r in normalized["boards"])
    assert sum(len(r["excluded_headers"]) for r in normalized["boards"]) == 192
    for r in normalized["boards"]:
        originals = [h["original_header"] for h in r["excluded_headers"]]
        assert any(h.get("pin_count") == 70 and h.get("rows") == 2 for h in originals)
        assert any(h.get("gender") == "mixed" for h in originals)
        plan = catalog.connectors_for([{"board": r["id"]}])
        assert plan["connectors"] == []
        assert plan["physical_validation"] is False
    assert len(merged["boards"]) == len(catalog.boards())


def test_wave8_exact_factory_skUs_never_promote_fit_or_import_held_lead():
    from text_to_reality.catalog_import import normalize_research_proposal
    root = Path(__file__).resolve().parents[1] / "docs/connector-library/research-wave8"
    normalized, _ = normalize_research_proposal(read_json(root / "headerBoards.proposed.json"))
    assert normalized == read_json(root / "headerBoards.validated-normalization.json")
    merged, report = prepare_import({"schemaVersion": 1, "boards": catalog.boards()}, normalized,
                                   root, read_json(root / "manifest.json"), "wave8-presoldered-2026-10-06")
    assert report["added_ids"] == [] and len(report["identical_replay_ids"]) == 10
    assert len({r["sku"] for r in normalized["boards"]}) == 10
    assert not any(r.get("sku") == "102010634" for r in catalog.boards())
    assert sum(len(r["headers"]) for r in normalized["boards"]) == 20
    assert sum(h["pin_count"] for r in normalized["boards"] for h in r["headers"]) == 168
    for r in normalized["boards"]:
        assert all(h["rows"] == 1 and h["gender"] == "male" and h["pitch_mm"] == 2.54 for h in r["headers"])
        plan = catalog.connectors_for([{"board": r["id"]}])
        assert sum(c["connectors"] for c in plan["connectors"]) == 2
        assert plan["physical_validation"] is False
        assert all(c["fit_approved"] is False for c in plan["connectors"])
        assert plan["model_choice"]["approved_model_revision"] is None
        assert all("exact_board_revision_missing" in row["issues"] for row in plan["row_checks"])
    assert len(merged["boards"]) == len(catalog.boards())
