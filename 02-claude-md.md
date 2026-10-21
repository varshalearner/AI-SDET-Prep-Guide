# 02 — CLAUDE.md Files

> FICO Score QA sign-off role — senior interview prep (personal lab framing for Claude Code)
> Explanation: Hinglish · Code / commands / model answers: English · All data synthetic

**30-minute study plan:** 0–8 min → Sections 1–3 · 8–15 min → 4–7 (lab sirf padhna, baad mein chalana) · 15–25 min → 8–10 (answers bol ke practice) · 25–30 min → 11 + quiz

---

## 1) Concept

**CLAUDE.md** ek markdown file hai jo Claude Code har session ke start mein **automatically apne context mein load** karta hai. Ye project ki "standing instructions" hai: build/test commands, conventions, rules, aur 'never do' list.

Ye ek **instruction** hai, **enforcement** nahi. Claude ise padhta hai aur follow karne ki koshish karta hai, lekin koi guarantee nahi hoti.

---

## 2) Hinglish Explanation (analogy)

Socho ek naya contractor har subah tumhari team mein aata hai aur **use kal ka kuch yaad nahi rehta**. Tum har subah use 1 page ka "site briefing sheet" pakda dete ho: test aise chalate hain, ye folders touch nahi karne, assertions aise likhte hain, client data kabhi print nahi karna.

- **CLAUDE.md = woh briefing sheet.** Agar sheet 40 pages ki hogi toh contractor skim karega aur important rule miss karega. Isliye file chhoti aur precise honi chahiye.
- Sheet par "achha kaam karna" likhne ka koi fayda nahi. "`pytest -m smoke` se pehle `make env-up` chalao" likhna kaam ka hai.
- Sheet ek **guideline** hai, taala nahi. Asli taala (jaise prod DB credentials tak access hi na hona) alag cheez hai, jo Claude Code mein **permissions aur hooks** se lagta hai.

---

## 3) Deep Dive

### 3.1 Hierarchy (broad → specific)

| Level | Location | Kiske liye | Git mein? |
|---|---|---|---|
| Enterprise / managed | macOS: `/Library/Application Support/ClaudeCode/CLAUDE.md` · Linux: `/etc/claude-code/CLAUDE.md` · Windows: `C:\ProgramData\ClaudeCode\CLAUDE.md` | Org-wide policy (security, data rules) | IT manage karta hai |
| User | `~/.claude/CLAUDE.md` (Windows: `C:\Users\<you>\.claude\CLAUDE.md`) | Tumhari personal preferences, sab projects mein | Nahi |
| Project | `./CLAUDE.md` ya `./.claude/CLAUDE.md` | Team ke shared rules | **Haan** |
| Modular rules | `.claude/rules/*.md` | Topic- ya path-wise rules | Haan |
| Subfolder | e.g. `services/scoring/CLAUDE.md` | Us folder ke specific rules | Haan |
| Local | `CLAUDE.local.md` | Personal, sirf is project ke liye | Gitignored |

### 3.2 Loading kaise hota hai

- Claude Code **current working directory se upar** root `/` tak (root ko chhod ke) jaata hai aur raste mein jo bhi `CLAUDE.md` / `CLAUDE.local.md` mile, sab padhta hai.
  - Example: `foo/bar/` mein Claude chalaya → `foo/CLAUDE.md` aur `foo/bar/CLAUDE.md` dono load.
- **Subdirectory** ki CLAUDE.md files **on demand** load hoti hain, jab Claude un folders mein kaam karta hai. Context tabhi bharta hai jab zaroorat ho.
- **Imports:** `@docs/test-conventions.md` likhoge toh woh file pull ho jaayegi.
  - Max **5 levels** tak nesting.
  - Bahar ke paths se pehli baar import par **approval dialog** aata hai.
  - Markdown **code spans / code blocks ke andar** imports evaluate nahi hote (jaise `` `@anthropic-ai/claude-code` `` import nahi hai).
  - Home path bhi chalta hai: `@~/.claude/my-project-prefs.md`.
