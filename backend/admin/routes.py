"""
Admin dashboard routes
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import datetime, timedelta
from database import get_db
from auth.utils import get_current_user
from models import DestinationBase

router = APIRouter(prefix="/admin", tags=["Admin"])


# Admin middleware
def require_admin(user: dict = Depends(get_current_user)):
    """Check if user is admin"""
    # For now, check if user ID is 1 or email contains 'admin'
    if user["id"] != 1 and "admin" not in user["email"].lower():
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


# Dashboard stats
@router.get("/dashboard/stats")
def get_dashboard_stats(admin: dict = Depends(require_admin)):
    """Get dashboard statistics"""
    conn = get_db()
    c = conn.cursor()

    # Total counts
    c.execute("SELECT COUNT(*) as total FROM users")
    total_users = c.fetchone()["total"]

    c.execute("SELECT COUNT(*) as total FROM destinations")
    total_destinations = c.fetchone()["total"]

    c.execute("SELECT COUNT(*) as total FROM trips")
    total_trips = c.fetchone()["total"]

    c.execute("SELECT COUNT(*) as total FROM reviews")
    total_reviews = c.fetchone()["total"]

    # Recent stats (last 30 days)
    thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()

    c.execute("SELECT COUNT(*) as count FROM users WHERE created_at > ?", (thirty_days_ago,))
    new_users = c.fetchone()["count"]

    c.execute("SELECT COUNT(*) as count FROM trips WHERE created_at > ?", (thirty_days_ago,))
    new_trips = c.fetchone()["count"]

    c.execute("SELECT COUNT(*) as count FROM reviews WHERE created_at > ?", (thirty_days_ago,))
    new_reviews = c.fetchone()["count"]

    # Revenue calculation (mock - sum of trip costs)
    c.execute("SELECT SUM(total_cost) as revenue FROM trips")
    total_revenue = c.fetchone()["revenue"] or 0

    c.execute("SELECT SUM(total_cost) as revenue FROM trips WHERE created_at > ?", (thirty_days_ago,))
    monthly_revenue = c.fetchone()["revenue"] or 0

    # Top destinations
    c.execute("""
              SELECT d.name, d.country, COUNT(t.id) as bookings
              FROM destinations d
                       LEFT JOIN trips t ON d.id = t.destination_id
              GROUP BY d.id
              ORDER BY bookings DESC LIMIT 5
              """)
    top_destinations = [dict(r) for r in c.fetchall()]

    # Recent activities
    c.execute("""
              SELECT 'trip' as type, u.username, d.name as destination, t.created_at
              FROM trips t
                       JOIN users u ON t.user_id = u.id
                       JOIN destinations d ON t.destination_id = d.id
              ORDER BY t.created_at DESC LIMIT 10
              """)
    recent_activities = [dict(r) for r in c.fetchall()]

    conn.close()

    return {
        "totals": {
            "users": total_users,
            "destinations": total_destinations,
            "trips": total_trips,
            "reviews": total_reviews,
            "revenue": round(total_revenue, 2)
        },
        "monthly": {
            "new_users": new_users,
            "new_trips": new_trips,
            "new_reviews": new_reviews,
            "revenue": round(monthly_revenue, 2)
        },
        "top_destinations": top_destinations,
        "recent_activities": recent_activities
    }


# User management
@router.get("/users")
def get_all_users(
        admin: dict = Depends(require_admin),
        limit: int = 50,
        offset: int = 0,
        search: Optional[str] = None
):
    """Get all users with pagination"""
    conn = get_db()
    c = conn.cursor()

    if search:
        c.execute("""
                  SELECT u.*,
                         COUNT(DISTINCT t.id) as trip_count,
                         COUNT(DISTINCT r.id) as review_count
                  FROM users u
                           LEFT JOIN trips t ON u.id = t.user_id
                           LEFT JOIN reviews r ON u.id = r.user_id
                  WHERE u.username LIKE ?
                     OR u.email LIKE ?
                  GROUP BY u.id LIMIT ?
                  OFFSET ?
                  """, (f"%{search}%", f"%{search}%", limit, offset))
    else:
        c.execute("""
                  SELECT u.*,
                         COUNT(DISTINCT t.id) as trip_count,
                         COUNT(DISTINCT r.id) as review_count
                  FROM users u
                           LEFT JOIN trips t ON u.id = t.user_id
                           LEFT JOIN reviews r ON u.id = r.user_id
                  GROUP BY u.id
                  ORDER BY u.created_at DESC LIMIT ?
                  OFFSET ?
                  """, (limit, offset))

    users = [dict(r) for r in c.fetchall()]

    c.execute("SELECT COUNT(*) as total FROM users")
    total = c.fetchone()["total"]

    conn.close()

    return {"users": users, "total": total}


@router.delete("/users/{user_id}")
def delete_user(user_id: int, admin: dict = Depends(require_admin)):
    """Delete a user (admin only)"""
    if user_id == admin["id"]:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    conn = get_db()
    c = conn.cursor()

    # Delete user's data
    c.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
    c.execute("DELETE FROM favorites WHERE user_id = ?", (user_id,))
    c.execute("DELETE FROM trips WHERE user_id = ?", (user_id,))
    c.execute("DELETE FROM reviews WHERE user_id = ?", (user_id,))
    c.execute("DELETE FROM users WHERE id = ?", (user_id,))

    conn.commit()
    conn.close()

    return {"message": "User deleted successfully"}


# Destination management
@router.post("/destinations")
def create_destination(dest: DestinationBase, admin: dict = Depends(require_admin)):
    """Create new destination"""
    conn = get_db()
    c = conn.cursor()

    c.execute("""
              INSERT INTO destinations
              (name, country, city_code, description, best_months, avg_daily_cost,
               flight_cost_estimate, category, image_url, latitude, longitude, rating)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 4.0)
              """, (
                  dest.name, dest.country, dest.city_code, dest.description,
                  dest.best_months, dest.avg_daily_cost, dest.flight_cost_estimate,
                  dest.category, dest.image_url, dest.latitude, dest.longitude
              ))

    dest_id = c.lastrowid
    conn.commit()
    conn.close()

    return {"id": dest_id, "message": "Destination created"}


@router.put("/destinations/{dest_id}")
def update_destination(
        dest_id: int,
        dest: DestinationBase,
        admin: dict = Depends(require_admin)
):
    """Update destination"""
    conn = get_db()
    c = conn.cursor()

    c.execute("""
              UPDATE destinations
              SET name                 = ?,
                  country              = ?,
                  city_code            = ?,
                  description          = ?,
                  best_months          = ?,
                  avg_daily_cost       = ?,
                  flight_cost_estimate = ?,
                  category             = ?,
                  image_url            = ?,
                  latitude             = ?,
                  longitude            = ?
              WHERE id = ?
              """, (
                  dest.name, dest.country, dest.city_code, dest.description,
                  dest.best_months, dest.avg_daily_cost, dest.flight_cost_estimate,
                  dest.category, dest.image_url, dest.latitude, dest.longitude, dest_id
              ))

    if c.rowcount == 0:
        raise HTTPException(status_code=404, detail="Destination not found")

    conn.commit()
    conn.close()

    return {"message": "Destination updated"}


@router.delete("/destinations/{dest_id}")
def delete_destination(dest_id: int, admin: dict = Depends(require_admin)):
    """Delete destination"""
    conn = get_db()
    c = conn.cursor()

    # Delete related data
    c.execute("DELETE FROM favorites WHERE destination_id = ?", (dest_id,))
    c.execute("DELETE FROM reviews WHERE destination_id = ?", (dest_id,))
    c.execute("DELETE FROM trips WHERE destination_id = ?", (dest_id,))
    c.execute("DELETE FROM destinations WHERE id = ?", (dest_id,))

    if c.rowcount == 0:
        raise HTTPException(status_code=404, detail="Destination not found")

    conn.commit()
    conn.close()

    return {"message": "Destination deleted"}


# Review moderation
@router.get("/reviews/pending")
def get_pending_reviews(admin: dict = Depends(require_admin)):
    """Get reviews for moderation"""
    conn = get_db()
    c = conn.cursor()

    c.execute("""
              SELECT r.*, u.username, d.name as destination_name
              FROM reviews r
                       JOIN users u ON r.user_id = u.id
                       JOIN destinations d ON r.destination_id = d.id
              ORDER BY r.created_at DESC LIMIT 50
              """)

    reviews = [dict(r) for r in c.fetchall()]
    conn.close()

    return reviews


@router.delete("/reviews/{review_id}")
def delete_review_admin(review_id: int, admin: dict = Depends(require_admin)):
    """Delete review (admin)"""
    conn = get_db()
    c = conn.cursor()

    # Get destination_id before deletion
    c.execute("SELECT destination_id FROM reviews WHERE id = ?", (review_id,))
    review = c.fetchone()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    destination_id = review["destination_id"]

    c.execute("DELETE FROM reviews WHERE id = ?", (review_id,))

    # Recalculate rating
    c.execute("SELECT AVG(rating) as avg FROM reviews WHERE destination_id = ?", (destination_id,))
    result = c.fetchone()
    avg_rating = result["avg"] if result["avg"] else 4.0

    c.execute("UPDATE destinations SET rating = ? WHERE id = ?", (round(avg_rating, 1), destination_id))

    conn.commit()
    conn.close()

    return {"message": "Review deleted"}


# Trip management
@router.get("/trips/all")
def get_all_trips(
        admin: dict = Depends(require_admin),
        status: Optional[str] = None,
        limit: int = 50
):
    """Get all trips"""
    conn = get_db()
    c = conn.cursor()

    if status:
        c.execute("""
                  SELECT t.*, u.username, d.name as destination_name, d.country
                  FROM trips t
                           JOIN users u ON t.user_id = u.id
                           JOIN destinations d ON t.destination_id = d.id
                  WHERE t.status = ?
                  ORDER BY t.created_at DESC LIMIT ?
                  """, (status, limit))
    else:
        c.execute("""
                  SELECT t.*, u.username, d.name as destination_name, d.country
                  FROM trips t
                           JOIN users u ON t.user_id = u.id
                           JOIN destinations d ON t.destination_id = d.id
                  ORDER BY t.created_at DESC LIMIT ?
                  """, (limit,))

    trips = [dict(r) for r in c.fetchall()]
    conn.close()

    return trips


# Analytics
@router.get("/analytics/revenue")
def get_revenue_analytics(admin: dict = Depends(require_admin)):
    """Get revenue analytics"""
    conn = get_db()
    c = conn.cursor()

    # Revenue by month (last 12 months)
    c.execute("""
              SELECT strftime('%Y-%m', created_at) as month,
            COUNT(*) as bookings,
            SUM(total_cost) as revenue
              FROM trips
              WHERE created_at > date ('now', '-12 months')
              GROUP BY month
              ORDER BY month
              """)

    monthly_revenue = [dict(r) for r in c.fetchall()]

    # Revenue by destination
    c.execute("""
              SELECT d.name,
                     d.country,
                     COUNT(t.id)       as bookings,
                     SUM(t.total_cost) as revenue
              FROM destinations d
                       LEFT JOIN trips t ON d.id = t.destination_id
              GROUP BY d.id
              ORDER BY revenue DESC LIMIT 10
              """)

    destination_revenue = [dict(r) for r in c.fetchall()]

    conn.close()

    return {
        "monthly": monthly_revenue,
        "by_destination": destination_revenue
    }


@router.get("/analytics/users")
def get_user_analytics(admin: dict = Depends(require_admin)):
    """Get user analytics"""
    conn = get_db()
    c = conn.cursor()

    # User growth
    c.execute("""
              SELECT strftime('%Y-%m', created_at) as month,
            COUNT(*) as new_users
              FROM users
              WHERE created_at > date ('now', '-12 months')
              GROUP BY month
              ORDER BY month
              """)

    user_growth = [dict(r) for r in c.fetchall()]

    # Active users (users who made trips in last 30 days)
    c.execute("""
              SELECT COUNT(DISTINCT user_id) as active_users
              FROM trips
              WHERE created_at > date ('now', '-30 days')
              """)

    active_users = c.fetchone()["active_users"]

    conn.close()

    return {
        "growth": user_growth,
        "active_users": active_users
    }