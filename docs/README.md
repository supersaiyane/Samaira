# Samaira – FinOps Automation Toolkit

Samaira is a full-stack **FinOps Automation Platform** that combines cost optimization,
forecasting, anomaly detection, rightsizing, and observability into one system.

---

## 🚀 Features

- **Backend (FastAPI)**: APIs for costs, savings, insights, AI queries.
- **Frontend (React)**: Dashboards for Insights, Forecast, Savings, Rightsizing.
- **Airflow DAGs**:
  - `billing_ingest.py` → billing ingestion
  - `usage_ingest.py` → usage ingestion
  - `rightsizing.py` → idle detection & rightsizing
  - `anomaly_detection_v3.py` → cost/usage anomalies
  - `savings_tracker.py` → savings tracker
  - `cost_forecasting_v2.py` → Prophet/ARIMA/SMA (v3 adds LSTM + drift detection)
  - `auto_remediation.py` → automated fixes
- **Secrets Management**: HashiCorp Vault integration.
- **Database**: PostgreSQL with partitioned billing/usage tables.
- **Monitoring & Observability**:
  - Prometheus, Grafana, Loki, Promtail.
  - Exporters for backend, Postgres, Airflow.
  - Grafana dashboards for forecasts, anomalies, AI queries usage.
- **AI Query Engine**:
  - YAML-defined queries (`ai_queries.yaml`).
  - LLM fallback (OpenAI, Anthropic, Ollama) with guardrails.
  - Logged in `ai_queries_log` for training & analytics.

---

## 📂 Project Structure

```
Samaira/
├── app/                 # FastAPI backend
│   ├── api/v1/          # Routers (accounts, savings, insights, ai, etc.)
│   ├── core/            # Config & DB setup
│   ├── db/              # Models & migrations
│   ├── services/        # Business logic (savings, ai_service, etc.)
│   └── ...
├── frontend/            # React frontend (Navbar, Insights, dashboards)
├── airflow/dags/        # DAGs (billing, usage, anomaly, forecasting, remediation)
├── monitoring/          # Prometheus, Grafana, Loki configs
├── docs/                # Documentation (GitBook/Honkit)
├── docker-compose.yaml  # Full stack definition
├── Dockerfile           # Build backend + frontend + Airflow
├── entrypoint.sh        # Init: migrations, DAG bootstrap, Vault fetch
├── healthcheck.sh
├── supervisord.conf
└── README.md
```

---

## 🛠️ Setup

### 1. Environment
Create `.env` file:

```ini
DB_USER=finops
DB_PASSWORD=finops123
DB_NAME=finopsdb
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_REGION=us-east-1

# LLM
USE_LLM_FALLBACK=true
LLM_PROVIDER=openai   # or anthropic | ollama
LLM_MODEL=gpt-4o-mini
LLM_API_KEY=sk-xxxx
```

### 2. Run with Docker Compose
```bash
docker compose up -d --build
```

### 3. Access Services
- Backend (FastAPI): [http://localhost:8000/docs](http://localhost:8000/docs)
- Frontend (React): [http://localhost:3000](http://localhost:3000)
- Airflow UI: [http://localhost:8080](http://localhost:8080)
- Grafana: [http://localhost:3001](http://localhost:3001)
- Vault: [http://localhost:8200](http://localhost:8200)
- Prometheus: [http://localhost:9090](http://localhost:9090)

---

## 📊 Observability

- Forecast drift metrics pushed to Prometheus.
- Grafana dashboards:
  - Forecast accuracy (Prophet, ARIMA, SMA, LSTM).
  - Anomaly detection events.
  - AI query usage (yaml vs llm vs ollama).

---

## 📖 Documentation

- [Cost Forecasting v3](./docs/cost_forecasting_v3.md)
- [AI Query Engine (LLM)](./docs/ai_service_llm_doc.md)
- Monitoring setup → `docs/monitoring.md`
- CI/CD setup → `docs/ci_cd.md`

---

## 🔮 Roadmap

- [ ] Add `cost_forecasting_v3.py` DAG (with LSTM + drift detection)
- [ ] Add Prometheus metrics in `ai_service.py`
- [ ] Add Grafana dashboards for AI queries + drift
- [ ] Multi-stage Dockerfile (smaller image)
- [ ] Extend frontend with Forecast, Savings, Rightsizing dashboards

---

## 📝 License

See [LICENSE](./LICENSE).

---
