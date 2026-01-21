from datetime import timedelta
from typing import Dict
from fastapi import APIRouter,HTTPException,status,Depends
from fastapi.security import OAuth2PasswordRequestForm
from auth.jwt_handler import create_access_token

router=APIRouter()

# MOCK  user data
MOCK_USERS: Dict[str, Dict[str,str]]={
    "admin":{"password":"admin123","role":"admin","department":"IT"},
    "user":{"password":"user123","role":"employee","department":"HR"},
    "intern":{"password":"intern123","role":"intern","department":"Finance"}
}

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm=Depends()):
    """
    Docstring for login
    
    :param form_data: Description
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
    
