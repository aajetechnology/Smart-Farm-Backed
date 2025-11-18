# routers/users.py
from fastapi import APIRouter, Depends
from routers.auth import get_current_user
from models import User

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
    }