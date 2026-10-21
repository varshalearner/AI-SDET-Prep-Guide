# Phase 02 + 03 — Concepts Cheat Sheet (Topics 09–19)

> Sirf concepts, concise. Interview questions voice mode mein.
> Examples synthetic hain, sensitive data masked (`SSN=***-**-1234`).

---

# PHASE 02 — AI OUTPUT REVIEW

## 09. Reviewing Unfamiliar Code Fast

**Core idea:** Pehle code ko *poora* padhne ki koshish mat karo. Pehle yeh samjho ki code ka *kaam kya hai* aur data *kahan se kahan jaata hai*. Phir sirf risky parts ko gehraai se padho.

**Analogy:** Naye sheher mein pehle highways dekho (entry points), phir sirf us gali mein jao jahan tumhe kaam hai.

**30-min strategy:**
1. **Orient (5 min):** README, folder structure, `package.json`/`pyproject.toml`/`pom.xml`. Dependencies se pata chalta hai code kya karta hai.
2. **Entry points:** `main`, route/controller definitions, CLI commands, Jenkinsfile, Dockerfile `CMD`.
3. **Tests se intent padho:** Test names ek spec ki tarah hote hain. Jo test nahi hai, woh shayad untested risk hai.
4. **Ek call flow trace karo:** request → handler → service → DB/external call → response.
5. **History:** `git log --oneline -20 -- path/`, `git blame -L 40,60 file`. Bahut churn = risk. "Hotfix" commits = fragile area.
6. **Grep navigation:** `rg "def score|calculate" -n`, `rg "TODO|FIXME|except:"`.
7. **Claude se explain karwao, phir verify karo:** Jo bhi woh claim kare, uske liye file:line maango aur khud check karo. Claude ek confident tour guide hai, oracle nahi.

**Review checklist:** inputs ka validation · error handling (swallowed exceptions) · boundaries/nulls · side effects · secrets/PII logging · concurrency · tests asli behaviour assert karte hain ya nahi.

**Kya poochna hai:** Is module ka owner kaun hai? Isse kaun call karta hai? Production mein kya toot sakta hai? Invariants kya hain?

**Senior nuance:** Har cheez samajhna goal nahi hai. Goal yeh hai ki **risk ke hisaab se depth** do. Scale 10x hone par, change-based review karo (diff + blast radius), poore repo ka review nahi.

---

## 10. Weak Assertions

**Core idea:** Ek weak assertion pass ho jaata hai chahe behaviour galat ho. Test green dikhta hai lekin kuch prove nahi karta.

**Catalogue (weak → strong):**

| Weak | Problem | Strong |
|---|---|---|
| `status == 200` only | Body galat ho sakti hai | Status + schema + key values |
| `x is not None` | Koi bhi value pass | `x == expected` |
| `len(items) > 0` | 1 galat item bhi pass | Exact count + content |
| `assert result` (truthy) | `"error"` bhi truthy hai | Exact value compare |
| Tautology `assert a == a` | Kabhi fail hi nahi hoga | Independent oracle se compare |
| Apna hi mock assert karna | Test ne SUT test hi nahi kiya | Real logic chalao, sirf boundaries mock karo |
| Snapshot blindly update | Bug ko "baseline" bana diya | Diff review karo, phir update |
| `except Exception: pass` | Failure chhup gaya | `pytest.raises(SpecificError)` |
| Partial fields | Baaki fields toot sakti hain | Contract/schema check |
| Float `==` | Precision mismatch | `pytest.approx` / `closeTo` |
| Order-dependent list compare | Flaky ya galat | Agar order spec nahi hai to sort ya set compare |

```python
# weak
assert resp.status_code == 200
# strong
assert resp.status_code == 200
body = resp.json()
assert body["score"] == 742
assert 300 <= body["score"] <= 850
assert body["reason_codes"] == ["R01", "R14"]
```

```java
// Rest Assured strong
given().get("/score/{id}", "SYN-001").then()
  .statusCode(200)
  .body(matchesJsonSchemaInClasspath("score.json"))
  .body("score", equalTo(742))
  .body("reasonCodes", contains("R01", "R14"));
```

