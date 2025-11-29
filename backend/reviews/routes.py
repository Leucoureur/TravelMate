"""
Review and rating routes
"""
from fastapi import APIRouter, HTTPException, Depends
from database import get_db
from models import ReviewCreate, ReviewResponse
from auth.utils import get_current_user

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.post("", response_model=ReviewResponse)
def create_review(review: ReviewCreate, user: dict = Depends(get_current_user)):
    """Create a new review for a destination"""
    if review.rating < 1 or review.rating > 5:
        raise HTTPException(
            status_code=400,
            detail="Rating must be between 1 and 5"
        )
    
    conn = get_db()
    c = conn.cursor()
    
    # Check if destination exists
    c.execute(
        "SELECT id FROM destinations WHERE id = ?",
        (review.destination_id,)
    )
    if not c.fetchone():
        raise HTTPException(status_code=404, detail="Destination not found")
    
    # Insert review
    c.execute("""
        INSERT INTO reviews 
        (user_id, destination_id, rating, title, content, travel_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user["id"],
        review.destination_id,
        review.rating,
        review.title,
        review.content,
        review.travel_date
    ))
    
    review_id = c.lastrowid
    
    # Update destination average rating
    c.execute(
        "SELECT AVG(rating) as avg_rating FROM reviews WHERE destination_id = ?",
        (review.destination_id,)
    )
    avg_rating = c.fetchone()["avg_rating"]
    
    c.execute(
        "UPDATE destinations SET rating = ? WHERE id = ?",
        (round(avg_rating, 1), review.destination_id)
    )
    
    conn.commit()
    conn.close()
    
    return ReviewResponse(id=review_id)

@router.get("/{destination_id}")
def get_reviews(
    destination_id: int,
    limit: int = 20,
    offset: int = 0
):
    """Get all reviews for a destination"""
    conn = get_db()
    c = conn.cursor()
    
    # Get reviews
    c.execute("""
        SELECT r.*, u.username, u.avatar_url
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        WHERE r.destination_id = ?
        ORDER BY r.created_at DESC
        LIMIT ? OFFSET ?
    """, (destination_id, limit, offset))
    
    reviews = [dict(r) for r in c.fetchall()]
    
    # Get total count
    c.execute(
        "SELECT COUNT(*) as total FROM reviews WHERE destination_id = ?",
        (destination_id,)
    )
    total = c.fetchone()["total"]
    
    # Get rating distribution
    c.execute("""
        SELECT rating, COUNT(*) as count
        FROM reviews
        WHERE destination_id = ?
        GROUP BY rating
    """, (destination_id,))
    
    distribution = {r["rating"]: r["count"] for r in c.fetchall()}
    
    conn.close()
    
    return {
        "reviews": reviews,
        "total": total,
        "distribution": distribution
    }

@router.post("/{review_id}/helpful")
def mark_helpful(review_id: int, user: dict = Depends(get_current_user)):
    """Mark a review as helpful"""
    conn = get_db()
    c = conn.cursor()
    
    c.execute(
        "UPDATE reviews SET helpful_count = helpful_count + 1 WHERE id = ?",
        (review_id,)
    )
    
    if c.rowcount == 0:
        raise HTTPException(status_code=404, detail="Review not found")
    
    conn.commit()
    conn.close()
    
    return {"message": "Review marked as helpful"}

@router.delete("/{review_id}")
def delete_review(review_id: int, user: dict = Depends(get_current_user)):
    """Delete own review"""
    conn = get_db()
    c = conn.cursor()
    
    # Get review to check ownership and get destination_id
    c.execute(
        "SELECT destination_id FROM reviews WHERE id = ? AND user_id = ?",
        (review_id, user["id"])
    )
    review = c.fetchone()
    
    if not review:
        raise HTTPException(
            status_code=404,
            detail="Review not found or not authorized"
        )
    
    destination_id = review["destination_id"]
    
    # Delete review
    c.execute("DELETE FROM reviews WHERE id = ?", (review_id,))
    
    # Recalculate destination rating
    c.execute(
        "SELECT AVG(rating) as avg_rating FROM reviews WHERE destination_id = ?",
        (destination_id,)
    )
    result = c.fetchone()
    avg_rating = result["avg_rating"] if result["avg_rating"] else 4.0
    
    c.execute(
        "UPDATE destinations SET rating = ? WHERE id = ?",
        (round(avg_rating, 1), destination_id)
    )
    
    conn.commit()
    conn.close()
    
    return {"message": "Review deleted successfully"}