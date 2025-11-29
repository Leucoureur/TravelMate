"""
TravelMate API - Main Application Entry Point
Professional structure with modular architecture
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configuration
from config import settings

# Database
from database import init_db, get_db
from destinations.mock_data import seed_destinations

# Routers
from auth.routes import router as auth_router
from destinations.routes import router as destinations_router
from trips.routes import router as trips_router
from reviews.routes import router as reviews_router
from external.weather import router as weather_router
from external.flights import router as flights_router
from external.hotels import router as hotels_router
from social.routes import router as social_router
from admin.routes import router as admin_router

# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth_router)
app.include_router(destinations_router)
app.include_router(trips_router)
app.include_router(reviews_router)
app.include_router(weather_router)
app.include_router(flights_router)
app.include_router(hotels_router)
app.include_router(social_router)
app.include_router(admin_router)

# Root endpoint
@app.get("/")
def root():
    """API root endpoint"""
    return {
        "message": "Welcome to TravelMate API",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "status": "operational"
    }

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "version": settings.API_VERSION
    }

# Startup event
@app.on_event("startup")
def startup_event():
    """Initialize database and seed data on startup"""
    print("🚀 Starting TravelMate API...")
    
    # Initialize database
    init_db()
    print("✅ Database initialized")
    
    # Seed destinations if needed
    conn = get_db()
    c = conn.cursor()
    seed_destinations(c)
    conn.commit()
    conn.close()
    print("✅ Mock data loaded")
    
    print(f"🌍 API running at http://localhost:8000")
    print(f"📚 Documentation at http://localhost:8000/docs")

# Shutdown event
@app.on_event("shutdown")
def shutdown_event():
    """Cleanup on shutdown"""
    print("👋 Shutting down TravelMate API...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )