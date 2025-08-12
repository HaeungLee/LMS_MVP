from datetime import datetime

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.orm import User


def upsert_admin(email: str, password: str, display_name: str = "admin") -> None:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        pwd_hash, pwd_salt = hash_password(password)
        if user:
            user.password_hash = pwd_hash
            user.password_salt = pwd_salt
            user.role = "admin"
            if not user.display_name:
                user.display_name = display_name
        else:
            user = User(
                email=email,
                password_hash=pwd_hash,
                password_salt=pwd_salt,
                role="admin",
                display_name=display_name,
                created_at=datetime.utcnow(),
            )
            db.add(user)
        db.commit()
        print(f"Upserted admin user: {email} / password set")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main():
    # 이메일 로그인 폼 제약(HTML5 email) 고려해 이메일 형태 사용
    upsert_admin(email="admin@admin.com", password="admin", display_name="admin")


if __name__ == "__main__":
    main()


