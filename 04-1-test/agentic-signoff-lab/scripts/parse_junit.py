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
