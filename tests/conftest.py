from __future__ import annotations

from typing import Any

import pytest


@pytest.fixture
def valid_payload() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "plan_id": "weekend-market",
        "as_of": "2026-08-27",
        "inventory": [
            {
                "lot_id": "rose-red-a",
                "flower": "rose",
                "variety": "Freedom",
                "color": "red",
                "stems": 12,
                "cost_per_stem": 1.25,
                "available_on": "2026-08-27",
                "expires_on": "2026-08-30",
            }
        ],
        "recipes": [
            {
                "recipe_id": "market-bouquet",
                "name": "Market Bouquet",
                "requirements": [
                    {
                        "requirement_id": "focal",
                        "stems_per_unit": 3,
                        "accepts": [
                            {"flower": "rose", "color": "red", "rank": 0},
                            {"flower": "dahlia", "color": "red", "rank": 1},
                        ],
                    }
                ],
            }
        ],
        "orders": [
            {
                "order_id": "sat-stand",
                "recipe_id": "market-bouquet",
                "quantity": 4,
                "due_on": "2026-08-29",
                "priority": 1,
            }
        ],
    }