- `CLAUDE.local.md` ko docs mein imports ke favour mein deprecated bataya gaya hai (imports multiple git worktrees ke saath behtar kaam karte hain). Versions badalte rehte hain — apne setup mein `/memory` chala ke verify karna.
- **Commands:**
  - `/init` → codebase scan karke starter CLAUDE.md banata hai.
  - `/memory` → loaded memory files dikhata hai aur editor mein kholta hai.

### 3.3 Senior nuances

1. **Context budget.** CLAUDE.md har turn ke context mein baithta hai. Har line baaki lines ke saath attention ke liye compete karti hai. 300-line file mein critical rule dilute ho jaata hai. Rule of thumb: root file ~100 lines ke andar; details imports ya `rules/` mein.
2. **Guidance vs enforcement.** "Never run against prod" = soft control. Hard control = `settings.json` mein deny permissions, pre-tool hooks, aur environment mein prod credentials ka na hona.
   Interview line: *"CLAUDE.md shapes behaviour; permissions and hooks guarantee it."*
3. **Specific > generic.** "Write good tests" ka koi asar nahi. Likho: "Assert on status code AND response body schema AND a business field; `assert response.ok` alone is forbidden."
4. **Conflicts.** Generally zyada specific file jeetti hai, lekin contradictory rules model ko confuse karte hain. Conflict ko design bug maano — resolve karo, rely mat karo.
5. **10x scale.** 10 teams + 1 monorepo: root CLAUDE.md mein sirf universal rules (data masking, commit rules). Har service ki CLAUDE.md apne subfolder mein. Shared standards ek jagah se import. Iske bina rules drift/duplicate hote hain, aur ek galat line 10 teams ka output bigaad deti hai → CODEOWNERS + PR review.

### 3.4 Kya likhna chahiye vs kya nahi

| Likho ✅ | Mat likho ❌ |
|---|---|
| Exact build / test / lint commands (single test bhi) | Secrets, tokens, passwords |
| Folder map (2–5 lines) | Real client data |
| Test-writing rules (AAA, naming, negative cases) | Lambi architecture history (import karo) |
| Assertion standards | Stale / purane commands |
| Flaky-test policy | Linter jo already enforce karta hai |
| Failure triage rule (product defect vs test bug vs env) | Vague lines: "be careful", "write good code" |
| Data-masking rules | Personal preferences (team file mein) |
| 'Never do' list | "Make sure tests pass" type lines |
| Sign-off report format (ya uska import) | |

---

## 4) Real-world Example (FICO Score delivery style, synthetic)

Repo: `score-delivery-signoff/` — har score delivery (batch file + API) ko client tak jaane se pehle validate karta hai.

```
score-delivery-signoff/
├── CLAUDE.md                 # universal: commands, masking, report location
├── .claude/rules/
│   ├── region-us.md          # region-specific delivery rules
│   └── region-xx.md          # naya region = sirf nayi file
├── docs/signoff-template.md  # imported from root CLAUDE.md
└── suites/
    ├── api/CLAUDE.md         # schema, score range 300–850, reason codes present
    ├── batch/CLAUDE.md       # record counts, file layout, checksum rules
    └── perf/CLAUDE.md        # k6 thresholds; never change thresholds to pass
```

- Root `CLAUDE.md`: commands, masking rule ("never print full SSN/account IDs; use `mask()` helper"), "sign-off reports go to `reports/` using `@docs/signoff-template.md`".
- `suites/api/CLAUDE.md`: API assertion standards.
- `suites/perf/CLAUDE.md`: k6 thresholds + "never change thresholds to make a test pass".
- Naya region add hua → sirf `rules/region-xx.md`. Core file untouched.

---

## 5) QA/SDET Perspective

