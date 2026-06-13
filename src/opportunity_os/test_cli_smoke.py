"""
CLI smoke tests -- every command must import cleanly and have valid option wiring.

`<cmd> --help` exercises Click's parameter validation and forces import of the
command's module-level dependencies, so this catches the failure modes a
hand-added command risks: a typo'd decorator, a bad option type, or an import
that only blows up at invocation. Introspects cli.commands so new commands are
covered automatically; a frozen expected-set guard catches silent removal/rename.
"""
from click.testing import CliRunner

from opportunity_os.main import cli

# Frozen snapshot of the command surface (2026-06-12). Update deliberately when
# adding/removing a command -- a diff here should be a conscious decision.
EXPECTED_COMMANDS = frozenset({
    "apify-research", "audit", "backup", "backups", "build", "calibrate",
    "daily", "deep-dive", "export", "free-research", "harvest", "kickoff",
    "kill-thesis", "like", "liked", "outcome", "rescore-all", "research",
    "restore", "search", "stats", "validate", "weekly",
})


def test_command_set_matches_expected():
    """The registered command surface must match the frozen snapshot exactly."""
    registered = set(cli.commands.keys())
    missing = EXPECTED_COMMANDS - registered
    unexpected = registered - EXPECTED_COMMANDS
    assert not missing, f"Commands disappeared from CLI: {sorted(missing)}"
    assert not unexpected, (
        f"New commands not in EXPECTED_COMMANDS (add them deliberately): {sorted(unexpected)}"
    )


def test_top_level_help_works():
    result = CliRunner().invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Commands:" in result.output


def test_every_command_help_succeeds():
    """`<cmd> --help` must exit 0 for every registered command.

    Exercises Click option wiring + forces import of each command's deps.
    """
    runner = CliRunner()
    failures = []
    for name in sorted(cli.commands):
        result = runner.invoke(cli, [name, "--help"])
        if result.exit_code != 0:
            detail = result.output.strip().splitlines()[-3:] if result.output else []
            failures.append(f"{name}: exit {result.exit_code} {detail}")
    assert not failures, "Commands with broken --help:\n" + "\n".join(failures)
