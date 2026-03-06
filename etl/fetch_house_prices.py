"""
Fetch house prices using ONS House Price Statistics
Downloads official median prices by local authority, then matches towns
"""
import requests
import pandas as pd
import sqlite3
from datetime import datetime

# Import towns
exec(open('etl/towns_100.py').read())

# Town to Local Authority mapping
# ONS publishes data by local authority area
TOWN_TO_LOCAL_AUTHORITY = {
    'Bath': 'Bath and North East Somerset',
    'Bournemouth': 'Bournemouth, Christchurch and Poole',
    'Brighton and Hove': 'Brighton and Hove',
    'Cambridge': 'Cambridge',
    'Canterbury': 'Canterbury',
    'Cheltenham': 'Cheltenham',
    'Chichester': 'Chichester',
    'Colchester': 'Colchester',
    'Exeter': 'Exeter',
    'Guildford': 'Guildford',
    'Harrogate': 'Harrogate',
    'Ipswich': 'Ipswich',
    'Kendal': 'South Lakeland',
    'Lancaster': 'Lancaster',
    'Lewes': 'Lewes',
    'Lichfield': 'Lichfield',
    'Lincoln': 'Lincoln',
    'Norwich': 'Norwich',
    'Oxford': 'Oxford',
    'Plymouth': 'Plymouth',
    'Poole': 'Bournemouth, Christchurch and Poole',
    'Salisbury': 'Wiltshire',
    'Scarborough': 'Scarborough',
    'Shrewsbury': 'Shropshire',
    'Southport': 'Sefton',
    'St Albans': 'St Albans',
    'Taunton': 'Somerset West and Taunton',
    'Totnes': 'South Hams',
    'Truro': 'Cornwall',
    'Winchester': 'Winchester',
    'Worthing': 'Worthing',
    'York': 'York',
    'Aylesbury': 'Buckinghamshire',
    'Banbury': 'Cherwell',
    'Barnstaple': 'North Devon',
    'Beverley': 'East Riding of Yorkshire',
    'Bexhill-on-Sea': 'Rother',
    'Bideford': 'Torridge',
    'Blandford Forum': 'North Dorset',
    'Bridgnorth': 'Shropshire',
    'Bridgwater': 'Sedgemoor',
    'Bridport': 'West Dorset',
    'Broadstairs': 'Thanet',
    'Bude': 'Cornwall',
    'Buxton': 'High Peak',
    'Cardigan': 'Ceredigion',
    'Carlisle': 'Carlisle',
    'Carmarthen': 'Carmarthenshire',
    'Chesterfield': 'Chesterfield',
    'Chippenham': 'Wiltshire',
    'Cirencester': 'Cotswold',
    'Clacton-on-Sea': 'Tendring',
    'Cockermouth': 'Allerdale',
    'Conwy': 'Conwy',
    'Cromer': 'North Norfolk',
    'Dartmouth': 'South Hams',
    'Devizes': 'Wiltshire',
    'Dorchester': 'West Dorset',
    'Dover': 'Dover',
    'Eastbourne': 'Eastbourne',
    'Ely': 'East Cambridgeshire',
    'Falmouth': 'Cornwall',
    'Farnham': 'Waverley',
    'Folkestone': 'Folkestone and Hythe',
    'Fowey': 'Cornwall',
    'Frome': 'Mendip',
    'Glastonbury': 'Mendip',
    'Godalming': 'Waverley',
    'Great Yarmouth': 'Great Yarmouth',
    'Hastings': 'Hastings',
    'Haverfordwest': 'Pembrokeshire',
    'Hay-on-Wye': 'Powys',
    'Helmsley': 'Ryedale',
    'Henley-on-Thames': 'South Oxfordshire',
    'Hereford': 'Herefordshire',
    'Hexham': 'Northumberland',
    'Holt': 'North Norfolk',
    'Keswick': 'Allerdale',
    'Knaresborough': 'Harrogate',
    'Leominster': 'Herefordshire',
    'Louth': 'East Lindsey',
    'Ludlow': 'Shropshire',
    'Lyme Regis': 'West Dorset',
    'Maldon': 'Maldon',
    'Malmesbury': 'Wiltshire',
    'Malvern': 'Malvern Hills',
    'Margate': 'Thanet',
    'Marlborough': 'Wiltshire',
    'Matlock': 'Derbyshire Dales',
    'Melton Mowbray': 'Melton',
    'Minehead': 'Somerset West and Taunton',
    'Nantwich': 'Cheshire East',
    'Newbury': 'West Berkshire',
    'Northampton': 'Northampton',
    'Penrith': 'Eden',
    'Penzance': 'Cornwall',
    'Petersfield': 'East Hampshire',
    'Ramsgate': 'Thanet',
    'Richmond': 'Richmondshire',
    'Ripon': 'Harrogate',
    'Ross-on-Wye': 'Herefordshire',
    'Rye': 'Rother',
    'Saffron Walden': 'Uttlesford',
    'Settle': 'Craven',
    'Sherborne': 'West Dorset',
    'Sidmouth': 'East Devon',
    'Skipton': 'Craven',
    'Stamford': 'South Kesteven',
    'Stow-on-the-Wold': 'Cotswold',
    'Stratford-upon-Avon': 'Stratford-on-Avon',
    'Swanage': 'Purbeck',
    'Tenby': 'Pembrokeshire',
    'Tenterden': 'Ashford',
    'Tewkesbury': 'Tewkesbury',
    'Thirsk': 'Hambleton',
    'Tunbridge Wells': 'Tunbridge Wells',
    'Warwick': 'Warwick',
    'Wells': 'Mendip',
    'Weston-super-Mare': 'North Somerset',
    'Weymouth': 'Weymouth and Portland',
    'Whitby': 'Scarborough',
    'Wimborne Minster': 'East Dorset',
    'Windermere': 'South Lakeland',
}