- CLAUDE.md asal mein AI ko diya gaya **test-quality policy document** hai. Weak assertions aur false passes AI-generated tests ki sabse common problem hai; CLAUDE.md pehla control hai.
- Ise bhi artifact ki tarah **test** karo: same task CLAUDE.md ke saath aur bina chalao, output checklist par score karo.
- **Product defect vs test bug** rule yahan likho: "If a test fails, first reproduce manually with curl; do not edit assertions until you've classified the failure."
- Data discipline: shared output mein masking by default, synthetic fixtures only, `data/client/` off-limits.

---

## 6) Hands-on Lab (personal lab, ~15 min)

### Step 1 — Repo setup

**macOS (first):**
```bash
mkdir score-api-tests && cd score-api-tests && git init
mkdir -p tests/api tests/fixtures docs
python3 -m venv .venv && source .venv/bin/activate
pip install pytest requests jsonschema
pip freeze > requirements.txt
```

**Windows (PowerShell):**
```powershell
mkdir score-api-tests; cd score-api-tests; git init
mkdir tests\api, tests\fixtures, docs
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install pytest requests jsonschema
pip freeze > requirements.txt
```

### Step 2 — Production-quality `CLAUDE.md`

```markdown
# score-api-tests

API test suite for a (synthetic) Score API. Python 3.11, pytest, requests.

## Commands
- Install: `pip install -r requirements.txt`
- Smoke: `pytest -m smoke -q`
- Full: `pytest -q --maxfail=5`
- Single test: `pytest tests/api/test_scores.py::test_name -q`

## Layout
- `tests/api/` – one file per endpoint
- `tests/fixtures/` – SYNTHETIC data only
- `docs/` – sign-off template: @docs/signoff-template.md

## Test-writing rules
- Every test: Arrange / Act / Assert, one behaviour per test.
- Name: `test_<endpoint>_<condition>_<expected>`.
- Mark fast critical-path tests `@pytest.mark.smoke`.
- Each new endpoint test needs at least one negative case (4xx).

## Assertion standards
- Always assert: status code, response schema (jsonschema), and at least one business rule
  (e.g. score is int in 300..850, reason_codes non-empty list).
- FORBIDDEN as the only assertion: `assert resp.ok`, `assert resp.json()`, `assert True`.
- No try/except that swallows assertion errors. No `pytest.skip` without a linked ticket.

## Flaky tests
- Never add retries or sleeps to make a test pass. Quarantine with `@pytest.mark.flaky_quarantine`
  and a reason; report it.

## Failures
- Before editing a failing test, classify it: product defect / test bug / env issue. Show evidence.

## Data rules
- Never print or log full IDs, SSNs, account numbers, tokens. Use `mask()` -> `XXXX1234`.
- Never read from `data/client/`. Never hit hosts other than `$SCORE_API_BASE_URL`.

## Never do
- Never weaken an assertion or threshold to get green.
- Never commit `.env` or credentials.
```

### Step 3 — Bura version (`CLAUDE.bad.md`, sirf comparison ke liye)

```markdown
# Project
This is a very important project for our company. Please write high quality code
and good tests. Be careful with data. Our architecture is microservices based and
we have been building it since 2019 with many teams... [80 more lines of history]
Run tests with the usual commands. Make sure tests pass.
API key for dev: sk-dev-XXXXXXXX
```

**Bad version mein kya galat hai:**
- Vague ("good tests", "be careful") — measurable nahi.
- Koi exact command nahi ("usual commands").
- History ka noise context kha raha hai.
- "Make sure tests pass" → assertions weaken karne ko encourage karta hai.
- **Secret commit ho gaya** (git history mein hamesha rahega).

### Step 4 — Run & compare

1. Claude Code start karo, `/memory` chalao.
   **Expected:** project `CLAUDE.md` list mein dikhegi.
2. Prompt: *"Write tests for GET /v1/scores/{id}. Return schema: {id, score, reason_codes}."*
3. Output ko checklist par score karo:

| Check | Good CLAUDE.md | Bad CLAUDE.md (expected) |
|---|---|---|
| Schema assert hua? | Haan | Aksar nahi |
| Score range 300–850 check? | Haan | Mostly nahi |
| Negative 4xx case? | Haan | Aksar nahi |
| `assert resp.ok` akela? | Nahi | Mil sakta hai |
| ID masked in logs? | Haan | Nahi |
| Naming convention | Follows | Random |

