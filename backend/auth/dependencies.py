from typing import Any, Dict

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from auth.jwt_handler import verify_access_token


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