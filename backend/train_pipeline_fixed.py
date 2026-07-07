import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import GradientBoostingClassifier
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
    print("[Engine] Booting Outcome-Only Pipeline...")

    # CHANGE: read the v3 file (generate_target_fixed.py's output), which
    # already has 'stakes_score' as a real numeric column. No more encode_stage()
    # here - that was reimplementing map_stakes() from generate_target.py in a
    # second place, and the two could silently drift out of sync. One source
    # of truth for stakes now.
    df = pd.read_csv('master_feature_matrix_v3.csv')

    # 1. DATA SEPARATION LAYER
    completed_matches = df[df['score1'].notna()].copy()
    upcoming_matches = df[df['score1'].isna()].copy()

    completed_matches['match_result'] = completed_matches.apply(engineer_match_result, axis=1)

    # 2. FEATURE SELECTION
    # CHANGE: 'stakes_score' replaces the old 'stage_num' - same idea (how much
    # is riding on this match), but computed once by generate_target.py instead
    # of twice. watchability_score / raw_watchability related columns are NOT
    # features here - they're not needed. Outcome classification doesn't use
    # watchability at all.
    dense_features = [
        'stadium_capacity', 't1_win_rate', 't1_avg_goals',
        't2_win_rate', 't2_avg_goals', 'rivalry_match_count', 'rivalry_avg_goals',
        'stakes_score'
    ]
    low_card_categoricals = ['group']
    all_features = dense_features + low_card_categoricals

    X_full = completed_matches[all_features]
    Y_classifier = completed_matches['match_result']
    X_upcoming = upcoming_matches[all_features]

    # 3. SINGLE STRATIFIED SPLIT
    # No second target to keep aligned anymore, so this is simpler than before
    # by construction - there's no way to reintroduce the old misalignment bug
    # because there's only one target now.
    X_train, X_test, y_train, y_test = train_test_split(
        X_full, Y_classifier, test_size=0.20, stratify=Y_classifier, random_state=42
    )

    print(f"[Telemetry] Dataset isolated. Train size: {len(X_train)} | Test size: {len(X_test)}")

    # 4. PREPROCESSING PIPELINE
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), dense_features),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), low_card_categoricals)
        ]
    )

    # 5. MODEL
    # min_samples_leaf=10 kept from the earlier fix - this is what stopped the
    # model from memorizing the 6-row "Round of 16" coincidence.
    clf_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', GradientBoostingClassifier(
            n_estimators=50, learning_rate=0.05, max_depth=2, min_samples_leaf=10, random_state=42))
    ])

    # 6. TRAINING
    print("[Engine] Training Outcome Classifier...")
    clf_pipeline.fit(X_train, y_train)

    # 7. METRICS
    print("\n============= HOLDOUT METRICS (single 80/20 split) =============")
    test_pred = clf_pipeline.predict(X_test)
    print(classification_report(y_test, test_pred, target_names=['Draw', 'Team 1 Win', 'Team 2 Win'], zero_division=0))

    print("\n============= 5-FOLD CROSS-VALIDATION (more reliable on ~94 rows) =============")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_acc = cross_val_score(clf_pipeline, X_full, Y_classifier, cv=skf, scoring='accuracy')
    print(f"Accuracy across folds: {np.round(cv_acc, 2)} -> mean {cv_acc.mean():.2f} +/- {cv_acc.std():.2f}")

    # 8. INFERENCE FOR UPCOMING MATCHES
    # CHANGE: watchability is no longer predicted. It's read straight from the
    # dataframe - generate_target_fixed.py already computed it correctly for
    # every upcoming match (including Quarter-final/Semi-final/Final rows the
    # classifier training data has never seen), with zero extrapolation risk.
    print("\n============= UPCOMING FIXTURE PREDICTIONS =============")
    pred_outcomes = clf_pipeline.predict(X_upcoming)
    pred_probabilities = clf_pipeline.predict_proba(X_upcoming)

    upcoming_matches = upcoming_matches.copy()
    upcoming_matches['pred_class'] = pred_outcomes

    class_mapping = {0: 'Draw', 1: 'Team 1 Win', 2: 'Team 2 Win'}

    for i, (idx, row) in enumerate(upcoming_matches.iterrows()):
        prob_draw = pred_probabilities[i][0] * 100
        prob_t1 = pred_probabilities[i][1] * 100
        prob_t2 = pred_probabilities[i][2] * 100

        print(f"\nFixture: {row['team1']} vs {row['team2']} ({row['round']})")
        print(f"-> Watchability Score (from formula, not ML): {row['watchability_score']} / 10.0")
        print(f"-> Predicted Direct Outcome                 : {class_mapping[row['pred_class']]}")
        print(f"-> Probability Matrix                       : {row['team1']}: {prob_t1:.1f}% | {row['team2']}: {prob_t2:.1f}% | Draw: {prob_draw:.1f}%")


if __name__ == "__main__":
    execute_outcome_pipeline()