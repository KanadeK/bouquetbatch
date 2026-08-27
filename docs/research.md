# Research and differentiation

Research snapshot: 2026-08-27.

## Evidence of the workflow

- [Stems Planner](https://stemsplanner.com/) markets recipe, order, inventory, and consolidated stem-report workflows as an alternative to spreadsheets.
- [FreshPortal](https://freshportal.com/bouquets-and-arrangements) describes bouquet recipes, stock allocation, and ingredient substitutions.
- [Curate's florist spreadsheet](https://curate.co/resources/wedding-florist-excel-spreadsheet/) demonstrates both stem-count demand and the common spreadsheet workaround.
- [Acanta](https://www.acanta.app/) describes matching stock to recipes, substitutes, and perishable first-in-first-out use.

These sources establish a real planning problem. They do not establish market size, revenue, or guaranteed GitHub popularity.

## Open-source search

GitHub searches covered florist bouquet recipe stem inventory optimizer, flower-stem inventory planners, bouquet recipe planners, exact-name matches for BouquetBatch, and repository-name availability.

Representative results such as [Flowershop Smart Management System](https://github.com/hammond022/Flowershop-Smart-Management-System-FSMS), [florists-inventory](https://github.com/jakubosiak/florists-inventory), [FlowerShopInventory](https://github.com/rochellegb/FlowerShopInventory), and [BloomInventories](https://github.com/isla-just/BloomInventories) focus on POS, inventory CRUD, roles, or learning projects. None of the inspected repositories exposed the same narrow contract: offline deterministic allocation of perishable lots across dated recipe requirements with ranked substitutions.

No exact repository-name match was found, and KanadeK/bouquetbatch was unclaimed at the time of the check. Search absence is not proof of universal novelty; it is evidence that the selected framing is differentiated from the inspected results.

## Local portfolio check

The workspace and prior-project registry were checked for florist, bouquet, recipe-allocation, aliquot, and centrifuge concepts. No local florist allocator was found. Several ideas were rejected because they overlapped local work, including theatre traffic, USB-C topology, sheet-music page turns, and wallpaper cutting.

## Differentiation boundary

BouquetBatch deliberately does one computation that CRUD-oriented flower-shop projects generally do not:

```text
perishable lots + recipe alternatives + dated competing orders
                              |
                              v
             deterministic, shortage-aware allocation
                              |
                              v
              pick list + machine plan + HTML report
```

The project remains differentiated only while it avoids becoming a generic shop-management suite.
