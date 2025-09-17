from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import psycopg2
import os
import logging
import prometheus_client as prom

from prophet import Prophet
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error
from tensorflow import keras
from tensorflow.keras import layers
from app.services.forecast_metrics import record_forecast_drift
from app.services.finops_metrics import record_forecast_drift

# =========================
# Prometheus Metrics
# =========================
FORECAST_DRIFT = prom.Gauge(
    "finops_forecast_drift",
    "Forecast drift (MAPE) per model",
    ["model"]
)

# =========================
# DB Connection
# =========================
def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "finopsdb"),
        user=os.getenv("DB_USER", "finops"),
        password=os.getenv("DB_PASSWORD", "finops123"),
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", 5432),
    )

# =========================
# Forecasting Logic
# =========================
def run_forecasting(**context):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT usage_date, SUM(cost_amount)
        FROM billing
        WHERE usage_date >= CURRENT_DATE - INTERVAL '180 days'
        GROUP BY usage_date
        ORDER BY usage_date
    """)
    rows = cur.fetchall()
    df = pd.DataFrame(rows, columns=["ds", "y"])

    results = []

    # Prophet
    m = Prophet()
    m.fit(df)
    future = m.make_future_dataframe(periods=30)
    forecast = m.predict(future)
    y_true, y_pred = df["y"].values, forecast["yhat"][:len(df)]
    mape = mean_absolute_percentage_error(y_true, y_pred)
    FORECAST_DRIFT.labels("Prophet").set(mape)
    results.append(("Prophet", forecast[["ds", "yhat"]]))

    mape = mean_absolute_percentage_error(y_true, y_pred)
    record_forecast_drift("Prophet", mape)

    # ARIMA
    model = ARIMA(df["y"], order=(5,1,0))
    model_fit = model.fit()
    forecast_arima = model_fit.forecast(steps=30)
    mape = mean_absolute_percentage_error(y_true[-len(forecast_arima):], forecast_arima)
    FORECAST_DRIFT.labels("ARIMA").set(mape)
    results.append(("ARIMA", pd.DataFrame({"ds": pd.date_range(df["ds"].iloc[-1], periods=30), "yhat": forecast_arima})))

    # SMA
    df["sma"] = df["y"].rolling(window=7).mean()
    sma_forecast = df["sma"].iloc[-30:].fillna(method="bfill")
    mape = mean_absolute_percentage_error(y_true[-len(sma_forecast):], sma_forecast)
    FORECAST_DRIFT.labels("SMA").set(mape)
    results.append(("SMA", pd.DataFrame({"ds": df["ds"].iloc[-30:], "yhat": sma_forecast})))

    # LSTM
    data = df["y"].values.reshape(-1, 1)
    seq_len = 7
    X, y = [], []
    for i in range(len(data) - seq_len):
        X.append(data[i:i+seq_len])
        y.append(data[i+seq_len])
    X, y = np.array(X), np.array(y)

    model = keras.Sequential([
        layers.LSTM(50, activation="relu", input_shape=(seq_len, 1)),
        layers.Dense(1)
    ])
    model.compile(optimizer="adam", loss="mse")
    model.fit(X, y, epochs=10, verbose=0)

    preds = model.predict(X[-30:])
    mape = mean_absolute_percentage_error(y[-30:], preds)
    FORECAST_DRIFT.labels("LSTM").set(mape)
    future_dates = pd.date_range(df["ds"].iloc[-1], periods=30)
    results.append(("LSTM", pd.DataFrame({"ds": future_dates, "yhat": preds.flatten()})))

    # Store results
    for model_name, forecast_df in results:
        for _, row in forecast_df.iterrows():
            cur.execute("""
                INSERT INTO forecasts (account_id, service_id, forecast_period_start, forecast_period_end, forecast_amount, currency, model_used)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                None, None, datetime.now().date(), row["ds"], float(row["yhat"]), "USD", model_name
            ))

    conn.commit()
    cur.close()
    conn.close()

# =========================
# DAG Definition
# =========================
default_args = {
    "owner": "finops",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "cost_forecasting_v3",
    default_args=default_args,
    description="Cost forecasting with Prophet, ARIMA, SMA, LSTM + drift detection",
    schedule_interval="@daily",
    catchup=False,
) as dag:

    forecast_task = PythonOperator(
        task_id="run_forecasting",
        python_callable=run_forecasting,
        provide_context=True,
    )

forecast_task