4. Bad file ko `CLAUDE.md` bana ke same prompt dobara do, fark note karo. **Yahi tumhara interview demo story hai.**

---

## 7) Common Mistakes & Anti-patterns

1. Bahut lambi file — critical rules dab jaate hain.
2. Vague instructions ("be careful") — koi measurable asar nahi.
3. "Make tests pass" — false passes ka nuskha. Iski jagah: "never weaken assertions."
4. Secrets ya real client data CLAUDE.md mein (file git mein jaati hai).
5. Stale commands — script rename hua, CLAUDE.md nahi badli → Claude galat command chalayega.
6. CLAUDE.md ko security control maan lena, bina permissions/hooks ke.
7. Linter ka kaam CLAUDE.md se karwana (formatting). Tooling use karo.
8. Personal preferences team file mein — user-level ya local file mein jaani chahiye.
9. Kabhi measure na karna ki file kaam kar rahi hai.
10. Contradictory rules alag-alag levels par.

---

## 8) Interview Questions (60–90 sec model answers)

### Q1. What is CLAUDE.md and why does it exist?
"CLAUDE.md is a markdown file Claude Code loads into context at the start of every session. It exists because each session starts without memory of the project, so without it you'd re-explain commands, conventions and constraints every time. I treat it as the project's standing brief: exact build and test commands, layout, test-writing and assertion standards, data rules, and a never-do list. The key point is that it's guidance, not enforcement. It shapes behaviour, but anything that must never happen, like touching production or leaking data, also needs permissions, hooks and environment-level controls."

### Q2. Explain the hierarchy.
"There's managed or enterprise policy for org-wide rules, user-level in `~/.claude/CLAUDE.md` for my personal preferences, project-level `./CLAUDE.md` committed to git for team rules, `.claude/rules/` for modular topic or path rules, and subfolder CLAUDE.md files that load on demand when Claude works in that area. Claude walks up from the working directory and loads files it finds. Imports with `@path` let me keep the main file short and pull detailed docs in. My design principle is: broad and universal at the top, specific near the code, and no contradictions between levels."

### Q3. What do you put in it for a test repository?
"Exact commands, including how to run a single test and the smoke set. A short layout map. Test-writing rules like AAA, naming, and a mandatory negative case. Assertion standards: status plus schema plus a business rule, and `assert resp.ok` alone is forbidden. A flaky policy: quarantine, never add retries or sleeps. A failure-triage rule: classify as product defect, test bug or env issue before editing. Data masking by default. And a never-do list, mainly 'never weaken an assertion or threshold to get green'."

### Q4. What should NOT go in it?
"Secrets, real client data, long architecture history, things a linter already enforces, and vague aspirations like 'write good code'. Secrets are the worst because the file is committed. History and long docs waste context and dilute the rules that matter, so I move them into imported docs. Vague lines are useless because you can't verify whether they were followed."

### Q5. Why keep it short?
"Because it sits in context every turn and every line competes for attention. In a 400-line file, the one rule that prevents false passes gets diluted. Short also means maintainable: people actually read and update it in reviews. I aim for roughly a page in the root file, and put depth in imports or subfolder files so it loads only when relevant."

### Q6. How do you know your CLAUDE.md is actually working?
"I treat it like any test artifact. First, confirm it's loaded using `/memory`. Then I run a fixed set of representative tasks, like 'write tests for this endpoint' or 'triage this failure', and score outputs against a checklist derived from the file's rules: schema asserted, negative case present, no weak-only assertion, IDs masked. I compare with and without the file, or old versus new version. Ongoing, I track recurring corrections in PR reviews. If reviewers keep fixing the same issue, either the rule is missing, unclear, or buried."

