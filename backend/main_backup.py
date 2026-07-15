from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import pandas as pd
import joblib
import os

app = FastAPI(
    title="World Cup Watch Party Predictor API",
    description="Serving live tournament schedules, live ML predictions, and Golden Boot standings.",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "data/world_cup.db"
MODEL_PATH = "data/match_model.joblib" # Adjust path to your trained model file
MODEL = None

@app.on_event("startup")
def startup_load_model():
    """Loads the trained ML model into server memory once upon initialization."""
    global MODEL
    if os.path.exists(MODEL_PATH):
        try:
            MODEL = joblib.load(MODEL_PATH)
            print("[Server] SUCCESS: Machine Learning Model loaded into runtime.")
        except Exception as e:
            print(f"[Server] WARNING: Could not load model: {e}")
    else:
        print("[Server] WARNING: data/match_model.joblib not found. Live predictions will be disabled.")

def get_db_connection():
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=503, detail="Database offline.")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/api/v1/fixtures")
def get_raw_schedule():
    """Serves the complete 104-match raw tournament calendar/schedule."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM raw_schedule ORDER BY date ASC")
        matches = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return {"status": "success", "count": len(matches), "data": matches}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/predictions")
def get_ml_predictions():
    """Serves the 98 resolved fixtures complete with calculated watchability scores and live ML probability vectors."""
    if MODEL is None:
        raise HTTPException(status_code=503, detail="ML inference engine is offline. Model file missing.")
        
    try:
        conn = get_db_connection()
        df = pd.read_sql_query("SELECT * FROM predicted_fixtures", conn)
        conn.close()

        if df.empty:
            return {"status": "success", "count": 0, "data": []}

        # FIX 1: Aligned feature columns exactly with the training matrix (6 features)
        feature_cols = [
            't1_win_rate', 
            't1_avg_goals', 
            't2_win_rate', 
            't2_avg_goals', 
            'rivalry_match_count', 
            'rivalry_avg_goals'
        ] 
        
        X = df[feature_cols]
        probabilities = MODEL.predict_proba(X) 
        
        results = []
        # FIX 2: Bulletproof iteration using enumerate to decouple from the Pandas index
        for i, (_, row) in enumerate(df.iterrows()):
            results.append({
                "date": row.get("date"),
                "team1": row.get("team1"),
                "team2": row.get("team2"),
                "watchability_score": row.get("watchability_score", 5.0),
                "probabilities": {
                    # FIX 3: Corrected Scikit-Learn class label mapping
                    # Class 0 = Draw, Class 1 = Team 1 Win, Class 2 = Team 2 Win
                    "team1_win": round(probabilities[i][1] * 100, 2),
                    "draw": round(probabilities[i][0] * 100, 2),
                    "team2_win": round(probabilities[i][2] * 100, 2)
                }
            })

        return {"status": "success", "count": len(results), "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/golden-boot")
def get_golden_boot():
    """Serves the deterministic tournament standings from player_goals."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT rank, player, team, goals, penalties FROM player_goals ORDER BY goals DESC, player ASC LIMIT 10")
        leaderboard = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return {"status": "success", "disclaimer": "Ties broken alphabetically.", "data": leaderboard}
    except sqlite3.OperationalError:
        raise HTTPException(status_code=503, detail="Golden Boot standings not initialized.")