⚙️ CI/CD Guide (GitHub Actions + ArgoCD)
========================================

1\. Overview
------------

CI/CD ensures **automated builds, tests, and deployments** for our FinOps platform:

*   **CI (Continuous Integration)** → Linting, unit tests, migrations, Docker image builds.
    
*   **CD (Continuous Deployment)** → Auto-deploy backend, frontend, Airflow DAGs via GitHub Actions or ArgoCD.
    

2\. GitHub Actions (CI/CD)
--------------------------

**File:** .github/workflows/ci-cd.yml

### Key Jobs

1.  **Backend (FastAPI)**
    
    *   Run lint + unit tests (pytest).
        
    *   Run migrations (alembic upgrade head).
        
    *   Build Docker image → push to registry.
        
2.  **Frontend (React)**
    
    *   Install deps (npm ci).
        
    *   Run tests (npm test).
        
    *   Build production bundle.
        
3.  **Airflow DAGs**
    
    *   Validate Python syntax.
        
    *   Run lightweight DAG parse test (airflow dags list).
        
4.  **Docker Compose Integration Test**
    
    *   Spin up stack in GitHub runner.
        
    *   Run smoke tests (curl /accounts, curl /insights/summary).
        

### Example Workflow

```
name: CI-CD


on:
  push:
    branches: [ "main" ]
  pull_request:


jobs:
  backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        ports: [5432:5432]
        env:
          POSTGRES_USER: finops
          POSTGRES_PASSWORD: finops123
          POSTGRES_DB: finopsdb
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with: { python-version: "3.11" }
      - run: pip install -r app/requirements.txt
      - run: alembic upgrade head
      - run: pytest app/tests/


  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with: { node-version: "20" }
      - run: npm ci --prefix frontend
      - run: npm test --prefix frontend
      - run: npm run build --prefix frontend


  docker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: docker build -t ghcr.io/${{ github.repository }}/finops-app:latest .
      - run: echo "${{ secrets.GITHUB_TOKEN }}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin
      - run: docker push ghcr.io/${{ github.repository }}/finops-app:latest

```

3\. ArgoCD (CD on Kubernetes)
-----------------------------

When deploying to **Kubernetes** (EKS/AKS/GKE):

*   **App of Apps pattern** → one umbrella app manages backend, frontend, airflow, monitoring.
    
*   **Sync Policy:** automated (with pruning & self-healing).
    

### Example ArgoCD App

```
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: finops-app
  namespace: argocd
spec:
  destination:
    server: https://kubernetes.default.svc
    namespace: finops
  source:
    repoURL: https://github.com/your-org/finops-platform
    targetRevision: main
    path: deploy/k8s
  syncPolicy:
    automated:
      prune: true
      selfHeal: true

```

4\. Secrets Management
----------------------

*   **GitHub Actions** → use secrets.\* (GitHub → Settings → Secrets).
    
*   **Kubernetes (ArgoCD)** → fetch secrets from Vault (via CSI driver or external-secrets).
    

5\. Deployment Flow
-------------------

1.  Developer pushes code → GitHub Actions runs CI.
    
2.  On success → build & push Docker image.
    
3.  ArgoCD watches Git repo → auto-syncs manifests.
    
4.  Kubernetes → new pods rollout (zero-downtime).
    

6\. Knowledge Check
-------------------

1.  What’s the role of alembic upgrade head in CI?
    
2.  Which step ensures React frontend builds successfully?
    
3.  How does ArgoCD achieve self-healing?
    
4.  Where are secrets stored in GitHub Actions?
    
5.  Which workflow job runs smoke tests against /insights/summary?