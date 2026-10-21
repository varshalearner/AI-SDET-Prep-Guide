# 03 — Claude Code Skills

> Prep for: FICO Score QA sign-off role (senior). Explanation Hinglish mein, model answers/code English mein. Sab data synthetic hai.
> Note: Claude Code mere resume pe professional claim nahi hai — interview mein ise **"personal lab / learning"** ki tarah frame karna hai. Facts Claude Code docs (code.claude.com/docs/en/skills, Oct 2026) se verified hain.

---

## 1) Core Idea

Skill = ek folder jismein `SKILL.md` hota hai — YAML frontmatter (name + description) + Markdown instructions, aur optionally scripts/reference files. Claude ko sirf description pehle se dikhti hai; jab task match karta hai (ya tum `/skill-name` type karti ho), tab poora body load hota hai.
**Analogy:** Skill ek **SOP binder** hai jo shelf pe rakha hai — shelf pe sirf spine label (description) dikhta hai, binder tabhi khulta hai jab kaam aata hai, aur andar ke appendix (reference files) sirf zaroorat pe padhe jaate hain.
QA ke liye matlab: repeatable kaam (tests likhna, sign-off report) ek-command workflow ban jaata hai — har baar same rules, same format.

---

## 2) Q&A Learning — 15 Questions (basic → senior)

### Q1. Skill kya hai, aur ye problem kya solve karta hai?

**Samajh:** Jab tum har baar chat mein same checklist paste karti ho ("assertions strong rakho, synthetic data use karo, report 25 lines max…"), toh ek din bhool jaogi ya kisi teammate ka version alag hoga. Skill us procedure ko file mein freeze kar deta hai — consistency + reuse. Trade-off: skill bhi code hai — galat skill = har run mein galat output, scale pe galti multiply hoti hai.

**Model answer (60 sec):**
> "A skill in Claude Code is a folder with a `SKILL.md` file: YAML frontmatter that says what the skill does and when to use it, plus Markdown instructions Claude follows when it runs. It can also bundle scripts and reference files. Claude sees only the name and description up front; the full body loads when the task matches or when I invoke it directly with `/skill-name`. The problem it solves is drift: repeatable work like generating API tests from a spec or writing a sign-off report gets done the same way every time, by everyone, without re-pasting instructions. For a QA sign-off team that matters because the value of sign-off is consistency — the same gates, the same evidence, the same report format for every delivery. The flip side is that a skill is now a shared asset, so I treat it like test code: versioned, reviewed, and tested."

---

### Q2. SKILL.md ka structure kya hai aur skill kahan rakhte hain?

**Samajh:** Folder ka naam = default command name. `SKILL.md` ki pehli line `---` honi chahiye, warna frontmatter ignore ho jaata hai. Location decide karti hai kaun use kar paayega — personal (sirf tum, saare projects), project (repo commit → poori team), plugin (namespaced `/plugin:skill`), enterprise (org-wide managed). Same naam ho toh **enterprise > personal > project** — yeh ek classic "mere machine pe chalta hai" bug ka source hai.

**Model answer:**
> "Structure is a directory named after the skill containing `SKILL.md`. The file starts with YAML frontmatter between `---` markers — that must be the very first line — followed by Markdown instructions. Optional siblings are reference docs, templates and a `scripts/` folder. Location sets the audience: `~/.claude/skills/<name>/` is personal across all my projects, `.claude/skills/<name>/` inside the repo is the project scope that I commit so the whole team gets it, plugins distribute skills namespaced as `/plugin:skill`, and enterprise skills come from managed settings. If two have the same name, enterprise beats personal and personal beats project — so a stale personal copy can silently shadow the team's version. For team workflows like sign-off, I keep skills in the repo so they're reviewed in PRs and versioned with the tests they generate."

```bash
# macOS — project skill
mkdir -p .claude/skills/signoff-report/scripts
# personal skill
mkdir -p ~/.claude/skills/my-helper
```
```powershell
# Windows (PowerShell)
New-Item -ItemType Directory -Force .claude\skills\signoff-report\scripts
New-Item -ItemType Directory -Force "$HOME\.claude\skills\my-helper"
```

```text
.claude/skills/signoff-report/
├── SKILL.md                 # required: frontmatter + instructions
├── templates/report.md      # read only when needed
└── scripts/parse_junit.py   # executed, its code never loads into context
```

---

### Q3. Frontmatter mein kaun se fields hote hain aur kab kaunsa use karein?

**Samajh:** Technically saare fields optional hain, par `description` ke bina Claude ko pata hi nahi kab use karna hai. Field ka spelling galat (e.g. `allowed_tools`) → Claude Code use **silently ignore** karta hai, koi error nahi — yahi sabse sneaky failure mode hai. Portability trade-off: claude.ai upload / Skills API sirf 6 fields maanta hai (`name, description, license, compatibility, metadata, allowed-tools`); baaki Claude Code extensions hain.

| Field | Kab use karein |
|---|---|
| `name` | Command name (default = folder name) |
| `description` | **Kya + kab** — triggering isi se hoti hai |
| `when_to_use` | Extra trigger phrases (description ke saath 1,536 char cap share karta hai) |
| `argument-hint` / `arguments` | `/write-api-tests [spec] [framework]` jaisa autocomplete; named args |
| `disable-model-invocation: true` | Side-effect / decision wale workflows — sirf human chalaye |
| `user-invocable: false` | Background knowledge, `/` menu se hide |
| `allowed-tools` | Is turn ke liye listed tools ko bina prompt ke approve karna |
| `disallowed-tools` | Skill active ho tab kuch tools hata dena |
| `context: fork` + `agent` | Skill ko isolated subagent mein chalana |
| `paths` | Sirf matching files pe kaam karte waqt auto-load |
| `model`, `effort`, `hooks`, `shell` | Model/effort override, skill-scoped hooks, `bash`/`powershell` |

