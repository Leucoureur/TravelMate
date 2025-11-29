"""
Script to verify TravelMate backend structure
Run this before starting the server
"""
import os
import sys


def check_file(path, description):
    """Check if a file exists"""
    if os.path.exists(path):
        print(f"✅ {description}: {path}")
        return True
    else:
        print(f"❌ MISSING {description}: {path}")
        return False


def main():
    print("🔍 Checking TravelMate Backend Structure...\n")

    required_files = [
        ("config.py", "Configuration"),
        ("database.py", "Database setup"),
        ("models.py", "Pydantic models"),
        ("main.py", "Main application"),
        ("requirements.txt", "Dependencies"),
        ("auth/__init__.py", "Auth module init"),
        ("auth/utils.py", "Auth utilities"),
        ("auth/routes.py", "Auth routes"),
        ("destinations/__init__.py", "Destinations module init"),
        ("destinations/mock_data.py", "Mock data"),
        ("destinations/routes.py", "Destination routes"),
        ("trips/__init__.py", "Trips module init"),
        ("trips/routes.py", "Trip routes"),
        ("reviews/__init__.py", "Reviews module init"),
        ("reviews/routes.py", "Review routes"),
        ("external/__init__.py", "External module init"),
        ("external/weather.py", "Weather API"),
        ("external/flights.py", "Flights API"),
        ("external/hotels.py", "Hotels API"),
        ("social/__init__.py", "Social module init"),
        ("social/routes.py", "Social routes"),
    ]

    all_good = True
    for file_path, description in required_files:
        if not check_file(file_path, description):
            all_good = False

    print("\n" + "=" * 50)

    if all_good:
        print("✨ All files present! Ready to start.")
        print("\n🚀 Run: python main.py")
        print("📚 Or: uvicorn main:app --reload")
    else:
        print("⚠️  Some files are missing. Please create them.")
        sys.exit(1)


if __name__ == "__main__":
    main()