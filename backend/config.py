"""
Configuration settings for TravelMate API
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Keys
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
    AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY", "")
    AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET", "")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "travel.db")
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    SESSION_EXPIRY_DAYS = 7
    
    # CORS
    CORS_ORIGINS = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    
    # API Settings
    API_TITLE = "TravelMate API"
    API_VERSION = "2.0.0"
    API_DESCRIPTION = "Travel planning API with AI suggestions"

settings = Settings()