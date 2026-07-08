import pandas as pd
import numpy as np

DATA_PATH = "data/results.csv"
def analyze_historical_powerhouses():
    print("Extracting baseline team performance metrics...")
        
    # Ingest the historical archive
    df = pd.read_csv(DATA_PATH)
    
    # Sanitize the dataset: Drop any rows where scores are missing
    df = df.dropna(subset=['home_score', 'away_score'])
    # Filter the dataset to only include Tier-1 FIFA World Cup matches
    df = df[df['tournament'] == 'FIFA World Cup']
    
    # Calculate match outcomes from the home team's perspective
    # 2 = Home Win, 1 = Draw, 0 = Away Win
    conditions = [
        (df['home_score'] > df['away_score']),
        (df['home_score'] < df['away_score'])
    ]
    choices = [2, 0]
    df['outcome'] = np.select(conditions, choices, default=1)
    
    # Tally up total home and away games
    home_games = df.groupby('home_team').size()
    away_games = df.groupby('away_team').size()
    total_games = home_games.add(away_games, fill_value=0)

    # Tally up total home and away wins
    home_wins = df[df['outcome'] == 2].groupby('home_team').size()
    away_wins = df[df['outcome'] == 0].groupby('away_team').size()
    total_wins = home_wins.add(away_wins, fill_value=0)

    # Calculate the win rate KPI and filter for established teams (>100 matches)
    win_rates = (total_wins / total_games * 100).round(2)
    established_teams = win_rates[total_games >= 30].sort_values(ascending=False)

    print("\n--- TOP 10 HISTORICAL POWERHOUSES (WIN RATE %) ---")
    print( established_teams.head(10))
    # Serialize the metrics to a JSON file for backend ingestion
    established_teams.to_json("data/team_form_baseline.json")
    print("Baseline metrics successfully exported to team_form_baseline.json")  
    # --- RIVALRY ANALYSIS ---
    # Create a unified matchup string (alphabetically sorted so A vs B is the same as B vs A)
    df['matchup'] = df.apply(lambda row: " vs ".join(sorted([str(row['home_team']), str(row['away_team'])])), axis=1)
    
    # Count how many times these specific matchups happened in the World Cup
    rivalry_counts = df.groupby('matchup').size()
    
    # Filter for intense rivalries (teams that have clashed 4 or more times)
    top_rivalries = rivalry_counts[rivalry_counts >= 4].sort_values(ascending=False)
    
    print("\n--- TIER-1 WORLD Cup RIVALRIES ---")
    print(top_rivalries.head(10))
    
    # Serialize the rivalries to JSON
    top_rivalries.to_json("data/rivalries_baseline.json")
    print("Rivalry metrics successfully exported to rivalries_baseline.json") 
if __name__ == "__main__":
    analyze_historical_powerhouses()