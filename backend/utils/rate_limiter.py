"""
In-memory rate limiter implementation.
Tracks requests per user_id/role or IP address with time-based windows.
"""
import time
from collections import defaultdict
from typing import Dict, Tuple, Optional
from threading import Lock
import logging

logger = logging.getLogger(__name__)


class InMemoryRateLimiter:
    """
    Thread-safe in-memory rate limiter.
    Stores request timestamps in nested dicts: {identifier: {window: [timestamps]}}
    """

    def __init__(self):
        self._storage: Dict[str, Dict[str, list]] = defaultdict(lambda: defaultdict(list))
        self._lock = Lock()

    def _cleanup_old_entries(self, identifier: str, window: str, window_seconds: int):
        """Remove timestamps older than the window."""
        current_time = time.time()
        cutoff = current_time - window_seconds

        with self._lock:
            if identifier in self._storage and window in self._storage[identifier]:
                self._storage[identifier][window] = [
                    ts for ts in self._storage[identifier][window] if ts > cutoff
                ]

    def check_rate_limit(
        self,
        identifier: str,
        limit: int,
        window_seconds: int,
        window_name: str = "default",
    ) -> Tuple[bool, Optional[int]]:
        """
        Check if request is within rate limit.
        Returns: (is_allowed, retry_after_seconds)
        """
        current_time = time.time()
        cutoff = current_time - window_seconds

        with self._lock:
            # Clean old entries
            if identifier in self._storage and window_name in self._storage[identifier]:
                self._storage[identifier][window_name] = [
                    ts for ts in self._storage[identifier][window_name] if ts > cutoff
                ]

            # Count requests in window
            request_count = len(self._storage[identifier][window_name])

            if request_count >= limit:
                # Calculate retry_after: oldest request + window_seconds - current_time
                oldest = min(self._storage[identifier][window_name]) if self._storage[identifier][window_name] else current_time
                retry_after = int((oldest + window_seconds) - current_time) + 1
                return False, max(1, retry_after)

            # Add current request
            self._storage[identifier][window_name].append(current_time)
            return True, None

    def check_multiple_limits(
        self,
        identifier: str,
        limits: Dict[str, Tuple[int, int]],
    ) -> Tuple[bool, Optional[int], Optional[str]]:
        """
        Check multiple rate limit windows (e.g., per_minute and per_hour).
        Returns: (is_allowed, retry_after_seconds, violated_window_name)
        """
        for window_name, (limit, window_seconds) in limits.items():
            allowed, retry_after = self.check_rate_limit(identifier, limit, window_seconds, window_name)
            if not allowed:
                return False, retry_after, window_name

        return True, None, None

    def reset(self, identifier: Optional[str] = None):
        """Reset rate limit data (for testing or manual cleanup)."""
        with self._lock:
            if identifier:
                if identifier in self._storage:
                    del self._storage[identifier]
            else:
                self._storage.clear()


# Global singleton instance
_rate_limiter = InMemoryRateLimiter()


def get_rate_limiter() -> InMemoryRateLimiter:
    """Get the global rate limiter instance."""
    return _rate_limiter