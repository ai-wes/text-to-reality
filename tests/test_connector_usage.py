import asyncio
import json
import os
import sys
from pathlib import Path

import pytest

from text_to_reality import catalog, connector_usage, package
from text_to_reality.server import INSTRUCTIONS, create_server
from text_to_reality.store import Store


def header(id="left", **updates):
    return {"id": id, "pin_count": 7, "pitch_mm": 2.54, "rows": 1,
            "gender": "male", "shrouded": False, "preinstalled": True, **updates}


def selection(**updates):
    return {"board": "measured XIAO ESP32S3", "revision": "sample-r1", "quantity": 1,
            "headers": [header(), header("right")], **updates}


def connector(**updates):
    return {"board": "measured XIAO ESP32S3", "board_revision": "sample-r1", "pins": 7,
            "size": "small", "header": header(), "model_revision": "caller-approved-clip",
            "housing": {"width_mm": 2, "height_mm": 2, "length_mm": 12, "wire_diameter_mm": 1.3},
            "model_envelope": {"width_mm": 2.1, "height_mm": 2.1, "length_mm": 12.15, "wire_diameter_mm": 1.6},
            "orientation": {"pin_one": "D0", "board_side": "top", "mating_direction": "+Z",
                            "ordered_pin_ids": [f"pin-{i}" for i in range(7)]},
            "contact_engagement_evidence": "measurements.json", "paired_model_hashes": "pair.json",
            "mount_source": "mount.step", "clearance_geometry": "clearance.step",
            "retention_protocol": "unapproved-guide.md", "print_conditions": "print.json", **updates}


def test_canonical_guidance_binds_unresolved_model_and_battery_bus_limits():
    result = connector_usage.guidance()
    assert result["rules"]["model_choice"]["approved_model_revision"] is None
    assert result["rules"]["model_choice"]["retention_motion"] is None
    assert result["rules"]["battery_adapter"]["qualified"] is False
    assert result["rules"]["battery_adapter"]["revision"] == "R29"
    assert result["rules"]["bus_blocks"]["solder_free"] is False
    assert result["rules"]["bus_blocks"]["automatic_signal_wiring_eligible"] is False
    assert "two 7-pin assemblies" in result["guide"]
    assert "Stop" in result["guide"]
    assert "connector_guidance" in INSTRUCTIONS


def test_xiao_full_rows_are_two_assemblies_not_wire_count_or_pack_count():
    result = catalog.connectors_for([selection()])
    item = result["connectors"][0]
    assert (item["pins"], item["connectors"], item["packs_to_order"], item["spare_assemblies"]) == (7, 2, 1, 3)
    assert item["base_units"] == item["retainer_units"] == 2
    assert result["bom_draft"][0]["quantity"] == 2
    assert result["bom_draft"][0]["unit"] == "assembly"
    assert len(result["row_diagrams"]) == 2
    assert all(r["full_row_positions"] == 7 for r in result["row_diagrams"])
    assert item["fit_approved"] is False
    assert result["model_choice"]["status"] == "unresolved"


@pytest.mark.parametrize("value", [True, False, 1.5, "2", 0, -1, None])
def test_finder_rejects_coerced_quantities_and_pin_counts(value):
    with pytest.raises(ValueError):
        catalog.connectors_for([selection(quantity=value)])
    with pytest.raises(ValueError):
        catalog.connectors_for([{"rows": [value]}])


@pytest.mark.parametrize("updates", [{"gender": "female"}, {"rows": 2}, {"shrouded": True},
                                     {"pitch_mm": 2.0}, {"pin_count": 23}])
def test_incompatible_headers_receive_no_jig_recommendation(updates):
    result = catalog.connectors_for([selection(headers=[header(**updates)])])
    assert result["connectors"] == []
    assert result["row_checks"][0]["excluded"] is True
    assert result["row_checks"][0]["issues"]


def test_custom_counts_and_catalog_references_never_bypass_fit_gates():
    result = catalog.connectors_for([{"board": "custom", "rows": [7, 7]}])
    assert result["connectors"][0]["connectors"] == 2
    assert "installed_male_gender_unverified" in result["row_checks"][0]["issues"]
    result = catalog.connectors_for([{"board": "XIAO ESP32S3"}])
    assert result["row_checks"][0]["issues"]
    assert not result["connectors"][0]["fit_approved"]


def test_catalog_keeps_legacy_ids_and_exact_variants_evidence_and_auxiliary_groups():
    assert len(catalog.boards()) >= 75
    assert len({b["id"] for b in catalog.boards()}) == len(catalog.boards())
    for id in ("seeed-xiao", "arduino-nano", "ssd1306-i2c", "esp32-devkitc-v4"):
        assert catalog.board(id)
    assert catalog.board("Raspberry Pi Pico H")["id"] == "raspberry-pi-pico-h"
    assert catalog.board("Pico H")["id"] == "raspberry-pi-pico-h"
    assert catalog.board("XIAO ESP32S3")["id"] == "seeed-xiao-esp32s3"
    assert catalog.board("esp32-s3-devkitc-1")["id"] == "esp32-s3-devkitc-1"  # explicit legacy ID
    assert catalog.board("espressif-esp32-devkitc-v4-wroom32e-female")["headers"][0]["gender"] == "female"
    feather = catalog.board("adafruit-feather-rp2040")
    assert [h["pin_count"] for h in feather["headers"]] == [16, 12]
    assert feather["evidence"] and feather["source_record"] and feather["original_record"]
    nano = catalog.board("nano-classic")
    assert any(h["original_header"].get("rows") == 2 for h in nano["excluded_headers"])
    for id, counts in [("espressif-esp32-c6-devkitc-1-v1-1", [16, 16]),
                       ("sparkfun-pro-micro-rp2040", [12, 12]), ("raspberry-pi-pico-h", [20, 20])]:
        assert [h["pin_count"] for h in catalog.board(id)["headers"]] == counts


