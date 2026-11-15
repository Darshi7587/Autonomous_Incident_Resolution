from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.database.models import User
from backend.core.security import hash_password, verify_password, create_access_token, get_current_user, require_role

router = APIRouter(prefix="/auth", tags=["Authentication & RBAC"])

@router.post("/login")
def login(
    username: str = Body(..., embed=True),
    password: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """Authenticate user credentials and issue a signed JWT token."""
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    token = create_access_token({
        "sub": user.id,
        "username": user.username,
        "role": user.role
    })
    return {
        "access_token": token,
        "token_type": "bearer",
        "username": user.username,
        "role": user.role
    }

@router.get("/me")
def get_profile(current_user: dict = Depends(get_current_user)):
    """Retrieve profile and RBAC permissions of the current authenticated user."""
    return current_user

@router.post("/register")
def register_user(
    username: str = Body(..., embed=True),
    password: str = Body(..., embed=True),
    role: str = Body(default="operator", embed=True),
    current_admin: dict = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """Admin-only endpoint to provision new operator or auditor users."""
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")

    new_user = User(
        username=username,
        hashed_password=hash_password(password),
        role=role
    )
    db.add(new_user)
    db.commit()
    return {"status": "SUCCESS", "username": username, "role": role}
