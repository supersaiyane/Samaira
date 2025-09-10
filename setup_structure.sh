#!/bin/bash

# # Root directory
# mkdir -p finops-toolkit
# cd finops-toolkit || exit

# ---------------- Backend ----------------
mkdir -p backend/app/api backend/app/core backend/app/db backend/app/services
touch backend/app/__init__.py \
      backend/app/main.py \
      backend/app/api/__init__.py \
      backend/app/api/costs.py \
      backend/app/api/savings.py \
      backend/app/api/clusters.py \
      backend/app/core/config.py \
      backend/app/core/logger.py \
      backend/app/db/models.py \
      backend/app/services/aws_client.py \
      backend/app/services/ai_engine.py
touch backend/requirements.txt

# ---------------- Frontend ----------------
mkdir -p frontend/src/components frontend/src/pages
touch frontend/src/App.js
touch frontend/package.json

# ---------------- Airflow ----------------
mkdir -p airflow/dags
touch airflow/dags/ingest_cur.py \
      airflow/dags/rightsize.py \
      airflow/dags/forecast.py
touch airflow/requirements.txt

# ---------------- Database ----------------
mkdir -p db
touch db/schema.sql

# ---------------- AI ----------------
mkdir -p ai
touch ai/forecasting.py \
      ai/right_sizing.py \
      ai/anomaly_detection.py

# ---------------- Docs ----------------
mkdir -p docs
touch docs/SUMMARY.md \
      docs/01-planning.md \
      docs/02-strategy.md \
      docs/03-architecture.md \
      docs/04-tools.md \
      docs/05-decision-notes.md \
      docs/06-workflow.md \
      docs/07-plantuml.md \
      docs/08-code-explained.md \
      docs/README.md

# ---------------- Root files ----------------
touch docker-compose.yaml \
      .env.example \
      README.md \
      LICENSE

echo "✅ finops-toolkit structure created successfully!"
