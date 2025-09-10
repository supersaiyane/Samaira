from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import boto3
import psycopg2
import os

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
# Get or Create Resource Mapping
# =========================
def get_or_create_resource(conn, account_id, service, dimension_name, dimension_value, region="us-east-1"):
    cursor = conn.cursor()

    # Ensure service exists or log to unmapped
    service_id = ensure_service_in_db(service)

    cursor.execute(
        """
        SELECT resource_id FROM resources
        WHERE resource_name=%s AND account_id=%s
        """,
        (dimension_value, account_id),
    )
    result = cursor.fetchone()

    if result:
        resource_id = result[0]
    else:
        cursor.execute(
            """
            INSERT INTO resources (account_id, service_id, resource_name, region, resource_type)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING resource_id
            """,
            (account_id, service_id, dimension_value, region, dimension_name),
        )
        resource_id = cursor.fetchone()[0]
        conn.commit()

    cursor.close()
    return resource_id

# =========================
# Fetch CloudWatch Metrics
# =========================
def fetch_usage_data(**context):
    client = boto3.client("cloudwatch", region_name=os.getenv("AWS_REGION", "us-east-1"))
    backfill_months = int(os.getenv("BACKFILL_MONTHS", "18"))
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=30 * backfill_months)

    # Define metrics for EC2, EKS, ECS, Lambda
    metrics_to_collect = [
        {"Service": "EC2", "Namespace": "AWS/EC2", "MetricName": "CPUUtilization", "Unit": "Percent", "DimensionName": "InstanceId", "DimensionValue": os.getenv("TEST_INSTANCE_ID", "i-123")},
        {"Service": "EKS", "Namespace": "ContainerInsights", "MetricName": "node_cpu_utilization", "Unit": "Percent", "DimensionName": "ClusterName", "DimensionValue": os.getenv("TEST_EKS_CLUSTER", "eks-cluster")},
        {"Service": "ECS", "Namespace": "AWS/ECS", "MetricName": "CPUUtilization", "Unit": "Percent", "DimensionName": "ClusterName", "DimensionValue": os.getenv("TEST_ECS_CLUSTER", "ecs-cluster")},
        {"Service": "Lambda", "Namespace": "AWS/Lambda", "MetricName": "Duration", "Unit": "Milliseconds", "DimensionName": "FunctionName", "DimensionValue": os.getenv("TEST_LAMBDA_FUNCTION", "lambda-func")},
    ]

    conn = get_db_connection()
    records = []

    for metric in metrics_to_collect:
        try:
            response = client.get_metric_statistics(
                Namespace=metric["Namespace"],
                MetricName=metric["MetricName"],
                Dimensions=[{"Name": metric["DimensionName"], "Value": metric["DimensionValue"]}],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400 if backfill_months > 1 else 3600,
                Statistics=["Average"],
                Unit=metric["Unit"],
            )

            # Map resource to resources table
            resource_id = get_or_create_resource(
                conn,
                account_id=1,  # TODO: map to correct account dynamically
                service=metric["Service"],
                dimension_name=metric["DimensionName"],
                dimension_value=metric["DimensionValue"],
                region=os.getenv("AWS_REGION", "us-east-1"),
            )

            for datapoint in response["Datapoints"]:
                records.append(
                    {
                        "resource_id": resource_id,
                        "metric_name": metric["MetricName"],
                        "metric_value": datapoint["Average"],
                        "unit": metric["Unit"],
                        "collected_at": datapoint["Timestamp"],
                        "namespace": metric["Namespace"],
                        "dimension": metric["DimensionValue"],
                    }
                )
        except Exception as e:
            print(f"⚠️ Error fetching {metric['MetricName']} from {metric['Namespace']}: {e}")

    conn.close()
    context["ti"].xcom_push(key="usage_records", value=records)

# =========================
# Load into PostgreSQL
# =========================
def load_usage_data(**context):
    records = context["ti"].xcom_pull(key="usage_records", task_ids="fetch_usage")
    if not records:
        print("⚠️ No usage records found.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    for row in records:
        cursor.execute(
            """
            INSERT INTO usage (resource_id, metric_name, metric_value, unit, collected_at, metadata)
            VALUES (%s, %s, %s, %s, %s, %s);
            """,
            (
                row["resource_id"],
                row["metric_name"],
                row["metric_value"],
                row["unit"],
                row["collected_at"],
                {"namespace": row["namespace"], "dimension": row["dimension"]},
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
    dag_id="usage_ingest",
    default_args=default_args,
    description="Ingest AWS usage metrics (EC2, EKS, ECS, Lambda) with resource mapping and unmapped services tracking",
    schedule_interval="0 */6 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["finops", "usage", "aws"],
) as dag:

    fetch_usage = PythonOperator(
        task_id="fetch_usage",
        python_callable=fetch_usage_data,
        provide_context=True,
    )

    load_usage = PythonOperator(
        task_id="load_usage",
        python_callable=load_usage_data,
        provide_context=True,
    )

    fetch_usage >> load_usage
