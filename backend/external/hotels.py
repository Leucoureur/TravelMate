"""
Hotel search API with enhanced mock data
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import random
from database import get_db

router = APIRouter(prefix="/hotels", tags=["Hotels"])

# Hotel name templates
HOTEL_TEMPLATES = {
    "luxury": [
        "{city} Grand Hotel",
        "The {city} Palace",
        "{city} Ritz-Carlton",
        "Four Seasons {city}",
        "Mandarin Oriental {city}"
    ],
    "upscale": [
        "{city} Plaza",
        "Marriott {city}",
        "Hilton {city}",
        "{city} Sheraton",
        "Hyatt Regency {city}"
    ],
    "midrange": [
        "{city} Inn & Suites",
        "Holiday Inn {city}",
        "Best Western {city}",
        "Courtyard by Marriott {city}",
        "{city} Central Hotel"
    ],
    "budget": [
        "{city} Hostel",
        "Budget Stay {city}",
        "{city} Backpackers",
        "Cozy Inn {city}",
        "{city} Lodge"
    ]
}

AMENITIES = {
    5: ["Pool", "Spa", "Fine Dining", "Gym", "Concierge", "Room Service", "WiFi", "Airport Transfer"],
    4: ["Pool", "Gym", "Restaurant", "Bar", "WiFi", "Parking", "Room Service"],
    3: ["WiFi", "Breakfast", "Parking", "Restaurant", "Gym"],
    2: ["WiFi", "Breakfast", "Shared Kitchen"],
}

HOTEL_IMAGES = [
    "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=300",
    "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=300",
    "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=300",
    "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=300",
    "https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=300",
    "https://images.unsplash.com/photo-1582719508461-905c673771fd?w=300",
]

def generate_mock_hotels(destination_name, base_price, num_hotels=8):
    """Generate realistic mock hotel data"""
    hotels = []
    
    # 5-star luxury
    for _ in range(2):
        template = random.choice(HOTEL_TEMPLATES["luxury"])
        hotels.append({
            "name": template.format(city=destination_name),
            "stars": 5,
            "price_per_night": round(base_price * random.uniform(2.5, 3.5), 2),
            "rating": round(random.uniform(4.5, 5.0), 1),
            "reviews": random.randint(800, 2000),
            "amenities": random.sample(AMENITIES[5], k=random.randint(5, 8)),
            "image": random.choice(HOTEL_IMAGES),
            "distance_from_center": round(random.uniform(0.5, 3.0), 1),
            "breakfast_included": random.choice([True, False]),
            "free_cancellation": True
        })
    
    # 4-star upscale
    for _ in range(2):
        template = random.choice(HOTEL_TEMPLATES["upscale"])
        hotels.append({
            "name": template.format(city=destination_name),
            "stars": 4,
            "price_per_night": round(base_price * random.uniform(1.5, 2.2), 2),
            "rating": round(random.uniform(4.0, 4.7), 1),
            "reviews": random.randint(400, 1200),
            "amenities": random.sample(AMENITIES[4], k=random.randint(4, 6)),
            "image": random.choice(HOTEL_IMAGES),
            "distance_from_center": round(random.uniform(1.0, 5.0), 1),
            "breakfast_included": random.choice([True, True, False]),
            "free_cancellation": random.choice([True, False])
        })
    
    # 3-star midrange
    for _ in range(3):
        template = random.choice(HOTEL_TEMPLATES["midrange"])
        hotels.append({
            "name": template.format(city=destination_name),
            "stars": 3,
            "price_per_night": round(base_price * random.uniform(0.8, 1.3), 2),
            "rating": round(random.uniform(3.5, 4.3), 1),
            "reviews": random.randint(200, 600),
            "amenities": random.sample(AMENITIES[3], k=random.randint(3, 5)),
            "image": random.choice(HOTEL_IMAGES),
            "distance_from_center": round(random.uniform(2.0, 8.0), 1),
            "breakfast_included": True,
            "free_cancellation": False
        })
    
    # 2-star budget
    for _ in range(1):
        template = random.choice(HOTEL_TEMPLATES["budget"])
        hotels.append({
            "name": template.format(city=destination_name),
            "stars": 2,
            "price_per_night": round(base_price * random.uniform(0.3, 0.6), 2),
            "rating": round(random.uniform(3.5, 4.0), 1),
            "reviews": random.randint(100, 400),
            "amenities": AMENITIES[2],
            "image": random.choice(HOTEL_IMAGES),
            "distance_from_center": round(random.uniform(3.0, 10.0), 1),
            "breakfast_included": True,
            "free_cancellation": False
        })
    
    # Sort by price
    hotels.sort(key=lambda x: x["price_per_night"], reverse=True)
    
    return hotels

@router.get("/search")
def search_hotels(
    destination_id: int,
    checkin: str,
    checkout: str,
    guests: int = 2,
    min_stars: int = 0,
    max_price: float = None
):
    """Search for hotels at a destination"""
    conn = get_db()
    c = conn.cursor()
    
    c.execute(
        "SELECT name, avg_daily_cost FROM destinations WHERE id = ?",
        (destination_id,)
    )
    dest = c.fetchone()
    conn.close()
    
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")
    
    dest = dict(dest)
    
    # Validate dates
    try:
        checkin_date = datetime.strptime(checkin, "%Y-%m-%d")
        checkout_date = datetime.strptime(checkout, "%Y-%m-%d")
        
        if checkin_date < datetime.now():
            raise HTTPException(
                status_code=400,
                detail="Check-in date must be in the future"
            )
        
        if checkout_date <= checkin_date:
            raise HTTPException(
                status_code=400,
                detail="Check-out must be after check-in"
            )
        
        nights = (checkout_date - checkin_date).days
        
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    # Calculate base hotel price (60% of daily cost)
    base_price = dest["avg_daily_cost"] * 0.6
    
    # Generate mock hotels
    hotels = generate_mock_hotels(dest["name"], base_price)
    
    # Apply filters
    if min_stars > 0:
        hotels = [h for h in hotels if h["stars"] >= min_stars]
    
    if max_price:
        hotels = [h for h in hotels if h["price_per_night"] <= max_price]
    
    # Calculate total costs
    for hotel in hotels:
        hotel["total_cost"] = round(hotel["price_per_night"] * nights, 2)
    
    return {
        "destination": dest["name"],
        "checkin": checkin,
        "checkout": checkout,
        "nights": nights,
        "guests": guests,
        "hotels": hotels,
        "source": "mock"
    }

@router.get("/{hotel_id}/details")
def get_hotel_details(hotel_id: str):
    """Get detailed information about a specific hotel (mock)"""
    return {
        "id": hotel_id,
        "description": "Experience luxury and comfort in the heart of the city.",
        "rooms": [
            {"type": "Standard Room", "size": "25 sqm", "beds": "1 King or 2 Twin"},
            {"type": "Deluxe Room", "size": "35 sqm", "beds": "1 King", "view": "City View"},
            {"type": "Suite", "size": "55 sqm", "beds": "1 King + Sofa", "view": "Panoramic"}
        ],
        "policies": {
            "check_in": "15:00",
            "check_out": "11:00",
            "cancellation": "Free cancellation up to 24 hours before check-in"
        },
        "nearby_attractions": [
            "City Center - 2 km",
            "Museum - 1.5 km",
            "Beach - 5 km"
        ]
    }