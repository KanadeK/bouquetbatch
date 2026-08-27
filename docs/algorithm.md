# Allocation algorithm

BouquetBatch builds a directed network:

```text
source -> one node per lot -> one node per order requirement -> sink
```

The source-to-lot capacity is the lot's stem count. Requirement-to-sink capacity is order quantity multiplied by stems per bouquet. A lot-to-requirement edge exists only when the recipe match and due-date eligibility both pass.

Successive shortest augmenting paths compute maximum flow at minimum integer cost. Reverse residual edges allow a later path to repair an earlier local choice. This matters when roses can satisfy both a flexible focal requirement and a rose-only requirement while tulips can satisfy only the flexible one.

Cost bands are derived from total demand and the actual edge set:

```text
priority band > every possible substitution + expiry + tie difference
substitution band > every possible expiry + tie difference
expiry band > every possible stable-tie difference
```

Python integers do not overflow, so the bands preserve the documented lexicographic objectives without floating-point tolerances.

The intended workload is independent-florist batch planning, not industrial-scale scheduling. New constraint families require a new architecture decision rather than hidden heuristics.
