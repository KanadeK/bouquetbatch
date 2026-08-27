# BouquetBatch v0.1 specification

## Goal and interface

Turn one versioned JSON document into an auditable flower-stem allocation. Runtime behavior is local, deterministic, and network-free.

```text
bouquetbatch plan INPUT --output DIRECTORY
bouquetbatch --version
```

INPUT is a UTF-8 JSON file. DIRECTORY must not exist. Output is created only after validation and planning.

Exit codes: 0 means every stem was allocated; 1 means a valid plan was written with shortages; 2 means command, I/O, or validation failure and no output. Errors go to standard error.

## Input contract

The top-level object contains schema_version (exactly 1), non-empty plan_id, ISO date as_of, and arrays inventory, recipes, and orders.

Each inventory lot has unique non-empty lot_id; non-empty flower, variety, and color; positive integer stems; non-negative cost_per_stem; and ISO dates available_on and expires_on, with availability not after expiry.

Each recipe has unique recipe_id, non-empty name, and non-empty requirements. A requirement has a recipe-local unique requirement_id, positive stems_per_unit, and non-empty accepts. An accepted match has non-negative integer rank and one or more of flower, variety, or color. A lot matches when every supplied field equals the lot field. Lower rank is preferred.

Each order has unique order_id, an existing recipe_id, positive integer quantity, due_on on or after as_of, and positive integer priority. Lower priority numbers are more important. Unknown fields are rejected so input mistakes fail visibly.

## Eligibility and objectives

A lot can supply a requirement only when it matches an accepted match and available_on <= due_on <= expires_on. If several matches fit, the lowest rank is used.

The engine computes min-cost maximum flow over source -> lots -> order requirements -> sink. Capacities are stem counts and quantity times stems_per_unit. Integer costs encode this strict order:

1. maximize allocated stems;
2. protect higher-priority orders;
3. prefer lower substitution ranks;
4. prefer earlier-expiring lots; and
5. break ties by stable identifiers.

Weight bands are derived from the input so no lower-order preference can outweigh one unit of a higher preference.

## Outputs

plan.json records versions, totals, one entry per requirement, allocations, cost totals, and shortage diagnostics. pick-list.csv contains one row per allocation and spreadsheet-safe text. report.html is self-contained, script-free, and escapes all input strings. Ordering is stable, so the same input and version produce byte-identical outputs.

## Security boundary

JSON is untrusted at the CLI boundary. The parser enforces the documented shape and types. Runtime code performs no shell execution and no network access. HTML is escaped. CSV text beginning with =, +, -, or @ is prefixed with a single quote.

## Acceptance

```text
uv sync --locked --all-extras --dev
uv run python scripts/check.py
uv build
```

The check runs formatting, linting, typing, tests with coverage, both planning examples, and a clean-wheel smoke test. CI runs the same gate on Linux and Windows. A release tag publishes a wheel, source distribution, and examples archive.
