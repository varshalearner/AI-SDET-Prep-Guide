# 04 — Agents & Subagents

> FICO Score QA sign-off role — senior interview prep (Claude Code = personal lab / learning, not a resume claim)
> Explanation: Hinglish · Code / commands / model answers: English · All data synthetic, sensitive values masked
> Format: Core Idea → 15 Q&A (basic → senior) → Mini Lab → 5 Special Questions → 1-min Revision

---

## 1) Core Idea

**Subagent** = ek alag Claude instance jise main session ek specific kaam deta hai. Uska **apna fresh context window, apna system prompt, apne allowed tools** hote hain, aur kaam khatam karke woh sirf **ek final summary** wapas bhejta hai.
**Analogy:** Tum QA lead ho. Tum 2,000-line Jenkins log khud nahi padhti — ek teammate ko do: "padh ke batao kaunsa failure product bug hai." Woh poora log padhta hai, tumhe 5 lines ka verdict deta hai. Tumhara dimaag (context) saaf rehta hai.
Senior angle: subagent ka asli fayda speed nahi, **isolation** hai — saaf context, kam permissions, aur ek **independent reviewer** jo writer ki galtiyon se "infected" nahi hai.

---

## 2) Q&A Learning — 15 Questions

### Q1. What is a subagent, and how is it different from just asking Claude in the main chat?

**(a) Samajh:** Main chat mein sab kuch ek hi context mein jama hota hai — har file read, har log, har galat attempt. Subagent ek **side-room** hai: main Claude ek prompt likh ke task delegate karta hai, subagent apne room mein kaam karta hai, aur sirf result bahar aata hai. Trade-off: subagent ko tumhari chat history **nahi** dikhti, isliye delegation prompt weak hua toh woh galat cheez solve karega.

**(b) Model answer:**
> "A subagent is a separate Claude instance that the main session spawns for a specific task. It starts with its own context window, its own system prompt and its own tool allow-list, does the work, and returns only a final message to the parent. The difference from doing it in the main chat is isolation. If I ask the main session to read a 5,000-line Jenkins console log, all of that lands in my working context and pushes out the things I actually care about — the spec, the decisions we made, the test plan. If a subagent reads it, the log stays in the subagent's context and I get back a ten-line classification. The cost of that isolation is that the subagent doesn't see my conversation, so the quality of the delegation prompt matters a lot — whatever it needs to know, I have to hand it explicitly."

---

### Q2. What exactly goes into a subagent's context, and what comes back? Why does that matter?

**(a) Samajh:** **Andar jaata hai:** subagent ka system prompt (uski definition file ki body), main agent ka likha hua task prompt, aur environment/project basics (jaise project instructions — exact list apne version ke docs ke "What loads at startup" section mein verify karna). **Andar NAHI jaata:** parent ki conversation history. **Bahar aata hai:** sirf final message — beech ke tool calls, file reads, galat attempts nahi. Failure mode: subagent ne kuch galat assume kiya aur summary mein confident likh diya — parent ke paas use check karne ka raw evidence nahi hota, jab tak tum summary mein evidence maango nahi.

**(b) Model answer:**
> "Going in: the subagent's own system prompt from its definition file, the task prompt the parent writes when it delegates, and the standard project context. Not going in: the parent's conversation history. Coming back: only the subagent's final message — none of its intermediate tool calls or file reads land in the parent's context. That design is why subagents keep the main session clean, but it creates a trust problem: the parent only sees a summary. So in every subagent I write, the output contract requires evidence — a file and line, a log line, a command that was run and its result — so the parent, or I, can verify a claim instead of trusting it. A summary without evidence is just an opinion."

---

### Q3. How do you define a custom subagent? Walk me through the file.

**(a) Samajh:** Ek markdown file with YAML frontmatter. **Frontmatter = config** (name, description, tools, model); **body = system prompt**. Project-level file git mein jaati hai aur team share karti hai; user-level sirf tumhare liye. Same name dono jagah ho toh project-level jeetta hai. Galti: `tools` field chhod dena → subagent ko parent ke **saare tools** (MCP bhi) mil jaate hain.

| Scope | macOS | Windows | Use |
|---|---|---|---|
| Project | `<repo>/.claude/agents/<name>.md` | `<repo>\.claude\agents\<name>.md` | Team-shared, versioned, PR-reviewed |
| User | `~/.claude/agents/<name>.md` | `%USERPROFILE%\.claude\agents\<name>.md` | Personal, all projects |