```ts
// Playwright/TS
expect(res.status()).toBe(200);
expect(await res.json()).toMatchObject({ score: 742, reasonCodes: ['R01', 'R14'] });
```

**Senior nuance:** Strength ka test yeh hai ki **agar code galat ho to kya yeh test fail hoga?** Lekin over-specification (timestamps, IDs) bhi galat hai, kyunki woh brittle tests banata hai. Balance yeh hai: jo *contract* hai usko assert karo, jo incidental hai usko nahi.

---

## 11. False Passes

**Core idea:** Test green hai, lekin ya to kuch chala hi nahi ya kuch check hi nahi hua. Yeh weak assertion se bhi zyada khatarnak hai, kyunki confidence jhootha hai.

**Causes:**
- **Collection miss:** `check_score.py`, function name `verify_x` → pytest ise collect hi nahi karta.
- **skip/xfail** jo bhool gaye; `xfail` jo ab pass ho raha hai (`strict=True` use karo).
- **try/except pass** assertion ke around.
- **Async not awaited:** coroutine kabhi chala hi nahi.
- **Empty loop:** `for r in rows: assert ...`, aur `rows` empty hai.
- **SUT khud mocked** hai.
- **Wrong env/fixture:** test stub server pe chala, real wale pe nahi.
- **Retries** jo intermittent bug chhupa dete hain.
- **Conditional assertions:** `if resp.ok: assert ...`
- **Callback assertion** jo kabhi call nahi hua.
- **Cached responses:** naya build test hi nahi hua.

```python
# false pass
for rec in fetch_records(file):   # file empty → 0 iterations
    assert rec["score"] <= 850
# fix
recs = fetch_records(file)
assert len(recs) == EXPECTED_COUNT
for rec in recs: assert 300 <= rec["score"] <= 850
```

**Detection:**
- Test count trend track karo. Agar count achanak gira hai, to collection issue hai.
- `pytest --collect-only`, `-rA` (skips dikhata hai).
- Break-the-code: SUT ko jaan-boojh ke toda, phir bhi green hai to false pass hai.
- `assert` count per test (lint), `pytest-asyncio` strict mode.
- Har report mein env/build ID log karo.

**Senior nuance:** Sign-off report mein sirf "pass" nahi likhna. Likhna chahiye **"N run, N executed, 0 skipped, build X, env Y"**. 3,000 tests pe ek silent skip kisi ko dikhega nahi, isliye counts ko gate banao.

---

## 12. Validating AI-Generated Tests

**Core idea:** AI ka likha test syntax mein sahi hota hai, lekin aksar woh *code* ko test karta hai, *requirement* ko nahi. Implementation se derive kiya gaya test bugs ko bhi "expected" maan leta hai.

**Techniques:**
- **Break-the-code check:** Code mein ek bug daalo. Agar test fail hua to theek hai, varna test bekaar hai.
- **Mutation testing:** Tool code mein chhote mutants banata hai (`>` → `>=`, `+` → `-`). **Mutation score = killed / total**. Tools: `mutmut` (Python), PIT (Java), Stryker (JS/TS).
  ```bash
  pip install mutmut
  mutmut run --paths-to-mutate src/score.py
  mutmut results    # survived mutants = weak spots
  ```
- **Coverage limitation:** 100% line coverage ka matlab sirf yeh hai ki line *chali*, yeh nahi ki *verify hui*. Coverage zaroori hai, kaafi nahi.
- **Requirement traceability:** Har requirement ko ek test se map karo. Jo requirement unmapped hai, woh gap hai.
- **Missing cases:** negative, boundary (299/300/850/851), null, empty, unicode, duplicate.
- **Oracle problem:** Expected value kahan se aayi? Agar SUT ke output se copy hui to tautology hai. Spec, independent calc, ya golden dataset use karo.
- **"Passes for wrong reason":** Pass to ho gaya, lekin galat path se. Jaise error response mein bhi `score` field ho.

**AI test review checklist:** Asserts specific hain? Negative cases hain? Mocks sirf boundaries pe hain? Expected values spec se aayi hain? Mutants kill hote hain? Naming collect hoti hai? Koi skip/try-except to nahi?

