#!/bin/bash
set -euo pipefail

VAULT_ADDR=http://vault:8200
ROLE_ID=${VAULT_ROLE_ID}
SECRET_ID=${VAULT_SECRET_ID}

echo "🔑 Logging into Vault with AppRole..."
LOGIN_JSON=$(curl -s --request POST \
  --data "{\"role_id\": \"$ROLE_ID\", \"secret_id\": \"$SECRET_ID\"}" \
  $VAULT_ADDR/v1/auth/approle/login)

VAULT_TOKEN=$(echo "$LOGIN_JSON" | jq -r '.auth.client_token')

if [ "$VAULT_TOKEN" == "null" ] || [ -z "$VAULT_TOKEN" ]; then
  echo "❌ Vault login failed"
  exit 1
fi
echo "✅ Vault login successful"

# ===============================
# Load secrets from Vault
# ===============================
echo "📥 Fetching secrets from Vault..."

# DB secrets
DB_JSON=$(curl -s --header "X-Vault-Token: $VAULT_TOKEN" \
  $VAULT_ADDR/v1/secret/data/db | jq -r '.data.data')
export DB_USER=$(echo "$DB_JSON" | jq -r '.DB_USER')
export DB_PASSWORD=$(echo "$DB_JSON" | jq -r '.DB_PASSWORD')
export DB_NAME=$(echo "$DB_JSON" | jq -r '.DB_NAME')
export DB_HOST=$(echo "$DB_JSON" | jq -r '.DB_HOST')
export DB_PORT=$(echo "$DB_JSON" | jq -r '.DB_PORT')

# AWS creds
AWS_JSON=$(curl -s --header "X-Vault-Token: $VAULT_TOKEN" \
  $VAULT_ADDR/v1/secret/data/aws | jq -r '.data.data')
export AWS_ACCESS_KEY_ID=$(echo "$AWS_JSON" | jq -r '.AWS_ACCESS_KEY_ID')
export AWS_SECRET_ACCESS_KEY=$(echo "$AWS_JSON" | jq -r '.AWS_SECRET_ACCESS_KEY')
export AWS_REGION=$(echo "$AWS_JSON" | jq -r '.AWS_REGION')

# Webhooks
WEBHOOK_JSON=$(curl -s --header "X-Vault-Token: $VAULT_TOKEN" \
  $VAULT_ADDR/v1/secret/data/webhooks | jq -r '.data.data')
export SLACK_WEBHOOK_URL=$(echo "$WEBHOOK_JSON" | jq -r '.SLACK_WEBHOOK_URL')
export TEAMS_WEBHOOK_URL=$(echo "$WEBHOOK_JSON" | jq -r '.TEAMS_WEBHOOK_URL')

# --- Wait for DB ---
echo "⏳ Waiting for database..."
until pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
  sleep 2
done
echo "✅ Database is ready"

# ===============================
# Database migrations
# ===============================
echo "⏳ Running Alembic migrations..."
if ! alembic upgrade head; then
  echo "❌ Alembic migrations failed (check DB connection and schema)"
  exit 1
fi
echo "✅ Migrations applied"

# ===============================
# Seed initial SQL (baseline data)
# ===============================
if [ -f "/db/init/01_init.sql" ]; then
  echo "📥 Running initial seed script (01_init.sql)..."
  PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f /db/init/01_init.sql || true
fi

# ===============================
# Seed instance catalog (first run only)
# ===============================
if [ "${SEED_CATALOG:-true}" = "true" ]; then
  echo "📥 Seeding EC2 Instance Catalog from AWS Pricing API..."
  python scripts/seed_instance_catalog.py || echo "⚠️ Seeding skipped"
fi

# ===============================
# Airflow DB Init + User
# ===============================
echo "⚙️ Initializing Airflow metadata DB..."
airflow db init || true

echo "👤 Creating default Airflow admin user (if missing)..."
airflow users list | grep -q "admin" || airflow users create \
  --username admin \
  --firstname FinOps \
  --lastname Admin \
  --role Admin \
  --email admin@example.com \
  --password admin || true

# ===============================
# Start Airflow services (background)
# ===============================
echo "🌬️ Starting Airflow scheduler & webserver..."
airflow scheduler -D
airflow webserver -D -p 8080

# --- Give Airflow a few seconds ---
sleep 15

# ===============================
# Trigger Bootstrap DAGs
# ===============================
echo "⚡ Triggering bootstrap DAGs..."
airflow dags trigger instance_catalog_updater || true
airflow dags trigger billing_ingest || true
airflow dags trigger usage_ingest || true
airflow dags trigger rightsizing || true

# ===============================
# Healthcheck
# ===============================
echo "💡 Writing healthcheck script..."
cat << 'EOF' > /healthcheck.sh
#!/bin/bash
set -e
pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" >/dev/null 2>&1 || exit 1
curl -fs $VAULT_ADDR/v1/sys/health >/dev/null 2>&1 || exit 1
exit 0
EOF
chmod +x /healthcheck.sh

# ===============================
# Start Supervisor (FastAPI + Airflow + Nginx)
# ===============================
echo "🚀 Starting Supervisor..."
exec /usr/local/bin/supervisord -c /etc/supervisord.conf
