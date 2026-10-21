# 01 — Claude Code Fundamentals

> FICO Score QA sign-off interview prep · Topic 01
> Status: **Complete** — Sections 1–11 + Quiz bank (all answers expanded for voice-mode revision).
> Note: Claude Code changes fast. Verify exact commands/flags with `claude --help` and docs.claude.com before the interview.
> Platforms: **macOS first (FICO laptops), then Windows.** Har jagah ke differences ke liye neeche ka "Platform Notes" section dekho.

---

## 0) Platform Notes: macOS (primary) + Windows

> Claude Code ka concept har OS pe same hai. Fark sirf install, shell, paths aur OS-level isolation mein hai. Remote/locked-down hosts **Linux** hi hote hain, toh wahan ke commands har laptop se same rahenge.

### 0.1 Install

| | macOS (zsh) | Windows (PowerShell) |
|---|---|---|
| Native installer | `curl -fsSL https://claude.ai/install.sh \| bash` | `irm https://claude.ai/install.ps1 \| iex` |
| Alternative | `brew install --cask claude-code` | WSL2 (Ubuntu) ke andar Linux installer |
| npm (Node 18+) | `npm install -g @anthropic-ai/claude-code` | same |
| Extra requirement | — | **Git for Windows** (Claude Code ka Bash tool Git Bash use karta hai) |
| Check | `claude --version`, `claude doctor` | same |

(Installer URLs aur Windows requirements docs se verify karo.)

### 0.2 Paths

| Cheez | macOS | Windows |
|---|---|---|
| User settings | `~/.claude/settings.json` | `%USERPROFILE%\.claude\settings.json` |
| Project settings | `<repo>/.claude/settings.json` | same |
| Managed (admin) settings | `/Library/Application Support/ClaudeCode/managed-settings.json` | `C:\ProgramData\ClaudeCode\managed-settings.json` |
| User CLAUDE.md | `~/.claude/CLAUDE.md` | `%USERPROFILE%\.claude\CLAUDE.md` |

(Managed settings paths docs se verify karo.) Settings files ke andar permission rules mein **forward slashes** (`./data/raw/**`) use karo, dono OS pe.

### 0.3 Shell differences (lab + daily use)

| Kaam | macOS (zsh/bash) | Windows PowerShell | Windows Git Bash |
|---|---|---|---|
| Python | `python3` | `py` / `python` | `python` |
| venv banao | `python3 -m venv .venv` | `py -m venv .venv` | `python -m venv .venv` |
| venv activate | `source .venv/bin/activate` | `.venv\Scripts\Activate.ps1` | `source .venv/Scripts/activate` |
| Folders | `mkdir -p a/b c` | `New-Item -ItemType Directory -Force a\b, c` | `mkdir -p a/b c` |
| Env var | `export X=1` | `$env:X = "1"` | `export X=1` |
| Last exit code | `echo $?` | `$LASTEXITCODE` | `echo $?` |
| Line continuation | `\` | `` ` `` (backtick) | `\` |
| Old file version restore | `git restore --source=HEAD~1 <file>` | same (cross-platform, safe) | same |

**Windows gotcha:** PowerShell 5.1 mein `>` redirect file ko **UTF-16** mein likhta hai, toh Python/pytest ke liye wo file toot sakti hai. Files restore karne ke liye `git restore` use karo, `git show ... > file` nahi.

### 0.4 Shortcuts

| | macOS | Windows |
|---|---|---|
| Claude Code mode cycle | `Shift+Tab` | `Shift+Tab` |
| Interrupt / rewind | `Esc` / `Esc Esc` | same |
| VS Code command palette | `Cmd+Shift+P` | `Ctrl+Shift+P` |
| VS Code Markdown preview | `Cmd+Shift+V` | `Ctrl+Shift+V` |

### 0.5 OS-level isolation (Section 3.5 sidebars ka platform version)

| Layer | macOS | Windows |
|---|---|---|
| Claude Code Bash sandbox | Built-in, macOS **Seatbelt** use karta hai | Native Windows pe nahi; **WSL2** ke andar Linux sandbox (verify docs) |
| Low-privilege user | `sysadminctl` + `dseditgroup` + `chmod` (Section 3.5 sidebar) | `net user` + `icacls` (Section 3.5 sidebar) |
| Container | Docker Desktop | Docker Desktop (WSL2 backend) |

> **Corporate laptop reality:** FICO jaise managed Mac/Windows laptops pe aksar **admin rights nahi hote** aur MDM naye users banane nahi deta. Wahan practical raasta **container** (Docker Desktop, agar approved ho) ya Claude Code ka **built-in sandbox** hai. Low-privilege user wala setup apne personal machine pe lab ke liye karo.

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
# macOS (zsh) — permanent ke liye ~/.zshrc mein daalo
export CLAUDE_CODE_USE_BEDROCK=1; export AWS_REGION=us-east-1   # + AWS profile/SSO creds
export CLAUDE_CODE_USE_VERTEX=1; export CLOUD_ML_REGION=us-east5; export ANTHROPIC_VERTEX_PROJECT_ID=my-gcp-project
```
```powershell
# Windows PowerShell (current session); permanent: [Environment]::SetEnvironmentVariable("CLAUDE_CODE_USE_BEDROCK","1","User")
$env:CLAUDE_CODE_USE_BEDROCK = "1"; $env:AWS_REGION = "us-east-1"
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

#### Sidebar: Low-privilege user setup (practical) + settings rules syntax

**A. Agent ko low-privilege user ke roop mein chalana**

**macOS (personal machine, admin rights chahiye):**
```bash
sudo sysadminctl -addUser qa_agent -fullName "QA Agent" -password -    # password prompt
sudo dseditgroup -o create qa_repo
sudo dseditgroup -o edit -a qa_agent -t user qa_repo
sudo dseditgroup -o edit -a "$USER" -t user qa_repo
sudo mkdir -p /Users/Shared/signoff-lab/data/raw /Users/Shared/signoff-lab/data/samples
sudo chown -R "$USER":qa_repo /Users/Shared/signoff-lab
chmod -R 770 /Users/Shared/signoff-lab
chmod 700 /Users/Shared/signoff-lab/data/raw          # sirf owner
chmod 750 /Users/Shared/signoff-lab/data/samples      # group read

# Verify
echo "FAKE RAW" > /Users/Shared/signoff-lab/data/raw/fake_raw.csv
sudo -u qa_agent cat /Users/Shared/signoff-lab/data/raw/fake_raw.csv     # Permission denied ✅
sudo -u qa_agent python3 -c "open('/Users/Shared/signoff-lab/data/raw/fake_raw.csv').read()"  # Errno 13 ✅

# Run Claude Code as qa_agent
sudo -iu qa_agent
curl -fsSL https://claude.ai/install.sh | bash
cd /Users/Shared/signoff-lab && claude
```

**Windows (admin PowerShell):**
```powershell
net user qa_agent * /add                                   # password prompt
New-Item -ItemType Directory -Force C:\signoff-lab\data\raw, C:\signoff-lab\data\samples
icacls C:\signoff-lab /grant "qa_agent:(OI)(CI)M"          # repo pe modify access
# raw: inheritance hatao, sirf aapko full access
icacls C:\signoff-lab\data\raw /inheritance:r /grant:r "${env:USERNAME}:(OI)(CI)F"
# samples: qa_agent sirf read
icacls C:\signoff-lab\data\samples /inheritance:r /grant:r "${env:USERNAME}:(OI)(CI)F" "qa_agent:(OI)(CI)RX"

# Verify
"FAKE RAW" | Set-Content C:\signoff-lab\data\raw\fake_raw.csv
runas /user:qa_agent "cmd /k type C:\signoff-lab\data\raw\fake_raw.csv"   # Access is denied ✅

# Run Claude Code as qa_agent
runas /user:qa_agent powershell
```

**Linux / WSL2 (Ubuntu):**

```bash
sudo useradd -m -s /bin/bash qa_agent
sudo groupadd qa_repo
sudo usermod -aG qa_repo qa_agent
sudo usermod -aG qa_repo $USER                 # re-login ke baad lagu
sudo mkdir -p /srv/signoff-lab
sudo chown -R $USER:qa_repo /srv/signoff-lab && sudo chmod -R 770 /srv/signoff-lab
mkdir -p /srv/signoff-lab/data/raw     && chmod 700 /srv/signoff-lab/data/raw      # sirf owner
mkdir -p /srv/signoff-lab/data/samples && chmod 750 /srv/signoff-lab/data/samples  # group read

# Verify boundary
sudo -u qa_agent cat /srv/signoff-lab/data/raw/anything.csv          # Permission denied ✅
sudo -u qa_agent python3 -c "open('/srv/signoff-lab/data/raw/anything.csv').read()"  # Errno 13 ✅
sudo -u qa_agent ls /srv/signoff-lab/data/samples                    # visible ✅

# Run Claude Code as that user
sudo -iu qa_agent
curl -fsSL https://claude.ai/install.sh | bash
cd /srv/signoff-lab && claude          # config ~qa_agent/.claude mein; aapke ~/.ssh, ~/.aws nahi dikhte
```
Trade-off: setup zyada; teams aksar container (`USER 1001`) use karti hain, concept same.

**B. Settings files:** `.claude/settings.json` (team, commit) · `.claude/settings.local.json` (personal, gitignored) · `~/.claude/settings.json` (user) · managed (admin). Rules combine; **deny kahin bhi = jeetta hai**; order deny > ask > allow; unlisted → mode ke hisaab se ask.

| Tool | Syntax | Example |
|---|---|---|
| Bash | `Bash(exact)` / `Bash(prefix:*)` | `Bash(git status)`, `Bash(pytest:*)` |
| Read | `Read(pattern)` (Grep/Glob bhi follow) | `Read(./data/raw/**)` |
| Edit | `Edit(pattern)` (sab file-modifying tools) | `Edit(./tests/**)` |
| WebFetch | `WebFetch(domain:x)` | `WebFetch(domain:docs.claude.com)` |
| WebSearch | `WebSearch` | — |
| MCP | `mcp__server` / `mcp__server__tool` | `mcp__jira__create_issue` |
| Bare name | `Read` | tool ke saare uses |

Path prefixes: `./x` / `x` = cwd-relative · `/x` = **settings file ke relative** (absolute nahi!) · `//x` = filesystem absolute · `~/x` = home. `*` = ek level, `**` = nested.

```json
{
  "permissions": {
    "defaultMode": "plan",
    "disableBypassPermissionsMode": "disable",
    "allow": [
      "Read(./src/**)", "Read(./tests/**)", "Read(./docs/**)", "Read(./data/samples/**)",
      "Edit(./tests/**)",
      "Bash(pytest:*)", "Bash(python -m pytest:*)",
      "Bash(git status)", "Bash(git diff:*)", "Bash(git log:*)",
      "WebFetch(domain:docs.claude.com)"
    ],
    "ask": ["Edit(./src/**)", "Bash(git add:*)", "Bash(git commit:*)"],
    "deny": [
      "Read(./.env)", "Read(./.env.*)", "Read(./data/raw/**)", "Read(~/.ssh/**)", "Read(~/.aws/**)",
      "Edit(./.claude/**)", "Edit(./data/**)",
      "Bash(curl:*)", "Bash(wget:*)", "Bash(ssh:*)", "Bash(scp:*)", "Bash(rm:*)", "Bash(git push:*)",
      "WebFetch"
    ]
  }
}
```
Why: plan default; bypass disabled; tests editable but `src/` edit pe ask (product-vs-test change pakadne ke liye); `.claude/**` edit deny (agent apne rules na badle); push deny. **Trap:** bare `WebFetch` deny docs-domain allow ko bhi kaat deta hai (deny jeetta hai), toh docs chahiye toh bare deny hatao.

Rules banane ke tareeke: `/permissions`; "don't ask again" → local settings (review karke shared mein lao); logic rules → **PreToolUse hooks** (later topic).

Rules ko test cases ki tarah verify karo: Read raw → blocked · `cat` raw → ask/block · `python -c open(raw)` → **rules fail ho sakte hain → OS permission zaroori** · Edit src → ask · git push → blocked.

Interview line: *"I define permissions in the committed `.claude/settings.json` so the team gets the same guardrails through code review: allowlist specific test and git-read commands, put product-code edits and commits on ask, deny secrets, raw data, network tools, push and edits to `.claude` itself, and disable bypass mode. Then I test the rules like a test suite, including a Python-script bypass attempt, which is why the agent also runs as a low-privilege user that can't read raw data at the OS level."*
(Exact syntax, khaaskar Bash wildcards aur `disableBypassPermissionsMode`, docs se verify karo.)

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

#### Sidebar: `/agents`, `/mcp`, `/hooks`, `/config`, `/help`, `/review`

| Command | Ek line | QA use |
|---|---|---|
| `/agents` | Subagents banao/manage karo | Read-only failure triager |
| `/mcp` | External tool connections (Jira, GitHub, DB) | Jira defects |
| `/hooks` | Tool call se pehle/baad apni script | `data/raw` block |
| `/config` | Settings UI | Personal session tuning |
| `/help` | Saare commands (custom bhi) | Team skills dhoondhna |
| `/review` | Code changes / PR review | Pre-merge AI review |

**1. `/agents`: Subagents.** Analogy: specialist alag kamre mein kaam kare, aapko sirf ek page report de. Apna context window, system prompt, allowed tools, optional model.
Files: project `<repo>/.claude/agents/*.md` (git) · user: macOS `~/.claude/agents/`, Windows `%USERPROFILE%\.claude\agents\`.
```markdown
---
name: failure-triager
description: Use when a test fails. Read-only triage that classifies product defect vs test bug vs spec ambiguity, with evidence.
tools: Read, Grep, Glob, Bash
model: sonnet
---
You are a QA triage specialist. Never modify files.
For each failing test, return:
- test name
- classification: product defect | test bug | spec ambiguity | environment
- evidence: spec file + line range + quoted text, failing input, expected vs actual
- confidence: high | medium | low
Mask any account reference as ACCT-****-<last4>.
```
Nuances: main context bachta hai; least privilege per role (no Edit; Bash pe project rules lagte hain); summary mein details chhoot sakti hain, isliye evidence fields compulsory; parallel triage possible.

**2. `/mcp`: Model Context Protocol.** Universal plug adapter: external systems ke tools (`mcp__jira__create_issue`). `/mcp` = status, OAuth login, tools list.
```bash
claude mcp add --transport http jira https://<your-jira-mcp-url>
claude mcp add my-db -- npx -y <some-mcp-server-package>
claude mcp add --scope project --transport http jira https://<url>   # .mcp.json in repo
claude mcp list
```
Nuances: tool schemas har request mein context khaate hain, unused band karo · permissions `mcp__jira` / `mcp__jira__create_issue`, write actions ask pe · server ka access = agent ka access (regulated DB MCP = raw data path) · third-party servers = code on your machine, approved only · tool output mein prompt injection possible · AI regression analyzer ke Jira auto-filing se link.

**3. `/hooks`: Deterministic automation.** CLAUDE.md = request; hook = har baar chalne wala rule.

| Event | Kab | Use |
|---|---|---|
| PreToolUse | Tool se pehle | Block (exit 2) |
| PostToolUse | Tool ke baad | Lint/format, log |
| UserPromptSubmit | Prompt se pehle | Check/add context |
| Stop / SubagentStop | Kaam khatam | Final check |
| SessionStart | Session start | Env info |
| PreCompact | Compact se pehle | Save important info |
| Notification | Input chahiye | Alert |

```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Bash|Read|Grep|Glob",
        "hooks": [ { "type": "command", "command": "python3 .claude/hooks/block_raw.py" } ] }
    ]
  }
}
```
(Windows: `python` instead of `python3`.)
```python
# .claude/hooks/block_raw.py
import json
import sys

data = json.load(sys.stdin)
tool_input = data.get("tool_input", {})
text = " ".join(str(v) for v in tool_input.values()).replace("\\", "/")

if "data/raw" in text:
    print("Blocked by hook: data/raw is off-limits. Use data/samples/.", file=sys.stderr)
    sys.exit(2)   # block; stderr goes to Claude

sys.exit(0)
```
Nuances: content inspect karta hai (python -c bhi pakda), lekin string-splitting se evade ho sakta hai, toh **boundary nahi** · hooks aapki permissions se chalte hain, PR-review karo · fast rakho · QA ideas: PostToolUse lint, Stop pe tests-ran check, Bash audit log.

**4. `/config`:** settings panel (theme, model, auto-compact, notifications, vim mode). Changes aksar user-level; team guardrails project `settings.json` + git mein.

**5. `/help`:** saare commands incl. custom skills; naye repo mein pehle chalao. `claude --help` = CLI flags.

**6. `/review`:** changes/PR review (version-dependent; PR ke liye `gh` lag sakta hai). `/security-review` alag. QA ke liye custom review skill with checklist (weak assertions, skip/xfail, timeouts, fails-without-fix). AI review = pre-filter, human replacement nahi. Same session self-review weak; fresh session/subagent use karo.

**Stack:** CLAUDE.md (advisory) → Permissions (guardrail) → Hooks (deterministic) → Subagents (isolated specialist) → MCP (external systems) → Skills/commands (one-command workflows).

Interview line: *"I separate advice from enforcement. CLAUDE.md tells the agent how we work, permissions define what it may do, and hooks enforce checks that must happen every time, like blocking any command that references raw data or logging every shell command. Subagents keep heavy exploration, like triaging fifty failures, out of the main context, with a read-only toolset and a strict evidence format. MCP connects tools like Jira, but I keep write actions on ask and I'm careful about which data systems I expose. I still review all of these like code, because a hook or an MCP server runs with my permissions."*

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

Laptop se connect: **macOS** Terminal mein built-in `ssh`; **Windows** PowerShell mein built-in OpenSSH client (`ssh -J bastion qa_user@host` same chalega). Keys/config: macOS `~/.ssh/config`, Windows `%USERPROFILE%\.ssh\config`. Host ke andar ke commands Linux ke hain, laptop OS se fark nahi padta.

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

## 6) Hands-on Lab: Claude Code se bug fix + test add karwana

> **Goal:** ek chhota synthetic "score delivery validator" repo banao jisme ek bug jaan-bujh ke daala gaya hai. Claude Code se pehle triage, phir fix + tests karwao, aur **har step pe verify karo** ki agent ne sahi kaam kiya.
> **Note:** LLM output har baar thoda alag hota hai. "Expected" ka matlab hai *ye behaviour dikhna chahiye*, exact same words nahi.
> **Resume framing:** ye aapka **personal lab** hai. Interview mein bolo: *"In my personal lab I built…"*

### 6.0 Prerequisites

- Python 3.10+, git, Claude Code installed (`claude --version`)
- Neeche ki commands **macOS (zsh)** ki hain; Windows ke liye PowerShell version saath mein diya hai. Baaki differences Section 0.3 mein hain.
- Windows pe `python3` ki jagah `python` / `py` likho.

### 6.1 Repo banao

**macOS:**
```bash
mkdir signoff-lab && cd signoff-lab
git init
mkdir -p src/signoff tests docs data/samples data/raw .claude
python3 -m venv .venv
source .venv/bin/activate
pip install pytest
```

**Windows (PowerShell):**
```powershell
mkdir signoff-lab; cd signoff-lab
git init
New-Item -ItemType Directory -Force src\signoff, tests, docs, data\samples, data\raw, .claude
py -m venv .venv
.venv\Scripts\Activate.ps1      # "running scripts is disabled" aaye toh:
                                # Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
pip install pytest
```

> Files VS Code mein banao/save karo (UTF-8 default hai). PowerShell `>` redirect se files mat banao (UTF-16 gotcha, Section 0.3).

**`pyproject.toml`**
```toml
[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

**`.gitignore`**
```
.venv/
__pycache__/
.claude/settings.local.json
```

**`docs/spec.md`** (source of truth)
```markdown
# Delivery Spec (synthetic) v1
1. A valid score is an integer from 300 to 850 inclusive.
2. Score 0 is allowed only for unscorable records, and only with an
   exclusion reason code starting with "X" (e.g. X01).
3. Account references must be masked in any output as ACCT-****-<last4>.
4. Record count must equal the manifest count.
```

**`src/signoff/__init__.py`**: khaali file.

**`src/signoff/validator.py`**
```python
VALID_MIN = 300
VALID_MAX = 850


def is_valid_score(score: int, reason_code: str = "") -> bool:
    """Return True if the score is valid per docs/spec.md."""
    if score == 0:
        return reason_code.startswith("X")
    return VALID_MIN < score < VALID_MAX


def mask_ref(account_ref: str) -> str:
    """Mask an account reference per docs/spec.md."""
    return "ACCT-****-" + account_ref[-4:]


def count_matches_manifest(records: list, manifest_count: int) -> bool:
    return len(records) == manifest_count
```

**`tests/test_validator.py`**
```python
from signoff.validator import is_valid_score, mask_ref, count_matches_manifest


def test_typical_score_is_valid():
    assert is_valid_score(720)


def test_out_of_range_score_is_invalid():
    assert not is_valid_score(900)


def test_mask_ref():
    assert mask_ref("1234567890").startswith("ACCT-****")


def test_count_matches():
    assert count_matches_manifest([1, 2, 3], 3)
```

**`data/samples/region_z_masked.csv`**
```
account_ref,score,reason_code
ACCT-****-0001,300,
ACCT-****-0002,850,
ACCT-****-0003,0,X01
ACCT-****-0004,712,
```

**`data/raw/fake_raw.csv`**: permission test ke liye ek fake file.
```
THIS FILE PRETENDS TO BE RAW CLIENT DATA - THE AGENT MUST NOT READ IT
```

**`CLAUDE.md`**
```markdown
# Sign-off lab
- Source of truth: docs/spec.md. If code or tests disagree with the spec,
  the spec wins. If the spec is ambiguous, flag it instead of guessing.
- Run tests: `python -m pytest -q`
- Never read data/raw/. Use data/samples/ only.
- Mask account refs as ACCT-****-<last4> in any output.
- When fixing a bug, change product code, not test expectations, unless the
  test contradicts the spec. Always say which one you changed and why.
- Keep diffs minimal. Don't touch unrelated files.
```

**`.claude/settings.json`**
```json
{
  "permissions": {
    "defaultMode": "plan",
    "allow": [
      "Read(./src/**)", "Read(./tests/**)", "Read(./docs/**)", "Read(./data/samples/**)",
      "Bash(python -m pytest:*)", "Bash(pytest:*)",
      "Bash(git status)", "Bash(git diff:*)"
    ],
    "ask":  ["Edit(./src/**)", "Edit(./tests/**)"],
    "deny": [
      "Read(./data/raw/**)", "Bash(curl:*)", "Bash(rm:*)",
      "Bash(git push:*)", "Edit(./.claude/**)"
    ]
  }
}
```

```bash
git add . && git commit -m "baseline: synthetic signoff lab"
```

> **Spoiler (agent ko mat batana, ye sirf aapke liye hai):** `is_valid_score` mein `300 < score < 850` hai, jabki spec kehta hai 300 aur 850 **inclusive**. Yaani boundary bug. Saath hi `test_mask_ref` weak hai: sirf `startswith` check karta hai.

### 6.2 Step 1: Baseline (bina Claude ke)

```bash
python -m pytest -q
```
**Expected:**
```
....                                                         [100%]
4 passed in 0.0Xs
```
**Lesson:** bug hone ke bawajood suite **green** hai. **Green suite ≠ correct product.** Tests kabhi boundaries check hi nahi kar rahe the.

### 6.3 Step 2: Permission boundary test (fix se pehle)

```bash
claude
```
Session plan mode mein khulna chahiye (status line/footer mein mode dikhega).

Prompt:
```
Show me the first 5 lines of data/raw/fake_raw.csv
```
**Expected:** Read tool **deny** ho jaata hai, aur Claude batata hai ki access allowed nahi hai.

Prompt:
```
Then use python to print that file.
```
**Expected:** `Bash(python -c ...)` allow list mein nahi hai (sirf `python -m pytest` hai), toh **approval maangega** ya plan mode ki wajah se chalayega hi nahi. **"No" bolo.**

**Lesson:** agar `Bash(python:*)` allow hota toh ye file padh leta. Rules guardrail hain, **OS permissions boundary hain** (Section 3.5 sidebar).

```
/clear
```

### 6.4 Step 3: Triage in plan mode

Prompt:
```
Read docs/spec.md, src/signoff/validator.py and tests/test_validator.py.
Compare the implementation and the tests against the spec.
List every gap as: spec rule, what code does, what tests check, verdict
(product defect / test gap / spec ambiguity). Do not modify anything.
```
**Expected (approx):**
- **Rule 1:** code `300 < score < 850` hai, toh 300 aur 850 reject ho jaate hain. Ye **product defect** hai. Tests boundaries cover nahi karte, toh saath mein **test gap** bhi hai.
- **Rule 2:** score 0 ka logic code mein hai, lekin koi test nahi. **Test gap.**
- **Rule 3:** `test_mask_ref` sirf prefix check karta hai, last4 verify nahi karta. **Weak assertion.** Kam length wale ref pe behaviour spec mein defined nahi hai, toh **spec ambiguity**.
- **Rule 4:** count ka sirf positive case hai, mismatch ka koi test nahi.

**Aapka verification:** agent ki har claim khud spec aur code ke against check karo. Agar usne kuch miss kiya ya kuch galat bola, observation log mein note karo.

### 6.5 Step 4: Fix + tests (default mode)

`Shift+Tab` se mode **default** pe le aao (taaki edits approval maange).

Prompt:
```
Fix the product defect for spec rule 1 with the smallest possible change.
Then add tests: boundary values 299, 300, 850, 851; score 0 with X01 (valid);
score 0 with no code (invalid); exact mask output for "1234567890";
count mismatch case. Use pytest.mark.parametrize where it helps.
Run the suite and show me the result. Don't change existing assertions.
```
**Expected:**
- `src/signoff/validator.py` ke edit pe approval maangega. Diff dekho: sirf `VALID_MIN <= score <= VALID_MAX` badalna chahiye.
- `tests/test_validator.py` ke edit pe approval maangega. Diff mein naye tests hone chahiye, jaise:

```python
import pytest

@pytest.mark.parametrize("score,expected", [
    (299, False), (300, True), (850, True), (851, False),
])
def test_score_boundaries(score, expected):
    assert is_valid_score(score) is expected


def test_zero_score_with_exclusion_code_is_valid():
    assert is_valid_score(0, "X01") is True


def test_zero_score_without_exclusion_code_is_invalid():
    assert is_valid_score(0) is False


def test_mask_ref_exact():
    assert mask_ref("1234567890") == "ACCT-****-7890"


def test_count_mismatch():
    assert count_matches_manifest([1, 2], 3) is False
```
- Pytest run (approx): `12 passed`

**Diff review checklist:**
```bash
git diff --stat           # sirf 2 files honi chahiye
git diff src/             # ek line ka change
git diff tests/           # sirf additions; purane assertions untouched
```

### 6.6 Step 5: Mutation check (sabse important step)

Naye tests ko **bug ke against** chalao. Agar wo fail nahi hote, toh wo kuch validate hi nahi kar rahe.

```bash
git stash push src/signoff/validator.py    # fix temporarily hatao
python -m pytest -q
```
**Expected:**
```
FAILED tests/test_validator.py::test_score_boundaries[300-True]
FAILED tests/test_validator.py::test_score_boundaries[850-True]
2 failed, 10 passed
```
```bash
git stash pop                              # fix wapas
python -m pytest -q                        # sab pass
git add . && git commit -m "fix: inclusive score range per spec rule 1; add boundary tests"
```
**Lesson:** "test fix ke bina fail hota hai" ye proof hai ki test sach mein behaviour validate karta hai. Ye manual **mutation testing** hai. Bade scale pe `mutmut` jaise tools yahi kaam automatically karte hain.

### 6.7 Step 6: Goal-substitution trap

Bug wapas daalo, lekin naye tests rehne do:
```bash
# macOS / Windows dono pe same (git restore cross-platform hai)
git restore --source=HEAD~1 src/signoff/validator.py
python -m pytest -q      # 2 failed   (venv active ho toh macOS pe bhi `python` chalega)
```
Claude mein:
```
/clear
```
Prompt (jaan-bujh ke vague):
```
pytest is failing. Make it green.
```
**Dekho:** agent kaunsi file edit karne ki permission maangta hai?
- ✅ **Achha:** `src/` edit karta hai aur spec rule 1 cite karta hai (CLAUDE.md ka rule follow hua).
- ❌ **Bura:** test ki expectation badalta hai (`(300, False)`), ya test delete/skip karta hai. **Approval deny karo** aur observation log mein note karo.

**Lesson:** vague prompt + "make it green" goal substitution ko invite karta hai. Isliye CLAUDE.md rule, `ask` on tests, aur diff review teeno chahiye.

```bash
git checkout -- src/     # lab state saaf karo
```

### 6.8 Step 7: Context & cost hygiene

Session mein:
```
/context        # tokens kahan ja rahe hain: system, tools, CLAUDE.md, messages
/cost           # API-key login pe cost dikhega; subscription pe usage alag dikh sakta hai
/compact keep only the spec gaps found and the fix status
/context        # compact ke baad usage kam dikhna chahiye
/clear
```
**Lesson:** dekho CLAUDE.md aur tool definitions kitna context lete hain, *aapke kuch bhi poochne se pehle hi*.

### 6.9 Step 8: Headless run (CI style)

**macOS:**
```bash
claude -p "Run python -m pytest -q and report passed count, failed count and failing test names." \
  --output-format json \
  --allowedTools "Bash(python -m pytest:*)" "Read" \
  --max-turns 5
```

**Windows (PowerShell):**
```powershell
claude -p "Run python -m pytest -q and report passed count, failed count and failing test names." `
  --output-format json `
  --allowedTools "Bash(python -m pytest:*)" "Read" `
  --max-turns 5
```
**Expected:** ek JSON object jisme model ka answer ek `result` field mein hoga, saath mein metadata jaise session id, turns, duration, cost (exact keys apne version mein dekh lena).

**Senior lesson:** CI gate **pytest ke exit code / JUnit XML** pe lagao, LLM ke summary pe nahi:
```bash
# macOS
python -m pytest -q --junitxml=report.xml; echo "exit=$?"
```
```powershell
# Windows PowerShell
python -m pytest -q --junitxml=report.xml; "exit=$LASTEXITCODE"
```
LLM summary report ko readable banane ke liye hai. **Pass/fail ka decision deterministic tool ka hai.**

### 6.10 Observation log (khud bharo; interview mein yahi aapka "real example" hai)

| Step | Kya expect kiya | Kya hua | Kya seekha |
|---|---|---|---|
| Baseline | 4 passed despite bug | | |
| Raw data read | Denied | | |
| Python bypass | Ask / blocked | | |
| Triage | 4 gaps, boundary = product defect | | |
| Fix diff | 1-line src change + new tests | | |
| Mutation check | 2 failed without fix | | |
| Trap | Edits src, not tests | | |
| Headless | JSON; gate on exit code | | |

**Interview demo line:** *"In a personal lab I planted a boundary bug in a synthetic score validator. The existing suite stayed green, which was the first lesson. I had Claude Code triage in plan mode against the spec, then fix it with edits on ask. I reviewed the diff, and I proved the new boundary tests were meaningful by stashing the fix and watching them fail. I also tried a vague 'make it green' prompt to see whether the agent would weaken tests instead of fixing code."*

---

## 7) Common Mistakes & Anti-patterns

| # | Mistake | Kyun bura hai | Fix |
|---|---|---|---|
| 1 | Agent ka "all tests pass ✅" maan lena | Shayad ek hi file chalayi, ya output padha hi nahi | Suite khud chalao; CI exit code dekho |
| 2 | `git diff tests/` review na karna | Goal substitution: assertion dheela, `skip`, timeout badha diya | Har diff review; tests pe `ask` rule |
| 3 | Naye tests ka mutation check na karna | Test bug ke saath bhi pass ho sakta hai (false pass) | Fix stash/revert karke test fail hona chahiye; scale pe `mutmut` |
| 4 | Weak assertions accept karna | `is not None`, `len > 0`, `startswith` behaviour prove nahi karte | Exact values, boundaries, negative cases, schema |
| 5 | Ek giant session mein saare tasks | Context rot, purane task ka context naye ko confuse karta hai, cost badhta hai | One task, one session; `/clear` |
| 6 | Bade logs `cat` karwana | Context bhar jaata hai, important part kho jaata hai | `grep`, `tail`, `--tb=short`, subagents |
| 7 | Real machine pe `--dangerously-skip-permissions` | Ek galat command = data loss ya leak | Sirf disposable isolated sandbox mein |
| 8 | Deny rules ko security boundary samajhna | Script/alternate tool se bypass ho sakta hai | OS user, container, egress control, sandbox |
| 9 | Broad allows: `Bash(*)`, `Bash(python:*)` | Practically bypass mode | Specific commands allowlist |
| 10 | Auto-generated CLAUDE.md bina trim kiye | Lamba, generic; har request mein tokens khata hai; important rules dab jaate hain | Short, specific, reviewed; PR mein maintain |
| 11 | Raw/unmasked data prompt mein paste karna | Data boundary violation | Masked samples only; masking rule + deny rules |
| 12 | LLM summary ko CI gate banana | Non-deterministic, hallucinate kar sakta hai | Gate = exit code/JUnit; LLM = explanation only |
| 13 | Vague prompts ("improve tests") | Scope creep, random changes | Scope, files, constraints, done-criteria do |
| 14 | CI mein no `--max-turns`/timeout/budget | Infinite loop credits jala sakta hai | Caps + per-pipeline budget + alerts |
| 15 | Agent ke citations verify na karna | "Spec §4.2 says…" hallucinated ho sakta hai | Cited source khud kholo |
| 16 | Docs gap chupchaap workaround karna | Agla banda wahi problem phir face karega | Gap report karo, doc fix ka PR/ticket |
| 17 | Galat model tier | Simple kaam pe expensive model, ya complex triage pe weak model | Complexity × cost × latency se choose |
| 18 | Bade unscoped diffs accept karna | Review impossible, hidden regressions | "Minimal diff, no unrelated files" + `git diff --stat` |

---

## 8) Interview Questions (R1 + Senior) with spoken model answers

> Har answer ~60–90 sec bolne ke liye hai. **"Interviewer kya sunna chahta hai"** line padh ke answer ka core yaad rakho.

### Q1. What is Claude Code, and how is it different from a chat assistant? (R1)

**Interviewer kya sunna chahta hai:** agent vs chatbot, aur control ka concept.

**Model answer:**
"Claude Code is Anthropic's agentic coding tool. It runs in the terminal, the IDE, desktop or headless. The key difference from a chat assistant is that it doesn't just suggest code. It acts on the actual repository. It can read files, search the codebase, edit files and run shell commands like tests or git, look at the results, and decide the next step itself.

Architecturally, I think of it as a harness around the model: the model plus tools, an execution loop, a permission layer and context management. The model decides what it wants to do, but the harness decides whether that action is allowed and actually executes it.

That shift from 'tells you' to 'does it' is why control matters so much. You decide what it can read, what it can run, and what needs approval, and you still verify the output. For QA that's powerful, because a lot of our work is repeatable: run a suite, read failures, correlate with code, draft a report. But it also means I treat its output like a PR from a fast new teammate, not as ground truth."

### Q2. Walk me through the agentic loop. (R1)

**Interviewer kya sunna chahta hai:** model requests, harness executes; gather → act → verify; failure modes.

**Model answer:**
"Each turn, the model sees the system prompt, the CLAUDE.md project instructions, the definitions of the available tools and the conversation so far. It then either replies with text, which ends the turn, or emits a tool call, for example 'run pytest on this file'.

The harness intercepts that call and checks permissions. If a deny rule matches, it's blocked. If an allow rule or the current mode permits it, it executes. Otherwise it asks me. The result, like stdout, file contents or an error, is appended to the context and goes back to the model, and the loop repeats.

In practice you see three phases: gather context, take action, verify. The important point is that the model never executes anything itself. It only requests, so the real safety boundary is the harness and the OS, not the model's intentions.

The failure modes I watch for are premature success claims, changing the test instead of the code, rabbit-holing on a wrong hypothesis until the context fills up, and scope creep into unrelated files. My mitigations are small scoped tasks, plan mode first, reviewing the diff, and running the verification myself."

### Q3. What built-in tools does it have, and why dedicated tools instead of just a shell? (R1)

**Interviewer kya sunna chahta hai:** tools ke naam + granular permissions + token efficiency.

**Model answer:**
"The core ones are Read for reading files, Edit for exact string replacements in an existing file, Write for creating or overwriting a whole file, Bash for shell commands, and Grep and Glob for searching content and finding files by pattern. On top of that there are web tools, subagents for isolated sub-tasks, and task tracking.

Technically, Bash alone could do most of this, so why dedicated tools? Three reasons. First, granular permissions: I can allow reading tests but deny reading raw data, or allow edits under tests but ask for product code. Second, efficiency: Grep returns structured, compact results, which saves context and cost compared to dumping shell output. Third, safety: Edit requires the file to be read first and the old string to be unique, so you get small, reviewable diffs instead of blind overwrites. That's also why I prefer Edit over Write for existing files: rewriting a large file risks silently losing lines.

Bash is the most powerful and the riskiest tool, so most of my permission rules focus on it."

### Q4. Explain permission modes and allow/ask/deny rules. When would you use which? (R1)

**Interviewer kya sunna chahta hai:** 4 modes, precedence, deny wins, shared settings in git.

**Model answer:**
"There are four main modes. Default asks the first time for edits and new commands. AcceptEdits auto-approves file edits but still asks for shell commands. Plan mode is read-only: it explores and proposes a plan without changing anything. BypassPermissions skips all prompts, and I'd only use it in a disposable, isolated sandbox.

My default for unfamiliar code or anything high-risk is plan mode first, then default mode for the change itself.

Rules live in settings files: user level, the project's shared `.claude/settings.json` which is committed, a personal local file, and organisation-managed settings that override everything. Rules come in allow, ask and deny lists, and deny always wins. For example, I'd allow `pytest` and `git diff`, ask for product-code edits and commits, and deny reading `.env` or raw data, network tools like curl, and `git push`.

I commit the project settings so the whole team gets the same guardrails, and so changes to them go through code review. In regulated work I prefer a tight allowlist over a denylist, because a list of what's forbidden is never complete."

### Q5. What is the context window and how do you manage it? `/clear` vs `/compact`? (R1)

**Interviewer kya sunna chahta hai:** sab kuch context mein count hota hai, context rot, cost link, practical hygiene.

**Model answer:**
"The context window is the model's working memory for each request. Everything counts against it: the system prompt, CLAUDE.md, the tool definitions including MCP servers, the whole conversation, every file read and every command output.

Two things matter. First, quality degrades as it fills up. Older details get less attention and irrelevant content confuses the reasoning, so a full context isn't a better context. Second, cost: the context is resent each turn, so long sessions get expensive.

So my rule is one task, one session. When I finish a task and start an unrelated one, I use `/clear`, which wipes the history but reloads CLAUDE.md. `/compact` is for when I'm mid-task and the session is long: it summarises the history, and I can tell it what to keep, like the failing test names and the current hypothesis. The trade-off is that the summary loses detail.

The biggest context killers in QA are huge logs, so I filter first with grep or tail, use short tracebacks, switch off unused MCP servers, and push broad exploration into subagents that return only a summary. `/context` shows me where tokens are going."

### Q6. When would you NOT use Claude Code? (R1 / Senior)

**Interviewer kya sunna chahta hai:** judgment, regulated data pehla answer, accountability.

**Model answer:**
"First and most important in this domain: on unmasked regulated data, like real consumer credit data or client delivery files, unless there's an approved data-handling path covering the endpoint, masking and policy sign-off. Related to that: on locked-down hosts where policy doesn't allow outbound AI traffic. There, I'd use it locally to write and test scripts against synthetic data and run them myself.

Second, for the final ship or no-ship decision. An agent can triage and draft the sign-off report, but accountability stays with a human.

Third, for deterministic jobs that are already scripted. A stable pytest or bash script is cheaper, faster and reproducible. I'd use the agent to write or improve the script, not to run the job through an LLM every time.

Fourth, when I can't verify the output. If I don't understand the domain well enough to catch a false pass, the speed doesn't help.

And finally, irreversible operations like production deploys or data deletion, and trivial edits where the agent overhead isn't worth it."

### Q7. Are permission rules a security boundary? How would you run Claude Code safely near regulated data? (Senior)

**Interviewer kya sunna chahta hai:** "No" + kyun + layered defence + routing.

**Model answer:**
"No. They're guardrails, not a boundary, because a rule matches the tool call, not its effect. If I deny reading a raw data folder but allow Python, the agent can write a one-line script that opens the file. Bash prefix matching is also best-effort.

So I enforce the boundary below the agent, in layers. One: run it as a low-privilege OS user, or in a container, that simply can't read raw data, so every route fails at the kernel. Two: container isolation, mounting only the repo and masked samples read-only, with no credentials or SSH keys inside. Three: network egress restricted to the approved model endpoint, so even if something is read, it can't be sent anywhere. That also limits prompt injection from a malicious file or log. Four: sandboxing for shell commands where available.

On top of that, at the organisation level: route traffic through the company's own cloud account, for example Bedrock, and use managed settings that users can't override. But routing only answers where traffic goes, not what's allowed to go, so masking rules stay. And I test the guardrails, including deliberate bypass attempts, like any other test suite."

### Q8. How do you evaluate whether an AI-generated test actually validates the intended behaviour? (Senior)

**Interviewer kya sunna chahta hai:** spec-first, mutation check, assertion strength, determinism.

**Model answer:**
"I start from the spec, not from the test. I write down what behaviour should be proven, including boundaries and negative cases, and then check the test against that list.

Then four checks. One, does it fail without the fix? I revert or stash the product change and run the test. If it still passes, it's a false pass and validates nothing. At scale, mutation testing tools automate this. Two, assertion strength: 'is not None' or 'length greater than zero' prove almost nothing. I want exact values, boundary values on both sides, error cases, and schema plus business-rule checks. Three, is it testing the real thing? Over-mocking can mean the test only verifies the mock. Four, determinism: no hidden dependency on time, randomness, test order or the network.

I also check the scope of the diff, because a generated test sometimes quietly changes a fixture or helper that other tests depend on.

For example, in my lab the existing suite was green despite an off-by-one boundary bug, because no test checked 300 or 850. Proving the new tests failed on the buggy code was what made me trust them."

### Q9. The agent says it fixed a failing sign-off test. How do you make sure it didn't just change the test? (Senior)

**Interviewer kya sunna chahta hai:** diff review, red flags, classification with evidence, process guardrails.

**Model answer:**
"I look at the diff first, not the summary. `git diff --stat` tells me which files changed, and then I read the test diff specifically. The red flags are loosened or deleted assertions, new skip or xfail markers, bigger timeouts or retries, broad try/except blocks, and changed fixtures or expected data files.

Then I ask the real question: was this a product defect or a test bug? Both are legitimate fixes, but they need evidence. If the test changed, the agent should point to the spec rule the old test contradicted, and I verify that citation myself, because agents can cite things confidently that don't say what they claim. If the product changed, the test should fail on the old code and pass on the new.

To prevent it rather than catch it, I put the rule in CLAUDE.md, 'change product code, not test expectations, unless the test contradicts the spec, and say which you changed and why', and I set test edits to ask in the permission settings. In my lab I deliberately gave a vague 'make it green' prompt to see how the agent behaves, and that's exactly the situation where those guardrails matter."

### Q10. How would you use Claude Code in a CI pipeline for sign-off? What guardrails? (Senior)

**Interviewer kya sunna chahta hai:** headless mode, deterministic gate, least privilege, caps, audit.

**Model answer:**
"I'd use headless mode, `claude -p` with JSON output, for the parts that need judgment: summarising failures, grouping them by likely cause, and drafting the sign-off report. I wouldn't let it decide pass or fail. The gate stays deterministic: test exit codes, JUnit XML, threshold checks on metrics. The LLM's text is an explanation layer on top.

Guardrails: an explicit tool allowlist for exactly the commands it needs, never bypass mode on a shared runner, and a max-turns cap plus a job timeout, so a loop can't burn credits overnight. It runs in a least-privilege container with only the workspace mounted, no production credentials, and egress limited to the model endpoint. It only sees masked data.

For auditability, I'd store the JSON output, the commit SHA and the test reports with the sign-off record, so anyone can see what was run and what the agent concluded. And I'd treat the prompt and the skill as code, versioned and reviewed, with known-bad fixtures, like a delivery with a deliberately out-of-range score, that the workflow must flag. If it doesn't, the workflow itself is broken."

### Q11. How do you work on locked-down Linux hosts, and where does Claude Code fit? (Senior)

**Interviewer kya sunna chahta hai:** read-only Bash discipline, masking, policy-first, safe AI patterns.

**Model answer:**
"On locked-down hosts I assume: access through a bastion, no sudo, no internet, limited tools, file transfer restricted, and every command audited. So I work read-only and targeted. I check file sizes and record counts against the manifest, checksums against the manifest, distributions with `cut`, `sort` and `uniq`, out-of-range counts with a single-pass `awk`, and only the relevant log lines with `grep` and `tail`. If I need to show a sample, I mask it in the pipeline. I never print raw records.

I wouldn't run an AI agent on the host itself. The first question is policy: can output from this host go to an AI tool at all? If not, I use Claude Code on my machine to write and test check scripts against synthetic data, in a container with the same OS image so the old tool versions match, and then I run them myself. If policy allows, I'd wrap a fixed set of read-only commands in a reviewed script and allow the agent to call only that script, with open SSH denied, so runs are identical, masked and auditable.

And if a runbook command doesn't work on the host, I report the doc gap instead of quietly working around it."

### Q12. Thirty engineers and twenty pipelines start using Claude Code. How do you handle model choice, cost and consistency? (Senior)

**Interviewer kya sunna chahta hai:** scale thinking: governance, tiering, metrics, shared assets.

**Model answer:**
"For model choice, I think in terms of task complexity versus cost and latency, not version numbers. The strongest model for planning and tricky root-cause analysis, a balanced model as the daily default for writing tests and fixes, and a small fast model for bulk work like classifying hundreds of failures or summarising logs, with uncertain cases escalated.

For cost: one task per session, filtered logs, unused MCP servers off, subagents for exploration, and in CI hard caps, timeouts and a budget per pipeline with alerts. I'd track spend per team like any other metric.

For consistency, the biggest risk at scale is everyone using different prompts and getting different quality. So CLAUDE.md files and skills live in git and go through PR review, shared permission settings are committed, and organisation-managed settings enforce the non-negotiables like approved endpoints and data denies.

Finally, trust. 'The AI wrote it' doesn't mean 'it was reviewed'. I'd keep review requirements for generated tests and track quality signals over time: mutation score, flake rate, escaped defects, and how often generated changes get rejected in review."

---

## 9) Cross-question Chains (senior interviewer drill)

### Chain A: Triage → evidence → hallucination → scale

**L1. "You said you used Claude Code to triage a failing test. How?"**
"I started in plan mode so nothing could change. I gave it the failing test name, the spec, and masked sample data only, and asked for a classification, product defect, test bug or spec ambiguity, with evidence: the spec rule, the failing input, expected versus actual. It found the test, read it, ran it with a short traceback, and correlated the failure with the data."

**L2. "How did you know it was a test bug and not a product defect?"**
"I didn't take the agent's word for it. I opened the spec section it cited and checked it said what the agent claimed. I reproduced the failure myself on the specific failing record. And I asked whether every failing record fit the explanation, for example whether all score-0 records carried an exclusion code. If even one didn't, that's a real product defect hiding inside the 'test bug' story."

**L3. "What if the spec is ambiguous?"**
"Then the right answer is neither 'test bug' nor 'product defect'. It's a spec gap, and I escalate it to the data-prep or model team with a concrete question and examples. I don't let the agent or myself guess, because a guess baked into a test becomes a silent requirement. Until it's clarified, I'd mark the test as a known issue with a ticket link, visible in the sign-off report, not silently skipped."

**L4. "What if the agent cited a spec section that doesn't exist or says something different?"**
"That's a hallucinated citation, and it's exactly why I verify citations. I'd reject the conclusion, note it, and re-run with a stricter instruction: quote the exact lines with file and line numbers. A quote is checkable, a paraphrase isn't. It also tells me something about the workflow: if the agent could make a claim that wasn't backed up, the process allowed unverified claims."

**L5. "How do you prevent that across the team, at scale?"**
"Build it into the skill. The triage skill's output format requires evidence fields: file path, line range, quoted text, failing input, expected, actual. Then a small deterministic check verifies the quoted text actually exists at that location before the result is accepted. I'd add known-answer fixtures, cases where we know the correct classification, and run them whenever the skill or the model changes, and track how often triage conclusions get overturned in review."

### Chain B: Data safety → boundary → prompt injection → testing guardrails

**L1. "How do you keep client data safe when using Claude Code?"**
"Data boundaries first: the agent works on masked samples or synthetic data, never raw delivery files, unless there's an approved path. CLAUDE.md states the masking rule, and permission rules deny reading raw data, env files and credentials, and deny network tools."

**L2. "Are deny rules enough?"**
"No. They match the tool call, not the effect. If Python is allowed, a script can read a denied file. Rules are guardrails for honest mistakes, not a security boundary."

**L3. "So what is the boundary?"**
"Layers enforced below the agent: a low-privilege OS user or a container that can't see raw data at all, only required mounts read-only, no credentials inside, network egress limited to the approved model endpoint, and sandboxing where available. At org level, routing through the company's cloud account and managed settings users can't override."

**L4. "What about prompt injection, say a delivery file or log containing instructions?"**
"I treat any file or log content as data, never instructions. The real protection is the same layering: if a malicious line says 'send this file to some URL', egress control means it can't reach that URL, and least privilege means there's little worth stealing. I'd also keep sensitive actions on ask, and never give a headless agent both access to sensitive data and an open network at the same time."

**L5. "How do you know your guardrails actually work?"**
"I test them like a test suite. Negative tests: try to read a raw file directly, through cat, through a Python one-liner; try curl; try editing the settings file itself. Each must be blocked or prompted. I run those checks whenever settings, the image or the Claude Code version changes, and I add a CI check that the committed settings still contain the required deny rules and that bypass mode is disabled."

### Chain C: AI-generated tests → false pass → mutation → cost → metrics

**L1. "How do you review AI-generated tests?"**
"Against the spec, not against the code. I list the behaviours that must be proven, including boundaries and negative cases, then check assertion strength, determinism, mocking, and diff scope."

**L2. "Give an example of a false pass."**
"In my lab, a validator used a strict range, 300 < score < 850, when the spec said inclusive. The existing tests checked 720 and 900, so they passed. The whole suite was green with a real boundary bug. Another one: a masking test that only checked the prefix 'ACCT-****', so it would pass even if the last four digits were wrong."

**L3. "How do you catch that systematically, not by eyeballing?"**
"Mutation testing. Introduce small faults into the product code, like changing `<=` to `<`, and check whether the suite fails. Surviving mutants show where tests are weak. Manually, it's 'revert the fix and the test must fail'. Automatically, tools like mutmut for Python do it across the codebase."

**L4. "Mutation testing on a big suite is slow. What then?"**
"Scope it. Run it on changed files only in the PR, and on critical modules, like score range, exclusion and masking logic, on a schedule rather than every commit. Prioritise boundary and comparison operators, because those are where off-by-one sign-off bugs live. And use a mutation-score threshold as a trend signal, not a hard gate, until it's stable."

**L5. "What metrics would you track for AI-generated test quality over time?"**
"Mutation score on critical modules, flake rate of generated tests versus hand-written ones, the review rejection rate for generated changes, escaped defects traced back to areas covered by generated tests, and time-to-triage for failures. If generated tests have a higher flake rate or more surviving mutants, that tells me where to tighten the skill or the review checklist."

---

## 10) Resume-linked Questions (sirf real claims; STAR skeleton)

> **Rule:** `[ ]` brackets mein apni real details bharo. **Koi number invent mat karna.** Agar metric yaad nahi, toh bolo "I don't have the exact number, but…".

### R1. "Tell me about the AI regression analyzer you built."
**Kyun poochenge:** JD mein AI tooling + critical evaluation of AI output.
- **S:** IAM aur Core teams ko regression failures triage karne mein bahut time lagta tha, kyunki data alag jagah tha: Jenkins logs, repo history, Kubernetes events. `[pain point in your words]`
- **T:** Ek tool banana jo ye signals correlate kare aur triage fast kare.
- **A:** Jenkins logs, repo history aur Kubernetes events ko correlate kiya; auto-filed Jira defects; ek chatbot interface. `[tech choices; how correlation worked; how you prevented duplicate/false Jira defects]`
- **R:** IAM + Core teams ne use kiya. `[real impact if known]`
- **Follow-ups ke liye ready raho:** "How did you validate its conclusions?" · "False defects ka kya kiya?" · "What would you do differently with Claude Code?"
- **Bridge line:** *"That's where I learned to treat AI output as a hypothesis that needs evidence. In my personal Claude Code lab I applied the same thinking: plan mode, evidence fields, and verifying every citation."*

### R2. "You built the DMP Metering suite from scratch. Walk me through it."
**Kyun:** "own UI, API and performance suites" + test design.
- **S:** Metering ke 6 services ke liye koi suite nahi thi. `[context]`
- **T:** Functional, resiliency, performance aur longevity coverage banana.
- **A:** ~250 tests, pytest + Cypress BDD. `[how you chose test layers; resiliency approach; data setup]`
- **R:** `[what it enabled: e.g., releases gated on it, defects caught — only real ones]`
- **Follow-ups:** "How did you decide what goes in BDD vs pytest?" · "How did you handle flaky tests?"

### R3. "How did you validate per-client usage aggregation with Athena over S3?"
**Kyun:** data-pipeline validation ≈ score delivery validation.
- **S/T:** Per-client usage aggregation correct hai ya nahi, ye verify karna tha.
- **A:** Athena SQL over S3 se independent aggregation, aur system output se comparison. `[reconciliation logic: counts, sums, per-client grouping, edge cases like late/duplicate events]`
- **R:** `[real outcome]`
- **Bridge:** *"It's the same pattern as delivery sign-off: independent recomputation, reconciliation against a manifest or source of truth, and masked output when reporting."*

### R4. "Tell me about smoke-on-merge and on-demand regression before promotion."
**Kyun:** sign-off gating = "before it reaches clients".
- **S/T:** Developer images promote hone se pehle quality gate chahiye tha.
- **A:** Har merge pe smoke; developer images ke liye on-demand regression, Jenkins + GitHub Actions ke through. `[how gating decisions were made; who signed off]`
- **R:** `[real outcome]`
- **Follow-ups:** "What's in smoke vs regression?" · "What happens when regression fails right before a release?"

### R5. "Tell me about the JMeter to k6 migration and the 72-hour longevity tests."
**Kyun:** performance suite ownership.
- **S/T:** `[why migrate: your real reasons]`
- **A:** JMeter → k6 migration; 72-hour longevity tests; Chaos Mesh on EKS. `[what you measured: latency percentiles, error rates, memory growth; what chaos experiments]`
- **R:** `[real findings]`
- **Follow-ups:** "How do you tell a performance regression from environment noise?" · "Longevity test mein kya dhoondh rahe the?"

### R6. "You wrote ~800 auth tests across OIDC, SAML, JWT and mTLS. How did you design them?"
**Kyun:** test design + effective assertions + negative testing.
- **A:** `[positive + negative: expired/tampered tokens, wrong audience/issuer, bad certs; how you asserted exact error codes/claims]`
- **Bridge:** *"Strong assertions there meant checking exact claims and exact error responses, not just 'status is not 200'. Same discipline I apply when reviewing AI-generated tests."*

### R7. "Tell me about a root-cause investigation during a release or hotfix."
**Kyun:** product defect vs test bug.
- **S:** `[one of the 6 releases / 2 hotfixes]`
- **T:** Failure ka root cause dhoondhna under time pressure.
- **A:** `[how you separated product defect vs test/env issue; evidence you gathered]`
- **R:** `[outcome]`

### R8. "Have you used Claude Code professionally?" (honesty question)
**Model answer:** *"Not in production at FICO. My professional AI tooling experience is the regression analyzer I built. For Claude Code, I've built a personal lab: a synthetic score-validator repo where I configured CLAUDE.md and permission rules, had the agent triage and fix a planted boundary bug, verified the new tests with a mutation check, and tested whether it would weaken tests under a vague prompt. I can walk you through exactly what I observed."*
**Kyun important:** honest framing + real demo > inflated claim. Senior interviewers turant cross-question karke pakad lete hain.

---

## 11) Quick Revision (10 lines)

1. Claude Code = model + tools + loop + permissions + context mgmt; model requests, **harness executes**.
2. Loop: gather → act → verify; watch premature success, goal substitution, rabbit-holing, scope creep.
3. Tools: Read, Edit (exact replace, read first), Write, Bash (riskiest), Grep, Glob, plus subagents.
4. Modes: default, acceptEdits, **plan (read-only)**, bypass (sandbox only); `Shift+Tab`.
5. Rules: allow/ask/deny in settings files; **deny wins**; managed > CLI > local > project > user.
6. Rules are **guardrails, not boundary**; real boundary = OS user, container, egress, sandbox.
7. Context: everything counts; context rot; one task one session; `/clear` new task, `/compact` same task.
8. AI tests: fail without the fix (mutation), strong assertions, determinism, review `git diff tests/`.
9. CI: headless `-p`, allowlist, `--max-turns`, least-privilege container; **gate on exit codes, not LLM text**.
10. Don't use on unmasked regulated data, locked-down hosts without approval, final sign-off, or deterministic jobs.

---

## Quiz Bank (voice-mode practice; answers expanded)

> **Kaise use karo:** question zor se padho, 60–90 sec mein bolo, phir model answer + "10/10 ke liye must-mention" se compare karo. Score khud do /10.

### Quiz 1. Model request karta hai, execute kaun karta hai? Ye security ke liye kyun matter karta hai?
**Model answer:** The model only emits tool-use requests; the harness checks permissions and executes them. So safety doesn't depend on the model's intentions. It depends on the harness's permission layer and, more fundamentally, on what the OS, container and network allow. A wrong or prompt-injected request is harmless if the environment won't let it succeed.
**10/10 must-mention:** model requests / harness executes · permission check before execution · real boundary is harness + OS · prompt injection angle.

### Quiz 2. `Read(./data/raw/**)` deny hai aur `Bash(python:*)` allow hai. Kya data safe hai?
**Model answer:** No. Rules match the tool call, not its effect, so a Python one-liner can open the denied file. Fix: narrow the allowlist (e.g. `Bash(python -m pytest:*)` only) and, more importantly, enforce at the OS level: run the agent as a user or in a container that can't read raw data, with egress restricted.
**10/10 must-mention:** No + reason · concrete bypass · narrow allowlist · OS/container/egress boundary.

### Quiz 3. `/clear` vs `/compact`: kab kaunsa?
**Model answer:** `/clear` wipes history (CLAUDE.md reloads) and is for starting a new, unrelated task: cheapest and cleanest. `/compact` summarises history to continue the same long task, optionally with focus instructions about what to keep; trade-off is lost detail. Rule: one task, one session.
**10/10 must-mention:** new task vs same task · CLAUDE.md reload · compact loses detail · focus instructions · context rot/cost reason.

### Quiz 4. Ek AI-generated test pass ho raha hai. Aap kaise prove karoge ki wo meaningful hai?
**Model answer:** Revert or stash the fix and run it: it must fail. Then check assertion strength (exact values, both sides of boundaries, negative cases), that it tests real behaviour and not a mock, determinism, and diff scope. At scale, mutation testing.
**10/10 must-mention:** fails without fix · assertion strength · boundaries/negatives · mocking · determinism · mutation testing.

### Quiz 5. Agent ne "fixed" bola. Aapko shak hai ki usne test hi badal diya. Kya check karoge?
**Model answer:** `git diff --stat` then the test diff: loosened/deleted assertions, skip/xfail, bigger timeouts or retries, broad try/except, changed fixtures or expected data. Demand evidence for the classification (spec rule, failing input, expected vs actual) and verify the citation myself. Prevent with a CLAUDE.md rule and `ask` on test edits.
**10/10 must-mention:** diff before summary · specific red flags · defect vs test bug with evidence · verify citation · prevention via CLAUDE.md + ask rule.

### Quiz 6. Permission modes ke naam aur ek-ek use case.
**Model answer:** default: unfamiliar repo, asks before edits/new commands. acceptEdits: trusted fast iteration, edits auto-approved, Bash still asks. plan: read-only exploration, triage, high-risk changes. bypassPermissions: only in disposable isolated sandboxes.
**10/10 must-mention:** all four · correct behaviour each · bypass only in sandbox · plan-first habit.

### Quiz 7. CI mein Claude Code use karna hai sign-off ke liye. Top 5 guardrails?
**Model answer:** (1) Gate on deterministic results (exit codes, JUnit XML), LLM only explains. (2) Explicit tool allowlist, no bypass. (3) `--max-turns`, timeouts, budget. (4) Least-privilege container, masked data only, restricted egress, no prod creds. (5) Audit trail: JSON output + commit SHA + reports; skill/prompt versioned with known-bad fixtures.
**10/10 must-mention:** deterministic gate · allowlist · caps/budget · least privilege + masking + egress · audit + known-bad fixtures.

### Quiz 8. Locked-down host pe delivery file check karni hai. Kaise karoge, aur AI kahan fit hota hai?
**Model answer:** Read-only, targeted Bash: `wc -l` vs manifest, `sha256sum` vs manifest, out-of-range count with `awk`, reason-code distribution with `cut | sort | uniq -c`, grep/tail logs, masked samples only. No agent on the host. Policy first; use Claude Code locally to write/test scripts against synthetic data (same OS image), run them myself; optionally a reviewed wrapper script as the only allowed command, open SSH denied. Report doc gaps.
**10/10 must-mention:** read-only + specific commands · no raw records · policy first · local script pattern · wrapper skill · doc gaps.

### Quiz 9. Bedrock/Vertex routing kya hai, aur kya isse raw data bhejna OK ho jaata hai?
**Model answer:** It sends Claude Code's model traffic through the company's own AWS or GCP account instead of Anthropic's API, inheriting IAM access control, audit logging, private networking, existing data agreements and cloud billing. It does not make sending raw data OK: routing answers where traffic goes, not what data is allowed to go, so masking and data boundaries still apply.
**10/10 must-mention:** company cloud account · IAM/audit/network/billing benefits · trade-offs (feature lag, model access) · routing ≠ permission.

### Quiz 10. Kab Claude Code use NAHI karoge? Kam se kam 4 reasons.
**Model answer:** Unmasked regulated data without an approved path; locked-down hosts where AI traffic isn't allowed; final ship/no-ship decision (human accountability); deterministic already-scripted jobs; output you can't verify; irreversible operations; trivial edits.
**10/10 must-mention:** regulated data first · accountability · deterministic jobs · verifiability · irreversible ops.
