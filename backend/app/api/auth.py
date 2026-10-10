from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, get_current_user
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, UserResponse, Token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists."
        )

    # Create new user
    new_user = User(
        name=user_in.name,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        role="Enterprise Member",
        plan="Enterprise Pro"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create JWT token
    access_token = create_access_token(data={"sub": new_user.id})

    user_resp = UserResponse(
        id=new_user.id,
        name=new_user.name,
        email=new_user.email,
        role=new_user.role,
        plan=new_user.plan,
        createdAt=new_user.created_at.strftime("%Y-%m-%d"),
        storageUsed=0.05,
        storageLimit=10.0
    )

    return Token(access_token=access_token, token_type="bearer", user=user_resp)

@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user.last_login = datetime.now(timezone.utc)
    # Seamless migration: upgrade legacy bcrypt hashes to modern Argon2id
    if user.password_hash.startswith("$2"):
        user.password_hash = get_password_hash(user_in.password)
    db.commit()

    access_token = create_access_token(data={"sub": user.id})

    user_resp = UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        plan=user.plan,
        createdAt=user.created_at.strftime("%Y-%m-%d") if user.created_at else None,
        storageUsed=1.42,
        storageLimit=10.0
    )

    return Token(access_token=access_token, token_type="bearer", user=user_resp)

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        plan=current_user.plan,
        createdAt=current_user.created_at.strftime("%Y-%m-%d") if current_user.created_at else None,
        storageUsed=1.42,
        storageLimit=10.0
    )
