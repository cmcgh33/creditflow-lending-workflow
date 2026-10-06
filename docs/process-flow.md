# CreditFlow process and decision design

A swimlane view of who acts, what the system checks, and how the fictional screening outcome is explained.

![CreditFlow colored analyst and system swimlane process](diagrams/creditflow-process.svg)

[Full-size SVG](diagrams/creditflow-process.svg) · [PNG](diagrams/creditflow-process.png) · [Editable diagrams.net file](diagrams/creditflow-process.drawio) · [Mermaid source](diagrams/creditflow-process.mmd)

## How to read the flow

| Lane / color | Meaning |
| --- | --- |
| Analyst / teal | Enter fictional inputs, review reasons, inspect history, export evidence |
| System / violet | Validate inputs, calculate ratios, evaluate all rules, record a snapshot |
| Diamonds / slate | Validation or routing questions with explicit Yes/No paths |
| Amber | Input correction or review outcome, distinguished by text |
| Pink | Screening decline |
| Green | Eligible for fictional underwriting |

## Decision logic

1. Validate every required field. Invalid input returns field errors and creates no record.
2. Calculate DSCR, LTV, and debt yield using Decimal arithmetic before display rounding.
3. Evaluate **all three rules**, then apply **decline > review > eligible** precedence. The gateways visualize that precedence; they are not an early-exit implementation.
4. Record the normalized inputs, ratios, individual rule statuses/reasons, policy version and snapshot, UUID, and UTC timestamp.
5. Explain the saved outcome and the suggested next step. The analyst can inspect previous evaluations or export the evidence as JSON.

The local HTTP app commits to SQLite before returning a successful response. The public Streamlit demo keeps records in isolated browser-session history; reloads/session termination can clear them. These paths share the same evaluation engine but use different storage.

The next-step labels communicate the screening result. There is no actual task assignment, authenticated override approval, or downstream underwriting integration in this MVP. A separate local [review demonstration](governance.md) records proposed screening dispositions using caller-supplied labels. Eligible does not mean loan approved.

## Requirements and implementation mapping

| Flow step | Requirement | Implementation / evidence |
| --- | --- | --- |
| Intake and error correction | CF-01 | `engine.validate`; API invalid-not-saved test; hosted adapter validation check |
| Ratio calculation | CF-02 | `engine.evaluate`; ratio and boundary tests |
| Complete evaluation and routing | CF-03 / CF-04 | All-rule evaluation, precedence checks, explanations, three sample scenarios |
| Evidence snapshot | CF-05 | SQLite record or Streamlit session record; policy snapshot and UUID |
| Inspect/export | CF-06 | Saved record inspection and JSON download |

See the [case study](case-study.md), [rule specification](business-rules.md), and [verification record](verification.md) for exact requirements, boundaries, and observed checks.

## Edit the diagram

Open `creditflow-process.drawio` in diagrams.net (File → Open from → Device) to edit nodes, labels, and connectors. It is an editable file, not a flattened image. This is a diagrams.net asset, not a native Lucidchart document.

The SVG and drawio versions are generated from the same node/connector definitions in `diagrams/build_flow.py`:

```bash
python docs/diagrams/build_flow.py
```

If editing the drawio file directly, export an updated SVG/PNG and keep the Mermaid source aligned. PNG is an image export of the SVG. The generator does not rasterize PNG.
