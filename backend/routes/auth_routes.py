from datetime import timedelta
from typing import Dict
from fastapi import APIRouter,HTTPException,status,Depends,Request
from fastapi.security import OAuth2PasswordRequestForm
from backend.auth.jwt_handler import create_access_token
from backend.auth.dependencies import rate_limit_ip
from backend.config.rate_limit_config import get_ip_rate_limit_config

router=APIRouter()

# MOCK  user data
MOCK_USERS: Dict[str, Dict[str,str]]={
    "admin":{"password":"admin123","role":"admin","department":"IT"},
    "user":{"password":"user123","role":"employee","department":"HR"},
    "intern":{"password":"intern123","role":"intern","department":"Finance"}
}

_ip_config=get_ip_rate_limit_config()
_login_rate_limit=rate_limit_ip("login",_ip_config["login_per_15min"],_ip_config["login_per_15min"])

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm=Depends(),_:None=Depends(_login_rate_limit)):
    """
    Docstring for login
    
    :param form_data: username and backend.password
    :type form_data: OAuth2PasswordRequestForm
    """
    if form_data is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Missing form data")
    
    username=(form_data.username or "").strip()
    password=form_data.password or ""

    user=MOCK_USERS.get(username)
    if not user or user.get("password")!=password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate":"Bearer"}
        )
    
    token=create_access_token(
        sub=username,
        role=user["role"],
        department=user["department"],
        expires_delta=timedelta(minutes=30)
    )

    return {"access_token":token,"token_type":"bearer"}
    
