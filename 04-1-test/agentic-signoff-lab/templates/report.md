# QA Sign-off — Synthetic Score Request API v1.0.0
**Verdict:** NO-GO  **Date:** 2026-10-21
**Results:** 10/11 passed · 1 failed · 0 errors · 0 skipped · 0.4s

## Blocking issues
| Test | Class | Evidence (masked) |
|---|---|---|
| test_score_requests_invalid_product_returns_400 | Product defect | Spec enum is [SCORE_8, SCORE_10]; server returned 201 for an unknown product |

## Risks / gaps
- No auth defined in spec; auth not tested.

## Next actions
- API owner — reject products outside enum with 400; QA re-runs suite.