**Model answer:**
> "Only `description` is effectively required, because it's what Claude matches against to decide when to load the skill. `name` sets the slash command. Then there are control fields: `disable-model-invocation: true` for workflows with side effects or decisions, so only a human triggers them; `user-invocable: false` for background knowledge. `allowed-tools` pre-approves specific tools for the invoking turn, and `context: fork` with `agent` runs the skill in an isolated subagent. `paths` scopes auto-loading to matching files, and `argument-hint` documents arguments. Two gotchas: unknown or misspelled fields are silently ignored, and malformed YAML loads the skill with empty metadata — the slash command still works but auto-triggering dies. Also, if the skill must be portable to claude.ai or the API, I restrict myself to the six spec fields, because uploads hard-fail on anything else."

---

### Q4. Description se triggering exactly kaise hoti hai? Achhi description kaise likhein?

**Samajh:** Har session mein Claude ko ek **listing** milti hai: saare skills ke naam + descriptions. Claude user ki request ko in descriptions se semantically match karta hai aur Skill tool call karta hai. Isliye description = **routing rule**. Failure modes: (a) vague description ("Helps with testing") → kabhi trigger nahi ya galat jagah trigger; (b) description+when_to_use 1,536 chars pe truncate; (c) bahut saare skills → listing ka budget (~1% context window) overflow, kam use hone wale skills ki description drop ho jaati hai. **10x scale:** 100 skills hon toh overlapping descriptions ek doosre se compete karenge — har description mein clear boundary chahiye ("Use when… Not for…").

**Formula:** `<What it does, concrete nouns>. Use when the user <natural trigger phrases>. Not for <near-miss cases>.`

```yaml
# Weak
description: Helps with tests
# Strong
description: Generate pytest or Rest Assured API tests from an OpenAPI or endpoint spec. Use when the user asks to write, generate or add API tests for an endpoint or spec file. Not for UI tests or for fixing failing tests.
```

**Model answer:**
> "At session start Claude gets a listing of every skill's name and description. When a request comes in, Claude decides from that listing whether a skill applies and invokes it. So the description is effectively a routing rule, and I write it like one: what it does with concrete nouns, the natural phrases a user would say, and an explicit 'not for' boundary to avoid near-miss triggers. Key use case first, because description plus `when_to_use` is truncated at 1,536 characters, and with many skills the total listing has a budget — descriptions of the least-used skills get dropped first. At scale the real risk is overlap: two skills both claiming 'test reports' will fight, so I'd audit descriptions for collisions and measure trigger rates rather than guess."

---

### Q5. Arguments aur dynamic context injection kaise kaam karte hain?

**Samajh:** `$ARGUMENTS` = jo bhi `/skill` ke baad type kiya; `$0`, `$1` = positional. `` !`command` `` line skill load hone se **pehle** shell mein chalti hai aur uska output prompt mein inline ho jaata hai — Claude ko live data milta hai, guess nahi karna padta. `${CLAUDE_SKILL_DIR}` se bundled script ka path cwd se independent ho jaata hai. **Failure modes:** injected command non-zero exit kare → **poora invocation abort** (Claude skill dekhta hi nahi); expected non-zero ke liye `|| true`. Permission check fail → abort. Data discipline: `!` command output seedha context mein jaata hai — production logs ya PII wahan dump kiya toh woh model context mein chala gaya. Isliye injection mein sirf masked/summarised output.

```markdown
---
name: triage-last-run
description: Summarize failures from the latest local test run. Use when the user asks why the last run failed.
---
## Masked summary of last run
!`python3 ${CLAUDE_SKILL_DIR}/scripts/parse_junit.py reports/junit.xml || true`

Classify each failure as product defect, test bug, environment, or unknown.
```

**Model answer:**
> "Arguments come in through `$ARGUMENTS`, or positionally through `$0`, `$1`, so `/write-api-tests specs/score.yaml pytest` maps the spec path and framework. Dynamic context injection uses a line starting with `!` and a backtick command: Claude Code runs it before Claude sees the skill and inlines the output, so the instructions arrive with real data — a diff, a parsed results file. I reference bundled scripts via `${CLAUDE_SKILL_DIR}` so paths work from any working directory. Two operational points. A failing injected command aborts the entire invocation, so for checks that legitimately exit non-zero I append `|| true`. And whatever the command prints goes straight into the model's context, so in a regulated setting I only inject masked, summarised output — never raw payloads or logs."

---

### Q6. Bundled scripts vs instructions — kab kya?

**Samajh:** Rule of thumb: **jo kaam deterministic hona chahiye, woh script; jo judgment maangta hai, woh instruction.** JUnit XML count karna, masking, schema validation → script (same input = same output, testable with pytest). "Failure product defect hai ya test bug?" → Claude ka judgment, but evidence ke saath. Trade-off: script ka code context mein load nahi hota (sirf output) → token-cheap aur reliable; par script maintain karni padti hai aur locked-down host pe Python version/permissions issue ho sakta hai. Failure mode: LLM se arithmetic karwana — 2,000 tests ke counts galat ho sakte hain; sign-off report mein ek galat number = credibility khatam.

**Model answer:**
> "I split by determinism. Anything that must produce the same answer every time — parsing JUnit XML, counting pass and fail, masking identifiers, validating a response against a schema — goes into a bundled script. The script's code never enters context; only its output does, so it's cheap, and I can unit-test it like any other code. Things that need judgment — classifying a failure as product defect versus test bug, wording the risk section — stay as instructions, with a rule that every claim cites evidence from the script output. I never let the model do arithmetic on results: in a sign-off report, one wrong count destroys trust in everything else. The cost is that scripts are now dependencies — they need a pinned interpreter and must run on the restricted hosts where the results live."

