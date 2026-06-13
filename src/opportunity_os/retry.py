"""
Shared retry helper for transient external-call failures.

The API clients (tavily, firecrawl, apify, anthropic) historically returned None
on the FIRST exception, so a single timeout or connection reset silently dropped
a research result. This wraps a call with bounded exponential backoff on a
configurable exception set. `sleep` is injectable so tests run instantly and
deterministically.

Deliberately minimal: retries on exceptions only. Non-retryable outcomes (an
HTTP 200 with empty results, a 4xx the server will keep rejecting) are the
caller's concern -- this helper does not interpret return values.
"""

from __future__ import annotations

import logging
import time
from typing import Callable, Tuple, Type, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_BASE_DELAY = 0.5   # seconds; doubles each retry
DEFAULT_MAX_DELAY = 8.0    # cap per-attempt backoff


def call_with_retry(
    fn: Callable[[], T],
    *,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    base_delay: float = DEFAULT_BASE_DELAY,
    max_delay: float = DEFAULT_MAX_DELAY,
    retry_on: Tuple[Type[BaseException], ...] = (Exception,),
    label: str = "call",
    sleep: Callable[[float], None] = time.sleep,
) -> T:
    """Call ``fn`` with bounded exponential backoff on ``retry_on`` exceptions.

    Returns fn()'s result on the first success. Re-raises the last exception
    after ``max_attempts`` failures. Backoff for attempt n (1-indexed) is
    ``min(max_delay, base_delay * 2**(n-1))``.

    Args:
        fn: zero-arg callable performing the external request.
        max_attempts: total tries including the first (must be >= 1).
        retry_on: exception types that trigger a retry; others propagate immediately.
        label: name used in log lines.
        sleep: injected for tests; defaults to time.sleep.
    """
    if max_attempts < 1:
        raise ValueError("max_attempts must be >= 1")

    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except retry_on as exc:
            if attempt == max_attempts:
                logger.warning("%s failed after %d attempt(s): %s", label, attempt, exc)
                raise
            delay = min(max_delay, base_delay * 2 ** (attempt - 1))
            logger.info(
                "%s attempt %d/%d failed (%s); retrying in %.2fs",
                label, attempt, max_attempts, exc, delay,
            )
            sleep(delay)
    # Unreachable: the loop either returns or raises. Present for type-checkers.
    raise RuntimeError(f"{label}: retry loop exited without return or raise")
