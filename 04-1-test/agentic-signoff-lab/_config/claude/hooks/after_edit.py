#!/usr/bin/env python3
"""PostToolUse on Edit|Write: run the edited test file; on failure tell Claude (exit 2)."""
import json
import subprocess
import sys

path = json.load(sys.stdin).get("tool_input", {}).get("file_path", "").replace("\\", "/")
if "/tests/" in f"/{path}" and path.endswith(".py"):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", path],
                       capture_output=True, text=True, timeout=50)
    if r.returncode != 0:
        print("Tests in edited file failed:\n" + r.stdout[-1500:], file=sys.stderr)
        sys.exit(2)
sys.exit(0)
