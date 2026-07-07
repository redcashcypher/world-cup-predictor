import json
import pandas as pd

def process_world_cup_json():
    # Load the raw file we just created
    with open('world_cup_data.json', 'r') as f:
        data = json.load(f)
    
    # We will walk through the JSON 'rounds' and extract the matches
    # This is where we flatten the 'box' into a 'table'
    all_matches = []
    for round_data in data['rounds']:
        for match in round_data['matches']:
            all_matches.append({
                'date': match.get('date'),
                'team1': match['team1']['name'],
                'team2': match['team2']['name'],
                'score1': match['score']['ft'][0] if match.get('score') else None,
                'score2': match['score']['ft'][1] if match.get('score') else None,
                'group': round_data.get('name')
            })
            
    # Turn it into a table and save it
    df = pd.DataFrame(all_matches)
    df.to_csv('matches_clean.csv', index=False)
    print("Success: matches_clean.csv created. Ready for ML.")

if __name__ == "__main__":
    process_world_cup_json()