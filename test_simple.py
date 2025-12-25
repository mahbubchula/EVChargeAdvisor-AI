"""
Simple API Test
"""
import requests
from config.api_keys import OPENCHARGEMAP_API_KEY

print("🧪 Testing OpenChargeMap API...")
print("=" * 60)

url = "https://api.openchargemap.io/v3/poi/"
params = {
    "output": "json",
    "key": OPENCHARGEMAP_API_KEY,
    "countrycode": "US",
    "latitude": 37.7749,
    "longitude": -122.4194,
    "distance": 5,
    "maxresults": 3
}

print("📍 Getting charging stations in San Francisco...")

response = requests.get(url, params=params, timeout=10)

if response.status_code == 200:
    data = response.json()
    print(f"✅ SUCCESS! Got {len(data)} stations!")
    
    if len(data) > 0:
        station = data[0]
        name = station.get('AddressInfo', {}).get('Title', 'Unknown')
        print(f"\nFirst station: {name}")
        print("=" * 60)
        print("🎉 YOUR SETUP IS WORKING PERFECTLY!")
else:
    print(f"❌ Error: {response.status_code}")