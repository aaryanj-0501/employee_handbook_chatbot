from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

from auth.jwt_handler import create_access_token,verify_access_token
from auth.dependencies import get_current_user
from main import app

def override_get_current_user():
    return {"username": "test-user"}

app.dependency_overrides[get_current_user] = override_get_current_user

class TestAuth:
    def test_login_success(self):
        """Test to check login success"""
        client=TestClient(app)
        response=client.post("/login",data={"username":"admin","password":"admin123"},headers={"Content-Type": "application/x-www-form-urlencoded"})
        assert response.status_code==200
        assert response.json()["access_token"] is not None
        assert response.json()["token_type"]=="bearer"

    def test_login_failure(self):
        """Test to check login failure"""
        client=TestClient(app)
        response=client.post("/login",data={"username":"admin","password":"wrong_password"},headers={"Content-Type": "application/x-www-form-urlencoded"})
        assert response.status_code==401
        assert response.json()["detail"]=="Invalid username or password"

    def test_create_access_token(self):
        """Test to create access token"""
        token=create_access_token(sub="admin",role="admin",department="IT")
        assert token is not None
        assert token.split(".")[1] is not None
        assert token.split(".")[2] is not None        

    def test_verify_access_token(self):
        """Test to validate access token"""
        token=create_access_token(sub="admin",role="admin",department="IT")
        payload=verify_access_token(token)
        assert payload is not None
        assert payload["sub"]=="admin"
        assert payload["role"]=="admin"
        assert payload["department"]=="IT"
        assert payload["exp"] is not None
        assert payload["exp"] > int(datetime.now(timezone.utc).timestamp())
        assert payload["exp"] <= int(datetime.now(timezone.utc).timestamp()+30*60)
        assert payload["exp"] <= int(datetime.now(timezone.utc).timestamp()+30*60)

    def test_get_current_user(self):
        """Test to get the current user"""
        token=create_access_token(sub="admin",role="admin",department="IT")
        payload=get_current_user(token)
        assert payload is not None
        assert payload["user_id"]=="admin"
        assert payload["role"]=="admin"
        assert payload["department"]=="IT"