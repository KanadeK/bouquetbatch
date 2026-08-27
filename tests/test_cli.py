from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from bouquetbatch.cli import run


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_complete_plan_writes_real_outputs(
    tmp_path: Path,
    valid_payload: dict[str, Any],
    capsys: Any,
) -> None:
    source = tmp_path / "input.json"
    output = tmp_path / "out"
    _write(source, valid_payload)

    assert run(["plan", str(source), "--output", str(output)]) == 0
    assert capsys.readouterr().out.strip() == str(output)
    assert sorted(path.name for path in output.iterdir()) == [
        "pick-list.csv",
        "plan.json",
        "report.html",
    ]
    plan = json.loads((output / "plan.json").read_text(encoding="utf-8"))
    assert plan["summary"] == {
        "allocated_stems": 12,
        "demand_stems": 12,
        "shortage_stems": 0,
        "total_cost": "15.00",
    }


def test_shortage_writes_diagnostics_and_exits_one(
    tmp_path: Path,
    valid_payload: dict[str, Any],
) -> None:
    payload = deepcopy(valid_payload)
    payload["inventory"][0]["stems"] = 2
    source = tmp_path / "short.json"
    output = tmp_path / "short-plan"
    _write(source, payload)

    assert run(["plan", str(source), "--output", str(output)]) == 1
    plan = json.loads((output / "plan.json").read_text(encoding="utf-8"))
    requirement = plan["requirements"][0]
    assert requirement["shortage_stems"] == 10
    assert requirement["diagnostics"]["eligible_supply_stems"] == 2


def test_invalid_input_exits_two_without_output(
    tmp_path: Path,
    valid_payload: dict[str, Any],
    capsys: Any,
) -> None:
    payload = deepcopy(valid_payload)
    payload["inventory"][0]["stems"] = 0
    source = tmp_path / "invalid.json"
    output = tmp_path / "must-not-exist"
    _write(source, payload)

    assert run(["plan", str(source), "--output", str(output)]) == 2
    assert not output.exists()
    assert "inventory[0].stems: expected a positive integer" in capsys.readouterr().err


def test_existing_output_is_not_overwritten(
    tmp_path: Path,
    valid_payload: dict[str, Any],
    capsys: Any,
) -> None:
    source = tmp_path / "input.json"
    output = tmp_path / "existing"
    output.mkdir()
    marker = output / "keep.txt"
    marker.write_text("keep", encoding="utf-8")
    _write(source, valid_payload)

    assert run(["plan", str(source), "--output", str(output)]) == 2
    assert marker.read_text(encoding="utf-8") == "keep"
    assert "output directory already exists" in capsys.readouterr().err


def test_outputs_escape_html_and_neutralize_csv_formulas(
    tmp_path: Path,
    valid_payload: dict[str, Any],
) -> None:
    payload = deepcopy(valid_payload)
    payload["plan_id"] = "<script>alert(1)</script>"
    payload["recipes"][0]["name"] = "<script>alert(2)</script>"
    payload["inventory"][0]["flower"] = "=CMD()"
    payload["recipes"][0]["requirements"][0]["accepts"][0]["flower"] = "=CMD()"
    source = tmp_path / "unsafe.json"
    output = tmp_path / "safe-output"
    _write(source, payload)

    assert run(["plan", str(source), "--output", str(output)]) == 0
    report = (output / "report.html").read_text(encoding="utf-8")
    pick_list = (output / "pick-list.csv").read_text(encoding="utf-8")

    assert "<script" not in report
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in report
    assert "'=CMD()" in pick_list


def test_outputs_are_byte_deterministic(
    tmp_path: Path,
    valid_payload: dict[str, Any],
) -> None:
    source = tmp_path / "input.json"
    first = tmp_path / "first"
    second = tmp_path / "second"
    _write(source, valid_payload)

    assert run(["plan", str(source), "--output", str(first)]) == 0
    assert run(["plan", str(source), "--output", str(second)]) == 0

    for name in ("plan.json", "pick-list.csv", "report.html"):
        assert (first / name).read_bytes() == (second / name).read_bytes()
