import pandas as pd
import numpy as np
from . import config

def load_data(path):
    """Load raw data from CSV."""
    return pd.read_csv(path)

def initial_cleaning(df):
    """Drop unnecessary columns and convert units."""
    # Drop lat/long
    cols_to_drop = [c for c in df.columns if c.startswith(("latitude", "longitude"))]
    df = df.drop(columns=cols_to_drop, errors='ignore')
    
    # Drop production if exists
    if "production_thousand_tonnes" in df.columns:
        df = df.drop(columns=["production_thousand_tonnes"])
        
    # Convert yield unit
    if "yield_ta_per_ha" in df.columns:
        df['yield_ton_per_ha'] = df['yield_ta_per_ha'] / 10
        df = df.drop(columns=['yield_ta_per_ha'])
        
    return df

def log_transform(df):
    """Apply log1p transform to area and yield."""
    cols_temp = ["yield_ton_per_ha", "area_thousand_ha"]
    for col in cols_temp:
        if col in df.columns:
            # Create new log column
            df[f"log1p_{col}"] = np.log1p(df[col].clip(lower=0))
    
    df = df.drop(columns=[c for c in cols_temp if c in df.columns], errors='ignore')
    
    return df

def create_domain_features(df):
    """Create domain-inspired features."""
    eps = 1e-6
    
    # Soil quality
    soil_cols = [c for c in df.columns if c.startswith("soil_") and "scaled" not in c]
    if soil_cols:
        df["soil_quality_index"] = df[soil_cols].mean(axis=1)
    else:
        df["soil_quality_index"] = np.nan
        
    # Climate features
    df["temp_range"] = df["max_temperature"] - df["min_temperature"]
    df["humidity_deficit"] = df["avg_temperature"] - df["wet_bulb_temperature"]
    df["precipitation_efficiency"] = df["precipitation"] / (df["avg_temperature"] + eps)
    
    # Temp anomaly
    # Note: transform('mean') requires the whole dataset or at least history
    if "province_name" in df.columns:
        df["temp_anomaly"] = df["avg_temperature"] - df.groupby("province_name")["avg_temperature"].transform("mean")
    
    df["season_length_proxy"] = df["precipitation"] * df["solar_radiation"]
    df["heat_stress"] = (df["max_temperature"] - 35).clip(lower=0)
    df["cold_stress"] = (20 - df["min_temperature"]).clip(lower=0)
    df["wetness_index"] = df["precipitation"] * df["humidity_deficit"]
    
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    return df

def create_temporal_features(df, windows=config.WINDOWS):
    """Create lag, rolling mean, and delta features."""
    if "year" not in df.columns:
        raise ValueError("Column 'year' is required.")
        
    group_keys = [c for c in config.GROUP_KEYS if c in df.columns]
    if not group_keys:
        raise ValueError("Grouping keys missing.")
        
    # Identify numeric columns for feature generation
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    exclude_cols = ["year"] + group_keys
    base_cols = [c for c in numeric_cols if c not in exclude_cols]
    
    # Sort
    df = df.sort_values(group_keys + ["year"]).reset_index(drop=True)
    
    new_features = {}
    
    for col in base_cols:
        g_col = df.groupby(group_keys)[col]
        
        for w in windows:
            lag_name = f"{col}_lag_{w}"
            roll_name = f"{col}_mean_{w}"
            delta_name = f"{col}_delta_{w}"
            
            # Lag
            new_features[lag_name] = g_col.shift(w)
            
            # Rolling Mean (shift 1 to avoid leakage)
            new_features[roll_name] = g_col.transform(lambda s: s.shift(1).rolling(window=w, min_periods=1).mean())
            
            # Delta
            past_current = g_col.shift(1)
            past_baseline = g_col.shift(w + 1)
            new_features[delta_name] = past_current - past_baseline
            
    if new_features:
        df_features = pd.DataFrame(new_features)
        df = pd.concat([df, df_features], axis=1)
        
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    return df

def process_single_input(input_data, historical_df):
    """
    Process a single input dictionary by appending it to historical data 
    to calculate temporal features.
    """
    # Convert input to DataFrame
    input_df = pd.DataFrame([input_data])
    
    # 0. Mark input vs historical
    input_df['is_input'] = True
    historical_df['is_input'] = False
    combined_df = pd.concat([historical_df, input_df], ignore_index=True)
    
    # 1. Initial Cleaning
    combined_df = initial_cleaning(combined_df)
    
    # 2. Log Transform
    combined_df = log_transform(combined_df)
    
    # 3. Domain Features
    combined_df = create_domain_features(combined_df)
    
    # 4. Temporal Features
    combined_df = create_temporal_features(combined_df)
    
    # Extract the input row
    processed_input = combined_df[combined_df['is_input'] == True].copy()
    processed_input = processed_input.drop(columns=['is_input'])
    
    print(f"\nProcessed input shape: {processed_input}\n")
    return processed_input
