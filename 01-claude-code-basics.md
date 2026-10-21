# 01 — Claude Code Fundamentals

> FICO Score QA sign-off interview prep · Topic 01
> Status: **Part 1 of 4** (Sections 1–5). Sections 6–11 + quiz will be appended.
> Note: Claude Code changes fast. Verify exact commands/flags with `claude --help` and docs.claude.com before the interview.

---

## 1) Concept

**Claude Code** Anthropic ka *agentic coding tool* hai. Ye terminal (aur IDE, desktop app, web) mein chalta hai. Ye codebase padh sakta hai, files edit kar sakta hai, shell commands chala sakta hai (tests, git, builds), aur results dekh ke agla step khud decide karta hai. Ye sab ek **permission system** ke andar hota hai jo aap control karte ho.

Interview definition:

> Claude Code is an agent harness around a Claude model: **model + tools + an execution loop + a permission layer + context management**. The model decides *what* to do; the harness decides *whether it's allowed* and *executes* it.

## 2) Hinglish Explanation (analogy)

**Normal chatbot** ek phone consultant jaisa hai. Aap code paste karte ho, wo advice deta hai, aur copy-paste karke chalana aapka kaam hai. Usne aapka repo kabhi dekha hi nahi.

**Claude Code** ek naye, bahut tez *contract SDET* jaisa hai jise aapne apne laptop pe baitha diya hai:
- Khud `ls`, `grep` karke repo samajhta hai → **Read/Grep/Glob tools**
- Khud `pytest` chala ke failure dekhta hai → **Bash tool**
- Fix likhta hai → **Edit/Write tools**
- Fix ke baad test dobara chala ke check karta hai → **agentic loop**
- Office ke **access card** ki tarah har zone mein bina poochhe nahi ja sakta → **permission modes + allow/deny rules**. Production DB room ka card mila hi nahi → *deny*.
- **Short-term memory limited** hai, whiteboard jitni → **context window**. Bhar gaya toh poora mitao (`/clear`) ya summary likh ke baaki mitao (`/compact`).
- Office ki **"team rules" diary** jo wo roz subah padhta hai → **CLAUDE.md**.

Ek line: chatbot *batata* hai, Claude Code *karta* hai, isliye use *control* karna sabse important skill hai.

## 3) Deep Dive

### 3.1 Install & Setup

```bash
# Native installer
curl -fsSL https://claude.ai/install.sh | bash

# Or via npm (Node.js 18+)
npm install -g @anthropic-ai/claude-code

cd my-repo
claude            # interactive session, login on first run
claude doctor     # diagnose install/config issues
```

| Auth option | Kab |
|---|---|
| Claude subscription (Pro/Max/Team/Enterprise) | Individual / team daily use |
| Claude Console API key | Pay-per-token, CI pipelines |
| Amazon Bedrock / Google Vertex AI (e.g. `CLAUDE_CODE_USE_BEDROCK=1`) | Regulated enterprise: traffic company ke apne cloud account se, governance + billing wahin |

**Senior nuance:** regulated company mein pehla sawaal: *"Code/data kis endpoint pe jaa raha hai?"* Jawab: Bedrock/Vertex routing + org-managed settings (`managed-settings.json`, users override nahi kar sakte).

#### Sidebar: Bedrock/Vertex routing kya hai?

Claude model Anthropic API ke alawa **AWS Bedrock** aur **Google Vertex AI** pe bhi hosted hai. Routing = Claude Code requests kahan jaayein.
- Default: `api.anthropic.com`, Anthropic account auth/billing.
- Bedrock: company ke AWS account ke andar; AWS IAM auth, AWS bill. Vertex: same, GCP project ke through.
- Analogy: same laptop, company ke **approved vendor** se kharidna (contract, billing, audit pehle se set).

```bash
export CLAUDE_CODE_USE_BEDROCK=1; export AWS_REGION=us-east-1   # + AWS profile/SSO creds
export CLAUDE_CODE_USE_VERTEX=1; export CLOUD_ML_REGION=us-east5; export ANTHROPIC_VERTEX_PROJECT_ID=my-gcp-project
```

| Concern | Kaise help karta hai |
|---|---|
| Data governance | Existing cloud data-processing agreement; naya vendor review nahi |
| Access control | IAM roles/policies |
| Audit | CloudTrail-style logs |
| Network | VPC/PrivateLink, no public internet |
| Billing | Existing cloud bill + budgets |

