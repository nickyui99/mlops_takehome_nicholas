# /pipelines/iris_training_dag.py
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from pathlib import Path
import sys

# Add /train to path so we can import train.py
sys.path.insert(0, str(Path(__file__).parent.parent / "train"))

from train import train_model  # your existing function

DAG_ID = "iris_training_pipeline"

with DAG(
    dag_id=DAG_ID,
    start_date=datetime(2025, 1, 1),
    schedule=None,  # manual trigger
    catchup=False,
    tags=["mlops", "iris"]
) as dag:

    def fetch_data(**context):
        # In real life: download from S3, DB, etc.
        # Here: just confirm sklearn is available
        from sklearn import datasets
        iris = datasets.load_iris()
        print(f"Fetched {len(iris.data)} samples")
        return "data_ready"

    def train_task(**context):
        run_id = train_model()  # this logs to MLflow
        # Push run_id to XCom for next task
        context["task_instance"].xcom_push(key="run_id", value=run_id)
        return run_id

    def evaluate_task(**context):
        run_id = context["task_instance"].xcom_pull(task_ids="train_model", key="run_id")
        print(f"Evaluating run: {run_id}")
        # In real life: compute drift, test set metrics, etc.
        # For now: just confirm it exists in MLflow
        import mlflow
        run = mlflow.get_run(run_id)
        accuracy = run.data.metrics.get("accuracy")
        print(f"Accuracy from MLflow: {accuracy}")
        if accuracy is None or accuracy < 0.9:
            raise ValueError("Model accuracy too low!")
        return "passed"

    def register_model_task(**context):
        run_id = context["task_instance"].xcom_pull(task_ids="train_model", key="run_id")
        import mlflow
        model_uri = f"runs:/{run_id}/model"
        mlflow.register_model(model_uri, "iris-classifier")
        print(f"Registered model from run {run_id} as 'iris-classifier'")
        return "registered"

    # Tasks
    fetch = PythonOperator(task_id="fetch_data", python_callable=fetch_data)
    train = PythonOperator(task_id="train_model", python_callable=train_task)
    evaluate = PythonOperator(task_id="evaluate_model", python_callable=evaluate_task)
    register = PythonOperator(task_id="register_model", python_callable=register_model_task)

    # Dependencies
    fetch >> train >> evaluate >> register