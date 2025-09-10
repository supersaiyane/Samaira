from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import requests
import json
import boto3
import psycopg2

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


import yaml
import glob

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

    # Replace placeholders (e.g., {{ resource_id }})
    resolved_args = {}
    for k, v in args.items():
        if isinstance(v, str) and v.startswith("{{") and v.endswith("}}"):
            key = v.strip("{} ").strip()
            resolved_args[k] = details.get(key)
        else:
            resolved_args[k] = v

    if pb["action"] == "notify_only":
        return pb["params"]["message"]

    if api == "ec2":
        client = boto3.client("ec2", region_name=os.getenv("AWS_REGION", "us-east-1"))
    elif api == "lambda":
        client = boto3.client("lambda", region_name=os.getenv("AWS_REGION", "us-east-1"))
    else:
        raise ValueError(f"Unsupported API: {api}")

    getattr(client, method)(**resolved_args)
    return f"Executed {pb['action']} on {pb['service']} with {resolved_args}"


# =========================
# AWS Clients
# =========================
ec2 = boto3.client("ec2", region_name=os.getenv("AWS_REGION", "us-east-1"))
lambda_client = boto3.client("lambda", region_name=os.getenv("AWS_REGION", "us-east-1"))

# =========================
# Remediation Logic
# =========================
def remediate_anomalies():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT anomaly_id, account_id, service_id, metric, details
        FROM anomalies
        WHERE status IS NULL OR status = 'unresolved'
    """)
    anomalies = cursor.fetchall()

    for anomaly_id, account_id, service_id, metric, details in anomalies:
        action_taken = None
        details = details if isinstance(details, dict) else {}

        # Example playbooks
        if details.get("issue") == "Idle Resource":
            # Stop EC2 instance
            instance_id = details.get("resource_id")
            if instance_id:
                ec2.stop_instances(InstanceIds=[instance_id])
                action_taken = f"Stopped idle EC2 instance {instance_id}"

        elif details.get("issue") == "Lambda Inactivity":
            # Delete unused Lambda
            fn_name = details.get("function_name")
            if fn_name:
                lambda_client.delete_function(FunctionName=fn_name)
                action_taken = f"Deleted idle Lambda function {fn_name}"

        elif details.get("issue") == "Budget Breach":
            action_taken = "Budget breach - no auto action, CFO notified"

        elif details.get("issue") == "Forecast Drift":
            action_taken = "Forecast drift - flagged to FinOps team"

        # Update DB
        cursor.execute("""
            UPDATE anomalies
            SET status = %s
            WHERE anomaly_id = %s
        """, ("remediated" if action_taken else "ignored", anomaly_id))

        if action_taken:
            notify(f"✅ Auto-remediation: {action_taken}")
        else:
            notify(f"⚠️ No remediation applied for anomaly {anomaly_id}")

    conn.commit()
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
    description="Auto-remediate anomalies from anomaly_detection_v3",
    schedule_interval="0 8 * * *",  # daily at 8 AM UTC (after anomaly detection at 7)
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["finops", "auto-remediation"],
) as dag:

    remediate = PythonOperator(
        task_id="remediate_anomalies",
        python_callable=remediate_anomalies,
    )
