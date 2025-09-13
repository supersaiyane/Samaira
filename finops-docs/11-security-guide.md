🔐 Security Guide
=================

1\. Overview
------------

The FinOps Platform handles **sensitive billing + cloud credentials**.Security is embedded at every layer:

*   **Secrets Management:** Vault integration.
    
*   **Authentication/Authorization:** API keys & RBAC.
    
*   **Network Security:** TLS, restricted ports.
    
*   **Least Privilege:** Scoped IAM roles.
    

2\. Secrets Management with Vault
---------------------------------

### Setup

*   **Vault runs as a container** (vault:1.15.2).
    
*   Dev mode root token (root) → replaced with AppRole in production.
    

### Usage

*   Secrets stored under:
    
    *   secret/data/db → DB\_USER, DB\_PASSWORD.
        
    *   secret/data/aws → AWS\_ACCESS\_KEY\_ID, AWS\_SECRET\_ACCESS\_KEY.
        
    *   secret/data/webhooks → SLACK\_WEBHOOK\_URL, TEAMS\_WEBHOOK\_URL.
        

### Injection Flow

1.  App logs into Vault via **AppRole**.
    
2.  /entrypoint.sh script fetches secrets.
    
3.  Secrets exported into container ENV.
    
4.  FastAPI, Airflow, DAGs read from ENV.
    

### Example Policy (db only)

```
path "secret/data/db" {
  capabilities = ["read"]
}

```

3\. Authentication (FastAPI)
----------------------------

### API Key Auth

*   Endpoints secured via X-API-Key header.
    
*   Keys stored in Vault (secret/data/api\_keys).
    

```
from fastapi import Depends, HTTPException, Header


API_KEYS = os.getenv("API_KEYS", "").split(",")


def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key not in API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API key")



```

### OAuth2 (Optional)

*   For frontend users → integrate with **Auth0/Azure AD**.
    
*   Tokens validated in middleware.
    

4\. RBAC (Role-Based Access Control)
------------------------------------

*   **Roles:** viewer, analyst, admin.
    
*   RBAC policies stored in DB (table users + roles).
    
*   Middleware enforces access per role.
    

Example:

```
-- RBAC table
CREATE TABLE roles (
  role_id SERIAL PRIMARY KEY,
  role_name VARCHAR(50) UNIQUE
);


CREATE TABLE user_roles (
  user_id INT REFERENCES users(user_id),
  role_id INT REFERENCES roles(role_id),
  PRIMARY KEY (user_id, role_id)
);

```

5\. Network & Infra Security
----------------------------

*   **TLS everywhere**: terminate TLS at reverse proxy (Nginx/Ingress).
    
*   **DB Access:** only exposed to backend + airflow.
    
*   **Monitoring:** Prometheus scrapes metrics over secure endpoints.
    

6\. IAM Best Practices (AWS)
----------------------------

*   **Use IAM Roles** instead of long-lived keys.
    
*   Each service (EC2, EKS, Lambda) gets **scoped IAM role**.
    
*   Vault rotates credentials periodically (if AWS Secrets Engine enabled).
    

7\. CI/CD Security
------------------

*   GitHub Actions → secrets injected via secrets.\*.
    
*   ArgoCD → pulls secrets from Vault via CSI driver.
    
*   Never commit secrets into Git.
    

8\. Threat Modeling
-------------------

*   **SQL Injection:** Prevented via SQLAlchemy ORM.
    
*   **DoS (Denial of Service):** Nginx rate limits.
    
*   **Anomaly Alerts:** Detect sudden billing spikes.
    
*   **Audit Logs:** Inserted into logs table.
    

9\. Knowledge Check
-------------------

1.  Where are DB credentials stored in Vault?
    
2.  How does /entrypoint.sh fetch secrets?
    
3.  What happens if an invalid X-API-Key is sent?
    
4.  Name 3 RBAC roles defined in the platform.
    
5.  Why should IAM Roles be preferred over static AWS keys?