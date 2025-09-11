from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import pandas as pd
import psycopg2
import requests
import json
import uuid

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
# Notifiers
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
            "themeColor": "0072C6",
            "title": "💰 Savings Tracker Update",
            "text": message,
        }
        requests.post(teams_url, json=payload)

# =========================
# Savings Tracker Logic
# =========================
def track_savings():
    conn = get_db_connection()

    # Pull applied recommendations (latest per resource)
    recs = pd.read_sql("""
        SELECT DISTINCT ON (resource_id) rec_id, resource_id, recommended_config, created_at
        FROM recommendations
        WHERE status = 'applied'
        ORDER BY resource_id, created_at DESC
    """, conn)

    if recs.empty:
        notify("ℹ️ No applied recommendations found to track savings.")
        conn.close()
        return

    results = []
    total_savings = 0
    cursor = conn.cursor()

    for _, row in recs.iterrows():
        rec_id = row["rec_id"]
        rid = row["resource_id"]
        applied_date = row["created_at"]

        # 30 days before
        cursor.execute("""
            SELECT SUM(cost_amount) 
            FROM billing
            WHERE resource_id = %s
              AND usage_date < %s
              AND usage_date >= %s
        """, (rid, applied_date.date(), applied_date.date() - timedelta(days=30)))
        before = cursor.fetchone()[0] or 0

        # 30 days after
        cursor.execute("""
            SELECT SUM(cost_amount) 
            FROM billing
            WHERE resource_id = %s
              AND usage_date >= %s
              AND usage_date < %s
        """, (rid, applied_date.date(), applied_date.date() + timedelta(days=30)))
        after = cursor.fetchone()[0] or 0

        savings = before - after if before > after else 0

        if savings > 0:
            cursor.execute("""
                INSERT INTO savings (account_id, resource_id, rec_id, actual_savings, currency, implemented_at)
                SELECT r.account_id, r.resource_id, %s, %s, 'USD', NOW()
                FROM resources r
                WHERE r.resource_id = %s
                ON CONFLICT (resource_id, rec_id) DO UPDATE
                  SET actual_savings = EXCLUDED.actual_savings,
                      implemented_at = NOW()
            """, (rec_id, savings, rid))

            cursor.execute("""
                UPDATE recommendations
                SET status = 'validated'
                WHERE rec_id = %s
            """, (rec_id,))

            cursor.execute("""
                SELECT a.account_name, s.service_name
                FROM resources r
                JOIN accounts a ON r.account_id = a.account_id
                JOIN services s ON r.service_id = s.service_id
                WHERE r.resource_id = %s
            """, (rid,))
            acct_name, svc_name = cursor.fetchone()

            results.append((rec_id, rid, acct_name, svc_name, savings, "validated"))
            total_savings += savings

        else:
            cursor.execute("""
                UPDATE recommendations
                SET status = 'no_savings'
                WHERE rec_id = %s
            """, (rec_id,))
            results.append((rec_id, rid, None, None, 0, "no_savings"))

        # Audit log
        cursor.execute("""
            INSERT INTO logs (timestamp, level, component, message, correlation_id, extra)
            VALUES (NOW(), %s, %s, %s, %s, %s)
        """, (
            "INFO" if savings > 0 else "WARN",
            "savings-tracker",
            f"Recommendation {rec_id} for Resource {rid} → {savings:.2f}",
            str(uuid.uuid4()),
            json.dumps({"rec_id": rec_id, "resource_id": rid, "savings": savings})
        ))

        conn.commit()

    cursor.close()
    conn.close()

    # Notifications
    if results:
        lines = ["💰 Savings Tracker Results:"]
        for rec_id, rid, acct, svc, savings, status in results:
            if savings > 0:
                lines.append(f"- Rec {rec_id} | {acct}/{svc} → Resource {rid}: ${savings:.2f} → {status}")
            else:
                lines.append(f"- Rec {rec_id} | Resource {rid}: no measurable savings → {status}")
        lines.append(f"\n📊 Total Savings This Month: ${total_savings:.2f}")
        notify("\n".join(lines))
    else:
        notify("ℹ️ No measurable savings detected.")

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
    dag_id="savings_tracker",
    default_args=default_args,
    description="Track realized savings from applied recommendations and update statuses",
    schedule_interval="0 9 * * *",  # daily at 9 AM UTC
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["finops", "savings"],
) as dag:

    track = PythonOperator(
        task_id="track_savings",
        python_callable=track_savings,
    )
