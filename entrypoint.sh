#!/bin/bash
set -e

echo "🚀 Starting FinOps setup..."

# 1. Wait for Postgres
echo "⏳ Waiting for database..."
until pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
  sleep 2
done

# 2. Run Alembic migrations
echo "📦 Running Alembic migrations..."
alembic upgrade head

# 3. Seed initial data if needed
if [ ! -f /app/.db_seeded ]; then
  echo "🌱 Seeding initial data..."
  psql postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME \
    -f /app/db/init/01_init.sql
  touch /app/.db_seeded
fi

# 4. Trigger first InstanceCatalog sync (so rightsizing works immediately)
echo "🔄 Syncing AWS instance catalog..."
airflow dags trigger instance_catalog_sync || true

# 5. Start Supervisor (will manage FastAPI, Airflow, Nginx)
echo "✅ Starting Supervisor..."
exec /usr/local/bin/supervisord -c /etc/supervisord.conf
