"""
Reports -- Jinja2 rendering helpers for opportunity reports.

Provides:
- render_template(template_name, context) -> rendered markdown string
- report_path(report_type, date) -> absolute path for output file
- Custom Jinja2 filters (format_tam, truncate_smart)
- ensure_report_dirs() -- creates all report directories
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import jinja2
    from jinja2 import Environment, FileSystemLoader
    _JINJA2_AVAILABLE = True
except ImportError:
    _JINJA2_AVAILABLE = False
    jinja2 = None  # type: ignore


def get_project_root() -> str:
    """Walk up from this file to find pyproject.toml (project root)."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return str(parent)
    return str(current.parents[3])  # fallback: 4 levels up from src/opportunity_os/


def format_tam(value) -> str:
    """Jinja2 filter: format TAM number as $10M, $1.2B, etc."""
    if value is None:
        return "Unknown"
    try:
        v = float(value)
        if v >= 1_000_000_000:
            return f"${v/1_000_000_000:.1f}B"
        elif v >= 1_000_000:
            return f"${v/1_000_000:.0f}M"
        elif v >= 1_000:
            return f"${v/1_000:.0f}K"
        return f"${v:.0f}"
    except (TypeError, ValueError):
        return str(value)


def truncate_smart(value: str, length: int = 120) -> str:
    """Jinja2 filter: truncate a string at a word boundary."""
    if not value:
        return ""
    if len(value) <= length:
        return value
    truncated = value[:length].rsplit(" ", 1)[0]
    return truncated + "..."


def get_jinja_env():
    """Build Jinja2 Environment with custom filters and templates dir."""
    if not _JINJA2_AVAILABLE:
        raise ImportError(
            "jinja2 is required for report rendering. "
            "Install it with: pip install jinja2"
        )
    templates_dir = os.path.join(get_project_root(), "templates", "reports")
    env = Environment(
        loader=FileSystemLoader(templates_dir),
        trim_blocks=True,
        lstrip_blocks=True,
        undefined=jinja2.Undefined,
    )
    env.filters["format_tam"] = format_tam
    env.filters["truncate_smart"] = truncate_smart
    return env


def render_template(template_name: str, context: dict) -> str:
    """Render a .j2 template with the given context. Returns markdown string."""
    try:
        env = get_jinja_env()
        template = env.get_template(template_name)
        return template.render(**context)
    except Exception as e:
        # Graceful fallback: return a minimal markdown report with error context
        return f"# Report Error\nFailed to render {template_name}: {e}\n"


def report_path(report_type: str, report_date: Optional[str] = None) -> str:
    """
    Build output path for a report.
    report_type: 'daily' | 'latam' | 'venezuela' | 'weekly' | 'deep-dive'
    Returns absolute path string.
    """
    root = get_project_root()
    if report_date is None:
        report_date = datetime.now().strftime("%Y-%m-%d")

    if report_type == "weekly":
        week = datetime.now().strftime("%Y-W%W")
        return os.path.join(root, "reports", "weekly", f"{week}-summary.md")
    elif report_type == "deep-dive":
        return os.path.join(root, "reports", "deep-dives", f"{report_date}-deep-dive.md")
    else:
        filename = f"{report_date}-{report_type}.md"
        return os.path.join(root, "reports", "daily", filename)


def ensure_report_dirs():
    """Create all report output directories."""
    root = get_project_root()
    dirs = [
        os.path.join(root, "reports", "daily"),
        os.path.join(root, "reports", "weekly"),
        os.path.join(root, "reports", "deep-dives"),
        os.path.join(root, "exports", "notion"),
        os.path.join(root, "data", "opportunities"),
        os.path.join(root, "data", "raw"),
        os.path.join(root, "data", "samples"),
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def write_report(content: str, path: str) -> str:
    """Write rendered report to disk. Returns path written."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path
