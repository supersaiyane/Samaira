from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import psycopg2
import os
import requests
import json

# =========================
# DB Connection Helper
# =========================
def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "finopsdb"),
        user=os.getenv("DB_USER", "finops"),
        password=os.getenv("DB_PASSWORD", "finops123"),
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", "5432"),
    )

# =========================
# Slack Notification
# =========================
def send_slack_message(message):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        print("⚠️ No Slack webhook configured")
        return
    payload = {"text": message}
    requests.post(webhook_url, data=json.dumps(payload), headers={"Content-Type": "application/json"})

# =========================
# Generate Report
# =========================
def report_recommendations():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT r.rec_type, r.estimated_savings, res.resource_name, res.resource_type, s.service_name
        FROM recommendations r
        JOIN resources res ON r.resource_id = res.resource_id
        JOIN services s ON res.service_id = s.service_id
        WHERE r.status = 'pending'
        ORDER BY r.estimated_savings DESC
        LIMIT 10;
    """)
    rows = cursor.fetchall()

    if not rows:
        send_slack_message("✅ No new recommendations today. All good!")
        return

    report_lines = ["📊 *Top 10 FinOps Savings Opportunities*"]
    for rec_type, savings, resource_name, resource_type, service_name in rows:
        report_lines.append(
            f"- {service_name}/{resource_name} ({resource_type}): *{rec_type}* → save ~${savings:,.2f}/month"
        )

    message = "\n".join(report_lines)
    send_slack_message(message)

    cursor.close()
    conn.close()

# =========================
# DAG Definition
# =========================
default_args = {
    "owner": "finops",
    "depends_on_past": False,
    "email_on_failure": True,
    "email": ["alerts@finops-toolkit.com"],
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="report_recommendations",
    default_args=default_args,
    description="Daily Slack report of top rightsizing/idle recommendations",
    schedule_interval="0 9 * * *",   # every day at 9 AM UTC
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["finops", "reporting", "slack"],
) as dag:

    report = PythonOperator(
        task_id="report_recommendations_task",
        python_callable=report_recommendations,
    )
