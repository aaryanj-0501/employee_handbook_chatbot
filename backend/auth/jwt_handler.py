import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple
from fastapi import HTTPException, status
from jose import JWTError,jwt # type: ignore

def create_access_token(
    *,
    sub: str,
    role: str,
    department: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a signed JWT access token.
    Required claims: sub, role, department, exp
    """
    secret_key = os.getenv("JWT_SECRET_KEY")
    algorithm = os.getenv("JWT_ALGORITHM", "HS256")
    default_exp_minutes = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    now = datetime.now(timezone.utc)
    expire = now + (expires_delta if expires_delta is not None else timedelta(minutes=default_exp_minutes))

    to_encode: Dict[str, Any] = {
        "sub": sub,
        "role": role,
        "department": department,
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


def verify_access_token(token: str) -> Dict[str, Any]:
    """
    Verify JWT signature + required claims + explicit expiry validation.
    Raises 401 on invalid/missing/expired token.
    """
    secret_key = os.getenv("JWT_SECRET_KEY")
    algorithm = os.getenv("JWT_ALGORITHM", "HS256")

    try:
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=[algorithm],
            options={
                "verify_signature": True,
                "verify_exp": False,  # we validate exp explicitly below for clarity
                "require_exp": True,
            },
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    sub = payload.get("sub")
    role = payload.get("role")
    department = payload.get("department")
    exp = payload.get("exp")

    if not sub or not role or not department or exp is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing required claims.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Explicit expiry validation
    try:
        exp_int = int(exp)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has an invalid expiry.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    now_ts = int(datetime.now(timezone.utc).timestamp())
    if exp_int <= now_ts:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload