#!/usr/bin/env python3
"""Record a human approval on a completed sign-off run."""
import argparse
import datetime as dt
import json
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("run_dir")
ap.add_argument("--by", required=True)
ap.add_argument("--waiver", help="approved waiver id, required to approve a NO-GO")
a = ap.parse_args()

path = Path(a.run_dir) / "audit.json"
audit = json.loads(path.read_text())
verdict = audit["result"]["verdict"]
if verdict == "BLOCKED" or (verdict == "NO-GO" and not a.waiver):
    raise SystemExit(f"Refusing: verdict is {verdict}. BLOCKED cannot be approved; NO-GO needs --waiver.")
audit["human_approval"] = {"by": a.by, "utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                           "verdict": verdict, "waiver": a.waiver}
path.write_text(json.dumps(audit, indent=2))
print(f"Recorded approval of {verdict} by {a.by}")
