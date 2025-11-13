# Airflow 2.10.x RecursionError Issue Analysis

## Problem Summary

Airflow 2.10.x tasks fail with zombie process detection and RecursionError when processing verbose MLflow output. This occurs specifically when MLflow performs database migrations that generate 100+ lines of log output.

## Root Cause

The issue occurs in Airflow's log processing pipeline:

1. **MLflow Verbose Output**: When MLflow initializes, it runs Alembic database migrations that produce very verbose output (~100+ lines)
2. **Airflow Log Processing**: Airflow's `logging_mixin.py` attempts to strip ANSI color codes from task output using the `re2` library
3. **Recursion Limit Hit**: The `re2.finditer()` function hits Python's recursion limit when processing the large text block from MLflow migrations
4. **Zombie Task**: Airflow scheduler detects the task as a zombie and kills it

## Evidence from Logs

```
Task exited with return code Negsignal.SIGKILL
Marking task as FAILED.
RecursionError: maximum recursion depth exceeded
  File "/usr/local/lib/python3.11/site-packages/airflow/utils/log/logging_mixin.py", line 118
    for match in re2.finditer(r"\x1b\[[0-9;]*m", text):
```

## MLflow Migration Output Example

When MLflow starts, it produces output like:
```
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 451aebb31d03, add metric step
INFO  [alembic.runtime.migration] Running upgrade 451aebb31d03 -> 90e64c465722, migrate user column to tags
...
[100+ more lines of migration logs]
```

## Solutions Implemented

### 1. Logging Suppression in Training Script

**File**: `train/train.py`

```python
# Suppress verbose logging
logging.getLogger("alembic").setLevel(logging.CRITICAL)
logging.getLogger("mlflow").setLevel(logging.CRITICAL)
logging.getLogger("git").setLevel(logging.CRITICAL)
```

This prevents MLflow from outputting verbose migration logs to stdout.

### 2. Subprocess Isolation in Airflow DAG

**File**: `pipelines/iris_training_dag.py`

**Before** (Direct execution - prone to RecursionError):
```python
def train_task(**context):
    mlflow.set_tracking_uri("file:///opt/airflow/mlruns")
    run_info = train_model()
    context['ti'].xcom_push(key='run_id', value=run_info.run_id)
```

**After** (Subprocess isolation - protects Airflow from verbose output):
```python
def train_task(**context):
    result = subprocess.run(
        ['python', '/opt/airflow/train/train.py'],
        capture_output=True,
        text=True,
        timeout=300,
        check=True
    )
    
    # Parse JSON output to extract run_id
    output = json.loads(result.stdout.strip().split('\n')[-1])
    context['ti'].xcom_push(key='run_id', value=output['run_id'])
```

### 3. Environment Variables for Better Task Management

**File**: `docker-compose.airflow.yaml`

```yaml
environment:
  - GIT_PYTHON_REFRESH=quiet
  - AIRFLOW__SCHEDULER__JOB_HEARTBEAT_SEC=10
  - AIRFLOW__CORE__KILLED_TASK_CLEANUP_TIME=300
```

These settings:
- Suppress git verbose output
- Increase scheduler heartbeat frequency for faster zombie detection
- Give killed tasks more time to clean up gracefully

### 4. Task Configuration with Retries and Timeouts

**File**: `pipelines/iris_training_dag.py`

```python
default_args = {
    'owner': 'mlops',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=1),
    'execution_timeout': timedelta(minutes=10),
}
```

## Task Status After Fixes

| Task | Before Fix | After Fix | Solution Applied |
|------|------------|-----------|------------------|
| `fetch_data` | ✅ SUCCESS | ✅ SUCCESS | No changes needed |
| `train_model` | ❌ FAILED (RecursionError) | ✅ SUCCESS | Subprocess isolation + logging suppression |
| `evaluate_model` | ⚠️ Blocked by train_model | ✅ SUCCESS | Subprocess isolation + logging suppression |
| `register_model` | ⚠️ Blocked by evaluate_model | ✅ SUCCESS | Subprocess isolation |

## Verification

Run the Airflow DAG and verify all tasks complete successfully:

```bash
# Using Docker Compose
docker-compose -f docker-compose.airflow.yaml up -d
docker-compose -f docker-compose.airflow.yaml exec airflow-webserver airflow dags trigger iris_training_pipeline

# Check logs
docker-compose -f docker-compose.airflow.yaml logs -f airflow-scheduler
```

## Alternative Approaches Considered

1. **Upgrade Airflow**: Wait for Airflow 2.11+ which may fix the re2 recursion issue
2. **Switch to Airflow 2.9.x**: Downgrade to avoid the bug (not recommended for long-term)
3. **Disable ANSI stripping**: Modify Airflow's logging configuration (complex, affects all tasks)
4. **MLflow silent mode**: Not available as a configuration option

**Chosen Solution**: Subprocess isolation is the most robust and maintainable solution.

## Testing

All DAG tasks now complete successfully with the implemented fixes. The MLflow UI shows all runs logged correctly at http://localhost:5000.

## References

- Airflow GitHub Issue: Similar recursion issues reported with verbose task output
- MLflow Documentation: Database migration behavior
- Airflow Documentation: Task isolation and zombie task detection
