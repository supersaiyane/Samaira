from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import boto3, psycopg2, os

def update_ec2_utilization():
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME", "finopsdb"),
        user=os.getenv("DB_USER", "finops"),
        password=os.getenv("DB_PASSWORD", "finops123"),
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", "5432"),
    )
    cur = conn.cursor()

    cloudwatch = boto3.client(
        "cloudwatch",
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

    cur.execute("SELECT instance_id, instance_name, region FROM ec2_instances WHERE status='running'")
    for row in cur.fetchall():
        instance_id, name, region = row

        metric = cloudwatch.get_metric_statistics(
            Namespace="AWS/EC2",
            MetricName="CPUUtilization",
            Dimensions=[{"Name": "InstanceId", "Value": name}],
            StartTime=datetime.utcnow() - timedelta(hours=1),
            EndTime=datetime.utcnow(),
            Period=300,
            Statistics=["Average"],
        )

        avg_util = metric["Datapoints"][0]["Average"] if metric["Datapoints"] else 0.0
        cur.execute("UPDATE ec2_instances SET utilization=%s WHERE instance_id=%s", (avg_util, instance_id))

    conn.commit()
    cur.close()
    conn.close()

with DAG(
    "update_ec2_utilization",
    default_args={"retries": 1, "retry_delay": timedelta(minutes=5)},
    schedule_interval="0 * * * *",  # every hour
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:

    update_task = PythonOperator(
        task_id="update_ec2_utilization",
        python_callable=update_ec2_utilization,
    )
