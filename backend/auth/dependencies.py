from typing import Any, Dict

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from auth.jwt_handler import verify_access_token
from config.rate_limit_config import get_rate_limit_config
from utils.rate_limiter import get_rate_limiter


# OAuth2PasswordBearer extracts "Authorization: Bearer <token>"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    FastAPI dependency: verifies JWT and returns user claims.
    Raises 401 for missing/invalid/expired token.
    """
    if not token:
        # Usually handled by OAuth2PasswordBearer, but keep a hard guard.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_access_token(token)
    return {
        "user_id": payload["sub"],
        "role": payload["role"],
        "department": payload["department"],
    }

def rate_limit_user(endpoint: str):
    """
    Dependency factory for role-aware user-based rate limiting.
    Usage: Depends(rate_limit_user("chat"))
    """
    def _rate_limit_dependency(current_user: Dict[str, Any] = Depends(get_current_user)):
        config = get_rate_limit_config()
        role = current_user.get("role", "intern")
        user_id = current_user.get("user_id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found in token.",
            )

        # Get limits for user's role and endpoint
        role_config = config.get(role, config.get("intern", {}))
        endpoint_config = role_config.get(endpoint)

        if not endpoint_config:
            # No rate limit configured for this role/endpoint combination
            return current_user

        # Convert config to (limit, window_seconds) format
        limits = {}
        if "per_minute" in endpoint_config:
            limits["per_minute"] = (endpoint_config["per_minute"], 60)
        if "per_hour" in endpoint_config:
            limits["per_hour"] = (endpoint_config["per_hour"], 3600)
        if "per_day" in endpoint_config:
            limits["per_day"] = (endpoint_config["per_day"], 86400)

        if not limits:
            return current_user

        # Check rate limits
        limiter = get_rate_limiter()
        identifier = f"user:{user_id}:{endpoint}"
        allowed, retry_after, violated_window = limiter.check_multiple_limits(identifier, limits)

        if not allowed:
            window_display = violated_window.replace("_", " ").title() if violated_window else "rate limit"
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. You have exceeded the {window_display} limit for this endpoint.",
                headers={"Retry-After": str(retry_after) if retry_after else "60"},
            )

        return current_user

    return _rate_limit_dependency


def rate_limit_ip(endpoint: str, per_15min: int, per_hour: int):
    """
    Dependency factory for IP-based rate limiting.
    Usage: Depends(rate_limit_ip("login", 5, 10))
    """
    def _rate_limit_dependency(request: Request):
        client_ip = request.client.host if request.client else "unknown"

        limiter = get_rate_limiter()
        identifier = f"ip:{client_ip}:{endpoint}"

        limits = {
            "per_15min": (per_15min, 900),  # 15 minutes = 900 seconds
            "per_hour": (per_hour, 3600),
        }

        allowed, retry_after, violated_window = limiter.check_multiple_limits(identifier, limits)

        if not allowed:
            window_display = violated_window.replace("_", " ").title() if violated_window else "rate limit"
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Too many requests from your IP address. {window_display} limit exceeded.",
                headers={"Retry-After": str(retry_after) if retry_after else "60"},
            )

    return _rate_limit_dependency