### Q7. How do you maintain it as a team artifact?
"It lives in git and changes through PRs like code, with CODEOWNERS on it so the QA lead reviews rule changes. When a script or command changes, the CLAUDE.md update goes in the same PR. When reviewers repeatedly correct an AI mistake, that becomes a candidate rule. I also prune: a rule nobody needs anymore is noise. Personal preferences stay out of it and go in user-level or local files."

### Q8. CLAUDE.md vs skills vs hooks?
"CLAUDE.md is always-on context: rules and conventions for every task. A skill is a packaged, on-demand workflow, like 'run sign-off for delivery X and produce the report', with its own instructions and scripts, loaded when relevant. Hooks are deterministic code that runs on events, like blocking a command or running a check after edits. So: CLAUDE.md for 'how we work', skills for 'how to do this specific job end to end', hooks and permissions for 'this must always or never happen'."

### Q9. Claude ignored a rule in CLAUDE.md. What do you do?
"First, check it was loaded: right file, right directory, `/memory`. Then check if the rule is specific and testable, or vague. Check for conflicts with another level or an import. Check if it's buried in a long file. Then rewrite it to be concrete, ideally with a do/don't example, and re-run the same task to verify. If the rule is critical, like data or prod access, I don't rely on wording at all. I add a permission deny or a hook."

### Q10. How does CLAUDE.md help with AI-generated test quality?
"The biggest risk with generated tests is that they pass without validating intended behaviour: asserting only status 200, mocking the thing under test, or catching exceptions. CLAUDE.md encodes the assertion bar up front and the never-weaken rule. But I still review generated tests critically. I do mutation-style checks: break the expected behaviour and confirm the test fails. A test that can't fail is not a test."

### Q11. How would you structure it in a monorepo with many teams at 10x scale?
"Root file holds only universal rules: data masking, commit rules, and how to find per-service commands. Each service has its own CLAUDE.md near its code, loaded on demand. Shared standards like assertion rules live in one doc imported everywhere, so there's a single source of truth. Ownership is set through CODEOWNERS. Then I add a periodic eval run across services to catch drift."

### Q12. How do you handle data masking via CLAUDE.md?
"I state it as a default, not an exception: never print full identifiers or tokens, use the `mask()` helper, fixtures are synthetic only, and certain paths are off-limits. But since it's a regulated domain, I back it with controls: deny read access to client data paths, keep real data out of the environment, and scan outputs and reports for unmasked patterns before anything is shared."

---

## 9) Cross-question Chains

### Chain A — "Is CLAUDE.md enough?"
1. **Q:** What's in your CLAUDE.md?
   **A:** Commands, assertion standards, data rules, never-do list.
2. **Q:** So data leakage is solved?
   **A:** No. That line is guidance. Enforcement comes from permissions, hooks, and the environment not containing real data.
3. **Q:** Which hook would you write?
   **A:** A pre-tool hook that blocks reads of `data/client/**` and bash commands that hit non-allowlisted hosts, plus a post-step check that regex-scans reports for unmasked IDs.
4. **Q:** What if the scan has false negatives?
   **A:** Defence in depth: synthetic-only fixtures mean there's nothing real to leak. The scan is a backstop, and I'd test it with seeded fake-PII samples.
5. **Q:** How do you prove all this to an auditor?
   **A:** CLAUDE.md, settings and hooks are versioned in git with PR history, scan logs are attached to each sign-off report, and the seeded-PII test runs in CI.

### Chain B — "Generated test passed. Done?"
1. **Q:** Claude wrote 20 tests, all green. Ship it?
   **A:** No. Green is not validation. I review what they assert.
2. **Q:** How do you review fast?
   **A:** Grep for weak patterns (`assert resp.ok`, bare `except`, `skip`), check every test has a business assertion, and run a quick mutation: break expected behaviour and confirm failures.
3. **Q:** Some still pass after the mutation. Why?
   **A:** Over-mocking, asserting on the mock, or asserting against values the test computed from the same buggy code.
4. **Q:** How do you stop it next time?
   **A:** Add a concrete rule with an example to CLAUDE.md, and add a lint/CI check for the forbidden patterns.
