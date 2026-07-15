import duckdb
import pandas as pd
import requests

KAGGLE_RESULTS_PATH = 'data/results.csv'  # your Kaggle 1872-2017 file
OPENFOOTBALL_BRIDGE_YEARS = [2018, 2022]  # fills the gap Kaggle doesn't cover
LIVE_2026_TABLE = 'live_matches'  # your existing DuckDB table/view for 2026 fixtures


def fetch_openfootball_year(year: int) -> pd.DataFrame:
    """Pulls one World Cup year from openfootball/worldcup.json in the same
    schema as your Kaggle results.csv, so it can be UNIONed in directly."""
    url = f'https://raw.githubusercontent.com/openfootball/worldcup.json/master/{year}/worldcup.json'
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    matches = resp.json()['matches']

    rows = []
    for m in matches:
        ft = (m.get('score') or {}).get('ft')
        if not ft:
            continue
        rows.append({
            'date': m['date'],
            'home_team': m['team1'],
            'away_team': m['team2'],
            'home_score': ft[0],
            'away_score': ft[1],
        })
    return pd.DataFrame(rows)


def build_historicized_pipeline(con: duckdb.DuckDBPyConnection):
    print("[Historicize] Loading Kaggle historical results (1872-2017)...")
    con.execute(f"""
        CREATE OR REPLACE TABLE kaggle_results AS
        SELECT date::DATE AS date, home_team, away_team, home_score, away_score
        FROM read_csv_auto('{KAGGLE_RESULTS_PATH}', nullstr='NA')
        WHERE home_score IS NOT NULL AND away_score IS NOT NULL
    """)
    kaggle_count = con.execute("SELECT COUNT(*) FROM kaggle_results").fetchone()[0]
    print(f"  -> {kaggle_count} rows loaded")

    print(f"[Historicize] Bridging gap with openfootball years {OPENFOOTBALL_BRIDGE_YEARS}...")
    bridge_frames = [fetch_openfootball_year(y) for y in OPENFOOTBALL_BRIDGE_YEARS]
    bridge_df = pd.concat(bridge_frames, ignore_index=True)
    bridge_df['date'] = pd.to_datetime(bridge_df['date']).dt.date
    con.register('bridge_df', bridge_df)
    print(f"  -> {len(bridge_df)} rows loaded ({', '.join(str(y) for y in OPENFOOTBALL_BRIDGE_YEARS)})")

    print("[Historicize] Combining all sources into one historical ledger...")
    con.execute("""
        CREATE OR REPLACE TABLE historical_results AS
        SELECT date, home_team, away_team, home_score, away_score FROM kaggle_results
        UNION ALL
        SELECT date, home_team, away_team, home_score, away_score FROM bridge_df
    """)
    con.execute("ALTER TABLE historical_results ADD COLUMN match_id INTEGER")
    con.execute("UPDATE historical_results SET match_id = rowid")
    total = con.execute("SELECT COUNT(*) FROM historical_results").fetchone()[0]
    print(f"  -> {total} total historical matches (this replaces your old ~94-row training set)")

    print("[Historicize] Building team-perspective long table...")
    con.execute("""
        CREATE OR REPLACE VIEW team_perspective AS
        SELECT match_id, date, home_team AS team, away_team AS opponent,
               home_score AS goals_for, away_score AS goals_against,
               CASE WHEN home_score > away_score THEN 1 ELSE 0 END AS is_win
        FROM historical_results
        UNION ALL
        SELECT match_id, date, away_team AS team, home_team AS opponent,
               away_score AS goals_for, home_score AS goals_against,
               CASE WHEN away_score > home_score THEN 1 ELSE 0 END AS is_win
        FROM historical_results
    """)

    print("[Historicize] Computing AS-OF-DATE rolling team stats (no leakage)...")
    # RANGE (not ROWS) + INTERVAL 1 DAY PRECEDING: this frame is defined by the
    # DATE VALUE, not physical row position, so two matches on the same date
    # never see each other's result - verified with a synthetic same-day
    # doubleheader test before writing this against real data.
    con.execute("""
        CREATE OR REPLACE TABLE team_rolling_stats AS
        SELECT
            match_id, date, team,
            COUNT(*) OVER w AS matches_before,
            SUM(is_win) OVER w AS wins_before,
            SUM(goals_for) OVER w AS goals_before
        FROM team_perspective
        WINDOW w AS (
            PARTITION BY team ORDER BY date
            RANGE BETWEEN UNBOUNDED PRECEDING AND INTERVAL 1 DAY PRECEDING
        )
    """)

    print("[Historicize] Computing AS-OF-DATE head-to-head rivalry stats...")
    con.execute("""
        CREATE OR REPLACE VIEW pairwise_perspective AS
        SELECT match_id, date,
               CASE WHEN home_team < away_team THEN home_team ELSE away_team END AS team_min,
               CASE WHEN home_team < away_team THEN away_team ELSE home_team END AS team_max,
               home_score + away_score AS combined_goals
        FROM historical_results
    """)
    con.execute("""
        CREATE OR REPLACE TABLE rivalry_rolling_stats AS
        SELECT
            match_id, date, team_min, team_max,
            COUNT(*) OVER w AS h2h_matches_before,
            SUM(combined_goals) OVER w AS h2h_goals_before
        FROM pairwise_perspective
        WINDOW w AS (
            PARTITION BY team_min, team_max ORDER BY date
            RANGE BETWEEN UNBOUNDED PRECEDING AND INTERVAL 1 DAY PRECEDING
        )
    """)

    print("[Historicize] Assembling final as-of-date training matrix...")
    training_matrix = con.execute("""
        SELECT
            m.match_id, m.date, m.home_team, m.away_team, m.home_score, m.away_score,
            t1.matches_before AS t1_matches_played,
            (t1.wins_before * 1.0 / NULLIF(t1.matches_before, 0)) AS t1_win_rate,
            (t1.goals_before * 1.0 / NULLIF(t1.matches_before, 0)) AS t1_avg_goals,
            t2.matches_before AS t2_matches_played,
            (t2.wins_before * 1.0 / NULLIF(t2.matches_before, 0)) AS t2_win_rate,
            (t2.goals_before * 1.0 / NULLIF(t2.matches_before, 0)) AS t2_avg_goals,
            COALESCE(r.h2h_matches_before, 0) AS rivalry_match_count,
            (r.h2h_goals_before * 1.0 / NULLIF(r.h2h_matches_before, 0)) AS rivalry_avg_goals
        FROM historical_results m
        LEFT JOIN team_rolling_stats t1 ON m.match_id = t1.match_id AND m.home_team = t1.team
        LEFT JOIN team_rolling_stats t2 ON m.match_id = t2.match_id AND m.away_team = t2.team
        LEFT JOIN rivalry_rolling_stats r ON m.match_id = r.match_id
        ORDER BY m.date
    """).fetchdf()

    return training_matrix


if __name__ == '__main__':
    con = duckdb.connect()
    matrix = build_historicized_pipeline(con)

    print(f"\n[Historicize] STATUS: SUCCESS. {len(matrix)} rows with as-of-date features.")
    print(f"[Historicize] Rows with a team's FIRST-EVER match (no prior history, will be NaN and should be dropped for training):")
    first_matches = matrix['t1_win_rate'].isna().sum() + matrix['t2_win_rate'].isna().sum()
    print(f"  -> {first_matches} team-sides with zero prior matches")

    matrix.to_csv('historicized_training_matrix.csv', index=False)
    print("\nSaved to historicized_training_matrix.csv")
    print(matrix.tail(10)[['date', 'home_team', 'away_team', 't1_win_rate', 't2_win_rate', 'rivalry_match_count']])
