"""Tests for the shared retry helper (call_with_retry)."""
import pytest

from opportunity_os.retry import call_with_retry


class Recorder:
    """Captures injected-sleep durations so backoff is asserted without waiting."""
    def __init__(self):
        self.delays = []

    def __call__(self, d):
        self.delays.append(d)


def test_returns_first_success_without_sleeping():
    sleep = Recorder()
    result = call_with_retry(lambda: 42, sleep=sleep)
    assert result == 42
    assert sleep.delays == []


def test_retries_then_succeeds():
    calls = {"n": 0}
    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ConnectionError("transient")
        return "ok"
    sleep = Recorder()
    result = call_with_retry(flaky, max_attempts=3, base_delay=0.5, sleep=sleep)
    assert result == "ok"
    assert calls["n"] == 3
    assert sleep.delays == [0.5, 1.0]  # exponential: 0.5 * 2**0, 0.5 * 2**1


def test_reraises_after_exhausting_attempts():
    def always_fails():
        raise TimeoutError("nope")
    sleep = Recorder()
    with pytest.raises(TimeoutError):
        call_with_retry(always_fails, max_attempts=3, sleep=sleep)
    assert len(sleep.delays) == 2  # slept between the 3 attempts, not after the last


def test_backoff_capped_at_max_delay():
    def always_fails():
        raise ConnectionError("x")
    sleep = Recorder()
    with pytest.raises(ConnectionError):
        call_with_retry(always_fails, max_attempts=5, base_delay=1.0, max_delay=3.0, sleep=sleep)
    # 1, 2, then capped at 3, 3
    assert sleep.delays == [1.0, 2.0, 3.0, 3.0]


def test_non_retryable_exception_propagates_immediately():
    def raises_value():
        raise ValueError("not retryable")
    sleep = Recorder()
    with pytest.raises(ValueError):
        call_with_retry(raises_value, retry_on=(ConnectionError,), sleep=sleep)
    assert sleep.delays == []  # never retried


def test_single_attempt_does_not_sleep():
    def fails():
        raise ConnectionError("x")
    sleep = Recorder()
    with pytest.raises(ConnectionError):
        call_with_retry(fails, max_attempts=1, sleep=sleep)
    assert sleep.delays == []


def test_invalid_max_attempts_rejected():
    with pytest.raises(ValueError):
        call_with_retry(lambda: 1, max_attempts=0)
