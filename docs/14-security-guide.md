🔐 Security Guide
=================

1\. Overview
------------

This document defines **security practices** for the FinOps Platform.It covers **authentication, secrets management, RBAC, IAM, network policies, and compliance**.

2\. Secrets Management (Vault)
------------------------------

### Storage

*   All secrets (DB creds, AWS keys, webhooks) stored in **Vault KV v2**.
    
```
vault kv put secret/db DB_USER=finops DB_PASSWORD=finops123 DB_NAME=finopsdb
vault kv put secret/aws AWS_ACCESS_KEY_ID=xxx AWS_SECRET_ACCESS_KEY=yyy AWS_REGION=us-east-1

```
    

### Access

*   Use **AppRole** auth method for services.
    
*   Role IDs + Secret IDs injected via Docker secrets or .env.
    

### Rotation

*   Database and AWS creds rotated every 90 days.
    
*   Update Vault → rolling restart services.
    

3\. Authentication & Authorization
----------------------------------

### Backend

*   **AWS Cognito** provides OAuth2 + JWT authentication for users.
    
*   JWT tokens validated on every API request.
    

### RBAC

*   Roles: **admin, finops, viewer**.
    
*   Permissions:
    
    *   admin: all CRUD ops, user management.
        
    *   finops: can view dashboards, trigger DAGs, approve/dismiss recs.
        
    *   viewer: read-only dashboards.
        

Enforced via **FastAPI dependencies**.

4\. IAM Practices
-----------------

*   **Least privilege** AWS IAM roles:
    
    *   CostExplorerReadOnly → Billing ingestion.
        
    *   CloudWatchReadOnly → Usage ingestion.
        
    *   EC2FullAccess (restricted) → rightsizing remediation.
        
*   Deny wildcards (\*).
    
*   Explicit tagging enforced via SCPs.
    

5\. Network Security
--------------------

*   **Vault**: accessible only on internal Docker/K8s network.
    
*   **DB**: restricted to backend + airflow.
    
*   **Prometheus/Grafana**: secured via reverse proxy + OAuth login.
    
*   **TLS everywhere** in production (terminate at Nginx/ALB).
    

6\. Compliance & Auditing
-------------------------

*   **Logs**:
    
    *   All API calls logged in logs table.
        
    *   Vault audit logs enabled.
        
    *   Airflow DAG runs logged in Loki.
        
*   **Compliance Frameworks**:
    
    *   SOC2, ISO27001 supported practices.
        
    *   GDPR → anonymize PII in billing data.
        

7\. Incident Response
---------------------

*   Failed login attempts → alert via Prometheus rule.
    
*   Vault unseal events → trigger Slack/Teams notification.
    
*   Breach response → revoke AppRole, rotate DB + AWS creds.
    

8\. Knowledge Check
-------------------

1.  Where are AWS credentials stored in the platform?
    
2.  Which Vault auth method is used by backend services?
    
3.  What RBAC role has read-only access?
    
4.  How often are DB/AWS creds rotated?
    
5.  Which compliance frameworks are supported?