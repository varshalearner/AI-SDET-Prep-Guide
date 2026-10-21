#!/usr/bin/env python3
"""Self-test for the lab hooks: pipes synthetic events and checks exit codes."""
import json
import subprocess
import sys
from pathlib import Path

HOOKS = Path(__file__).resolve().parent.parent / ".claude" / "hooks"

CASES = [
    ("guard_bash.py", {"tool_name": "Bash", "tool_input": {"command": "rm -rf reports"}}, 2),
    ("guard_bash.py", {"tool_name": "Bash", "tool_input": {"command": "rm -r -f reports"}}, 2),
    ("guard_bash.py", {"tool_name": "Bash", "tool_input": {"command": "ssh qa@score-prod-01 ls"}}, 2),
    ("guard_bash.py", {"tool_name": "Bash", "tool_input": {"command": "curl https://api.prod.example.internal/v1"}}, 2),
    ("guard_bash.py", {"tool_name": "Bash", "tool_input": {"command": "curl -d product=SCORE_8 http://127.0.0.1:8099/v1/score-requests"}}, 0),
    ("guard_bash.py", {"tool_name": "Bash", "tool_input": {"command": "git log -n 5"}}, 0),
    ("guard_bash.py", "not json", 2),
    ("mask_guard.py", {"tool_input": {"file_path": "reports/signoff.md", "content": "client CLI-0001"}}, 2),
    ("mask_guard.py", {"tool_input": {"file_path": "runs/DLV-0001/x/signoff.md", "content": "a@b.com"}}, 2),
    ("mask_guard.py", {"tool_input": {"file_path": "reports/signoff.md", "content": "client <ID>"}}, 0),
    ("mask_guard.py", {"tool_input": {"file_path": "tests/api/x.py", "content": "CLI-0001"}}, 0),
]

failed = 0
for hook, event, expected in CASES:
    data = event if isinstance(event, str) else json.dumps(event)
    r = subprocess.run([sys.executable, str(HOOKS / hook)], input=data, capture_output=True, text=True)
    ok = r.returncode == expected
    failed += not ok
    label = data if isinstance(event, str) else json.dumps(event["tool_input"])
    print(f"{'PASS' if ok else 'FAIL'}  {hook:<14} exit={r.returncode} expected={expected}  {label[:70]}")
print(f"\n{len(CASES) - failed}/{len(CASES)} passed")
sys.exit(1 if failed else 0)
