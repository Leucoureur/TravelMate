# TravelMate - Professional Travel Planning Platform

A full-stack travel application with modular architecture and extensive mock data.

## 🏗️ Architecture

### Backend Structure (Professional & Maintainable)

```
backend/
├── main.py                    # Application entry point
├── config.py                  # Configuration & settings
├── database.py                # Database connection & init
├── models.py                  # Pydantic models
├── requirements.txt
├── .env                       # Environment variables
├── auth/
│   ├── __init__.py
│   ├── utils.py              # Auth helpers & middleware
│   └── routes.py             # Auth endpoints
├── destinations/
│   ├── __init__.py
│   ├── routes.py             # Destination endpoints
│   └── mock_data.py          # 26+ destinations
├── trips/
│   ├── __init__.py
│   └── routes.py             # Trip management
├── reviews/
│   ├── __init__.py
│   └── routes.py             # Reviews & ratings
├── external/
│   ├── __init__.py
│   ├── weather.py            # Weather API (real + mock)
│   ├── flights.py            # Flight search (real + mock)
│   └── hotels.py             # Hotel search (mock)
└── social/
    ├── __init__.py
    └── routes.py             # Sharing & favorites
```

## ✨ New Features

### 💰 Budget Range 
- Set **minimum** and **maximum** budget
- Flexible price filtering
- Better matching algorithm

### 📊 Enhanced Mock Data
- **26 destinations** across 6 continents
- Realistic flight prices and durations
- 8+ hotels per destination (all star ratings)
- Climate-aware weather forecasts
- 12 airline options

### 🎯 Better AI Suggestions
- Scores destinations on multiple factors
- Considers value for money
- Seasonal recommendations
- Returns top 8 matches

## 🚀 Quick Start

### 1. Backend Setup

```bash

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn pydantic[email] httpx python-dotenv

# Save all Python files from artifacts

# Create .env (optional - works without API keys)
cat > .env << EOF
WEATHER_API_KEY=
AMADEUS_API_KEY=
AMADEUS_API_SECRET=
SECRET_KEY=your-secret-key-here
EOF

# Run server
python main.py
# or
uvicorn main:app --reload
```

**Backend:** http://localhost:8000  
**API Docs:** http://localhost:8000/docs

### 2. Frontend Setup

```bash
# From project root
cd ..
npm create vite@latest frontend -- --template react
cd frontend
npm install

# Replace src/App.jsx and src/App.css

# Run
npm run dev
```

**Frontend:** http://localhost:5173

---

## 📋 File Creation Checklist

Copy these files from the artifacts in order:

### Backend Files
1. ✅ `config.py` - Configuration
2. ✅ `database.py` - Database setup
3. ✅ `models.py` - Pydantic models
4. ✅ `auth/utils.py` - Auth utilities
5. ✅ `auth/routes.py` - Auth endpoints
6. ✅ `destinations/mock_data.py` - Mock destinations (26+)
7. ✅ `destinations/routes.py` - Destination endpoints
8. ✅ `trips/routes.py` - Trip management
9. ✅ `reviews/routes.py` - Reviews & ratings
10. ✅ `external/weather.py` - Weather API
11. ✅ `external/flights.py` - Flight search
12. ✅ `external/hotels.py` - Hotel search
13. ✅ `social/routes.py` - Sharing & favorites
14. ✅ `main.py` - Application entry
15. ✅ `requirements.txt` - Dependencies

### Frontend Files
16. ✅ `src/App.jsx` - React app (with budget range)
17. ✅ `src/App.css` - Styles

---

## 🌍 Mock Data Included

### Destinations (26)
- **Europe:** Paris, Barcelona, Rome, Santorini, Iceland, Amsterdam, Prague, Lisbon
- **Asia:** Tokyo, Bali, Thailand, Dubai, Singapore, Seoul, Maldives, Vietnam
- **Americas:** New York, Machu Picchu, Rio, Mexico City, Cancun
- **Africa & Oceania:** Cape Town, Marrakech, Sydney, New Zealand, Egypt

### Airlines (12)
Air France, British Airways, Lufthansa, Emirates, Qatar Airways, Singapore Airlines, American Airlines, Delta, United, KLM, Turkish Airlines, Finnair

### Hotels
- 2-5 star options for each destination
- Realistic pricing based on location
- Full amenities lists
- Ratings and reviews

### Weather
- Climate-zone aware forecasts
- Realistic temperature ranges
- Seasonal variations

---

## 🎯 API Endpoints

### Auth
```
POST   /auth/register         # Create account
POST   /auth/login            # Login
GET    /auth/me               # Get current user
POST   /auth/logout           # Logout
```

### Destinations
```
GET    /destinations          # List all (with favorites)
GET    /destinations/{id}     # Get single
POST   /destinations/suggestions  # AI suggestions (budget range!)
GET    /destinations/categories/list  # Get categories
```

### Trips
```
GET    /trips                 # List user trips
POST   /trips                 # Create trip
GET    /trips/{id}            # Get single trip
DELETE /trips/{id}            # Delete trip
PUT    /trips/{id}/status     # Update status
```

### Reviews
```
GET    /reviews/{dest_id}     # Get reviews
POST   /reviews               # Create review
POST   /reviews/{id}/helpful  # Mark helpful
DELETE /reviews/{id}          # Delete own review
```

### External APIs
```
GET    /weather/{dest_id}     # Weather forecast
GET    /flights/search        # Search flights
GET    /flights/airlines      # List airlines
GET    /hotels/search         # Search hotels
GET    /hotels/{id}/details   # Hotel details
```

### Social
```
POST   /trips/{id}/share      # Create share link
GET    /shared/{token}        # View shared trip (public)
DELETE /trips/{id}/share      # Make trip private
GET    /favorites             # List favorites
POST   /favorites/{dest_id}   # Add favorite
DELETE /favorites/{dest_id}   # Remove favorite
GET    /favorites/check/{dest_id}  # Check if favorited
```

---

## 🔑 Optional API Keys

The app works perfectly with mock data, but you can add real APIs:

### OpenWeatherMap (Weather)
1. Sign up: https://openweathermap.org/api
2. Add to `.env`: `WEATHER_API_KEY=your_key`

### Amadeus (Flights)
1. Sign up: https://developers.amadeus.com
2. Create app
3. Add to `.env`:
   ```
   AMADEUS_API_KEY=your_key
   AMADEUS_API_SECRET=your_secret
   ```

**The app automatically falls back to mock data if APIs fail!**

## 🐛 Troubleshooting

**"Module not found"**
- Make sure all `__init__.py` files exist
- Check file names match exactly

**"Table doesn't exist"**
- Delete `travel.db` and restart
- Database auto-creates on startup

**"CORS error"**
- Check backend is running on port 8000
- Check frontend is on port 5173

---

## 📝 License

MIT License - Free to use and modify!