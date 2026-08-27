from __future__ import annotations

import json
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import cast

from bouquetbatch.model import (
    AcceptedMatch,
    Lot,
    Order,
    PlanningDocument,
    Recipe,
    Requirement,
)


class InputError(ValueError):
    """Raised when a planning document violates the public input contract."""


def _object(
    value: object,
    path: str,
    required: set[str],
    optional: set[str] | None = None,
) -> dict[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise InputError(f"{path}: expected an object")
    result = cast(dict[str, object], value)
    allowed = required | (optional or set())
    unknown = sorted(set(result) - allowed)
    if unknown:
        raise InputError(f"{path}: unknown field '{unknown[0]}'")
    missing = sorted(required - set(result))
    if missing:
        raise InputError(f"{path}: missing field '{missing[0]}'")
    return result


def _array(value: object, path: str) -> list[object]:
    if not isinstance(value, list):
        raise InputError(f"{path}: expected an array")
    return cast(list[object], value)


def _string(value: object, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InputError(f"{path}: expected a non-empty string")
    return value


def _positive_integer(value: object, path: str) -> int:
    if type(value) is not int or value <= 0:
        raise InputError(f"{path}: expected a positive integer")
    return value


def _non_negative_integer(value: object, path: str) -> int:
    if type(value) is not int or value < 0:
        raise InputError(f"{path}: expected a non-negative integer")
    return value


def _non_negative_decimal(value: object, path: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        raise InputError(f"{path}: expected a non-negative number")
    try:
        result = Decimal(str(value))
    except InvalidOperation as error:
        raise InputError(f"{path}: expected a non-negative number") from error
    if not result.is_finite() or result < 0:
        raise InputError(f"{path}: expected a non-negative number")
    return result


def _date(value: object, path: str) -> date:
    text = _string(value, path)
    try:
        result = date.fromisoformat(text)
    except ValueError as error:
        raise InputError(f"{path}: expected a date in YYYY-MM-DD format") from error
    if result.isoformat() != text:
        raise InputError(f"{path}: expected a date in YYYY-MM-DD format")
    return result


def _unique(identifier: str, seen: set[str], path: str) -> None:
    if identifier in seen:
        raise InputError(f"{path}: duplicate '{identifier}'")
    seen.add(identifier)


def _parse_match(value: object, path: str) -> AcceptedMatch:
    item = _object(
        value,
        path,
        required={"rank"},
        optional={"flower", "variety", "color"},
    )
    fields = {
        name: _string(item[name], f"{path}.{name}") if name in item else None
        for name in ("flower", "variety", "color")
    }
    if all(field is None for field in fields.values()):
        raise InputError(f"{path}: expected at least one of flower, variety, or color")
    return AcceptedMatch(
        rank=_non_negative_integer(item["rank"], f"{path}.rank"),
        flower=fields["flower"],
        variety=fields["variety"],
        color=fields["color"],
    )


def _parse_lot(value: object, path: str) -> Lot:
    item = _object(
        value,
        path,
        required={
            "lot_id",
            "flower",
            "variety",
            "color",
            "stems",
            "cost_per_stem",
            "available_on",
            "expires_on",
        },
    )
    available_on = _date(item["available_on"], f"{path}.available_on")
    expires_on = _date(item["expires_on"], f"{path}.expires_on")
    if available_on > expires_on:
        raise InputError(f"{path}.available_on: must be on or before expires_on")
    return Lot(
        lot_id=_string(item["lot_id"], f"{path}.lot_id"),
        flower=_string(item["flower"], f"{path}.flower"),
        variety=_string(item["variety"], f"{path}.variety"),
        color=_string(item["color"], f"{path}.color"),
        stems=_positive_integer(item["stems"], f"{path}.stems"),
        cost_per_stem=_non_negative_decimal(item["cost_per_stem"], f"{path}.cost_per_stem"),
        available_on=available_on,
        expires_on=expires_on,
    )


def _parse_recipe(value: object, path: str) -> Recipe:
    item = _object(value, path, required={"recipe_id", "name", "requirements"})
    raw_requirements = _array(item["requirements"], f"{path}.requirements")
    if not raw_requirements:
        raise InputError(f"{path}.requirements: expected at least one item")
    requirements: list[Requirement] = []
    seen: set[str] = set()
    for index, raw_requirement in enumerate(raw_requirements):
        requirement_path = f"{path}.requirements[{index}]"
        data = _object(
            raw_requirement,
            requirement_path,
            required={"requirement_id", "stems_per_unit", "accepts"},
        )
        requirement_id = _string(data["requirement_id"], f"{requirement_path}.requirement_id")
        _unique(requirement_id, seen, f"{requirement_path}.requirement_id")
        raw_accepts = _array(data["accepts"], f"{requirement_path}.accepts")
        if not raw_accepts:
            raise InputError(f"{requirement_path}.accepts: expected at least one item")
        requirements.append(
            Requirement(
                requirement_id=requirement_id,
                stems_per_unit=_positive_integer(
                    data["stems_per_unit"], f"{requirement_path}.stems_per_unit"
                ),
                accepts=tuple(
                    _parse_match(match, f"{requirement_path}.accepts[{match_index}]")
                    for match_index, match in enumerate(raw_accepts)
                ),
            )
        )
    return Recipe(
        recipe_id=_string(item["recipe_id"], f"{path}.recipe_id"),
        name=_string(item["name"], f"{path}.name"),
        requirements=tuple(requirements),
    )


def _parse_order(value: object, path: str) -> Order:
    item = _object(
        value,
        path,
        required={"order_id", "recipe_id", "quantity", "due_on", "priority"},
    )
    return Order(
        order_id=_string(item["order_id"], f"{path}.order_id"),
        recipe_id=_string(item["recipe_id"], f"{path}.recipe_id"),
        quantity=_positive_integer(item["quantity"], f"{path}.quantity"),
        due_on=_date(item["due_on"], f"{path}.due_on"),
        priority=_positive_integer(item["priority"], f"{path}.priority"),
    )


def parse_document(value: object) -> PlanningDocument:
    root = _object(
        value,
        "document",
        required={"schema_version", "plan_id", "as_of", "inventory", "recipes", "orders"},
    )
    if type(root["schema_version"]) is not int or root["schema_version"] != 1:
        raise InputError("schema_version: expected 1")
    as_of = _date(root["as_of"], "as_of")

    inventory: list[Lot] = []
    lot_ids: set[str] = set()
    for index, raw_lot in enumerate(_array(root["inventory"], "inventory")):
        lot = _parse_lot(raw_lot, f"inventory[{index}]")
        _unique(lot.lot_id, lot_ids, f"inventory[{index}].lot_id")
        inventory.append(lot)

    recipes: list[Recipe] = []
    recipe_ids: set[str] = set()
    for index, raw_recipe in enumerate(_array(root["recipes"], "recipes")):
        recipe = _parse_recipe(raw_recipe, f"recipes[{index}]")
        _unique(recipe.recipe_id, recipe_ids, f"recipes[{index}].recipe_id")
        recipes.append(recipe)

    orders: list[Order] = []
    order_ids: set[str] = set()
    for index, raw_order in enumerate(_array(root["orders"], "orders")):
        order = _parse_order(raw_order, f"orders[{index}]")
        _unique(order.order_id, order_ids, f"orders[{index}].order_id")
        if order.recipe_id not in recipe_ids:
            raise InputError(f"orders[{index}].recipe_id: unknown recipe '{order.recipe_id}'")
        if order.due_on < as_of:
            raise InputError(f"orders[{index}].due_on: must be on or after as_of")
        orders.append(order)

    return PlanningDocument(
        schema_version=1,
        plan_id=_string(root["plan_id"], "plan_id"),
        as_of=as_of,
        inventory=tuple(inventory),
        recipes=tuple(recipes),
        orders=tuple(orders),
    )


def load_document(path: Path) -> PlanningDocument:
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as error:
        raise InputError(f"{path}: {error}") from error
    try:
        value = json.loads(source, parse_float=Decimal)
    except json.JSONDecodeError as error:
        raise InputError(
            f"{path}: invalid JSON at line {error.lineno}, column {error.colno}"
        ) from error
    return parse_document(value)
