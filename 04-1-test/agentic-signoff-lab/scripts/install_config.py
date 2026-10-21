#!/usr/bin/env python3
"""Copy _config/claude -> .claude and _config/github -> .github (run once, after reviewing the files)."""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for src, dst in (("_config/claude", ".claude"), ("_config/github", ".github")):
    shutil.copytree(ROOT / src, ROOT / dst, dirs_exist_ok=True)
    for f in sorted((ROOT / dst).rglob("*")):
        if f.is_file():
            print("installed", f.relative_to(ROOT).as_posix())
