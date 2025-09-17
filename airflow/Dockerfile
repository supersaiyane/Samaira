FROM apache/airflow:2.7.2-python3.11

USER root
WORKDIR /opt/airflow

# Install custom deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy DAGs
COPY dags/ /opt/airflow/dags/

# Expose Airflow webserver
EXPOSE 8080
CMD ["airflow", "webserver"]
