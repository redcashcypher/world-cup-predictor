import duckdb

def setup_analytical_engine():
    # 1. Connect to (or create) a local file-based DuckDB database
    # This creates a single file that holds all our tables, just like SQLite but faster.
    print("[1/3] Booting DuckDB engine...")
    con = duckdb.connect('world_cup_predictor.duckdb')

    # 2. Ingest the clean CSV into a persistent table
    print("[2/3] Ingesting live matches into 'live_matches' table...")
    con.execute("""
        CREATE OR REPLACE TABLE live_matches AS
        SELECT * FROM read_csv_auto('matches_clean.csv')
    """)

    # 3. Run a diagnostic query to prove the SQL layer is functional
    print("[3/3] Running diagnostic SQL query...")
    result = con.execute("""
        SELECT date, team1, team2, stadium 
        FROM live_matches 
        WHERE team1 IS NOT NULL
        LIMIT 5
    """).fetchdf() # .fetchdf() hands it right back to us as a Pandas DataFrame!
    
    print("\n--- Analytics Engine Online. Top 5 Matches ---")
    print(result)

    # Always close the connection to prevent file locks
    con.close()
    print("\nStatus: Green. Database ready for historical data integration.")

if __name__ == "__main__":
    setup_analytical_engine()