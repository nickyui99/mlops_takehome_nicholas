# /pipelines/iris_training_dag.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from pathlib import Path
import sys

# Add /train to path so we can import train.py
sys.path.insert(0, str(Path(__file__).parent.parent / "train"))

from train import train_model  # your existing function

DAG_ID = "titanic_training_pipeline"

# Default args with retries and timeouts
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
    'execution_timeout': timedelta(minutes=10),
}

with DAG(
    dag_id=DAG_ID,
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule=None,  # manual trigger
    catchup=False,
    tags=["mlops", "titanic"]
) as dag:

    def fetch_data(**context):
        # In real life: download from S3, DB, etc.
        # Here: confirm seaborn titanic dataset is available
        import seaborn as sns
        titanic = sns.load_dataset('titanic')
        print(f"Fetched {len(titanic)} Titanic passenger records")
        return "data_ready"

    def train_task(**context):
        # Suppress output by redirecting to subprocess
        import subprocess
        import sys
        
        # Run training in a subprocess to isolate logging
        result = subprocess.run(
            [sys.executable, "-c", 
             "import sys; sys.path.insert(0, '/opt/airflow/train'); from train import train_model; print(train_model(), end='')"],
            capture_output=True,
            text=True,
            cwd="/opt/airflow"
        )
        
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            raise RuntimeError(f"Training failed with error: {result.stderr}")
        
        # Extract just the run_id (last line of output)
        run_id = result.stdout.strip().split('\n')[-1]
        print(f"✅ Training completed. Run ID: {run_id}")
        
        # Push run_id to XCom for next task
        context["task_instance"].xcom_push(key="run_id", value=run_id)
        return run_id

    def evaluate_task(**context):
        # Isolate MLflow operations in subprocess to avoid log processing issues
        import subprocess
        import sys
        
        run_id = context["task_instance"].xcom_pull(task_ids="train_model", key="run_id")
        print(f"Evaluating run: {run_id}")
        
        # Run evaluation in subprocess
        result = subprocess.run(
            [sys.executable, "-c", f"""
import sys
sys.path.insert(0, '/opt/airflow/train')
import mlflow
import logging
logging.getLogger('mlflow').setLevel(logging.CRITICAL)
logging.getLogger('alembic').setLevel(logging.CRITICAL)

mlflow.set_tracking_uri('sqlite:///mlflow.db')
run = mlflow.get_run('{run_id}')
accuracy = run.data.metrics.get('accuracy')
print(accuracy if accuracy is not None else 'None', end='')
"""],
            capture_output=True,
            text=True,
            cwd="/opt/airflow"
        )
        
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            raise RuntimeError(f"Evaluation failed: {result.stderr}")
        
        accuracy_str = result.stdout.strip()
        if accuracy_str == 'None':
            raise ValueError("Model accuracy not found in MLflow!")
        
        accuracy = float(accuracy_str)
        print(f"✅ Accuracy from MLflow: {accuracy:.4f}")
        
        if accuracy < 0.75:
            raise ValueError(f"Model accuracy too low: {accuracy:.4f} < 0.75")
        
        return "passed"

    def register_model_task(**context):
        # Isolate MLflow operations in subprocess to avoid log processing issues
        import subprocess
        import sys
        
        run_id = context["task_instance"].xcom_pull(task_ids="train_model", key="run_id")
        
        # Run model registration in subprocess
        result = subprocess.run(
            [sys.executable, "-c", f"""
import sys
sys.path.insert(0, '/opt/airflow/train')
import mlflow
import logging
logging.getLogger('mlflow').setLevel(logging.CRITICAL)
logging.getLogger('alembic').setLevel(logging.CRITICAL)

mlflow.set_tracking_uri('sqlite:///mlflow.db')
mlflow.set_registry_uri('sqlite:///mlflow.db')

model_uri = f'runs:/{run_id}/model'
mlflow.register_model(model_uri, 'titanic-classifier')
print('success', end='')"""
""".replace('{run_id}', run_id)],
            capture_output=True,
            text=True,
            cwd="/opt/airflow"
        )
        
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            raise RuntimeError(f"Model registration failed: {result.stderr}")
        
        print(f"✅ Registered model from run {run_id} as 'titanic-classifier'")
        return "registered"

    # Tasks
    fetch = PythonOperator(task_id="fetch_data", python_callable=fetch_data)
    train = PythonOperator(task_id="train_model", python_callable=train_task)
    evaluate = PythonOperator(task_id="evaluate_model", python_callable=evaluate_task)
    register = PythonOperator(task_id="register_model", python_callable=register_model_task)

    # Dependencies
    fetch >> train >> evaluate >> register