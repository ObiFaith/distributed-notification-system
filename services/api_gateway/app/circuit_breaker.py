# app/circuit_breaker.py
import asyncio
import time
from typing import Callable, Any

class SimpleCircuitBreaker:
    """
    Very simple CB for external synchronous calls (e.g., calls to SMTP or 3rd party).
    States: CLOSED -> OPEN -> HALF-OPEN (trial) -> CLOSED on success
    """
    def __init__(self, max_failures=5, reset_timeout=30):
        self.max_failures = max_failures
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.state = "CLOSED"
        self.opened_since = None

    def record_failure(self):
        self.failure_count += 1
        if self.failure_count >= self.max_failures:
            self.state = "OPEN"
            self.opened_since = time.time()

    def record_success(self):
        self.failure_count = 0
        self.state = "CLOSED"
        self.opened_since = None

    def allow(self):
        if self.state == "OPEN":
            if time.time() - self.opened_since > self.reset_timeout:
                # move to half-open - allow a trial
                self.state = "HALF-OPEN"
                return True
            return False
        return True

# Example usage (shared across components that call risky services)
gateway_cb = SimpleCircuitBreaker(max_failures=3, reset_timeout=20)