```markdown
---
name: failure-triager            # lowercase-hyphen; how you refer to it
description: Use PROACTIVELY after any failed test run. Classifies each failure as PRODUCT_DEFECT, TEST_BUG, FLAKY or ENV with evidence. Never edits files.
tools: Read, Grep, Glob, Bash    # allow-list; omit = inherit ALL parent tools
model: sonnet                    # sonnet | opus | haiku | inherit | full model ID
---
You are a test-failure triage specialist for a QA sign-off pipeline.
<role, steps, rules, output format...>
```

Other fields exist (e.g. `disallowedTools`, `permissionMode`, `skills`, `hooks`, `mcpServers`, `memory`, `effort`) — exact list aur allowed values apne Claude Code version ke docs "Frontmatter reference" mein check karna. `/agents` command se list / create / edit kar sakte ho.

**(b) Model answer:**
> "A subagent is a Markdown file with YAML frontmatter. Project-scoped ones live in `.claude/agents/` and get committed, so the whole team gets the same triager and the same reviewer, and changes go through PR review like any test code. User-scoped ones live in `~/.claude/agents/`. The frontmatter has the name, a description — which is what Claude uses to decide when to delegate — a tools allow-list and a model. The body is the system prompt: the role, the steps, the hard rules and, most importantly, the output format. The one field I never skip is `tools`, because if you omit it the subagent inherits every tool the parent has, including write access and any MCP servers. I treat agent definitions as test infrastructure: versioned, reviewed, and tested against known inputs."

---

### Q4. How does Claude decide to use a subagent? Can you force it?

**(a) Samajh:** **Automatic delegation** `description` field padh ke hoti hai — yahi uska "trigger". Vague description ("helps with tests") = kabhi trigger nahi hoga ya galat jagah hoga. "Use PROACTIVELY after…" jaisa phrase automatic use badhata hai. **Explicit:** prompt mein naam lo — "Use the failure-triager subagent on reports/run1.txt". Built-in subagents bhi hote hain (jaise read-only **Explore** for codebase search, **Plan**, aur **general-purpose**) — custom tab banao jab repeatable role + fixed rules chahiye. Trade-off: automatic = convenient but non-deterministic; sign-off pipeline mein **explicit** better.

**(b) Model answer:**
> "Two ways. Automatic delegation is driven by the description field — Claude reads the descriptions of available subagents and matches them to the task, so the description is effectively a routing rule. I write it as a trigger condition plus a boundary: 'Use after any failed test run; classifies failures; never edits files.' Explicit invocation is just naming the agent in the request, which is what I'd use in a sign-off workflow, because I want the same step to run every time rather than depend on the model's routing judgment. Claude Code also ships built-in subagents, like a read-only Explore agent for searching a codebase. I build a custom one only when the role repeats and needs fixed rules — a triage taxonomy, a review checklist, a masking rule — that I don't want to re-type in every prompt."

---

### Q5. Why restrict tools and choose a model per subagent? What's the trade-off?

**(a) Samajh:** **Least privilege:** triager ka kaam padhna hai, toh `Edit/Write` dena = risk ki woh "fix" kar de. Reviewer ko `Bash` bhi na do toh woh pure judgment karega. **Model:** sasta/fast model high-volume mechanical kaam ke liye; strongest model judgment-heavy review ke liye. Trade-off: zyada restriction → agent kaam adhoora chhod sakta hai ("I couldn't rerun the test"). Note: `Bash` dena = practically write access bhi (shell se file badal sakta hai) — isliye Bash ko permission rules se narrow karo.

| Agent | Tools | Model | Why |
|---|---|---|---|
| failure-triager | Read, Grep, Glob, Bash (reruns only) | sonnet | Reruns needed for FLAKY verdict; volume high; no edits |
| test-reviewer | Read, Grep, Glob | opus (or `inherit`) | Pure judgment; can't edit what it reviews |
| log-summarizer (example) | Read, Grep | haiku | Mechanical extraction, huge volume, cheap |

**(b) Model answer:**
> "Two reasons: blast radius and cost-to-quality fit. A triage agent only needs to read logs and rerun tests, so it gets Read, Grep, Glob and Bash, and no Edit or Write — if it can't edit, it can't quietly 'fix' a failing test. And because Bash can modify files too, I narrow it with permission rules to the test runner and git read commands. A reviewer gets read-only tools only, so its job is pure judgment. On models, I match capability to the task: a smaller, faster model for high-volume mechanical extraction, the strongest model for review, where a missed weak assertion is expensive. The trade-off is that over-restricting makes agents fail tasks halfway, so I tune the allow-list from real runs, not guesses."

---

### Q6. When should you use a subagent, and when should you NOT?

**(a) Samajh:** Rule: **"Kya mujhe process chahiye ya sirf result?"** Sirf result chahiye + input bada/noisy hai → subagent. Back-and-forth chahiye, ya tiny task hai → main chat. Har subagent ka cost: startup + context building + tokens, aur tumhe uska reasoning nahi dikhta.