**Senior nuance:** Mutation testing slow hai. 10x scale pe ise sirf changed modules pe chalao, nightly. Equivalent mutants (jo behaviour change hi nahi karte) noise hain, isliye 100% target mat rakho, trend track karo.

---

## 13. Following Docs Precisely & Finding Gaps

**Core idea:** Shipped doc ko **word-by-word** follow karo, jaise ek naya client karega. Apna knowledge use karke gaps silently fill mat karo. Jahan tum atke, wahi gap hai.

**Analogy:** Recipe follow kar rahe ho. "Thoda namak" likha hai to note karo ki *thoda kitna?* Apne andaaz se mat daalo.

**Gap types:**
- **Missing step/prereq:** version, permission, env var.
- **Ambiguity:** "configure the service" (kaise?).
- **Contradiction:** README mein port 8080 hai, config mein 9090.
- **Doc vs actual mismatch:** doc mein response field `fico_score` hai, API mein `score`.
- **Stale:** purane commands ya flags.
- **Unstated assumptions:** OS, shell, network access.

**Process:** Clean env lo → har step chalao → exact command + output note karo → jahan bhi deviate kiya, usse **assumption** ke roop mein log karo → report banao.

**Gap report format:** `Step # | Doc says | Actual | Impact | Suggested fix | Severity`

**Skeptical without negative:** Tone factual aur solution-oriented rakho. "Doc galat hai" mat bolo, bolo "Step 4 mein expected X tha, observed Y, suggestion Z." Insaan pe nahi, artefact pe focus karo.

**Senior nuance:** Har region ya delivery type ka alag doc hota hai, isliye doc ko bhi test-suite ki tarah treat karo (doc tests, runnable examples). Jo client ke paas jaata hai, uske gaps directly support tickets ban jaate hain.

---

# PHASE 03 — TESTING FUNDAMENTALS

## 14. Test Design Techniques

| Technique | Kab use karein | FICO-style example |
|---|---|---|
| **Equivalence Partitioning** | Bada input range | Score: `<300` invalid, `300–850` valid, `>850` invalid |
| **Boundary Value Analysis** | Range/limits | 299, 300, 301, 849, 850, 851 |
| **Decision Table** | Multiple conditions → action | (file valid? × region supported? × client active?) → deliver/reject |
| **State Transition** | Lifecycle | Delivery: Created → Validated → Signed-off → Delivered / Rejected |
| **Pairwise** | Bahut combinations | region × format × delivery type × client tier |
| **Error Guessing** | Experience-based | Empty file, BOM, CRLF, duplicate IDs, trailing spaces |
| **Risk-based** | Time limited ho | Score values, PII masking > UI colour |
| **Exploratory** | Naya/unclear area | Time-boxed charter: "explore malformed delivery files" |

**Trade-off:** Coverage vs effort. Exhaustive testing impossible hai. EP+BVA se cases kam hote hain lekin bugs wahi pakde jaate hain. Pairwise se ~90% interaction bugs bahut kam cases mein mil jaate hain.

**Senior nuance:** Technique ka choice **risk + structure** se hota hai. Numeric range ho to BVA, rules ho to decision table, workflow ho to state, combinations ho to pairwise. Plan mein *kya test nahi kiya aur kyun* bhi likho.

---

## 15. Effective Assertions

**Kya assert karein:**
- **Behaviour:** output sahi hai ya nahi.
- **Contract:** schema, types, required fields.
- **Side effects:** DB row bani, event publish hua, file likhi gayi.
- **Data correctness:** values, counts, aggregates.

