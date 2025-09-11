from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import psycopg2
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
# Notifier
# =========================
def notify(message):
    slack_url = os.getenv("SLACK_WEBHOOK_URL")
    teams_url = os.getenv("TEAMS_WEBHOOK_URL")
    if slack_url:
        requests.post(slack_url, json={"text": message})
    if teams_url:
        payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "FF0000",
            "title": "🚨 Forecast Drift Alert",
            "text": message,
        }
        requests.post(teams_url, json=payload)

# =========================
# Forecast Drift Logic
# =========================
def check_forecast_drift():
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT f.forecast_id, f.account_id, f.service_id, a.account_name, s.service_name,
               f.forecast_period_start, f.forecast_period_end, f.forecast_amount, f.confidence_interval,
               SUM(b.cost_amount) as actual_cost
        FROM forecasts f
        JOIN accounts a ON f.account_id = a.account_id
        JOIN services s ON f.service_id = s.service_id
        LEFT JOIN billing b
            ON f.account_id = b.account_id
           AND f.service_id = b.service_id
           AND b.usage_date BETWEEN f.forecast_period_start AND f.forecast_period_end
        WHERE f.forecast_period_end >= CURRENT_DATE - INTERVAL '1 day'
        GROUP BY f.forecast_id, f.account_id, f.service_id, a.account_name, s.service_name,
                 f.forecast_period_start, f.forecast_period_end, f.forecast_amount, f.confidence_interval
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    anomalies = []

    for row in rows:
        forecast_id, acct_id, svc_id, acct_name, svc_name, f_start, f_end, forecast_amt, ci_json, actual_cost = row
        if not ci_json:
            continue
        ci = json.loads(ci_json)
        lower, upper = ci.get("lower"), ci.get("upper")

        if actual_cost is None:
            continue

        if actual_cost < lower or actual_cost > upper:
            cursor.execute("""
                INSERT INTO anomalies (account_id, service_id, metric, observed_value,
                                       expected_value, deviation_percent, details, status)
                VALUES (%s, %s, 'cost', %s, %s, %s, %s, 'open')
                ON CONFLICT DO NOTHING;
            """, (
                acct_id,
                svc_id,
                actual_cost,
                forecast_amt,
                round(((actual_cost - forecast_amt) / forecast_amt) * 100, 2) if forecast_amt > 0 else 0,
                json.dumps({"forecast_id": forecast_id, "lower": lower, "upper": upper})
            ))
            conn.commit()

            anomalies.append(f"- {acct_name} / {svc_name}: Actual ${actual_cost:.2f} outside forecast range (${lower:.2f}–${upper:.2f})")

    cursor.close()
    conn.close()

    if anomalies:
        notify("🚨 Forecast Drift Detected:\n" + "\n".join(anomalies))
    else:
        notify("✅ No forecast drift detected today.")

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
    dag_id="forecast_drift_check",
    default_args=default_args,
    description="Daily check for forecast drift (actual vs forecast) with anomaly API integration",
    schedule_interval="0 8 * * *",   # daily at 8 AM UTC
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["finops", "forecast", "drift"],
) as dag:

    drift_check = PythonOperator(
        task_id="check_forecast_drift",
        python_callable=check_forecast_drift,
    )
