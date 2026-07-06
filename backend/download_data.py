import os
from dotenv import load_dotenv

# 1. Force the environment load
load_dotenv()

# 2. Hard check to ensure the token is registered in the OS
if "KAGGLE_API_TOKEN" not in os.environ:
    print("ERROR: Token missing. Verify your file isn't accidentally named '.env.txt'")
    exit()

# 3. Initialize Kaggle ONLY AFTER variables are locked
import kaggle

print("Authenticating and initializing download...")
kaggle.api.dataset_download_files('martj42/international-football-results-from-1872-to-2017', path='.', unzip=True)
print("Ingestion complete. The dataset should be in your directory.")