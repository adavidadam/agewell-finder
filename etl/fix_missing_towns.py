"""
Re-fetch with larger 5km radius for smaller towns.
"""
import osmnx as ox
import sqlite3
import time

TOWNS = {
    'Lewes': (50.8750, -0.0170),
    'Totnes': (50.4312, -3.6846),
    'Salisbury': (51.0688, -1.7945),
    'Southport': (53.6477, -3.0065)
}

RADIUS_M = 5000  # Increase to 5km

conn = sqlite3.connect('data/agewell.db')
cursor = conn.cursor()

print("🔧 Trying 5km radius for smaller towns...\n")

for town, (lat, lon) in TOWNS.items():
    print(f"{town}...", end=" ")
    
    lc, gy, cc, bus = 0, 0, 0, 0
    
    try:
        leisure = ox.features_from_point((lat, lon), tags={'leisure': 'sports_centre'}, dist=RADIUS_M)
        lc = len(leisure)
    except:
        pass
    
    try:
        gyms = ox.features_from_point((lat, lon), tags={'leisure': 'fitness_centre'}, dist=RADIUS_M)
        gy = len(gyms)
    except:
        pass
    
    try:
        community = ox.features_from_point((lat, lon), tags={'amenity': 'community_centre'}, dist=RADIUS_M)
        cc = len(community)
    except:
        pass
    
    try:
        bus_stops = ox.features_from_point((lat, lon), tags={'highway': 'bus_stop'}, dist=RADIUS_M)
        bus = len(bus_stops)
    except:
        pass
    
    cursor.execute('''
        UPDATE amenities 
        SET leisure_centres = ?, gyms = ?, community_centres = ?, bus_stops = ?
        WHERE town = ?
    ''', (lc, gy, cc, bus, town))
    
    conn.commit()
    print(f"✅ LC:{lc} G:{gy} CC:{cc} Bus:{bus}")
    time.sleep(0.5)

conn.close()
print("\n✨ Complete!")
