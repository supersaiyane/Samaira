# 01 - Planning

## Overview

This project is a **FinOps Platform** that integrates:

* **Backend (FastAPI)** → APIs for accounts, resources, billing, usage, anomalies, recommendations, savings, insights, AI queries.
* **Frontend (React + Tailwind)** → Dashboards for cost, usage, savings, anomalies, forecasts, insights.
* **Airflow DAGs** → Automated workflows for billing ingestion, usage ingestion, anomaly detection, rightsizing, cost forecasting, savings tracker, and auto-remediation.
* **Postgres Database** → Central schema with 15+ tables (accounts, resources, billing, usage, anomalies, forecasts, savings, budgets, logs, insights, AI query logs, etc.).
* **Monitoring Stack (Prometheus + Grafana + Loki + Promtail)** → Observability across backend, DB, and Airflow.
* **Vault (Secrets Manager)** → Secure storage of DB credentials, AWS keys, and webhooks.

The goal is to **track cloud costs, detect anomalies, recommend savings, and forecast usage** across AWS (EC2, ECS, EKS, Lambda), with extensibility for Azure and GCP.

---

## Problem Statement

Cloud costs are **rising unpredictably** due to:

* Idle or oversized resources.
* Lack of visibility into anomalies and trends.
* No systematic way to measure realized savings.
* Reactive instead of proactive governance.

This platform aims to **automate FinOps workflows**:

* Detect → anomalous costs & usage patterns.
* Recommend → rightsizing & idle shutdown.
* Track → applied savings vs estimated.
* Forecast → next 30/90/180 days with ML models.
* Govern → budgets and policy-driven auto-remediation.

---

## Objectives

1. **Cost Optimization** → Save 20–30% of cloud spend.
2. **Automation First** → All FinOps processes automated (via Airflow DAGs).
3. **Unified Dashboard** → One pane of glass for costs, anomalies, savings, and forecasts.
4. **AI Assistance** → Natural language queries (e.g., "Top 5 services with rising cost last 60 days?").
5. **Auditability** → Every recommendation, anomaly, forecast, and applied saving logged.
6. **Secure & Observable** → Vault for secrets, Prometheus + Grafana + Loki for observability.

---

## Scope

* **Supported Cloud Provider:** AWS (EC2, ECS, EKS, Lambda).
* **Data Sources:** Billing (CUR/Cost Explorer), Usage (CloudWatch/Prometheus), AWS Pricing API.
* **Core Features:**

  * Billing + usage ingestion.
  * Rightsizing & idle detection.
  * Anomaly detection.
  * Cost forecasting (Prophet, ARIMA, SMA).
  * Savings tracker.
  * Auto-remediation.
  * AI assistant for FinOps queries.
* **Out of Scope (for now):** Azure/GCP integration, chargeback/showback, policy as code.

---

## Deliverables

* **Infrastructure:** Docker Compose + Helm chart.
* **Database Schema:** With migrations (Alembic) and ERD.
* **Backend APIs:** FastAPI with modular services.
* **Frontend Dashboards:** React + Tailwind + Grafana dashboards.
* **Airflow DAGs:** Automated workflows for ingestion, rightsizing, forecasting, savings, remediation.
* **Monitoring Stack:** Prometheus, Grafana, Loki, Promtail.
* **Vault:** Configured for secrets injection at runtime.
* **Documentation:** Planning → Strategy → Architecture → Tools → Decision Notes → Workflow → PlantUML → Code Explanation → Setup & CI/CD.

---

## Milestones

1. **DB & Backend API (v1)** → Core tables + FastAPI endpoints.
2. **Airflow DAGs (v2)** → Ingestion + anomaly detection + rightsizing.
3. **Forecasting & Savings (v3)** → Prophet/ARIMA + tracker DAG.
4. **Frontend Dashboards (v4)** → Insights, savings, anomalies, forecasts.
5. **Monitoring & Vault (v5)** → Prometheus, Grafana, Loki, Vault.
6. **AI Assistant (v6)** → Conversational insights.
7. **Docs & CI/CD (v7)** → Final polish.

---

## Review Questions

1. What problem is this FinOps project solving?
2. Which AWS services are currently supported?
3. Name the **six objectives** of this project.
4. What is the role of **Airflow DAGs** here?
5. Why do we use **Vault** in this setup?
6. What is the difference between a **recommendation** and a **savings record**?
7. Which ML models are used for forecasting?
8. What are the planned milestones (v1–v7)?
