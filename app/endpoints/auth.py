from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserLogin

from app.core.security import verify_password
from app.core.jwt import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == user_data.email).first()

    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    if not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    access_token = create_access_token({"sub": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }