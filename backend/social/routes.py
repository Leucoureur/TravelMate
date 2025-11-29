"""
Social features - sharing and favorites
"""
from fastapi import APIRouter, HTTPException, Depends
import secrets
import sqlite3
from database import get_db
from models import ShareResponse
from auth.utils import get_current_user

router = APIRouter(tags=["Social"])

# ==================== SHARING ====================
@router.post("/trips/{trip_id}/share", response_model=ShareResponse)
def create_share_link(trip_id: int, user: dict = Depends(get_current_user)):
    """Create a shareable link for a trip"""
    share_token = secrets.token_urlsafe(16)
    
    conn = get_db()
    c = conn.cursor()
    
    c.execute(
        """UPDATE trips SET share_token = ?, is_public = 1 
           WHERE id = ? AND user_id = ?""",
        (share_token, trip_id, user["id"])
    )
    
    if c.rowcount == 0:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    conn.commit()
    conn.close()
    
    return ShareResponse(
        share_url=f"/shared/{share_token}",
        token=share_token
    )

@router.get("/shared/{share_token}")
def get_shared_trip(share_token: str):
    """View a shared trip (public access)"""
    conn = get_db()
    c = conn.cursor()
    
    c.execute("""
        SELECT 
            t.*,
            d.name as destination_name,
            d.country,
            d.image_url,
            d.description as destination_description,
            u.username
        FROM trips t
        JOIN destinations d ON t.destination_id = d.id
        JOIN users u ON t.user_id = u.id
        WHERE t.share_token = ? AND t.is_public = 1
    """, (share_token,))
    
    trip = c.fetchone()
    conn.close()
    
    if not trip:
        raise HTTPException(
            status_code=404,
            detail="Trip not found or not shared"
        )
    
    return dict(trip)

@router.delete("/trips/{trip_id}/share")
def remove_share_link(trip_id: int, user: dict = Depends(get_current_user)):
    """Remove sharing from a trip (make it private)"""
    conn = get_db()
    c = conn.cursor()
    
    c.execute(
        """UPDATE trips SET share_token = NULL, is_public = 0
           WHERE id = ? AND user_id = ?""",
        (trip_id, user["id"])
    )
    
    if c.rowcount == 0:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    conn.commit()
    conn.close()
    
    return {"message": "Trip is now private"}

# ==================== FAVORITES ====================
@router.post("/favorites/{destination_id}")
def add_favorite(destination_id: int, user: dict = Depends(get_current_user)):
    """Add destination to favorites"""
    conn = get_db()
    c = conn.cursor()
    
    # Check if destination exists
    c.execute(
        "SELECT id FROM destinations WHERE id = ?",
        (destination_id,)
    )
    if not c.fetchone():
        raise HTTPException(status_code=404, detail="Destination not found")
    
    try:
        c.execute(
            "INSERT INTO favorites (user_id, destination_id) VALUES (?, ?)",
            (user["id"], destination_id)
        )
        conn.commit()
        message = "Added to favorites"
    except sqlite3.IntegrityError:
        message = "Already in favorites"
    
    conn.close()
    
    return {"message": message}

@router.delete("/favorites/{destination_id}")
def remove_favorite(destination_id: int, user: dict = Depends(get_current_user)):
    """Remove destination from favorites"""
    conn = get_db()
    c = conn.cursor()
    
    c.execute(
        "DELETE FROM favorites WHERE user_id = ? AND destination_id = ?",
        (user["id"], destination_id)
    )
    
    if c.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="Favorite not found"
        )
    
    conn.commit()
    conn.close()
    
    return {"message": "Removed from favorites"}

@router.get("/favorites")
def get_favorites(user: dict = Depends(get_current_user)):
    """Get all user's favorite destinations"""
    conn = get_db()
    c = conn.cursor()
    
    c.execute("""
        SELECT d.*, f.created_at as favorited_at
        FROM destinations d
        JOIN favorites f ON d.id = f.destination_id
        WHERE f.user_id = ?
        ORDER BY f.created_at DESC
    """, (user["id"],))
    
    favorites = [dict(r) for r in c.fetchall()]
    conn.close()
    
    return favorites

@router.get("/favorites/check/{destination_id}")
def check_favorite(
    destination_id: int,
    user: dict = Depends(get_current_user)
):
    """Check if a destination is favorited"""
    conn = get_db()
    c = conn.cursor()
    
    c.execute(
        """SELECT COUNT(*) as is_favorite FROM favorites
           WHERE user_id = ? AND destination_id = ?""",
        (user["id"], destination_id)
    )
    
    result = c.fetchone()
    conn.close()
    
    return {"is_favorite": result["is_favorite"] > 0}