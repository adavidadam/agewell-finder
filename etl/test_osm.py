"""
Test if we can fetch real amenity data from OpenStreetMap.
"""
import osmnx as ox

# Bath coordinates
BATH_LAT = 51.3811
BATH_LON = -2.3590
RADIUS_M = 2000  # 2km radius

print("🔍 Testing OSM data fetch for Bath...")
print(f"   Looking within {RADIUS_M}m of city center\n")

try:
    # Try to get pharmacies
    print("📍 Fetching pharmacies...")
    pharmacies = ox.features_from_point(
        (BATH_LAT, BATH_LON),
        tags={'amenity': 'pharmacy'},
        dist=RADIUS_M
    )
    print(f"✅ Found {len(pharmacies)} pharmacies in Bath")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n✨ Test complete!")
