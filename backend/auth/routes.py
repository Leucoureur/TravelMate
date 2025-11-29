"""
Authentication routes
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials
import sqlite3
from database import get_db
from models import UserCreate, UserLogin, UserResponse
from auth.utils import hash_password, create_session, get_current_user, delete_session, security

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register")
def register(user: UserCreate):
    """Register a new user"""
    conn = get_db()
    c = conn.cursor()
    
    try:
        c.execute(
            "INSERT INTO users (email, username, password_hash) VALUES (?, ?, ?)",
            (user.email, user.username, hash_password(user.password))
        )
        user_id = c.lastrowid
        conn.commit()
        
        token = create_session(user_id)
        
        return {
            "token": token,
            "user": {
                "id": user_id,
                "email": user.email,
                "username": user.username
            }
        }
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="Email or username already exists"
        )
    finally:
        conn.close()

@router.post("/login")
def login(creds: UserLogin):
    """Login user"""
    conn = get_db()
    c = conn.cursor()
    
    c.execute(
        "SELECT * FROM users WHERE email = ? AND password_hash = ?",
        (creds.email, hash_password(creds.password))
    )
    user = c.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user = dict(user)
    token = create_session(user["id"])
    
    return {
        "token": token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "username": user["username"]
        }
    }

@router.get("/me", response_model=UserResponse)
def get_me(user: dict = Depends(get_current_user)):
    """Get current user info"""
    return {
        "id": user["id"],
        "email": user["email"],
        "username": user["username"],
        "avatar_url": user.get("avatar_url")
    }

@router.post("/logout")
def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout user"""
    delete_session(credentials.credentials)
    return {"message": "Logged out successfully"}