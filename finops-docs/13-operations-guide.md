⚙️ Operations Guide
===================

1\. Overview
------------

This document guides operators and SREs managing the **FinOps Platform** in **production**.It covers **monitoring, scaling, backup, DR, and troubleshooting**.

2\. Service Ports & Health
--------------------------

| Service     | Port | Healthcheck                     |
|-------------|------|---------------------------------|
| FastAPI API | 8000 | /health                         |
| Frontend    | 3000 | React build served via Nginx    |
| Airflow UI  | 8080 | /health DAG Scheduler heartbeat |
| Grafana     | 3001 | /api/health                     |
| Prometheus  | 9090 | /-/healthy                      |
| Postgres    | 5432 | pg_isready                      |
| Vault       | 8200 | /v1/sys/health                  |

3\. Monitoring & Alerts
-----------------------

### Metrics

*   **FastAPI** → request rates, latency (P50/P95/P99), error rates.
    
*   **Airflow** → DAG run success/fail, scheduler heartbeat.
    
*   **Postgres** → TPS, slow queries, connection usage.
    
*   **FinOps KPIs** → Cost anomalies, rightsizing, savings applied.
    

### Dashboards

Provisioned in Grafana:

*   **App Overview**
    
*   **Cost & Usage Trends**
    
*   **Rightsizing Opportunities**
    
*   **Forecast Accuracy**
    
*   **Anomalies & Alerts**
    

### Alerts

Prometheus rules:

*   API latency > 1s (critical).
    
*   Error rate > 5%.
    
*   DB connections > 80%.
    
*   No Airflow scheduler heartbeat > 5 min.
    
*   Anomaly detected → Slack/Teams notification.
    

4\. Scaling & Performance
-------------------------

### Horizontal Scaling

*   **Backend** → Scale with replicas behind a load balancer (K8s preferred).
    
*   **Frontend** → Serve via CDN or Nginx cluster.
    
*   **Airflow** → Switch to **CeleryExecutor** for distributed workers.
    

### Vertical Scaling

*   Increase **Postgres memory** for query-heavy workloads.
    
*   Adjust Airflow worker concurrency.
    

5\. Backup & Recovery
---------------------

### Database

*   Daily snapshot via pg\_dump or managed service (RDS/Aurora).
    
*   Store backups in **S3 with lifecycle policies**.
    

```
pg_dump -U $DB_USER -d $DB_NAME | gzip > backup.sql.gz

```

### Vault

*   Enable Vault **raft storage snapshots**.
    
*   Store encrypted copies offsite.
    

### Airflow

*   Backup DAGs + logs (already volume-mounted).
    

6\. Disaster Recovery (DR)
--------------------------

1.  Restore DB from latest snapshot.
    
2.  Restore Vault snapshots.
    
3.  Redeploy stack (docker compose up -d).
    
4.  airflow dags trigger instance\_catalog\_updaterairflow dags trigger billing\_ingestairflow dags trigger usage\_ingest
    

7\. Troubleshooting
-------------------

| Symptom              | Likely Cause                | Fix                                      |
|----------------------|-----------------------------|------------------------------------------|
| Backend 500 errors   | DB unreachable              | Check db logs, ensure migrations applied |
| Airflow DAGs stuck   | Executor misconfigured      | Switch to Celery or check scheduler logs |
| Grafana panels empty | Prometheus target misconfig | Check Prometheus scrape configs          |
| Vault login fails    | Wrong AppRole creds         | Re-run vault write auth/approle/role/... |
| No cost data         | AWS credentials invalid     | Update Vault secret aws path             |

8\. Logs
--------

*   **Application logs**: shipped via Promtail → Loki → Grafana.
    
*   **Airflow logs**: mounted under ./airflow/logs/.
    
*   **DB logs**: available inside container (docker logs finops-db).
    

Query logs in Grafana → Explore → Loki.

9\. Ops Playbooks
-----------------

*   **Idle Resource** → stop instance, notify owner.
    
*   **Budget Breach** → escalate to finance team.
    
*   **Forecast Drift** → trigger re-training job.
    
*   **Vault Down** → switch to backup cluster.
    

10\. Knowledge Check
--------------------

1.  What executor is used to scale Airflow beyond one node?
    
2.  Where are application logs shipped?
    
3.  How do you restore Vault in DR?
    
4.  What Prometheus alert fires when the API latency exceeds 1s?
    
5.  Which DAGs must be re-triggered after disaster recovery?