| Use subagent ✅ | Don't ✅ |
|---|---|
| Huge noisy input (logs, 200 test files) → small answer | 2-line fix, single file read |
| Independent review (fresh eyes) | Task needs your live steering / iterative design |
| Repeatable role with fixed rules | One-off task you'll never repeat |
| Independent tasks that can run in parallel | Tasks that share state / edit same files |
| Least-privilege step (read-only triage) | When you need to see every intermediate step |

Related options: **skill** = reusable instructions/workflow loaded into the *current* context (no isolation); **agent teams** = multiple sessions that can message each other (subagents only report to parent) — more coordination, more tokens.

**(b) Model answer:**
> "I use a subagent when the input is large and noisy but the answer I need is small — triaging a 3,000-test regression run, scanning a suite for weak assertions — or when I need independence, like a reviewer that hasn't seen how the code was written, or a least-privilege step. I don't use one for small tasks, because the spin-up and context-building cost more than the task, or for exploratory work where I need to steer every step, because I only see the final summary. The way I decide: do I need the process or just the result? If I need the process, it stays in the main session. And if I find myself writing the same instructions repeatedly but they don't need isolation, that's a skill, not a subagent."

---

### Q7. How do parallel agents work, and what goes wrong?

**(a) Samajh:** Main agent ek saath kai subagents launch kar sakta hai (e.g. 4 services ke failures ek-ek triager ko). Wall-clock time kam, **tokens zyada** (har agent apna context banata hai). Failure modes: (1) do agents **same file edit** karein → conflicts — fix: read-only parallel, ya har writer apne **git worktree** mein; (2) results inconsistent format → fix: strict output contract; (3) hidden dependency — task B ko A ka result chahiye tha. Concurrent subagents ki ek limit bhi hoti hai. **10x scale:** 40 parallel triagers ka summary bhi main context bhar dega → hierarchical: triagers → ek aggregator step jo sirf table merge kare.

**(b) Model answer:**
> "The main session can launch several subagents at once, each with its own context, and gather their results. I use it when tasks are truly independent — say, triaging failures for four DMP-style services, one agent per service — so wall-clock time drops. The costs: total tokens go up, because every agent builds its own context, and there's a concurrency limit. The failure modes I design against are shared state, inconsistent output and hidden dependencies. Parallel readers are safe; parallel writers on the same files aren't, so writers each get their own git worktree. Every agent uses the same output schema so results merge mechanically. And at 10x scale, forty summaries would flood the parent, so I'd add an aggregation step that merges the tables and only surfaces the exceptions."

---

### Q8. Why should the agent that writes code NOT be the one that reviews it? ("Work grading itself")

**(a) Samajh:** Jis agent ne test likha, uske context mein uska **reasoning aur assumptions** pade hain — "maine 670 ko C maana kyunki code mein aisa dikha." Review karte waqt woh wahi assumption dobara confirm karega: **self-confirmation bias**. Fresh-context reviewer ke paas sirf **spec + code** hota hai, writer ki kahani nahi, isliye woh "ye expected value kahan se aayi?" pooch sakta hai. Trap: **fork** (jo poori current conversation inherit karta hai) independent reviewer NAHI hai — woh writer ka hi clone hai.

**(b) Model answer:**
> "If the same agent writes and reviews, the review is anchored on the writer's reasoning — its assumptions are sitting in the context, so it re-confirms them. The classic QA example: an agent reads buggy code, derives the expected value from the code instead of the spec, writes a test that encodes the bug, and then 'reviews' it as correct because the test matches the code. A reviewer subagent with a fresh context only gets the spec and the test file, not the writer's conversation, so it has to justify every expected value from the spec. That's why I'd never use a fork of the writing session as the reviewer — a fork inherits the full conversation, so it shares the same blind spots. It's the same principle as not letting a developer sign off their own test plan: independence is the control."

---

### Q9. How do you use agents to write tests without getting tests that "pass but prove nothing"?

**(a) Samajh:** AI-generated tests ki sabse common bimari: **weak assertions** (`assert response.ok`, `assert result`), **expected values code se copy**, aur happy-path only. Workflow: spec → writer generates → run → **prove the test can fail** (code mein deliberately bug daalo — mutation check — test red hona chahiye) → fresh reviewer. Agar test bug daalne par bhi green rehta hai, woh **false pass** hai.

**(b) Model answer:**
> "I treat agent-written tests as untrusted until they've proven they can fail. My workflow: I give the writer the spec, not just the code, with explicit expected values and boundaries — for a score-band rule, the exact lower and upper edge of each band. It writes the tests and runs them. Then I do a quick mutation check: flip a comparison or shift a boundary by one in the code under test, and the relevant test must go red. If it stays green, it's a false pass. Then the fresh-context reviewer checks every assertion against the spec: is it asserting a business value or just 'not None'? Is the expected value from the spec or copied from the implementation? Are there negative and boundary cases? Only after that does the test count toward sign-off coverage."

