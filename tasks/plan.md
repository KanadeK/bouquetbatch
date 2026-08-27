# Implementation plan

## Phase 1: contract and project skeleton

Deliver packaging metadata, typed models, strict JSON parsing, and boundary tests. Success: valid data becomes domain objects; malformed fields, references, dates, identifiers, and numbers fail with precise paths.

## Phase 2: allocation engine

Deliver the graph primitive and planner. Success: capacity conservation, objective order, substitution choice, expiry behavior, and a greedy-counterexample pass deterministically.

## Phase 3: outputs and CLI

Deliver JSON, CSV, HTML, exit codes, and console entry point. Success: complete input exits 0, shortage exits 1, invalid input exits 2 without output, HTML is escaped, and CSV formulas are neutralized.

## Phase 4: examples and documentation

Deliver complete, shortage, and invalid examples; generated output; bilingual quick starts; reference and troubleshooting docs. Success: a new user can reproduce output and exercise every exit code.

## Phase 5: automation and release

Deliver one local gate, cross-platform CI, package builds, tag-triggered release, and examples archive. Success: local and remote gates pass and the downloaded wheel installs cleanly.
