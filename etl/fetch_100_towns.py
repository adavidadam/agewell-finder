"""
Fetch all amenity data for 100 UK towns
"""
import osmnx as ox
import sqlite3
import time
from datetime import datetime

# Import the town list
exec(open('etl/towns_100.py').read())

RADIUS_M = 2000
SMALL_TOWN_RADIUS = 5000

# Towns that need larger radius
SMALL_TOWNS = ['Lewes', 'Totnes', 'Salisbury', 'Southport', 'Bude', 'Fowey', 
               'Cockermouth', 'Settle', 'Helmsley', 'Hay-on-Wye']

conn = sqlite3.connect('data/agewell.db')
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS amenities (
        town TEXT PRIMARY KEY,
        county TEXT,
        lat REAL,
        lon REAL,
        pharmacies INTEGER DEFAULT 0,
        parks INTEGER DEFAULT 0,
        leisure_centres INTEGER DEFAULT 0,
        gyms INTEGER DEFAULT 0,
        community_centres INTEGER DEFAULT 0,
        bus_stops INTEGER DEFAULT 0,
        gp_surgeries INTEGER DEFAULT 0,
        fetched_at TEXT
    )
''')

print(f"🏙️ Fetching data for {len(TOWNS_100)} towns...\n")

for i, (town, (lat, lon, county)) in enumerate(TOWNS_100.items(), 1):
    print(f"[{i}/{len(TOWNS_100)}] {town}, {county}...")
    
    radius = SMALL_TOWN_RADIUS if town in SMALL_TOWNS else RADIUS_M
    
    # Fetch all metrics
    counts = {
        'pharmacies': 0,
        'gp_surgeries': 0,
        'parks': 0,
        'leisure_centres': 0,
        'gyms': 0,
        'community_centres': 0,
        'bus_stops': 0
    }
    
    try:
        # Pharmacies
        try:
            pharmacies = ox.features_from_point((lat, lon), tags={'amenity': 'pharmacy'}, dist=radius)
            counts['pharmacies'] = len(pharmacies)
        except:
            pass
        
        # GP surgeries
        try:
            gps = ox.features_from_point((lat, lon), tags={'amenity': 'doctors'}, dist=radius)
            counts['gp_surgeries'] = len(gps)
        except:
            pass
        
        # Parks
        try:
            parks = ox.features_from_point((lat, lon), tags={'leisure': 'park'}, dist=radius)
            counts['parks'] = len(parks)
        except:
            pass
        
        # Leisure centres
        try:
            leisure = ox.features_from_point((lat, lon), tags={'leisure': 'sports_centre'}, dist=radius)
            counts['leisure_centres'] = len(leisure)
        except:
            pass
        
        # Gyms
        try:
            gyms = ox.features_from_point((lat, lon), tags={'leisure': 'fitness_centre'}, dist=radius)
            counts['gyms'] = len(gyms)
        except:
            pass
        
        # Community centres
        try:
            community = ox.features_from_point((lat, lon), tags={'amenity': 'community_centre'}, dist=radius)
            counts['community_centres'] = len(community)
        except:
            pass
        
        # Bus stops
        try:
            buses = ox.features_from_point((lat, lon), tags={'highway': 'bus_stop'}, dist=radius)
            counts['bus_stops'] = len(buses)
        except:
            pass
        
    except Exception as e:
        print(f"   ⚠️ Error: {e}")
    
    # Insert or update
    cursor.execute('''
        INSERT OR REPLACE INTO amenities 
        (town, county, lat, lon, pharmacies, gp_surgeries, parks, leisure_centres, 
         gyms, community_centres, bus_stops, fetched_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (town, county, lat, lon, counts['pharmacies'], counts['gp_surgeries'],
          counts['parks'], counts['leisure_centres'], counts['gyms'], 
          counts['community_centres'], counts['bus_stops'], 
          datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    
    conn.commit()
    
    print(f"   ✅ GPs:{counts['gp_surgeries']} Pharmacies:{counts['pharmacies']} "
          f"Parks:{counts['parks']} Leisure:{counts['leisure_centres']} "
          f"Gyms:{counts['gyms']} Community:{counts['community_centres']} "
          f"Bus:{counts['bus_stops']}")
    
    time.sleep(0.5)  # Be nice to OSM servers

conn.close()
print("\n✨ Complete! 100 towns in database.")
