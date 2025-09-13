🌐 Disaster Recovery (DR) Plan
==============================

1\. Objectives
--------------

*   **RPO (Recovery Point Objective):** ≤ 1 hour (data loss tolerance).
    
*   **RTO (Recovery Time Objective):** ≤ 2 hours (time to recover).
    
*   Ensure **continuous cost visibility** and **no data corruption** after failover.
    

2\. Critical Components
-----------------------

*   **Postgres (DB):** source of truth (billing, usage, recommendations, forecasts).
    
*   **Vault:** stores AWS creds, DB creds, webhook URLs.
    
*   **Airflow:** orchestrates ingest, rightsizing, anomaly detection, forecasting.
    
*   **Backend (FastAPI):** APIs for UI & insights.
    
*   **Frontend (React):** dashboards for users.
    
*   **Monitoring (Prometheus/Grafana/Loki):** observability stack.
    

3\. Backup Strategy
-------------------

### Postgres

*   docker compose exec db pg\_dump -U $DB\_USER $DB\_NAME > backup-$(date +%F).sql
    
*   Store in **S3 with lifecycle policy** (30-day retention).
    

### Vault

*   vault operator raft snapshot save vault-$(date +%F).snap
    
*   Store snapshots in **secure S3 bucket** with encryption (KMS).
    

### Airflow

*   DAGs in Git repo → **no backup needed**, always re-deployed.
    
*   Metadata DB is included in Postgres backup.
    

### Monitoring

*   Prometheus WAL → back up every **6 hours**.
    
*   Grafana dashboards stored in Git → always recoverable.
    

4\. Failover Strategy
---------------------

### Database

*   Preferred: **RDS Multi-AZ** with automated failover.
    
*   Self-hosted: configure **streaming replication** to standby DB.
    

### Vault

*   Use **HA mode** with Raft peers (3+ nodes).
    
*   Recovery: restore snapshot → unseal with quorum keys.
    

### Airflow

*   Stateless, can be redeployed quickly.
    
*   Ensure DB + DAGs are restored first.
    

### Backend + Frontend

*   Stateless containers → redeploy from image.
    

### Monitoring

*   Prometheus can be restored from WAL backups.
    
*   Grafana dashboards reload from Git.
    

5\. DR Runbook
--------------

### Step 1: Declare Incident

*   Mark severity **SEV-1**.
    
*   Notify FinOps & SRE teams via Slack/Teams.
    

### Step 2: Spin Up Infra in DR Region

*   Deploy DB container (or RDS restore).
    
*   Restore Vault snapshot.
    
*   Start finops-app (backend + frontend + airflow).
    

### Step 3: Restore Data

*   docker compose exec -T db psql -U $DB\_USER $DB\_NAME < backup-latest.sql
    
*   vault operator raft snapshot restore vault-latest.snap
    

### Step 4: Reconfigure Airflow

*   alembic upgrade head
    
*   airflow dags trigger billing\_ingestairflow dags trigger usage\_ingestairflow dags trigger rightsizing
    

### Step 5: Validate

*   Login to UI → check insights are populated.
    
*   Grafana dashboards → confirm metrics flowing.
    
*   Trigger a test recommendation → verify pipeline end-to-end.
    

6\. Testing DR
--------------

*   **Quarterly failover drills**:
    
    1.  Simulate DB outage.
        
    2.  Validate RPO/RTO objectives.
        
    3.  Update runbook if steps fail.
        

7\. Knowledge Check
-------------------

1.  What’s the RPO and RTO for this system?
    
2.  Which components are stateless (can be redeployed easily)?
    
3.  How do you restore Vault after a region loss?
    
4.  Which Airflow DAGs should be re-triggered after recovery?
    
5.  How often should DR drills be conducted?