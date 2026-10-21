#!/usr/bin/env python3
"""Deterministic batch checks for a synthetic score delivery. Prints JSON."""
import csv
import hashlib
import json
import sys
from pathlib import Path


def score_ok(value: str) -> bool:
    try:
        return 300 <= int(value) <= 850
    except ValueError:
        return False


def main(delivery_dir: str) -> None:
    d = Path(delivery_dir)
    manifest = json.loads((d / "manifest.json").read_text())
    raw = (d / manifest["file"]).read_bytes()
    rows = list(csv.DictReader(raw.decode("utf-8").splitlines()))
    refs = [r["consumer_ref"] for r in rows]
    bad_lines = [i for i, r in enumerate(rows, start=2) if not score_ok(r["score"])]
    checks = {
        "checksum_ok": hashlib.sha256(raw).hexdigest() == manifest["sha256"],
        "row_count_ok": len(rows) == manifest["expected_rows"],
        "no_duplicate_refs": len(refs) == len(set(refs)),
        "scores_in_range": not bad_lines,
    }
    print(json.dumps({"delivery_id": manifest["delivery_id"], "rows": len(rows),
                      "checks": checks, "bad_score_lines": bad_lines}, indent=2))


if __name__ == "__main__":
    main(sys.argv[1])