5. **Q:** How do you measure improvement?
   **A:** Before/after rate of weak-assertion findings per PR, and mutation score on the suite.

### Chain C — "Scale and drift"
1. **Q:** Who owns CLAUDE.md?
   **A:** The team, via git and CODEOWNERS.
2. **Q:** A dev renames `make test` to `make check`. What happens?
   **A:** Claude runs a stale command and fails or worse. So command changes and CLAUDE.md updates go in the same PR.
3. **Q:** How do you catch drift automatically?
   **A:** A CI job that executes the commands listed in CLAUDE.md.
4. **Q:** The file grew to 500 lines. Now what?
   **A:** Audit it, delete dead rules, move domain detail into imports or subfolder files, keep the root to universal rules.
5. **Q:** How do you know you didn't remove something important?
   **A:** Re-run the eval task set before and after the change and compare checklist scores.

---

## 10) Resume-linked Questions (sirf real claims — STAR skeleton)

> Claude Code ko hamesha **personal lab / learning** ki tarah frame karna.

### R1. "Your AI regression analyzer is used by IAM and Core teams. How would CLAUDE.md fit into something like that?"
- **S:** Regression failures across Jenkins, repos and K8s events took long to triage.
- **T:** Build an analyzer that correlates the signals and auto-files Jira defects.
- **A:** Describe what you built. Bridge: "The same lesson applies to CLAUDE.md: the tool is only as good as the rules you give it — how to classify product defect vs test bug, what evidence goes in a ticket, and masking."
- **R:** Used by two teams. Lesson: precise, testable instructions plus human review of output.

### R2. "You maintain ~2,000 Rest Assured tests. What assertion standards would you encode?"
- **S:** Large API suite across DMP Core services (notification, CSP, ignite).
- **T:** Keep tests meaningful at scale.
- **A:** Status + schema + business-field assertions, negative cases, no swallow-catches. "These are exactly the rules I'd put in a CLAUDE.md so AI-written tests meet the same bar."
- **R:** Smoke on every merge and regression before promotion caught issues early.

### R3. "Metering suite from scratch. How would you onboard an AI agent to it?"
- **S:** 6 services, ~250 functional/resiliency/performance/longevity tests, pytest + Cypress BDD, Athena SQL validation over S3.
- **T:** Make it easy to extend correctly.
- **A:** CLAUDE.md with exact pytest/Cypress commands, folder map, rule "validate aggregation with the Athena query, never with hardcoded totals", and masking of client IDs in outputs.
- **R:** In a personal lab version, compare generated tests with and without the file.

---

## 11) Quick Revision (10 lines)

1. CLAUDE.md = session-start context with standing project instructions. Guidance, not enforcement.
2. Hierarchy: managed → user `~/.claude/CLAUDE.md` → project `./CLAUDE.md` → `.claude/rules/` → subfolder (on demand) → local.
3. Claude walks up from cwd to load files; subfolder files load when you work there.
4. `@path` imports, nested up to 5 levels, ignored inside code spans/blocks.
5. Write: exact commands, layout, test rules, assertion bar, flaky policy, triage rule, masking, never-do.
6. Don't write: secrets, client data, history essays, linter rules, vague lines.
7. Keep it short — every line competes for attention.
8. Critical rules also need permissions and hooks.
9. Treat it as team code: git, PRs, CODEOWNERS, update commands in the same PR.
10. Verify: `/memory`, fixed eval task set + checklist, before/after comparison, recurring PR corrections.

---

## Quiz (in progress)

**Q1 of 8:** Tumhare team ke CLAUDE.md mein likha hai "Never print full account numbers." Phir bhi ek generated sign-off report mein ek full (synthetic) account number aa gaya. Step by step batao tum kya karogi, aur long term mein ise kaise rokogi?

_Your answer:_

_Score / feedback:_

---

**Sources:**
- [Claude Code memory docs](https://docs.claude.com/en/docs/claude-code/memory)
- [Memory guide (claude.nagdy.me)](https://claude.nagdy.me/learn/memory)
