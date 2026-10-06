import asyncio
import json

import pytest

from text_to_reality import catalog, package
from text_to_reality.cli import main
from text_to_reality.server import create_server
from text_to_reality.store import ProjectError, Store


def finished_project(tmp_path):
    store = Store(tmp_path)
    store.create("Desk Meter", "A small screen that shows my coding agent's status.")
    folder = tmp_path / "desk-meter"
    (folder / "bom.json").write_text(json.dumps([
        {"part": "Seeed Studio XIAO ESP32S3", "quantity": 1},
        {"part": "JIG_ 7-pin connector, small", "quantity": 2, "jig_part": "jig-connector"},
    ]))
    (folder / "wiring.json").write_text(json.dumps({
        "connections": [{"from": "XIAO D1", "to": "LCD SDA", "color": "blue"}],
        "connectors": [{"pins": 7, "size": "small", "plugs_onto": "XIAO left row"}],
    }))
    (folder / "body.stl").write_bytes(b"solid body\nendsolid body\n")
    (folder / "main.ino").write_text("void setup() {}\nvoid loop() {}\n")
    (folder / "guide.md").write_text("1. Plug the blue connector onto the left row.\n")
    (folder / "tests.md").write_text("Screen lights up within 5 seconds.\n")
    for stage, path in [("parts", "bom.json"), ("electronics", "wiring.json"), ("mechanical", "body.stl"),
                        ("firmware", "main.ino"), ("assembly", "guide.md"), ("testing", "tests.md")]:
        store.record("desk-meter", stage, [path])
    return store, folder


def test_new_project_lists_what_is_left(tmp_path):
    store = Store(tmp_path)
    status = store.create("Plant Buddy!", "Reminds me to water the plant.")
    assert status["id"] == "plant-buddy"
    assert status["stages"]["requirements"]["status"] == "done"
    assert status["stages"]["parts"]["next"].startswith("bom.json")
    report = package.validate(tmp_path / "plant-buddy")
    assert not report["complete"]
    assert "parts: not finished" in report["problems"]


def test_counts_only_header_package_is_blocked_and_links_parts(tmp_path):
    _, folder = finished_project(tmp_path)
    report = package.validate(folder)
    assert not report["complete"]
    assert any("approved_connector_model_unresolved" in p for p in report["problems"])
    assert report["get_the_parts"] == [{"name": "JIG_ wire connectors", "url": "https://jig-robotics.com/support/dupont-housings"}]


def test_edited_file_is_caught(tmp_path):
    store, folder = finished_project(tmp_path)
    (folder / "main.ino").write_text("changed")
    assert "main.ino" in store.status("desk-meter")["changed_since_recorded"]
    assert any("main.ino: changed" in p for p in package.validate(folder)["problems"])


def test_connectors_need_a_parts_row_and_valid_pins(tmp_path):
    store, folder = finished_project(tmp_path)
    (folder / "bom.json").write_text(json.dumps([{"part": "XIAO", "quantity": 1}]))
    (folder / "wiring.json").write_text(json.dumps({"connections": [{"from": "a", "to": "b"}], "connectors": [{"pins": 30, "size": "tiny"}]}))
    store.record("desk-meter", "parts", ["bom.json"])
    store.record("desk-meter", "electronics", ["wiring.json"])
    problems = package.validate(folder)["problems"]
    assert any("'pins' must be 1-22" in p for p in problems)
    assert any("'size' must be small or large" in p for p in problems)
    assert any("no row with jig_part 'jig-connector'" in p for p in problems)


def test_stage_rules(tmp_path):
    store = Store(tmp_path)
    store.create("Phone Stand", "A printed stand.")
    with pytest.raises(ProjectError):
        store.set_stage("phone-stand", "electronics", "not_applicable")
    store.set_stage("phone-stand", "electronics", "not_applicable", "printed only")
    store.set_stage("phone-stand", "parts", "not_applicable", "nothing")
    assert "parts: every build needs this stage" in package.validate(tmp_path / "phone-stand")["problems"]


def test_files_must_stay_inside_the_project(tmp_path):
    store = Store(tmp_path)
    store.create("Box", "A box.")
    (tmp_path / "outside.txt").write_text("x")
    with pytest.raises(ProjectError):
        store.record("box", "mechanical", ["../outside.txt"])


def test_connectors_use_one_per_full_row():
    result = catalog.connectors_for([{"board": "XIAO ESP32S3", "quantity": 1}, {"board": "ESP32-DevKitC V4", "quantity": 1}, {"board": "mystery", "quantity": 1}])
    rows = {c["pins"]: c for c in result["connectors"]}
    assert rows[7]["connectors"] == 2 and rows[7]["packs_to_order"] == 1 and not rows[7]["printed_to_order"]
    assert rows[19]["pack"] == "2 x 19-pin (printed to order)" and rows[19]["printed_to_order"]
    assert result["unknown_boards"] == ["mystery"]
    custom = catalog.connectors_for([{"board": "my board", "rows": [6, 6], "quantity": 3}], "large")
    assert custom["connectors"][0]["connectors"] == 6
    assert custom["connectors"][0]["packs_to_order"] == 2
    assert custom["connectors"][0]["fit_approved"] is False


def test_history_and_outcomes(tmp_path):
    store = Store(tmp_path)
    store.create("Lamp", "A lamp.")
    store.new_revision("lamp", "brighter LED")
    store.outcome("lamp", "worked", "bright enough")
    events = [e["event"] for e in store.history("lamp")]
    assert events[0] == "recorded" and events[-2:] == ["revision", "outcome"]


def test_server_exposes_the_tools(tmp_path):
    server = create_server(Store(tmp_path))
    names = {tool.name for tool in asyncio.run(server.list_tools())}
    assert names == {"create_project", "list_projects", "project_status", "record_files", "set_stage", "check_package",
                     "new_revision", "log_outcome", "build_history", "find_jig_parts", "board_headers", "connectors_for_boards", "connector_guidance"}


def test_cli_check(tmp_path, capsys):
    store, folder = finished_project(tmp_path)
    (folder / "wiring.json").write_text(json.dumps({
        "connections": [{"from": "computer USB", "to": "device USB"}],
        "connector_scope": {"kind": "no_header_wiring", "reason": "USB-only device"},
    }))
    store.record("desk-meter", "electronics", ["wiring.json"])
    assert main(["check", str(folder)]) == 0
    assert json.loads(capsys.readouterr().out)["complete"]
