from datetime import datetime
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, Response, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    generate_csrf_token,
)
from app.models.orm import User, RefreshToken


router = APIRouter()


class RegisterDto(BaseModel):
    email: EmailStr
    password: str
    display_name: str | None = None


class LoginDto(BaseModel):
    email: EmailStr
    password: str
    remember: bool | None = True


@router.post("/auth/register")
def register(body: RegisterDto, response: Response, db: Session = Depends(get_db)) -> Dict:
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    pwd_hash, pwd_salt = hash_password(body.password)
    user = User(
        email=body.email,
        password_hash=pwd_hash,
        password_salt=pwd_salt,
        role="student",
        display_name=body.display_name,
        created_at=datetime.utcnow(),
    )
    db.add(user)
    db.flush()
    # issue tokens
    access = create_access_token(user)
    # 회원가입 시에는 기본 30일로 설정 (remember me 기본값 적용)
    refresh_days = 30
    refresh, jti, exp = create_refresh_token(user, expires_days=refresh_days)
    db.add(RefreshToken(id=jti, user_id=user.id, issued_at=datetime.utcnow(), expires_at=exp, revoked=False))
    db.commit()
    resp = {"id": user.id, "email": user.email, "role": user.role, "display_name": user.display_name}
    response.set_cookie("access_token", access, httponly=True, samesite="lax")
    # refresh는 기본 30일로 설정
    max_age = refresh_days * 24 * 60 * 60
    response.set_cookie("refresh_token", refresh, httponly=True, samesite="lax", max_age=max_age)
    # CSRF 토큰 발급 (더블 서브밋 쿠키)
    response.set_cookie("csrf_token", generate_csrf_token(), httponly=False, samesite="lax")
    return resp


@router.post("/auth/refresh")
def refresh(request: Request, response: Response, db: Session = Depends(get_db)) -> Dict:
    """쿠키의 refresh_token으로 access 갱신 + refresh 로테이션"""
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="No refresh token")
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
    jti = payload.get("jti")
    sub = payload.get("sub")
    if not jti or not sub:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    # 토큰 유효성 검사
    row = db.query(RefreshToken).filter(RefreshToken.id == jti).first()
    if not row or row.revoked:
        raise HTTPException(status_code=401, detail="Refresh revoked or not found")
    # 로테이션: 기존 revoke, 새 토큰 발급
    row.revoked = True
    user = db.query(User).filter(User.id == int(sub)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    access = create_access_token(user)
    # 기존 refresh 만료 남은 시간을 쿠키 max_age로 반영
    import datetime as dt
    now = dt.datetime.utcnow()
    remaining_seconds = int((row.expires_at - now).total_seconds()) if row.expires_at else 0
    # 새 refresh는 남은 기간과 동일하게 재발급(간단 정책)
    days = max(1, remaining_seconds // 86400) if remaining_seconds > 0 else 14
    new_refresh, new_jti, new_exp = create_refresh_token(user, expires_days=days)
    db.add(RefreshToken(id=new_jti, user_id=user.id, issued_at=now, expires_at=new_exp, revoked=False))
    db.commit()
    # 쿠키 갱신
    response.set_cookie("access_token", access, httponly=True, samesite="lax")
    if remaining_seconds > 0:
        response.set_cookie("refresh_token", new_refresh, httponly=True, samesite="lax", max_age=remaining_seconds)
    else:
        response.set_cookie("refresh_token", new_refresh, httponly=True, samesite="lax")
    # CSRF 토큰 재발급
    response.set_cookie("csrf_token", generate_csrf_token(), httponly=False, samesite="lax")
    return {"ok": True}
    return resp


@router.post("/auth/login")
def login(body: LoginDto, response: Response, db: Session = Depends(get_db)) -> Dict:
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access = create_access_token(user)
    # Remember me 정책: ON=30일, OFF=14일
    refresh_days = 30 if (body.remember is None or body.remember) else 14
    refresh, jti, exp = create_refresh_token(user, expires_days=refresh_days)
    db.add(RefreshToken(id=jti, user_id=user.id, issued_at=datetime.utcnow(), expires_at=exp, revoked=False))
    db.commit()
    resp = {"id": user.id, "email": user.email, "role": user.role, "display_name": user.display_name}
    response.set_cookie("access_token", access, httponly=True, samesite="lax")
    # refresh는 remember에 따라 만료일 지정
    max_age = refresh_days * 24 * 60 * 60
    response.set_cookie("refresh_token", refresh, httponly=True, samesite="lax", max_age=max_age)
    # CSRF 토큰 발급 (더블 서브밋 쿠키)
    response.set_cookie("csrf_token", generate_csrf_token(), httponly=False, samesite="lax")
    return resp


@router.post("/auth/logout")
def logout(response: Response) -> Dict:
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    response.delete_cookie("csrf_token")
    return {"ok": True}


@router.get("/auth/me")
def me(current_user: User = Depends(get_current_user)) -> Dict:
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "display_name": current_user.display_name,
    }


@router.get("/auth/has-refresh")
def has_refresh(request: Request) -> Dict:
    """리프레시 쿠키 존재 여부만 판단하여 401 네트워크 에러 없이 자동 로그인 시도 여부를 결정하기 위한 경량 엔드포인트"""
    token = request.cookies.get("refresh_token")
    return {"has": bool(token)}