def test_housing_dimensions_orientation_and_exact_model_approval_are_checked():
    assert connector_usage.connector_issues(connector()) == ["approved_connector_model_unresolved"]
    bad = connector(housing={"width_mm": 3, "height_mm": 3, "length_mm": 15, "wire_diameter_mm": 2})
    assert len([p for p in connector_usage.connector_issues(bad) if p.endswith("exceeds_model")]) == 4
    assert "connector_must_cover_full_row" in connector_usage.connector_issues(connector(pins=3))
    assert "ordered_full_row_pin_map_missing" in connector_usage.connector_issues(connector(orientation={}))
    assert "approved_connector_model_unresolved" in connector_usage.connector_issues(connector(approved=True))


def test_power_current_ratings_cannot_be_inferred_from_mechanical_fit():
    wire = {"function": "power", "voltage_v": 3.3, "expected_current_ma": 400,
            "wire_current_limit_ma": 200, "contact_current_limit_ma": 100}
    issues = connector_usage.wire_issues(wire)
    assert "wire_current_limit_ma_exceeded" in issues
    assert "contact_current_limit_ma_exceeded" in issues
    assert "electrical_rating_polarity_protection_evidence_missing" in issues


def test_package_cannot_omit_default_connectors_or_shorten_row():
    problems = []
    package.check_wiring({"boards": [selection()], "connections": [{"from": "a", "to": "b"}]}, problems)
    assert any("JIG assemblies must cover" in p for p in problems)
    problems = []
    package.check_wiring({"boards": [selection()], "connections": [{"from": "a", "to": "b"}],
                          "connectors": [connector(pins=3)]}, problems)
    assert any("connector_must_cover_full_row" in p for p in problems)
    assert any("approved_connector_model_unresolved" in p for p in problems)


def test_identical_row_sizes_cannot_hide_duplicate_endpoint_assemblies():
    problems = []
    package.check_wiring({"boards": [selection()], "connections": [{"from": "a", "to": "b"}],
                          "connectors": [connector(quantity=2)]}, problems)
    assert any("board/header identities must cover" in p for p in problems)


def test_explicit_exceptions_are_row_bound_and_need_evidence():
    wiring = {"boards": [selection()], "connections": [{"from": "a", "to": "b"}],
              "connector_exceptions": [{"board": "measured XIAO ESP32S3", "header_id": row,
                                        "reason": "explicit project alternative", "alternative": "qualified harness",
                                        "evidence": "owner-decision.md"} for row in ("left", "right")]}
    problems = []
    package.check_wiring(wiring, problems)
    assert not problems
    wiring["connector_exceptions"][0]["header_id"] = "wrong"
    package.check_wiring(wiring, problems)
    assert any("unknown endpoint row" in p for p in problems)
    assert any("JIG assemblies must cover" in p for p in problems)


def test_mcp_resource_and_tool_use_the_same_canonical_bytes(tmp_path):
    async def check():
        server = create_server(Store(tmp_path))
        result = await server.call_tool("connector_guidance", {})
        assert result.structured_content["rules"] == connector_usage.rules()
        resource = list(await server.read_resource("text-to-reality://connectors/usage-rules"))
        assert json.loads(resource[0].content) == result.structured_content["rules"]
        readable = list(await server.read_resource("text-to-reality://connectors/agent-guide"))
        assert readable[0].content == connector_usage.guide()
        rows = await server.call_tool("connectors_for_boards", {"boards": [selection()]})
        assert rows.structured_content["connectors"][0]["connectors"] == 2
        assert rows.structured_content["model_choice"]["status"] == "unresolved"
        resources = await server.list_resources()
        assert len(resources) == 3
    asyncio.run(check())


def test_fresh_stdio_agent_retrieves_guidance_and_gated_catalog_mapping(tmp_path):
    async def check():
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        params = StdioServerParameters(command=sys.executable,
            args=["-m", "text_to_reality.cli", "mcp", "--dir", str(tmp_path)],
            env={**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")})
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("connector_guidance", {})
                assert not result.is_error
                assert result.structured_content["rules"]["model_choice"]["status"] == "unresolved"
                resource = await session.read_resource("text-to-reality://connectors/agent-guide")
                assert "two 7-pin assemblies" in resource.contents[0].text
                plan = await session.call_tool("connectors_for_boards", {"boards": [{"board": "XIAO ESP32S3"}]})
                assert plan.structured_content["connectors"][0]["connectors"] == 2
                assert plan.structured_content["row_checks"][0]["issues"]
    asyncio.run(check())


def test_source_revision_descriptions_do_not_approve_actual_board_revision():
    plan = catalog.connectors_for([{"board": "st-nucleo-f031k6"}])
    assert "exact_board_revision_missing" in plan["row_checks"][0]["issues"]
    assert plan["model_choice"]["approved_model_revision"] is None
