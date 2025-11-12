from fastapi import APIRouter

router = APIRouter()

@router.post("/chat")
def chat():
    return {"message": "Chat endpoint (to be implemented)"}