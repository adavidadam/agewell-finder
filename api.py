"""
Simple API to serve AgeWell rankings.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

app = FastAPI(title="AgeWell Finder API")

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TownRanking(BaseModel):
    town: str
    county: str
    lat: float
    lon: float
    pharmacies: int
    parks: int
    leisure_centres: int
    gyms: int
    community_centres: int
    bus_stops: int
    gp_surgeries: int
    avg_house_price: int
    care_score: float
    green_score: float
    active_score: float
    social_score: float
    mobility_score: float
    overall_score: float


class TownRecommendation(BaseModel):
    rank: int
    town: str
    county: str
    overall_score: float
    avg_house_price: int
    reasons: List[str]


class QuickShortlistResponse(BaseModel):
    count: int
    filters: Dict[str, Any]
    recommendations: List[TownRecommendation]

def get_db():
    conn = sqlite3.connect('data/agewell.db')
    conn.row_factory = sqlite3.Row
    return conn

def calculate_scores(towns):
    """Calculate normalized scores for all towns."""
    import pandas as pd
    
    df = pd.DataFrame([dict(t) for t in towns])
    
    # Normalize function
    def normalize(series):
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return pd.Series([50.0] * len(series))
        return 100.0 * (series - min_val) / (max_val - min_val)
    
    # Calculate scores
    df['care_score'] = (normalize(df['pharmacies']) + normalize(df['gp_surgeries'])) / 2
    df['green_score'] = normalize(df['parks'])
    df['active_score'] = (normalize(df['leisure_centres']) + normalize(df['gyms'])) / 2
    df['social_score'] = normalize(df['community_centres'])
    df['mobility_score'] = normalize(df['bus_stops'])
    
    # Overall score with weights (default equal)
    df['overall_score'] = (
        df['care_score'] + df['green_score'] + 
        df['active_score'] + df['social_score'] + df['mobility_score']
    ) / 5
    
    # Round
    score_cols = ['care_score', 'green_score', 'active_score', 'social_score', 'mobility_score', 'overall_score']
    df[score_cols] = df[score_cols].round(1)
    
    df['avg_house_price'] = df['avg_house_price'].fillna(0).astype(int)
    return df

@app.get("/")
def root():
    return {"message": "AgeWell Finder API", "version": "0.1"}

@app.get("/towns", response_model=List[TownRanking])
def get_towns(
    care_weight: float = 1.0,
    green_weight: float = 1.0,
    active_weight: float = 1.0,
    social_weight: float = 1.0,
    mobility_weight: float = 1.0,
    limit: Optional[int] = None
):
    """Get all towns with scores, optionally with custom weights."""
    conn = get_db()
    towns = conn.execute("SELECT * FROM amenities").fetchall()
    conn.close()
    
    df = calculate_scores(towns)
    
    # Apply custom weights if provided
    total_weight = care_weight + green_weight + active_weight + social_weight + mobility_weight
    df['overall_score'] = (
        df['care_score'] * care_weight +
        df['green_score'] * green_weight +
        df['active_score'] * active_weight +
        df['social_score'] * social_weight +
        df['mobility_score'] * mobility_weight
    ) / total_weight
    df['overall_score'] = df['overall_score'].round(1)
    
    # Sort by overall score
    df = df.sort_values('overall_score', ascending=False)
    
    # Limit results if requested
    if limit:
        df = df.head(limit)
    
    return df.to_dict('records')


@app.get('/quick-shortlist', response_model=QuickShortlistResponse)
def quick_shortlist(
    max_price: Optional[int] = None,
    min_care: float = 0,
    min_green: float = 0,
    min_active: float = 0,
    min_social: float = 0,
    min_mobility: float = 0,
    care_weight: float = 1.0,
    green_weight: float = 1.0,
    active_weight: float = 1.0,
    social_weight: float = 1.0,
    mobility_weight: float = 1.0,
    limit: int = 5
):
    """Return a practical top-N shortlist with plain-English reasons."""
    conn = get_db()
    towns = conn.execute("SELECT * FROM amenities").fetchall()
    conn.close()

    df = calculate_scores(towns)

    total_weight = care_weight + green_weight + active_weight + social_weight + mobility_weight
    df['overall_score'] = (
        df['care_score'] * care_weight +
        df['green_score'] * green_weight +
        df['active_score'] * active_weight +
        df['social_score'] * social_weight +
        df['mobility_score'] * mobility_weight
    ) / total_weight
    df['overall_score'] = df['overall_score'].round(1)

    if max_price and max_price > 0:
        df = df[(df['avg_house_price'] > 0) & (df['avg_house_price'] <= max_price)]

    df = df[
        (df['care_score'] >= min_care) &
        (df['green_score'] >= min_green) &
        (df['active_score'] >= min_active) &
        (df['social_score'] >= min_social) &
        (df['mobility_score'] >= min_mobility)
    ]

    df = df.sort_values('overall_score', ascending=False).head(max(1, min(limit, 20)))

    recs = []
    for i, row in enumerate(df.to_dict('records'), start=1):
        strongest = sorted([
            ('Care', row['care_score']),
            ('Green', row['green_score']),
            ('Active', row['active_score']),
            ('Community', row['social_score']),
            ('Transport', row['mobility_score']),
        ], key=lambda x: x[1], reverse=True)[:2]

        reasons = [
            f"{strongest[0][0]} score {strongest[0][1]:.0f}",
            f"{strongest[1][0]} score {strongest[1][1]:.0f}",
            f"Area median price £{int(row['avg_house_price']):,}" if int(row['avg_house_price']) > 0 else 'Price currently unavailable'
        ]

        recs.append({
            'rank': i,
            'town': row['town'],
            'county': row['county'],
            'overall_score': row['overall_score'],
            'avg_house_price': int(row['avg_house_price'] or 0),
            'reasons': reasons
        })

    return {
        'count': len(recs),
        'filters': {
            'max_price': max_price,
            'min_care': min_care,
            'min_green': min_green,
            'min_active': min_active,
            'min_social': min_social,
            'min_mobility': min_mobility,
            'weights': {
                'care': care_weight,
                'green': green_weight,
                'active': active_weight,
                'social': social_weight,
                'mobility': mobility_weight
            },
            'limit': limit
        },
        'recommendations': recs
    }


@app.get("/town/{town_name}")
def get_town(town_name: str):
    """Get details for a specific town."""
    conn = get_db()
    town = conn.execute("SELECT * FROM amenities WHERE town = ?", (town_name,)).fetchone()
    conn.close()
    
    if not town:
        return {"error": "Town not found"}
    
    # Calculate scores for this town in context of all towns
    conn = get_db()
    all_towns = conn.execute("SELECT * FROM amenities").fetchall()
    conn.close()
    
    df = calculate_scores(all_towns)
    town_data = df[df['town'] == town_name].iloc[0].to_dict()
    
    return town_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