---

### Q7. Progressive disclosure kya hai aur ye 10x scale pe kyun matter karta hai?

**Samajh:** Teen level ki loading:
1. **Metadata** (name + description) — har session mein hamesha context mein.
2. **SKILL.md body** — sirf invoke hone pe.
3. **Reference files / scripts** — sirf tab jab body unhe point kare aur task ko zaroorat ho; scripts execute hote hain, padhe nahi jaate.

Why: context window = limited budget; 50 skills ka poora text har turn mein = slow, mehenga, aur Claude confuse. Trade-off: agar important rule level-3 file mein chhupa diya aur body ne clearly point nahi kiya → Claude kabhi padhega hi nahi. Guideline: `SKILL.md` < 500 lines; body mein "kab kaunsi file padhni hai" likho.

**Model answer:**
> "Progressive disclosure means a skill loads in layers. Only the name and description sit in context all the time. The body of `SKILL.md` loads when the skill is invoked. Reference files and scripts load only when the body points to them and the task needs them — and scripts are executed, so only their output costs tokens. This is what lets a team have dozens of skills without paying for all of them on every turn. The design implication is that the body has to be a good index: keep it short, under about 500 lines, put must-follow rules in the body itself, and push long material like a Rest Assured template or an assertion cookbook into separate files with an explicit 'read this when…' pointer. If a critical rule lives only in a reference file, assume it will sometimes be skipped."

---

### Q8. Skill vs CLAUDE.md — kya kahan jaayega?

**Samajh:** `CLAUDE.md` = **facts jo har session mein sach hain** (build command, repo layout, "never commit secrets", "mask client IDs in any output"). Har session mein poora load hota hai → har line ka recurring token cost. Skill = **procedure jo kabhi-kabhi chahiye** (spec se tests likhna, sign-off report). Docs ka signal: jab CLAUDE.md ka koi section "fact" se "procedure" ban jaaye, use skill mein nikalo. Failure mode: 800-line CLAUDE.md → important rule noise mein dab jaata hai. Ulta failure: universal data rule ko skill mein daal diya → jab skill load nahi hua, rule bhi gaayab.

**Model answer:**
> "CLAUDE.md holds standing facts that apply to every session in the repo — how to build and run tests, directory layout, non-negotiable rules like 'mask client identifiers in anything you print'. It's always loaded, so every line is a recurring cost and it has to stay lean. A skill holds a procedure I need sometimes, like generating tests from a spec or producing a sign-off report; its body loads only when used. My test is: if it's true for every task, it's CLAUDE.md; if it's a multi-step how-to for a specific task, it's a skill. The two common mistakes are a bloated CLAUDE.md where key rules get lost, and putting a universal rule — like data masking — only inside one skill, so it silently doesn't apply when that skill isn't loaded."

---

### Q9. Skill vs slash command vs subagent — decision kaise lein?

**Samajh:** Custom slash commands ab **skills mein merge** ho chuke hain — `.claude/commands/x.md` aur `.claude/skills/x/SKILL.md` dono `/x` banate hain; skill extra deta hai (supporting files, auto-invocation, invocation control). Subagent = alag context window wala worker (apna system prompt, tools). Skill `context: fork` se subagent mein chal sakta hai — par us subagent ko tumhari conversation history **nahi** dikhti, isliye skill self-contained hona chahiye.

| Need | Choose |
|---|---|
| Short repeatable prompt, sirf main chalaun | Skill + `disable-model-invocation: true` (ya legacy command) |
| Procedure Claude khud pehchaan ke chalaaye | Skill (default) |
| Heavy kaam jo main context pollute kare (100 logs scan) | Skill with `context: fork` ya subagent |
| Alag persona/permissions wala reusable worker | Subagent (`.claude/agents/`), skills preload kar sakta hai |
| Rule jo **har baar** enforce ho, judgment nahi | Hook (Q11) |

**Model answer:**
> "Slash commands have been merged into skills, so for new work I write a skill; a `.claude/commands` file still works but can't bundle files. The real decision is skill versus subagent. A skill is instructions that run in my current context — good when the work benefits from the conversation so far. A subagent has its own context window, system prompt and tool set — good for noisy, heavy work like scanning hundreds of failure logs, where I only want the conclusion back. You can combine them: `context: fork` runs a skill as the task for a subagent, but that subagent doesn't see my conversation, so the skill must be self-contained. And if something must happen every single time — not by judgment — that's a hook, not any of these."

---

### Q10. Invocation control aur safety — kaunsi skill Claude ko khud chalaane deni chahiye?

**Samajh:** Default mein Claude aur tum dono invoke kar sakte ho. Jo skill **side effect** kare (Jira defect file karna, report publish karna, deploy) ya **decision** le (GO/NO-GO) → `disable-model-invocation: true`. Bahut log `allowed-tools` ko sandbox samajhte hain — **galat**: woh sirf us turn ke liye listed tools ko bina prompt approve karta hai; baaki tools ab bhi callable hain (permission settings ke hisaab se). Restrict karna ho toh `disallowed-tools` ya permission deny rules. Security: repo ki skill khud ko broad `allowed-tools` de sakti hai, aur workspace trust isse gate nahi karta — unknown repo ki skills review karo.

