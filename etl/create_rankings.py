"""
Calculate scores for all towns and create rankings.
"""
import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('data/agewell.db')

# Load all data
df = pd.read_sql_query("SELECT * FROM amenities", conn)
conn.close()

print(f"📊 Loaded data for {len(df)} towns\n")

# Define the metrics for each pillar
metrics = {
    'care_access': ['pharmacies'],
    'green_quiet': ['parks'],
    'active_living': ['leisure_centres', 'gyms'],
    'social_fabric': ['community_centres'],
    'mobility_safety': ['bus_stops']
}

# Normalize each metric to 0-100 (min-max scaling)
def normalize(series):
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return pd.Series([50] * len(series))
    return 100 * (series - min_val) / (max_val - min_val)

# Calculate pillar scores
df['care_score'] = normalize(df['pharmacies'])
df['green_score'] = normalize(df['parks'])
df['active_score'] = (normalize(df['leisure_centres']) + normalize(df['gyms'])) / 2
df['social_score'] = normalize(df['community_centres'])
df['mobility_score'] = normalize(df['bus_stops'])

# Calculate overall score (equal weights for now)
df['overall_score'] = (
    df['care_score'] + 
    df['green_score'] + 
    df['active_score'] + 
    df['social_score'] + 
    df['mobility_score']
) / 5

# Round scores
score_cols = ['care_score', 'green_score', 'active_score', 'social_score', 'mobility_score', 'overall_score']
df[score_cols] = df[score_cols].round(1)

# Sort by overall score
df_ranked = df.sort_values('overall_score', ascending=False)

# Display top 10
print("🏆 TOP 10 TOWNS:\n")
print(df_ranked[['town', 'care_score', 'green_score', 'active_score', 'social_score', 'mobility_score', 'overall_score']].head(10).to_string(index=False))

print("\n\n📉 BOTTOM 5 TOWNS:\n")
print(df_ranked[['town', 'care_score', 'green_score', 'active_score', 'social_score', 'mobility_score', 'overall_score']].tail(5).to_string(index=False))

# Save to CSV
df_ranked.to_csv('data/processed/rankings.csv', index=False)
print("\n\n💾 Full rankings saved to data/processed/rankings.csv")

