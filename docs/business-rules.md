# Fictional screening specification

Policy ID: **demo-cre-1.0**. These thresholds are invented solely for this portfolio project.

## Inputs and validation

| Field | Meaning | Constraints |
| --- | --- | --- |
| borrower | Fictional borrower name | Trimmed, 1–80 characters, no control characters |
| property_type | Contextual asset category | Industrial, Office, Retail, Multifamily |
| loan_amount | Requested principal in dollars | 1–1,000,000,000, at most 2 decimals |
| property_value | Fictional collateral value in dollars | 1–1,000,000,000, at most 2 decimals |
| noi | Annual net operating income in dollars | 0–1,000,000,000, at most 2 decimals |
| annual_debt_service | Annual principal/interest service in dollars | 1–1,000,000,000, at most 2 decimals |

API monetary values may be decimal strings or JSON numbers. Decimal strings are recommended to preserve decimal amounts. Booleans, nulls, arrays, objects, non-finite values, unknown fields, and numeric representations longer than 30 characters are rejected. Scientific notation within the constraints is accepted and normalized. Every field is required.

## Formulas and outcomes

| Rule | Formula | Pass | Review | Decline |
| --- | --- | --- | --- | --- |
| DSCR | NOI / annual debt service | ≥ 1.25 | ≥ 1.00 and < 1.25 | < 1.00 |
| LTV | loan amount / property value × 100 | ≤ 75% | > 75% and ≤ 85% | > 85% |
| Debt yield | NOI / loan amount × 100 | ≥ 8% | ≥ 6% and < 8% | < 6% |

**Precedence:** decline > review > eligible. All rules are evaluated; there is no early exit. No weighted average may cancel a decline trigger. Property category is not a decision factor.

Python Decimal arithmetic uses its default 28-digit precision. Comparisons occur before conversion to JSON numeric values or display rounding. Each rule includes a decimal `comparison_value` string in exported evidence. Cards and explanatory text show two decimal places; a value just below a boundary can therefore display the same rounded value as the boundary while still correctly triggering review. The policy reference states this explicitly.

## Sample scenarios

| Scenario | Loan | Value | NOI | Debt service | DSCR | LTV | Debt yield | Outcome |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Harbor Point | 4,500,000 | 6,500,000 | 520,000 | 380,000 | 1.37 | 69.23% | 11.56% | Eligible |
| Juniper Square | 4,500,000 | 5,800,000 | 350,000 | 300,000 | 1.17 | 77.59% | 7.78% | Review |
| Cedar Commons | 4,500,000 | 5,000,000 | 250,000 | 300,000 | 0.83 | 90.00% | 5.56% | Decline |

Eligible is a screening handoff, not a credit approval. The project has no authority to approve or reject real loans.
