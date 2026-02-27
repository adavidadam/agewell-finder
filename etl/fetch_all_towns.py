"""
Fetch pharmacy and park data for all 30 pilot towns.
Save results to SQLite database.
"""
import osmnx as ox
import sqlite3
import time

# All 30 pilot towns with coordinates
TOWNS = {
    'Bath': (51.3811, -2.3590),
    'Bournemouth': (50.7192, -1.8808),
    'Brighton and Hove': (50.8270, -0.1687),
    'Cambridge': (52.2053, 0.1218),
    'Canterbury': (51.2798, 1.0837),
    'Cheltenham': (51.9000, -2.0800),
    'Chichester': (50.8367, -0.7800),
    'Colchester': (51.8892, 0.9042),
    'Exeter': (50.7184, -3.5339),
    'Guildford': (51.2362, -0.5704),
    'Harrogate': (53.9921, -1.5418),
    'Ipswich': (52.0567, 1.1482),
    'Kendal': (54.3280, -2.7460),
    'Lancaster': (54.0470, -2.8010),
    'Lichfield': (52.6810, -1.8262),
    'Lincoln': (53.2307, -0.5406),
    'Norwich': (52.6309, 1.2974),
    'Oxford': (51.7520, -1.2577),
    'Plymouth': (50.3755, -4.1427),
    'Poole': (50.7184, -1.9810),
    'Salisbury': (51.0688, -1.7945),
    'Scarborough': (54.2831, -0.3996),
    'Shrewsbury': (52.7073, -2.7553),
    'Southport': (53.6477, -3.0065),
    'St Albans': (51.7527, -0.3394),
    'Taunton': (51.0153, -3.1069),
    'Truro': (50.2632, -5.0510),
    'Winchester': (51.0629, -1.3101),
    'Worthing': (50.8148, -0.3719),
    'York': (53.9590, -1.0815),
    'Lewes': (50.8750, -0.0170),
    'Totnes': (50.4312, -3.6846)
}

RADIUS_M = 2000

# Create database
conn = sqlite3.connect('data/agewell.db')
cursor = conn.cursor()

# Create table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS amenities (
        town TEXT PRIMARY KEY,
        lat REAL,
        lon REAL,
        pharmacies INTEGER,
        parks INTEGER,
        fetched_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
''')

print("🚀 Fetching data for 32 towns...\n")

for i, (town, (lat, lon)) in enumerate(TOWNS.items(), 1):
    print(f"[{i}/32] {town}...", end=" ")
    
    try:
        # Fetch pharmacies
        pharmacies = ox.features_from_point(
            (lat, lon),
            tags={'amenity': 'pharmacy'},
            dist=RADIUS_M
        )
        pharm_count = len(pharmacies)
        
        # Fetch parks
        parks = ox.features_from_point(
            (lat, lon),
            tags={'leisure': 'park'},
            dist=RADIUS_M
        )
        parks_count = len(parks)
        
        # Save to database
        cursor.execute('''
            INSERT OR REPLACE INTO amenities (town, lat, lon, pharmacies, parks)
            VALUES (?, ?, ?, ?, ?)
        ''', (town, lat, lon, pharm_count, parks_count))
        
        conn.commit()
        
        print(f"✅ {pharm_count} pharmacies, {parks_count} parks")
        
        # Be nice to OSM servers
        time.sleep(0.5)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        continue

conn.close()

print("\n✨ Complete! Data saved to data/agewell.db")
print("\nTo view results, run: sqlite3 data/agewell.db 'SELECT * FROM amenities'")
