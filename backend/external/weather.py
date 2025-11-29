"""
Weather API integration with enhanced mock data
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import httpx
import random
from database import get_db
from config import settings

router = APIRouter(prefix="/weather", tags=["Weather"])

# Enhanced mock weather conditions
WEATHER_CONDITIONS = {
    "tropical": ["Sunny", "Partly Cloudy", "Scattered Showers", "Thunderstorms"],
    "temperate": ["Sunny", "Partly Cloudy", "Cloudy", "Light Rain"],
    "cold": ["Cloudy", "Snow", "Light Snow", "Clear and Cold"],
    "desert": ["Sunny", "Hot and Sunny", "Clear Skies", "Dusty"],
}

def get_climate_zone(latitude):
    """Determine climate zone from latitude"""
    abs_lat = abs(latitude)
    if abs_lat < 23.5:
        return "tropical"
    elif abs_lat < 35:
        return "desert" if random.random() > 0.5 else "temperate"
    elif abs_lat < 60:
        return "temperate"
    else:
        return "cold"

def generate_mock_weather(dest_name, latitude, longitude, days=7):
    """Generate realistic mock weather data"""
    climate = get_climate_zone(latitude)
    conditions = WEATHER_CONDITIONS[climate]
    
    # Base temperature by climate
    temp_ranges = {
        "tropical": (25, 32),
        "temperate": (15, 25),
        "cold": (-5, 10),
        "desert": (30, 40),
    }
    
    base_high, base_low = temp_ranges[climate]
    
    forecast = []
    for i in range(days):
        date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
        
        # Add some variation
        temp_high = base_high + random.randint(-3, 5)
        temp_low = base_low + random.randint(-3, 3)
        
        condition = random.choice(conditions)
        humidity = random.randint(40, 85) if climate == "tropical" else random.randint(30, 70)
        
        # Weather icons
        icon_map = {
            "Sunny": "☀️", "Hot and Sunny": "🌞", "Clear Skies": "☀️",
            "Partly Cloudy": "⛅", "Cloudy": "☁️", "Clear and Cold": "🌤️",
            "Light Rain": "🌦️", "Scattered Showers": "🌧️",
            "Thunderstorms": "⛈️", "Snow": "❄️", "Light Snow": "🌨️",
            "Dusty": "🌫️"
        }
        
        forecast.append({
            "date": date,
            "temp_high": temp_high,
            "temp_low": temp_low,
            "condition": condition,
            "humidity": humidity,
            "icon": icon_map.get(condition, "🌡️"),
            "wind_speed": random.randint(5, 25)
        })
    
    return {
        "destination": dest_name,
        "forecast": forecast,
        "source": "mock",
        "climate_zone": climate
    }

@router.get("/{destination_id}")
async def get_weather(destination_id: int, days: int = 7):
    """Get weather forecast for a destination"""
    conn = get_db()
    c = conn.cursor()
    
    c.execute(
        "SELECT latitude, longitude, name FROM destinations WHERE id = ?",
        (destination_id,)
    )
    dest = c.fetchone()
    conn.close()
    
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")
    
    dest = dict(dest)
    
    # Try real API if key available
    if settings.WEATHER_API_KEY:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://api.openweathermap.org/data/2.5/forecast",
                    params={
                        "lat": dest["latitude"],
                        "lon": dest["longitude"],
                        "appid": settings.WEATHER_API_KEY,
                        "units": "metric",
                        "cnt": days * 8
                    },
                    timeout=10.0
                )
                
                if resp.status_code == 200:
                    data = resp.json()
                    
                    # Process API data
                    daily = {}
                    for item in data["list"]:
                        date = item["dt_txt"].split()[0]
                        if date not in daily:
                            daily[date] = {
                                "temps": [],
                                "conditions": [],
                                "humidity": []
                            }
                        daily[date]["temps"].append(item["main"]["temp"])
                        daily[date]["conditions"].append(item["weather"][0]["main"])
                        daily[date]["humidity"].append(item["main"]["humidity"])
                    
                    forecast = []
                    for date, vals in list(daily.items())[:days]:
                        condition = max(set(vals["conditions"]), key=vals["conditions"].count)
                        forecast.append({
                            "date": date,
                            "temp_high": round(max(vals["temps"])),
                            "temp_low": round(min(vals["temps"])),
                            "condition": condition,
                            "humidity": round(sum(vals["humidity"]) / len(vals["humidity"]))
                        })
                    
                    return {
                        "destination": dest["name"],
                        "forecast": forecast,
                        "source": "openweathermap"
                    }
        except Exception as e:
            print(f"Weather API error: {e}")
            # Fall through to mock data
    
    # Return enhanced mock data
    return generate_mock_weather(
        dest["name"],
        dest["latitude"],
        dest["longitude"],
        days
    )