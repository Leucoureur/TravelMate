"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List

# Auth Models
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    avatar_url: Optional[str] = None

# Destination Models
class DestinationBase(BaseModel):
    name: str
    country: str
    city_code: Optional[str] = None
    description: Optional[str] = None
    best_months: Optional[str] = None
    avg_daily_cost: Optional[float] = None
    flight_cost_estimate: Optional[float] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

# Trip Models
class TripCreate(BaseModel):
    destination_id: int
    start_date: str
    end_date: str
    num_travelers: int = 1
    is_public: bool = False

class TripResponse(BaseModel):
    id: int
    total_cost: float
    flight_price: float
    hotel_price: float
    message: str = "Trip created successfully"

# Review Models
class ReviewCreate(BaseModel):
    destination_id: int
    rating: int  # 1-5
    title: str
    content: str
    travel_date: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    message: str = "Review created"

# Suggestion Models
class SuggestionRequest(BaseModel):
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    month: Optional[int] = None
    category: Optional[str] = None
    num_travelers: int = 1
    duration_days: int = 7
    origin_city: Optional[str] = None

# Share Models
class ShareResponse(BaseModel):
    share_url: str
    token: str