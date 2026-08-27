from __future__ import annotations

from copy import deepcopy
from typing import Any

from bouquetbatch.input import parse_document
from bouquetbatch.planner import create_plan


def test_planner_repairs_a_greedy_dead_end(valid_payload: dict[str, Any]) -> None:
    payload = deepcopy(valid_payload)
    payload["inventory"] = [
        {
            "lot_id": "rose",
            "flower": "rose",
            "variety": "Freedom",
            "color": "red",
            "stems": 5,
            "cost_per_stem": 1,
            "available_on": "2026-08-27",
            "expires_on": "2026-08-30",
        },
        {
            "lot_id": "tulip",
            "flower": "tulip",
            "variety": "Strong Gold",
            "color": "yellow",
            "stems": 5,
            "cost_per_stem": 1,
            "available_on": "2026-08-27",
            "expires_on": "2026-08-30",
        },
    ]
    payload["recipes"][0]["requirements"] = [
        {
            "requirement_id": "flexible",
            "stems_per_unit": 5,
            "accepts": [
                {"flower": "rose", "rank": 0},
                {"flower": "tulip", "rank": 1},
            ],
        },
        {
            "requirement_id": "rose-only",
            "stems_per_unit": 5,
            "accepts": [{"flower": "rose", "rank": 0}],
        },
    ]
    payload["orders"][0]["quantity"] = 1

    plan = create_plan(parse_document(payload))
    requirements = {item.requirement_id: item for item in plan.requirements}

    assert plan.allocated_stems == 10
    assert requirements["flexible"].allocations[0].lot_id == "tulip"
    assert requirements["rose-only"].allocations[0].lot_id == "rose"


def test_priority_wins_when_supply_is_short(valid_payload: dict[str, Any]) -> None:
    payload = deepcopy(valid_payload)
    payload["inventory"][0]["stems"] = 3
    payload["recipes"][0]["requirements"][0]["stems_per_unit"] = 3
    payload["orders"] = [
        {
            "order_id": "low",
            "recipe_id": "market-bouquet",
            "quantity": 1,
            "due_on": "2026-08-29",
            "priority": 2,
        },
        {
            "order_id": "high",
            "recipe_id": "market-bouquet",
            "quantity": 1,
            "due_on": "2026-08-29",
            "priority": 1,
        },
    ]

    plan = create_plan(parse_document(payload))
    requirements = {item.order_id: item for item in plan.requirements}

    assert requirements["high"].allocated_stems == 3
    assert requirements["low"].shortage_stems == 3


def test_exact_match_and_earlier_expiry_are_preferred(valid_payload: dict[str, Any]) -> None:
    payload = deepcopy(valid_payload)
    payload["inventory"] = [
        {
            "lot_id": "late-exact",
            "flower": "rose",
            "variety": "Freedom",
            "color": "red",
            "stems": 3,
            "cost_per_stem": 2,
            "available_on": "2026-08-27",
            "expires_on": "2026-08-31",
        },
        {
            "lot_id": "early-exact",
            "flower": "rose",
            "variety": "Freedom",
            "color": "red",
            "stems": 3,
            "cost_per_stem": 1,
            "available_on": "2026-08-27",
            "expires_on": "2026-08-29",
        },
        {
            "lot_id": "substitute",
            "flower": "dahlia",
            "variety": "Cornel",
            "color": "red",
            "stems": 3,
            "cost_per_stem": 1,
            "available_on": "2026-08-27",
            "expires_on": "2026-08-28",
        },
    ]
    payload["orders"][0]["quantity"] = 1

    plan = create_plan(parse_document(payload))

    assert [(a.lot_id, a.match_rank) for a in plan.requirements[0].allocations] == [
        ("early-exact", 0)
    ]


def test_expired_supply_is_reported_but_not_allocated(valid_payload: dict[str, Any]) -> None:
    payload = deepcopy(valid_payload)
    payload["inventory"][0]["expires_on"] = "2026-08-28"

    plan = create_plan(parse_document(payload))
    requirement = plan.requirements[0]

    assert requirement.shortage_stems == 12
    assert requirement.diagnostics.expired_stems == 12
    assert requirement.diagnostics.eligible_supply_stems == 0
