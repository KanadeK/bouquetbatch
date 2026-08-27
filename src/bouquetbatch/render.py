from __future__ import annotations

import csv
import html
import io
import json
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from bouquetbatch import __version__
from bouquetbatch.model import AcceptedMatch, PlanningDocument
from bouquetbatch.planner import PlanResult


class OutputError(ValueError):
    """Raised when output cannot be created under the public output contract."""


def _decimal(value: Decimal) -> str:
    return format(value, "f")


def _match_dict(match: AcceptedMatch) -> dict[str, Any]:
    result: dict[str, Any] = {"rank": match.rank}
    if match.flower is not None:
        result["flower"] = match.flower
    if match.variety is not None:
        result["variety"] = match.variety
    if match.color is not None:
        result["color"] = match.color
    return result


def plan_to_dict(plan: PlanResult) -> dict[str, Any]:
    return {
        "application_version": __version__,
        "schema_version": 1,
        "plan_id": plan.plan_id,
        "as_of": plan.as_of.isoformat(),
        "summary": {
            "demand_stems": plan.demand_stems,
            "allocated_stems": plan.allocated_stems,
            "shortage_stems": plan.shortage_stems,
            "total_cost": _decimal(plan.total_cost),
        },
        "requirements": [
            {
                "order_id": item.order_id,
                "recipe_id": item.recipe_id,
                "recipe_name": item.recipe_name,
                "requirement_id": item.requirement_id,
                "due_on": item.due_on.isoformat(),
                "priority": item.priority,
                "demand_stems": item.demand_stems,
                "allocated_stems": item.allocated_stems,
                "shortage_stems": item.shortage_stems,
                "allocations": [
                    {
                        "lot_id": allocation.lot_id,
                        "stems": allocation.stems,
                        "match_rank": allocation.match_rank,
                        "cost_per_stem": _decimal(allocation.cost_per_stem),
                        "total_cost": _decimal(allocation.total_cost),
                    }
                    for allocation in item.allocations
                ],
                "diagnostics": {
                    "accepted_matches": [
                        _match_dict(match) for match in item.diagnostics.accepted_matches
                    ],
                    "eligible_supply_stems": item.diagnostics.eligible_supply_stems,
                    "allocated_elsewhere_stems": (item.diagnostics.allocated_elsewhere_stems),
                    "unavailable_stems": item.diagnostics.unavailable_stems,
                    "expired_stems": item.diagnostics.expired_stems,
                },
            }
            for item in plan.requirements
        ],
    }


