from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from bouquetbatch.flow import Edge, MinCostFlow
from bouquetbatch.model import AcceptedMatch, Lot, Order, PlanningDocument, Recipe, Requirement


@dataclass(frozen=True, slots=True)
class Allocation:
    lot_id: str
    stems: int
    match_rank: int
    cost_per_stem: Decimal
    flower: str
    variety: str
    color: str

    @property
    def total_cost(self) -> Decimal:
        return self.cost_per_stem * self.stems


@dataclass(frozen=True, slots=True)
class ShortageDiagnostics:
    accepted_matches: tuple[AcceptedMatch, ...]
    eligible_supply_stems: int
    allocated_elsewhere_stems: int
    unavailable_stems: int
    expired_stems: int


@dataclass(frozen=True, slots=True)
class RequirementPlan:
    order_id: str
    recipe_id: str
    recipe_name: str
    requirement_id: str
    due_on: date
    priority: int
    demand_stems: int
    allocated_stems: int
    shortage_stems: int
    allocations: tuple[Allocation, ...]
    diagnostics: ShortageDiagnostics


@dataclass(frozen=True, slots=True)
class PlanResult:
    plan_id: str
    as_of: date
    demand_stems: int
    allocated_stems: int
    shortage_stems: int
    total_cost: Decimal
    requirements: tuple[RequirementPlan, ...]


@dataclass(frozen=True, slots=True)
class _Demand:
    key: tuple[str, str]
    order: Order
    recipe: Recipe
    requirement: Requirement
    stems: int


@dataclass(frozen=True, slots=True)
class _Candidate:
    lot: Lot
    demand: _Demand
    match_rank: int


def _best_match_rank(lot: Lot, requirement: Requirement) -> int | None:
    ranks = [match.rank for match in requirement.accepts if match.matches(lot)]
    return min(ranks) if ranks else None


def _build_demands(document: PlanningDocument) -> list[_Demand]:
    recipes = {recipe.recipe_id: recipe for recipe in document.recipes}
    demands = [
        _Demand(
            key=(order.order_id, requirement.requirement_id),
            order=order,
            recipe=recipes[order.recipe_id],
            requirement=requirement,
            stems=order.quantity * requirement.stems_per_unit,
        )
        for order in document.orders
        for requirement in recipes[order.recipe_id].requirements
    ]
    return sorted(demands, key=lambda demand: demand.key)


def _eligible(lot: Lot, demand: _Demand) -> bool:
    return lot.available_on <= demand.order.due_on <= lot.expires_on


