"""Tests for the unified .env bootstrap (env.py)."""

import os

from opportunity_os.env import get_key, load_env_file


def test_loads_keys_and_skips_placeholders(tmp_path, monkeypatch):
    monkeypatch.delenv("OPP_OS_SKIP_DOTENV", raising=False)
    monkeypatch.delenv("TEST_REAL_KEY", raising=False)
    monkeypatch.delenv("TEST_PLACEHOLDER_KEY", raising=False)
    env = tmp_path / ".env"
    env.write_text(
        "# comment\n"
        "TEST_REAL_KEY=abc123\n"
        "TEST_PLACEHOLDER_KEY=your_key_here\n"
        'TEST_QUOTED_KEY="quoted-value"\n'
        "\n"
        "not a kv line\n",
        encoding="utf-8",
    )

    loaded = load_env_file(str(env))

    assert loaded == 2
    assert os.environ["TEST_REAL_KEY"] == "abc123"
    assert os.environ["TEST_QUOTED_KEY"] == "quoted-value"
    assert "TEST_PLACEHOLDER_KEY" not in os.environ
    monkeypatch.delenv("TEST_REAL_KEY", raising=False)
    monkeypatch.delenv("TEST_QUOTED_KEY", raising=False)


def test_existing_env_vars_win(tmp_path, monkeypatch):
    monkeypatch.delenv("OPP_OS_SKIP_DOTENV", raising=False)
    monkeypatch.setenv("TEST_PRECEDENCE_KEY", "from-environment")
    env = tmp_path / ".env"
    env.write_text("TEST_PRECEDENCE_KEY=from-dotenv\n", encoding="utf-8")

    load_env_file(str(env))

    assert os.environ["TEST_PRECEDENCE_KEY"] == "from-environment"


def test_skip_flag_disables_loading(tmp_path, monkeypatch):
    monkeypatch.setenv("OPP_OS_SKIP_DOTENV", "1")
    env = tmp_path / ".env"
    env.write_text("TEST_SKIPPED_KEY=value\n", encoding="utf-8")

    assert load_env_file(str(env)) == 0
    assert "TEST_SKIPPED_KEY" not in os.environ


def test_missing_file_returns_zero(tmp_path, monkeypatch):
    monkeypatch.delenv("OPP_OS_SKIP_DOTENV", raising=False)
    assert load_env_file(str(tmp_path / "nope.env")) == 0


# ─── get_key: the single accessor the API clients now route through ───────────

def test_get_key_returns_value_already_in_environ(monkeypatch):
    monkeypatch.setenv("OPP_OS_SKIP_DOTENV", "1")  # prove it does not need .env
    monkeypatch.setenv("TEST_GETKEY", "live-value")
    assert get_key("TEST_GETKEY") == "live-value"


def test_get_key_treats_placeholder_as_unset(monkeypatch):
    monkeypatch.setenv("OPP_OS_SKIP_DOTENV", "1")
    monkeypatch.setenv("TEST_GETKEY_PH", "your_key_here")
    assert get_key("TEST_GETKEY_PH") is None


def test_get_key_missing_returns_none(monkeypatch):
    monkeypatch.setenv("OPP_OS_SKIP_DOTENV", "1")
    monkeypatch.delenv("TEST_GETKEY_ABSENT", raising=False)
    assert get_key("TEST_GETKEY_ABSENT") is None


def test_get_key_respects_skip_flag_does_not_read_dotenv(tmp_path, monkeypatch):
    """The isolation guarantee: with the skip flag set, get_key never reads a
    real .env -- the exact leak the per-client loaders had before consolidation."""
    monkeypatch.setenv("OPP_OS_SKIP_DOTENV", "1")
    monkeypatch.delenv("SECRET_FROM_DOTENV", raising=False)
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("SECRET_FROM_DOTENV=should-not-be-read\n", encoding="utf-8")
    assert get_key("SECRET_FROM_DOTENV") is None