def render_json(plan: PlanResult) -> str:
    return json.dumps(plan_to_dict(plan), ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _spreadsheet_safe(value: str) -> str:
    return f"'{value}" if value.startswith(("=", "+", "-", "@")) else value


def render_csv(document: PlanningDocument, plan: PlanResult) -> str:
    lots = {lot.lot_id: lot for lot in document.inventory}
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(
        [
            "order_id",
            "due_on",
            "priority",
            "recipe_id",
            "recipe_name",
            "requirement_id",
            "lot_id",
            "flower",
            "variety",
            "color",
            "stems",
            "match_rank",
            "cost_per_stem",
            "total_cost",
        ]
    )
    for requirement in plan.requirements:
        for allocation in requirement.allocations:
            lot = lots[allocation.lot_id]
            writer.writerow(
                [
                    _spreadsheet_safe(requirement.order_id),
                    requirement.due_on.isoformat(),
                    requirement.priority,
                    _spreadsheet_safe(requirement.recipe_id),
                    _spreadsheet_safe(requirement.recipe_name),
                    _spreadsheet_safe(requirement.requirement_id),
                    _spreadsheet_safe(allocation.lot_id),
                    _spreadsheet_safe(lot.flower),
                    _spreadsheet_safe(lot.variety),
                    _spreadsheet_safe(lot.color),
                    allocation.stems,
                    allocation.match_rank,
                    _decimal(allocation.cost_per_stem),
                    _decimal(allocation.total_cost),
                ]
            )
    return output.getvalue()


def _e(value: object) -> str:
    return html.escape(str(value), quote=True)


def render_html(plan: PlanResult) -> str:
    state = "READY" if plan.shortage_stems == 0 else "SHORT"
    requirement_rows: list[str] = []
    allocation_rows: list[str] = []
    for requirement in plan.requirements:
        requirement_rows.append(
            "<tr>"
            f"<td>{_e(requirement.order_id)}</td>"
            f"<td>{_e(requirement.recipe_name)}</td>"
            f"<td>{_e(requirement.requirement_id)}</td>"
            f"<td>{_e(requirement.due_on.isoformat())}</td>"
            f"<td>{requirement.priority}</td>"
            f"<td>{requirement.allocated_stems} / {requirement.demand_stems}</td>"
            f"<td>{requirement.shortage_stems}</td>"
            "</tr>"
        )
        for allocation in requirement.allocations:
            allocation_rows.append(
                "<tr>"
                f"<td>{_e(requirement.order_id)}</td>"
                f"<td>{_e(requirement.requirement_id)}</td>"
                f"<td>{_e(allocation.lot_id)}</td>"
                f"<td>{allocation.stems}</td>"
                f"<td>{allocation.match_rank}</td>"
                f"<td>{_e(_decimal(allocation.total_cost))}</td>"
                "</tr>"
            )

    allocation_body = "".join(allocation_rows) or (
        '<tr><td colspan="6" class="empty">No stems could be allocated.</td></tr>'
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BouquetBatch report - {_e(plan.plan_id)}</title>
<style>
:root {{ color-scheme: light; --ink:#26211d; --muted:#6e6259; --paper:#fffaf5;
--line:#e8d9ce; --leaf:#315c4b; --rose:#b64f68; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:#f3ebe5; color:var(--ink); font:15px/1.5 system-ui,sans-serif; }}
main {{ max-width:1100px; margin:40px auto; padding:0 20px 60px; }}
header {{ display:flex; justify-content:space-between; gap:24px; align-items:end; }}
.eyebrow {{ color:var(--rose); font-weight:700; letter-spacing:.12em; text-transform:uppercase; }}
h1 {{ margin:.2rem 0; font:700 clamp(2rem,5vw,4rem)/1.05 Georgia,serif; }}
.status {{ border:1px solid var(--line); border-radius:999px; padding:8px 14px;
background:var(--paper); color:var(--leaf); font-weight:800; }}
.grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin:28px 0; }}
.card, section {{ background:var(--paper); border:1px solid var(--line); border-radius:14px; }}
.card {{ padding:18px; }}
.card b {{ display:block; font:700 1.7rem Georgia,serif; }}
.card span {{ color:var(--muted); }}
section {{ margin-top:16px; padding:20px; overflow:auto; }}
h2 {{ margin:0 0 12px; font:700 1.25rem Georgia,serif; }}
table {{ width:100%; border-collapse:collapse; white-space:nowrap; }}
th, td {{ padding:10px 12px; border-bottom:1px solid var(--line); text-align:left; }}
th {{ color:var(--muted); font-size:.78rem; letter-spacing:.05em; text-transform:uppercase; }}
.empty {{ color:var(--muted); text-align:center; }}
footer {{ margin-top:20px; color:var(--muted); }}
@media (max-width:720px) {{ .grid {{ grid-template-columns:repeat(2,1fr); }}
header {{ display:block; }} }}
</style>
</head>
<body>
<main>
<header><div><div class="eyebrow">BouquetBatch plan</div><h1>{_e(plan.plan_id)}</h1>
<div>As of {_e(plan.as_of.isoformat())}</div></div><div class="status">{state}</div></header>
<div class="grid">
<div class="card"><b>{plan.demand_stems}</b><span>stems demanded</span></div>
<div class="card"><b>{plan.allocated_stems}</b><span>stems allocated</span></div>
<div class="card"><b>{plan.shortage_stems}</b><span>stems short</span></div>
<div class="card"><b>{_e(_decimal(plan.total_cost))}</b><span>planned stem cost</span></div>
</div>
<section><h2>Requirement coverage</h2><table><thead><tr><th>Order</th><th>Recipe</th>
<th>Requirement</th><th>Due</th><th>Priority</th><th>Allocated</th><th>Short</th>
</tr></thead><tbody>{"".join(requirement_rows)}</tbody></table></section>
<section><h2>Lot pick list</h2><table><thead><tr><th>Order</th><th>Requirement</th>
<th>Lot</th><th>Stems</th><th>Match rank</th><th>Cost</th></tr></thead>
<tbody>{allocation_body}</tbody></table></section>
<footer>Generated offline by BouquetBatch {__version__}. No scripts or remote assets.</footer>
</main>
</body>
</html>
"""


def write_outputs(
    document: PlanningDocument,
    plan: PlanResult,
    output_directory: Path,
) -> None:
    if output_directory.exists():
        raise OutputError(f"{output_directory}: output directory already exists")
    output_directory.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(
        prefix=f".{output_directory.name}-", dir=output_directory.parent
    ) as temporary_name:
        temporary = Path(temporary_name)
        (temporary / "plan.json").write_text(render_json(plan), encoding="utf-8")
        (temporary / "pick-list.csv").write_text(
            render_csv(document, plan), encoding="utf-8", newline=""
        )
        (temporary / "report.html").write_text(render_html(plan), encoding="utf-8")
        temporary.replace(output_directory)