Third option: **LLM gateway** (`ANTHROPIC_BASE_URL` → internal proxy) for company-side logging/budgets/filtering.
Trade-offs: new models/features kabhi late; alag model IDs; console mein model access enable karna; account-level quotas.

> **Routing ≠ permission to send sensitive data.** Masking, deny rules, data boundaries tab bhi lagte hain.

Interview line: *"In a regulated setup I'd expect Claude Code routed through the company's own cloud account, e.g. Bedrock on AWS, so usage inherits IAM, audit logging and existing data agreements. But routing only answers where traffic goes, not what data is allowed to go, so masking and data boundaries still apply."*

**First-time setup:** `/init` → starter `CLAUDE.md` banata hai. Use **review aur trim karo**, auto-generated version generic aur lamba hota hai.

### 3.2 Surfaces

| Surface | Strength | Weakness | Best for |
|---|---|---|---|
| CLI | Max control, scriptable, SSH host pe chalta hai | Terminal diff review | Daily power use, remote hosts |
| IDE extension (VS Code/JetBrains) | Visual diffs, open-file/selection context | IDE chahiye | Review-heavy work |
| Desktop / Web | Setup-free, cloud sessions, parallel tasks | Locked-down local infra tak access nahi | Exploratory / async |
| Headless (`claude -p`) | Non-interactive, JSON output, CI | No human approval → permissions pehle se tight | Jenkins / GitHub Actions |

```bash
claude -p "Run pytest, summarize failures as JSON" \
  --output-format json \
  --allowedTools "Bash(pytest:*)" "Read" "Grep" \
  --max-turns 10
```

**Decision rule:** interactive → CLI/IDE. Repeatable, unattended → headless + explicit allowlist + `--max-turns`.

### 3.3 Agentic Loop

```
User prompt
   │
   ▼
Model sees: system prompt + CLAUDE.md + tool definitions + conversation
   │
   ▼
Model emits: (a) text → turn ends, OR (b) tool_use {name: "Bash", input: "pytest tests/ -x"}
   │
   ▼
HARNESS permission check: deny → blocked | allow/mode → execute | else → ASK user
   │
   ▼
tool_result appended to context → back to model → repeat
```

Phases: **Gather context → Take action → Verify**, repeat.

**Key insight:** model khud execute nahi karta, sirf *request* karta hai. **Security boundary harness + OS hai, model ki "achhi niyat" nahi.**

**Failure modes:**
1. **Premature success**: "All tests pass ✅" bina poora suite chalaye.
2. **Goal substitution**: product ki jagah test badal diya (assertion dheela, `skip`).
3. **Rabbit-holing**: galat hypothesis pe 20 turns, context bhar gaya.
4. **Scope creep**: bug fix bola, 6 unrelated files refactor.
5. **Stale assumption**: purani padhi file ke content pe edit.

Mitigation: chhote scoped tasks, plan mode pehle, `git diff` review, verification khud chalao.

### 3.4 Built-in Tools

| Tool | Kya karta hai | Senior nuance |
|---|---|---|
| Read | File padhta hai (line numbers, images/PDF) | Badi files offset/limit se; poori file context mein mehengi |
| Edit | Exact string replacement, pehle Read zaroori | Unique old string → accidental edits kam, diff chhota |
| Write | Poori file create/overwrite | Badi existing file rewrite risky; Edit prefer karo |
| Bash | Shell commands | Sabse powerful + risky; zyada rules isi pe |
| Grep | ripgrep search | Structured output, kam tokens |
| Glob | File patterns (`**/*_test.py`) | `find` se tez, safe |
| Extra: WebFetch/WebSearch, Agent/Task (subagents), TodoWrite | Web, isolated sub-tasks, tracking | Subagent alag context mein explore karke sirf summary deta hai |

**Dedicated tools kyun?** Granular permissions, chhota structured output, aur Edit ka "pehle Read" rule blind overwrites rokta hai.

### 3.5 Permission Modes + Rules

| Mode | Behaviour | Kab |
|---|---|---|
| default | Edits/new Bash pe pehli baar poochta hai | Unfamiliar repo |
| acceptEdits | Edits auto-approve, Bash poochta hai | Trusted fast iteration |
| plan | Read-only, plan propose karta hai | Triage, high-risk, locked-down hosts |
| bypassPermissions (`--dangerously-skip-permissions`) | Kuch nahi poochta | Sirf disposable isolated sandbox |

`Shift+Tab` se cycle, ya `--permission-mode`.

**Settings precedence (upar wala jeetta hai):**
1. Enterprise managed settings
2. CLI arguments
3. `.claude/settings.local.json` (personal, gitignored)
4. `.claude/settings.json` (team, committed)
5. `~/.claude/settings.json` (user)

