import pandas as pd
import joblib
from . import config

def load_preprocessor(path=config.PREPROCESSOR_FILE):
    """Load the pre-trained preprocessor pipeline."""
    if not path.exists():
        raise FileNotFoundError(f"Preprocessor not found at {path}. Please run notebook 02_scaling_encoding.ipynb to generate it.")
    return joblib.load(path)

def transform_data(preprocessor, df):
    """Transform data using the loaded preprocessor."""
    # Transform returns numpy array or sparse matrix
    X_transformed = preprocessor.transform(df)
    
    # Get feature names
    feature_names = preprocessor.get_feature_names_out()
    
    # Convert to DataFrame
    return pd.DataFrame(X_transformed, columns=feature_names)
