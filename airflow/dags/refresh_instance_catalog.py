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
# Refresh Instance Catalog
# =========================
def refresh_instance_catalog():
    ec2 = boto3.client("ec2", region_name=os.getenv("AWS_REGION", "us-east-1"))

    paginator = ec2.get_paginator("describe_instance_types")
    conn = get_db_connection()
    cursor = conn.cursor()

    for page in paginator.paginate():
        for itype in page["InstanceTypes"]:
            instance_type = itype["InstanceType"]               # e.g. m5.xlarge
            family, size = instance_type.split(".", 1)

            vcpu = itype["VCpuInfo"]["DefaultVCpus"]
            memory_gb = round(itype["MemoryInfo"]["SizeInMiB"] / 1024, 2)
            storage = (
                str(itype["InstanceStorageInfo"]["Disks"]) if "InstanceStorageInfo" in itype else "EBS Only"
            )
            network = itype.get("NetworkInfo", {}).get("NetworkPerformance", "Unknown")
            generation = itype.get("ProcessorInfo", {}).get("SupportedArchitectures", ["x86_64"])[0]
            baremetal = itype.get("BareMetal", False)
            gpu_count = (
                itype["GpuInfo"]["Gpus"][0]["Count"] if "GpuInfo" in itype else 0
            )

            cursor.execute(
                """
                INSERT INTO instance_catalog (instance_type, family, size, vcpu, memory_gb, storage, network_performance, generation, baremetal, gpu_count, last_updated)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (instance_type) DO UPDATE SET
                    vcpu = EXCLUDED.vcpu,
                    memory_gb = EXCLUDED.memory_gb,
                    storage = EXCLUDED.storage,
                    network_performance = EXCLUDED.network_performance,
                    generation = EXCLUDED.generation,
                    baremetal = EXCLUDED.baremetal,
                    gpu_count = EXCLUDED.gpu_count,
                    last_updated = NOW();
                """,
                (instance_type, family, size, vcpu, memory_gb, storage, network, generation, baremetal, gpu_count),
            )

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Instance catalog refreshed successfully")

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
    dag_id="refresh_instance_catalog",
    default_args=default_args,
    description="Refresh EC2 instance catalog (families, sizes, specs) into DB",
    schedule_interval="@daily",   # refresh daily
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["finops", "ec2", "catalog"],
) as dag:

    refresh_task = PythonOperator(
        task_id="refresh_instance_catalog_task",
        python_callable=refresh_instance_catalog,
    )

    refresh_task
