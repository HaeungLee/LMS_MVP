from datetime import datetime
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, Response, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.orm import User, RefreshToken
from app.core.security import (
    hash_password, 
    verify_password, 
    create_access_token, 
    create_refresh_token,
    get_current_user,
    generate_csrf_token
)

router = APIRouter()

class RegisterDto(BaseModel):
    email: EmailStr
    password: str
    display_name: str = None

class LoginDto(BaseModel):
    email: EmailStr
    password: str
    remember: bool = None

# 회원가입
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
    access = create_access_token(user)
    refresh, jti, exp = create_refresh_token(user, expires_days=30)
    db.add(RefreshToken(id=jti, user_id=user.id, issued_at=datetime.utcnow(), expires_at=exp, revoked=False))
    db.commit()
    resp = {"id": user.id, "email": user.email, "role": user.role, "display_name": user.display_name}
    response.set_cookie("access_token", access, httponly=True, samesite="lax")
    response.set_cookie("refresh_token", refresh, httponly=True, samesite="lax", max_age=30*24*60*60)
    response.set_cookie("csrf_token", generate_csrf_token(), httponly=False, samesite="lax")
    return resp

# 중간 부분을 위한 함수들 (토큰 갱신 등)
@router.post("/auth/refresh")
def refresh(request: Request, response: Response, db: Session = Depends(get_db)) -> Dict:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    
    try:
        from app.core.security import decode_refresh_token
        payload = decode_refresh_token(refresh_token)
        user_id = payload.get("sub")
        jti = payload.get("jti")
        
        if not user_id or not jti:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        # DB에서 토큰 확인
        stored_token = db.query(RefreshToken).filter(
            RefreshToken.id == jti,
            RefreshToken.user_id == user_id,
            RefreshToken.revoked == False
        ).first()
        
        if not stored_token:
            raise HTTPException(status_code=401, detail="Refresh token revoked or not found")
        
        # 새 액세스 토큰 발급
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        new_access = create_access_token(user)
        response.set_cookie("access_token", new_access, httponly=True, samesite="lax")
        
        return {"message": "Token refreshed successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

# 로그인
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

# 로그아웃
@router.post("/auth/logout")
def logout(response: Response) -> Dict:
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    response.delete_cookie("csrf_token")
    return {"message": "Logged out successfully"}

# 현재 사용자 정보
@router.get("/auth/me")
def me(current_user: User = Depends(get_current_user)) -> Dict:
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "display_name": current_user.display_name
    }

# 리프레시 토큰 존재 여부 확인
@router.get("/auth/has-refresh")
def has_refresh(request: Request) -> Dict:
    refresh_token = request.cookies.get("refresh_token")
    return {"has_refresh": refresh_token is not None}