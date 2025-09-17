from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import psycopg2, os

def update_cluster_status():
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME", "finopsdb"),
        user=os.getenv("DB_USER", "finops"),
        password=os.getenv("DB_PASSWORD", "finops123"),
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", "5432"),
    )
    cur = conn.cursor()

    # Dummy logic: mark clusters with <2 resources as degraded
    cur.execute("""
        UPDATE clusters c
        SET status = CASE
            WHEN COUNT(cr.resource_id) < 2 THEN 'degraded'
            ELSE 'active'
        END
        FROM cluster_resources cr
        WHERE c.cluster_id = cr.cluster_id
        GROUP BY c.cluster_id
    """)

    conn.commit()
    cur.close()
    conn.close()

with DAG(
    "update_cluster_status",
    default_args={"retries": 1, "retry_delay": timedelta(minutes=5)},
    schedule_interval="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:

    update_task = PythonOperator(
        task_id="update_cluster_status",
        python_callable=update_cluster_status,
    )