**Model answer:**
> "By default both I and Claude can invoke a skill. Anything with side effects or that represents a decision — filing defects, publishing a report, a GO/NO-GO call — I mark `disable-model-invocation: true`, so it only runs when a human types the command. I'm careful with `allowed-tools`: it pre-approves the listed tools for the invoking turn; it does not restrict Claude to them. To actually remove tools I use `disallowed-tools` or deny rules in permissions. I also review `allowed-tools` in any repository's skills before running Claude Code there, because a project skill can grant itself broad access. For a sign-off context I'd pre-approve only narrow, exact patterns — like the one parsing script via `${CLAUDE_SKILL_DIR}` — rather than `Bash(*)`."

---

### Q11. Skill session mein kitni der tak "yaad" rehta hai? Claude beech mein skill follow karna kyun chhod deta hai?

**Samajh:** Invoke hone pe rendered SKILL.md ek message ban ke conversation mein **reh jaata hai**; file dobara nahi padhi jaati. Isliye instructions "standing rules" ki tarah likho ("Run tests after every edit"), one-time steps ki tarah nahi. Auto-compaction ke baad har skill ke sirf pehle ~5,000 tokens re-attach hote hain (sab skills ka combined ~25,000 budget) → **sabse important rules top pe**. Jo rule kabhi skip nahi hona chahiye (e.g. output mein unmasked ID na jaaye) → skill ke `hooks` frontmatter ya project hooks mein daalo — hook har event pe chalta hai, judgment nahi.

**Model answer:**
> "Once invoked, the rendered skill stays in the conversation as a message; Claude Code doesn't re-read the file later. So I write guidance as standing rules that apply to the whole task, not one-off steps. After auto-compaction only the first portion of each invoked skill is re-attached, within a shared budget, so critical rules go at the top, and re-invoking the skill restores it fully. If Claude drifts from a judgment-style rule, I reword it to cover the whole task. If it's a rule that must hold every time — for example, never write unmasked identifiers into a report file — I don't rely on the model at all; I enforce it with a hook, which runs on every matching event regardless of whether Claude is following the skill."

---

### Q12. Skill ko test kaise karte hain?

**Samajh:** "Skill trigger ho gaya" ≠ "skill kaam kar raha hai." Do alag cheezein measure karo:
1. **Trigger accuracy** — should-trigger prompts pe chala? should-NOT-trigger (near-miss) pe ruka?
2. **Output quality** — jab chala, output expected tha? (assertions on the output)

Method = **baseline comparison**: same realistic prompts, **fresh session**, skill ON vs OFF (`/skills` menu → `skillOverrides: "off"`). Fresh session isliye kyunki authoring ka bacha context gaps chhupa deta hai. Tools: `skill-creator` plugin (evals/evals.json, isolated subagent runs, grading, with/without benchmark, blind A/B between versions, description tuning); plugin skills ke liye `claude plugin eval` (CI gate). Trade-off: LLM non-deterministic → ek run pe judge mat karo, har prompt 3–5 baar chalao aur pass-rate dekho.

```json
// .claude/skills/write-api-tests/evals/evals.json  (shape illustrative — skill-creator writes the real one)
[
  {"prompt": "write api tests for specs/score-api.yaml", "should_trigger": true,
   "expect": ["tests/api/test_score_requests.py exists",
              "a test asserts 400 for unknown product",
              "no test uses `status_code < 500`"]},
  {"prompt": "why is my cypress login test flaky?", "should_trigger": false}
]
```

**Model answer:**
> "I test two things separately: does it trigger on the right prompts and stay quiet on near-misses, and when it runs, is the output correct. The method is a baseline comparison — a small set of realistic prompts, each run in a fresh session with the skill on and again with it turned off, because leftover authoring context hides gaps. Since outputs are non-deterministic, I run each prompt several times and look at pass rates, not a single result. The skill-creator plugin automates this: it stores cases in `evals/evals.json`, runs each in an isolated subagent, grades assertions with evidence, benchmarks with versus without the skill including token and time cost, and can do a blind A/B between two versions before I commit an edit. For skills shipped in a plugin, `claude plugin eval` can gate CI on a threshold."

---

### Q13. Skill ne tests generate kiye, sab green hain. Kaise pata ki woh sach mein kuch validate karte hain?

**Samajh:** Yeh JD ka core hai — *critical evaluation of AI output*. Green ≠ correct. Common weak patterns: `assert resp.status_code < 500`, `assert resp.json()`, sirf status check (body nahi), expected value server se copy (tautology), `try/except: pass`, test jo kabhi fail ho hi nahi sakta. Check karne ke tareeke: (1) har test ko spec rule se map karo (coverage table); (2) **planted-bug / mutation check** — server ya expected value thoda badlo, test fail hona chahiye; agar phir bhi green → false pass; (3) assertion density / specificity review; (4) "spec se derive kiya ya current behaviour se?" — agar server behaviour se derive kiya toh bug ko hi expected bana diya. Fix **skill mein** karo (rule add + eval case), sirf generated file mein nahi — warna har agla run wahi galti karega.

```python
# False pass (weak)
def test_create_score_request():
    r = requests.post(f"{BASE}/v1/score-requests", json=payload)
    assert r.status_code < 500          # passes on 400, 404, 201...

# Strong
def test_create_score_request_valid_returns_201_with_score_in_range():
    r = requests.post(f"{BASE}/v1/score-requests", json=payload, timeout=5)
    assert r.status_code == 201
    body = r.json()
    assert body["request_id"] == payload["request_id"]
    assert body["status"] == "ACCEPTED"
    assert isinstance(body["score"], int) and 300 <= body["score"] <= 850
```

