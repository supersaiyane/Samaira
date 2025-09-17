from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import psycopg2
import os
import boto3
import json
from app.services.finops_metrics import record_idle_resource_cost

record_idle_resource_cost(resource_name, wasted_cost)

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
# AWS Pricing Helpers
# =========================
def get_ec2_price(instance_type, region="US East (N. Virginia)"):
    pricing = boto3.client("pricing", region_name="us-east-1")
    response = pricing.get_products(
        ServiceCode="AmazonEC2",
        Filters=[
            {"Type": "TERM_MATCH", "Field": "instanceType", "Value": instance_type},
            {"Type": "TERM_MATCH", "Field": "location", "Value": region},
            {"Type": "TERM_MATCH", "Field": "operatingSystem", "Value": "Linux"},
            {"Type": "TERM_MATCH", "Field": "tenancy", "Value": "Shared"},
            {"Type": "TERM_MATCH", "Field": "preInstalledSw", "Value": "NA"},
        ],
        MaxResults=1,
    )
    if not response["PriceList"]:
        return None
    price_item = json.loads(response["PriceList"][0])
    on_demand = list(price_item["terms"]["OnDemand"].values())[0]
    price_dimensions = list(on_demand["priceDimensions"].values())[0]
    return float(price_dimensions["pricePerUnit"]["USD"])

def get_fargate_price(vcpu, memory_gb, region="US East (N. Virginia)"):
    """Return ECS Fargate hourly price for vCPU/memory combo"""
    pricing = boto3.client("pricing", region_name="us-east-1")
    response = pricing.get_products(
        ServiceCode="AmazonECS",
        Filters=[{"Type": "TERM_MATCH", "Field": "location", "Value": region}],
        MaxResults=100,
    )
    for item in response["PriceList"]:
        price_item = json.loads(item)
        for term in price_item["terms"]["OnDemand"].values():
            for dim in term["priceDimensions"].values():
                desc = dim["description"].lower()
                if f"{vcpu} vcpu" in desc and f"{int(memory_gb)} gb" in desc:
                    return float(dim["pricePerUnit"]["USD"])
    return None

def get_lambda_prices(region="US East (N. Virginia)"):
    """Return Lambda per-request and per-GB-second prices"""
    # Requests are globally consistent
    request_price = 0.20 / 1_000_000  # $0.20 per 1M
    # GB-sec via Pricing API
    pricing = boto3.client("pricing", region_name="us-east-1")
    response = pricing.get_products(
        ServiceCode="AWSLambda",
        Filters=[{"Type": "TERM_MATCH", "Field": "location", "Value": region}],
        MaxResults=1,
    )
    price_item = json.loads(response["PriceList"][0])
    on_demand = list(price_item["terms"]["OnDemand"].values())[0]
    price_dimensions = list(on_demand["priceDimensions"].values())[0]
    gb_sec_price = float(price_dimensions["pricePerUnit"]["USD"])
    return request_price, gb_sec_price

