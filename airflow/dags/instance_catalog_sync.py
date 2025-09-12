from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import boto3, os, json, psycopg2

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "finopsdb"),
        user=os.getenv("DB_USER", "finops"),
        password=os.getenv("DB_PASSWORD", "finops123"),
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", "5432"),
    )

def update_instance_catalog():
    pricing = boto3.client("pricing", region_name="us-east-1")
    conn = get_db_connection()
    cursor = conn.cursor()

    paginator = pricing.get_paginator("get_products")
    for page in paginator.paginate(ServiceCode="AmazonEC2", Filters=[
        {"Type": "TERM_MATCH", "Field": "operatingSystem", "Value": "Linux"},
        {"Type": "TERM_MATCH", "Field": "tenancy", "Value": "Shared"},
        {"Type": "TERM_MATCH", "Field": "preInstalledSw", "Value": "NA"},
    ]):
        for item in page["PriceList"]:
            data = json.loads(item)
            attrs = data["product"]["attributes"]
            instance_type = attrs.get("instanceType")
            vcpu = attrs.get("vcpu")
            memory = attrs.get("memory")
            region = attrs.get("location")

            terms = list(data["terms"]["OnDemand"].values())
            if not terms: 
                continue
            price_dimensions = list(terms[0]["priceDimensions"].values())[0]
            price_per_hour = float(price_dimensions["pricePerUnit"]["USD"])

            cursor.execute("""
                INSERT INTO instance_catalog (family, size, vcpu, memory_gb, region, price_per_hour, last_updated)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (family, size, region) DO UPDATE
                SET vcpu=EXCLUDED.vcpu, memory_gb=EXCLUDED.memory_gb,
                    price_per_hour=EXCLUDED.price_per_hour, last_updated=NOW()
            """, (
                instance_type.split(".")[0],
                instance_type.split(".")[1],
                int(vcpu) if vcpu else None,
                float(memory.split()[0]) if memory else None,
                region,
                price_per_hour
            ))

    conn.commit()
    cursor.close()
    conn.close()

default_args = {"owner": "finops", "retries": 1, "retry_delay": timedelta(minutes=10)}

with DAG(
    dag_id="update_instance_catalog",
    default_args=default_args,
    description="Weekly sync of EC2 instance catalog from AWS Pricing API",
    schedule_interval="0 2 * * 0",  # Sunday 2 AM
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:
    sync = PythonOperator(task_id="update_catalog", python_callable=update_instance_catalog)
