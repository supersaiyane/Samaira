
# 🚀 FinOps Platform Setup Guide

This guide explains how to set up the **FinOps Platform** from scratch: Database, Backend (FastAPI), Frontend (React), Airflow DAGs, Monitoring (Prometheus/Grafana/Loki), and AWS integration.

---

## 1. 📦 Prerequisites
Ensure you have the following installed:

- **Docker & Docker Compose** (≥ v2.3)
- **Python 3.11+**
- **Node.js (≥18) + npm / yarn**
- **AWS CLI v2** configured with access/secret keys
- **Make** (optional but recommended)

---

## 2. 🗄️ Database Setup (Postgres)

We use **Postgres 15** as the core DB.

### Start Postgres via Docker Compose
```bash
docker compose up -d db
```

### Initialize schema
- SQL schema is auto-loaded from:
  - `db/schema.sql`
  - `db/init/01_init.sql`

If you need to apply migrations after model changes:
```bash
alembic revision --autogenerate -m "init schema"
alembic upgrade head
```

👉 Alembic is already wired to `app/db/models.py`, so new models will be auto-detected.

---

## 3. 🔑 Credentials & Environment Variables

All credentials are managed in `.env` at project root.

Example `.env`:
```env
# Database
DB_USER=finops
DB_PASSWORD=finops123
DB_NAME=finopsdb
DB_HOST=db
DB_PORT=5432

# AWS
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=us-east-1

# Notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/xxx

# FastAPI
API_PORT=8000
```

💡 Docker Compose automatically injects `.env` into backend, frontend, and Airflow services.

---

## 4. ⚡ Backend (FastAPI)

### Build & Run
```bash
docker compose up -d backend
```

### Local dev (hot reload):
```bash
cd app
uvicorn app.main:app --reload
```

### API available at:
```
http://localhost:8000/docs
```

---

## 5. 🎨 Frontend (React + Tailwind)

### Build & Run
```bash
docker compose up -d frontend
```

Local dev (hot reload):
```bash
cd frontend
npm install
npm run dev
```

UI available at:
```
http://localhost:3000
```

---

## 6. ⏳ Airflow (ETL & FinOps DAGs)

Airflow orchestrates billing ingestion, usage collection, rightsizing, anomaly detection, forecasting, savings tracking, and auto-remediation.

### Start Airflow
```bash
docker compose up -d airflow
```

### Access UI
```
http://localhost:8080
```

### DAGs included:
- `billing_ingest`
- `usage_ingest`
- `rightsizing`
- `anomaly_detection_v3`
- `forecasting`
- `savings_tracker`
- `auto_remediation`
- `instance_catalog_updater`

### First-time Run (populate baseline data)
1. Run **`instance_catalog_updater`** → loads AWS instance families & prices into DB.
2. Run **`billing_ingest`** and **`usage_ingest`** to populate data.
3. Run **`forecasting`** to generate initial forecasts.

---

## 7. 📊 Monitoring & Observability

We include **Prometheus + Grafana + Loki**.

### Start monitoring stack
```bash
docker compose up -d prometheus grafana loki
```

- **Prometheus**: http://localhost:9090  
- **Grafana**: http://localhost:3001 (login: `admin` / `admin`)  
- **Loki Logs**: Integrated into Grafana  

Dashboards included:
- Cost Trends
- Savings Tracker
- Rightsizing Opportunities
- Forecast vs Actual
- Anomalies Overview
- Resource Utilization
- Budget & Spend Tracking
- Logs Overview
- Account/Service Drilldown

---

## 8. 🔐 AWS Credentials Flow

AWS credentials must be injected into backend + airflow containers.

Options:
1. **Environment Variables (preferred in dev)** → via `.env`.
2. **Mounted AWS Profile** → mount `~/.aws/credentials` inside containers.
3. **AWS IAM Role** (prod) → when running in ECS/EKS, rely on role-based access.

Example Docker Compose snippet:
```yaml
environment:
  - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
  - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
  - AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}
```

---

## 9. ✅ Verification Steps

- Check DB is seeded:
```sql
SELECT * FROM accounts LIMIT 5;
```

- Verify backend health:
```
curl http://localhost:8000/health
```

- Verify DAGs in Airflow UI:
http://localhost:8080

- Run a test query via AI Assistant:
```
POST http://localhost:8000/api/v1/ai/query
{ "query": "Top 5 services by cost last 60 days" }
```

---

## 10. 🛠️ Common Issues

- **Migrations not applied** → Run `alembic upgrade head`.
- **Airflow webserver crash** → Ensure DB is up first (`docker compose up db`).
- **No AWS data** → Check AWS credentials are passed inside container (`printenv` inside `airflow`).

---

## 11. 📌 Deployment Notes

For production:
- Use **Helm charts** instead of Docker Compose.
- Store secrets in **AWS Secrets Manager** / **Vault**.
- Use **RDS Postgres** instead of local Postgres.
- Enable **CloudWatch exporters** for AWS service-level metrics.