**Principles:**
- **Hard vs soft:** Hard assertion pehle failure pe ruk jaata hai. Soft assertion saari failures collect karta hai (`assertj SoftAssertions`, `pytest-check`). Ek record ki many fields check karni ho to soft use karo. Precondition ho to hard.
- **Schema validation:** `jsonschema` / `matchesJsonSchema`. Ise value checks ke saath use karo, replace karne ke liye nahi.
- **Custom matchers/helpers:** `assert_valid_score_record(r)`. Isse readable aur reusable code banta hai.
- **Meaningful messages:** `assert s == 742, f"score mismatch for id={rid}: got {s}"`.
- **Granularity / one concept per test:** Ek test ek behaviour check kare, lekin uske liye multiple asserts allowed hain.
- **Data comparison:** floats ke liye tolerance, unordered data ke liye sort/set, ignore-list mein sirf volatile fields (timestamp, uuid).

```python
from pytest import approx
assert usage["total_calls"] == 1200
assert usage["avg_latency_ms"] == approx(45.2, rel=1e-3)
assert sorted(r["id"] for r in rows) == sorted(expected_ids)
```

**Senior nuance:** Bahut zyada asserts = brittle, bahut kam = weak. Asli rule: **"Jo client ke liye matter karta hai, woh assert karo."** Large datasets pe row-by-row diff ki jagah aggregate checks (count, sum, checksum) aur sampling use karo.

---

## 16. Flaky Tests: Detection & Isolation

**Definition:** Same code aur same test, lekin kabhi pass, kabhi fail.

**Causes:** timing/async (`sleep` ki jagah wait use karo) · order dependence · shared state/data · environment drift · network · time zones / DST · randomness · resource limits (CPU/mem/ports) · external dependencies.

**Detection:**
- Same commit pe reruns (`pytest --count=20` with `pytest-repeat`).
- History analysis: pass/fail pattern ko commit ke against dekho.
- **Flaky rate** = inconsistent runs / total runs, per test.
- Random order run (`pytest-randomly`) se order dependence pakdi jaati hai.

**Isolation:**
- **Quarantine:** Test ko alag job mein daalo, non-blocking banao, owner + ticket + deadline do.
- **Seed fix:** randomness ko reproducible banao.
- **Isolated data:** har test apna unique data banaye aur saaf kare.
- **Retries:** symptom chhupate hain. Sirf infra-level transient issues ke liye theek hain, aur retry ka count report karo.

**Root-cause fix:** explicit waits, time freezing (`freezegun`), fixture scope sahi karna, dependencies stub karna.

**Team policy:** Flaky test ko gate se hatao (quarantine), lekin SLA ke saath fix karo. Flaky rate ko ek metric banao. "Rerun until green" ko culture mat banne do.

**Senior nuance:** 10x scale pe 1% flaky rate ka matlab hai ki lagbhag har build mein koi na koi failure hogi. Flakiness trust ko maar deti hai, aur phir log real failures bhi ignore karne lagte hain.

---

## 17. Product Defect vs Test Bug

**Triage decision tree:**
1. **Reproduce:** Manually/curl se same input bhejo. Agar fail hua to product ki taraf lean karo.
2. **Isolate layer:** UI → API → service → data. Kis layer pe toota?
3. **Test check karo:** assertion galat? test data stale? locator badal gaya?
4. **Env check karo:** config, version, dependency down, cert expiry.
5. **Spec se compare karo:** spec kya kehta hai? (oracle)
6. **Recent changes:** product commit vs test commit vs env change. Pehle kya badla?
7. **Evidence collect karo:** request/response, logs, build IDs, timestamps (masked).

| Signal | Likely |
|---|---|
| Manual repro fail, spec violation | Product defect |
| Sirf automated fail, manual pass | Test bug ya env |
| Ek hi env mein fail | Env/config |
| Test code recent change | Test bug |
| Intermittent | Flaky (timing/data) |

**Product bug kaise prove karein:** Minimal repro + spec reference + evidence jo test framework ke bina bhi fail ho.

**Senior nuance:** Galat classification costly hai. Test bug ko defect bana diya to dev ka time waste hota hai aur QA ki credibility girti hai. Defect ko test bug bana diya to bug client tak pahunch jaata hai. Shak ho to **product defect assume karke investigate karo**.

---

## 18. Test Strategy, Pyramid & CI Gating

**Pyramid:** Bahut saare unit tests (fast, cheap) → kam API/integration tests → bahut kam UI/E2E (slow, brittle).
**Trophy:** Integration tests pe zyada weight. Service-heavy systems ke liye fit hai.

