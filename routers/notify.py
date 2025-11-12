from fastapi import APIRouter

router = APIRouter()

@router.post("/notify")
def notify():
    return {"message": "Notify endpoint (to be implemented)"}