# Screening governance and review

## Implemented scope
The original policy version and snapshot stay attached to an immutable application-level evaluation. A separate proposal records original/proposed screening outcomes, proposer label and rationale. A different reviewer label can accept or reject the proposal exactly once. Acceptance records a review disposition; it neither rewrites the screening nor approves financing. SQLite stores proposal and resolution events, with a serialized resolution transaction to prevent competing reviewers from resolving the same pending item twice.

Run the original local server, evaluate a fictional scenario, and use **Fictional screening review**. Propose a different disposition, attempt self-review, then resolve with a different label. Export review evidence to see the original evaluation and both events. The Streamlit public adapter remains a screening demo; these SQLite review controls run in the local HTTP workspace.

## API contracts

| Endpoint | Request | Result |
| --- | --- | --- |
| POST /api/evaluations/{id}/reviews | proposer, rationale, proposed_outcome (eligible/review/decline, different from original) | 201 pending proposal |
| POST /api/reviews/{id}/resolve | reviewer, rationale, decision (accepted/rejected) | 201 resolved proposal |
| GET /api/evaluations/{id}/reviews | none | Ordered pending/resolution event snapshots |

Invalid fields, blank rationale, self-review and repeat resolution return 422. Missing evaluation/proposal returns 404. Existing JSON size, content type and cross-origin controls apply. See [OpenAPI](openapi.json).

## Authority and limitations
The labels illustrate maker/checker separation; they are supplied by the caller and are **not authenticated identities**. A caller can impersonate a reviewer by changing a label. The loopback-only app has no role enforcement, tamper-proof ledger, formal policy administration or lending authority. SQLite events are append-only through the application, but a database owner can alter them. Multiple independent proposals can coexist; the prototype does not collapse them into an authoritative final lending decision.

A production design would derive identity from authentication, authorize reviewers, prevent conflicted reviewers, control policy releases with approved versions/effective dates, and store durable audit evidence. These are design requirements, not implemented claims.

## Policy lifecycle design
Current rules are fixed in code as demo-cre-1.0. Proposed lifecycle: author a new version → compare changed thresholds and affected cases → independent policy review → effective-date release → keep historical evaluations with their original snapshot. Re-evaluation creates a new record; it must never overwrite the old result. Policy administration and effective-date routing are deferred.

## Executed evidence
Updated standard-library suite: 25 checks passed, including review API round trip, self-review/re-resolution rejection, preservation of original evaluation and policy, invalid proposals, and competing resolution tests. Reviewer labels and test data are fictional. Browser verification is documented in the verification record.
