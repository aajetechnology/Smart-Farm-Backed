from fastapi import APIRouter

router = APIRouter()

@router.get("/weather")
def get_weather():
    return {"message": "Weather endpoint (to be implemented)"}