```json
{
  "permissions": {
    "defaultMode": "plan",
    "allow": ["Bash(pytest:*)", "Bash(git status)", "Bash(git diff:*)", "Read(./src/**)", "Read(./tests/**)"],
    "ask":   ["Bash(git commit:*)"],
    "deny":  ["Read(./.env)", "Read(./data/raw/**)", "Bash(curl:*)", "Bash(ssh:*)", "Bash(rm -rf:*)"]
  }
}
```

**Order: deny > ask > allow.**

**Senior nuances:**
- Rules = defense-in-depth, **security boundary nahi**. `Read(./data/raw/**)` deny ho par `Bash(python:*)` allow ho toh script se file padh sakta hai. Asli boundary: OS permissions, container isolation, network egress, sandboxing.
- Bash prefix rules best-effort. `Bash(*)` allow ≈ bypass mode.
- Regulated work: **allowlist > denylist**.
- Shared `settings.json` git mein commit → team-wide guardrails, reviewable.

#### Sidebar: Asli boundary (OS permissions, container, egress, sandbox)

**Problem:** rules tool call match karte hain, effect nahi.
```json
"deny":  ["Read(./data/raw/**)"], "allow": ["Bash(python:*)"]
```
```bash
python -c "print(open('data/raw/clients.csv').read())"   # Read deny bypass
```
Analogy: rules = receptionist ko instructions; peeche ki seedhi se koi bhi jaa sakta hai. Asli boundary raaste ki parwah nahi karti.

| Layer | Analogy | Kya rokta hai |
|---|---|---|
| OS permissions | Darwaze pe taala | Kisi bhi raaste se file access (kernel check) |
| Container isolation | Alag building, sirf zaroori saamaan | Baaki machine ki files dikhti hi nahi |
| Network egress | Koi courier bahar nahi | Data exfiltration |
| Sandboxing | Room jahan sirf kuch kaam allowed (kernel-enforced) | Process kya touch kare |

```bash
# 1. OS permissions
sudo useradd qa_agent
sudo chown -R datateam:datateam data/raw && sudo chmod -R 750 data/raw
# as qa_agent → PermissionError: [Errno 13] Permission denied

# 2. Container: sirf zaroori mounts
docker run --rm -it --user 1001:1001 \
  -v "$PWD/src:/work/src" -v "$PWD/tests:/work/tests" \
  -v "$PWD/data/samples:/work/data/samples:ro" qa-agent-image
```
3. Egress: allowlist proxy (sirf model API + internal mirror); model-free jobs `--network none`. Blocks curl exfil, malicious installs, prompt-injection leaks.
4. Sandbox: OS-enforced write/network limits; Claude Code built-in Bash sandbox (bubblewrap/Seatbelt, `/sandbox`, verify docs); stronger: gVisor, VM, disposable cloud env.

Defense in depth: rules (guardrail/approvals) → OS perms → container → egress → sandbox/VM. Rules = convenience; neeche ki layers = guarantee.

Interview line: *"I treat Claude Code's permission rules as guardrails, not a security boundary, because a rule matches the tool call, not its effect. If Python is allowed, a denied file can still be read through a script. The real boundary is enforced below the agent: a low-privilege OS user, a container that only mounts the repo and masked samples, egress restricted to the model endpoint, and ideally a sandbox. Then even a wrong or prompt-injected action can't reach raw data or send it anywhere."*

### 3.6 Context Window

Context mein sab count hota hai: system prompt, CLAUDE.md, tool definitions (MCP schemas bhi), conversation, padhi files, command outputs.

- Typical ~200K tokens; `/context` se breakdown.
- **Context rot**: context bharne se quality girti hai. Full context ≠ better answers.
- **Auto-compact** limit ke paas; summary mein details lose hoti hain.
- QA killers: 10 MB Jenkins log `cat`, poora report, unused MCP servers.
- Fix: `tail -n 200`, `grep -n "FAILED\|Error"`, `pytest -x -q --tb=short`, subagents.

### 3.7 `/clear`, `/compact`, `/resume`

| Command | Kya | Kab |
|---|---|---|
| `/clear` | History saaf, CLAUDE.md reload | Naya unrelated task |
| `/compact [focus]` | History → summary | Same lamba task; e.g. `/compact keep failing test names and root-cause hypothesis` |
| `/resume`, `claude --resume` | Purani session choose | Kal ka kaam |
| `claude --continue` (`-c`) | Latest session is dir mein | Quick restart |
| `Esc` / `Esc Esc` | Interrupt / rewind | Galat direction |

