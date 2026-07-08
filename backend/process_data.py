import json
import pandas as pd

def process_world_cup_json():
    print("[Ingestion Engine] Parsing raw World Cup JSON payload...")
    
    # Load the raw file from the new data directory
    with open('data/world_cup_data.json', 'r') as f:
        data = json.load(f)
    
    all_matches = []
    
    # The OpenFootball schema uses a flat 'matches' array
    matches = data.get('matches', [])
    
    if not matches:
        print("CRITICAL ERROR: No 'matches' array found in JSON payload.")
        return

    for match in matches:
        # OpenFootball schema can be inconsistent: sometimes teams are nested dicts, sometimes flat strings.
        # This handles both cases gracefully.
        t1 = match.get('team1')
        t2 = match.get('team2')
        team1_name = t1.get('name') if isinstance(t1, dict) else t1
        team2_name = t2.get('name') if isinstance(t2, dict) else t2
        
        # Safely extract full-time (ft) scores if the match has been played
        score_data = match.get('score')
        ft_score = score_data.get('ft') if score_data else None
        
        all_matches.append({
            'date': match.get('date'),
            'team1': team1_name,
            'team2': team2_name,
            'score1': ft_score[0] if ft_score and len(ft_score) > 0 else None,
            'score2': ft_score[1] if ft_score and len(ft_score) > 1 else None,
            'group': match.get('round') or match.get('group', 'Unknown Phase') 
        })
            
    # Serialize to CSV
    df = pd.DataFrame(all_matches)
    df.to_csv('data/matches_clean.csv', index=False)
    print(f"[Ingestion Engine] SUCCESS: data/matches_clean.csv created with {len(df)} rows. Matrix is primed.")

if __name__ == "__main__":
    process_world_cup_json()