**Model answer:**
> "Green tells me nothing on its own. First I map every generated test to a spec rule and look for gaps and for tests derived from the server's current behaviour rather than the spec — that pattern turns a bug into an expected value. Second I read the assertions: status-only checks, `< 500` ranges, 'response is truthy', or broad try/except are false-pass risks. Third, the decisive check: I make the tests prove they can fail — plant a bug in a mock, flip an expected value, or run a mutation tool — and any test that stays green is not testing anything. Then I fix it at the source: I add a rule to the skill, like 'assert status, schema and key values', and add an eval case that fails on the weak pattern, so the next generation doesn't repeat it."

---

### Q14. Skill fail ho raha hai — debug ka systematic ladder kya hai?

**Samajh:** Pehle decide karo **kis layer pe** fail hai: load → trigger → execute → output.

| Symptom | Check |
|---|---|
| `/skill-name` bhi kaam nahi karta | Path/location sahi? Folder naam mein invalid char? Same naam ka higher-precedence skill (personal ne project shadow kiya)? |
| `/skill-name` chalta hai, auto-trigger nahi | Frontmatter YAML malformed (skill empty metadata ke saath load hota hai) → `claude --debug`, `claude plugin validate .claude/skills`; `---` first line? Description vague/truncated? Listing budget overflow? `disable-model-invocation` set? |
| Galat jagah trigger | Description too broad → "Not for…" add karo, ya manual-only karo |
| Invocation abort "Shell command failed" | `!` command non-zero exit → `\|\| true`; Windows pe bash nahi (`shell: powershell`); permission deny |
| Chalta hai par output galat | Instructions ambiguous; rule level-3 file mein chhupa; compaction ke baad drift → re-invoke; eval case add karo |
| Teammate pe fail | `python3` vs `python`, hardcoded path (use `${CLAUDE_SKILL_DIR}`), personal copy shadowing |

```bash
# macOS
claude --debug                               # parse errors, refused names, listing-budget warnings
claude plugin validate .claude/skills        # find SKILL.md whose frontmatter doesn't parse
# inside Claude Code
/skills          # is it listed? which source? on/off?
/context         # how much the skill listing costs
```
```powershell
# Windows — same CLI
claude --debug
claude plugin validate .claude\skills
```

**Model answer:**
> "I localise the failure layer first: does it load, does it trigger, does it execute, is the output right. If even `/name` doesn't work, it's location, an invalid name, or a same-named skill with higher precedence shadowing it. If `/name` works but auto-trigger doesn't, I suspect the frontmatter — malformed YAML loads the skill with empty metadata — so I run `claude --debug` and `claude plugin validate` on the skills folder, then look at description wording and whether the listing budget dropped it. If invocation aborts, an injected shell command exited non-zero or was denied by permissions. If it runs but output is wrong, that's an instruction problem: ambiguous wording, a rule buried in a reference file, or drift after compaction. Every fixed bug becomes an eval case so it can't regress."

---

### Q15. Team mein skills ko version, review aur maintain kaise karein — 10x scale pe?

**Samajh:** Skill = **production code jo tests banata hai**, isliye wahi discipline: repo mein `.claude/skills/`, PR review, CODEOWNERS, har change ke saath evals chalna, changelog. Breaking change (output format badla jo downstream report parser use karta hai) → version bump + announce. Scale problems: (a) description collisions, (b) listing budget — unused skills context kha rahe → `/skill-doctor` se usage vs cost dekh ke retire karo; (c) personal forks drift → enterprise/plugin distribution; (d) owner chala gaya → orphan skill. Distribution choice: single repo → project skills; multiple repos/teams → **plugin** (namespaced, versioned); org-wide mandatory → managed settings. Delivery-quality metrics se jodo: skill ka value measure karo (e.g. generated tests mein escaped-defect rate, sign-off report time) warna skills sirf grow karte jaate hain.

```yaml
---
name: signoff-report
description: ...
metadata:
  version: 1.3.0
  owner: qa-signoff
  changelog: "1.3.0 — BLOCKED verdict when zero tests ran"
---
```
(`metadata` free-form hai — Claude Code use ignore karta hai, tumhari tooling padh sakti hai.)

**Model answer:**
> "I treat skills as production code because they generate the artifacts we sign off on. They live in the repo under `.claude/skills`, changes go through PR review with an owner in CODEOWNERS, and every change runs the skill's eval set so we see trigger and output regressions before merging. I keep a version and changelog in the `metadata` field, and bump on breaking changes like a report format other tooling parses. Once skills are shared across repos, I package them as a plugin so teams get one versioned, namespaced copy instead of drifting personal forks. At ten times the number of skills the problems are collisions between descriptions and context cost, so I periodically review usage with `/skill-doctor`, retire unused ones, and require each skill to have an owner and a measurable reason to exist."

---

## 3) Mini Lab — `write-api-tests` + `signoff-report`

**Goal:** Synthetic "score request" API (with a **planted bug**) → skill se tests generate → run → doosri skill se masked sign-off report. Pass criterion: generated tests **planted bug pakdein**, aur report **NO-GO** de.
Prereq: Python 3.10+, Claude Code installed & logged in.

### Step 1 — Project + mock API + spec

```bash
# macOS
mkdir -p ~/skills-lab/{specs,tests/api,reports} && cd ~/skills-lab
python3 -m venv .venv && source .venv/bin/activate
pip install pytest requests
```
```powershell
# Windows (PowerShell)
New-Item -ItemType Directory -Force "$HOME\skills-lab\specs","$HOME\skills-lab\tests\api","$HOME\skills-lab\reports"
cd "$HOME\skills-lab"
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install pytest requests
```

