from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.auth import UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/profile", response_model=UserResponse)
def get_user_profile(current_user: User = Depends(get_current_user)):
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

@router.put("/profile", response_model=UserResponse)
def update_user_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if user_update.name is not None:
        current_user.name = user_update.name
    if user_update.role is not None:
        current_user.role = user_update.role
    if user_update.plan is not None:
        current_user.plan = user_update.plan
    db.commit()
    db.refresh(current_user)
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
