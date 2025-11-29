"""
Destination routes
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from database import get_db
from models import SuggestionRequest
from auth.utils import get_optional_user

router = APIRouter(prefix="/destinations", tags=["Destinations"])

@router.get("")
def get_destinations(
    category: Optional[str] = None,
    user: Optional[dict] = Depends(get_optional_user)
):
    """Get all destinations with optional category filter"""
    conn = get_db()
    c = conn.cursor()
    
    if category:
        c.execute("SELECT * FROM destinations WHERE category = ?", (category,))
    else:
        c.execute("SELECT * FROM destinations")
    
    destinations = [dict(r) for r in c.fetchall()]
    
    # Add favorite status if user is logged in
    if user:
        c.execute(
            "SELECT destination_id FROM favorites WHERE user_id = ?",
            (user["id"],)
        )
        fav_ids = {r["destination_id"] for r in c.fetchall()}
        for d in destinations:
            d["is_favorite"] = d["id"] in fav_ids
    
    conn.close()
    return destinations

@router.get("/{dest_id}")
def get_destination(dest_id: int):
    """Get single destination by ID"""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM destinations WHERE id = ?", (dest_id,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Destination not found")
    
    return dict(row)

@router.post("/suggestions")
def get_suggestions(req: SuggestionRequest):
    """Get AI-powered destination suggestions based on preferences"""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM destinations")
    destinations = [dict(r) for r in c.fetchall()]
    conn.close()
    
    suggestions = []
    
    for dest in destinations:
        score = 0
        reasons = []
        
        # Calculate total trip cost
        total_cost = (
            dest["avg_daily_cost"] * req.duration_days + 
            dest["flight_cost_estimate"]
        ) * req.num_travelers
        
        # Budget range filter (updated to use min/max)
        if req.budget_min is not None or req.budget_max is not None:
            within_budget = True
            
            if req.budget_min and total_cost < req.budget_min:
                continue  # Too cheap, skip
            
            if req.budget_max:
                if total_cost <= req.budget_max:
                    score += 30
                    reasons.append("Within your budget")
                elif total_cost <= req.budget_max * 1.15:
                    score += 15
                    reasons.append("Slightly over budget")
                else:
                    continue  # Too expensive
        
        # Best month filter
        if req.month and dest["best_months"]:
            best_months = [int(m) for m in dest["best_months"].split(",")]
            if req.month in best_months:
                score += 40
                reasons.append("Ideal time to visit")
            elif (req.month - 1) % 12 + 1 in best_months or (req.month + 1) % 12 in best_months:
                score += 20
                reasons.append("Good time to visit")
        
        # Category preference
        if req.category and dest["category"] == req.category:
            score += 30
            reasons.append(f"Matches your {req.category} preference")
        
        # Rating bonus
        score += dest["rating"] * 5
        
        # Value for money bonus
        if dest["avg_daily_cost"] < 100:
            score += 10
            reasons.append("Great value for money")
        
        suggestions.append({
            **dest,
            "score": score,
            "reasons": reasons,
            "estimated_total_cost": round(total_cost, 2),
            "cost_breakdown": {
                "flights": round(dest["flight_cost_estimate"] * req.num_travelers, 2),
                "accommodation_and_expenses": round(
                    dest["avg_daily_cost"] * req.duration_days * req.num_travelers, 2
                ),
                "per_person": round(total_cost / req.num_travelers, 2)
            }
        })
    
    # Sort by score descending
    suggestions.sort(key=lambda x: x["score"], reverse=True)
    
    return suggestions[:8]  # Return top 8 suggestions

@router.get("/categories/list")
def get_categories():
    """Get all available categories"""
    return [
        {"id": "culture", "name": "Culture & History", "icon": "🏛️"},
        {"id": "beach", "name": "Beach & Relaxation", "icon": "🏖️"},
        {"id": "adventure", "name": "Adventure", "icon": "🏔️"},
        {"id": "city", "name": "City Break", "icon": "🌆"},
        {"id": "luxury", "name": "Luxury", "icon": "✨"},
    ]