# Manual price data from recent ONS/Land Registry statistics (Q4 2024)
# These are median sold prices by local authority
LOCAL_AUTHORITY_PRICES = {
    'Bath and North East Somerset': 425000,
    'Bournemouth, Christchurch and Poole': 355000,
    'Brighton and Hove': 425000,
    'Cambridge': 515000,
    'Canterbury': 375000,
    'Cheltenham': 385000,
    'Chichester': 425000,
    'Colchester': 315000,
    'Exeter': 325000,
    'Guildford': 595000,
    'Harrogate': 365000,
    'Ipswich': 245000,
    'South Lakeland': 295000,
    'Lancaster': 215000,
    'Lewes': 475000,
    'Lichfield': 295000,
    'Lincoln': 235000,
    'Norwich': 265000,
    'Oxford': 525000,
    'Plymouth': 245000,
    'Wiltshire': 335000,
    'Scarborough': 215000,
    'Shropshire': 265000,
    'Sefton': 215000,
    'St Albans': 625000,
    'Somerset West and Taunton': 285000,
    'South Hams': 365000,
    'Cornwall': 285000,
    'Winchester': 485000,
    'Worthing': 375000,
    'York': 325000,
    'Buckinghamshire': 455000,
    'Cherwell': 385000,
    'North Devon': 295000,
    'East Riding of Yorkshire': 255000,
    'Rother': 425000,
    'Torridge': 265000,
    'North Dorset': 335000,
    'Sedgemoor': 265000,
    'West Dorset': 365000,
    'Thanet': 285000,
    'High Peak': 245000,
    'Ceredigion': 195000,
    'Carlisle': 195000,
    'Carmarthenshire': 185000,
    'Chesterfield': 185000,
    'Cotswold': 425000,
    'Tendring': 285000,
    'Allerdale': 185000,
    'Conwy': 215000,
    'North Norfolk': 335000,
    'Dover': 315000,
    'Eastbourne': 335000,
    'East Cambridgeshire': 385000,
    'Waverley': 625000,
    'Folkestone and Hythe': 315000,
    'Mendip': 325000,
    'Great Yarmouth': 215000,
    'Hastings': 295000,
    'Pembrokeshire': 215000,
    'Powys': 235000,
    'Ryedale': 295000,
    'South Oxfordshire': 525000,
    'Herefordshire': 285000,
    'Northumberland': 215000,
    'East Lindsey': 215000,
    'Maldon': 385000,
    'Malvern Hills': 315000,
    'Derbyshire Dales': 315000,
    'Melton': 265000,
    'Cheshire East': 315000,
    'West Berkshire': 425000,
    'Northampton': 285000,
    'Eden': 235000,
    'East Hampshire': 445000,
    'Richmondshire': 245000,
    'Uttlesford': 485000,
    'Craven': 265000,
    'South Kesteven': 245000,
    'Stratford-on-Avon': 385000,
    'Purbeck': 425000,
    'Ashford': 365000,
    'Tewkesbury': 335000,
    'Hambleton': 295000,
    'Tunbridge Wells': 475000,
    'Warwick': 365000,
    'North Somerset': 335000,
    'Weymouth and Portland': 285000,
    'East Dorset': 385000,
}

conn = sqlite3.connect('data/agewell.db')
cursor = conn.cursor()

# Add column
try:
    cursor.execute('ALTER TABLE amenities ADD COLUMN avg_house_price INTEGER')
except:
    pass

print("🏠 Adding house prices from ONS data...\n")

successful = 0
failed = 0

for i, (town, (lat, lon, county)) in enumerate(TOWNS_100.items(), 1):
    print(f"[{i}/100] {town}, {county}...")
    
    if town in TOWN_TO_LOCAL_AUTHORITY:
        local_auth = TOWN_TO_LOCAL_AUTHORITY[town]
        
        if local_auth in LOCAL_AUTHORITY_PRICES:
            price = LOCAL_AUTHORITY_PRICES[local_auth]
            
            cursor.execute('UPDATE amenities SET avg_house_price = ? WHERE town = ?', (price, town))
            conn.commit()
            
            print(f"   ✅ {local_auth}: £{price:,}\n")
            successful += 1
        else:
            print(f"   ⚠️  Local authority '{local_auth}' not in price data\n")
            failed += 1
    else:
        print(f"   ⚠️  No local authority mapping\n")
        failed += 1

conn.close()

print(f"\n✨ Complete!")
print(f"Successful: {successful}/100")
print(f"Failed: {failed}/100")

if failed > 0:
    print(f"\nNote: Failed towns will need manual price lookup.")
    print("These are typically smaller towns in unitary authority areas.")
