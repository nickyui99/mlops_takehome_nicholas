# Airflow Setup on Windows

## ✅ What's Running

Airflow is running in Docker containers with all required dependencies (MLflow, scikit-learn, FastAPI, etc.)

### Access Airflow

- **Web UI**: http://localhost:8080
- **Username**: `admin`
- **Password**: `admin`

## 🚀 Quick Start Commands

### Start Airflow
```powershell
cd mlops_takehome_nicholas
docker compose -f docker-compose.airflow.yaml up -d
```

### Stop Airflow
```powershell
docker compose -f docker-compose.airflow.yaml down
```

### Trigger DAG (CLI)
```powershell
docker exec airflow-webserver airflow dags trigger iris_training_pipeline
```

### View DAG Status
```powershell
docker exec airflow-webserver airflow dags list-runs -d iris_training_pipeline
```

### View DAG Logs
```powershell
# Check scheduler logs
docker logs airflow-scheduler --tail 100

# Check webserver logs
docker logs airflow-webserver --tail 100
```

### View Task Logs
```powershell
# List tasks
docker exec airflow-webserver airflow tasks list iris_training_pipeline

# View task state
docker exec airflow-webserver airflow tasks state iris_training_pipeline train_model <run-date>
```

## 📋 DAG Details

**DAG ID**: `iris_training_pipeline`

**Tasks**:
1. `fetch_data` - Loads Iris dataset from sklearn
2. `train_model` - Trains model and logs to MLflow  
3. `evaluate_model` - Validates accuracy > 0.9
4. `register_model` - Registers model in MLflow

**Flow**: fetch_data → train_model → evaluate_model → register_model

## 🔧 Troubleshooting

### DAG Not Showing Up
```powershell
# Check for import errors
docker exec airflow-webserver airflow dags list-import-errors

# Restart scheduler
docker restart airflow-scheduler
```

### View Container Status
```powershell
docker ps --filter "name=airflow"
```

### Access Container Shell
```powershell
# Webserver
docker exec -it airflow-webserver bash

# Scheduler
docker exec -it airflow-scheduler bash
```

### Rebuild Containers (After Code Changes)
```powershell
docker compose -f docker-compose.airflow.yaml down
docker compose -f docker-compose.airflow.yaml up -d --build
```

## 📁 File Structure

```
mlops_takehome_nicholas/
├── docker-compose.airflow.yaml  # Airflow Docker config
├── pipelines/
│   └── iris_training_dag.py     # Your DAG file
├── train/
│   └── train.py                 # Training script
├── airflow-data/                # Airflow metadata & logs (auto-created)
│   ├── airflow.db
│   ├── dags/                    # DAGs copied here
│   └── logs/                    # Task execution logs
└── mlruns/                      # MLflow tracking data
```

## 🌐 Web UI Navigation

1. **Home/DAGs**: Lists all DAGs
2. **Graph View**: Visual representation of task dependencies
3. **Tree View**: Historical runs and task states
4. **Task Logs**: Click any task → View Log

## 📝 Notes

- **Why Docker**: Airflow doesn't support native Windows installation
- **Executor**: Using SequentialExecutor (runs tasks one at a time)
- **Database**: SQLite (sufficient for development)
- **MLflow**: Logs stored in `./mlruns` directory
- **Auto-unpause**: DAGs start unpaused (`AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=False`)

## 🔄 Development Workflow

1. Edit DAG file in `pipelines/iris_training_dag.py`
2. Changes are automatically detected (volume mounted)
3. Refresh Airflow UI or wait ~30 seconds for scheduler to pick up changes
4. Trigger DAG manually or via API

## 🛑 Common Issues

### "Zombie Task" Error
- This happens when tasks exceed heartbeat timeout
- Solution: Trigger the DAG again or increase heartbeat timeout in airflow.cfg

### Module Not Found
- Ensure all dependencies are in `requirements.txt`
- Rebuild containers: `docker compose -f docker-compose.airflow.yaml up -d --build`

### Port 8080 Already in Use
- Stop other services using port 8080
- Or change port in docker-compose.airflow.yaml: `"8081:8080"`
