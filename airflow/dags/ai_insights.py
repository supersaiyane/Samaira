from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import psycopg2
import requests
import json
import pandas as pd

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
            "themeColor": "0072C6",
            "title": "🤖 FinOps AI Insights",
            "text": message,
        }
        requests.post(teams_url, json=payload)

# =========================
# AI Insights Logic
# =========================
def generate_insights():
    conn = get_db_connection()
    cursor = conn.cursor()
    insights = []

    # --------- 1. Cost Trend Analysis (Top Services Growing) ---------
    billing = pd.read_sql("""
        SELECT s.service_name, b.service_id, a.account_id, a.account_name,
               date_trunc('month', b.usage_date) as month, SUM(b.cost_amount) as cost
        FROM billing b
        JOIN accounts a ON b.account_id = a.account_id
        JOIN services s ON b.service_id = s.service_id
        WHERE b.usage_date >= CURRENT_DATE - INTERVAL '180 days'
        GROUP BY s.service_name, b.service_id, a.account_id, a.account_name, month
        ORDER BY month
    """, conn)

    if not billing.empty:
        for (acct, svc), group in billing.groupby(["account_id", "service_id"]):
            if len(group) >= 3:
                last, prev = group.iloc[-1]["cost"], group.iloc[-2]["cost"]
                if last > prev * 1.3:  # >30% increase
                    insights.append({
                        "account_id": acct,
                        "service_id": svc,
                        "insight_type": "trend",
                        "severity": "warning",
                        "message": f"Service {group.iloc[-1]['service_name']} cost rose 30%+ last month",
                        "metadata": {"last": float(last), "prev": float(prev)}
                    })

    # --------- 2. Pending Recommendations (Potential Savings) ---------
    recs = pd.read_sql("""
        SELECT r.rec_id, r.resource_id, r.estimated_savings, r.currency, r.status,
               rs.service_id, a.account_id, s.service_name
        FROM recommendations r
        JOIN resources rs ON r.resource_id = rs.resource_id
        JOIN accounts a ON rs.account_id = a.account_id
        JOIN services s ON rs.service_id = s.service_id
        WHERE r.status = 'pending'
    """, conn)

    if not recs.empty:
        for _, row in recs.iterrows():
            insights.append({
                "account_id": row["account_id"],
                "service_id": row["service_id"],
                "insight_type": "savings",
                "severity": "info",
                "message": f"Recommendation pending for {row['service_name']} → est. savings ${row['estimated_savings']:.2f}",
                "metadata": {"rec_id": row["rec_id"], "currency": row["currency"]}
            })

    # --------- 3. Idle Resources ---------
    idle = pd.read_sql("""
        SELECT r.resource_id, s.service_name, a.account_id, rs.service_id,
               AVG(u.metric_value) as avg_util, SUM(b.cost_amount) as cost
        FROM usage u
        JOIN resources r ON u.resource_id = r.resource_id
        JOIN accounts a ON r.account_id = a.account_id
        JOIN services s ON r.service_id = s.service_id
        JOIN billing b ON r.resource_id = b.resource_id
        WHERE u.collected_at >= NOW() - INTERVAL '30 days'
        GROUP BY r.resource_id, s.service_name, a.account_id, rs.service_id
    """, conn)

    if not idle.empty:
        for _, row in idle.iterrows():
            if (row["avg_util"] or 0) < 1 and (row["cost"] or 0) > 10:
                insights.append({
                    "account_id": row["account_id"],
                    "service_id": row["service_id"],
                    "insight_type": "idle",
                    "severity": "critical",
                    "message": f"Idle {row['service_name']} resource incurring ${row['cost']:.2f}",
                    "metadata": {"resource_id": row["resource_id"], "avg_util": float(row["avg_util"] or 0)}
                })

    # --------- 4. Forecast vs Budget Gap ---------
    gaps = pd.read_sql("""
        SELECT f.account_id, f.service_id, f.forecast_amount, f.confidence_interval,
               b.budget_limit, a.account_name, s.service_name
        FROM forecasts f
        JOIN budgets b ON f.account_id = b.account_id AND (f.service_id = b.service_id OR b.service_id IS NULL)
        JOIN accounts a ON f.account_id = a.account_id
        JOIN services s ON f.service_id = s.service_id
        WHERE f.forecast_period_end >= CURRENT_DATE + INTERVAL '30 days'
    """, conn)

    if not gaps.empty:
        for _, row in gaps.iterrows():
            if row["forecast_amount"] > float(row["budget_limit"]):
                insights.append({
                    "account_id": row["account_id"],
                    "service_id": row["service_id"],
                    "insight_type": "forecast_gap",
                    "severity": "high",
                    "message": f"Forecasted spend {row['service_name']} exceeds budget by ${(row['forecast_amount'] - float(row['budget_limit'])):.2f}",
                    "metadata": {"forecast": row["forecast_amount"], "budget": float(row["budget_limit"])}
                })

    # --------- Insert into DB ---------
    for i in insights:
        cursor.execute("""
            INSERT INTO insights (account_id, service_id, insight_type, severity, message, metadata)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            i["account_id"],
            i["service_id"],
            i["insight_type"],
            i["severity"],
            i["message"],
            json.dumps(i["metadata"])
        ))
    conn.commit()
    cursor.close()
    conn.close()

    # --------- Notifications ---------
    if insights:
        lines = ["🤖 AI Insights Generated:"]
        for i in insights[:10]:
            lines.append(f"- {i['severity'].upper()} | {i['message']}")
        notify("\n".join(lines))
    else:
        notify("ℹ️ No new AI insights generated.")

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
    dag_id="ai_insights",
    default_args=default_args,
    description="Daily AI-powered FinOps insights (trend, savings, idle, forecast_gap)",
    schedule_interval="0 11 * * *",  # daily at 11 AM UTC
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["finops", "ai", "insights"],
) as dag:

    generate = PythonOperator(
        task_id="generate_insights",
        python_callable=generate_insights,
    )
