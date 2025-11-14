from fastapi import APIRouter
from routers.auth import get_current_user
from fastapi import Depends, APIRouter, HTTPException, status

router = APIRouter()

@router.post("/notify")
def notify(current_user: dict = Depends(get_current_user)):
    return {"message": "Notify endpoint (to be implemented)"}