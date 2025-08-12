import os
import time
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple

import jwt
import bcrypt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .database import get_db
from app.models.orm import User, RefreshToken


JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret_change_me")
JWT_ALG = "HS256"
ACCESS_EXPIRES_MIN = int(os.getenv("JWT_EXPIRES_IN_MIN", "15"))
REFRESH_EXPIRES_DAYS = int(os.getenv("REFRESH_EXPIRES_IN_DAYS", "14"))


def hash_password(plain: str) -> Tuple[str, str]:
    salt = bcrypt.gensalt().decode()
    digest = bcrypt.hashpw(plain.encode(), salt.encode()).decode()
    return digest, salt


def verify_password(plain: str, digest: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), digest.encode())
    except Exception:
        return False


def _now_ts() -> int:
    return int(time.time())


def create_access_token(user: User) -> str:
    exp = datetime.utcnow() + timedelta(minutes=ACCESS_EXPIRES_MIN)
    payload = {
        "sub": str(user.id),
        "role": user.role,
        "exp": exp,
        "type": "access",
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def create_refresh_token(user: User, jti: Optional[str] = None, expires_days: Optional[int] = None) -> Tuple[str, str, datetime]:
    jti = jti or secrets.token_hex(16)
    days = expires_days if expires_days is not None else REFRESH_EXPIRES_DAYS
    exp = datetime.utcnow() + timedelta(days=days)
    payload = {
        "sub": str(user.id),
        "role": user.role,
        "jti": jti,
        "exp": exp,
        "type": "refresh",
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)
    return token, jti, exp


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


bearer_scheme = HTTPBearer(auto_error=False)


def _extract_token_from_cookies(request: Request, cookie_name: str) -> Optional[str]:
    token = request.cookies.get(cookie_name)
    if token:
        return token
    return None


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> User:
    token: Optional[str] = None
    # 1) httpOnly 쿠키 우선
    token = _extract_token_from_cookies(request, "access_token")
    # 2) Authorization: Bearer
    if not token and creds and creds.scheme.lower() == "bearer":
        token = creds.credentials
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")
    user = db.query(User).filter(User.id == int(payload["sub"])) .first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_role(roles: list[str]):
    def _dep(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return _dep


# CSRF Protection (Double Submit Cookie)
CSRF_HEADER_NAME = "x-csrf-token"


def generate_csrf_token() -> str:
    return secrets.token_hex(16)


def require_csrf(request: Request) -> None:
    """Validate CSRF token via double submit cookie pattern.
    Compares header X-CSRF-Token with cookie 'csrf_token'.
    """
    header = request.headers.get(CSRF_HEADER_NAME)
    cookie = request.cookies.get("csrf_token")
    if not header or not cookie or header != cookie:
        raise HTTPException(status_code=403, detail="CSRF validation failed")


