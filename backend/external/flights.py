"""
Flight search API with enhanced mock data
"""
from fastapi import APIRouter, HTTPException
import httpx
import random
from datetime import datetime, timedelta
from database import get_db
from config import settings

router = APIRouter(prefix="/flights", tags=["Flights"])

# Airlines database
AIRLINES = [
    {"code": "AF", "name": "Air France"},
    {"code": "BA", "name": "British Airways"},
    {"code": "LH", "name": "Lufthansa"},
    {"code": "EK", "name": "Emirates"},
    {"code": "QR", "name": "Qatar Airways"},
    {"code": "SQ", "name": "Singapore Airlines"},
    {"code": "AA", "name": "American Airlines"},
    {"code": "DL", "name": "Delta"},
    {"code": "UA", "name": "United"},
    {"code": "KL", "name": "KLM"},
    {"code": "TK", "name": "Turkish Airlines"},
    {"code": "AY", "name": "Finnair"},
]

def generate_mock_flights(origin, destination, date, base_price, num_flights=6):
    """Generate realistic mock flight data"""
    flights = []
    
    for i in range(num_flights):
        airline = random.choice(AIRLINES)
        
        # Generate departure and arrival times
        dep_hour = random.randint(6, 22)
        dep_min = random.choice([0, 15, 30, 45])
        departure = f"{dep_hour:02d}:{dep_min:02d}"
        
        # Flight duration (5-15 hours based on distance)
        duration_hours = random.randint(5, 15)
        duration_mins = random.choice([0, 15, 30, 45])
        duration = f"{duration_hours}h {duration_mins}m"
        
        # Calculate arrival time
        arr_hour = (dep_hour + duration_hours) % 24
        arr_min = (dep_min + duration_mins) % 60
        arrival = f"{arr_hour:02d}:{arr_min:02d}"
        
        # Price variation
        price_factor = 1.0 + (i * 0.15) + random.uniform(-0.1, 0.1)
        price = round(base_price * price_factor, 2)
        
        # Stops
        stops = 0 if i < 2 else (1 if i < 4 else 2)
        
        # Cabin class
        cabin = random.choice(["Economy", "Economy", "Economy", "Premium Economy", "Business"])
        
        flights.append({
            "airline_code": airline["code"],
            "airline": airline["name"],
            "price": price,
            "currency": "USD",
            "departure": departure,
            "arrival": arrival,
            "duration": duration,
            "stops": stops,
            "cabin": cabin,
            "seats_available": random.randint(1, 12),
            "baggage_included": random.choice([True, True, False])
        })
    
    # Sort by price
    flights.sort(key=lambda x: x["price"])
    
    return flights

@router.get("/search")
async def search_flights(
    origin: str,
    destination_id: int,
    date: str,
    adults: int = 1,
    cabin: str = "economy"
):
    """Search for flights"""
    conn = get_db()
    c = conn.cursor()
    
    c.execute(
        "SELECT city_code, name, flight_cost_estimate FROM destinations WHERE id = ?",
        (destination_id,)
    )
    dest = c.fetchone()
    conn.close()
    
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")
    
    dest = dict(dest)
    
    # Validate date
    try:
        flight_date = datetime.strptime(date, "%Y-%m-%d")
        if flight_date < datetime.now():
            raise HTTPException(
                status_code=400,
                detail="Flight date must be in the future"
            )
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    # Try Amadeus API if credentials available
    if settings.AMADEUS_API_KEY and settings.AMADEUS_API_SECRET:
        try:
            async with httpx.AsyncClient() as client:
                # Get access token
                auth_resp = await client.post(
                    "https://api.amadeus.com/v1/security/oauth2/token",
                    data={
                        "grant_type": "client_credentials",
                        "client_id": settings.AMADEUS_API_KEY,
                        "client_secret": settings.AMADEUS_API_SECRET
                    },
                    timeout=10.0
                )
                
                if auth_resp.status_code == 200:
                    token = auth_resp.json().get("access_token")
                    
                    # Search flights
                    search_resp = await client.get(
                        "https://api.amadeus.com/v2/shopping/flight-offers",
                        headers={"Authorization": f"Bearer {token}"},
                        params={
                            "originLocationCode": origin.upper(),
                            "destinationLocationCode": dest["city_code"],
                            "departureDate": date,
                            "adults": adults,
                            "max": 10,
                            "travelClass": cabin.upper()
                        },
                        timeout=10.0
                    )
                    
                    if search_resp.status_code == 200:
                        data = search_resp.json()
                        flights = []
                        
                        for offer in data.get("data", []):
                            seg = offer["itineraries"][0]["segments"][0]
                            flights.append({
                                "airline_code": seg["carrierCode"],
                                "airline": seg.get("carrierName", seg["carrierCode"]),
                                "price": float(offer["price"]["total"]),
                                "currency": offer["price"]["currency"],
                                "departure": seg["departure"]["at"],
                                "arrival": seg["arrival"]["at"],
                                "duration": offer["itineraries"][0]["duration"],
                                "stops": len(offer["itineraries"][0]["segments"]) - 1
                            })
                        
                        if flights:
                            return {
                                "origin": origin.upper(),
                                "destination": dest["name"],
                                "date": date,
                                "flights": flights,
                                "source": "amadeus"
                            }
        except Exception as e:
            print(f"Amadeus API error: {e}")
            # Fall through to mock data
    
    # Generate enhanced mock flight data
    flights = generate_mock_flights(
        origin.upper(),
        dest["name"],
        date,
        dest["flight_cost_estimate"] * adults
    )
    
    return {
        "origin": origin.upper(),
        "destination": dest["name"],
        "destination_code": dest["city_code"],
        "date": date,
        "flights": flights,
        "adults": adults,
        "source": "mock"
    }

@router.get("/airlines")
def get_airlines():
    """Get list of available airlines"""
    return AIRLINES