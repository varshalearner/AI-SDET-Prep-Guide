# fico-interview-prep

Senior SDET/QA interview prep for a FICO Score sign-off role.
Uses Claude Code as the study environment.

## File conventions
- Study modules: `NN-topic-name.md` (e.g. `02-claude-md.md`)
- Hands-on labs: `NN-N-test/<lab-name>/` (self-contained repo inside)
- All data in labs: **synthetic only** — no real account numbers, scores, SSNs, or client identifiers

## Language rule
- Explanations: Hinglish (Hindi + English)
- Code, commands, model answers, table content: English only

## Lab commands (signoff-lab)
- Activate venv (Windows): `.venv\Scripts\Activate.ps1`
- Run tests: `python -m pytest -q`
- Single test: `pytest tests/<file>.py::<test_name> -q`

## Writing rules for study modules
- Each module must have: concept, Hinglish analogy, deep dive, real-world example, QA perspective, lab, common mistakes, interview Q&A, quick revision, quiz
- Model answers: ~60–90 sec spoken length
- Quote spec sections by rule number, not paraphrase

## Never do
- Never include real FICO client data, real account refs, real SSNs, or real scores
- Never weaken quiz answers to seem easier — the bar is senior-level
- Never leave `data/raw/` readable from lab agents (deny rule must be in lab's settings.json)
- Never commit `.env` or credentials