```bash
# macOS: quick manual mutation check (flip a boundary, expect the test to go red, then restore)
sed -i '' 's/if lo <= score <= hi/if lo < score <= hi/' src/score_band.py && python -m pytest -q; git checkout -- src/score_band.py
```
```powershell
# Windows (PowerShell)
(Get-Content src\score_band.py) -replace 'if lo <= score <= hi','if lo < score <= hi' | Set-Content src\score_band.py; python -m pytest -q; git checkout -- src/score_band.py
```

---

### Q10. How would you design an agent that triages test failures?

**(a) Samajh:** Triage ka core skill: **product defect vs test bug vs flaky vs environment** alag karna. Agent ko fixed taxonomy, evidence rule, aur "kya nahi karna" do. Sabse khatarnak failure mode: agent **rerun karke green hone par "FLAKY" bol de** jabki product mein race condition hai — flaky label real bugs ka kabristan ban jaata hai. Rule: FLAKY tabhi jab reruns mein mixed result + timing/order/network dependency evidence ho; "intermittent" product failures alag flag ho.

**(b) Model answer:**
> "I give the triager a fixed taxonomy — product defect, test bug, flaky, environment — and an evidence rule: every verdict cites the assertion line, the log line, or the rerun results. Product defect means the code violates the spec; test bug means the test's expectation or setup is wrong against the spec; environment means things like a connection refused or an expired token; flaky needs mixed results across reruns plus a plausible nondeterminism source, like a timing assertion. It reruns suspected flaky tests a fixed number of times rather than until green. The hard rules: it never edits files, never marks something flaky just because a rerun passed, and anything it isn't sure about is labelled 'needs human' with a confidence level. The output is a table that the sign-off report can consume directly."

---

### Q11. How do you get agents to execute a multi-step workflow, like a sign-off run?

**(a) Samajh:** **Main session = orchestrator**, subagents = specialists, chained: run suite → triage failures → review new tests → draft sign-off report. Har step ka output agle ka input (files mein save karo, sirf chat mein nahi — auditability). **Deterministic gates** model ke haath mein mat chhodo: "PASS only if zero PRODUCT_DEFECT" ek script/hook check kare. Repeatable flow ko skill mein pack karo (one-command), CI mein non-interactive `claude -p` se chala sakte ho. Failure mode: chain ke beech mein ek step ne galat output diya aur agla step usse "sach" maan ke aage badh gaya → har handoff par schema check.

**(b) Model answer:**
> "I keep the main session as the orchestrator and chain specialist subagents: run the suite and save results to a file, have the triager classify failures into a structured table, have the reviewer check any new or changed tests, then draft the sign-off report from those artifacts. Every handoff goes through a file, not just chat, so there's an audit trail of what each step saw and produced. The go/no-go rule itself is deterministic — a script or hook checks that there are zero product defects and zero unreviewed tests; the model drafts, it doesn't decide. Once the flow is stable, I'd package it as a skill so it's one command, and run it non-interactively in CI with `claude -p` and a restricted tool set. Each step validates the previous step's output schema, so a bad handoff fails loudly instead of propagating."

```bash
# macOS / Linux CI: non-interactive run with restricted tools (flags vary by version; check `claude --help`)
claude -p "Use the failure-triager subagent on reports/run1.txt and write reports/triage.md" \
  --allowedTools "Read,Grep,Glob,Write,Bash(python -m pytest:*)"
```
```powershell
# Windows (PowerShell)
claude -p "Use the failure-triager subagent on reports/run1.txt and write reports/triage.md" --allowedTools "Read,Grep,Glob,Write,Bash(python -m pytest:*)"
```

---

### Q12. How do you handle hallucination risk in agent output?

**(a) Samajh:** Agent confident tone mein **non-existent root cause, galat file:line, ya made-up log line** likh sakta hai — aur subagent mein yeh aur khatarnak hai kyunki parent ko raw evidence dikhta hi nahi (Q2). Defence: **verifiable evidence mandatory**, "unknown" bolne ki permission, aur spot-check — har report mein 1–2 citations khud kholo. Metric: agent verdicts vs human verdicts ka agreement rate track karo.

