⚙️ Operations Guide
===================

1\. Overview
------------

This guide covers **day-to-day operational tasks** for running the FinOps Platform:

*   Monitoring health
    
*   Scaling services
    
*   Performing backups & restores
    
*   Troubleshooting common issues
    
*   Handling DR (Disaster Recovery)
    

2\. Service Health Monitoring
-----------------------------

### Quick Checks

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   docker compose ps  docker compose logs -f finops-app   `

### Health Endpoints

*   **Backend (FastAPI):** http://localhost:8000/health
    
*   **Airflow:** http://localhost:8080/health
    
*   **DB:** pg\_isready -h db -U $DB\_USER -d $DB\_NAME
    
*   **Vault:** curl http://localhost:8200/v1/sys/health
    

### Grafana Dashboards

*   **FinOps Overview** → Costs, usage, anomalies.
    
*   **Airflow Dashboard** → DAG success/fail.
    
*   **DB Dashboard** → TPS, cache hit ratio.
    

3\. Scaling
-----------

### Vertical Scaling

*   Increase container CPU/RAM in docker-compose.override.yml.
    
*   Move DB to managed **RDS** for production.
    

### Horizontal Scaling

*   deploy: replicas: 3 resources: limits: cpus: "2" memory: 2G
    

### Airflow Executors

*   Dev: LocalExecutor
    
*   Prod: CeleryExecutor or KubernetesExecutor
    

4\. Backups & Restore
---------------------

### Database (Postgres)

Backup:

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   docker compose exec db pg_dump -U $DB_USER $DB_NAME > backup.sql   `

Restore:

```
docker compose exec -T db psql -U $DB_USER $DB_NAME < backup.sql



```

### Vault

Enable audit logs & snapshots:

```
vault operator raft snapshot save vault-backup.snap
vault operator raft snapshot restore vault-backup.snap

```

### Airflow Metadata

Stored in same **Postgres DB** (included in pg\_dump).

5\. Disaster Recovery (DR)
--------------------------

1.  **DB Replication**: enable **RDS Multi-AZ** or streaming replication.
    
2.  **Vault Unseal Keys**: securely store with ops team.
    
3.  **Airflow DAGs**: kept in Git repo (infra as code).
    
4.  **Restore Flow**:
    
    *   Bring up DB from snapshot.
        
    *   Restore Vault snapshot.
        
    *   Redeploy app containers.
        
    *   Sync DAGs from Git.
        

6\. Troubleshooting
-------------------

### Backend

*   502 Bad Gateway → check backend logs.
    
*   DB Connection Refused → verify DB\_HOST.
    

### Airflow

*   DAG not running → check scheduler logs.
    
*   Webserver crash → increase memory to 1G+.
    

### Vault

*   permission denied → expired token → re-login with AppRole.
    

### Grafana

*   curl http://localhost:9090/api/v1/targets
    

7\. Automation Tasks
--------------------

*   **Daily DAGs**:
    
    *   billing\_ingest
        
    *   usage\_ingest
        
    *   rightsizing
        
    *   anomaly\_detection
        
*   **Weekly DAGs**:
    
    *   instance\_catalog\_updater
        
    *   forecasting
        
*   **Monthly Ops**:
    
    *   Rotate AWS + DB creds in Vault.
        
    *   Validate DR runbook.
        

8\. Knowledge Check
-------------------

1.  Which executor should Airflow run in production?
    
2.  How do you back up Vault?
    
3.  Where is Airflow metadata stored?
    
4.  What is the difference between vertical and horizontal scaling?
    
5.  Which DAG should run weekly for keeping AWS instance types updated?