| Layer | + | − |
|---|---|---|
| Unit | Fast, precise | Integration bugs miss karte hain |
| API | Contract + logic, stable | Setup chahiye |
| UI | Real user flow | Slow, flaky, costly |

**Suite types:**
- **Smoke:** critical paths, minutes mein. "Build zinda hai?"
- **Sanity:** specific fix/area ka quick check.
- **Regression:** broad suite. "Kuch purana toota?"

**Test selection:** change-based (impacted modules), risk tags, priority tiers.

**CI quality gates:** build → unit → smoke (block on fail) → regression → perf thresholds → sign-off. Gate criteria explicit hone chahiye: pass rate, 0 critical defects, perf p95 < X.

**Entry/Exit criteria:**
- *Entry:* build deployed, env healthy, data ready.
- *Exit:* executed %, pass %, open defects by severity, sign-off report.

**New delivery type/region ka test plan:** scope · risks (format, locale, data rules, regulatory) · test data · techniques · environments · gates · owners · rollback.

**Smoke-on-merge + on-demand regression ko defend karna:** Har merge pe fast feedback milta hai aur cost kam hai. Regression developer image ke promotion se pehle chalta hai, matlab promotion se pehle broad confidence. Trade-off yeh hai ki merge pe deep bug miss ho sakta hai, isliye **promotion gate** uski bharpai karta hai.

---

## 19. Defect Reporting & RCA

**Achhi bug report:**
- Title: `[Area] What fails under which condition`
- Env/build/version
- Steps (minimal, numbered)
- Expected vs Actual
- Evidence: logs, request/response (masked), screenshot
- Impact: kaun affected hai, kitna
- **Severity** (technical impact) vs **Priority** (fix kitna urgent hai). Jaise typo in client report = low severity, high priority.

**RCA techniques:**
- **5 Whys:** symptom se root tak "kyun?" poochte jao. Process gap pe ruko, insaan pe nahi.
- **Timeline:** kab deploy hua, kab error aaya, kab detect hua.
- **Fault isolation:** components ko ek-ek karke hatao, binary search karo (jaise `git bisect`).

**Fix verification:** original repro + related regressions + **sabhi envs** mein (dev → staging → prod-like). Ek test add karo jo is bug ko future mein pakde.

**Regression risk:** fix ka blast radius kya hai? Shared code touch hua?

**Hotfix process:** severity decide karo → minimal fix → focused tests (fix + smoke + impacted regression) → expedited approval → deploy → monitor → main branch mein back-merge → postmortem.

**STAR skeleton (releases/hotfix stories):**
- **S:** Release/hotfix context, kaunsi service, kya symptom.
- **T:** Meri responsibility (triage, root cause, verification).
- **A:** Kaise isolate kiya (logs/K8s events/repo history), evidence, kis se coordinate kiya.
- **R:** Fix verified, test add kiya, kya seekha/process change.

**Senior nuance:** RCA ka output sirf "bug fixed" nahi hota, balki **"yeh class of bug dobara kaise nahi aayega"** hota hai, jaise naya test, gate, ya check.

---

# QUICK REVISION (10 lines)
1. Unfamiliar code: entry points → tests → ek flow trace → git history → risk ke hisaab se depth.
2. Claude explain kare, lekin file:line se verify karo.
3. Weak assertion = galat behaviour pe bhi pass. Test: "code toda to fail hoga?"
4. False pass = chala hi nahi ya kuch check nahi kiya. Executed/skipped counts ko gate banao.
5. AI tests: oracle spec se lo, mutation testing, negative/boundary cases check karo.
6. Docs: word-by-word follow karo, gaps ko assumptions ki tarah log karo, factual tone rakho.
7. Test design: BVA/EP ranges ke liye, decision table rules ke liye, state workflows ke liye, pairwise combos ke liye.
8. Flaky: quarantine + owner + SLA. Retries symptom chhupate hain.
9. Triage: repro → layer → test/env → spec → recent change → evidence.
10. RCA output = recurrence prevention, sirf fix nahi.
