# Contributing

Thank you for improving BouquetBatch.

Open an issue with one concrete allocator problem and a small input that demonstrates it. Keep proposals inside the boundary: perishable lots, recipe matching, order allocation, diagnostics, or output correctness. POS, CRM, purchasing, accounts, and hosted services are out of scope.

```console
git clone https://github.com/KanadeK/bouquetbatch.git
cd bouquetbatch
uv sync --locked --dev
uv run python scripts/check.py
```

Add a failing test before changing behavior. Keep public input or output changes versioned and update docs/spec.md. Do not add a runtime dependency without explaining why the standard library cannot meet the requirement.

A pull request should contain one focused change, its tests, and contract documentation when needed. Describe observable behavior and failures rather than aspirations.
