#!/usr/bin/env python3
"""Pre-commit gate: block forbidden strings from entering this repo.

This repo (daily-opportunity-os, public on GitHub) must contain ZERO content
from Daniel's employer or unrelated ventures. History was purged once with
git-filter-repo (2026-06-12) after contamination reached the public remote;
this gate makes recurrence impossible at commit time instead of cleanup time.

Install (once per clone):
    py scripts/git-hooks/check_forbidden_content.py --install

Patterns are assembled from fragments so this file never matches itself.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# Assembled at runtime so the gate never flags its own source.
FORBIDDEN = [
    "bit" + "2me",
    "oik" + "os",
    "clever" + "tap",
    "b2m" + "e",
]
SELF = "check_forbidden_content"
HOOK_SHIM = "#!/bin/sh\npy scripts/git-hooks/check_forbidden_content.py || exit 1\n"


def staged_files() -> list[str]:
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True, text=True, check=True,
    )
    return [f for f in out.stdout.splitlines() if f and SELF not in f]


def staged_content(path: str) -> str:
    out = subprocess.run(
        ["git", "show", f":{path}"], capture_output=True, text=True,
    )
    return out.stdout if out.returncode == 0 else ""


def find_violations() -> list[tuple[str, int, str]]:
    violations = []
    for path in staged_files():
        content = staged_content(path)
        low_lines = content.lower().splitlines()
        for lineno, line in enumerate(low_lines, 1):
            for pat in FORBIDDEN:
                if pat in line:
                    violations.append((path, lineno, pat))
    return violations


def install() -> int:
    root = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    hook = Path(root) / ".git" / "hooks" / "pre-commit"
    hook.write_text(HOOK_SHIM, encoding="utf-8", newline="\n")
    sys.stderr.write(f"installed pre-commit gate at {hook}\n")
    return 0


def main() -> int:
    if "--install" in sys.argv:
        return install()
    violations = find_violations()
    if not violations:
        return 0
    sys.stderr.write(
        "COMMIT BLOCKED: forbidden content (this is a public repo that must "
        "stay free of employer/other-venture strings):\n"
    )
    for path, lineno, pat in violations:
        sys.stderr.write(f"  {path}:{lineno}: contains '{pat}'\n")
    sys.stderr.write("Remove the content (do not bypass with --no-verify).\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
