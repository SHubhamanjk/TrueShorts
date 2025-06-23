from fastapi import APIRouter, HTTPException, status
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from utils.database import db
from model.user import UserCreate, UserLogin
from pydantic import BaseModel
import os
from config import Config
from services.news_service import deduplicate_articles_for_user
import asyncio
from typing import Dict

class SignupResponse(BaseModel):
    msg: str
    class Config:
        json_schema_extra = {"example": {"msg": "Account created"}}

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    class Config:
        json_schema_extra = {"example": {"access_token": "jwt_token_here", "token_type": "bearer"}}

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_user(email: str):
    return await db.db.users.find_one({"email": email})

async def create_user(user: dict):
    result = await db.db.users.insert_one(user)
    return result.inserted_id

async def create_access_token(data: dict):
    expire = datetime.utcnow() + timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({"exp": expire})
    return jwt.encode(data, Config.SECRET_KEY, algorithm="HS256")

@router.post("/signup", response_model=SignupResponse)
async def signup(user: UserCreate):
    existing = await get_user(user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_dict = user.dict()
    user_dict["password"] = pwd_context.hash(user.password)
    user_id = await create_user(user_dict)
    # Start background task for fetching articles for this user
    asyncio.create_task(deduplicate_articles_for_user(str(user_id)))
    return SignupResponse(msg="Account created")

@router.post("/login", response_model=LoginResponse)
async def login(data: UserLogin):
    user = await get_user(data.email)
    if not user or not pwd_context.verify(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = await create_access_token({"sub": str(user["_id"])})
    return LoginResponse(access_token=token, token_type="bearer")
