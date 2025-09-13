📊 Monitoring & Observability Guide
===================================

1\. Overview
------------

We use the **Prometheus + Grafana + Loki + Promtail** stack for observability.It provides **metrics, dashboards, and logs** for:

*   **Backend (FastAPI)** → request rate, errors, latency.
    
*   **Database (Postgres)** → TPS, slow queries, connection usage.
    
*   **Airflow** → DAG/task metrics, scheduler health.
    
*   **App Logs** → via Loki + Promtail.
    

2\. Prometheus
--------------

**Config File:** monitoring/prometheus.yml

*   Scrapes exporters + backend metrics.
    
*   Endpoints:
    
    *   FastAPI → /metrics via backend-metrics.
        
    *   Postgres → postgres-exporter (:9187).
        
    *   Airflow → airflow-exporter (:9112).
        
    *   Loki logs → optionally.
        

Run:

```
docker-compose up prometheus
```

3\. Grafana
-----------

**Provisioned Dashboards:**Stored under monitoring/dashboards/.

### Preloaded Dashboards:

1.  **FinOps Overview Dashboard**
    
    *   Cost trend, anomalies, savings summary.
        
2.  **Rightsizing Dashboard**
    
    *   EC2 utilization vs costs, idle detection.
        
3.  **Forecast Dashboard**
    
    *   Actual vs Forecast, drift, model accuracy.
        
4.  **Anomaly Dashboard**
    
    *   Detected anomalies by severity & type.
        
5.  **Savings Tracker Dashboard**
    
    *   Validated savings over time.
        
6.  **FastAPI Dashboard**
    
    *   Request rate, latency (P50/95/99), error rates.
        
7.  **Postgres Dashboard**
    
    *   TPS, cache hit ratio, connection usage, slow queries.
        
8.  **Airflow Dashboard**
    
    *   DAG run status, task trends, scheduler heartbeat.
        
9.  **Logs Explorer (Loki)**
    
    *   Application logs searchable in Grafana Explore.
        

Access Grafana:[http://localhost:3001](http://localhost:3001)(default user/pass = admin/admin).

4\. Loki + Promtail
-------------------

*   **Loki**: stores logs in time-series.
    
*   **Promtail**: ships container logs → Loki.
    

Config files:

*   monitoring/loki-config.yml
    
*   monitoring/promtail-config.yml
    

You can search logs in Grafana **Explore → Loki datasource**.

5\. Exporters
-------------

*   **FastAPI Exporter** (backend-metrics): scrapes /metrics.
    
*   **Postgres Exporter**: metrics at :9187.
    
*   **Airflow Exporter**: metrics at :9112.
    

All wired into Prometheus automatically.

6\. Alerting
------------

Add **Alertmanager** integration later:

*   Slack → cost anomalies.
    
*   Teams → forecast drift.
    
*   PagerDuty → critical outages.
    

7\. Example Queries
-------------------

*   **FastAPI request latency (95th percentile):**
    

```
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
```

*   **Postgres active connections:**
    

```
pg_stat_activity_count{datname="finopsdb"}
```

*   **Airflow DAG failures (last hour):**
    

```
rate(airflow_dag_run_failed[1h])
```

8\. Knowledge Check
-------------------

1.  Which component ships logs into Loki?
    
2.  Which dashboard shows EC2 idle detection?
    
3.  What’s the default Grafana login?
    
4.  How do we check Airflow scheduler heartbeat in Grafana?
    
5.  Which exporter provides /metrics for FastAPI?