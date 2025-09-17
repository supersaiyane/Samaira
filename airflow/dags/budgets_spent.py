from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import psycopg2
import os

def update_spent_amounts():
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME", "finopsdb"),
        user=os.getenv("DB_USER", "finops"),
        password=os.getenv("DB_PASSWORD", "finops123"),
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", "5432"),
    )
    cur = conn.cursor()

    sql = """
    UPDATE budgets b
    SET spent_amount = sub.total
    FROM (
        SELECT account_id, service_id, SUM(cost_amount) AS total
        FROM billing
        WHERE usage_date >= b.start_date AND (b.end_date IS NULL OR usage_date <= b.end_date)
        GROUP BY account_id, service_id
    ) sub
    WHERE b.account_id = sub.account_id AND b.service_id = sub.service_id;
    """

    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()

with DAG(
    "update_budgets_spent",
    default_args={"retries": 1, "retry_delay": timedelta(minutes=5)},
    schedule_interval="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:

    update_task = PythonOperator(
        task_id="update_spent_amounts",
        python_callable=update_spent_amounts,
    )
