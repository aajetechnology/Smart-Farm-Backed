
from routers.auth import get_current_user
from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Message
import requests

router = APIRouter(prefix="/notify")

@router.get("/")
async def get_notifications(
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    unread_count = db.query(Message).filter(
        Message.recipient_id == current_user.id,
        Message.is_read == False


    ).count()


    weather_alert = None
    try:
        ip = "8.8.8.8"
        geo_url = f"https://ipapi.co/{ip}/json/"
        geo_res = requests.get(geo_url, timeout=5)
        lat = geo_res.json().get("latitude", 9.0662)
        lon = geo_res.json().get("longitude", 7.4862)

        url = "https://api.open-meteo.com/v1/forecast"
        params ={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,precipitation,relative_humidity_2m,weather_code",
            "forecast_days": 1
        }
        res = requests.get(url, params=params, timeout=10)
        data = res.json()["current"]

        temp = data["temperature_2m"]
        precip = data["precipitation"]
        humid = data["relative_humidity_2m"]

        advice = []
        if temp < 15:
            advice.append("Cold: Use greenhouse")
        elif temp > 32:
            advice.append("Hot: Water more")
        if precip > 10:
            advice.append("Heavy rain: Check drainage")
        if humid > 80:
            advice.append("High humidity: watch for blight")
        
        if advice:
            weather_alert = " | ".join(advice)

    except:
        pass

    return {
        "wather_alert": weather_alert,
        "unread_chats": unread_count,
        "has_alert": bool(weather_alert or unread_count > 0)
    }