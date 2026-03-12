import os
import joblib

_rf_model = None

def load_rf_model():
    global _rf_model
    if _rf_model is None:
        model_path = os.path.join(os.path.dirname(__file__), "..", "ml_models", "rf_model.joblib")
        try:
            _rf_model = joblib.load(model_path)
        except Exception as e:
            print(f"[ERROR] Failed to load Random Forest model: {e}")
            _rf_model = None
    return _rf_model

def predict_risk_rf(pa_theta: float, ran_theta: float, or_theta: float, ran_rt: float) -> float:
    """Predict risk using the pre-trained Random Forest model."""
    model = load_rf_model()
    if model is None:
        return 0.0
        
    # Model expects exactly these 4 feature names in this order
    import pandas as pd
    X = pd.DataFrame([{
        'est_theta_pa': pa_theta,
        'est_theta_ran': ran_theta,
        'est_theta_or': or_theta,
        'avg_rt_ran': ran_rt
    }])
    
    # Predict probabilities. [0][1] is the probability for class '1' (At Risk)
    probs = model.predict_proba(X)
    risk_score = probs[0][1]
    
    return float(risk_score)
