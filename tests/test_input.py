from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest

from bouquetbatch.input import InputError, load_document, parse_document


def test_parse_valid_document(valid_payload: dict[str, Any]) -> None:
    document = parse_document(valid_payload)

    assert document.plan_id == "weekend-market"
    assert document.inventory[0].stems == 12
    assert document.recipes[0].requirements[0].accepts[1].rank == 1
    assert document.orders[0].recipe_id == "market-bouquet"


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (
            lambda data: data["inventory"][0].update({"stems": True}),
            r"inventory\[0\]\.stems: expected a positive integer",
        ),
        (
            lambda data: data["inventory"][0].update({"mystery": "value"}),
            r"inventory\[0\]: unknown field 'mystery'",
        ),
        (
            lambda data: data["orders"][0].update({"recipe_id": "missing"}),
            r"orders\[0\]\.recipe_id: unknown recipe 'missing'",
        ),
        (
            lambda data: data["orders"][0].update({"due_on": "2026-08-26"}),
            r"orders\[0\]\.due_on: must be on or after as_of",
        ),
    ],
)
def test_invalid_documents_fail_at_precise_path(
    valid_payload: dict[str, Any],
    mutate: Any,
    message: str,
) -> None:
    payload = deepcopy(valid_payload)
    mutate(payload)

    with pytest.raises(InputError, match=message):
        parse_document(payload)


def test_duplicate_identifier_is_rejected(valid_payload: dict[str, Any]) -> None:
    payload = deepcopy(valid_payload)
    payload["inventory"].append(deepcopy(payload["inventory"][0]))

    with pytest.raises(InputError, match=r"inventory\[1\]\.lot_id: duplicate 'rose-red-a'"):
        parse_document(payload)


def test_load_document_reports_invalid_json(tmp_path: Path) -> None:
    source = tmp_path / "broken.json"
    source.write_text("{", encoding="utf-8")

    with pytest.raises(InputError, match=r"invalid JSON"):
        load_document(source)
