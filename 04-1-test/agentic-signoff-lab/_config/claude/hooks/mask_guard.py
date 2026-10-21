#!/usr/bin/env python3
"""PreToolUse on Write|Edit: block unmasked identifiers in reports/ and runs/. Fail-closed."""
import json
import re
import sys

UNMASKED = re.compile(r"\b(?:CLI|CON)-\d+\b|[\w.+-]+@[\w-]+\.[\w.]+|\b\d{9,}\b")

try:
    event = json.load(sys.stdin)
    ti = event.get("tool_input", {})
    path = ti.get("file_path", "").replace("\\", "/")
    text = ti.get("content") or ti.get("new_string") or ""
    if any(f"/{d}/" in f"/{path}" for d in ("reports", "runs")):
        hits = sorted(set(UNMASKED.findall(text)))
        if hits:
            print(f"BLOCKED: {len(hits)} unmasked identifier(s) in {path}. "
                  "Replace with <ID>/<EMAIL>/<NUM> and retry.", file=sys.stderr)
            sys.exit(2)
except Exception as exc:
    print(f"mask_guard error: {exc}; blocking by default", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
