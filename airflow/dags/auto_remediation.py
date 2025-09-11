from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import requests
import json
import boto3
import psycopg2
import yaml
import glob
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
# Slack/Teams Notifiers
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
            "title": "⚡ Auto-Remediation Executed",
            "text": message,
        }
        requests.post(teams_url, json=payload)

# =========================
# Load Playbooks
# =========================
def load_playbooks():
    playbooks = {}
    for file in glob.glob("airflow/playbooks/*.yaml"):
        with open(file, "r") as f:
            pb = yaml.safe_load(f)
            key = (pb["issue"], pb["service"])
            playbooks[key] = pb
    return playbooks

# =========================
# Execute Playbook
# =========================
def execute_playbook(pb, details):
    api = pb["params"]["api"]
    method = pb["params"]["method"]
    args = pb["params"]["args"]

    # Replace placeholders
    resolved_args = {}
    for k, v in args.items():
        if isinstance(v, str) and v.startswith("{{") and v.endswith("}}"):
            key = v.strip("{} ").strip()
            resolved_args[k] = details.get(key)
        else:
            resolved_args[k] = v

    if pb["action"] == "notify_only":
        return pb["params"].get("message", "Notification only")

    if api == "ec2":
        client = boto3.client("ec2", region_name=os.getenv("AWS_REGION", "us-east-1"))
    elif api == "lambda":
        client = boto3.client("lambda", region_name=os.getenv("AWS_REGION", "us-east-1"))
    else:
        raise ValueError(f"Unsupported API: {api}")

    getattr(client, method)(**resolved_args)
    return f"Executed {pb['action']} on {pb['service']} with {resolved_args}"

# =========================
# Remediation Logic
# =========================
def remediate_anomalies():
    conn = get_db_connection()
    cursor = conn.cursor()
    playbooks = load_playbooks()

    cursor.execute("""
        SELECT anomaly_id, account_id, service_id, metric, details
        FROM anomalies
        WHERE status = 'open'
    """)
    anomalies = cursor.fetchall()

    for anomaly_id, account_id, service_id, metric, details in anomalies:
        try:
            # Ensure JSON details
            if isinstance(details, str):
                details = json.loads(details)
            details = details or {}

            issue = details.get("issue")
            service = details.get("service")

            action_taken = None

            # Find matching playbook
            pb = playbooks.get((issue, service))
            if pb:
                action_taken = execute_playbook(pb, details)
            else:
                action_taken = f"No playbook found for {issue}/{service}"

            # Update anomaly status
            new_status = "remediated" if "Executed" in action_taken else "ignored"
            cursor.execute(
                "UPDATE anomalies SET status = %s WHERE anomaly_id = %s",
                (new_status, anomaly_id),
            )

            # Insert into logs table
            cursor.execute("""
                INSERT INTO logs (timestamp, level, component, message, correlation_id, extra)
                VALUES (NOW(), %s, %s, %s, %s, %s)
            """, (
                "INFO" if new_status == "remediated" else "WARN",
                "auto-remediation",
                action_taken,
                str(uuid.uuid4()),
                json.dumps({"anomaly_id": anomaly_id, "details": details})
            ))

            notify(f"⚡ {action_taken}")
            conn.commit()

        except Exception as e:
            cursor.execute("""
                UPDATE anomalies SET status = 'error' WHERE anomaly_id = %s
            """, (anomaly_id,))
            conn.commit()
            notify(f"❌ Error remediating anomaly {anomaly_id}: {e}")

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
    dag_id="auto_remediation",
    default_args=default_args,
    description="Auto-remediate anomalies using pluggable playbooks",
    schedule_interval="0 8 * * *",  # daily at 8 AM UTC
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["finops", "auto-remediation"],
) as dag:

    remediate = PythonOperator(
        task_id="remediate_anomalies",
        python_callable=remediate_anomalies,
    )
