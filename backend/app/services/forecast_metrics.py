import prometheus_client as prom

# ==============================
# Prometheus Metrics for Forecasting
# ==============================
FORECAST_DRIFT = prom.Gauge(
    "finops_forecast_drift",
    "Forecast drift (MAPE) per model",
    ["model"]  # Prophet, ARIMA, SMA, LSTM
)

FORECAST_RUNS = prom.Counter(
    "finops_forecast_runs_total",
    "Total forecast runs per model",
    ["model"]
)

def record_forecast_drift(model: str, mape: float):
    """Update Prometheus gauge with forecast drift."""
    FORECAST_DRIFT.labels(model=model).set(mape)
    FORECAST_RUNS.labels(model=model).inc()