**(b) Model answer:**
> "I assume any agent claim can be fabricated until it's tied to evidence I can check. So the output contract demands citations: file and line, the exact assertion message, the rerun command and its result. I explicitly allow 'unknown — needs human' in the taxonomy, because if the only options are confident verdicts, the model will pick one. Then I verify: I spot-check a couple of citations in every report, and I'd track agreement between agent verdicts and human verdicts over time — if agreement on 'product defect' drops, the agent's prompt or model needs attention before anyone relies on it. For sign-off specifically, an agent verdict is an input to my decision, never the decision, and the report says which items were agent-classified and which were human-confirmed."

---

### Q13. What is scope creep in agents, and how do you prevent it?

**(a) Samajh:** Scope creep = agent ko kaha "failure batao", usne **test ki assertion loose karke green kar diya**, ya config badal di, ya extra files "clean up" kar di. Yeh QA mein sabse dangerous hai kyunki result **green dikhta hai**. Layers: (1) prompt mein explicit "never" rules — soft; (2) **tools allow-list** — hard; (3) **permission deny rules** in `settings.json` (e.g. deny writes to `tests/` for that workflow, deny reading raw data) — hard; (4) **hooks** jo tool call ko block karein — hard; (5) `git diff` check after run.

**(b) Model answer:**
> "Scope creep is an agent doing more than it was asked — the classic one in QA is being asked to investigate a failure and 'fixing' it by loosening the assertion, which turns a red build green and hides a defect. I prevent it in layers. The prompt states what's out of scope, but that's guidance, not enforcement. The enforcement is the tool allow-list — a triager simply has no Edit or Write — plus permission rules in settings that deny writes to protected paths and deny reading raw data, and hooks that can block a tool call before it runs. After any agent run, a `git diff --stat` check is part of the workflow: for a read-only step, any diff fails the step. The principle: prompts shape behaviour, permissions and hooks guarantee it."

```json
// .claude/settings.json (lab-level example; same file on macOS and Windows)
{
  "permissions": {
    "deny": ["Read(./data/raw/**)", "Edit(./tests/**)", "Bash(git push:*)"]
  }
}
```

---

### Q14. What do agents cost, and how do you decide if it's worth it?

**(a) Samajh:** Har subagent apna context fresh banata hai → files dobara padhta hai → tokens. Parallel = time kam, tokens zyada. Hidden costs: galat delegation prompt se poora run waste; reviewer ka strongest model har PR par mehenga. **Decision:** cost per run × runs/day vs human time bachaaya + defects pakde. **10x scale:** 10 delivery types × 5 regions = 50 sign-offs — har ek par full opus review = expensive; tier karo: cheap model sab par, strong model sirf changed tests + high-risk deliveries par.

**(b) Model answer:**
> "Every subagent builds its own context, so it re-reads files the parent may already have read — isolation is paid for in tokens, and parallelism trades tokens for wall-clock time. I decide with simple numbers: cost per run times runs per day, against human triage time saved and defects caught that would otherwise have escaped. I'd measure it on a pilot before scaling — Claude Code's usage reporting gives per-session cost. At 10x scale, say many delivery types across regions, running the strongest model on every review isn't sensible, so I tier: a fast model for mechanical triage across everything, the strongest model only for changed tests and high-risk deliveries, and nothing at all for unchanged suites whose results match the last good baseline. If an agent step isn't catching anything for weeks, that's a signal to cut it or change what it looks for."

---

### Q15. How do data boundaries and masking apply when agents handle test output?

**(a) Samajh:** Subagent ka final message parent ke context mein jaata hai, phir report mein, phir shayad Jira/Slack mein — **leak chain**. Toh masking **source par** karo: agent prompt mein rule "identifiers ko mask karo by default (`SYN-****3907`)", aur hard boundary: raw data folder ko permissions se deny. Locked-down Linux host (SSH) par agent wahi permissions le jo tumhare paas hain — isliye wahan read-only, narrow commands. Failure mode: assertion message mein full ID print hoti hai → triager use copy karta hai → report mein chala gaya.

**(b) Model answer:**
> "I treat everything an agent returns as shareable output, because it flows from the subagent to the parent, into the sign-off report and possibly into a ticket. So masking happens at the source: every agent that touches test output has a rule to mask identifiers by default — keep only the last four characters — and never echo raw records, only counts and field names. That's guidance; the hard boundary is that raw-data paths are denied by permission rules, so the agent can't read them in the first place. I'd also fix the tests themselves so assertion messages don't print full identifiers. On a locked-down Linux host over SSH, the agent runs with my access, so I keep it to a narrow command allow-list and read-only operations, and nothing leaves the host unmasked."

---

## 3) Mini Lab — `failure-triager` + `test-reviewer` (~20 min)

**Goal:** Ek synthetic repo jisme 4 planted problems hain (product defect, test bug, flaky test, weak assertion). Do subagents banao aur dekho ki kya woh sahi pakadte hain — aur triager ne kuch edit toh nahi kiya.

