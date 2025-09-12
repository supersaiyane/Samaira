FROM apache/airflow:2.7.2

USER root
RUN apt-get update && apt-get install -y build-essential python3-dev libpq-dev && rm -rf /var/lib/apt/lists/*
USER airflow

# Copy extra deps
COPY airflow/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy DAGs
COPY airflow/dags /opt/airflow/dags
