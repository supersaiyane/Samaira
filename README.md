# 🌟 Samaira – The FinOps Insight Platform

Welcome to **Samaira**, an open-source, extensible, AI-enhanced **FinOps (Financial Operations)** platform built to help teams **understand, optimize, and forecast** cloud spending with deep insights and real-time cost governance. Named after clarity and balance, Samaira empowers DevOps, SRE, FinOps, and Engineering leaders to take back control over their cloud costs while maintaining service reliability and performance.

---

## 🚀 Why Samaira?

Modern cloud-native organizations often struggle with:
- Unpredictable and rising cloud bills 💸
- Lack of visibility into real-time usage 📉
- Siloed teams between Finance and Engineering 🤝
- Manual budgeting, anomaly detection, or rightsizing 🔍

**Samaira** bridges this gap by combining:
- **Observability (Prometheus/Grafana)**
- **AI-based recommendations (savings, idle, anomaly detection)**
- **Forecasting engines**
- **Instance catalog optimization**
- **Automated remediation pipelines**

All tightly integrated into a clean and extensible architecture.

---

## ✨ Features

### 📊 Dashboards & Visualizations
- Real-time cost explorer by service/account
- Daily/weekly/monthly usage trends
- Forecasted vs actual budget tracking
- SLO-driven cost-to-performance dashboards

### 🤖 AI-Powered Insights
- Idle & underutilized resource detection
- Rightsizing recommendations (CPU, memory, storage)
- Monthly savings tracker and reports

### 🔍 Anomaly Detection
- Time-series-based anomaly detection on sudden spikes
- Alerting integration (email, Slack, Prometheus alerts)

### 🛠️ Automated Remediation (optional)
- Lambda triggers for stopping/downsizing resources
- Integration with Infrastructure-as-Code (Terraform modules)

### 📚 Catalog & Intelligence Layer
- Centralized catalog of instance types
- Recommendations based on workload mapping

---

## 🧱 Clean Architecture

Samaira follows **Domain-Driven Design (DDD)** and **modular clean architecture**:

- `frontend/` – React-based dashboards
- `backend/app/api/` – FastAPI REST endpoints
- `backend/app/core/` – Business logic, AWS clients
- `backend/app/db/` – PostgreSQL ORM models
- `backend/app/services/` – Cost calculators, anomaly engine, AI models
- `airflow/` – DAGs for data extraction, transformation, forecasts, etc.

---


---
## 🧱 Flow Diagram HighLevel

```
                        ┌────────────────────┐
                        │   React Frontend   │
                        │  Dashboards & AI   │
                        └────────┬───────────┘
                                 │
                   ┌────────────▼────────────┐
                   │      FastAPI Backend    │
                   │ API | Logic | Services  │
                   └────────┬────┬───────────┘
                            │    │
          ┌─────────────────┘    └──────────────────┐
          ▼                                          ▼
┌───────────────────────┐               ┌──────────────────────┐
│ PostgreSQL Database   │◄──────────────┤    Airflow DAGs      │
│ (costs, forecasts,    │               │ Anomaly, Recs, etc.  │
│ savings, anomalies)   │──────────────►│ Scheduled Pipelines  │
└───────────────────────┘               └──────────────────────┘
         ▲                                          ▲
         │                                          │
┌────────┴─────┐                         ┌──────────┴─────────┐
│ Prometheus   │                         │ Infracost + OPA    │
│ + Exporters  │                         │ Pre-deploy guardrails
└──────┬───────┘                         │  GitOps/CLI Hooks  │
       │                                 └──────────┬─────────┘
       │                                ┌──────────▼─────────┐
       │                                │ Kubernetes / ECS   │
       │                                │ Cluster Metadata   │
       │                                └────────────────────┘
       ▼
┌───────────────┐
│ Grafana UI    │
│ Dashboards:   │
│ - Cost Trends │
│ - Savings     │
│ - Anomalies   │
└───────────────┘
```

---

## 📂 Explore the Docs

Find detailed documentation and guides in:

- [`docs/architecture/`](./docs/architecture/) – Diagrams, system flow, DB schemas
- [`docs/usage/`](./docs/usage/) – How to deploy, query, and operate Samaira
- [`docs/devguide/`](./docs/devguide/) – Developer onboarding and code structure
- [`docs/ai/`](./docs/ai/) – How recommendations, anomaly detection, and forecasting work

---

## 🛣️ Upcoming Roadmap

Here are some of the exciting features we’re building next:

- [ ] **Multi-cloud support** (Azure, GCP alongside AWS)
- [ ] **FinOps maturity benchmarking**
- [ ] **User tagging and attribution engine**
- [ ] **Budgets-as-Code module**
- [ ] **Slack bot assistant for cost queries**
- [ ] **Grafana plugin integration**
- [ ] **Kubernetes cost insights (via Kubecost or custom model)**

Stay tuned! 🌈

---

## 🤝 Call for Contributions

Samaira is a community-first project. Whether you're a **FinOps practitioner**, **DevOps engineer**, **data scientist**, or just someone passionate about cloud cost optimization – **we welcome your ideas, code, and feedback!**

Ways you can contribute:

- 💻 Improve the dashboards or build new visualizations
- 📦 Add more AWS services or multi-cloud support
- 🤖 Enhance ML-based detection and forecasting
- 📚 Improve docs, tutorials, or walkthroughs
- 🐞 File and fix bugs, optimize queries

📬 Have an idea? Open an issue or a discussion.
📢 Want to join the contributors team? [Raise a PR](https://github.com/yourusername/samaira)

---

## 📜 License

Samaira is licensed under the **MIT License**. See [`LICENSE`](./LICENSE) for more.

---

## 💌 A Note from the Creator

> "Built out of the need to demystify cloud bills and empower teams with **actionable insights**, Samaira is more than a tool – it’s a mission to bring **transparency, accountability, and optimization** to cloud-native development."

Stay curious, stay frugal 💡

---

**Happy Optimizing!**