**Step 1 — Repo setup** (lab folder: `04-1-test/subagent-lab/`)

```bash
# macOS
mkdir -p 04-1-test/subagent-lab/{src,tests,reports,.claude/agents} && cd 04-1-test/subagent-lab
python3 -m venv .venv && source .venv/bin/activate && pip install pytest
touch src/__init__.py tests/__init__.py && git init
```
```powershell
# Windows (PowerShell)
New-Item -ItemType Directory -Force 04-1-test\subagent-lab\src,04-1-test\subagent-lab\tests,04-1-test\subagent-lab\reports,04-1-test\subagent-lab\.claude\agents | Out-Null
cd 04-1-test\subagent-lab
python -m venv .venv; .venv\Scripts\Activate.ps1; pip install pytest
New-Item src\__init__.py,tests\__init__.py | Out-Null; git init
```

**Step 2 — Code + tests (planted problems).** Create these two files:

`src/score_band.py`
```python
"""Synthetic score-band mapper for the lab. Bands are invented, not real FICO bands."""

BANDS = [
    (300, 579, "E"),
    (580, 669, "D"),
    (670, 739, "C"),
    (740, 799, "B"),
    (800, 850, "A"),
]


def band_for(score: int) -> str:
    if not isinstance(score, int) or score < 300 or score > 850:
        raise ValueError(f"score out of range: {score}")
    for lo, hi, label in BANDS:
        if lo < score <= hi:  # planted defect: lower bound should be inclusive
            return label
    return "UNBANDED"
```

`tests/test_bands.py`
```python
import random
import time

import pytest

from src.score_band import band_for


def test_lower_boundary_670_is_band_c():
    ref = "SYN-48213907"  # synthetic applicant ref
    result = band_for(670)
    assert result == "C", f"ref={ref} score=670 expected C got {result}"


def test_upper_boundary_739_is_band_c():
    # planted test bug: expected value is wrong (739 belongs to C, not B)
    assert band_for(739) == "B"


def test_mid_score_returns_something():
    # planted weak assertion: any non-empty string passes, even "UNBANDED"
    assert band_for(705)


def test_band_lookup_is_fast():
    # planted flaky test: fake latency, timing-based assertion
    start = time.perf_counter()
    time.sleep(random.uniform(0.03, 0.07))
    band_for(705)
    assert time.perf_counter() - start < 0.05


def test_out_of_range_rejected():
    with pytest.raises(ValueError):
        band_for(900)
```

> Note: the "planted ..." comments make it easy for you to check the agents. For a harder test, delete those comments before Step 4 and see if the agents still find all four.

**Step 3 — The two subagents.**

`.claude/agents/failure-triager.md`
```markdown
---
name: failure-triager
description: Use PROACTIVELY after any failed test run. Classifies each failing test as PRODUCT_DEFECT, TEST_BUG, FLAKY, ENV or NEEDS_HUMAN with evidence. Read-only; never edits files.
tools: Read, Grep, Glob, Bash
model: sonnet
---
You are a test-failure triage specialist for a QA sign-off pipeline.

Steps:
1. Read the test run output you are given. List every failing test.
2. For each failure, read the test and the code under test. The spec is the docstring/comments of the code under test plus the test name; if they disagree, say so.
3. If a failure might be nondeterministic, rerun ONLY that test exactly 5 times
   (python -m pytest <nodeid> -q) and record pass/fail counts.
4. Classify:
   - PRODUCT_DEFECT: code violates the intended behaviour.
   - TEST_BUG: the test's expectation or setup is wrong.
   - FLAKY: mixed results across reruns AND a nondeterminism source you can point to.
   - ENV: infrastructure/setup problem (missing dependency, connection, permissions).
   - NEEDS_HUMAN: you cannot decide with evidence.

Hard rules:
- Never edit, create or delete files. Bash is only for running pytest and read-only git commands.
- Never call something FLAKY just because one rerun passed.
- Mask identifiers: keep only the last 4 characters (SYN-48213907 -> SYN-****3907). Never print raw records.

Output (and nothing else):
| Test | Verdict | Confidence (H/M/L) | Evidence (file:line, assertion msg, rerun counts) | Suggested next action |
Then one line: "Sign-off blockers: <count of PRODUCT_DEFECT>".
```

