import joblib
import pandas as pd
from catboost import CatBoostRegressor
from . import config

def load_models():
    models = {}
    
    # Load XGBoost
    try:
        xgb_path = config.MODELS_DIR / "xgb_yield_model.pkl"
        models['xgb'] = joblib.load(xgb_path)
        print(f"Loaded XGBoost model.")
    except Exception as e:
        print(f"Error loading XGBoost: {e}")

    # Load LightGBM
    try:
        lgb_path = config.MODELS_DIR / "lgb_yield_model.pkl"
        models['lgb'] = joblib.load(lgb_path)
        print(f"Loaded LightGBM model.")
    except Exception as e:
        print(f"Error loading LightGBM: {e}")

    # Load CatBoost
    try:
        # Find latest .cbm file
        cat_files = list(config.MODELS_DIR.glob("*.cbm"))
        if cat_files:
            latest_cat = max(cat_files, key=lambda p: p.stat().st_mtime)
            models['cat'] = CatBoostRegressor()
            models['cat'].load_model(str(latest_cat))
            print(f"Loaded CatBoost model.")
        else:
            print("Warning: CatBoost model not found")
    except Exception as e:
        print(f"Error loading CatBoost: {e}")

    # Load Random Forest
    try:
        # Look for random_forest*.pkl or rf*.pkl
        rf_files = list(config.MODELS_DIR.glob("*random_forest*.pkl"))
        if not rf_files:
            rf_files = list(config.MODELS_DIR.glob("rf_*.pkl"))
            
        if rf_files:
            latest_rf = max(rf_files, key=lambda p: p.stat().st_mtime)
            models['rf'] = joblib.load(latest_rf)
            print(f"Loaded Random Forest model.")
        else:
            print("Warning: Random Forest model not found")
    except Exception as e:
        print(f"Error loading Random Forest: {e}")
        
    return models

def get_underscore_data(df):
    """Replace spaces with underscores in column names (for LightGBM)."""
    df_new = df.copy()
    new_cols = []
    for col in df_new.columns:
        if col.startswith("province_name_"):
            new_cols.append(col.replace(" ", "_"))
        else:
            new_cols.append(col)
    df_new.columns = new_cols
    return df_new

def predict_single_model(model, X_data, model_type):
    """Generate predictions for a single model."""
    if model_type == 'lgb':
        X_curr = get_underscore_data(X_data)
        if hasattr(model, 'feature_name_'):
            # Ensure column order
            # Filter only available columns
            available_cols = [c for c in model.feature_name_ if c in X_curr.columns]
            # If missing columns, might crash. 
            # Ideally we should have all columns.
            X_curr = X_curr[available_cols]
    else:
        X_curr = X_data.copy()
        if hasattr(model, 'feature_names_in_'):
            available_cols = [c for c in model.feature_names_in_ if c in X_curr.columns]
            X_curr = X_curr[available_cols]
        elif hasattr(model, 'feature_names_'):
            available_cols = [c for c in model.feature_names_ if c in X_curr.columns]
            X_curr = X_curr[available_cols]
            
    return model.predict(X_curr)
