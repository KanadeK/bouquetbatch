from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from bouquetbatch.cli import run


def test_write_failure_leaves_no_partial_output(
    tmp_path: Path,
    valid_payload: dict[str, Any],
    monkeypatch: Any,
    capsys: Any,
) -> None:
    source = tmp_path / "input.json"
    source.write_text(json.dumps(valid_payload), encoding="utf-8")
    output = tmp_path / "result"
    original_write_text = Path.write_text

    def fail_on_csv(path: Path, *args: Any, **kwargs: Any) -> int:
        if path.name == "pick-list.csv":
            raise OSError("simulated disk failure")
        return original_write_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", fail_on_csv)

    assert run(["plan", str(source), "--output", str(output)]) == 2
    assert not output.exists()
    assert not list(tmp_path.glob(".result-*"))
    assert "simulated disk failure" in capsys.readouterr().err
