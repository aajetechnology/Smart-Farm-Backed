from fastapi import APIRouter, HTTPException, Request
import requests
from datetime import datetime

router = APIRouter()

def get_tomato_advice(temperature, precipitation, humidity):
    """Generate tomato farming advice based on weather conditions."""
    advice = []
    if temperature < 15:
        advice.append("⚠️ Temperature too low for tomatoes. Consider greenhouse protection.")
    elif temperature > 32:
        advice.append("⚠️ High temperatures may stress tomatoes. Ensure adequate watering.")
    else:
        advice.append("✅ Temperature suitable for tomato growth.")
    
    if precipitation > 10:
        advice.append("🌧️ Heavy rain expected. Ensure proper drainage to avoid root rot.")
    elif precipitation == 0:
        advice.append("☀️ No rain expected. Regular irrigation needed for tomatoes.")
    
    if humidity > 80:
        advice.append("💧 High humidity. Monitor for fungal diseases like blight.")
    elif humidity < 50:
        advice.append("💨 Low humidity. Increase watering to support tomato plants.")
    
    return " ".join(advice) or "✅ Conditions are generally good for tomato farming."

@router.get("/weather")
async def get_weather(
    request: Request,
    lat: float = None,
    lon: float = None
):
    """
    Fetch weather forecast from Open-Meteo. Temporarily no auth for testing.
    """
    # Auto-detect location if not provided
    if lat is None or lon is None:
        try:
            ip = request.client.host
            geo_response = requests.get(f"https://ipapi.co/{ip}/json/", timeout=5)
            geo_response.raise_for_status()
            geo_data = geo_response.json()
            lat = geo_data.get("latitude")
            lon = geo_data.get("longitude")
            if lat is None or lon is None:
                raise ValueError("Could not get location from IP")
        except (requests.RequestException, ValueError):
            # Fallback to Abuja, Nigeria
            lat, lon = 9.0662, 7.4862

    # Validate coordinates
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise HTTPException(status_code=400, detail="Invalid lat/lon coordinates")

    try:
        # Open-Meteo API request
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,precipitation,relative_humidity_2m,weather_code",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "auto",
            "forecast_days": 7
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Map weather code to condition/icon
        weather_code = data["current"]["weather_code"]
        condition_map = {
            0: ("Sunny", "sunny"),
            1: ("Mostly Sunny", "partly-sunny"),
            2: ("Partly Cloudy", "partly-sunny"),
            3: ("Cloudy", "cloudy"),
            61: ("Rainy", "rainy"),
            63: ("Rainy", "rainy"),
            80: ("Light Showers", "rainy"),
        }
        condition, icon = condition_map.get(weather_code, ("Sunny", "sunny"))

        # Format response
        forecast = {
            "user": "test_user",  # Placeholder
            "location": {"lat": lat, "lon": lon},
            "current": {
                "temperature": f"{data['current']['temperature_2m']:.1f}°C",
                "precipitation": data["current"]["precipitation"],
                "humidity": f"{data['current']['relative_humidity_2m']}%",
                "condition": condition,
                "icon": icon,
                "time": data["current"]["time"]
            },
            "daily": [
                {
                    "date": d,
                    "max_temp": f"{max_temp:.1f}°C",
                    "min_temp": f"{min_temp:.1f}°C",
                    "precip_sum": precip_sum
                }
                for d, max_temp, min_temp, precip_sum in zip(
                    data["daily"]["time"],
                    data["daily"]["temperature_2m_max"],
                    data["daily"]["temperature_2m_min"],
                    data["daily"]["precipitation_sum"]
                )
            ],
            "tomato_advice": get_tomato_advice(
                data["current"]["temperature_2m"],
                data["current"]["precipitation"],
                data["current"]["relative_humidity_2m"]
            )
        }
        return forecast
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Weather API error: {str(e)}")