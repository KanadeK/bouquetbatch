from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Lot:
    lot_id: str
    flower: str
    variety: str
    color: str
    stems: int
    cost_per_stem: Decimal
    available_on: date
    expires_on: date


@dataclass(frozen=True, slots=True)
class AcceptedMatch:
    rank: int
    flower: str | None
    variety: str | None
    color: str | None

    def matches(self, lot: Lot) -> bool:
        return (
            (self.flower is None or self.flower == lot.flower)
            and (self.variety is None or self.variety == lot.variety)
            and (self.color is None or self.color == lot.color)
        )


@dataclass(frozen=True, slots=True)
class Requirement:
    requirement_id: str
    stems_per_unit: int
    accepts: tuple[AcceptedMatch, ...]


@dataclass(frozen=True, slots=True)
class Recipe:
    recipe_id: str
    name: str
    requirements: tuple[Requirement, ...]


@dataclass(frozen=True, slots=True)
class Order:
    order_id: str
    recipe_id: str
    quantity: int
    due_on: date
    priority: int


@dataclass(frozen=True, slots=True)
class PlanningDocument:
    schema_version: int
    plan_id: str
    as_of: date
    inventory: tuple[Lot, ...]
    recipes: tuple[Recipe, ...]
    orders: tuple[Order, ...]
