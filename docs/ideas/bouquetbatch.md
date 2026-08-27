# BouquetBatch concept brief

Status: selected for implementation on 2026-08-27.

## Problem

Independent florists often plan several bouquets from perishable flower lots in a spreadsheet. A recipe may accept substitutions, lots expire on different dates, and several orders compete for the same stems. The hard part is deciding which physical lots to pick for which requirement without silently over-allocating stock.

## Product promise

Given one local JSON file containing flower lots, bouquet recipes, substitution rules, and dated orders, BouquetBatch creates a deterministic allocation plan, a spreadsheet-safe pick list, and a self-contained HTML report.

The planner must:

1. maximize fulfilled stems;
2. protect higher-priority orders when stock is short;
3. prefer exact recipe matches over substitutions;
4. consume earlier-expiring eligible lots first; and
5. produce the same result for the same input.

## Candidate decision

| Candidate | Existing overlap | Decision |
| --- | --- | --- |
| Centrifuge tube balancer | SpinZero and centrifugeR cover the core arrangement problem | Reject |
| Stained-glass cutting planner | Existing nesting tools cover the central workflow | Reject |
| Theatre movement collision checker | Local project stagetraffic already covers performer-path collisions | Reject |
| Florist batch allocator | Public results were dominated by POS and inventory CRUD; no focused offline allocator was found | Select |

This is a dated novelty check, not a claim that no similar software exists anywhere.

## Non-goals

- POS, CRM, quoting, invoicing, or accounts;
- purchasing, vendor ordering, or price prediction;
- cloud synchronization or a hosted service;
- image recognition or AI-generated arrangements;
- a general production scheduler; or
- a graphical shell around placeholder data.

## Smallest useful release

- `bouquetbatch plan INPUT --output DIRECTORY`;
- a versioned JSON input contract;
- real min-cost maximum-flow allocation;
- complete and shortage examples;
- JSON, CSV, and HTML outputs;
- clear exit codes and failure repair instructions;
- unit, integration, output-safety, packaging, and clean-install checks; and
- CI plus a tagged GitHub Release with packages and example outputs.

The release succeeds when a florist can run one offline command and see exactly which lot supplies each requirement and why any shortage remains.
