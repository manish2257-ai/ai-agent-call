from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ..database.session import SessionLocal
from ..core.security import decode_token
from ..models.models import User, UserSettings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    # If no token provided in demo/dev mode, return or seed the default owner user
    if not token:
        default_user = db.query(User).filter(User.email == "manish@aicallagent.com").first()
        if not default_user:
            from ..core.security import get_password_hash
            default_user = User(
                email="manish@aicallagent.com",
                hashed_password=get_password_hash("password123"),
                full_name="Manish Kumar",
                phone_number=os.getenv("OWNER_PHONE_NUMBER") or None
            )
            db.add(default_user)
            db.commit()
            db.refresh(default_user)

            # Add default settings
            default_settings = UserSettings(
                user_id=default_user.id,
                ai_phone_number=os.getenv("EXOTEL_VIRTUAL_NUMBER") or None,
                owner_phone_number=os.getenv("OWNER_PHONE_NUMBER") or None
            )
            db.add(default_settings)
            db.commit()

        return default_user

    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication credentials"
        )
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
