import pandas as pd
import numpy as np
from . import config, feature_engineering, preprocessing, models, ensemble

class Predictor:
    def __init__(self):
        self.historical_df = None
        self.preprocessor = None
        self.models = {}

    def load_resources(self):
        """Load data, preprocessor, models, and weights."""
        # Load historical data
        if config.RAW_DATA_FILE.exists():
            self.historical_df = feature_engineering.load_data(config.RAW_DATA_FILE)
            # Pre-process history up to domain features to save time?
            # For now, just load raw.
        else:
            print(f"Warning: Historical data not found at {config.RAW_DATA_FILE}")
            
        # Load preprocessor
        if config.PREPROCESSOR_FILE.exists():
            self.preprocessor = preprocessing.load_preprocessor()
        else:
            print("Warning: Preprocessor not found. Please run training/preprocessing first.")
            
        self.models = models.load_models()
        
        
    def predict(self, input_data):
        """
        Run the full prediction pipeline for a single input.
        input_data: dict
        """
        if self.historical_df is None:
            raise ValueError("Historical data not loaded.")
            
        # 1. Feature Engineering (including temporal features)
        processed_df = feature_engineering.process_single_input(input_data, self.historical_df)
        
        # 2. Preprocessing (Scaling/Encoding)
        if self.preprocessor:
            X_scaled = preprocessing.transform_data(self.preprocessor, processed_df)
        else:
            X_scaled = processed_df
            
        # 3. Model Prediction
        model_preds = {}
        for name, model in self.models.items():
            try:
                model_preds[name] = models.predict_single_model(model, X_scaled, name)
            except Exception as e:
                print(f"Prediction failed for {name}: {e}")
                
        if not model_preds:
            return None
            
        # 4. Ensemble
        final_yield_log_pred = ensemble.ensemble_predict(model_preds)
        
        # 5. Inverse Transform (Log1p -> Original)
        yield_pred = np.expm1(final_yield_log_pred)
        
        # If user wants total production: yield * area
        area = input_data.get('area_thousand_ha', 0)
        production_pred = yield_pred * area
        
        return {
            "yield_ton_per_ha": yield_pred[0],
            "production_tonnes": production_pred[0] * 1000 # area is in 1000 ha
        }

def run_pipeline(input_data):
    predictor = Predictor()
    predictor.load_resources()
    return predictor.predict(input_data)
