import requests
import json

def fetch_data():
    url = "https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Save locally so you have the "Source of Truth"
        with open('data/world_cup_data.json', 'w') as f:
            json.dump(data, f, indent=4)
        print("Success: Data pulled and saved to data/world_cup_data.json")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_data()