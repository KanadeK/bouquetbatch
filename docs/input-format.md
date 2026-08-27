# Input format

The input is one UTF-8 JSON object. Unknown fields are rejected. Dates use YYYY-MM-DD.

## Top level

| Field | Type | Meaning |
| --- | --- | --- |
| schema_version | integer | Must be 1 |
| plan_id | non-empty string | Name copied into outputs |
| as_of | date | Planning date |
| inventory | array | Physical flower lots |
| recipes | array | Reusable bouquet recipes |
| orders | array | Dated recipe quantities |

## Inventory lot

Each lot_id is unique. Flower, variety, and color are non-empty strings. Stems is a positive integer. Cost per stem is a non-negative JSON number. Available and expiry dates are inclusive, and availability cannot be after expiry.

## Recipe requirement

Each recipe has recipe_id, name, and at least one requirement. Requirement IDs are unique inside their recipe. A requirement has positive stems_per_unit and one or more accepted match objects.

An accepted match contains non-negative integer rank and at least one of flower, variety, or color. Every supplied field must equal the lot. The lowest matching rank is used.

```json
{
  "requirement_id": "focal",
  "stems_per_unit": 3,
  "accepts": [
    {"flower": "rose", "color": "red", "rank": 0},
    {"flower": "dahlia", "color": "red", "rank": 1}
  ]
}
```

## Order

Each order_id is unique. Recipe ID must reference the same document. Quantity and priority are positive integers; lower priority numbers are more important. Due date must be on or after as_of.

A requirement demands quantity multiplied by stems_per_unit. A lot is eligible only when its match succeeds and its availability range includes the order due date.

The executable [complete example](../examples/complete.json) is the recommended starting point.
