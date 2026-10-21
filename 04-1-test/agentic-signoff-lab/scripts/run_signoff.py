#!/usr/bin/env python3
"""Deterministic part of /signoff. Idempotent per (delivery_id, input hash)."""
import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable


def input_hash(ddir: Path) -> str:
    h = hashlib.sha256()
    files = sorted(p for p in ddir.rglob("*") if p.is_file())
    files += sorted((ROOT / "tests").rglob("*.py"))
    files.append(ROOT / "mock_api.py")            # system-under-test version
    for p in files:
        h.update(p.relative_to(ROOT).as_posix().encode())
        h.update(p.read_bytes())
    return h.hexdigest()[:16]


def load(path: Path):
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def decide(batch, summary):
    if batch is None or summary is None:
        return {"verdict": "BLOCKED", "reasons": ["a step produced no readable output"]}
    if summary["total"] == 0:
        return {"verdict": "BLOCKED", "reasons": ["zero tests ran"]}
    reasons = [f"batch check failed: {k}" for k, ok in batch["checks"].items() if not ok]
    if summary["failed"] + summary["errors"]:
        reasons.append(f'{summary["failed"]} failed, {summary["errors"]} errors')
    return {"verdict": "NO-GO" if reasons else "GO", "reasons": reasons}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("delivery_id")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    ddir = ROOT / "deliveries" / a.delivery_id
    if not re.fullmatch(r"DLV-\d{4}", a.delivery_id) or not (ddir / "manifest.json").exists():
        print(json.dumps({"verdict": "BLOCKED", "reasons": ["unknown or invalid delivery id"]}))
        return 3

    ih = input_hash(ddir)
    base = ROOT / "runs" / a.delivery_id
    for prev in sorted(base.glob("*/audit.json"), reverse=True):
        old = load(prev)
        if old and old["input_hash"] == ih and old["status"] == "complete" and not a.force:
            print(json.dumps({"reused_run": prev.parent.relative_to(ROOT).as_posix(), **old["result"]}))
            return 0

    run = base / dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run.mkdir(parents=True)
    try:
        git = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                             capture_output=True, text=True).stdout.strip()
    except OSError:  # git not installed
        git = ""
    audit = {"delivery_id": a.delivery_id, "input_hash": ih, "status": "running",
             "git_sha": git or "uncommitted", "python": sys.version.split()[0],
             "started_utc": run.name, "steps": [], "human_approval": None}

    def step(name, args, out):
        try:
            r = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=300)
            (run / out).write_text(r.stdout)
            code = r.returncode
        except subprocess.TimeoutExpired:
            code = "timeout"
        audit["steps"].append({"step": name, "args": [str(x) for x in args[1:]],
                               "exit": code, "output": out})

    step("batch_checks", [PY, "scripts/validate_batch.py", str(ddir)], "batch.json")
    step("api_tests", [PY, "-m", "pytest", "tests/api", "-q", f"--junitxml={run / 'junit.xml'}"], "pytest.txt")
    step("parse_results", [PY, "scripts/parse_junit.py", str(run / "junit.xml")], "summary.json")

    result = decide(load(run / "batch.json"), load(run / "summary.json"))
    result["run_dir"] = run.relative_to(ROOT).as_posix()
    audit.update(status="complete", result=result)
    (run / "audit.json").write_text(json.dumps(audit, indent=2))
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
