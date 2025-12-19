from pathlib import Path

# Paths
# BASE_DIR is now backend/ml_engine
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"

# Files
RAW_DATA_FILE = DATA_DIR / "final_sau_missingvalues.csv"
# X_TRAIN_FILE is not needed for inference, only for training preprocessor
X_TRAIN_FILE = DATA_DIR / "X_train.csv"

# Columns
TARGET_COL = "log1p_yield_ton_per_ha"

# Feature Engineering Config
WINDOWS = [1, 2, 3, 4, 5, 6, 7]
GROUP_KEYS = ["province_name", "commodity", "season"]

# Preprocessing Config (notebook 02_scaling_encoding.ipynb)
PREPROCESSOR_FILE = MODELS_DIR / "preprocessor.joblib"

# Ensemble Weights
DEFAULT_WEIGHTS = {
    'xgb': 0.0000,
    'lgb': 0.5076,
    'cat': 0.0000,
    'rf': 0.4924
}