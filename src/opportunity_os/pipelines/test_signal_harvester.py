"""Tests for signal_harvester.py noise gate."""
import pytest
from opportunity_os.pipelines.signal_harvester import _is_noise_signal


def _make_signal(name: str, description: str = "some description about a market") -> dict:
    return {
        "name": name,
        "description": description,
        "geography": "venezuela",
        "vertical": "fintech",
        "source_url": "https://reddit.com/r/vzla/abc",
        "raw_notes": "Reddit r/vzla.",
        "harvested_at": "2026-05-20",
    }


def test_noise_gate_blocks_first_person_post():
    assert _is_noise_signal(_make_signal("I need help finding a bank that works in Venezuela")) is True


def test_noise_gate_blocks_question_post():
    assert _is_noise_signal(_make_signal("Does anyone know how to transfer money in Venezuela")) is True


def test_noise_gate_blocks_short_name():
    assert _is_noise_signal(_make_signal("help with money")) is True  # 3 words


def test_noise_gate_allows_valid_opportunity():
    signal = _make_signal(
        "Venezuelan fintech startup raises seed round for remittance corridor",
        "A Caracas-based startup has raised $1.2M to build remittance infrastructure.",
    )
    assert _is_noise_signal(signal) is False


def test_noise_gate_allows_market_signal():
    signal = _make_signal(
        "LATAM payment infrastructure gap leaves SMBs without banking access",
        "Small businesses across Latin America cannot access credit or payment rails.",
    )
    assert _is_noise_signal(signal) is False


def test_noise_gate_case_insensitive():
    assert _is_noise_signal(_make_signal("MY PROBLEM with banking in Venezuela")) is True
