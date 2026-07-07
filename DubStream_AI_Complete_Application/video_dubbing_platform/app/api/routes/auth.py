from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.db.session import get_db
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

router = APIRouter(prefix="/api/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    try:
        hashed_password = pwd_context.hash(request.password)
        return {
            "message": "Registration endpoint ready",
            "status": "ok"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    return {
        "message": "Login endpoint ready",
        "access_token": "token_placeholder",
        "token_type": "bearer"
    }