`mock_api.py` (stdlib only, synthetic):
```python
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

ALLOWED_PRODUCTS = {"SCORE_8", "SCORE_10"}  # spec says others -> 400

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.path != "/v1/score-requests":
            return self._send(404, {"error": "not_found"})
        try:
            raw = self.rfile.read(int(self.headers.get("Content-Length", 0)))
            body = json.loads(raw or b"{}")
        except json.JSONDecodeError:
            return self._send(400, {"error": "invalid_json"})
        for field in ("request_id", "client_id", "consumer_ref", "product"):
            if field not in body:
                return self._send(400, {"error": "missing_field", "field": field})
        # PLANTED BUG: unknown product is accepted instead of rejected with 400
        return self._send(201, {"request_id": body["request_id"], "status": "ACCEPTED", "score": 712})

    def log_message(self, *args):
        pass

if __name__ == "__main__":
    print("mock API on http://127.0.0.1:8099")
    HTTPServer(("127.0.0.1", 8099), Handler).serve_forever()
```

`specs/score-api.yaml`:
```yaml
openapi: 3.0.3
info: {title: Synthetic Score Request API, version: 1.0.0}
paths:
  /v1/score-requests:
    post:
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [request_id, client_id, consumer_ref, product]
              properties:
                request_id:   {type: string, format: uuid}
                client_id:    {type: string, example: "CLI-0001"}
                consumer_ref: {type: string, example: "CON-0001"}
                product:      {type: string, enum: [SCORE_8, SCORE_10]}
      responses:
        "201":
          description: Accepted
          content:
            application/json:
              schema:
                type: object
                required: [request_id, status, score]
                properties:
                  request_id: {type: string}
                  status:     {type: string, enum: [ACCEPTED]}
                  score:      {type: integer, minimum: 300, maximum: 850}
        "400": {description: Missing field, invalid JSON, or product not in enum}
```

### Step 2 — Skill 1: `write-api-tests`

```bash
# macOS
mkdir -p .claude/skills/write-api-tests/reference
```
```powershell
# Windows
New-Item -ItemType Directory -Force .claude\skills\write-api-tests\reference
```

`.claude/skills/write-api-tests/SKILL.md`:
```markdown
---
name: write-api-tests
description: Generate pytest or Rest Assured API tests from an OpenAPI or endpoint spec. Use when the user asks to write, generate or add API tests for an endpoint or spec file. Not for UI tests or for fixing failing tests.
argument-hint: [spec-path] [pytest|restassured]
allowed-tools: Read Grep Glob
---

# Write API tests from a spec

Spec: `$0`. Framework: `$1` (default `pytest`).

## Standing rules (apply to every test)
1. Derive expected behaviour from the SPEC, never from what the server currently returns.
2. For each operation cover: happy path; each required field missing; each enum with an invalid value; type/boundary violations; invalid JSON body.
3. Assert status code AND response body: required keys, types, enum values, ranges, and echoed inputs. Forbidden: `status_code < 500`, bare `assert r.json()`, try/except that swallows errors.
4. One behaviour per test. Name: `test_<resource>_<condition>_<expected>`.
5. Base URL from env `API_BASE_URL` (default `http://127.0.0.1:8099`). Synthetic data only (`CLI-0001`, `CON-0001`, `uuid4()`); no real identifiers, hosts or tokens.
6. Tests must be independent and order-free; always pass `timeout=5`.
7. Do not edit a test to make it pass. If a test fails, report it as: suspected product defect / test bug / unknown — with the evidence.

## Output
- pytest: `tests/api/test_<resource>.py`. Rest Assured: see `reference/restassured-template.md`.
- Finish with a table: spec rule → test name, then a list of spec ambiguities you found.
- For assertion patterns, read `reference/assertion-patterns.md` before writing.
```

`.claude/skills/write-api-tests/reference/assertion-patterns.md`:
```markdown
# Assertion patterns
- Success: exact status, required keys present, types, enums, numeric range, echoed request_id.
- Validation error: exact 4xx status AND error body identifies the problem (e.g. `field`).
- Never assert only on status; never compare against a value copied from a live response.
- Parametrize missing-field and invalid-enum cases with `pytest.mark.parametrize`.
```

`.claude/skills/write-api-tests/reference/restassured-template.md`:
````markdown
```java
given().baseUri(System.getenv().getOrDefault("API_BASE_URL", "http://127.0.0.1:8099"))
  .contentType(ContentType.JSON).body(payload)
.when().post("/v1/score-requests")
.then().statusCode(201)
  .body("status", equalTo("ACCEPTED"))
  .body("score", allOf(greaterThanOrEqualTo(300), lessThanOrEqualTo(850)));
```
````

### Step 3 — Skill 2: `signoff-report`

```bash
# macOS
mkdir -p .claude/skills/signoff-report/{scripts,templates}
```
```powershell
# Windows
New-Item -ItemType Directory -Force .claude\skills\signoff-report\scripts, .claude\skills\signoff-report\templates
```

`.claude/skills/signoff-report/SKILL.md`:
```markdown
---
name: signoff-report
description: Turn JUnit XML test results into a concise, masked QA sign-off report with a GO / NO-GO / BLOCKED verdict. Use when the user asks for a sign-off, release-readiness summary or test results report.
argument-hint: [junit-xml-path ...]
disable-model-invocation: true
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/parse_junit.py *) Read
---

# QA sign-off report

## Standing rules
- Data comes ONLY from the parser's JSON. Never state a number that is not in it.
- Do not open raw logs or payloads unless the user asks. Anything you quote must stay masked.
- Verdict: BLOCKED if total == 0. NO-GO if failed + errors > 0 (unless the user gives an approved waiver ID). GO otherwise.
- Classify every failure: Product defect / Test bug / Environment / Unknown, each with one line of evidence. Prefer "Unknown" to guessing.
- Max 25 lines. Follow `templates/report.md` exactly.

