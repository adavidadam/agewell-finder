import osmnx as ox

lat, lon = 51.2798, 1.0837
radius = 2000

print(f"Searching for GPs within {radius}m of Canterbury center...")

try:
    gps = ox.features_from_point((lat, lon), tags={'amenity': 'doctors'}, dist=radius)
    print(f"\nFound {len(gps)} GP surgeries")
    
    if len(gps) > 0:
        print("\nGP surgeries found:")
        for idx, row in gps.iterrows():
            name = row.get('name', 'Unnamed')
            print(f"  - {name}")
    else:
        print("\nNo GPs found in OSM data for Canterbury")
        
except Exception as e:
    print(f"Error: {e}")
