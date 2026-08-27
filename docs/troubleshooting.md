# Troubleshooting and repair

## Exit 2: invalid input

Read the first error line. It includes the precise JSON path.

```text
error: inventory[0].stems: expected a positive integer
```

Repair the named field, then rerun with a new output directory. BouquetBatch rejects unknown fields, booleans used as integers, duplicate IDs, invalid dates, broken recipe references, and non-positive quantities.

## Exit 2: output directory already exists

BouquetBatch never overwrites a prior plan. Inspect or rename the existing directory, or choose a different output path. Do not point the command at a directory containing unrelated files.

## Exit 1: valid shortage

Open plan.json or report.html. For every short requirement, inspect eligible supply, stems allocated elsewhere, matching lots arriving too late, and matching lots already expired. Correct a mistaken date, match, priority, or quantity, or add real stock, then write a new plan directory. Exit 1 is an auditable result, not a crash.

## uv cannot write its user cache

Keep the workaround project-local.

```powershell
$env:UV_CACHE_DIR = "$PWD/.uv-cache"
uv sync --locked --dev
```

```sh
UV_CACHE_DIR=.uv-cache uv sync --locked --dev
```

## A test or CI job fails

```console
uv sync --locked --dev
uv run python scripts/check.py
```

The first failing command is printed with real stdout and stderr. Fix that failure and rerun the whole gate. A successful build does not replace tests or clean-install verification.

## Packaging fails

Confirm that pyproject.toml, README.md, LICENSE, and uv.lock are tracked, then run uv build. The release-grade check builds into a temporary directory and installs the wheel with --no-index, proving that it has no undeclared runtime dependency.
