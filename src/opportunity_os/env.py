"""Project .env bootstrap -- one loader for every API key.

Called once at CLI / dashboard startup. Populates os.environ from the .env at
the project root so every module's os.environ.get() works uniformly --
previously only Tavily/Apify/Firecrawl walked the .env file themselves while
Serper/Exa/Reddit read environment variables only, so keys placed in .env were
silently ignored for half the sources.

Rules:
- Existing environment variables always win (never overwritten).
- Placeholder values ("your_key_here") and blank values are skipped.
- Set OPP_OS_SKIP_DOTENV=1 to disable (used by the test suite).
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

PLACEHOLDER = "your_key_here"


def _find_env_file() -> Optional[Path]:
    current = Path(__file__).resolve().parent
    for parent in [current] + list(current.parents):
        if (parent / "pyproject.toml").exists():
            candidate = parent / ".env"
            return candidate if candidate.exists() else None
    return None


def load_env_file(path: Optional[str] = None) -> int:
    """Load KEY=value pairs from .env into os.environ. Returns count loaded."""
    if os.environ.get("OPP_OS_SKIP_DOTENV"):
        return 0

    env_path = Path(path) if path else _find_env_file()
    if env_path is None or not env_path.exists():
        return 0

    loaded = 0
    try:
        lines = env_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        logger.warning("[env] could not read %s: %s", env_path, exc)
        return 0

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if not key or not val or val == PLACEHOLDER:
            continue
        if key not in os.environ:
            os.environ[key] = val
            loaded += 1

    if loaded:
        logger.debug("[env] loaded %d keys from %s", loaded, env_path)
    return loaded


def get_key(name: str) -> Optional[str]:
    """Return an API key from the environment, loading .env on first miss.

    Single source of truth for API-key access. Replaces the per-client .env
    walkers (tavily/apify/firecrawl/ai_scorer), which each re-implemented this
    AND ignored OPP_OS_SKIP_DOTENV -- meaning they could read the real .env
    during tests. Routing through load_env_file() closes that isolation hole:
    when the skip flag is set, no .env is read and only os.environ is consulted.

    Placeholder values ("your_key_here") and empty strings are treated as unset.
    """
    val = os.environ.get(name)
    if val is None:
        load_env_file()  # idempotent, respects OPP_OS_SKIP_DOTENV, only fills missing keys
        val = os.environ.get(name)
    if not val or val == PLACEHOLDER:
        return None
    return val
