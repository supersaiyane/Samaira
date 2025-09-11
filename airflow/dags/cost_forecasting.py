from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import pandas as pd
import psycopg2
import requests
import json
import numpy as np

from prophet import Prophet
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error

# =========================
# DB Connection Helper
# =========================
def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "finopsdb"),
        user=os.getenv("DB_USER", "finops"),
        password=os.getenv("DB_PASSWORD", "finops123"),
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", "5432"),
    )

# =========================
# Notifier
# =========================
def notify(message):
    slack_url = os.getenv("SLACK_WEBHOOK_URL")
    teams_url = os.getenv("TEAMS_WEBHOOK_URL")
    if slack_url:
        requests.post(slack_url, json={"text": message})
    if teams_url:
        payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "0072C6",
            "title": "📈 Forecast Update",
            "text": message,
        }
        requests.post(teams_url, json=payload)

# =========================
# Forecasting Logic
# =========================
def generate_forecasts():
    conn = get_db_connection()

    query = """
        SELECT a.account_id, a.account_name, s.service_id, s.service_name,
               b.usage_date, SUM(b.cost_amount) as cost
        FROM billing b
        JOIN accounts a ON b.account_id = a.account_id
        JOIN services s ON b.service_id = s.service_id
        WHERE usage_date >= CURRENT_DATE - INTERVAL '730 days'
        GROUP BY a.account_id, a.account_name, s.service_id, s.service_name, b.usage_date
        ORDER BY b.usage_date
    """
    billing = pd.read_sql(query, conn)

    if billing.empty:
        notify("ℹ️ No billing data available for forecasting.")
        conn.close()
        return

    results = []

    for (acct_id, svc_id), group in billing.groupby(["account_id", "service_id"]):
        account_name = group["account_name"].iloc[0]
        service_name = group["service_name"].iloc[0]
        df = group[["usage_date", "cost"]].rename(columns={"usage_date": "ds", "cost": "y"})

        if len(df) < 60:
            continue

        # Train/test split (last 30d for validation)
        train = df.iloc[:-30]
        test = df.iloc[-30:]

        best_model, best_mape, best_rmse, best_forecast = None, float("inf"), float("inf"), None

        # ---------- Model 1: Prophet ----------
        try:
            m = Prophet(interval_width=0.8, weekly_seasonality=True, yearly_seasonality=True)
            m.fit(train)
            future = m.make_future_dataframe(periods=180)
            forecast = m.predict(future)

            test_forecast = forecast.tail(30)
            mape = mean_absolute_percentage_error(test["y"], test_forecast["yhat"])
            rmse = np.sqrt(mean_squared_error(test["y"], test_forecast["yhat"]))

            if mape < best_mape:
                best_model, best_mape, best_rmse, best_forecast = "Prophet", mape, rmse, forecast
        except Exception as e:
            print(f"⚠️ Prophet failed for {acct_id}/{svc_id}: {e}")

        # ---------- Model 2: ARIMA ----------
        try:
            series = train["y"].values
            model = ARIMA(series, order=(5,1,0))
            fitted = model.fit()
            forecast_vals = fitted.forecast(steps=180)
            forecast_index = pd.date_range(start=train["ds"].iloc[-1], periods=180, freq="D")
            forecast = pd.DataFrame({"ds": forecast_index, "yhat": forecast_vals})

            mape = mean_absolute_percentage_error(test["y"].values, forecast.head(30)["yhat"].values)
            rmse = np.sqrt(mean_squared_error(test["y"].values, forecast.head(30)["yhat"].values))

            if mape < best_mape:
                best_model, best_mape, best_rmse, best_forecast = "ARIMA", mape, rmse, forecast
        except Exception as e:
            print(f"⚠️ ARIMA failed for {acct_id}/{svc_id}: {e}")

        # ---------- Model 3: SMA (baseline) ----------
        try:
            sma = train["y"].rolling(window=7).mean().iloc[-1]
            forecast_vals = [sma] * 180
            forecast_index = pd.date_range(start=train["ds"].iloc[-1], periods=180, freq="D")
            forecast = pd.DataFrame({"ds": forecast_index, "yhat": forecast_vals})

            mape = mean_absolute_percentage_error(test["y"].values, forecast.head(30)["yhat"].values)
            rmse = np.sqrt(mean_squared_error(test["y"].values, forecast.head(30)["yhat"].values))

            if mape < best_mape:
                best_model, best_mape, best_rmse, best_forecast = "SMA", mape, rmse, forecast
        except Exception as e:
            print(f"⚠️ SMA failed for {acct_id}/{svc_id}: {e}")

        # ---------- Store Forecasts with UPSERT ----------
        if best_forecast is not None:
            for horizon in [30, 90, 180]:
                horizon_df = best_forecast.tail(horizon)

                if best_model == "Prophet":
                    lower = horizon_df["yhat_lower"].min()
                    upper = horizon_df["yhat_upper"].max()
                else:
                    lower = horizon_df["yhat"].min()
                    upper = horizon_df["yhat"].max()

                avg_forecast = horizon_df["yhat"].sum()

                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO forecasts (account_id, service_id, forecast_period_start, forecast_period_end,
                                           forecast_amount, currency, model_used, confidence_interval, generated_at)
                    VALUES (%s, %s, %s, %s, %s, 'USD', %s, %s, NOW())
                    ON CONFLICT (account_id, service_id, forecast_period_start, forecast_period_end)
                    DO UPDATE SET forecast_amount = EXCLUDED.forecast_amount,
                                  model_used = EXCLUDED.model_used,
                                  confidence_interval = EXCLUDED.confidence_interval,
                                  generated_at = NOW()
                """, (
                    acct_id,
                    svc_id,
                    datetime.utcnow().date(),
                    (datetime.utcnow() + timedelta(days=horizon)).date(),
                    avg_forecast,
                    best_model,
                    json.dumps({"lower": float(lower), "upper": float(upper), "mape": best_mape, "rmse": best_rmse})
                ))
                conn.commit()
                cursor.close()

            results.append((account_name, service_name, best_model, best_mape, best_rmse, avg_forecast))

    conn.close()

    # Notifications
    if results:
        lines = ["📈 Forecasts Generated:"]
        for acct, svc, model, mape, rmse, avg in results[:10]:  # top 10
            lines.append(f"- {acct} / {svc}: ${avg:.2f} | Model={model}, MAPE={mape:.2f}, RMSE={rmse:.2f}")
        notify("\n".join(lines))
    else:
        notify("ℹ️ No forecasts generated.")

# =========================
# DAG Definition
# =========================
default_args = {
    "owner": "finops",
    "depends_on_past": False,
    "email_on_failure": True,
    "email": ["alerts@finops-toolkit.com"],
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="cost_forecasting_v2",
    default_args=default_args,
    description="Multi-model multi-horizon cost forecasting with UPSERT + enriched notifications",
    schedule_interval="0 10 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["finops", "forecast", "v2"],
) as dag:

    forecast = PythonOperator(
        task_id="generate_forecasts",
        python_callable=generate_forecasts,
    )
