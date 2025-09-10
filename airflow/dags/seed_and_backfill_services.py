from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import psycopg2
import os
import json

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
# Seed Services from JSON
# =========================
def seed_services():
    conn = get_db_connection()
    cursor = conn.cursor()

    json_path = os.getenv("SERVICE_MAP_FILE", "/opt/airflow/data/aws-services-categorized.json")

    with open(json_path, "r") as f:
        data = json.load(f)

    for category, services in data.items():
        # Insert category if not exists
        cursor.execute(
            """
            INSERT INTO service_categories (category_name, description)
            VALUES (%s, %s)
            ON CONFLICT (category_name) DO NOTHING
            RETURNING category_id
            """,
            (category, f"AWS {category} services"),
        )
        result = cursor.fetchone()

        if result:
            category_id = result[0]
        else:
            cursor.execute(
                "SELECT category_id FROM service_categories WHERE category_name=%s",
                (category,),
            )
            category_id = cursor.fetchone()[0]

        # Insert services
        for svc in services:
            cursor.execute(
                """
                INSERT INTO services (cloud_provider, service_code, service_name, category_id)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (cloud_provider, service_code) DO NOTHING
                """,
                ("AWS", svc.replace(" ", ""), svc, category_id),
            )

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ AWS services + categories seeded successfully")

# =========================
# Backfill Service IDs
# =========================
def backfill_service_ids():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Find unmapped services that now exist in services
    cursor.execute(
        """
        SELECT u.id, u.service_name, s.service_id
        FROM unmapped_services u
        JOIN services s
        ON u.service_name = s.service_name
        WHERE s.cloud_provider = u.cloud_provider
        """
    )
    mappings = cursor.fetchall()

    for unmapped_id, service_name, service_id in mappings:
        print(f"🔹 Backfilling service {service_name} → service_id {service_id}")

        # Update resources
        cursor.execute(
            """
            UPDATE resources
            SET service_id = %s
            WHERE service_id IS NULL
            AND resource_name ILIKE %s
            """,
            (service_id, f"%{service_name}%"),
        )

        # Update billing
        cursor.execute(
            """
            UPDATE billing
            SET service_id = %s
            WHERE service_id IS NULL
            AND metadata->>'service_name' = %s
            """,
            (service_id, service_name),
        )

        # Cleanup
        cursor.execute("DELETE FROM unmapped_services WHERE id=%s", (unmapped_id,))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Backfill complete")

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
    dag_id="seed_and_backfill_services",
    default_args=default_args,
    description="Seed AWS services/categories from JSON and backfill service_ids in resources + billing",
    schedule_interval="@weekly",   # can also trigger manually
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["finops", "services", "seed", "backfill"],
) as dag:

    seed_services_task = PythonOperator(
        task_id="seed_services",
        python_callable=seed_services,
    )

    backfill_service_ids_task = PythonOperator(
        task_id="backfill_service_ids",
        python_callable=backfill_service_ids,
    )

    seed_services_task >> backfill_service_ids_task