## Steps
1. Run `python3 ${CLAUDE_SKILL_DIR}/scripts/parse_junit.py $ARGUMENTS` (on Windows without `python3`, use `python`).
2. Fill `${CLAUDE_SKILL_DIR}/templates/report.md` and save it as `reports/signoff.md`.
```

`.claude/skills/signoff-report/scripts/parse_junit.py`:
```python
#!/usr/bin/env python3
"""Summarise JUnit XML into masked JSON. Deterministic; no network."""
import json
import re
import sys
import xml.etree.ElementTree as ET

MASKS = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "<EMAIL>"),
    (re.compile(r"\b(?:CLI|CON)-\d+\b"), "<ID>"),
    (re.compile(r"\b\d{6,}\b"), "<NUM>"),
]

def mask(text: str) -> str:
    for rx, repl in MASKS:
        text = rx.sub(repl, text)
    return text

def summarise(paths):
    s = {"total": 0, "passed": 0, "failed": 0, "errors": 0, "skipped": 0,
         "duration_s": 0.0, "failures": []}
    for path in paths:
        for case in ET.parse(path).getroot().iter("testcase"):
            s["total"] += 1
            s["duration_s"] += float(case.get("time") or 0)
            name = mask(f'{case.get("classname", "")}::{case.get("name", "")}')
            bad = case.find("failure")
            if bad is None:
                bad = case.find("error")
            if bad is not None:
                s["failed" if bad.tag == "failure" else "errors"] += 1
                lines = (bad.get("message") or bad.text or "").strip().splitlines()
                s["failures"].append({"test": name, "kind": bad.tag,
                                      "message": mask(lines[0] if lines else "")[:200]})
            elif case.find("skipped") is not None:
                s["skipped"] += 1
            else:
                s["passed"] += 1
    s["duration_s"] = round(s["duration_s"], 2)
    return s

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: parse_junit.py <junit.xml> [more.xml ...]")
    print(json.dumps(summarise(sys.argv[1:]), indent=2))
```

`.claude/skills/signoff-report/templates/report.md`:
```markdown
# QA Sign-off — <delivery name>
**Verdict:** <GO | NO-GO | BLOCKED>  **Date:** <YYYY-MM-DD>
**Results:** <passed>/<total> passed · <failed> failed · <errors> errors · <skipped> skipped · <duration_s>s

## Blocking issues
| Test | Class | Evidence (masked) |
|---|---|---|

## Risks / gaps
- <coverage gaps, skipped tests, spec ambiguities>

## Next actions
- <owner — action>
```

Script ko pehle khud unit-check karo (skill ke bahar) — deterministic part ka trust isi se aata hai.

### Step 4 — Generate + run tests

Terminal 1 (mock server):
```bash
python3 mock_api.py        # macOS
```
```powershell
python mock_api.py         # Windows
```

Terminal 2:
```bash
claude
> /write-api-tests specs/score-api.yaml pytest
# review the generated file against Q13 before running anything
> /exit
pytest tests/api -q --junitxml=reports/junit.xml
```
(Windows: same commands in the activated venv.)

**Expected output (approx — counts depend on the generated tests):**
```text
.......F...                                                       [100%]
FAILED tests/api/test_score_requests.py::test_score_requests_invalid_product_returns_400
  - assert 201 == 400
