# BouquetBatch

[中文说明](README.zh-CN.md)

[![CI](https://github.com/KanadeK/bouquetbatch/actions/workflows/ci.yml/badge.svg)](https://github.com/KanadeK/bouquetbatch/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/KanadeK/bouquetbatch)](https://github.com/KanadeK/bouquetbatch/releases)
[![Python](https://img.shields.io/badge/Python-3.11%2B-315c4b)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-b64f68.svg)](LICENSE)

**Stop silently double-booking stems.**

BouquetBatch is an offline CLI that turns perishable flower lots, bouquet recipes, ranked substitutions, and dated orders into an auditable pick plan. It performs a real min-cost maximum-flow optimization; it is not a POS screen, inventory CRUD demo, or hosted service.

```text
inventory lots ─┐
recipe rules ───┼─> deterministic allocator ─> plan.json
dated orders ───┘                            ├> pick-list.csv
                                             └> report.html
```

## Why it exists

A spreadsheet can count stems, but competing orders make allocation subtle:

- one lot may satisfy several recipes;
- a flexible requirement can consume stock that a strict requirement uniquely needs;
- substitutions have an explicit preference order;
- lots may not have arrived yet or may expire before an order is due; and
- a shortage should be visible, not hidden by a plausible-looking total.

BouquetBatch solves that narrow problem locally and reproducibly.

## Install

Python 3.11 or newer is required.

```console
uv tool install .
bouquetbatch --version
```

From the v0.1.0 GitHub Release:

```console
uv tool install https://github.com/KanadeK/bouquetbatch/releases/download/v0.1.0/bouquetbatch-0.1.0-py3-none-any.whl
```

The installed planner has no runtime dependencies and does not use the network.

## Run the complete example

```console
bouquetbatch plan examples/complete.json --output market-plan
```

The command creates:

- **plan.json**: stable machine-readable allocation and shortage diagnostics;
- **pick-list.csv**: one row per lot-to-requirement pick, safe to open in a spreadsheet; and
- **report.html**: a self-contained, script-free human report.

The committed [complete output](examples/generated/complete/plan.json) shows two orders sharing exact and substitute flower lots.

## Input in one minute

```json
{
  "schema_version": 1,
  "plan_id": "weekend-market",
  "as_of": "2026-08-27",
  "inventory": [{
    "lot_id": "rose-red-a",
    "flower": "rose",
    "variety": "Freedom",
    "color": "red",
    "stems": 40,
    "cost_per_stem": 1.25,
    "available_on": "2026-08-27",
    "expires_on": "2026-08-30"
  }],
  "recipes": [{
    "recipe_id": "market-bouquet",
    "name": "Market Bouquet",
    "requirements": [{
      "requirement_id": "focal",
      "stems_per_unit": 3,
      "accepts": [
        {"flower": "rose", "color": "red", "rank": 0},
        {"flower": "dahlia", "color": "red", "rank": 1}
      ]
    }]
  }],
  "orders": [{
    "order_id": "sat-stand",
    "recipe_id": "market-bouquet",
    "quantity": 8,
    "due_on": "2026-08-29",
    "priority": 1
  }]
}
```

A match may specify flower, variety, color, or a combination. Lower **rank** is better. Lower order **priority** numbers are more important. See the [input reference](docs/input-format.md) and [complete schema contract](docs/spec.md).

## Allocation rules

The engine first maximizes total allocated stems. Among equally full plans it then, in strict order:

1. protects higher-priority orders;
2. prefers lower-ranked substitutions;
3. consumes earlier-expiring lots; and
4. uses stable identifiers to break remaining ties.

This order is encoded as non-overlapping integer cost bands, so a lower-order preference cannot outweigh a higher one. See [the algorithm note](docs/algorithm.md) and [ADR 0001](docs/decisions/0001-allocation-engine.md).

## Shortage is a valid result

```console
bouquetbatch plan examples/shortage.json --output short-plan
echo $?
# 1
```

A shortage still writes all three outputs. Each short requirement reports eligible supply, stock allocated elsewhere, stock arriving too late, and expired stock. BouquetBatch does not invent a purchase recommendation.

| Code | Meaning |
| --- | --- |
| 0 | Complete plan written |
| 1 | Valid plan written with shortages |
| 2 | Invalid command, input, I/O, or existing output directory |

See [troubleshooting](docs/troubleshooting.md) for copy-ready repair steps.

## Reproduce the release gate

```console
uv sync --locked --dev
uv run python scripts/check.py
```

The gate checks format, lint, strict typing, branch coverage, complete/short/invalid examples, wheel and source builds, and installation of the wheel into a clean virtual environment. CI runs the same command on Linux and Windows.

## Scope

BouquetBatch does not provide POS, CRM, quoting, purchasing, accounts, cloud sync, image recognition, or a general production scheduler. The [research snapshot](docs/research.md) explains how this focused allocator differs from inspected flower-shop CRUD projects.

Contributions that improve the allocator's documented contract are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and the [changelog](CHANGELOG.md).

## License

MIT
