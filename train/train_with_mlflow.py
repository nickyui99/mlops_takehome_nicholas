"""
Training script with MLflow tracking for Titanic Classifier
This demonstrates model versioning and experiment tracking
"""
import os
import mlflow
import mlflow.sklearn
import pandas as pd
import joblib
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

# Configure MLflow
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment("titanic-classifier-training")

print(f"MLflow Tracking URI: {MLFLOW_TRACKING_URI}")

def load_and_preprocess_data():
    """Load and preprocess the Titanic dataset"""
    # This is a placeholder - adjust path to your actual dataset
    data_path = Path(__file__).parent.parent / "datasets" / "titanic_train.csv"
    
    if not data_path.exists():
        print(f"⚠️  Dataset not found at {data_path}")
        print("Creating synthetic data for demonstration...")
        # Create synthetic data for demo
        import numpy as np
        np.random.seed(42)
        n_samples = 800
        df = pd.DataFrame({
            'Pclass': np.random.choice([1, 2, 3], n_samples),
            'Sex': np.random.choice(['male', 'female'], n_samples),
            'Age': np.random.normal(30, 15, n_samples),
            'SibSp': np.random.poisson(0.5, n_samples),
            'Parch': np.random.poisson(0.3, n_samples),
            'Fare': np.random.lognormal(3, 1.5, n_samples),
            'Embarked': np.random.choice(['C', 'Q', 'S'], n_samples),
            'Survived': np.random.choice([0, 1], n_samples, p=[0.6, 0.4])
        })
    else:
        df = pd.read_csv(data_path)
    
    # Encode categorical variables
    df['Sex'] = df['Sex'].map({'male': 0, 'female': 1})
    df['Embarked'] = df['Embarked'].map({'C': 0, 'Q': 1, 'S': 2})
    
    # Select features
    features = ['Pclass', 'Sex', 'Age', 'SibSp', 'Parch', 'Fare', 'Embarked']
    X = df[features]
    y = df['Survived']
    
    return train_test_split(X, y, test_size=0.2, random_state=42)

def train_model(n_estimators=100, max_depth=10, min_samples_split=5, version="1.0"):
    """Train a Random Forest model with MLflow tracking"""
    
    print(f"\n🚀 Starting training for model version {version}...")
    
    # Start MLflow run
    with mlflow.start_run(run_name=f"titanic-v{version}") as run:
        # Load data
        X_train, X_test, y_train, y_test = load_and_preprocess_data()
        print(f"✅ Data loaded: {len(X_train)} training samples, {len(X_test)} test samples")
        
        # Imputation and Scaling
        imputer = SimpleImputer(strategy='median')
        scaler = StandardScaler()
        
        X_train_imputed = imputer.fit_transform(X_train)
        X_train_scaled = scaler.fit_transform(X_train_imputed)
        
        X_test_imputed = imputer.transform(X_test)
        X_test_scaled = scaler.transform(X_test_imputed)
        
        # Log preprocessing parameters
        mlflow.log_param("imputation_strategy", "median")
        mlflow.log_param("scaling", "StandardScaler")
        
        # Train model
        model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            random_state=42,
            n_jobs=-1
        )
        
        print(f"🔧 Training model with n_estimators={n_estimators}, max_depth={max_depth}...")
        model.fit(X_train_scaled, y_train)
        
        # Make predictions
        y_pred_train = model.predict(X_train_scaled)
        y_pred_test = model.predict(X_test_scaled)
        
        # Calculate metrics
        train_accuracy = accuracy_score(y_train, y_pred_train)
        test_accuracy = accuracy_score(y_test, y_pred_test)
        precision = precision_score(y_test, y_pred_test)
        recall = recall_score(y_test, y_pred_test)
        f1 = f1_score(y_test, y_pred_test)
        
        print(f"📊 Results:")
        print(f"   Train Accuracy: {train_accuracy:.4f}")
        print(f"   Test Accuracy:  {test_accuracy:.4f}")
        print(f"   Precision:      {precision:.4f}")
        print(f"   Recall:         {recall:.4f}")
        print(f"   F1 Score:       {f1:.4f}")
        
        # Log parameters
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("max_depth", max_depth)
        mlflow.log_param("min_samples_split", min_samples_split)
        mlflow.log_param("model_version", version)
        
        # Log metrics
        mlflow.log_metric("train_accuracy", train_accuracy)
        mlflow.log_metric("test_accuracy", test_accuracy)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        mlflow.log_metric("f1_score", f1)
        
        # Log model to MLflow
        mlflow.sklearn.log_model(
            model, 
            "model"
        )
        
        # Save model artifacts locally
        artifacts_dir = Path(__file__).parent.parent / "artifacts" / "titanic-classifier"
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        
        joblib.dump(model, artifacts_dir / "model.pkl")
        joblib.dump(imputer, artifacts_dir / "imputer.pkl")
        joblib.dump(scaler, artifacts_dir / "scaler.pkl")
        
        # Save metadata
        import json
        metadata = {
            "model_version": version,
            "mlflow_run_id": run.info.run_id,
            "model_path": str(artifacts_dir),
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "test_accuracy": test_accuracy,
            "f1_score": f1
        }
        
        with open(artifacts_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n✅ Model saved to {artifacts_dir}")
        print(f"📝 MLflow Run ID: {run.info.run_id}")
        print(f"🔗 View in MLflow UI: {MLFLOW_TRACKING_URI}/#/experiments/{run.info.experiment_id}/runs/{run.info.run_id}")
        
        return run.info.run_id

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Train Titanic Classifier with MLflow")
    parser.add_argument("--n-estimators", type=int, default=100, help="Number of trees")
    parser.add_argument("--max-depth", type=int, default=10, help="Maximum depth of trees")
    parser.add_argument("--min-samples-split", type=int, default=5, help="Minimum samples to split")
    parser.add_argument("--version", type=str, default="1.0", help="Model version")
    
    args = parser.parse_args()
    
    run_id = train_model(
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        min_samples_split=args.min_samples_split,
        version=args.version
    )
    
    print(f"\n🎉 Training complete! Run ID: {run_id}")
