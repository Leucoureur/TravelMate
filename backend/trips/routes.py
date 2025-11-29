"""
Trip management routes
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from database import get_db
from models import TripCreate, TripResponse
from auth.utils import get_current_user

router = APIRouter(prefix="/trips", tags=["Trips"])

@router.post("", response_model=TripResponse)
def create_trip(trip: TripCreate, user: dict = Depends(get_current_user)):
    """Create a new trip"""
    conn = get_db()
    c = conn.cursor()
    
    # Get destination info
    c.execute("SELECT * FROM destinations WHERE id = ?", (trip.destination_id,))
    dest = c.fetchone()
    
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")
    
    dest = dict(dest)
    
    # Calculate trip duration
    start = datetime.strptime(trip.start_date, "%Y-%m-%d")
    end = datetime.strptime(trip.end_date, "%Y-%m-%d")
    duration = (end - start).days
    
    if duration <= 0:
        raise HTTPException(
            status_code=400,
            detail="End date must be after start date"
        )
    
    # Calculate costs
    flight_price = dest["flight_cost_estimate"] * trip.num_travelers
    hotel_price = dest["avg_daily_cost"] * 0.6 * duration * trip.num_travelers
    other_expenses = dest["avg_daily_cost"] * 0.4 * duration * trip.num_travelers
    total_cost = flight_price + hotel_price + other_expenses
    
    # Insert trip
    c.execute("""
        INSERT INTO trips 
        (user_id, destination_id, start_date, end_date, num_travelers, 
         total_cost, flight_price, hotel_price, is_public)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user["id"],
        trip.destination_id,
        trip.start_date,
        trip.end_date,
        trip.num_travelers,
        total_cost,
        flight_price,
        hotel_price,
        trip.is_public
    ))
    
    trip_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return TripResponse(
        id=trip_id,
        total_cost=round(total_cost, 2),
        flight_price=round(flight_price, 2),
        hotel_price=round(hotel_price, 2)
    )

@router.get("")
def get_trips(user: dict = Depends(get_current_user)):
    """Get all trips for current user"""
    conn = get_db()
    c = conn.cursor()
    
    c.execute("""
        SELECT t.*, d.name as destination_name, d.country, d.image_url
        FROM trips t
        JOIN destinations d ON t.destination_id = d.id
        WHERE t.user_id = ?
        ORDER BY t.created_at DESC
    """, (user["id"],))
    
    trips = [dict(r) for r in c.fetchall()]
    conn.close()
    
    return trips

@router.get("/{trip_id}")
def get_trip(trip_id: int, user: dict = Depends(get_current_user)):
    """Get single trip by ID"""
    conn = get_db()
    c = conn.cursor()
    
    c.execute("""
        SELECT t.*, d.name as destination_name, d.country, d.image_url
        FROM trips t
        JOIN destinations d ON t.destination_id = d.id
        WHERE t.id = ? AND t.user_id = ?
    """, (trip_id, user["id"]))
    
    trip = c.fetchone()
    conn.close()
    
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    return dict(trip)

@router.delete("/{trip_id}")
def delete_trip(trip_id: int, user: dict = Depends(get_current_user)):
    """Cancel/delete a trip"""
    conn = get_db()
    c = conn.cursor()
    
    c.execute(
        "DELETE FROM trips WHERE id = ? AND user_id = ?",
        (trip_id, user["id"])
    )
    
    if c.rowcount == 0:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    conn.commit()
    conn.close()
    
    return {"message": "Trip deleted successfully"}

@router.put("/{trip_id}/status")
def update_trip_status(
    trip_id: int,
    status: str,
    user: dict = Depends(get_current_user)
):
    """Update trip status (planned, ongoing, completed, cancelled)"""
    valid_statuses = ["planned", "ongoing", "completed", "cancelled"]
    
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    conn = get_db()
    c = conn.cursor()
    
    c.execute(
        "UPDATE trips SET status = ? WHERE id = ? AND user_id = ?",
        (status, trip_id, user["id"])
    )
    
    if c.rowcount == 0:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    conn.commit()
    conn.close()
    
    return {"message": f"Trip status updated to {status}"}