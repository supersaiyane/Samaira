from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import boto3
import psycopg2
import os
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
# Ensure Account in DB
# =========================
def ensure_account_in_db(account_id, account_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO accounts (cloud_provider, account_number, account_name)
        VALUES (%s, %s, %s)
        ON CONFLICT (account_number) DO NOTHING;
        """,
        ("AWS", account_id, account_name),
    )
    conn.commit()
    cursor.close()
    conn.close()

# =========================
# Ensure Service in DB or log to unmapped_services
# =========================
def ensure_service_in_db(service_name, service_code=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT service_id FROM services WHERE service_name=%s AND cloud_provider='AWS'",
        (service_name,),
    )
    result = cursor.fetchone()

    if result:
        service_id = result[0]
    else:
        # Unknown service → log in unmapped_services
        cursor.execute(
            """
            INSERT INTO unmapped_services (cloud_provider, service_name, first_seen, last_seen)
            VALUES (%s, %s, NOW(), NOW())
            ON CONFLICT (cloud_provider, service_name)
            DO UPDATE SET last_seen = NOW();
            """,
            ("AWS", service_name),
        )
        service_id = None

    conn.commit()
    cursor.close()
    conn.close()
    return service_id

# =========================
# Fetch all linked accounts (AWS Orgs)
# =========================
def get_all_accounts():
    try:
        org_client = boto3.client(
            "organizations",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "us-east-1"),
        )
        accounts = []
        paginator = org_client.get_paginator("list_accounts")
        for page in paginator.paginate():
            for acct in page["Accounts"]:
                if acct["Status"] == "ACTIVE":
                    accounts.append({"Id": acct["Id"], "Name": acct["Name"]})
        return accounts
    except Exception as e:
        print(f"⚠️ Could not fetch AWS Organizations accounts: {e}")
        return []

# =========================
# Fetch Billing Data (Cost Explorer)
# =========================
def fetch_billing_data(**context):
    client = boto3.client(
        "ce",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION", "us-east-1"),
    )

    # Find last ingested date
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(usage_date) FROM billing;")
    last_date = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    # Backfill if no data, else continue from last_date
    if last_date:
        start_date = last_date
    else:
        start_date = datetime.utcnow() - timedelta(days=30 * 18)  # ~1.5 years
    end_date = datetime.utcnow()

    print(f"Fetching billing data from {start_date.date()} to {end_date.date()}")

    # Try to fetch all accounts (if Orgs is enabled)
    accounts = get_all_accounts()
    if not accounts:
        accounts = [{"Id": None, "Name": "Standalone"}]

    all_records = []

    for account in accounts:
        account_id = account["Id"]
        account_name = account["Name"]

        if account_id:
            ensure_account_in_db(account_id, account_name)

        print(f"🔹 Fetching billing for account {account_id} ({account_name})")

        response = client.get_cost_and_usage(
            TimePeriod={
                "Start": start_date.strftime("%Y-%m-%d"),
                "End": end_date.strftime("%Y-%m-%d"),
            },
            Granularity="DAILY",
            Metrics=["UnblendedCost", "UsageQuantity"],
            GroupBy=[
                {"Type": "DIMENSION", "Key": "SERVICE"},
                {"Type": "DIMENSION", "Key": "USAGE_TYPE"},
            ],
            Filter={"Dimensions": {"Key": "LINKED_ACCOUNT", "Values": [account_id]}}
            if account_id
            else None,
        )

        for result in response["ResultsByTime"]:
            usage_date = result["TimePeriod"]["Start"]
            for group in result["Groups"]:
                service = group["Keys"][0]
                usage_type = group["Keys"][1]
                amount = float(group["Metrics"]["UnblendedCost"]["Amount"])
                usage = float(group["Metrics"]["UsageQuantity"]["Amount"])

                all_records.append(
                    {
                        "account_id": account_id,
                        "account_name": account_name,
                        "usage_date": usage_date,
                        "service_name": service,
                        "usage_type": usage_type,
                        "cost_amount": amount,
                        "usage_quantity": usage,
                    }
                )

    if all_records:
        df = pd.DataFrame(all_records)
        context["ti"].xcom_push(key="billing_df", value=df.to_dict())
    else:
        print("⚠️ No billing data found.")

# =========================
# Insert Billing Data into PostgreSQL
# =========================
def load_billing_data(**context):
    data_dict = context["ti"].xcom_pull(key="billing_df", task_ids="fetch_billing")
    if not data_dict:
        print("⚠️ No data to load into billing table.")
        return

    df = pd.DataFrame.from_dict(data_dict)

    conn = get_db_connection()
    cursor = conn.cursor()

    for _, row in df.iterrows():
        service_id = ensure_service_in_db(row["service_name"])

        cursor.execute(
            """
            INSERT INTO billing (account_id, service_id, usage_date, cost_amount, usage_quantity, usage_type, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
            """,
            (
                row.get("account_id"),
                service_id,
                row["usage_date"],
                row["cost_amount"],
                row["usage_quantity"],
                row["usage_type"],
                {"service_name": row["service_name"], "account_name": row.get("account_name")},
            ),
        )

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
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="billing_ingest",
    default_args=default_args,
    description="Ingest AWS billing data (multi-account, normalized accounts/services, unmapped tracking, 1.5 years backfill) into PostgreSQL",
    schedule_interval="0 */6 * * *",   # every 6 hours
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["finops", "billing", "aws"],
) as dag:

    fetch_billing = PythonOperator(
        task_id="fetch_billing",
        python_callable=fetch_billing_data,
        provide_context=True,
    )

    load_billing = PythonOperator(
        task_id="load_billing",
        python_callable=load_billing_data,
        provide_context=True,
    )

    fetch_billing >> load_billing
