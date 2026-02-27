"""
Add GP surgery data to existing towns.
"""
import osmnx as ox
import sqlite3
import time

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

conn = sqlite3.connect('data/agewell.db')
cursor = conn.cursor()

# Add GP column
try:
    cursor.execute('ALTER TABLE amenities ADD COLUMN gp_surgeries INTEGER DEFAULT 0')
except:
    pass

print("🏥 Fetching GP surgeries...\n")

for i, (town, (lat, lon)) in enumerate(TOWNS.items(), 1):
    print(f"[{i}/32] {town}...", end=" ")
    
    gp_count = 0
    try:
        gps = ox.features_from_point((lat, lon), tags={'amenity': 'doctors'}, dist=RADIUS_M)
        gp_count = len(gps)
    except:
        pass
    
    cursor.execute('UPDATE amenities SET gp_surgeries = ? WHERE town = ?', (gp_count, town))
    conn.commit()
    
    print(f"✅ {gp_count} GPs")
    time.sleep(0.5)

conn.close()
print("\n✨ Complete!")
