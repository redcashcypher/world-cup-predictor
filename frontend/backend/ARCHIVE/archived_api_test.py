import requests
import json
import os
from dotenv import load_dotenv

# Initialize the secure environment variables
load_dotenv()

# Extract the key from the hidden vault
API_KEY = os.getenv("API_FOOTBALL_KEY")

def fetch_2026_fixtures():
    print("Requesting live 2026 World Cup fixtures from API-Football...")
    
    # The dedicated fixtures endpoint
    url = "https://v3.football.api-sports.io/fixtures"
    
    # League 1 = FIFA World Cup, Season = 2026
    querystring = {"league": "1", "season": "2026"}
    
    headers = {
        'x-apisports-key': API_KEY
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()
        
        # Cache the payload locally to protect our API quota
        with open("live_fixtures_2026.json", "w") as f:
            json.dump(data, f, indent=4)
            
        print("Data ingestion complete!")
        print(f"Total matches retrieved and secured in live_fixtures_2026.json: {data['results']}")
        
    except Exception as e:
        print(f"Data ingestion failed: {e}")

if __name__ == "__main__":
    fetch_2026_fixtures()