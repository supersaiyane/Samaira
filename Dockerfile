# =========================
# Stage 1: Build frontend (React)
# =========================
FROM node:20 AS frontend-build
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# =========================
# Stage 2: Backend + Airflow base
# =========================
FROM apache/airflow:2.7.2-python3.11

USER root
WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# =========================
# Backend setup (FastAPI)
# =========================
COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app /app/app

# =========================
# Airflow DAGs
# =========================
COPY airflow/requirements.txt /app/airflow/requirements.txt
RUN pip install --no-cache-dir -r /app/airflow/requirements.txt

COPY airflow/dags /opt/airflow/dags

# =========================
# Frontend (built in Stage 1)
# =========================
RUN mkdir -p /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

COPY --from=frontend-build /frontend/dist /usr/share/nginx/html

# =========================
# Entrypoint Supervisor
# =========================
RUN pip install supervisor

COPY supervisord.conf /etc/supervisord.conf

EXPOSE 8000 3000 8080

CMD ["/usr/local/bin/supervisord", "-c", "/etc/supervisord.conf"]
