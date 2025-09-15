Cost Forecasting v3
-------------------

### 🎯 Goal

*   Extend existing **cost\_forecasting\_v2.py** (Prophet + ARIMA + SMA) with **deep-learning based LSTM**.
    
*   Add **forecast drift monitoring** (detect when model diverges from reality).
    
*   Push metrics to **Prometheus/Grafana** for observability.
    

### 🔹 Current (v2) Setup

*   **Prophet** → captures seasonality & trend.
    
*   **ARIMA** → handles autoregressive cost patterns.
    
*   **SMA** → provides a quick baseline (simple moving average).
    
*   Forecasts stored in forecasts table:
    
    *   forecast\_amount, forecast\_period\_start, forecast\_period\_end, model\_used, confidence\_interval.
        

### 🔹 v3 Enhancements

#### 1\. Add LSTM (Deep Learning)

*   Use **PyTorch/Keras LSTM** for sequential data.
    
*   Input: daily\_costs (normalized).
    
*   Output: next 30 days forecast.
    
*   Store results with model\_used = 'LSTM'.
    

Sample snippet:

```
import torch
import torch.nn as nn

class LSTMForecaster(nn.Module):
    def __init__(self, input_size=1, hidden_size=50, num_layers=2, output_size=1):
        super(LSTMForecaster, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])
        return out

```

*   Train on last 12 months of billing data.
    
*   Save model state in models/ or DB (optional).
    
*   Compare against Prophet/ARIMA predictions.
    

#### 2\. Forecast Drift Detection

*   Metrics: MAPE (Mean Absolute Percentage Error), RMSE.
    
*   If MAPE > 20% → trigger anomaly alert.
    
*   Store drift values in DB or expose as Prometheus metrics.
    

```
from sklearn.metrics import mean_absolute_percentage_error

mape = mean_absolute_percentage_error(actuals, forecast)
if mape > 0.2:
    trigger_alert("Forecast drift detected")

```

#### 3\. Observability

*   Push metrics to Prometheus:
    
    *   finops\_forecast\_drift{model="LSTM"}.
        
    *   finops\_forecast\_accuracy{model="Prophet"}.
        
*   Grafana dashboards:
    
    *   Line chart → actual vs predicted.
        
    *   Table → model comparison per service/account.
        

#### 4\. Airflow DAG Updates

*   cost\_forecasting\_v3.py:
    
    *   Train LSTM daily.
        
    *   Generate forecasts.
        
    *   Log drift metrics.
        
*   Store outputs in forecasts table.
    
*   Backfill logic for missing data.
    

### ✅ Outcomes

*   **More accurate predictions** on irregular workloads.
    
*   **Safety nets** with drift detection → alerts if model goes bad.
    
*   **Multi-model ensemble** → Prophet/ARIMA/LSTM side by side.
    
*   Continuous improvement loop (log errors → retrain LSTM).