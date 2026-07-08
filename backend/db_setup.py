import sqlite3
import pandas as pd
import os

def load_all_assets_to_db():
    print("[Database] Beginning unified database synchronization...")
    
    clean_matches_path = 'data/matches_clean.csv'
    feature_matrix_path = 'data/master_feature_matrix.csv'
    db_path = 'data/world_cup.db'

    if not os.path.exists(clean_matches_path) or not os.path.exists(feature_matrix_path):
        print("CRITICAL ERROR: Data matrices missing. Please check your pipeline execution order.")
        return

    conn = sqlite3.connect(db_path)
    
    # Table 1: Raw Schedule (104 rows for the calendar/fixtures view)
    df_raw = pd.read_csv(clean_matches_path)
    df_raw.to_sql('raw_schedule', conn, if_exists='replace', index=False)
    print(f"[Database] SUCCESS: Synchronized {len(df_raw)} records to 'raw_schedule' table.")

    # Table 2: ML Features & Watchability Matrix (98 resolved rows)
    df_features = pd.read_csv(feature_matrix_path)
    df_features.to_sql('predicted_fixtures', conn, if_exists='replace', index=False)
    print(f"[Database] SUCCESS: Synchronized {len(df_features)} records to 'predicted_fixtures' table.")

    conn.close()

if __name__ == "__main__":
    load_all_assets_to_db()