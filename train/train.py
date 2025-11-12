import os
from pathlib import Path
import mlflow
import mlflow.sklearn
from sklearn import datasets
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Use SQLite + relative artifact root (tracking DB only)
mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_registry_uri("sqlite:///mlflow.db")


def train_model():
    mlflow.set_experiment("iris-experiment")

    with mlflow.start_run() as run:
        # Log params
        params = {"test_size": 0.2, "random_state": 42, "max_iter": 200}
        mlflow.log_params(params)

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
            shutil.rmtree(local_dir)
        mlflow.sklearn.save_model(model, str(local_dir))

        print(f"✅ Training successful!")
        print(f"   Run ID: {run.info.run_id}")
        print(f"   Accuracy: {accuracy:.4f}")
        if register:
            print(f"   Model registered as 'iris-classifier'")
        print(f"   Local model saved to: {local_dir.resolve()}")
        return run.info.run_id

if __name__ == "__main__":
    train_model()