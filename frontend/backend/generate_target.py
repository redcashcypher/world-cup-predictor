import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def map_stakes(round_str):
    round_str = str(round_str).lower()
    if 'final' in round_str and 'quarter' not in round_str and 'semi' not in round_str and 'third' not in round_str:
        return 1.0
    elif 'semi' in round_str:
        return 0.95
    elif 'quarter' in round_str:
        return 0.85
    elif 'round of 16' in round_str:
        return 0.70
    elif 'round of 32' in round_str:
        return 0.55
    elif 'third' in round_str:
        return 0.60
    else:
        return 0.30  # Group Stage / Matchdays

def synthesize_watchability_v3(input_path='data/master_feature_matrix.csv',
                                output_path='data/master_feature_matrix.csv'):
    print("[Phase 2] Loading Live Inference Matrix...")
    df = pd.read_csv(input_path)

    # Drop the old watchability score so we don't duplicate columns
    if 'watchability_score' in df.columns:
        df = df.drop(columns=['watchability_score'])

    print("[Phase 2] Engineering Match Stakes...")
    df['stakes_score'] = df['round'].apply(map_stakes)

    print("[Phase 2] Initializing Scalers...")
    scaler = MinMaxScaler()

    # Safely fill NaNs just for the heuristic calculation to prevent scaler crashes
    df['stadium_capacity'] = df['stadium_capacity'].fillna(50000)
    df['rivalry_match_count'] = df['rivalry_match_count'].fillna(0)
    df['t1_avg_goals'] = df['t1_avg_goals'].fillna(0)
    df['t2_avg_goals'] = df['t2_avg_goals'].fillna(0)
    df['t1_win_rate'] = df['t1_win_rate'].fillna(0)
    df['t2_win_rate'] = df['t2_win_rate'].fillna(0)

    df['scaled_capacity'] = scaler.fit_transform(df[['stadium_capacity']])
    df['scaled_rivalry'] = scaler.fit_transform(df[['rivalry_match_count']])

    df['firepower'] = df['t1_avg_goals'] + df['t2_avg_goals']
    df['scaled_firepower'] = scaler.fit_transform(df[['firepower']])

    df['quality'] = df['t1_win_rate'] + df['t2_win_rate']
    df['scaled_quality'] = scaler.fit_transform(df[['quality']])

    print("[Phase 2] Applying Recalibrated Weighted Heuristic...")
    df['raw_watchability'] = (
        (df['stakes_score'] * 0.35) +      # Up from 0.25: Stakes are the ultimate driver
        (df['scaled_quality'] * 0.25) +    # Unchanged: Elite matchups matter
        (df['scaled_rivalry'] * 0.20) +    # Up from 0.10: Historic bad blood is box office
        (df['scaled_firepower'] * 0.15) +  # Down from 0.20: Goals are great, but stakes are better
        (df['scaled_capacity'] * 0.05)     # Down from 0.20: A stadium is just a building
    )

    final_scaler = MinMaxScaler(feature_range=(1.0, 10.0))
    df['watchability_score'] = final_scaler.fit_transform(df[['raw_watchability']])
    df['watchability_score'] = df['watchability_score'].round(1)

    # Clean up intermediate calculation columns
    df = df.drop(columns=[
        'scaled_capacity', 'scaled_rivalry',
        'firepower', 'scaled_firepower', 'quality', 'scaled_quality', 'raw_watchability'
    ])

    # Overwrite the matrix in-place so the training script picks it up automatically
    df.to_csv(output_path, index=False)

    print(f"\n[Phase 2] STATUS: SUCCESS. Heuristic recalibrated. Saved to {output_path}")
    
    print("\n--- Diagnostic: Top 5 Highest Rated Matches (V3) ---")
    top_matches = df.sort_values(by='watchability_score', ascending=False).head(5)
    print(top_matches[['round', 'team1', 'team2', 'stakes_score', 'watchability_score']])

if __name__ == "__main__":
    synthesize_watchability_v3()