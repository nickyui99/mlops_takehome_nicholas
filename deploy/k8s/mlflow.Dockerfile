FROM python:3.11-slim

# Install MLflow with database support (no system deps needed)
RUN pip install --no-cache-dir mlflow==2.9.2 psycopg2-binary

# Create mlflow directory
RUN mkdir -p /mlflow/artifacts

WORKDIR /mlflow

EXPOSE 5000

CMD ["mlflow", "server", \
     "--host", "0.0.0.0", \
     "--port", "5000", \
     "--backend-store-uri", "postgresql://postgres:postgres@postgres:5432/mlops", \
     "--default-artifact-root", "/mlflow/artifacts", \
     "--serve-artifacts"]