`.claude/agents/test-reviewer.md`
```markdown
---
name: test-reviewer
description: Use to review test code with fresh eyes before it counts toward sign-off. Finds weak assertions, false passes, expected values copied from code, flaky patterns and missing boundary/negative cases. Read-only.
tools: Read, Grep, Glob
model: opus
---
You are an independent, skeptical test reviewer. You did NOT write these tests and you
must not trust their author. Judge every expected value against the spec
(docstrings/comments of the code under test), never against the implementation.

For each test, check:
1. Assertion strength: does it assert a specific business value, or just truthiness / not-None / status-ok?
2. False pass: would the test still pass if the code under test were broken? Name a concrete mutation it would miss.
3. Expected value source: does it come from the spec, or does it look copied from the implementation?
4. Determinism: timing, randomness, ordering, network, shared state.
5. Coverage gaps: missing lower/upper boundaries, invalid inputs, negative cases.

Rules: read-only; mask identifiers to last 4 characters; no praise, no filler.

Output:
| Test | Problem | Severity (BLOCKER/MAJOR/MINOR) | Why (1 line) | Fix suggestion |
Then: "Missing tests:" as a bullet list.
```
(Agar tumhare plan par `opus`/`sonnet` alias available nahi hai, `model: inherit` likh do.)

**Step 4 — Run and triage.**

```bash
# macOS
python -m pytest -q > reports/run1.txt 2>&1; git add -A && git commit -qm "lab baseline"
claude
```
```powershell
# Windows (PowerShell)
python -m pytest -q *> reports\run1.txt; git add -A; git commit -qm "lab baseline"
claude
```
Claude Code ke andar:
```text
/agents
Use the failure-triager subagent on reports/run1.txt
```

**Expected output (shape — wording will vary):**

| Test | Verdict | Confidence | Evidence | Next action |
|---|---|---|---|---|
| test_lower_boundary_670_is_band_c | PRODUCT_DEFECT | H | `score_band.py` uses `lo < score`; 670 → `UNBANDED`; ref=SYN-****3907 | Make lower bound inclusive |
| test_upper_boundary_739_is_band_c | TEST_BUG | H | 739 is in (670, 739) → C; test expects B | Fix expected value |
| test_band_lookup_is_fast *(only if it failed in run1)* | FLAKY | M | 5 reruns: mixed pass/fail; `random.uniform` sleep vs 0.05s threshold | Remove timing assertion |

`Sign-off blockers: 1`. `/agents` mein dono agents dikhne chahiye. **Check:** full ref `SYN-48213907` output mein nahi hona chahiye.

**Step 5 — Fresh-context review.**
```text
Use the test-reviewer subagent to review tests/test_bands.py
```
**Expected:** `test_mid_score_returns_something` → **BLOCKER** (weak assertion; passes even for `UNBANDED`), `test_band_lookup_is_fast` → MAJOR (timing/random), `test_upper_boundary_739` → expected value wrong vs spec; Missing tests: 300, 579/580, 799/800, 850, non-int input.

**Step 6 — Prove the triager stayed in scope.**
```bash
# macOS and Windows (same command)
git status --short
```
**Expected:** sirf `reports/` mein naye files (agar kuch likha ho) — `src/` ya `tests/` mein **koi change nahi**. Agar change hai → tool allow-list / permissions tight karo (Q13).

**Stretch:** Product bug fix karo (`lo <= score <= hi`), test bug fix karo, weak assertion ko `== "C"` karo, sab green hone par **commit karo**, phir Q9 wala mutation check chalao — ab 670 wala test red hona chahiye (aur `git checkout` tumhara committed fix wapas le aayega).

---

## 4) Special Questions (senior / tricky)

### S1. Cross-question chain (3 levels): "The reviewer agent approved the tests. Can we sign off?"

**L1 — "Reviewer approved the new tests. Ship?"**
> "Not on that alone. The reviewer's approval means the tests passed a read-only checklist review. Before they count toward sign-off, I need evidence they can fail — a mutation check on the critical rules — and the suite results themselves. The review is one input to sign-off, not the sign-off."

**L2 — "How do you know the reviewer itself isn't wrong?"**
> "I test the reviewer like any other test tool: I keep a small seeded set of known-bad tests — weak assertions, copied expected values, timing dependencies — and every time the agent's prompt or model changes, I run it against that set and check it catches all of them. That's a regression suite for the agent. I also spot-check its citations on real reviews and track how often humans overturn its findings."

**L3 — "A defect still escaped to a client. The agents said everything was fine. What failed?"**
> "First, the process failed, not 'the AI' — a sign-off owner relied on a control that wasn't sufficient. I'd do a blameless RCA: was the defect in a rule the spec covered? If yes, why did no test assert it — a coverage gap in the generated tests, a weak assertion the reviewer missed, or a failure the triager mislabelled as flaky? Each answer maps to a fix: add the escaped case to the reviewer's seeded set, tighten the triage rule, or add a deterministic gate. And I'd make the sign-off report state which checks were agent-performed and which were human-confirmed, so that boundary is explicit next time."

---

### S2. Trap: "Why not one big agent with all tools? Fewer moving parts."

