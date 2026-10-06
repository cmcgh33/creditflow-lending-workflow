"""Pure deterministic evaluation. Decimal ratios are compared before display rounding."""
from decimal import Decimal, InvalidOperation

VERSION = "demo-cre-1.0"
POLICY = {
    "version": VERSION,
    "name": "Fictional CRE screening policy",
    "rules": [
        {"id": "DSCR", "metric": "dscr", "review_below": "1.25", "decline_below": "1.00", "label": "Cash-flow coverage"},
        {"id": "LTV", "metric": "ltv", "review_above": "75", "decline_above": "85", "label": "Collateral leverage"},
        {"id": "DY", "metric": "debt_yield", "review_below": "8", "decline_below": "6", "label": "Debt yield"},
    ],
    "precedence": ["decline", "review", "eligible"],
}
FIELDS = {"loan_amount": ("1", "1000000000"), "property_value": ("1", "1000000000"),
          "noi": ("0", "1000000000"), "annual_debt_service": ("1", "1000000000")}
PROPERTIES = {"Industrial", "Office", "Retail", "Multifamily"}

class ValidationError(ValueError):
    def __init__(self, errors):
        self.errors = errors
        super().__init__("Invalid application")

def validate(payload):
    errors, data = {}, {}
    if not isinstance(payload, dict):
        raise ValidationError({"application": "Provide a JSON object."})
    unknown = set(payload) - set(FIELDS) - {"borrower", "property_type"}
    if unknown:
        errors["application"] = "Unknown fields: " + ", ".join(sorted(unknown))
    for field, (low, high) in FIELDS.items():
        value = payload.get(field)
        try:
            if isinstance(value, (bool, list, dict)) or value is None or len(str(value)) > 30:
                raise ValueError
            number = Decimal(str(value))
            if not number.is_finite() or not Decimal(low) <= number <= Decimal(high):
                raise ValueError
            if number != number.quantize(Decimal("0.01")):
                raise ValueError
            data[field] = number
        except (InvalidOperation, ValueError):
            errors[field] = f"Enter a dollar amount from {low} to {high}, with at most 2 decimal places."
    borrower = payload.get("borrower")
    if not isinstance(borrower, str) or not 1 <= len(borrower.strip()) <= 80 or any(ord(c) < 32 for c in borrower):
        errors["borrower"] = "Enter a fictional borrower name (1–80 characters)."
    else:
        data["borrower"] = borrower.strip()
    if not isinstance(payload.get("property_type"), str) or payload["property_type"] not in PROPERTIES:
        errors["property_type"] = "Choose Industrial, Office, Retail, or Multifamily."
    else:
        data["property_type"] = payload["property_type"]
    if errors:
        raise ValidationError(errors)
    return data

def evaluate(payload):
    data = validate(payload)
    metrics = {"dscr": data["noi"] / data["annual_debt_service"],
               "ltv": data["loan_amount"] / data["property_value"] * 100,
               "debt_yield": data["noi"] / data["loan_amount"] * 100}
    results = []
    for rule in POLICY["rules"]:
        value = metrics[rule["metric"]]
        direction = "below" if "review_below" in rule else "above"
        review, decline = Decimal(rule[f"review_{direction}"]), Decimal(rule[f"decline_{direction}"])
        fails = (lambda threshold: value < threshold) if direction == "below" else (lambda threshold: value > threshold)
        status = "decline" if fails(decline) else "review" if fails(review) else "pass"
        unit = "×" if rule["metric"] == "dscr" else "%"
        operator = "≥" if direction == "below" else "≤"
        results.append({"id": rule["id"], "label": rule["label"], "metric": rule["metric"],
                        "value": float(value), "comparison_value": str(value), "status": status,
                        "target": f"{operator} {review}{unit}",
                        "explanation": f"{rule['label']}: {value:.2f}{unit}. Eligible target {operator} {review}{unit}; decline when {direction} {decline}{unit}."})
    status = "decline" if any(r["status"] == "decline" for r in results) else "review" if any(r["status"] == "review" for r in results) else "eligible"
    summaries = {"eligible": "All three screening rules pass. Proceed to fictional underwriting.",
                 "review": "At least one rule needs analyst review. No decline rule triggered.",
                 "decline": "At least one decline rule triggered. This fictional scenario does not pass screening."}
    return {"policy_version": VERSION, "outcome": status, "summary": summaries[status],
            "metrics": {k: float(v) for k, v in metrics.items()}, "rules": results,
            "application": {k: format(v, "f") if isinstance(v, Decimal) else v for k, v in data.items()},
            "policy_snapshot": POLICY}
