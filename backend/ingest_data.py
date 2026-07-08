import requests
import json

def ingest_world_cup_json():
    url = "https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json"
    
    print("[1/2] Fetching live data from OpenFootball...")
    try:
        response = requests.get(url)
        response.raise_for_status() # This will crash if the website is down
        data = response.json()
        
        # Save as our 'master copy' inside the data folder
        with open('data/world_cup_data.json', 'w') as f:
            json.dump(data, f, indent=4)
        print("Success: data/world_cup_data.json created.")
        
    except Exception as e:
        print(f"Failed to fetch data: {e}")

if __name__ == "__main__":
    ingest_world_cup_json()