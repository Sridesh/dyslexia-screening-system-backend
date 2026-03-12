import sys
import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

def train_and_save_rf():
    dataset_path = "stratified_ml_dataset.csv"
    if not os.path.exists(dataset_path):
        print(f"Dataset not found: {dataset_path}. Run generate_balanced_dataset.py first.")
        return
        
    print(f"Loading {dataset_path}...")
    df = pd.read_csv(dataset_path)
    X = df[['est_theta_pa', 'est_theta_ran', 'est_theta_or', 'avg_rt_ran']]
    y = df['is_at_risk']
    
    # Train heavily on the balanced matrix to eliminate uniform biases
    print("Training Random Forest Classifier on 10,000 balanced scenarios...")
    rf_model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    rf_model.fit(X, y)
    
    # Ensure models directory exists
    models_dir = os.path.join(os.path.dirname(__file__), "..", "ml_models")
    os.makedirs(models_dir, exist_ok=True)
    
    model_path = os.path.join(models_dir, "rf_model.joblib")
    joblib.dump(rf_model, model_path)
    
    print(f"Successfully trained and saved new Balanced Random Forest to {model_path}")

if __name__ == "__main__":
    train_and_save_rf()
