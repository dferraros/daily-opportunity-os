#!/usr/bin/env python3
"""Pre-commit gate: keep out-of-scope content from entering this repo.

Blocks commits whose staged content contains any denylisted token. Tokens are
stored as SHA-256 hashes so the denylist itself stays private; staged text is
tokenized and each token is hashed for comparison.

Install (once per clone):
    py scripts/git-hooks/check_forbidden_content.py --install
"""
from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path

# SHA-256 hashes of lowercase denylisted tokens (list is intentionally opaque).
DENYLIST_HASHES = {
    "8569e923144d208ea660a28bf4c3e72d6e6915f3f9abeed426fab6b576029a3d",
    "318ebbe829f3c9caff52400ea7512cbcc27ed2e9100a85e342883225b65235e7",
    "ef3dfd0f0e4ac3a31f8852177c21b1bee30dc59758e49130f5c74e8df39b1eac",
    "5d86e825e7ba8275ca02f8452385401bf04c6cce5d799c26c84bec9e3bfdfe9a",
}
TOKEN_RE = re.compile(r"[a-z0-9]+")
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


def line_is_clean(line: str) -> bool:
    for token in TOKEN_RE.findall(line.lower()):
        if hashlib.sha256(token.encode()).hexdigest() in DENYLIST_HASHES:
            return False
    return True


def find_violations() -> list[tuple[str, int]]:
    violations = []
    for path in staged_files():
        for lineno, line in enumerate(staged_content(path).splitlines(), 1):
            if not line_is_clean(line):
                violations.append((path, lineno))
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
    sys.stderr.write("COMMIT BLOCKED: staged content is out of scope for this repo:\n")
    for path, lineno in violations:
        sys.stderr.write(f"  {path}:{lineno}\n")
    sys.stderr.write("Remove the flagged lines (do not bypass with --no-verify).\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
