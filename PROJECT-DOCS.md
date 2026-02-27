# AgeWell Finder - Complete Project Documentation

**Last Updated:** February 27, 2026  
**Status:** Working prototype with real data  
**Version:** 0.2.0

---

## Executive Summary

AgeWell Finder is a functional web application that ranks UK towns for older adults planning later-life relocations. It uses real OpenStreetMap data across 32 pilot towns, measuring healthcare access, green spaces, active living facilities, social infrastructure, and public transport.

**Current State:**
- ✅ Working data pipeline fetching real UK amenity data
- ✅ FastAPI backend calculating weighted scores
- ✅ Interactive Next.js frontend with adjustable priorities
- ✅ 32 towns with 6 metrics each (GPs, pharmacies, parks, leisure centres, gyms, community centres, bus stops)
- ✅ Professional UI with tooltips, sortable columns, modal popups, color-coded scores

**Commercial Model:** Free tool funded by ethical affiliate partnerships (removals, equity release, conveyancing)

---

## What We've Built

### 1. Data Pipeline (Python/OSMnx)

**Location:** `/agewell-finder/etl/`

**Scripts:**
- `fetch_all_towns.py` - Initial data fetch for pharmacies and parks
- `fetch_more_amenities.py` - Added leisure centres, gyms, community centres, bus stops
- `add_gps.py` - Added GP surgery data
- `create_rankings.py` - Calculates normalized scores

**Data Sources:**
- OpenStreetMap via OSMnx library
- Amenity tags: amenity=pharmacy, amenity=doctors, leisure=park, leisure=sports_centre, leisure=fitness_centre, amenity=community_centre, highway=bus_stop
- Search radius: 2km for most towns, 5km for smaller towns (Lewes, Totnes, Salisbury, Southport)

**Database:**
- SQLite: data/agewell.db
- Tables: places (32 towns), amenities (raw counts)
- Metrics stored: pharmacies, gp_surgeries, parks, leisure_centres, gyms, community_centres, bus_stops

### 2. Backend API (FastAPI)

**Location:** `/agewell-finder/api.py`

**Endpoints:**
- GET / - Health check
- GET /towns - Returns all towns with calculated scores
  - Query params: care_weight, green_weight, active_weight, social_weight, mobility_weight
  - Returns: JSON array of towns with scores
- GET /town/{town_name} - Returns details for specific town

**Scoring Algorithm:**
- Min-max normalization (0-100 scale)
- Care score = average of (normalized pharmacies + normalized GPs)
- Green score = normalized parks
- Active score = average of (normalized leisure centres + normalized gyms)
- Social score = normalized community centres
- Mobility score = normalized bus stops
- Overall score = weighted sum of 5 pillar scores (user-adjustable weights)

**Running:** 
```
cd ~/agewell-finder
source venv/bin/activate
python api.py
```
Runs on http://localhost:8000

### 3. Frontend (Next.js/React/TypeScript)

**Location:** `/agewell-finder/frontend/app/page.tsx`

**Features:**
- Priority Sliders: 5 adjustable weights (care, green, active, social, mobility)
- Reset Button: Restore default weights (1.0 each)
- Tooltips: Hover over info icons to see metric explanations
- Rankings Table: Shows all 32 towns with individual scores
- Sortable Columns: Click any column header to sort by that metric
- Color-Coded Scores: Green (70+), yellow (50-69), orange (<50)
- Modal Popup: Click any town to see detailed amenity counts
- Data Freshness: Header shows data source and update date

**Running:**
```
cd ~/agewell-finder/frontend
npm run dev
```
Runs on http://localhost:3000

---

## System Architecture
```
User Browser (localhost:3000)
    ↓
Next.js Frontend (TypeScript/React)
    ↓ (HTTP requests with weight parameters)
FastAPI Backend (Python)
    ↓ (SQL queries)
SQLite Database (agewell.db)
    ↑ (populated by)
ETL Scripts (Python/OSMnx)
    ↑ (data from)
OpenStreetMap API
```

---

## The 32 Pilot Towns

Bath, Bournemouth, Brighton and Hove, Cambridge, Canterbury, Cheltenham, Chichester, Colchester, Exeter, Guildford, Harrogate, Ipswich, Kendal, Lancaster, Lewes, Lichfield, Lincoln, Norwich, Oxford, Plymouth, Poole, Salisbury, Scarborough, Shrewsbury, Southport, St Albans, Taunton, Totnes, Truro, Winchester, Worthing, York

---

## Data Metrics & Current Limitations

### What We Measure

**Care Access:** GP surgeries + Pharmacies within 2km
**Green & Quiet:** Parks within 2km  
**Active Living:** Leisure centres + Gyms within 2km
**Social Fabric:** Community centres within 2km
**Mobility & Safety:** Bus stops within 2km

### What We Don't Measure (Yet)

- GP appointment availability or quality ratings
- Air quality or noise levels
- Actual green space area
- Bus frequency or rail access
- Crime rates or safety data
- Cost of living (house prices, council tax)
- Terrain steepness or walkability

---

## Technical Stack

