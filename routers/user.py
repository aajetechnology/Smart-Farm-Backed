# routers/user.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User
from routers.schemas import UserOut
from routers.auth import get_current_user  # reuse dependency

router = APIRouter(tags=["users"])  # NO prefix here

@router.get("/users/me", response_model=UserOut)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user