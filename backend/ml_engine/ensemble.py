import numpy as np
from . import config


def ensemble_predict(predictions):
    """
    Compute weighted average of predictions.
    predictions: dict of {model_name: prediction_array}
    weights: dict of {model_name: weight}
    """
    if not predictions:
        return None
        
    model_names = list(predictions.keys())
    
    # Use default weights from config
    w = np.array([config.DEFAULT_WEIGHTS.get(name, 0) for name in model_names])
        
    # Normalize
    if w.sum() > 0:
        w = w / w.sum()
    else:
        w = np.ones(len(model_names)) / len(model_names)
            
    # Stack predictions: (n_samples, n_models)
    preds_stack = np.column_stack([predictions[name] for name in model_names])
    
    # Weighted average
    final_pred = np.average(preds_stack, axis=1, weights=w)
    
    return final_pred
