"""User authentication controller.

Endpoints (mounted under /api by main.py):
    POST /api/auth/signup  -> create account, set httpOnly session cookie
    POST /api/auth/login   -> verify credentials, set httpOnly session cookie
    POST /api/auth/logout  -> clear the session cookie
    GET  /api/auth/me      -> current user from the session cookie

The session is a signed JWT stored in an httpOnly cookie. Other routes can
depend on `get_current_user` to require an authenticated user.
"""
import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel

from db.SupabaseAPI import SupabaseAPI
from services.authService import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])
db = SupabaseAPI()

COOKIE_NAME = "access_token"
# In production (HTTPS) set COOKIE_SECURE=true so the cookie is only sent over TLS.
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"

PUBLIC_USER_FIELDS = ("id", "name", "email", "research_interests", "major", "created_at", "updated_at")


class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    research_interests: Optional[str] = None
    major: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


def _public_user(user: dict) -> dict:
    """Strip password_hash before returning a user to the client."""
    return {field: user.get(field) for field in PUBLIC_USER_FIELDS}


def _set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )


def get_current_user(request: Request) -> dict:
    """FastAPI dependency: resolve the logged-in user from the session cookie."""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session.")
    user = db.get_user_by_id(int(payload["sub"]))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User no longer exists.")
    return user


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, response: Response):
    if not payload.email or not payload.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email and password are required.")
    if db.get_user_by_email(payload.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists.")

    user = db.create_user(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        research_interests=payload.research_interests,
        major=payload.major,
    )
    token = create_access_token(user["id"], user["email"])
    _set_auth_cookie(response, token)
    return {"user": _public_user(user)}


@router.post("/login")
def login(payload: LoginRequest, response: Response):
    user = db.get_user_by_email(payload.email)
    if not user or not verify_password(payload.password, user.get("password_hash")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
    token = create_access_token(user["id"], user["email"])
    _set_auth_cookie(response, token)
    return {"user": _public_user(user)}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME, path="/")
    return {"message": "Logged out."}


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return {"user": _public_user(current_user)}
