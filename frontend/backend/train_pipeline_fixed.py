import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import classification_report

def engineer_match_result(row):
    """Encodes ground truth scores into 3 distinct classification buckets."""
    if row['score1'] > row['score2']:
        return 1  # Team 1 Win
    elif row['score2'] > row['score1']:
        return 2  # Team 2 Win
    else:
        return 0  # Draw

def execute_outcome_pipeline():
    print("[Engine] Booting Modern HistGradientBoosting Outcome Pipeline...")

    # 1. LOAD HISTORICAL TRAINING DATA (49k+ rows)
    print("[Engine] Ingesting point-in-time historical matrix...")
    history_df = pd.read_csv('data/historicized_training_matrix.csv')
    
    # Translate historical column names to pipeline schema
    history_df = history_df.rename(columns={
        'home_team': 'team1', 
        'away_team': 'team2', 
        'home_score': 'score1', 
        'away_score': 'score2'
    })

    # Historical completed matches are our core training rows
    completed_matches = history_df[history_df['score1'].notna()].copy()
    completed_matches['match_result'] = completed_matches.apply(engineer_match_result, axis=1)

    # 2. LOAD LIVE 2026 INFERENCE DATA
    print("[Engine] Ingesting live 2026 fixture matrix for upcoming predictions...")
    try:
        live_df = pd.read_csv('data/master_feature_matrix.csv')
        upcoming_matches = live_df[live_df['score1'].isna()].copy()
    except FileNotFoundError:
        print("WARNING: data/master_feature_matrix.csv not found. Running feature_pipeline.py first is recommended.")
        upcoming_matches = pd.DataFrame()

    # 3. FEATURE SELECTION LAYER
    # Focus strictly on pristine football performance metrics common to both sets.
    features = [
        't1_win_rate', 't1_avg_goals',
        't2_win_rate', 't2_avg_goals',
        'rivalry_match_count', 'rivalry_avg_goals'
    ]

    X_full = completed_matches[features]
    Y_full = completed_matches['match_result']

    # 4. STRATIFIED HOLDOUT SPLIT FOR VALIDATION
    X_train, X_test, y_train, y_test = train_test_split(
        X_full, Y_full, test_size=0.20, stratify=Y_full, random_state=42
    )

    print(f"[Telemetry] Dataset isolated. Total Training Rows: {len(X_full)}")
    print(f"[Telemetry] Split specs -> Train size: {len(X_train)} | Test size: {len(X_test)}")

    # 5. INITIALIZE HISTGRADIENTBOOSTING CLASSIFIER
    model = HistGradientBoostingClassifier(
        max_iter=100,
        learning_rate=0.05,
        max_depth=3,
        random_state=42
    )

    # 6. TRAINING
    print("[Engine] Training HistGradientBoosting Classifier...")
    model.fit(X_train, y_train)

    # 7. METRICS EVALUATION
    print("\n============= HOLDOUT METRICS (Single 80/20 Split) =============")
    test_pred = model.predict(X_test)
    print(classification_report(y_test, test_pred, target_names=['Draw', 'Team 1 Win', 'Team 2 Win'], zero_division=0))

    print("\n============= 5-FOLD CROSS-VALIDATION ON HISTORICAL DATA =============")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_acc = cross_val_score(model, X_full, Y_full, cv=skf, scoring='accuracy')
    print(f"Accuracy across folds: {np.round(cv_acc, 2)} -> mean {cv_acc.mean():.2f} +/- {cv_acc.std():.2f}")
    
    # 8. SERIALIZATION (Correctly scoped inside the function)
    joblib.dump(model, "data/match_model.joblib")
    print("\n[Model Serialization] SUCCESS: HistGradientBoostingClassifier saved to data/match_model.joblib")

    if not upcoming_matches.empty:
        print("\n============= UPCOMING 2026 FIXTURE PREDICTIONS =============")
        X_upcoming = upcoming_matches[features]
        pred_outcomes = model.predict(X_upcoming)
        pred_probabilities = model.predict_proba(X_upcoming)

        upcoming_matches['pred_class'] = pred_outcomes
        class_mapping = {0: 'Draw', 1: 'Team 1 Win', 2: 'Team 2 Win'}

        if 'watchability_score' not in upcoming_matches.columns:
            upcoming_matches['watchability_score'] = 5.0

        for i, (idx, row) in enumerate(upcoming_matches.iterrows()):
            prob_draw = pred_probabilities[i][0] * 100
            prob_t1 = pred_probabilities[i][1] * 100
            prob_t2 = pred_probabilities[i][2] * 100
            round_name = row.get('round', 'Group Stage')

            print(f"\nFixture: {row['team1']} vs {row['team2']} ({round_name})")
            print(f"-> Watchability Score (calculated score)   : {row['watchability_score']} / 10.0")
            print(f"-> Predicted Direct Outcome                 : {class_mapping[row['pred_class']]}")
            print(f"-> Probability Matrix                       : {row['team1']}: {prob_t1:.1f}% | {row['team2']}: {prob_t2:.1f}% | Draw: {prob_draw:.1f}%")
    else:
        print("\n[Inference] Skipping live fixture predictions because upcoming data is empty.")

if __name__ == "__main__":
    execute_outcome_pipeline()