# =========================
# Get Next Smaller EC2 Instance from DB
# =========================
def get_smaller_instance(conn, instance_type):
    if "." not in instance_type:
        return None
    family, size = instance_type.split(".", 1)

    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT size FROM instance_catalog
        WHERE family = %s
        ORDER BY last_updated DESC
        """,
        (family,),
    )
    sizes = [row[0] for row in cursor.fetchall()]
    cursor.close()

    if size not in sizes:
        return None
    idx = sizes.index(size)
    return f"{family}.{sizes[idx+1]}" if idx+1 < len(sizes) else None

# =========================
# Analyze Rightsizing & Idle Detection
# =========================
def analyze_rightsizing():
    conn = get_db_connection()
    cursor = conn.cursor()

    # ========== EC2 ==========
    cursor.execute("""
        SELECT r.resource_id, r.resource_name, r.resource_type, r.region,
               AVG(u.metric_value) as avg_cpu
        FROM usage u
        JOIN resources r ON u.resource_id = r.resource_id
        JOIN services s ON r.service_id = s.service_id
        WHERE u.metric_name = 'CPUUtilization'
          AND u.collected_at >= NOW() - INTERVAL '14 days'
          AND s.service_name = 'EC2'
        GROUP BY r.resource_id, r.resource_name, r.resource_type, r.region
    """)
    for resource_id, resource_name, instance_type, region, avg_cpu in cursor.fetchall():
        if not instance_type:
            continue
        current_price = get_ec2_price(instance_type)
        if not current_price:
            continue
        monthly_cost = current_price * 730
        if avg_cpu < 5:
            rec_type, recommended, est_savings = "Idle", {"action": "stop"}, monthly_cost
        elif avg_cpu < 20:
            recommended_type = get_smaller_instance(conn, instance_type)
            if not recommended_type:
                continue
            new_price = get_ec2_price(recommended_type)
            if not new_price:
                continue
            est_savings = (current_price - new_price) * 730
            rec_type, recommended = "Rightsize", {"recommend": recommended_type}
        else:
            continue
        cursor.execute("""
            INSERT INTO recommendations (resource_id, rec_type, current_config, recommended_config, estimated_savings, status)
            VALUES (%s, %s, %s, %s, %s, 'pending')
            ON CONFLICT DO NOTHING;
        """, (
            resource_id,
            rec_type,
            {"avg_cpu": float(avg_cpu), "instance_type": instance_type, "service": "EC2"},
            recommended,
            est_savings,
        ))

    # ========== ECS (Fargate) ==========
    cursor.execute("""
        SELECT r.resource_id, r.resource_name,
               AVG(CASE WHEN u.metric_name='CPUUtilization' THEN u.metric_value END) as avg_cpu,
               AVG(CASE WHEN u.metric_name='MemoryUtilization' THEN u.metric_value END) as avg_mem
        FROM usage u
        JOIN resources r ON u.resource_id = r.resource_id
        JOIN services s ON r.service_id = s.service_id
        WHERE u.collected_at >= NOW() - INTERVAL '14 days'
          AND s.service_name = 'ECS'
        GROUP BY r.resource_id, r.resource_name
    """)
    for resource_id, resource_name, avg_cpu, avg_mem in cursor.fetchall():
        vcpu, mem = 1, 2  # TODO: extract from resource metadata
        current_price = get_fargate_price(vcpu, mem)
        new_price = get_fargate_price(0.5, 1)
        monthly_cost = current_price * 730 if current_price else 0
        if (avg_cpu or 0) < 5 and (avg_mem or 0) < 5:
            rec_type, recommended, est_savings = "Idle", {"action": "scale_to_zero"}, monthly_cost
        elif (avg_cpu or 0) < 30 or (avg_mem or 0) < 30:
            est_savings = (current_price - new_price) * 730 if current_price and new_price else 0
            rec_type, recommended = "Rightsize", {"recommend": "smaller_task_size"}
        else:
            continue
        cursor.execute("""
            INSERT INTO recommendations (resource_id, rec_type, current_config, recommended_config, estimated_savings, status)
            VALUES (%s, %s, %s, %s, %s, 'pending')
            ON CONFLICT DO NOTHING;
        """, (
            resource_id,
            rec_type,
            {"avg_cpu": float(avg_cpu or 0), "avg_mem": float(avg_mem or 0), "service": "ECS"},
            recommended,
            est_savings,
        ))

    # ========== EKS (nodes = EC2) ==========
    cursor.execute("""
        SELECT r.resource_id, r.resource_name, r.resource_type, r.region,
               AVG(CASE WHEN u.metric_name='node_cpu_utilization' THEN u.metric_value END) as avg_cpu,
               AVG(CASE WHEN u.metric_name='node_memory_utilization' THEN u.metric_value END) as avg_mem
        FROM usage u
        JOIN resources r ON u.resource_id = r.resource_id
        JOIN services s ON r.service_id = s.service_id
        WHERE u.collected_at >= NOW() - INTERVAL '14 days'
          AND s.service_name = 'EKS'
        GROUP BY r.resource_id, r.resource_name, r.resource_type, r.region
    """)
    for resource_id, resource_name, instance_type, region, avg_cpu, avg_mem in cursor.fetchall():
        current_price = get_ec2_price(instance_type)
        monthly_cost = current_price * 730 if current_price else 0
        if (avg_cpu or 0) < 5 and (avg_mem or 0) < 5:
            rec_type, recommended, est_savings = "Idle", {"action": "scale_down_node"}, monthly_cost
        elif (avg_cpu or 0) < 20 or (avg_mem or 0) < 30:
            recommended_type = get_smaller_instance(conn, instance_type)
            if not recommended_type:
                continue
            new_price = get_ec2_price(recommended_type)
            est_savings = (current_price - new_price) * 730 if current_price and new_price else 0
            rec_type, recommended = "Rightsize", {"recommend": recommended_type}
        else:
            continue
        cursor.execute("""
            INSERT INTO recommendations (resource_id, rec_type, current_config, recommended_config, estimated_savings, status)
            VALUES (%s, %s, %s, %s, %s, 'pending')
            ON CONFLICT DO NOTHING;
        """, (
            resource_id,
            rec_type,
            {"avg_cpu": float(avg_cpu or 0), "avg_mem": float(avg_mem or 0), "service": "EKS"},
            recommended,
            est_savings,
        ))

    # ========== Lambda ==========
    cursor.execute("""
        SELECT r.resource_id, r.resource_name,
               SUM(CASE WHEN u.metric_name='Invocations' THEN u.metric_value ELSE 0 END) as total_invocations,
               AVG(CASE WHEN u.metric_name='Duration' THEN u.metric_value ELSE 0 END) as avg_duration
        FROM usage u
        JOIN resources r ON u.resource_id = r.resource_id
        JOIN services s ON r.service_id = s.service_id
        WHERE u.collected_at >= NOW() - INTERVAL '30 days'
          AND s.service_name = 'Lambda'
        GROUP BY r.resource_id, r.resource_name
    """)
    req_price, gb_sec_price = get_lambda_prices()
    for resource_id, resource_name, total_invocations, avg_duration in cursor.fetchall():
        if not total_invocations:
            continue
        # Example: assume 128MB memory allocation
        monthly_cost = (total_invocations * (avg_duration/1000) * 0.128 * gb_sec_price) + (total_invocations * req_price)
        if total_invocations == 0:
            rec_type, recommended, est_savings = "Idle", {"action": "delete_function"}, monthly_cost
        elif avg_duration > 5000:  # >5s
            rec_type, recommended, est_savings = "Rightsize", {"recommend": "adjust_memory_allocation"}, monthly_cost * 0.2
        else:
            continue
        cursor.execute("""
            INSERT INTO recommendations (resource_id, rec_type, current_config, recommended_config, estimated_savings, status)
            VALUES (%s, %s, %s, %s, %s, 'pending')
            ON CONFLICT DO NOTHING;
        """, (
            resource_id,
            rec_type,
            {"invocations": int(total_invocations or 0), "avg_duration": float(avg_duration or 0), "service": "Lambda"},
            recommended,
            est_savings,
        ))

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
    dag_id="rightsizing",
    default_args=default_args,
    description="Multi-service rightsizing & idle detection (EC2/EKS/ECS/Lambda w/ Pricing API)",
    schedule_interval="0 4 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["finops", "rightsizing", "idle-detection"],
) as dag:

    analyze = PythonOperator(
        task_id="analyze_rightsizing",
        python_callable=analyze_rightsizing,
    )
