"""
Authentication utilities
"""
import hashlib
import secrets
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from database import get_db
from config import settings

security = HTTPBearer()

def hash_password(password: str) -> str:
    """Hash a password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_session(user_id: int) -> str:
    """Create a new session token for user"""
    token = secrets.token_urlsafe(32)
    expires = datetime.now() + timedelta(days=settings.SESSION_EXPIRY_DAYS)
    
    conn = get_db()
    conn.execute(
        "INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)",
        (user_id, token, expires.isoformat())
    )
    conn.commit()
    conn.close()
    
    return token

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user from token"""
    token = credentials.credentials
    conn = get_db()
    c = conn.cursor()
    
    c.execute("""
        SELECT u.* FROM users u
        JOIN sessions s ON u.id = s.user_id
        WHERE s.token = ? AND s.expires_at > ?
    """, (token, datetime.now().isoformat()))
    
    user = c.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return dict(user)

def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
):
    """Get user if authenticated, None otherwise"""
    if not credentials:
        return None
    try:
        return get_current_user(credentials)
    except:
        return None

def delete_session(token: str):
    """Delete a session token (logout)"""
    conn = get_db()
    conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
    conn.commit()
    conn.close()