World Cup Watch Party Predictor 2026
A production-grade predictive engine for the 2026 World Cup, utilizing an automated ETL pipeline, machine learning, and real-time tournament tracking.

Summary:
1. python download_data.py       # pulls Kaggle results.csv, goalscorers.xlsx, etc.
2. python ingest_data.py         # pulls live 2026 fixtures from openfootball
3. python process_data.py        # → data/matches_clean.csv
4. python db_setup.py            # → world_cup_predictor.duckdb
5. python feature_pipeline.py    # → data/master_feature_matrix.csv
6. python historicize_features.py # → data/historicized_training_matrix.csv
7. python generate_target.py     # adds watchability_score
8. python train_pipeline_fixed.py

Architecture
Ingestion: Automated extraction of historical results and live 2026 fixtures.

Processing: Dimensional flattening of complex nested JSON structures into feature-rich matrices.

Analytics: A proprietary heuristic weighting system for tournament "watchability."

ML: A high-performance HistGradientBoostingClassifier trained on 49,629 historical match vectors.

Serving: A FastAPI-based backend serving live Golden Boot standings and match predictions.

Setup Requirements
1. Environment Configuration
Ensure you have Python 3.10+ installed. Create and activate a virtual environment:

Bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
2. Dataset Initialization
The /data directory is excluded from version control. You must generate it locally:

Download History: Run python download_data.py to fetch historical results.

Ingest Fixtures: Run python ingest_data.py to pull the latest 2026 tournament JSON.

Pipeline Execution:

python feature_pipeline.py (Builds the feature matrix)

python generate_target.py (Calculates watchability heuristics)

python golden_boot.py (Syncs the live Golden Boot leaderboard)

Data Disclaimer
Golden Boot: Ties are broken alphabetically based on the feed's limitations.

Predictions: ML outcomes are probabilistic; they reflect statistical history, not future certainty.

Why this is the "Lead Engineer" approach:
Dependency Clarity: You clearly document that the data/ folder is excluded, so no one accidentally commits 50k rows to Git.

Standardized Workflow: You provide a "How-to" sequence that documents the ETL process, ensuring the next person who runs your code won't run into a FileNotFound error.

Versioning: You define the scope of the project so anyone reading the repo knows exactly what you are trying to predict.