**Rule:** one task, one session.

### 3.8 Slash Commands

Built-ins: `/init`, `/clear`, `/compact`, `/resume`, `/model`, `/context`, `/cost`, `/permissions`, `/memory`, `/agents`, `/mcp`, `/hooks`, `/config`, `/help`, `/review`.

Custom: `.claude/commands/*.md` → ab **skills** (`.claude/skills/<name>/SKILL.md`). Slash command = saved, versioned, reviewable prompt + workflow (JD ka "one-command workflows").

Shortcuts: `@path/to/file` (file reference), `!` prefix (bash mode).

### 3.9 Model Choice

| Family | Strength | Trade-off | Use |
|---|---|---|---|
| Opus | Deepest reasoning, multi-file planning | Mehenga, slow | Triage, tricky root cause, planning |
| Sonnet | Strong coding, balanced | — | Daily default |
| Haiku | Tez, sasta | Complex reasoning kamzor | Subagents, log summarization, bulk classification |

`/model` se switch. Pattern: plan strong model pe, execute balanced pe; bulk kaam chhote model pe, uncertain cases escalate. Version numbers pe mat atko: **task complexity × cost × latency**.

### 3.10 Cost & Credit Hygiene

Har turn mein poora context dobara jaata hai (prompt caching sasta karta hai, free nahi) → lambi sessions bahut mehengi.

1. Task khatam → `/clear`
2. Specific prompts ("fix test_x in tests/test_score.py; don't touch other files")
3. Logs pehle filter karo
4. Unused MCP servers band
5. Exploration → subagents
6. CI: `--max-turns`, timeouts, per-pipeline budget
7. `/cost` / usage dashboard track karo
8. Sahi model tier

### 3.11 Kab NAHI use karna

1. Unmasked sensitive/regulated data (real consumer credit data, PII, client delivery files) bina approved data-handling path ke. **#1 answer for FICO.**
2. Locked-down hosts jahan outbound AI traffic allowed nahi.
3. Final ship/no-ship sign-off (accountability human ki).
4. Deterministic already-scripted jobs (LLM se script *likhwao*, har baar *chalwao* nahi).
5. Jab output verify nahi kar sakte.
6. Irreversible operations (prod deploy, deletion, client push).
7. Trivial edits.

#### Sidebar: Locked-down hosts

Regulated Linux servers (real client data / production deliveries) jahan freedom bahut kam hai. Analogy: **bank vault room** (security gate, apna saamaan andar nahi, bahar kuch nahi, CCTV, kuch drawers sirf dekhne ke liye).

| Restriction | Matlab |
|---|---|
| Bastion/jump host | `ssh -J bastion user@target` |
| No sudo/root | Install ya config change nahi |
| No outbound internet | pip/curl/git clone nahi; Claude Code host pe usually chal hi nahi sakta |
| Limited tools | `rg`/`jq`/new Python shayad nahi; grep/awk/sed/find/less |
| File transfer blocked | scp/rsync restricted |
| Read-only / `noexec` mounts | `/tmp` se script nahi chalti |
| Audit logging + timeout | Har command record |
| Restricted shell | Sirf approved commands |

```bash
ssh -J bastion qa_user@delivery-host-01
ls -lh /deliveries/region_z/2026-10-20/; du -sh /deliveries/region_z/2026-10-20/
wc -l scores.csv                       # count vs manifest
sha256sum scores.csv                   # checksum vs manifest
awk -F, 'NR>1 && ($2<300 || $2>850) {c++} END {print c+0" out-of-range"}' scores.csv
cut -d, -f3 scores.csv | sort | uniq -c | sort -rn | head
grep -n "ERROR\|FAIL" job.log | tail -n 50
journalctl -u signoff-job --since "1 hour ago" | tail -n 100
head -n 5 scores.csv | sed -E 's/^[^,]*([0-9]{4}),/ACCT-****-\1,/'   # masked sample
```

Rule: **counts, distributions, checksums, masked samples. Raw records kabhi print nahi.**

**Claude Code ke saath 3 patterns (safest pehle):**
1. Laptop pe script likhwao → synthetic data pe test → review → host pe khud chalao. AI host ko touch nahi karta.
2. Masked summary output bahar laao → Claude Code se triage (sirf jab policy allow kare).
3. Fixed wrapper skill: reviewed `scripts/remote_check.sh` jo sirf fixed read-only commands chalaye + output mask kare.

