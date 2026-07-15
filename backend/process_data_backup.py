import json
import pandas as pd
import os

def process_raw_fixtures(input_path='data/world_cup_data.json', output_path='data/matches_clean.csv'):
    print("[ETL] Booting dimensional flattening engine...")
    
    if not os.path.exists(input_path):
        print(f"CRITICAL ERROR: {input_path} not found. Please run ingest_data.py first.")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    matches = data.get('matches', [])
    records = []
    
    for m in matches:
        # OpenFootball feeds sometimes nest names inside objects
        team1 = m.get('team1', {}).get('name') if isinstance(m.get('team1'), dict) else m.get('team1')
        team2 = m.get('team2', {}).get('name') if isinstance(m.get('team2'), dict) else m.get('team2')
        stadium = m.get('stadium', {}).get('name') if isinstance(m.get('stadium'), dict) else m.get('stadium')
        
        records.append({
            'date': m.get('date'),
            'team1': team1,
            'team2': team2,
            'score1': m.get('score1'),
            'score2': m.get('score2'),
            'round': m.get('round'),
            'group': m.get('group'),
            'stadium': stadium
        })
    
    df = pd.DataFrame(records)
    df.to_csv(output_path, index=False)
    print(f"[ETL] SUCCESS: Flattened {len(df)} matches. Schema locked and saved to {output_path}")
    return df

if __name__ == "__main__":
    process_raw_fixtures()