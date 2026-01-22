"""
IP-based rate limiting middleware for global protection.
Applies a per-IP hourly limit to all requests.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from fastapi import HTTPException, status
from config.rate_limit_config import get_ip_rate_limit_config
from utils.rate_limiter import get_rate_limiter
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware that applies global IP-based rate limiting.
    Excludes health check and root endpoints from rate limiting.
    """

    def __init__(self, app, exclude_paths: list = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/health", "/", "/docs", "/openapi.json", "/redoc"]
        self.config = get_ip_rate_limit_config()
        self.limiter = get_rate_limiter()

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        identifier = f"ip:{client_ip}:global"

        # Check global hourly limit
        limit = self.config.get("global_per_hour", 1000)
        allowed, retry_after = self.limiter.check_rate_limit(
            identifier, limit, 3600, "per_hour"
        )

        if not allowed:
            logger.warning(f"Global rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
                headers={"Retry-After": str(retry_after) if retry_after else "3600"},
            )

        response = await call_next(request)
        return response