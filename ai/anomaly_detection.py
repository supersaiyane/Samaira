from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import psycopg2
import os
import requests
import json
import pandas as pd
import statistics

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
def send_slack_message(blocks):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        return
    payload = {"blocks": blocks}
    requests.post(webhook_url, data=json.dumps(payload), headers={"Content-Type": "application/json"})

def send_teams_message(message):
    webhook_url = os.getenv("TEAMS_WEBHOOK_URL")
    if not webhook_url:
        return
    payload = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "summary": "FinOps Anomaly Alert",
        "themeColor": "FF0000",
        "title": "🚨 FinOps Anomaly Report",
        "text": message,
    }
    requests.post(webhook_url, data=json.dumps(payload), headers={"Content-Type": "application/json"})

def notify(anomalies):
    if not anomalies:
        send_slack_message([{"type": "section", "text": {"type": "mrkdwn", "text": "✅ No anomalies detected"}}])
        send_teams_message("✅ No anomalies detected")
        return

    # Slack block kit
    blocks = [{"type": "header", "text": {"type": "plain_text", "text": "🚨 FinOps Anomalies Detected"}}]
    for a in anomalies[:10]:  # top 10
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn",
                     "text": f"*{a['severity'].upper()}* | {a['account']} / {a['service']}\n"
                             f"{a['issue']} → Observed: {a['observed']} Expected: {a.get('expected', '-')}"}
        })
    send_slack_message(blocks)

    # Teams fallback
    msg = "\n".join([f"- [{a['severity'].upper()}] {a['account']} / {a['service']}: {a['issue']}" for a in anomalies])
    send_teams_message(msg)

# =========================
# Severity Scoring
# =========================
def classify_severity(deviation, abs_diff, service_criticality="medium"):
    if abs_diff < 10:
        return "low"
    if abs_diff > 1000 or abs(deviation) > 200 or service_criticality == "high":
        return "high"
    return "medium"

# =========================
# Anomaly Detection Logic
# =========================
def detect_anomalies():
    conn = get_db_connection()

    # Pull billing (last 31 days), usage, budgets, forecasts into DataFrames
    billing = pd.read_sql("""
        SELECT b.account_id, a.account_name, b.service_id, s.service_name, b.usage_date, SUM(b.cost_amount) as cost
        FROM billing b
        JOIN accounts a ON b.account_id = a.account_id
        JOIN services s ON b.service_id = s.service_id
        WHERE usage_date >= CURRENT_DATE - INTERVAL '31 days'
        GROUP BY b.account_id, a.account_name, b.service_id, s.service_name, b.usage_date
    """, conn)

    usage = pd.read_sql("""
        SELECT r.resource_id, a.account_name, s.service_name, u.metric_name, AVG(u.metric_value) as value
        FROM usage u
        JOIN resources r ON u.resource_id = r.resource_id
        JOIN accounts a ON r.account_id = a.account_id
        JOIN services s ON r.service_id = s.service_id
        WHERE u.collected_at >= NOW() - INTERVAL '7 days'
        GROUP BY r.resource_id, a.account_name, s.service_name, u.metric_name
    """, conn)

    budgets = pd.read_sql("SELECT account_id, budget_limit FROM budgets", conn)
    forecasts = pd.read_sql("SELECT * FROM forecasts WHERE forecast_period_end >= CURRENT_DATE", conn)

    anomalies = []

    # ---------- Cost Anomalies ----------
    for (acct, svc), group in billing.groupby(["account_name", "service_name"]):
        if len(group) < 8:
            continue
        yesterday = group[group["usage_date"] == group["usage_date"].max()]
        hist = group[group["usage_date"] < group["usage_date"].max()]["cost"].tolist()
        if not yesterday.empty:
            obs = yesterday["cost"].iloc[0]
            avg = statistics.mean(hist)
            stddev = statistics.pstdev(hist)
            deviation = ((obs - avg) / avg) * 100 if avg > 0 else 0
            if abs(deviation) > float(os.getenv("ANOMALY_THRESHOLD", "50")) and (stddev == 0 or abs(obs - avg) > 2 * stddev):
                severity = classify_severity(deviation, abs(obs - avg))
                anomalies.append({"account": acct, "service": svc, "issue": "Cost Spike",
                                  "observed": f"${obs:.2f}", "expected": f"${avg:.2f}", "severity": severity})

    # ---------- Usage Anomalies ----------
    for _, row in usage.iterrows():
        if row["metric_name"] in ["CPUUtilization", "node_cpu_utilization"] and row["value"] > 90:
            anomalies.append({"account": row["account_name"], "service": row["service_name"],
                              "issue": "High CPU", "observed": f"{row['value']:.1f}%", "severity": "high"})
        if row["metric_name"] in ["MemoryUtilization", "node_memory_utilization"] and row["value"] > 85:
            anomalies.append({"account": row["account_name"], "service": row["service_name"],
                              "issue": "High Memory", "observed": f"{row['value']:.1f}%", "severity": "high"})
        if row["metric_name"] == "Invocations" and row["value"] == 0:
            anomalies.append({"account": row["account_name"], "service": row["service_name"],
                              "issue": "Lambda Inactivity", "observed": "0 invocations", "severity": "medium"})

    # ---------- Idle/Orphan Resources ----------
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.resource_id, a.account_name, s.service_name, SUM(b.cost_amount) as cost
        FROM billing b
        JOIN resources r ON b.resource_id = r.resource_id
        JOIN accounts a ON r.account_id = a.account_id
        JOIN services s ON r.service_id = s.service_id
        WHERE b.usage_date >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY r.resource_id, a.account_name, s.service_name
    """)
    for rid, acct, svc, cost in cursor.fetchall():
        cursor.execute("SELECT AVG(metric_value) FROM usage WHERE resource_id=%s", (rid,))
        avg_usage = cursor.fetchone()[0] or 0
        if cost > 10 and avg_usage < 1:
            anomalies.append({"account": acct, "service": svc, "issue": "Idle Resource",
                              "observed": f"${cost:.2f}", "severity": "medium"})

    # ---------- Budget Breaches ----------
    for _, row in budgets.iterrows():
        acct_id = row["account_id"]
        limit = row["budget_limit"]
        mtd = billing[billing["account_id"] == acct_id]["cost"].sum()
        if mtd > limit:
            anomalies.append({"account": acct_id, "service": "ALL",
                              "issue": "Budget Breach", "observed": f"${mtd:.2f}", "expected": f"${limit:.2f}", "severity": "high"})

    # ---------- Forecast Drift ----------
    for _, row in forecasts.iterrows():
        acct = row["account_id"]
        svc = row["service_id"]
        forecast = row["forecast_amount"]
        ci = row["confidence_interval"]
        actual = billing[(billing["account_id"] == acct) & (billing["service_id"] == svc)]["cost"].sum()
        if ci and (actual > ci["upper"] or actual < ci["lower"]):
            anomalies.append({"account": acct, "service": svc, "issue": "Forecast Drift",
                              "observed": f"${actual:.2f}", "expected": f"${forecast:.2f}", "severity": "high"})

    conn.close()

    notify(anomalies)

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
    dag_id="anomaly_detection_v2",
    default_args=default_args,
    description="Refined anomaly detection (cost, usage, idle, budget, forecast) with severity & alerts",
    schedule_interval="0 7 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["finops", "anomaly", "v2"],
) as dag:

    detect = PythonOperator(
        task_id="detect_anomalies",
        python_callable=detect_anomalies,
    )
