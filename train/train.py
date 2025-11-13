import os
from pathlib import Path
import mlflow
import mlflow.sklearn
from sklearn import datasets
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import json
from datetime import datetime

# Use SQLite + relative artifact root (tracking DB only)
mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_registry_uri("sqlite:///mlflow.db")


def get_model_version() -> str:
    """Generate automatic version using timestamp."""
    return datetime.now().strftime("v%Y%m%d_%H%M%S")


def train_model():
    mlflow.set_experiment("iris-experiment")

    with mlflow.start_run() as run:
        # Generate automatic version
        model_version = get_model_version()
        
        # Log params
        params = {"test_size": 0.2, "random_state": 42, "max_iter": 200}
        mlflow.log_params(params)
        mlflow.log_param("model_version", model_version)
        mlflow.set_tag("model_version", model_version)

        # Load & split data
        iris = datasets.load_iris()
        X, y = iris.data, iris.target
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=params["test_size"], random_state=params["random_state"]
        )

        # Train
        model = LogisticRegression(max_iter=params["max_iter"])
        model.fit(X_train, y_train)

        # Evaluate
        accuracy = accuracy_score(y_test, model.predict(X_test))
        mlflow.log_metric("accuracy", accuracy)

        # Log model artifact once
        mlflow.sklearn.log_model(model, "model")

        # Optionally register model (OFF by default to avoid Windows/Linux path issues)
        register = os.getenv("REGISTER_TO_MLFLOW", "false").lower() in {"1", "true", "yes"}
        if register:
            model_uri = f"runs:/{run.info.run_id}/model"
            mlflow.register_model(model_uri, "iris-classifier")

        # Always save a portable copy for local serving
        local_dir = Path("artifacts") / "iris-classifier"
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
        
        # ⭐ CRITICAL: Save metadata with version
        metadata = {
            "model_version": model_version,
            "run_id": run.info.run_id,
            "accuracy": float(accuracy),
            "trained_at": datetime.now().isoformat(),
            "params": params
        }
        metadata_path = local_dir / "metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"✅ Training successful!")
        print(f"   Model Version: {model_version}")
        print(f"   Run ID: {run.info.run_id}")
        print(f"   Accuracy: {accuracy:.4f}")
        if register:
            print(f"   Model registered as 'iris-classifier'")
        print(f"   Local model saved to: {local_dir.resolve()}")
        print(f"   Metadata saved to: {metadata_path.resolve()}")
        return run.info.run_id

if __name__ == "__main__":
    train_model()