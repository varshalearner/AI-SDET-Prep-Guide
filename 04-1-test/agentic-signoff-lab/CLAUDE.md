# agentic-signoff-lab
Synthetic score-delivery sign-off lab (personal learning project). Python 3.10+, pytest, requests.
Always start Claude Code from an activated venv so `python` resolves on macOS and Windows.

## Commands
- Mock API: `python mock_api.py` (port 8099, has one PLANTED BUG on purpose)
- Tests: `python -m pytest tests/api -q --junitxml=reports/junit.xml`
- Parse results: `python scripts/parse_junit.py reports/junit.xml`
- Sign-off (deterministic part): `python scripts/run_signoff.py DLV-0001`
- Hook self-test: `python scripts/check_hooks.py`

## Layout
- `tests/api/` real suite · `exercises/` review exercises (not part of sign-off)
- `deliveries/<id>/` synthetic deliveries · `runs/` sign-off runs (generated)
- `logs/` synthetic Jenkins / K8s / git evidence for triage practice

## Rules
- Synthetic data only (CLI-0001, CON-0001). Mask identifiers in any output.
- Classify failures (product defect / test bug / environment / data / flaky / unknown) with evidence before editing any test.
- Never weaken an assertion or threshold to get green. Never edit mock_api.py unless asked.
- Never approve a sign-off; only a human runs scripts/approve.py.
- Never read `data/raw/`. Never run commands against hosts in `.claude/hooks/prod_hosts.txt`.
