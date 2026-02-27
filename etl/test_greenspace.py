"""
Check if we can work with green space data.
For now, just test the concept with OSM parks as a backup.
"""
import osmnx as ox

BATH_LAT = 51.3811
BATH_LON = -2.3590
RADIUS_M = 1000  # 1km radius

print("🌳 Testing green space data for Bath...\n")

try:
    print("📍 Fetching parks from OSM...")
    parks = ox.features_from_point(
        (BATH_LAT, BATH_LON),
        tags={'leisure': 'park'},
        dist=RADIUS_M
    )
    print(f"✅ Found {len(parks)} parks in Bath (1km radius)")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n✨ Test complete!")
