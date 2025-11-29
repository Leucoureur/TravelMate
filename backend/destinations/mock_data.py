"""
Enhanced mock data for destinations
"""

DESTINATIONS = [
    # Europe
    ("Paris", "France", "PAR", "The City of Light - art, cuisine, and romance", "4,5,6,9,10", 150, 600, "culture", "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=400", 48.8566, 2.3522, 4.8),
    ("Barcelona", "Spain", "BCN", "Gaudi architecture, beaches, and vibrant nightlife", "5,6,9,10", 100, 500, "culture", "https://images.unsplash.com/photo-1583422409516-2895a77efded?w=400", 41.3851, 2.1734, 4.7),
    ("Rome", "Italy", "ROM", "Eternal city of ancient history and gastronomy", "4,5,9,10", 120, 550, "culture", "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=400", 41.9028, 12.4964, 4.8),
    ("Santorini", "Greece", "JTR", "Stunning sunsets and whitewashed buildings", "5,6,9,10", 130, 550, "beach", "https://images.unsplash.com/photo-1613395877344-13d4a8e0d49e?w=400", 36.3932, 25.4615, 4.8),
    ("Iceland", "Iceland", "REK", "Northern lights and dramatic landscapes", "9,10,2,3", 170, 700, "adventure", "https://images.unsplash.com/photo-1529963183134-61a90db47eaf?w=400", 64.1466, -21.9426, 4.8),
    ("Amsterdam", "Netherlands", "AMS", "Canals, museums, and cycling culture", "4,5,9", 140, 450, "city", "https://images.unsplash.com/photo-1534351590666-13e3e96b5017?w=400", 52.3676, 4.9041, 4.6),
    ("Prague", "Czech Republic", "PRG", "Medieval architecture and beer culture", "5,6,9,10", 80, 400, "culture", "https://images.unsplash.com/photo-1541849546-216549ae216d?w=400", 50.0755, 14.4378, 4.7),
    ("Lisbon", "Portugal", "LIS", "Colorful tiles, hills, and Atlantic coast", "5,6,9,10", 90, 500, "city", "https://images.unsplash.com/photo-1555881400-74d7acaacd8b?w=400", 38.7223, -9.1393, 4.6),
    
    # Asia
    ("Tokyo", "Japan", "TYO", "Ancient traditions meet cutting-edge technology", "3,4,10,11", 120, 900, "culture", "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=400", 35.6762, 139.6503, 4.9),
    ("Bali", "Indonesia", "DPS", "Tropical paradise with temples and beaches", "4,5,6,9", 60, 700, "beach", "https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=400", -8.3405, 115.0920, 4.7),
    ("Thailand", "Thailand", "BKK", "Temples, beaches, and incredible street food", "11,12,1,2,3", 50, 750, "beach", "https://images.unsplash.com/photo-1528181304800-259b08848526?w=400", 13.7563, 100.5018, 4.6),
    ("Dubai", "UAE", "DXB", "Luxury shopping and ultramodern architecture", "11,12,1,2,3", 180, 650, "luxury", "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=400", 25.2048, 55.2708, 4.5),
    ("Singapore", "Singapore", "SIN", "Futuristic city-state with amazing food", "1,2,3,7,8,12", 150, 800, "city", "https://images.unsplash.com/photo-1525625293386-3f8f99389edd?w=400", 1.3521, 103.8198, 4.7),
    ("Seoul", "South Korea", "SEL", "K-pop culture, tech, and traditional palaces", "4,5,9,10", 100, 850, "city", "https://images.unsplash.com/photo-1517154421773-0529f29ea451?w=400", 37.5665, 126.9780, 4.6),
    ("Maldives", "Maldives", "MLE", "Overwater bungalows and crystal clear waters", "1,2,3,4,11,12", 300, 900, "luxury", "https://images.unsplash.com/photo-1514282401047-d79a71a590e8?w=400", 3.2028, 73.2207, 4.9),
    ("Vietnam", "Vietnam", "HAN", "Rich history, stunning landscapes, delicious pho", "2,3,4,10,11", 45, 700, "culture", "https://images.unsplash.com/photo-1583417267826-aebc4d1542e1?w=400", 21.0285, 105.8542, 4.5),
    
    # Americas
    ("New York", "USA", "NYC", "The city that never sleeps", "4,5,9,10,11,12", 200, 400, "city", "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=400", 40.7128, -74.0060, 4.6),
    ("Machu Picchu", "Peru", "CUZ", "Ancient Incan citadel in the clouds", "4,5,9,10", 80, 800, "adventure", "https://images.unsplash.com/photo-1587595431973-160d0d94add1?w=400", -13.1631, -72.5450, 4.9),
    ("Rio de Janeiro", "Brazil", "GIG", "Beaches, carnival, and Christ the Redeemer", "12,1,2,3,4,5", 85, 750, "beach", "https://images.unsplash.com/photo-1483729558449-99ef09a8c325?w=400", -22.9068, -43.1729, 4.5),
    ("Mexico City", "Mexico", "MEX", "Ancient pyramids, vibrant culture, amazing tacos", "3,4,5,10,11", 70, 450, "culture", "https://images.unsplash.com/photo-1518105779142-d975f22f1b0a?w=400", 19.4326, -99.1332, 4.4),
    ("Cancun", "Mexico", "CUN", "Caribbean beaches and Mayan ruins", "12,1,2,3,4", 110, 500, "beach", "https://images.unsplash.com/photo-1568402102990-bc541580b59f?w=400", 21.1619, -86.8515, 4.6),
    
    # Africa & Oceania
    ("Cape Town", "South Africa", "CPT", "Table Mountain, wine country, and beaches", "1,2,3,11,12", 95, 850, "adventure", "https://images.unsplash.com/photo-1580060839134-75a5edca2e99?w=400", -33.9249, 18.4241, 4.7),
    ("Marrakech", "Morocco", "RAK", "Medinas, souks, and Sahara gateway", "3,4,5,10,11", 70, 550, "culture", "https://images.unsplash.com/photo-1597212618440-806262de4f6b?w=400", 31.6295, -7.9811, 4.5),
    ("Sydney", "Australia", "SYD", "Opera House, beaches, and harbor life", "9,10,11,12,1,2,3", 160, 1100, "city", "https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?w=400", -33.8688, 151.2093, 4.7),
    ("New Zealand", "New Zealand", "AKL", "Lord of the Rings landscapes and adventure sports", "12,1,2,3", 130, 1000, "adventure", "https://images.unsplash.com/photo-1507699622108-4be3abd695ad?w=400", -36.8485, 174.7633, 4.8),
    ("Egypt", "Egypt", "CAI", "Pyramids, Nile River, and ancient wonders", "10,11,2,3,4", 75, 600, "culture", "https://images.unsplash.com/photo-1572252821143-035a024857ac?w=400", 30.0444, 31.2357, 4.6),
]

def seed_destinations(cursor):
    """Seed database with destination data"""
    # Check if already seeded
    cursor.execute("SELECT COUNT(*) FROM destinations")
    if cursor.fetchone()[0] > 0:
        return
    
    cursor.executemany("""
        INSERT INTO destinations 
        (name, country, city_code, description, best_months, avg_daily_cost, 
         flight_cost_estimate, category, image_url, latitude, longitude, rating)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, DESTINATIONS)