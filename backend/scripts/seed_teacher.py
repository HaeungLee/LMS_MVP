from datetime import datetime

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.orm import User


def upsert_teacher(email: str, password: str, display_name: str = "test") -> None:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        pwd_hash, pwd_salt = hash_password(password)
        if user:
            user.password_hash = pwd_hash
            user.password_salt = pwd_salt
            user.role = "teacher"
            if not user.display_name:
                user.display_name = display_name
        else:
            user = User(
                email=email,
                password_hash=pwd_hash,
                password_salt=pwd_salt,
                role="teacher",
                display_name=display_name,
                created_at=datetime.utcnow(),
            )
            db.add(user)
        db.commit()
        print(f"Upserted teacher user: {email} / password set")
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


def main():
    upsert_teacher(email="test@test.com", password="test", display_name="test")


if __name__ == "__main__":
    main()