1 failed, 10 passed in 0.4s
```
✅ Agar **ek bhi failure nahi** aaya → generated tests weak hain (invalid-enum case missing ya assertion weak). Yeh lab ka asli lesson hai: skill ki rule 2/3 tighten karo, eval case add karo, regenerate.

### Step 5 — Trigger test (fresh session, ON vs OFF)

```bash
claude      # fresh session
> add api tests for the score requests spec          # should trigger write-api-tests
> why does my cypress login test keep timing out?    # should NOT trigger
> give me a sign-off for reports/junit.xml           # should NOT auto-run (manual-only skill)
> /skills   # turn write-api-tests OFF, repeat prompt 1 in a new session, compare output quality
```
Har should-trigger prompt 3 baar chalao, hit-rate note karo. Description badlo → dobara chalao.

### Step 6 — Sign-off report

```bash
claude
> /signoff-report reports/junit.xml
```
**Expected `reports/signoff.md` (approx):**
```markdown
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
```
Bonus check: parser ke JSON mein `CLI-0001` jaisi koi value nahi dikhni chahiye — `<ID>` dikhna chahiye.

---

## 4) Special Questions (senior interviewer traps)

### S1. Trap — "Maine `allowed-tools: Read Grep` likha hai, toh meri skill files edit nahi kar sakti, right?"

**Samajh:** Galat. `allowed-tools` **pre-approval** hai, restriction nahi. Write/Bash ab bhi available hain — bas unke liye normal permission prompt aayega (ya auto mode mein classifier decide karega).

**Model answer:**
> "No — that's a common misreading. `allowed-tools` pre-approves those tools for the invoking turn so they run without a prompt; every other tool is still callable under the normal permission settings. If I need the skill to be genuinely read-only, I add `disallowed-tools` for Edit and Write, or a deny rule in permissions, and for a hard guarantee a hook. I'd also point out the grant clears on the next user message, even though the skill text stays in context."

### S2. Cross-question chain (3 levels)

**L1 — "Your `write-api-tests` skill generated 40 tests for a new delivery type, all green. Do you sign off?"**
> "Not yet. Green only means the tests didn't fail. I first map each test to a spec rule to see coverage, and read assertions for false-pass patterns. Sign-off needs evidence that the tests can detect a defect, not just that they ran."

**L2 — "How do you prove they can detect a defect, quickly, before the release window?"**
> "Cheapest first: a planted-bug run against a mock or stub — flip one behaviour per spec rule, like accepting an invalid enum — and confirm the matching test fails. If I have more time, a mutation run on the expected values or on the client mapping layer. Any test that stays green under a planted bug is either deleted or rewritten before it counts toward sign-off."

**L3 — "The planted-bug run shows a third of the tests survive. Ten people use this skill. What do you change, and how do you know the fix worked?"**
> "I fix the source, not the 40 files. I classify the surviving tests — usually status-only assertions or expectations copied from live responses — and turn each pattern into an explicit rule in the skill plus an eval case that fails on that pattern. Then I run the skill's eval set before and after, blind A/B if possible, across several runs, and compare the planted-bug kill rate. The change goes through PR review with the eval results attached, I bump the skill version, and I tell the users which previously generated suites should be regenerated."

### S3. Scenario — "Results ek locked-down Linux host pe hain (SSH only, no internet, regulated data). Tumhari sign-off skill wahan kaise chalegi?"

**Samajh:** Point = data boundary. Raw results/payloads ko model context tak le jaana hi risk hai. Deterministic script host pe chale, sirf masked summary bahar aaye. `!` injection mein raw data kabhi nahi.

**Model answer:**
> "I keep the data boundary on the host. The parsing and masking step is a plain stdlib Python script with no network dependency, so I copy it to the host and run it there over SSH; only the masked JSON summary leaves the box — never raw XML, logs or payloads. The skill on my side consumes that summary only, its rules forbid opening raw artifacts, and it never uses dynamic injection to cat files from the host into context. I'd verify the script's masking with unit tests that include synthetic identifier formats, and default to masking even for internal-only reports. If the org enforces it, `disableSkillShellExecution` in managed settings stops skills from running injected shell commands at all. Where the procedure is unclear in the shipped docs for that host, I'd document the gap rather than improvise."

```bash
# macOS / Linux client — run parser on host, bring back only masked JSON
scp .claude/skills/signoff-report/scripts/parse_junit.py qa@host-masked:/tmp/
ssh qa@host-masked 'python3 /tmp/parse_junit.py /data/run-123/junit.xml' > reports/summary.json
```
```powershell
# Windows (built-in OpenSSH)
scp .claude\skills\signoff-report\scripts\parse_junit.py qa@host-masked:/tmp/
ssh qa@host-masked "python3 /tmp/parse_junit.py /data/run-123/junit.xml" > reports\summary.json
```

### S4. Trap — "Skill mere laptop pe perfectly chalti hai, teammate (Windows) pe 'Shell command failed' aata hai, aur doosre teammate pe purana behaviour dikhta hai. Kyun?"

**Model answer:**
> "Two different bugs. The Windows one is environmental: an injected `!` command or the script call uses `python3` or bash syntax that doesn't exist there — Claude Code needs Git Bash for bash commands, otherwise you set `shell: powershell` or make the script call portable — and any non-zero exit aborts the invocation. The 'old behaviour' one is precedence: that teammate probably has a personal copy with the same name in `~/.claude/skills`, and personal beats project, so it silently shadows the repo version. I'd check with `/skills`, which shows the source, remove the stale copy, and prevent recurrence by using `${CLAUDE_SKILL_DIR}` for paths, testing the skill on both OSes in CI, and distributing shared skills as a versioned plugin."

### S5. Resume-linked STAR skeleton — "Tell me about a time you automated QA triage. How would you do it with Claude Code skills?"

*(Sirf real claims. Koi metric invent nahi — agar tumhare paas measured number hai toh hi bolna.)*

- **S:** At FICO on the Decision Management Platform, I work across IAM and Core with roughly 3,000 automated tests running through Jenkins and GitHub Actions — smoke on every merge and on-demand regression for developer images before promotion.
- **T:** When regressions failed, figuring out *why* meant manually correlating Jenkins logs with recent repo changes and Kubernetes events before anyone could file a defect.
- **A:** I built an AI regression analyzer that correlates Jenkins logs, repository history and Kubernetes events, auto-files Jira defects, and has a chatbot interface for questions about failures.
- **R:** It's used by both the IAM and Core teams. *(Add your own measured impact here only if you have it.)*
- **Bridge (personal lab, not a professional claim):** "In my own lab with Claude Code, I'd express the repeatable parts as skills: a deterministic, masking parser script for results; a `triage` skill with `context: fork` so log-heavy analysis doesn't flood the main context; and a manual-only `file-defect` skill with `disable-model-invocation: true`, because creating tickets is a side effect a human should trigger. I'd evaluate the triage skill against past failures where we already know the root cause."

---

## 5) 1-min Revision

- **SKILL.md** = frontmatter (`name`, **`description` = routing rule**) + instructions; `---` first line; misspelled field = silently ignored.
- **Location precedence:** enterprise > personal > project; plugins namespaced `/plugin:skill`; commands merged into skills.
- **Progressive disclosure:** description always → body on invoke → files/scripts on demand; SKILL.md < 500 lines, critical rules at top.
- **Script for determinism** (counts, masking), **instructions for judgment**; `${CLAUDE_SKILL_DIR}`; `!`cmd`` fails → whole invocation aborts.
- **CLAUDE.md = always-true facts; skill = sometimes-needed procedure; subagent/`context: fork` = isolated heavy work; hook = must-happen-every-time.**
- **`disable-model-invocation`** for side effects/decisions; **`allowed-tools` pre-approves, doesn't restrict.**
- **Test = trigger accuracy + output quality**, fresh session, ON vs OFF, multiple runs; skill-creator evals / `claude plugin eval`.
- **Green ≠ correct:** spec mapping, weak-assertion review, planted-bug/mutation check; fix the skill + add eval; mask by default.
