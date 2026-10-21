#!/usr/bin/env python3
"""PreToolUse guard for Bash. Fail-closed: any internal error blocks."""
import fnmatch
import json
import re
import sys
from pathlib import Path

PATTERNS = [line.strip().lower()
            for line in (Path(__file__).with_name("prod_hosts.txt")).read_text().splitlines()
            if line.strip() and not line.startswith("#")]


def is_rm_rf(segment: str) -> bool:
    tokens = segment.split()
    if not any(t.split("/")[-1] == "rm" for t in tokens):
        return False
    short = "".join(t[1:] for t in tokens if t.startswith("-") and not t.startswith("--"))
    recursive = "r" in short.lower() or "--recursive" in tokens
    force = "f" in short or "--force" in tokens
    return recursive and force


def prod_target(segment: str):
    for raw in re.split(r"[\s'\"=]+", segment):
        host = re.sub(r"^\w+://", "", raw).split("@")[-1].split("/")[0].split(":")[0].lower()
        if host and any(fnmatch.fnmatch(host, p) for p in PATTERNS):
            return host
    return None


def main():
    try:
        cmd = json.load(sys.stdin).get("tool_input", {}).get("command", "")
        for seg in re.split(r"[;&|]+", cmd):
            if is_rm_rf(seg):
                sys.exit(block("recursive force delete (rm -rf)"))
            host = prod_target(seg)
            if host:
                sys.exit(block(f"production target '{host}'"))
    except SystemExit:
        raise
    except Exception as exc:  # fail closed
        sys.exit(block(f"guard error: {exc}"))
    sys.exit(0)


def block(reason: str) -> int:
    print(f"BLOCKED by guard_bash: {reason}. The command was not run. "
          "Ask the user for a safe alternative.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    main()
