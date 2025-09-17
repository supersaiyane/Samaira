# 📊 Monitoring & Observability – Samaira

Samaira uses **Prometheus + Grafana + Loki + Promtail** for full observability across
cost forecasting, AI queries, and system health.

---

## 🔹 Components

- **Prometheus** → Collects metrics
  - `finops_ai_queries_total{status=...}`
  - `finops_forecast_drift{model=...}`
  - `finops_forecast_runs_total{model=...}`
- **Grafana** → Dashboards + Alerts
- **Loki + Promtail** → Centralized logs
- **Exporters**:
  - Postgres exporter → DB stats
  - Airflow exporter → DAG metrics
  - Backend `/metrics` → AI queries + drift metrics

---

## 🔹 Metrics

### AI Queries
- `finops_ai_queries_total{status="yaml|llm|ollama|unsupported|unsafe|llm_failed"}`
  - Counts queries by type & outcome.

### Forecasting
- `finops_forecast_drift{model="Prophet|ARIMA|SMA|LSTM"}`
  - Gauge → current drift (MAPE).
- `finops_forecast_runs_total{model="..."}`  
  - Counter → number of runs executed.

---

## 🔹 Dashboards

### 1. Forecast Drift & Model Comparison
📂 `monitoring/dashboards/forecast_drift.json`
- Line chart: Drift % over time
- Timeseries: Prophet vs ARIMA vs SMA vs LSTM
- Table: Current drift snapshot

### 2. AI Query Engine Usage
📂 `monitoring/dashboards/ai_queries.json`
- Stat: Total queries
- Pie: Source split (YAML vs LLM vs Ollama vs errors)
- Timeseries: Query volume by type
- Table: Error breakdown

---

## 🔹 Alerts

### Forecast Drift Alerts
📂 `monitoring/provisioning/alerting/forecast_drift_alerts.yaml`
- Fires if forecast drift > **20%** for 2 minutes.

### AI Query Error Alerts
📂 `monitoring/provisioning/alerting/ai_queries_alerts.yaml`
- Fires if > **5 unsafe/unsupported/failed queries** in 10 minutes.

---

## 🔹 Setup

### 1. Prometheus Scrape Config
In `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: "finops-backend"
    metrics_path: /metrics
    static_configs:
      - targets: ["finops-app:8000"]
```

### 2. Grafana Provisioning
In `docker-compose.yaml`, mount provisioning dirs:

```yaml
volumes:
  - ./monitoring/dashboards:/etc/grafana/provisioning/dashboards
  - ./monitoring/provisioning/datasources:/etc/grafana/provisioning/datasources
  - ./monitoring/provisioning/alerting:/etc/grafana/provisioning/alerting
```

### 3. Notification Channels
Configure in Grafana UI → Alerting → Contact Points:
- Slack
- Email
- PagerDuty

---

## 🔹 Future Enhancements
- Add **per-service cost anomaly metrics**.
- Push **pipeline DAG success/failure metrics**.
- Expose **LLM latency metrics** (`finops_ai_llm_latency_seconds`).
- Add **custom Grafana dashboards** for budget breaches.

---

✅ With this setup, you get **full visibility** into:
- Forecast accuracy & drift
- AI query reliability
- DB, DAGs, backend health
- Logs & traces
