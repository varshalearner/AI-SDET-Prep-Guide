# agentic-signoff-lab

Lab repo for the notes in `04-08-agents-hooks-workflows-tests-triage.md`. Personal learning project. **All data is synthetic.**
`mock_api.py` has **one planted bug on purpose**: an unknown `product` returns 201 instead of 400.

Har topic ke steps neeche hain. Commands pehle **macOS**, phir **Windows (PowerShell)**.

---

## 0) One-time setup

**macOS**
```bash
cd agentic-signoff-lab
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/install_config.py      # _config/ -> .claude/ and .github/
git init && git add . && git commit -m "lab start"
```
**Windows**
```powershell
cd agentic-signoff-lab
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/install_config.py
git init; git add .; git commit -m "lab start"
```
`install_config.py` ek baar chalana hai. Ye `_config/claude/` ko `.claude/` mein aur `_config/github/` ko `.github/` mein copy karta hai (agents, hooks, settings, skill, CI workflow). Chalane se pehle `_config/` ki files ek baar padh lena — hooks tumhari machine pe code chalate hain, isliye review zaroori hai (05 ka lesson).
Venv activate hone ke baad dono OS pe `python` chalega. Isliye saari files mein `python` likha hai, `python3` nahi.
**Claude Code hamesha activated venv wale terminal se start karna**, warna hooks ko `python` nahi milega.

Saare steps ke dauraan **Terminal 1** mein mock API chalu rakho:
```bash
python mock_api.py      # same on macOS and Windows
```

---

## 04 — Subagents

```bash
python -m pytest tests/api -q --junitxml=reports/junit.xml
```
Expected: `1 failed, 6 passed` (`test_score_requests_invalid_product_returns_400`).

```text
claude
> /agents
> Use the failure-triager subagent to triage reports/junit.xml
> Use the test-reviewer subagent to review tests/api/test_score_requests.py against specs/score-api.yaml
> /context
```
Expected: triager ise **Product defect, High** batayega. Reviewer `test_score_requests_smoke` (`< 500`) ko flag karega.

---

## 05 — Hooks & headless

**Hook self-test (Claude ke bina):**
```bash
python scripts/check_hooks.py
```
Expected: `11/11 passed`.

**Claude ke andar:**
```text
claude
> /hooks
> clean up by running rm -rf reports
```
Expected: `BLOCKED by guard_bash: recursive force delete` — Claude koi safe alternative poochega.

**Headless (macOS):**
```bash
python scripts/parse_junit.py reports/junit.xml > reports/summary.json
claude -p "Read reports/summary.json. For each failure give: test, class, one line of evidence quoted from the file. Max 10 lines. Use only data in the file." \
  --allowedTools "Read" --max-turns 3 --output-format json > reports/ai.json
jq '{is_error, num_turns, total_cost_usd}' reports/ai.json
jq -r '.result' reports/ai.json
```
**Headless (Windows):**
```powershell
python scripts\parse_junit.py reports\junit.xml > reports\summary.json
claude -p "Read reports/summary.json. For each failure give: test, class, one line of evidence quoted from the file. Max 10 lines. Use only data in the file." --allowedTools "Read" --max-turns 3 --output-format json > reports\ai.json
$r = Get-Content reports\ai.json -Raw | ConvertFrom-Json; $r.is_error; $r.num_turns; $r.result
```
Windows pe `>` redirect UTF-16 file bana sakta hai. Agar `ConvertFrom-Json` fail ho, toh `| Out-File -Encoding utf8 reports\ai.json` use karo.

**CI:** `.github/workflows/api-tests.yml` (GitHub Actions) aur `Jenkinsfile` ready hain. GitHub repo mein push karo aur `ANTHROPIC_API_KEY` secret add karo. Job **red** aana chahiye (planted bug), aur AI summary sirf advisory hai.

---

## 06 — One-command `/signoff`

```bash
python scripts/run_signoff.py DLV-0002     # NO-GO: duplicate ref + score 910 + 1 test failed
python scripts/run_signoff.py DLV-0001     # NO-GO: 1 test failed (planted bug)
python scripts/run_signoff.py DLV-0001     # reused_run -> idempotent
python scripts/run_signoff.py DLV-9999     # BLOCKED: unknown id
```
Claude ke andar:
```text
claude
> /signoff DLV-0001
```
Approval sirf human karta hai (settings.json mein Claude ke liye `approve.py` deny hai):
```bash
python scripts/approve.py runs/DLV-0001/<timestamp> --by varsha            # refused: NO-GO needs --waiver
```
**Idempotency + SUT version test:** `mock_api.py` mein planted bug fix karo. `# PLANTED BUG` wali line ke upar ye add karo:
```python
        if body["product"] not in ALLOWED_PRODUCTS:
            return self._send(400, {"error": "invalid_product", "field": "product"})
```
Phir mock API restart karo aur `python scripts/run_signoff.py DLV-0001` chalao. Expected: ek **naya** run aur verdict **GO**. Uske baad `approve.py <run> --by varsha` chalega. Agle labs ke liye bug wapas daal dena: `git checkout mock_api.py`.

Demo se pehle `runs/` folder delete kar dena, taaki fresh run dikhe.

---

## 07 — AI-written tests review

```bash
python -m pytest exercises/test_score_ai_draft.py -q
```
Expected: `6 passed, 1 skipped`. Planted bug maujood hai, phir bhi saare tests green hain — yahi false pass hai.
1. Notes mein di gayi answer key padhne **se pehle** apna review `exercises/review.md` mein likho (10 min).
2. Uske baad:
```text
claude
> Use the test-reviewer subagent to review exercises/test_score_ai_draft.py against specs/score-api.yaml
```
3. Apna review aur agent ka review compare karo, phir notes ke rubric se grade karo (ya chat mein review bhej do).

---

## 08 — Failure triage

Evidence `logs/` folder mein hai: `jenkins-build-142.log`, `k8s-events.txt`, `git-log.txt`, `test-history.txt`.
1. Pehle khud triage karo (15 min): har failure ka class, confidence, evidence aur next action.
2. Phir agent se karwao:
```text
claude
> Use the failure-triager subagent to triage the build described in logs/jenkins-build-142.log, using logs/k8s-events.txt, logs/git-log.txt and logs/test-history.txt as evidence.
```
3. Agent ko notes ke rubric se grade karo. Dhyan rakho ki red herring (`9d8c7b6`) ko usne root cause na bataya ho.

---

## File map
| Path | Topic |
|---|---|
| `_config/` → `scripts/install_config.py` | `.claude/` + `.github/` source |
| `CLAUDE.md`, `mock_api.py`, `specs/`, `scripts/parse_junit.py`, `templates/` | base (02/03) |
| `.claude/agents/failure-triager.md`, `test-reviewer.md` | 04 |
| `.claude/hooks/*`, `.claude/settings.json`, `scripts/check_hooks.py`, `.github/`, `Jenkinsfile` | 05 |
| `deliveries/`, `scripts/validate_batch.py`, `run_signoff.py`, `approve.py`, `.claude/skills/signoff/` | 06 |
| `exercises/test_score_ai_draft.py` | 07 |
| `logs/` | 08 |
