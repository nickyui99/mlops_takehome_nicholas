import os
from pathlib import Path
import mlflow
import mlflow.sklearn
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import json
from datetime import datetime
import logging
import warnings

# Suppress all logging output
logging.getLogger("alembic").setLevel(logging.CRITICAL)
logging.getLogger("mlflow").setLevel(logging.CRITICAL)
logging.getLogger("git").setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore")
os.environ["GIT_PYTHON_REFRESH"] = "quiet"

# Use SQLite + relative artifact root (tracking DB only)
mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_registry_uri("sqlite:///mlflow.db")


def get_model_version() -> str:
    """Generate automatic version using timestamp."""
    return datetime.now().strftime("v%Y%m%d_%H%M%S")


def load_and_preprocess_titanic():
    """Load and preprocess Titanic dataset from seaborn."""
    import seaborn as sns
    
    # Load Titanic dataset
    df = sns.load_dataset('titanic')
    
    # Select features for prediction
    features = ['pclass', 'sex', 'age', 'sibsp', 'parch', 'fare', 'embarked']
    target = 'survived'
    
    # Drop rows with missing target
    df = df.dropna(subset=[target])
    
    # Prepare features
    X = df[features].copy()
    y = df[target].values
    
    # Handle categorical variables
    X['sex'] = X['sex'].map({'male': 0, 'female': 1})
    X['embarked'] = X['embarked'].map({'C': 0, 'Q': 1, 'S': 2})
    
    # Fill missing values
    imputer = SimpleImputer(strategy='median')
    X_imputed = imputer.fit_transform(X)
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_imputed)
    
    return X_scaled, y, features, imputer, scaler


def train_model():
    mlflow.set_experiment("titanic-experiment")

    with mlflow.start_run() as run:
        # Generate automatic version
        model_version = get_model_version()
        
        # Log params
        params = {"test_size": 0.2, "random_state": 42, "max_iter": 200, "class_weight": "balanced"}
        mlflow.log_params(params)
        mlflow.log_param("model_version", model_version)
        mlflow.set_tag("model_version", model_version)

        # Load & preprocess data
        X, y, features, imputer, scaler = load_and_preprocess_titanic()
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=params["test_size"], random_state=params["random_state"], stratify=y
        )

        # Train
        model = LogisticRegression(max_iter=params["max_iter"], class_weight=params["class_weight"])
        model.fit(X_train, y_train)

        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        mlflow.log_metric("f1_score", f1)

        # Log model artifact with preprocessing objects
        mlflow.sklearn.log_model(model, "model")
        
        # Log preprocessing artifacts
        import joblib
        imputer_path = Path("temp_imputer.pkl")
        scaler_path = Path("temp_scaler.pkl")
        joblib.dump(imputer, imputer_path)
        joblib.dump(scaler, scaler_path)
        mlflow.log_artifact(str(imputer_path), "preprocessors")
        mlflow.log_artifact(str(scaler_path), "preprocessors")
        imputer_path.unlink()
        scaler_path.unlink()

        # Optionally register model (OFF by default to avoid Windows/Linux path issues)
        register = os.getenv("REGISTER_TO_MLFLOW", "false").lower() in {"1", "true", "yes"}
        if register:
            model_uri = f"runs:/{run.info.run_id}/model"
            mlflow.register_model(model_uri, "titanic-classifier")

        # Always save a portable copy for local serving
        local_dir = Path("artifacts") / "titanic-classifier"
        local_dir.parent.mkdir(parents=True, exist_ok=True)
        if local_dir.exists():
            import shutil
            # Windows-compatible directory removal with error handling
            try:
                shutil.rmtree(local_dir)
            except PermissionError:
                # On Windows, retry with different approach
                import time
                time.sleep(0.1)  # Brief pause
                shutil.rmtree(local_dir, onerror=lambda func, path, exc: os.chmod(path, 0o777) or func(path))
        mlflow.sklearn.save_model(model, str(local_dir))
        
        # Save preprocessing objects
        import joblib
        joblib.dump(imputer, local_dir / "imputer.pkl")
        joblib.dump(scaler, local_dir / "scaler.pkl")
        joblib.dump(features, local_dir / "features.pkl")
        
        # ⭐ CRITICAL: Save metadata with version
        metadata = {
            "model_version": model_version,
            "run_id": run.info.run_id,
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "trained_at": datetime.now().isoformat(),
            "params": params,
            "features": features
        }
        metadata_path = local_dir / "metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        # Only print if running as main (not when imported)
        if __name__ == "__main__":
            print(f"✅ Training successful!")
            print(f"   Model Version: {model_version}")
            print(f"   Run ID: {run.info.run_id}")
            print(f"   Accuracy: {accuracy:.4f}")
            print(f"   Precision: {precision:.4f}")
            print(f"   Recall: {recall:.4f}")
            print(f"   F1 Score: {f1:.4f}")
            if register:
                print(f"   Model registered as 'titanic-classifier'")
            print(f"   Local model saved to: {local_dir.resolve()}")
            print(f"   Metadata saved to: {metadata_path.resolve()}")
        
        return run.info.run_id

if __name__ == "__main__":
    train_model()