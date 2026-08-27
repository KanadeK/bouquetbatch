# ADR 0001: Use min-cost maximum flow

Status: accepted on 2026-08-27.

## Context

Finite flower lots must be shared across many requirements. A greedy first-match loop can strand flexible stock on a requirement that had a unique alternative, reducing total fulfillment. Results also need deterministic, explainable preferences.

## Decision

Model lots and order requirements as a capacitated bipartite network and solve it with a successive-shortest-augmenting-path min-cost maximum-flow algorithm using Python's standard library.

Maximum flow establishes the primary objective. Integer edge costs encode order priority, substitution rank, expiry, and stable tie order in non-overlapping weight bands.

## Consequences

- The engine finds globally better allocations than a local greedy rule for this model.
- Each allocation maps directly to a graph edge, keeping reports auditable.
- Runtime installation has no solver dependency and works offline.
- The project owns a small graph algorithm and needs focused unit tests, including a greedy-counterexample.
- This is not a general mixed-integer scheduler; new constraint families require a fresh decision.