**(a) Samajh:** Trap hai — "simpler" sunne mein achha lagta hai. Jawab: ek agent = ek context (noise), ek permission set (sabse zyada wala), aur khud ka kaam khud grade karna (Q8). Lekin over-splitting bhi galat — handoffs mein info loss aur cost.

**(b) Model answer:**
> "One agent is simpler to start but worse on the three things that matter for sign-off. Its context fills with everything, so quality drops on long runs. Its permissions are the union of every step's needs, so a triage step ends up with write access. And it grades its own work. That said, I don't split for the sake of it — every handoff loses information and adds cost. I split exactly where there's a different permission need, a need for independence, or a large noisy input that should be summarized. Everything else stays in the main session."

---

### S3. Scenario: "On release day, the triager labels 40 of 50 failures as FLAKY. What do you do?"

**(a) Samajh:** Red flag! 40/50 flaky = ya toh environment toot gaya hai, ya agent ka FLAKY rule loose hai, ya ek real intermittent product bug (race/timeout) hai. "Flaky hai, ignore" bol ke ship karna = senior-level galti.

**(b) Model answer:**
> "I don't accept that at face value — 80% flaky on one run is a signal, not noise. First I look for a common cause: same service, same time window, same error like timeouts or connection resets — that usually means an environment problem or a real intermittent product issue, like a race or a resource leak, not 40 independent flaky tests. I compare with the flaky rate from the last few baseline runs. I check the agent's evidence: did it actually rerun five times and see mixed results, or did it label on one pass? Release-blocking decision: the sign-off stays on hold until the common cause is identified. Any test that's genuinely flaky gets quarantined with a ticket and an owner, never silently ignored."

---

### S4. Trap: "Just give the reviewer the writer's full conversation — more context means a better review, right?"

**(a) Samajh:** Nahi. Zyada context ≠ better review jab context mein **writer ke assumptions** hon. Reviewer ko spec + code chahiye, writer ki reasoning nahi.

**(b) Model answer:**
> "More context isn't better when the extra context is the writer's assumptions. If the reviewer reads the writer's reasoning — 'I took the expected value from the implementation' — it tends to accept that framing instead of challenging it. The reviewer should get exactly what an independent human reviewer would get: the spec, the code under test and the tests. If it needs something else, that's a gap in the spec, which is itself a finding. That's also why a forked session isn't an independent reviewer."

---

### S5. Resume-linked STAR skeleton: "You built an AI regression analyzer. How would you apply subagents to it?"

**(a) Samajh:** Sirf real claims use karo: analyzer **Jenkins logs, repo history, Kubernetes events correlate karta hai, Jira defects auto-file karta hai, chatbot hai, IAM + Core teams use karti hain**. Claude Code subagents ko **"personal lab / how I'd evolve it"** ki tarah frame karo — professional claim nahi. Numbers sirf wahi bolo jo tumhe sach mein pata ho; placeholders khud bharna.

**(b) STAR skeleton (English):**
> **S:** "At FICO, regression failures across the DMP services took time to triage, because the evidence was spread across Jenkins logs, repo history and Kubernetes events."
> **T:** "I built an AI regression analyzer to correlate those sources and speed up triage."
> **A:** "It correlates Jenkins logs, repository history and Kubernetes events, auto-files Jira defects, and has a chatbot interface; the IAM and Core teams use it. [Add one concrete design decision you actually made — e.g. how you chose what goes into a defect.]"
> **R:** "[Only a result you can actually back up — e.g. teams using it, or a time saving you measured. Don't estimate on the spot.]"
> **Bridge (lab framing):** "In my personal lab with Claude Code, I've been exploring how I'd structure that with subagents: a read-only triager with a fixed taxonomy and evidence rule, a separate reviewer with a fresh context, and a deterministic gate before anything is auto-filed — so a hallucinated root cause can't become a Jira ticket without evidence attached."

---

## 5) 1-min Revision

- **Subagent** = fresh context + own system prompt + tool allow-list → returns only final message
- **File:** `.claude/agents/<name>.md` (team) · `~/.claude/agents/` (personal) · frontmatter = config, body = prompt · `/agents`
- **`description` = routing rule**; sign-off workflows → explicit invocation; omit `tools` = inherits everything
- **Use when:** big noisy input → small answer, independence, least privilege · **Not when:** tiny task, need to steer, shared files
- **Writer ≠ reviewer** — fresh context, spec only; a fork is not independent
- **Agent tests must prove they can fail** — mutation check + weak-assertion review
- **Triage taxonomy + evidence + NEEDS_HUMAN**; never "flaky because rerun passed"
- **Prompts shape, permissions/hooks guarantee**; mask at source; tokens scale with agents → tier models
