---
name: signoff
description: Run the end-to-end QA sign-off for one synthetic score delivery and draft the report. Manual only.
argument-hint: [delivery-id e.g. DLV-0001]
disable-model-invocation: true
allowed-tools: Bash(python scripts/run_signoff.py *) Read
---
# /signoff $0

## Standing rules
- The verdict comes ONLY from run_signoff.py output. Never change, soften or re-derive it.
- Numbers come only from files in the run directory. Do no arithmetic of your own.
- If the output says BLOCKED, report BLOCKED with its reasons and stop.
- Mask identifiers. Never quote rows from deliveries/*/scores.csv.
- Never publish, email, approve, or file tickets. This workflow ends at a draft plus a request for human approval.

## Steps
1. Run `python scripts/run_signoff.py $0`. Note `run_dir`.
2. If verdict is NO-GO and `<run_dir>/summary.json` has failures, use the failure-triager subagent on `<run_dir>/junit.xml` and include its table.
3. Fill `templates/report.md` into `<run_dir>/signoff.md`. Put failed batch checks and failed tests under "Blocking issues".
4. Show the verdict, reasons and the path to signoff.md. Then say:
   "To approve, run: python scripts/approve.py <run_dir> --by <your-name>" — and stop.
