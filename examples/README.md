# Example set

- `complete.json` allocates two market orders, uses exact matches first, and then uses ranked substitutions.
- `shortage.json` is valid but exits 1 because some matching stems are expired or not yet available.
- `invalid.json` exits 2 because an inventory lot has zero stems.
- `generated/complete` and `generated/shortage` are committed reference outputs from v0.1.0.

Run from the repository root:

```console
bouquetbatch plan examples/complete.json --output my-plan
bouquetbatch plan examples/shortage.json --output my-short-plan
bouquetbatch plan examples/invalid.json --output never-created
```