```json
{ "permissions": {
    "allow": ["Bash(./scripts/remote_check.sh:*)"],
    "deny":  ["Bash(ssh:*)", "Bash(scp:*)", "Bash(rsync:*)"] } }
```

Senior nuances: pehle policy check (output AI tak jaa sakta hai?); host ke purane tools ke hisaab se script, same OS image container mein test; bade files pe single-pass `awk`, off-peak; runbook command fail ho toh **doc gap report karo**, silent workaround nahi.

Interview line: *"On locked-down hosts I work read-only and targeted: counts, checksums, distributions and masked samples, never raw records. I wouldn't run an AI agent on the host itself. I'd use Claude Code locally to write and test the check scripts against synthetic data, then run them myself. If policy allows, I'd wrap a fixed set of read-only commands in a reviewed script and let the agent call only that script, with open SSH denied, so every run is identical, masked and auditable."*

### 3.12 10x Scale

- **Governance**: managed settings, org-wide deny, approved endpoints
- **Consistency**: shared CLAUDE.md + skills in git, PR-reviewed
- **Cost**: per-team budgets, model tiering, usage metrics
- **Trust**: AI-generated tests ka review process, mutation/negative checks
- **Auditability**: headless JSON outputs + transcripts store
- **Blast radius**: least-privilege containers, restricted egress

## 4) Real-world Example: FICO Score delivery sign-off (synthetic)

**Scenario:** Naya region "Region-Z". Delivery files: `account_ref, score, reason_codes`. Sign-off checks: score range 300–850, reason codes present, record count = manifest. `test_score_range` fail ho raha hai.

**Setup:** `.claude/settings.json` → `defaultMode: plan`, `data/raw/**` deny, sirf `data/samples/region_z_masked.csv` readable.

```
> The Region-Z sign-off run failed test_score_range. Triage it: is this a
  product defect or a test bug? Do not modify any files. Use only
  data/samples/. Mask account refs in any output.

[Grep]  "def test_score_range" → tests/test_signoff.py:42
[Read]  tests/test_signoff.py (lines 30-70)
[Read]  data/samples/region_z_masked.csv (first 50 lines)
[Bash]  pytest tests/test_signoff.py::test_score_range -q --tb=short
        → FAILED: score 0 not in range(300, 851) for ref ACCT-****-0007

Claude: Records with score 0 appear only where reason_codes == "NO_SCORE".
The delivery spec (docs/delivery_spec.md §4.2) says unscorable records
carry score 0 + an exclusion code. The test treats every record as
scoreable.
Classification: likely TEST BUG (spec gap in test), not product defect.
Proposed fix: filter exclusion-coded records before the range check, and
add a separate test asserting every score-0 record has a valid exclusion
code.
```

**Senior QA follow-up:**
- Spec §4.2 khud padho; cite ≠ verified.
- Region-Z exclusion codes baaki regions jaise hain? Nahi toh data-prep team ke saath spec gap clarify.
- Fix kahin har score 0 pass toh nahi kar raha? Naya test exclusion code *validate* kare.
- Finding sign-off report mein masked format mein.

**Takeaway:** plan mode + deny rules + masked samples + explicit scope = safe regulated workflow; human judgment last word.

## 5) QA/SDET Perspective

**1. AI output = untrusted PR from a fast junior.** Checklist:
- Fix revert karke test chalao: fail hona chahiye. Pass ho toh false pass.
- Assertions strong? `is not None` / `len(x) > 0` weak; exact value + schema + range + business rule strong.
- `git diff tests/`: dheele assertions, naye `skip`/`xfail`, badhe timeouts, `try/except: pass` = red flags.
- Deterministic? Time/random/order/network dependency?
- Scope: sirf expected files?

**2. Product defect vs test bug:** classification evidence ke saath maango (spec ref, failing input, expected vs actual), khud confirm karo.

**3. Flaky isolation:** `pytest -p no:randomly`, `--count=50` (pytest-repeat); ordering vs timing vs data. Agent experiments chalaye, aap judge karo.

**4. Data discipline:** CLAUDE.md: *"Never print raw account identifiers; mask as ACCT-****-last4. Only read data/samples/."* Deny rules se back karo.

**5. Claude Code bhi system under test hai:** sign-off skill ke liye known-bad fixtures (out-of-range score) jinpe FAIL aana *chahiye*.

**6. Reproducibility:** command + commit SHA + output; headless JSON + test report sign-off report mein attach.

---

<!-- Part 2 (Section 6 Hands-on Lab + Section 7 Mistakes) will be appended here -->