def create_plan(document: PlanningDocument) -> PlanResult:
    lots = sorted(document.inventory, key=lambda lot: lot.lot_id)
    demands = _build_demands(document)
    candidates = [
        _Candidate(lot=lot, demand=demand, match_rank=match_rank)
        for lot in lots
        for demand in demands
        if (match_rank := _best_match_rank(lot, demand.requirement)) is not None
        and _eligible(lot, demand)
    ]

    source = 0
    lot_node = {lot.lot_id: index + 1 for index, lot in enumerate(lots)}
    demand_offset = 1 + len(lots)
    demand_node = {demand.key: demand_offset + index for index, demand in enumerate(demands)}
    sink = demand_offset + len(demands)
    network = MinCostFlow(sink + 1)

    for lot in lots:
        network.add_edge(source, lot_node[lot.lot_id], lot.stems, 0)
    for demand in demands:
        network.add_edge(demand_node[demand.key], sink, demand.stems, 0)

    total_demand = sum(demand.stems for demand in demands)
    flow_bound = max(1, total_demand)
    tie_max = max(0, len(candidates) - 1)
    expiry_dates = sorted({candidate.lot.expires_on for candidate in candidates})
    expiry_rank = {expiry: index for index, expiry in enumerate(expiry_dates)}
    max_expiry_rank = max(expiry_rank.values(), default=0)
    max_match_rank = max((candidate.match_rank for candidate in candidates), default=0)
    priority_values = sorted({demand.order.priority for demand in demands})
    priority_rank = {priority: index for index, priority in enumerate(priority_values)}

    expiry_weight = flow_bound * tie_max + 1
    lower_than_match = max_expiry_rank * expiry_weight + tie_max
    match_weight = flow_bound * lower_than_match + 1
    lower_than_priority = max_match_rank * match_weight + lower_than_match
    priority_weight = flow_bound * lower_than_priority + 1

    allocation_edges: dict[tuple[str, tuple[str, str]], tuple[Edge, int]] = {}
    for tie_rank, candidate in enumerate(candidates):
        cost = (
            priority_rank[candidate.demand.order.priority] * priority_weight
            + candidate.match_rank * match_weight
            + expiry_rank[candidate.lot.expires_on] * expiry_weight
            + tie_rank
        )
        edge = network.add_edge(
            lot_node[candidate.lot.lot_id],
            demand_node[candidate.demand.key],
            min(candidate.lot.stems, candidate.demand.stems),
            cost,
        )
        allocation_edges[(candidate.lot.lot_id, candidate.demand.key)] = (
            edge,
            candidate.match_rank,
        )

    network.solve(source, sink)
    lots_by_id = {lot.lot_id: lot for lot in lots}
    allocations_by_demand: dict[tuple[str, str], list[Allocation]] = {
        demand.key: [] for demand in demands
    }
    allocated_by_lot: dict[str, int] = {lot.lot_id: 0 for lot in lots}
    for (lot_id, demand_key), (edge, match_rank) in allocation_edges.items():
        if edge.flow:
            lot = lots_by_id[lot_id]
            allocation = Allocation(
                lot_id=lot_id,
                stems=edge.flow,
                match_rank=match_rank,
                cost_per_stem=lot.cost_per_stem,
                flower=lot.flower,
                variety=lot.variety,
                color=lot.color,
            )
            allocations_by_demand[demand_key].append(allocation)
            allocated_by_lot[lot_id] += edge.flow

    requirement_plans: list[RequirementPlan] = []
    for demand in demands:
        allocations = tuple(sorted(allocations_by_demand[demand.key], key=lambda item: item.lot_id))
        allocated = sum(allocation.stems for allocation in allocations)
        matching_lots = [
            lot for lot in lots if _best_match_rank(lot, demand.requirement) is not None
        ]
        eligible_lots = [lot for lot in matching_lots if _eligible(lot, demand)]
        current_by_lot = {allocation.lot_id: allocation.stems for allocation in allocations}
        diagnostics = ShortageDiagnostics(
            accepted_matches=demand.requirement.accepts,
            eligible_supply_stems=sum(lot.stems for lot in eligible_lots),
            allocated_elsewhere_stems=sum(
                allocated_by_lot[lot.lot_id] - current_by_lot.get(lot.lot_id, 0)
                for lot in eligible_lots
            ),
            unavailable_stems=sum(
                lot.stems for lot in matching_lots if lot.available_on > demand.order.due_on
            ),
            expired_stems=sum(
                lot.stems for lot in matching_lots if lot.expires_on < demand.order.due_on
            ),
        )
        requirement_plans.append(
            RequirementPlan(
                order_id=demand.order.order_id,
                recipe_id=demand.recipe.recipe_id,
                recipe_name=demand.recipe.name,
                requirement_id=demand.requirement.requirement_id,
                due_on=demand.order.due_on,
                priority=demand.order.priority,
                demand_stems=demand.stems,
                allocated_stems=allocated,
                shortage_stems=demand.stems - allocated,
                allocations=allocations,
                diagnostics=diagnostics,
            )
        )

    allocated_total = sum(item.allocated_stems for item in requirement_plans)
    return PlanResult(
        plan_id=document.plan_id,
        as_of=document.as_of,
        demand_stems=total_demand,
        allocated_stems=allocated_total,
        shortage_stems=total_demand - allocated_total,
        total_cost=sum(
            (
                allocation.total_cost
                for item in requirement_plans
                for allocation in item.allocations
            ),
            start=Decimal(0),
        ),
        requirements=tuple(requirement_plans),
    )
