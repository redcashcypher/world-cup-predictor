import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np

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
        # FIX: previously fell into the else-bucket at 0.30, same as an
        # ordinary group-stage match. A 3rd-place playoff is a real knockout
        # fixture with something at stake - rate it above group stage but
        # below the semis that feed into it.
        return 0.60
    else:
        return 0.30  # Group Stage / Matchdays


def synthesize_watchability_v3(input_path='master_feature_matrix.csv',
                                output_path='master_feature_matrix_v3.csv'):
    print("[Phase 2 - Final V3] Loading Master Feature Matrix...")
    df = pd.read_csv(input_path)

    # Drop the old watchability score so we don't duplicate columns
    if 'watchability_score' in df.columns:
        df = df.drop(columns=['watchability_score'])

    print("[Phase 2 - Final V3] Engineering Match Stakes...")
    df['stakes_score'] = df['round'].apply(map_stakes)

    print("[Phase 2 - Final V3] Initializing Scalers...")
    scaler = MinMaxScaler()

    df['scaled_capacity'] = scaler.fit_transform(df[['stadium_capacity']])
    df['scaled_rivalry'] = scaler.fit_transform(df[['rivalry_match_count']])

    df['firepower'] = df['t1_avg_goals'] + df['t2_avg_goals']
    df['scaled_firepower'] = scaler.fit_transform(df[['firepower']])

    df['quality'] = df['t1_win_rate'] + df['t2_win_rate']
    df['scaled_quality'] = scaler.fit_transform(df[['quality']])

    print("[Phase 2 - Final V3] Applying New Weighted Heuristic...")
    df['raw_watchability'] = (
        (df['stakes_score'] * 0.25) +
        (df['scaled_quality'] * 0.25) +
        (df['scaled_firepower'] * 0.20) +
        (df['scaled_capacity'] * 0.20) +
        (df['scaled_rivalry'] * 0.10)
    )

    final_scaler = MinMaxScaler(feature_range=(1, 10))
    df['watchability_score'] = final_scaler.fit_transform(df[['raw_watchability']])
    df['watchability_score'] = df['watchability_score'].round(1)

    # Keep stakes_score in the output - your ML pipeline should use THIS
    # directly as a numeric feature instead of re-deriving stakes from a
    # 'round' one-hot/ordinal column the model may never have seen a
    # Quarter-final/Semi-final/Final example of (see conversation notes).
    df = df.drop(columns=[
        'scaled_capacity', 'scaled_rivalry',
        'firepower', 'scaled_firepower', 'quality', 'scaled_quality', 'raw_watchability'
    ])

    # FIX: previously wrote back to the SAME file this function reads from
    # (input_path == output_path == 'master_feature_matrix.csv'). That means
    # every re-run permanently overwrites your source data with no way back
    # if something's wrong. Now writes to a separate file by default; pass
    # matching input_path/output_path explicitly if you really want to
    # overwrite in place.
    df.to_csv(output_path, index=False)

    print(f"\n[Phase 2] STATUS: SUCCESS. Heuristic recalibrated with Round Stakes. Saved to {output_path}")

    print("\n--- Diagnostic: Top 5 Highest Rated Matches (V3) ---")
    top_matches = df.sort_values(by='watchability_score', ascending=False).head(5)
    print(top_matches[['round', 'team1', 'team2', 'watchability_score']])

    print("\n--- Sanity Check: England vs Norway ---")
    specifics = df[(df['team1'].isin(['England', 'Norway'])) & (df['team2'].isin(['England', 'Norway']))]
    print(specifics[['round', 'team1', 'team2', 'stakes_score', 'watchability_score']])

    return df


if __name__ == "__main__":
    synthesize_watchability_v3()