**Backend:** Python 3.9, FastAPI, SQLAlchemy, OSMnx, pandas  
**Frontend:** Next.js 14, React 18, TypeScript, Tailwind CSS  
**Database:** SQLite (current), Postgres (future)  
**Infrastructure:** Mac Mini M4 (development), TBD (production)

---

## Development Workflow

**Three Terminals:**

1. **API Terminal:** `cd ~/agewell-finder && source venv/bin/activate && python api.py`
2. **Frontend Terminal:** `cd ~/agewell-finder/frontend && npm run dev`
3. **Tasks Terminal:** `cd ~/agewell-finder && source venv/bin/activate` (for scripts/editing)

**Making Changes:**
- Edit files using nano or text editor
- Restart relevant server (Ctrl+C then re-run)
- Refresh browser to see changes

---

## Completed Features (Days 1-2)

**Day 1:**
- Data pipeline with OSMnx
- SQLite database with 32 towns
- FastAPI backend with weighted scoring
- Next.js frontend with sliders and rankings
- Initial metrics: pharmacies, parks

**Day 2:**
- Added metrics: leisure centres, gyms, community centres, bus stops, GP surgeries
- Reset to defaults button
- Modal popup for town details
- Data freshness indicator
- Tooltip explanations
- Sortable table columns
- Color-coded scores

---

## Next Steps (Prioritized)

### Immediate
1. Set up GitHub repository (version control + backup)
2. Add About/Methodology page (build trust)
3. Get user feedback (5-10 people in target demographic)

### Short-term (1-2 weeks)
4. Deploy to production (Railway/Render)
5. Add more metrics based on feedback
6. Expand to 50-60 towns

### Medium-term (1 month)
7. Integrate first affiliate partnership
8. Add confidence ratings per town
9. Basic analytics

### Future
10. Premium downloadable reports (£9.99)
11. B2B dashboards (if demand exists)
12. Expand to 100+ towns

---

## Success Metrics

**v1 Launch:**
- 32 towns with 5+ metrics ✅
- Professional UI ✅
- Deployed with real URL ⏳
- 10+ people tested ⏳
- 3+ said "useful" ⏳

**6 Months:**
- 1,000+ monthly users
- 2+ affiliate partners
- £300+ monthly revenue

**12 Months:**
- 5,000+ monthly users  
- £500+ monthly revenue
- 100+ towns

---

## Commercial Strategy

**Revenue Model:** Free + Affiliates (primary), Premium Reports (secondary), B2B (opportunistic)

**Why This Works:**
- Users already planning £10k+ moves
- Affiliate revenue aligns with user intent
- Low barrier to entry (free tool)
- Can add premium features later

**Realistic Targets:**
- Year 1: £300-500/month
- Year 2: £500-1,500/month
- Sustainable solo project, not venture-scale

---

## Key Design Decisions

**Why OpenStreetMap?** Free, open, regularly updated, good UK coverage, no API limits

**Why 32 towns?** Large enough to be useful, small enough to validate quickly

**Why SQLite?** Simple, fast for <100 towns, easy to migrate later

**Why FastAPI + Next.js?** Modern stack, separates concerns, scales well, industry standard

**Why free + affiliates?** Lower barrier, aligns with user intent, more sustainable than ads

---

## Known Limitations

**Data Quality:**
- OSM completeness varies by location
- Smaller towns may be under-represented
- Quantity ≠ quality (10 bad gyms ≠ 10 good gyms)

**Metrics:**
- Missing key factors (cost, safety, quality)
- 2km radius may be too small for some towns
- No dynamic data (appointment availability, etc.)

**Product:**
- No user accounts or saved preferences
- No mobile app
- No email notifications

**These are acceptable for v1 - we'll iterate based on feedback**

---

## File Structure
```
agewell-finder/
├── api.py                 # FastAPI backend
├── data/
│   ├── agewell.db        # SQLite database
│   └── processed/        # CSV exports
├── etl/                   # Data scripts
│   ├── fetch_all_towns.py
│   ├── add_gps.py
│   └── create_rankings.py
├── frontend/
│   ├── app/
│   │   └── page.tsx      # Main UI code
│   ├── package.json
│   └── next.config.js
└── venv/                  # Python environment
```

---

## How To...

### Add a New Town
1. Add to TOWNS dict in all ETL scripts
2. Run each script to fetch data
3. Automatically appears in API/frontend

### Add a New Metric  
1. Create ETL script, add database column
2. Update API scoring calculation
3. Update frontend type, table, modal, tooltip

### Change Scoring
1. Edit api.py scoring logic
2. Restart API
3. Frontend gets new scores automatically

---

## Maintenance & Updates

**Data Refresh:** Re-run ETL scripts monthly to update amenity counts

**Code Changes:** Edit files, restart servers, test in browser

**Backups:** GitHub (to be set up) + local database file

**Monitoring:** Add analytics after deployment

---

## Resources

**Dependencies:**
- OpenStreetMap: https://www.openstreetmap.org
- OSMnx: https://github.com/gboeing/osmnx
- FastAPI: https://fastapi.tiangolo.com
- Next.js: https://nextjs.org

**Developer:** Adam Elston  
**Started:** February 24, 2026  
**Version:** 0.2.0  
**License:** TBD  
**Repository:** GitHub (pending)

---

**This documentation is a living document. Update as the project evolves.**
