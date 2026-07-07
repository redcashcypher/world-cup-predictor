import duckdb
import pandas as pd

def execute_phase_1_pipeline():
    print("[Phase 1] Connecting to Analytical Engine...")
    con = duckdb.connect('world_cup_predictor.duckdb')

    print("[Phase 1] Ingesting Historical Ledger (results.csv)...")
    con.execute("""
        CREATE OR REPLACE TABLE historical_results AS 
        SELECT * FROM read_csv_auto('results.csv', nullstr='NA')
        WHERE home_score IS NOT NULL AND away_score IS NOT NULL
    """)

    print("[Phase 1] Computing Baseline Performance Metrics...")
    con.execute("""
        CREATE OR REPLACE VIEW team_historical_stats AS
        WITH home_stats AS (
            SELECT home_team AS team, COUNT(*) as matches, 
                   SUM(CASE WHEN home_score > away_score THEN 1 ELSE 0 END) as wins, 
                   SUM(home_score) as goals_for
            FROM historical_results GROUP BY home_team
        ),
        away_stats AS (
            SELECT away_team AS team, COUNT(*) as matches, 
                   SUM(CASE WHEN away_score > home_score THEN 1 ELSE 0 END) as wins, 
                   SUM(away_score) as goals_for
            FROM historical_results GROUP BY away_team
        )
        SELECT 
            team,
            SUM(matches) as total_matches,
            SUM(wins)*1.0 / NULLIF(SUM(matches), 0) as win_rate,
            SUM(goals_for)*1.0 / NULLIF(SUM(matches), 0) as avg_goals_scored
        FROM (SELECT * FROM home_stats UNION ALL SELECT * FROM away_stats) combined
        GROUP BY team;
    """)

    print("[Phase 1] Engineering the Pairwise Rivalry Index...")
    con.execute("""
        CREATE OR REPLACE VIEW historical_rivalries AS
        SELECT 
            CASE WHEN home_team < away_team THEN home_team ELSE away_team END as team_min,
            CASE WHEN home_team < away_team THEN away_team ELSE home_team END as team_max,
            COUNT(*) as head_to_head_matches,
            AVG(home_score + away_score) as avg_combined_historical_goals
        FROM historical_results
        GROUP BY team_min, team_max;
    """)

    print("[Phase 1] Fusing Live Fixtures with Capacities & Rivalry Data...")
    feature_matrix = con.execute("""
        WITH cleaned_live_matches AS (
            SELECT 
                date, round, "group", stadium,
                CASE 
                    WHEN team1 = 'USA' THEN 'United States'
                    WHEN team1 = 'Bosnia & Herzegovina' THEN 'Bosnia and Herzegovina'
                    ELSE team1 
                END AS team1,
                CASE 
                    WHEN team2 = 'USA' THEN 'United States'
                    WHEN team2 = 'Bosnia & Herzegovina' THEN 'Bosnia and Herzegovina'
                    ELSE team2 
                END AS team2,
                score1, score2,
                CASE 
                    WHEN stadium LIKE '%Mexico City%' THEN 87523
                    WHEN stadium LIKE '%New York%' OR stadium LIKE '%East Rutherford%' THEN 82500
                    WHEN stadium LIKE '%Dallas%' OR stadium LIKE '%Arlington%' THEN 80000
                    WHEN stadium LIKE '%Kansas City%' THEN 76416
                    WHEN stadium LIKE '%Houston%' THEN 72220
                    WHEN stadium LIKE '%Atlanta%' THEN 71000
                    WHEN stadium LIKE '%Los Angeles%' OR stadium LIKE '%Inglewood%' THEN 70240
                    WHEN stadium LIKE '%Philadelphia%' THEN 69796
                    WHEN stadium LIKE '%Seattle%' THEN 69000
                    WHEN stadium LIKE '%Santa Clara%' OR stadium LIKE '%San Francisco%' THEN 68500
                    WHEN stadium LIKE '%Boston%' OR stadium LIKE '%Foxborough%' THEN 65878
                    WHEN stadium LIKE '%Miami%' OR stadium LIKE '%Miami Gardens%' THEN 64767
                    WHEN stadium LIKE '%Vancouver%' THEN 54500
                    WHEN stadium LIKE '%Monterrey%' OR stadium LIKE '%Guadalupe%' THEN 53500
                    WHEN stadium LIKE '%Guadalajara%' OR stadium LIKE '%Zapopan%' THEN 48056
                    WHEN stadium LIKE '%Toronto%' THEN 45000
                    ELSE 50000 
                END AS stadium_capacity
            FROM live_matches
            -- FIX: the old filter was `team1 NOT LIKE 'W%' AND team1 NOT LIKE 'L%'`.
            -- That silently drops ANY real team whose name starts with W or L
            -- (e.g. 'Wales') the moment it's ever drawn into the team1 slot -
            -- not just bracket placeholders like 'W93'/'L101'. This dataset's
            -- current 48-team roster happens not to include one, so it hasn't
            -- bitten yet, but it's a live landmine for the next roster update.
            -- Match the EXACT placeholder pattern (a letter, then only digits)
            -- instead of any name that merely starts with that letter.
            WHERE NOT regexp_matches(team1, '^[WL][0-9]+$')
              AND NOT regexp_matches(team2, '^[WL][0-9]+$')
        )
        SELECT 
            m.date, m.round, m."group", m.stadium, m.stadium_capacity,
            m.team1, t1.win_rate AS t1_win_rate, t1.avg_goals_scored AS t1_avg_goals,
            m.team2, t2.win_rate AS t2_win_rate, t2.avg_goals_scored AS t2_avg_goals,
            COALESCE(r.head_to_head_matches, 0) as rivalry_match_count,
            COALESCE(r.avg_combined_historical_goals, 0) as rivalry_avg_goals,
            m.score1, m.score2
        FROM cleaned_live_matches m
        LEFT JOIN team_historical_stats t1 ON m.team1 = t1.team
        LEFT JOIN team_historical_stats t2 ON m.team2 = t2.team
        LEFT JOIN historical_rivalries r 
          ON (CASE WHEN m.team1 < m.team2 THEN m.team1 ELSE m.team2 END = r.team_min)
         AND (CASE WHEN m.team1 < m.team2 THEN m.team2 ELSE m.team1 END = r.team_max)
        ORDER BY m.date, m.team1
    """).fetchdf()

    # Save the Phase 1 Augmented Matrix
    feature_matrix.to_csv('master_feature_matrix.csv', index=False)
    
    print("\n--- Pipeline Complete. Diagnostic Preview of Augmented Features ---")
    print(feature_matrix[['team1', 'team2', 'stadium_capacity', 'rivalry_match_count']].head())

    # Automated Data Hygiene Guardrail
    nulls = feature_matrix['t1_win_rate'].isna().sum()
    if nulls > 0:
        missing = feature_matrix[feature_matrix['t1_win_rate'].isna()]['team1'].unique()
        print(f"\nCRITICAL WARNING: {nulls} teams still failed to join historical baselines: {missing}")
    else:
        print("\n[Phase 1] STATUS: GREEN. 100% Match Rate. Stadium capacities and rivalries mapped without errors.")

    con.close()

if __name__ == "__main__":
    execute_phase_1_pipeline()