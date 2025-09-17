# 🚀 CI/CD for Samaira – GitHub Actions + ArgoCD

Samaira uses **GitHub Actions** for CI and **ArgoCD** for CD (GitOps).

---

## 🔹 Pipeline Overview

1. **Developer Workflow**
   - Developer pushes code to `main` or creates a Pull Request (PR).
   - GitHub Actions runs tests, linting, build, and Docker image creation.

2. **Continuous Integration (CI)**
   - Lint & test backend (FastAPI + Python).
   - Lint & test frontend (React + Node).
   - Build Docker images (multi-stage).
   - Push to container registry (ECR/GHCR/DockerHub).

3. **Continuous Delivery (CD)**
   - ArgoCD watches `infra/` Helm/Terraform manifests.
   - Syncs to target Kubernetes cluster.
   - Handles rollouts with health checks & auto-rollback.

---

## 🔹 GitHub Actions Workflow

📂 `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install backend deps
        run: pip install -r requirements.txt

      - name: Run backend tests
        run: pytest

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: "18"

      - name: Install frontend deps
        run: cd frontend && npm install

      - name: Run frontend build
        run: cd frontend && npm run build

      - name: Build Docker image
        run: docker build -t ghcr.io/org/finops-app:${{ github.sha }} .

      - name: Push Docker image
        run: echo "${{ secrets.GITHUB_TOKEN }}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin &&              docker push ghcr.io/org/finops-app:${{ github.sha }}
```

---

## 🔹 ArgoCD Deployment

- **App of Apps pattern** → manages backend, frontend, monitoring, airflow.  
- GitOps repo contains:
  - `infra/helm/finops-app/` (Helm chart)
  - `infra/terraform/` (network, DB, secrets)

### Example ArgoCD App

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: finops-app
spec:
  project: default
  source:
    repoURL: https://github.com/org/finops-infra.git
    targetRevision: main
    path: infra/helm/finops-app
  destination:
    server: https://kubernetes.default.svc
    namespace: finops
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

---

## 🔹 Observability in CI/CD

- Push test coverage to Codecov.  
- Linting reports in PR checks.  
- Prometheus metrics auto-validated post-deploy.  
- Grafana alerts validate rollout health.

---

## 🔹 Roadmap

- [ ] Add GitHub Actions job for Alembic migrations.  
- [ ] Add security scans (Trivy, Snyk).  
- [ ] Add e2e Cypress tests for frontend.  
- [ ] Blue-Green or Canary deploys with Argo Rollouts.  

---

✅ This ensures every code push → tested, containerized, deployed → observable in minutes.
