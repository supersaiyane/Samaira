import prometheus_client as prom

# ==============================
# Forecast Drift Metrics
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
    FORECAST_DRIFT.labels(model=model).set(mape)
    FORECAST_RUNS.labels(model=model).inc()


# ==============================
# Budget Utilization Metrics
# ==============================
BUDGET_UTILIZATION = prom.Gauge(
    "finops_budget_utilization",
    "Budget utilization ratio (actual spend / budget limit)",
    ["budget_name", "account_id", "service_id"]
)

def record_budget_utilization(budget_name: str, account_id: str, service_id: str, utilization: float):
    BUDGET_UTILIZATION.labels(
        budget_name=budget_name,
        account_id=account_id,
        service_id=service_id,
    ).set(utilization)


# ==============================
# Cost Anomaly Metrics
# ==============================
COST_ANOMALY = prom.Gauge(
    "finops_cost_anomaly",
    "Cost anomaly flag (1 = anomaly detected, 0 = normal)",
    ["account_id", "service_id"]
)

def record_cost_anomaly(account_id: str, service_id: str, is_anomaly: bool):
    COST_ANOMALY.labels(
        account_id=account_id,
        service_id=service_id,
    ).set(1 if is_anomaly else 0)


# ==============================
# Idle Resource Cost Metrics
# ==============================
IDLE_RESOURCE_COST = prom.Gauge(
    "finops_idle_resource_cost",
    "Idle resource cost in USD",
    ["resource_name"]
)

def record_idle_resource_cost(resource_name: str, cost: float):
    IDLE_RESOURCE_COST.labels(resource_name=resource_name).set(cost)
