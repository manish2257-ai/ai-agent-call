from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..schemas.schemas import UserRegister, UserLogin, UserResponse, Token
from ..models.models import User, UserSettings
from ..core.security import verify_password, get_password_hash, create_access_token
from .deps import get_db, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        phone_number=user_in.phone_number
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    import os
    # Initialize default settings
    settings = UserSettings(
        user_id=user.id,
        owner_phone_number=user_in.phone_number or os.getenv("OWNER_PHONE_NUMBER") or None,
        ai_phone_number=os.getenv("EXOTEL_VIRTUAL_NUMBER") or None
    )
    db.add(settings)
    db.commit()

    return user

@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
    token = create_access_token(subject=user.id)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
