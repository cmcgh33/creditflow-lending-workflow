# Verification and UAT evidence

Executed on **2026-10-06**, Python **3.12.14**, local Linux environment.

## Completed checks

| Check | Observed result |
| --- | --- |
| `python -m unittest discover -s tests -v` | 15 test methods passed; threshold method includes 12 boundary subcases |
| Three fictional scenario outcomes in Chromium | Eligible, review, decline matched expected results |
| History inspection | Restored selected inputs/result and synchronized scenario selector |
| Evidence export | Downloaded JSON contained selected borrower, version, full policy snapshot, and unrounded comparison values |
| Pending edits | Editing inputs flagged the displayed result as a saved evaluation with unevaluated changes |
| Browser reload | Previously saved records remained available |
| Borrower containing HTML markup | Rendered as text, no injected image element |
| Responsive layout | 1440px desktop and 390px narrow viewport screenshots captured; no page-level horizontal overflow at 390px |
| Browser errors | No page/console errors during the final smoke run |
| JavaScript syntax | `node --check web/app.js` passed |
| API contract | JSON parsed and all local schema references resolved; no external OpenAPI validator run |

Screenshots: [desktop](images/workspace.png), [mobile](images/mobile.png). They are captured from the running application, using only fictional scenarios.

## Acceptance traceability

| Requirement | Evidence |
| --- | --- |
| CF-01 validated intake | `test_invalid_numeric_inputs`, `test_invalid_application`, `test_zero_noi_is_valid_decline`, `test_invalid_not_saved` |
| CF-02 ratios | `test_all_pass`, `test_thresholds` |
| CF-03 routing and boundaries | `test_precedence`, `test_thresholds`, three browser scenarios |
| CF-04 rule reasons | Browser renders all three explanations; exported rule snapshot inspected |
| CF-05 saved evidence | `test_snapshot_and_normalized_input`, `test_persistence_and_independent_evaluations`, `test_round_trip` |
| CF-06 history/export/pending edits | Browser smoke checks for inspection, selector synchronization, export, edits, reload |
| CF-07 readable responsive UI | Explicit labels/text statuses/focus styles inspected; desktop/mobile captures and overflow check |

## Repeatable checks

Core suite uses only Python's standard library and temporary databases:

```bash
python -m unittest discover -s tests -v
```

Optional browser suite requires Playwright separately. It launches a temporary server/database and regenerates screenshots:

```bash
python -m pip install playwright==1.51.0
python -m playwright install chromium
```

From the repository root:

```bash
# macOS/Linux
PYTHONPATH=. python tests/ui_smoke.py
```

Windows PowerShell:

```powershell
$env:PYTHONPATH = "."
python tests/ui_smoke.py
```

Playwright is a verification tool, not a runtime dependency. The committed CI workflow runs core tests on Python 3.11, 3.12, and 3.13; [hosted CI results are available in GitHub Actions](https://github.com/cmcgh33/creditflow-lending-workflow/actions).

## Manual owner review — still pending

These checks are proposed for Carla's review, not recorded as completed sign-off:

1. Confirm the wording and visual design fit the intended portfolio story.
2. Run all three examples on the owner's computer.
3. Enter a custom review case and explain the result back using the visible rules.
4. Inspect an older result, change a field, and confirm the pending-change label is understandable.
5. Navigate with a keyboard; assess label readability at the preferred zoom.

Not yet validated: Windows/macOS runtime, browsers other than Chromium, screen-reader behavior, load/concurrency, recovery from storage failures, and any real lending policy. There is no production deployment or real-user pilot.
